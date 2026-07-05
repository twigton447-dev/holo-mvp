#!/usr/bin/env python3
"""Post-hoc scorer for the HoloVerify stress-matrix Wave 1 solo scout."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_stress_matrix_expansion_wave1_2026_07_05"
    / "holoverify_stress_matrix_expansion_wave1_scoring_map_2026_07_05.json"
)
EXPECTED_SCORING_MAP_SHA256 = "854695052774477c3fbb23c834b40cb6cdd33891f4b47c60512ac829b49365a5"
ROLLUP_JSON = BENCHMARK_ROOT / "HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_ROLLUP_2026_07_05.json"
ROLLUP_MD = BENCHMARK_ROOT / "HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_ROLLUP_2026_07_05.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(errors="replace").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def error_class(verdict: str, truth: str | None, admissible: bool) -> str:
    if not admissible:
        return "PARSE_OR_ADMISSIBILITY_FAILURE"
    if verdict not in {"ALLOW", "ESCALATE"}:
        return "UNKNOWN_VERDICT"
    if verdict == truth:
        return "KNEW_ADMISSIBLE"
    if verdict == "ALLOW" and truth == "ESCALATE":
        return "FALSE_NEGATIVE_ALLOW_ON_ESCALATE"
    if verdict == "ESCALATE" and truth == "ALLOW":
        return "FALSE_POSITIVE_ESCALATE_ON_ALLOW"
    return "WRONG_VERDICT"


def compact_pair_summary(score_rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in score_rows:
        by_pair[str(row.get("pair_id"))].append(row)
    pair_rows: list[dict[str, Any]] = []
    summary = Counter()
    for pair_id, rows in sorted(by_pair.items()):
        failures = [row for row in rows if not row.get("solo_knew_admissible")]
        wrong = [
            row
            for row in rows
            if row.get("error_class") in {"FALSE_POSITIVE_ESCALATE_ON_ALLOW", "FALSE_NEGATIVE_ALLOW_ON_ESCALATE", "WRONG_VERDICT"}
        ]
        parse = [row for row in rows if row.get("error_class") == "PARSE_OR_ADMISSIBILITY_FAILURE"]
        fp = [row for row in rows if row.get("error_class") == "FALSE_POSITIVE_ESCALATE_ON_ALLOW"]
        fn = [row for row in rows if row.get("error_class") == "FALSE_NEGATIVE_ALLOW_ON_ESCALATE"]
        if failures:
            summary["pairs_with_any_solo_failure"] += 1
        if wrong:
            summary["pairs_with_wrong_verdict"] += 1
        if fp:
            summary["pairs_with_false_positive"] += 1
        if fn:
            summary["pairs_with_false_negative"] += 1
        if parse and not wrong:
            summary["pairs_parse_only"] += 1
        pair_rows.append(
            {
                "pair_id": pair_id,
                "domain": rows[0].get("domain") if rows else None,
                "solo_calls": len(rows),
                "solo_failure_count": len(failures),
                "wrong_verdict_count": len(wrong),
                "parse_or_admissibility_count": len(parse),
                "false_positive_count": len(fp),
                "false_negative_count": len(fn),
                "legacy_packets": sorted({str(row.get("legacy_packet_id")) for row in rows}),
                "failing_models": sorted({str(row.get("model_key")) for row in failures}),
                "error_classes": dict(Counter(str(row.get("error_class")) for row in rows)),
            }
        )
    summary["pair_count"] = len(by_pair)
    return {"summary": dict(summary), "pairs": pair_rows}


def build_markdown(rollup: dict[str, Any]) -> str:
    return (
        "# HoloVerify Stress Matrix Wave 1 Solo Scout Rollup\n\n"
        "Status: `SOLO_SCOUT_SCORED_POSTHOC`\n\n"
        f"- Run dir: `{rollup['run_dir']}`\n"
        f"- Packets: `{rollup['packet_count']}`\n"
        f"- Solo calls: `{rollup['solo_call_count']}`\n"
        f"- Trace hash: `{rollup['trace_binding']['trace_provider_calls_sha256']}`\n"
        f"- Scoring map hash: `{rollup['trace_binding']['scoring_map_sha256']}`\n\n"
        "## Aggregate\n\n"
        "```json\n"
        f"{json.dumps(rollup['aggregate'], indent=2, sort_keys=True)}\n"
        "```\n\n"
        "## Pair Summary\n\n"
        "```json\n"
        f"{json.dumps(rollup['pair_summary'], indent=2, sort_keys=True)}\n"
        "```\n\n"
        "## Claim Boundary\n\n"
        "Solo stress-matrix discovery only. No Holo, no Gov, no judges, and no public benchmark claim.\n"
    )


def score(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    trace_path = run_dir / "TRACE_PROVIDER_CALLS.jsonl"
    runtime_results_path = run_dir / "solo_one_shot_runtime_results.json"
    live_summary_path = run_dir / "solo_one_shot_live_summary.json"
    missing = [str(path) for path in (trace_path, runtime_results_path, live_summary_path) if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required frozen solo trace artifacts: {missing}")
    scoring_hash = sha256_file(SCORING_MAP)
    if scoring_hash != EXPECTED_SCORING_MAP_SHA256:
        raise RuntimeError(f"scoring_map_hash_mismatch:{scoring_hash}")

    runtime = load_json(runtime_results_path)
    provider_rows = load_jsonl(trace_path)
    scoring = load_json(SCORING_MAP)
    truth_by_opaque = {
        row["opaque_runtime_id"]: {
            "truth": row["truth"],
            "domain": row.get("domain_group"),
            "pair_id": row.get("pair_id"),
            "legacy_packet_id": row.get("legacy_design_packet_id"),
            "seam_class": row.get("seam_class"),
            "target_failure_shape": row.get("target_failure_shape"),
        }
        for row in scoring.get("rows", [])
    }
    provider_by_call = {row.get("call_number"): row for row in provider_rows}
    score_rows: list[dict[str, Any]] = []
    by_model: dict[str, Counter] = defaultdict(Counter)
    by_domain_model: dict[str, Counter] = defaultdict(Counter)
    packet_to_model_results: dict[str, list[dict[str, Any]]] = defaultdict(list)
    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    token_totals_by_model: dict[str, dict[str, int]] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})

    for provider in provider_rows:
        model_key = str(provider.get("model_key"))
        for key in token_totals:
            value = provider.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                token_totals_by_model[model_key][key] += value

    for index, row in enumerate(runtime.get("results", []), start=1):
        opaque = row.get("opaque_runtime_id")
        truth_meta = truth_by_opaque.get(opaque, {})
        truth = truth_meta.get("truth")
        verdict = row.get("final_verdict")
        admissible = bool(row.get("admissible"))
        correct = verdict == truth
        knew_admissible = admissible and correct
        cls = error_class(str(verdict), truth, admissible)
        model_key = str(row.get("model_key"))
        domain = str(truth_meta.get("domain"))
        scored = {
            "opaque_runtime_id": opaque,
            "domain": truth_meta.get("domain"),
            "pair_id": truth_meta.get("pair_id"),
            "legacy_packet_id": truth_meta.get("legacy_packet_id"),
            "seam_class": truth_meta.get("seam_class"),
            "target_failure_shape": truth_meta.get("target_failure_shape"),
            "model_key": model_key,
            "provider": row.get("provider"),
            "model": row.get("model"),
            "truth": truth,
            "solo_verdict": verdict,
            "solo_admissible": admissible,
            "solo_correct": correct,
            "solo_knew_admissible": knew_admissible,
            "error_class": cls,
            "gate_failures": (row.get("gate_result") or {}).get("failures", []),
            "trace_call_number": index,
            "provider_row": provider_by_call.get(index, {}),
        }
        score_rows.append(scored)
        packet_to_model_results[str(opaque)].append(scored)
        by_model[model_key]["total"] += 1
        by_model[model_key][cls] += 1
        by_model[model_key]["admissible"] += 1 if admissible else 0
        by_model[model_key]["correct"] += 1 if correct else 0
        by_model[model_key]["knew_admissible"] += 1 if knew_admissible else 0
        by_model[model_key]["false_positive"] += 1 if cls == "FALSE_POSITIVE_ESCALATE_ON_ALLOW" else 0
        by_model[model_key]["false_negative"] += 1 if cls == "FALSE_NEGATIVE_ALLOW_ON_ESCALATE" else 0
        domain_key = f"{domain}|{model_key}"
        by_domain_model[domain_key]["total"] += 1
        by_domain_model[domain_key]["knew_admissible"] += 1 if knew_admissible else 0
        by_domain_model[domain_key][cls] += 1

    packet_collapse_rows: list[dict[str, Any]] = []
    collapse_counts = Counter()
    for opaque, rows in packet_to_model_results.items():
        failures = [row for row in rows if not row["solo_knew_admissible"]]
        knew = [row for row in rows if row["solo_knew_admissible"]]
        if len(failures) == 3:
            collapse_class = "ALL_THREE_SOLO_COLLAPSE"
        elif len(failures) == 2:
            collapse_class = "TWO_OF_THREE_SOLO_COLLAPSE"
        elif len(failures) == 1:
            collapse_class = "ONE_OF_THREE_SOLO_COLLAPSE"
        else:
            collapse_class = "ALL_THREE_SOLO_KNEW"
        collapse_counts[collapse_class] += 1
        first = rows[0]
        packet_collapse_rows.append(
            {
                "opaque_runtime_id": opaque,
                "domain": first.get("domain"),
                "pair_id": first.get("pair_id"),
                "legacy_packet_id": first.get("legacy_packet_id"),
                "truth": first.get("truth"),
                "collapse_class": collapse_class,
                "solo_knew_count": len(knew),
                "solo_failure_count": len(failures),
                "model_outcomes": [
                    {
                        "model_key": item["model_key"],
                        "solo_verdict": item["solo_verdict"],
                        "solo_admissible": item["solo_admissible"],
                        "solo_knew_admissible": item["solo_knew_admissible"],
                        "error_class": item["error_class"],
                    }
                    for item in rows
                ],
            }
        )

    score_report = {
        "classification": "HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_POSTHOC_SCORE_V1",
        "run_dir": str(run_dir),
        "runtime_manifest": runtime.get("runtime_manifest"),
        "runtime_manifest_sha256": runtime.get("runtime_manifest_sha256"),
        "packet_count": runtime.get("packet_count"),
        "solo_call_count": len(score_rows),
        "models_per_packet": runtime.get("models_per_packet"),
        "trace_binding": {
            "trace_provider_calls_sha256": sha256_file(trace_path),
            "runtime_results_sha256": sha256_file(runtime_results_path),
            "live_summary_sha256": sha256_file(live_summary_path),
            "scoring_map_sha256": scoring_hash,
        },
        "scoring_map_loaded_after_trace_hash_binding": True,
        "score_rows": score_rows,
        "summary_by_model": {key: dict(counter) for key, counter in by_model.items()},
        "summary_by_domain_model": {key: dict(counter) for key, counter in by_domain_model.items()},
        "packet_collapse_summary": dict(collapse_counts),
        "packet_collapse_rows": sorted(packet_collapse_rows, key=lambda item: str(item["opaque_runtime_id"])),
        "token_totals": token_totals,
        "token_totals_by_model": dict(token_totals_by_model),
    }
    score_path = run_dir / "stress_matrix_wave1_solo_posthoc_score.json"
    write_json(score_path, score_report)

    aggregate = Counter()
    for row in score_rows:
        aggregate["solo_calls"] += 1
        aggregate[str(row.get("error_class"))] += 1
        aggregate["knew_admissible"] += 1 if row.get("solo_knew_admissible") else 0
        aggregate["correct"] += 1 if row.get("solo_correct") else 0
        aggregate["admissible"] += 1 if row.get("solo_admissible") else 0
        aggregate["false_positive"] += 1 if row.get("error_class") == "FALSE_POSITIVE_ESCALATE_ON_ALLOW" else 0
        aggregate["false_negative"] += 1 if row.get("error_class") == "FALSE_NEGATIVE_ALLOW_ON_ESCALATE" else 0
        aggregate["parse_or_admissibility_failure"] += 1 if row.get("error_class") == "PARSE_OR_ADMISSIBILITY_FAILURE" else 0

    rollup = {
        "classification": "HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_ROLLUP_V1",
        "status": "SOLO_SCOUT_SCORED_POSTHOC",
        "run_dir": str(run_dir),
        "score_ref": str(score_path),
        "packet_count": runtime.get("packet_count"),
        "solo_call_count": len(score_rows),
        "models_per_packet": runtime.get("models_per_packet"),
        "trace_binding": score_report["trace_binding"],
        "summary_by_model": score_report["summary_by_model"],
        "summary_by_domain_model": score_report["summary_by_domain_model"],
        "packet_collapse_summary": score_report["packet_collapse_summary"],
        "aggregate": dict(aggregate),
        "pair_summary": compact_pair_summary(score_rows),
        "token_totals": token_totals,
        "token_totals_by_model": dict(token_totals_by_model),
        "claim_boundary": "Solo stress-matrix discovery only. No Holo, no Gov, no judges, no public benchmark claim.",
    }
    write_json(ROLLUP_JSON, rollup)
    ROLLUP_MD.write_text(build_markdown(rollup))
    (run_dir / "stress_matrix_wave1_solo_posthoc_score.md").write_text(build_markdown(rollup))
    return rollup


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
