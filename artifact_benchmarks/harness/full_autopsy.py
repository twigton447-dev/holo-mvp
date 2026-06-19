from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def mean_or_none(values: list[float]) -> float | None:
    return round(mean(values), 3) if values else None


def csv_write(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def latest_run_dir(packet_dir: Path) -> Path:
    runs_dir = packet_dir / "runs"
    candidates = [
        path
        for path in runs_dir.iterdir()
        if path.is_dir() and (path / "run_manifest.json").exists()
    ]
    if not candidates:
        raise SystemExit(f"No run manifests found under {runs_dir}")
    return max(candidates, key=lambda path: (path / "run_manifest.json").stat().st_mtime)


def condition_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for condition, payload in sorted((manifest.get("condition_results") or {}).items()):
        if not isinstance(payload, dict):
            continue
        validity = payload.get("artifact_validity_report") or {}
        rows.append(
            {
                "condition": condition,
                "provider_model": payload.get("provider_model"),
                "final_artifact_path": payload.get("final_artifact_path"),
                "final_sha256": payload.get("final_sha256"),
                "final_word_count": payload.get("final_word_count"),
                "word_count_in_band": payload.get("word_count_in_band"),
                "selected_turn": payload.get("selected_turn"),
                "valid_final": validity.get("valid"),
                "validity_flags": "; ".join(validity.get("flags") or []),
            }
        )
    return rows


def trace_inventory(run_dir: Path) -> dict[str, Any]:
    traces = sorted((run_dir / "traces").glob("**/*.json"))
    by_call_type = Counter()
    by_condition = Counter()
    by_provider = Counter()
    by_model = Counter()
    missing_artifacts = []
    for path in traces:
        try:
            trace = read_json(path)
        except Exception:
            continue
        by_call_type[str(trace.get("call_type"))] += 1
        by_condition[str(trace.get("condition"))] += 1
        by_provider[str(trace.get("provider"))] += 1
        by_model[str(trace.get("model") or trace.get("provider_model"))] += 1
        artifact = trace.get("artifact_path")
        if artifact and not Path(artifact).exists():
            missing_artifacts.append({"trace": str(path), "artifact_path": artifact})
    return {
        "trace_count": len(traces),
        "by_call_type": dict(sorted(by_call_type.items())),
        "by_condition": dict(sorted(by_condition.items())),
        "by_provider": dict(sorted(by_provider.items())),
        "by_model": dict(sorted(by_model.items())),
        "missing_artifacts": missing_artifacts,
    }


def judge_outputs(run_dir: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[dict[str, Any]]]:
    summary_path = run_dir / "judge_score_summary_all_pairs.json"
    if not summary_path.exists():
        return None, [], []
    summary = read_json(summary_path)
    judge_rows: list[dict[str, Any]] = []
    criterion_rows: list[dict[str, Any]] = []
    anon_path = run_dir / "sealed" / "anonymization_map.json"
    pair_map_by_id = {}
    if anon_path.exists():
        anon = read_json(anon_path)
        pair_map_by_id = {item["judge_packet_id"]: item for item in anon.get("pairs", [])}
    for pair in summary.get("pair_summaries", []):
        pair_id = pair.get("pair_id")
        pair_map = pair_map_by_id.get(pair_id, {})
        solo_condition = pair.get("solo_condition")
        for score_path in sorted((run_dir / "judge_scores" / str(pair_id)).glob("*.json")):
            score = read_json(score_path)
            x_condition = pair_map.get("document_x_condition")
            y_condition = pair_map.get("document_y_condition")
            x_score = float(score.get("document_x", {}).get("weighted_score_1_10") or 0)
            y_score = float(score.get("document_y", {}).get("weighted_score_1_10") or 0)
            if x_condition == "holo_frontier_gov":
                holo_doc = score.get("document_x", {})
                solo_doc = score.get("document_y", {})
                holo_score = x_score
                solo_score = y_score
            else:
                holo_doc = score.get("document_y", {})
                solo_doc = score.get("document_x", {})
                holo_score = y_score
                solo_score = x_score
            flags = score.get("validation_flags") or []
            harness = score.get("_harness") or {}
            row = {
                "pair_id": pair_id,
                "solo_condition": solo_condition,
                "judge_id": score.get("judge_id") or score_path.stem,
                "judge_provider": harness.get("judge_provider"),
                "judge_model": harness.get("judge_model"),
                "holo_score": holo_score,
                "solo_score": solo_score,
                "gap_holo_minus_solo": round(holo_score - solo_score, 3),
                "validation_flags": "; ".join(str(flag) for flag in flags),
                "is_clean": not bool(flags),
                "stronger_document": (score.get("comparative_verdict") or {}).get("stronger_document"),
            }
            judge_rows.append(row)
            holo_by_id = {
                item.get("criterion_id"): item
                for item in holo_doc.get("criterion_scores", [])
                if isinstance(item, dict)
            }
            solo_by_id = {
                item.get("criterion_id"): item
                for item in solo_doc.get("criterion_scores", [])
                if isinstance(item, dict)
            }
            for criterion_id in sorted(set(holo_by_id) | set(solo_by_id)):
                if not criterion_id:
                    continue
                h_score = float((holo_by_id.get(criterion_id) or {}).get("score_1_10") or 0)
                s_score = float((solo_by_id.get(criterion_id) or {}).get("score_1_10") or 0)
                criterion_rows.append(
                    {
                        "pair_id": pair_id,
                        "solo_condition": solo_condition,
                        "judge_id": row["judge_id"],
                        "judge_provider": row["judge_provider"],
                        "criterion_id": criterion_id,
                        "holo_score_1_10": h_score,
                        "solo_score_1_10": s_score,
                        "gap_holo_minus_solo": round(h_score - s_score, 3),
                    }
                )
    return summary, judge_rows, criterion_rows


def final_artifact_checks(condition_row: dict[str, Any]) -> dict[str, Any]:
    path_text = condition_row.get("final_artifact_path")
    if not path_text:
        return {"exists": False, "non_empty": False, "computed_word_count": None, "ends_cleanly": False}
    path = Path(path_text)
    if not path.exists():
        return {"exists": False, "non_empty": False, "computed_word_count": None, "ends_cleanly": False}
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    return {
        "exists": True,
        "non_empty": bool(stripped),
        "computed_word_count": word_count(text),
        "ends_cleanly": bool(stripped) and stripped[-1] in ".!?)]}",
        "contains_internal_process_residue": any(
            marker in text
            for marker in [
                "HoloGov mission packet",
                "Diagnostic placeholder",
                "Benchmark credit",
                "Provider calls",
                "Condition:",
            ]
        ),
    }


def build_autopsy(packet_dir: Path, run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "run_manifest.json"
    manifest = read_json(manifest_path)
    hash_lock = read_json(packet_dir / "hash_lock.json") if (packet_dir / "hash_lock.json").exists() else None
    conditions = condition_rows(manifest)
    for row in conditions:
        row["artifact_checks"] = final_artifact_checks(row)
    judge_summary, judge_rows, criterion_rows = judge_outputs(run_dir)
    clean_rows = [row for row in judge_rows if row.get("is_clean")]
    flagged_rows = [row for row in judge_rows if not row.get("is_clean")]
    criterion_means: dict[str, float | None] = {}
    for criterion_id in sorted({row["criterion_id"] for row in criterion_rows}):
        criterion_means[criterion_id] = mean_or_none(
            [
                float(row["gap_holo_minus_solo"])
                for row in criterion_rows
                if row["criterion_id"] == criterion_id
            ]
        )
    failures = []
    if manifest.get("benchmark_credit") is not False:
        failures.append("benchmark_credit_not_false_default")
    if manifest.get("public_claim") is not False:
        failures.append("public_claim_not_false_default")
    if not conditions and manifest.get("status") not in {"NO_PROVIDER_SMOKE_PASS", "analysis_incomplete_no_judge_summary"}:
        failures.append("missing_condition_results")
    for row in conditions:
        checks = row["artifact_checks"]
        if not checks["exists"]:
            failures.append(f"missing_final_artifact:{row['condition']}")
        if checks["exists"] and not checks["non_empty"]:
            failures.append(f"empty_final_artifact:{row['condition']}")
        if checks["exists"] and not checks["ends_cleanly"]:
            failures.append(f"unclean_final_ending:{row['condition']}")
        if checks.get("contains_internal_process_residue"):
            failures.append(f"process_residue_in_final:{row['condition']}")
    if judge_summary and not judge_rows:
        failures.append("judge_summary_present_but_no_judge_rows")
    return {
        "status": "autopsy_complete",
        "run_id": manifest.get("run_id", run_dir.name),
        "run_status": manifest.get("status"),
        "packet_dir": str(packet_dir),
        "run_manifest": str(manifest_path),
        "hash_lock_id": (hash_lock or {}).get("hash_lock_id"),
        "combined_packet_hash": (hash_lock or {}).get("combined_packet_hash"),
        "benchmark_credit": manifest.get("benchmark_credit"),
        "public_claim": manifest.get("public_claim"),
        "provider_call_count": manifest.get("provider_call_count"),
        "total_input_tokens": manifest.get("total_input_tokens"),
        "total_output_tokens": manifest.get("total_output_tokens"),
        "total_latency_ms": manifest.get("total_latency_ms"),
        "condition_results": conditions,
        "trace_inventory": trace_inventory(run_dir),
        "judge_summary": judge_summary,
        "judge_row_count": len(judge_rows),
        "clean_judge_row_count": len(clean_rows),
        "flagged_judge_row_count": len(flagged_rows),
        "overall_gap_all_judges": (judge_summary or {}).get("overall", {}).get("gap_holo_minus_solo") if judge_summary else None,
        "overall_gap_clean_only": mean_or_none([float(row["gap_holo_minus_solo"]) for row in clean_rows]),
        "criterion_gap_means": criterion_means,
        "flagged_judge_rows": flagged_rows,
        "autopsy_failures": failures,
    }


def write_autopsy(run_dir: Path, autopsy: dict[str, Any]) -> None:
    out_dir = run_dir / "autopsy"
    write_json(out_dir / "full_autopsy.json", autopsy)
    csv_write(
        out_dir / "condition_results.csv",
        autopsy["condition_results"],
        [
            "condition",
            "provider_model",
            "final_word_count",
            "word_count_in_band",
            "selected_turn",
            "valid_final",
            "validity_flags",
            "final_sha256",
            "final_artifact_path",
        ],
    )
    csv_write(
        out_dir / "flagged_judge_rows.csv",
        autopsy["flagged_judge_rows"],
        [
            "pair_id",
            "solo_condition",
            "judge_id",
            "judge_provider",
            "judge_model",
            "holo_score",
            "solo_score",
            "gap_holo_minus_solo",
            "validation_flags",
            "stronger_document",
        ],
    )
    lines = [
        "# Full Artifact Benchmark Autopsy",
        "",
        f"Run ID: `{autopsy['run_id']}`",
        f"Run status: `{autopsy['run_status']}`",
        f"Benchmark credit: `{autopsy['benchmark_credit']}`",
        f"Public claim: `{autopsy['public_claim']}`",
        f"Hash lock: `{autopsy['hash_lock_id']}`",
        "",
        "## Score Summary",
        "",
        f"- Overall gap all judges: `{autopsy['overall_gap_all_judges']}`",
        f"- Overall gap clean-only: `{autopsy['overall_gap_clean_only']}`",
        f"- Judge rows: `{autopsy['judge_row_count']}`",
        f"- Flagged judge rows: `{autopsy['flagged_judge_row_count']}`",
        "",
        "## Conditions",
        "",
    ]
    for row in autopsy["condition_results"]:
        checks = row["artifact_checks"]
        lines.extend(
            [
                f"### {row['condition']}",
                "",
                f"- Word count: `{row.get('final_word_count')}`",
                f"- In band: `{row.get('word_count_in_band')}`",
                f"- Final exists: `{checks.get('exists')}`",
                f"- Ends cleanly: `{checks.get('ends_cleanly')}`",
                f"- Process residue: `{checks.get('contains_internal_process_residue')}`",
                "",
            ]
        )
    lines.extend(["## Criterion Gap Means", ""])
    for criterion_id, value in autopsy["criterion_gap_means"].items():
        lines.append(f"- `{criterion_id}`: `{value}`")
    lines.extend(["", "## Autopsy Failures", ""])
    if autopsy["autopsy_failures"]:
        lines.extend(f"- `{item}`" for item in autopsy["autopsy_failures"])
    else:
        lines.append("- none")
    write_text(out_dir / "full_autopsy.md", "\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet_dir", type=Path, help="Packet directory containing runs/ and optional hash_lock.json.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--latest", action="store_true")
    group.add_argument("--run-id")
    args = parser.parse_args()
    packet_dir = args.packet_dir.resolve()
    run_dir = latest_run_dir(packet_dir) if args.latest else packet_dir / "runs" / str(args.run_id)
    if not (run_dir / "run_manifest.json").exists():
        raise SystemExit(f"Missing run manifest: {run_dir / 'run_manifest.json'}")
    autopsy = build_autopsy(packet_dir, run_dir)
    write_autopsy(run_dir, autopsy)
    print(json.dumps(autopsy, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
