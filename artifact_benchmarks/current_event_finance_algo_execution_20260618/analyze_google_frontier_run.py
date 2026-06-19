from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


PACKET_DIR = Path(__file__).resolve().parent
RUNS_DIR = PACKET_DIR / "runs"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_run_dir() -> Path:
    candidates = [
        path
        for path in RUNS_DIR.iterdir()
        if path.is_dir() and (path / "run_manifest.json").exists()
    ]
    if not candidates:
        raise SystemExit(f"No run manifests found under {RUNS_DIR}")
    return max(candidates, key=lambda path: (path / "run_manifest.json").stat().st_mtime)


def csv_write(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def score_to_condition(
    *,
    score: dict[str, Any],
    pair_map: dict[str, Any],
    condition: str,
) -> dict[str, Any]:
    x_condition = pair_map["document_x_condition"]
    y_condition = pair_map["document_y_condition"]
    if x_condition == condition:
        return score["document_x"]
    if y_condition == condition:
        return score["document_y"]
    raise KeyError(f"condition {condition} not in pair {pair_map}")


def verdict_consistency(row: dict[str, Any]) -> str:
    flags = row.get("validation_flags") or []
    contradiction_flags = [
        flag
        for flag in flags
        if "verdict_score_contradiction" in str(flag)
        or "stronger_document" in str(flag)
        or "tie" in str(flag)
    ]
    return "flagged" if contradiction_flags else "clean"


def collect_score_rows(run_dir: Path, judge_summary: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    anon_path = run_dir / "sealed" / "anonymization_map.json"
    if not anon_path.exists():
        return [], [], []
    anon = read_json(anon_path)
    pair_map_by_id = {item["judge_packet_id"]: item for item in anon.get("pairs", [])}
    score_rows: list[dict[str, Any]] = []
    judge_rows: list[dict[str, Any]] = []
    criterion_rows: list[dict[str, Any]] = []

    for pair in judge_summary.get("pair_summaries", []):
        pair_id = pair["pair_id"]
        pair_map = pair_map_by_id[pair_id]
        solo_condition = pair["solo_condition"]
        for score_path in sorted((run_dir / "judge_scores" / pair_id).glob("*.json")):
            score = read_json(score_path)
            judge_id = score.get("judge_id") or score_path.stem
            harness = score.get("_harness") or {}
            holo_doc = score_to_condition(score=score, pair_map=pair_map, condition="holo_frontier_gov")
            solo_doc = score_to_condition(score=score, pair_map=pair_map, condition=solo_condition)
            holo_score = float(holo_doc["weighted_score_1_10"])
            solo_score = float(solo_doc["weighted_score_1_10"])
            gap = round(holo_score - solo_score, 3)
            flags = score.get("validation_flags") or []
            verdict = score.get("comparative_verdict") or {}
            judge_row = {
                "pair_id": pair_id,
                "solo_condition": solo_condition,
                "judge_id": judge_id,
                "judge_provider": harness.get("judge_provider"),
                "judge_model": harness.get("judge_model"),
                "holo_score": holo_score,
                "solo_score": solo_score,
                "gap_holo_minus_solo": gap,
                "stronger_document": verdict.get("stronger_document"),
                "margin_of_difference": verdict.get("margin_of_difference"),
                "judge_confidence_1_5": verdict.get("judge_confidence_1_5"),
                "validation_flags": "; ".join(str(flag) for flag in flags),
                "verdict_consistency": verdict_consistency({"validation_flags": flags}),
            }
            judge_rows.append(judge_row)
            score_rows.append(judge_row)
            holo_by_id = {
                item["criterion_id"]: item
                for item in holo_doc.get("criterion_scores", [])
                if isinstance(item, dict) and "criterion_id" in item
            }
            solo_by_id = {
                item["criterion_id"]: item
                for item in solo_doc.get("criterion_scores", [])
                if isinstance(item, dict) and "criterion_id" in item
            }
            for criterion_id in sorted(set(holo_by_id) | set(solo_by_id)):
                holo_item = holo_by_id.get(criterion_id, {})
                solo_item = solo_by_id.get(criterion_id, {})
                h_score = float(holo_item.get("score_1_10") or 0)
                s_score = float(solo_item.get("score_1_10") or 0)
                criterion_rows.append(
                    {
                        "pair_id": pair_id,
                        "solo_condition": solo_condition,
                        "judge_id": judge_id,
                        "judge_provider": harness.get("judge_provider"),
                        "criterion_id": criterion_id,
                        "holo_score_1_10": h_score,
                        "solo_score_1_10": s_score,
                        "gap_holo_minus_solo": round(h_score - s_score, 3),
                        "holo_notes": holo_item.get("notes", ""),
                        "solo_notes": solo_item.get("notes", ""),
                    }
                )
    return score_rows, judge_rows, criterion_rows


def mean_or_none(values: list[float]) -> float | None:
    return round(mean(values), 3) if values else None


def analyze(run_dir: Path) -> dict[str, Any]:
    manifest = read_json(run_dir / "run_manifest.json")
    analysis_dir = run_dir / "analysis"
    summary_path = None
    if manifest.get("judge_summary_path"):
        summary_path = Path(manifest["judge_summary_path"])
    elif (run_dir / "judge_score_summary_all_pairs.json").exists():
        summary_path = run_dir / "judge_score_summary_all_pairs.json"
    if not summary_path or not summary_path.exists():
        result = {
            "status": "analysis_incomplete_no_judge_summary",
            "run_id": manifest.get("run_id", run_dir.name),
            "run_status": manifest.get("status"),
            "run_manifest": str(run_dir / "run_manifest.json"),
            "message": "No judge summary found yet. Run the live benchmark first.",
        }
        write_json(analysis_dir / "analysis_summary.json", result)
        write_text(analysis_dir / "analysis_summary.md", "# Analysis Incomplete\n\nNo judge summary found yet. Run the live benchmark first.\n")
        return result

    judge_summary = read_json(summary_path)
    score_rows, judge_rows, criterion_rows = collect_score_rows(run_dir, judge_summary)
    clean_judge_rows = [row for row in judge_rows if not row["validation_flags"]]
    flagged_judge_rows = [row for row in judge_rows if row["validation_flags"]]

    condition_results = manifest.get("condition_results") or {}
    condition_rows = []
    for condition, payload in sorted(condition_results.items()):
        if not isinstance(payload, dict):
            continue
        condition_rows.append(
            {
                "condition": condition,
                "provider_model": payload.get("provider_model"),
                "final_word_count": payload.get("final_word_count"),
                "word_count_in_band": payload.get("word_count_in_band"),
                "selected_turn": payload.get("selected_turn"),
                "final_sha256": payload.get("final_sha256"),
                "final_artifact_path": payload.get("final_artifact_path"),
                "valid_final": (payload.get("artifact_validity_report") or {}).get("valid"),
                "validity_flags": "; ".join((payload.get("artifact_validity_report") or {}).get("flags") or []),
            }
        )

    pair_rows = []
    for pair in judge_summary.get("pair_summaries", []):
        rows_for_pair = [row for row in judge_rows if row["solo_condition"] == pair.get("solo_condition")]
        clean_rows_for_pair = [row for row in rows_for_pair if not row["validation_flags"]]
        pair_rows.append(
            {
                "pair_id": pair.get("pair_id"),
                "solo_condition": pair.get("solo_condition"),
                "holo_mean_all": pair.get("holo_mean"),
                "solo_mean_all": pair.get("solo_mean"),
                "gap_all": pair.get("gap_holo_minus_solo"),
                "gap_clean_only": mean_or_none([float(row["gap_holo_minus_solo"]) for row in clean_rows_for_pair]),
                "judge_count": len(rows_for_pair),
                "flagged_judge_count": len(rows_for_pair) - len(clean_rows_for_pair),
            }
        )

    criterion_gap_means: dict[str, float | None] = {}
    for criterion_id in sorted({row["criterion_id"] for row in criterion_rows}):
        criterion_gap_means[criterion_id] = mean_or_none(
            [
                float(row["gap_holo_minus_solo"])
                for row in criterion_rows
                if row["criterion_id"] == criterion_id
            ]
        )

    summary = {
        "status": "analysis_complete",
        "run_id": manifest.get("run_id", run_dir.name),
        "run_status": manifest.get("status"),
        "benchmark_credit": manifest.get("benchmark_credit"),
        "public_claim": manifest.get("public_claim"),
        "run_manifest": str(run_dir / "run_manifest.json"),
        "judge_summary_path": str(summary_path),
        "overall": judge_summary.get("overall"),
        "overall_gap_clean_only": mean_or_none([float(row["gap_holo_minus_solo"]) for row in clean_judge_rows]),
        "pair_summaries": pair_rows,
        "criterion_gap_means": criterion_gap_means,
        "condition_results": condition_rows,
        "judge_row_count": len(judge_rows),
        "clean_judge_row_count": len(clean_judge_rows),
        "flagged_judge_row_count": len(flagged_judge_rows),
        "flagged_judge_rows": flagged_judge_rows,
        "provider_call_count": manifest.get("provider_call_count"),
        "total_input_tokens": manifest.get("total_input_tokens"),
        "total_output_tokens": manifest.get("total_output_tokens"),
        "total_latency_ms": manifest.get("total_latency_ms"),
        "outputs": {
            "analysis_summary_json": str(analysis_dir / "analysis_summary.json"),
            "analysis_summary_md": str(analysis_dir / "analysis_summary.md"),
            "scores_csv": str(analysis_dir / "scores.csv"),
            "judge_rows_csv": str(analysis_dir / "judge_rows.csv"),
            "criterion_gaps_csv": str(analysis_dir / "criterion_gaps.csv"),
            "condition_results_csv": str(analysis_dir / "condition_results.csv"),
        },
    }

    csv_write(
        analysis_dir / "scores.csv",
        score_rows,
        [
            "pair_id",
            "solo_condition",
            "judge_id",
            "judge_provider",
            "judge_model",
            "holo_score",
            "solo_score",
            "gap_holo_minus_solo",
            "stronger_document",
            "margin_of_difference",
            "judge_confidence_1_5",
            "validation_flags",
            "verdict_consistency",
        ],
    )
    csv_write(analysis_dir / "judge_rows.csv", judge_rows, list(score_rows[0].keys()) if score_rows else [])
    csv_write(
        analysis_dir / "criterion_gaps.csv",
        criterion_rows,
        [
            "pair_id",
            "solo_condition",
            "judge_id",
            "judge_provider",
            "criterion_id",
            "holo_score_1_10",
            "solo_score_1_10",
            "gap_holo_minus_solo",
            "holo_notes",
            "solo_notes",
        ],
    )
    csv_write(
        analysis_dir / "condition_results.csv",
        condition_rows,
        [
            "condition",
            "provider_model",
            "final_word_count",
            "word_count_in_band",
            "selected_turn",
            "final_sha256",
            "final_artifact_path",
            "valid_final",
            "validity_flags",
        ],
    )

    lines = [
        "# Finance Frontier Run Analysis",
        "",
        f"Run ID: `{summary['run_id']}`",
        f"Run status: `{summary['run_status']}`",
        f"Benchmark credit: `{summary['benchmark_credit']}`",
        f"Public claim: `{summary['public_claim']}`",
        "",
        "## Overall",
        "",
        f"- Holo mean: `{(summary['overall'] or {}).get('holo_mean')}`",
        f"- Solo mean: `{(summary['overall'] or {}).get('solo_mean')}`",
        f"- Gap Holo minus Solo: `{(summary['overall'] or {}).get('gap_holo_minus_solo')}`",
        f"- Clean-only gap: `{summary['overall_gap_clean_only']}`",
        f"- Judge rows: `{summary['judge_row_count']}`",
        f"- Flagged judge rows: `{summary['flagged_judge_row_count']}`",
        "",
        "## Pair Summary",
        "",
    ]
    for pair in pair_rows:
        lines.extend(
            [
                f"### {pair['solo_condition']}",
                "",
                f"- Gap all judges: `{pair['gap_all']}`",
                f"- Gap clean-only: `{pair['gap_clean_only']}`",
                f"- Flagged judge rows: `{pair['flagged_judge_count']}`",
                "",
            ]
        )
    lines.extend(["## Criterion Gap Means", ""])
    for criterion_id, value in criterion_gap_means.items():
        lines.append(f"- `{criterion_id}`: `{value}`")
    lines.extend(["", "## Output Files", ""])
    for name, path in summary["outputs"].items():
        lines.append(f"- `{name}`: `{path}`")
    if flagged_judge_rows:
        lines.extend(["", "## Flagged Judge Rows", ""])
        for row in flagged_judge_rows:
            lines.append(
                f"- `{row['solo_condition']}` / `{row['judge_id']}`: {row['validation_flags']}"
            )

    write_json(analysis_dir / "analysis_summary.json", summary)
    write_text(analysis_dir / "analysis_summary.md", "\n".join(lines) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest", action="store_true", help="Analyze the latest run folder.")
    parser.add_argument("--run-id", help="Analyze a specific run id.")
    args = parser.parse_args()
    if bool(args.latest) == bool(args.run_id):
        parser.error("Choose exactly one of --latest or --run-id")
    run_dir = latest_run_dir() if args.latest else RUNS_DIR / str(args.run_id)
    if not (run_dir / "run_manifest.json").exists():
        raise SystemExit(f"Missing run manifest: {run_dir / 'run_manifest.json'}")
    summary = analyze(run_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["status"] == "analysis_complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
