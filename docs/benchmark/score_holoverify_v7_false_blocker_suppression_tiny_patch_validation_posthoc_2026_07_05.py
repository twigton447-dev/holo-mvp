#!/usr/bin/env python3
"""Post-hoc scorer for the V7 false-blocker tiny patch-validation lane."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_v7_false_blocker_suppression_tiny_patch_validation_2026_07_05"
    / "holoverify_v7_false_blocker_suppression_tiny_patch_validation_scoring_map_2026_07_05.json"
)
EXPECTED_SCORING_MAP_SHA256 = "d373168a818b5337855970a84217f7caf98e8c1f666dfa409ba4c78edc7a69bb"
EXPECTED_PACKET_COUNT = 6
EXPECTED_PAIR_COUNT = 3
EXPECTED_PROVIDER_CALL_COUNT = 30


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(errors="replace").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def pair_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_pair[str(row.get("pair_id"))].append(row)
    output = []
    for pair_id, items in sorted(by_pair.items()):
        output.append(
            {
                "pair_id": pair_id,
                "packet_count": len(items),
                "pair_group_complete": len(items) == 2,
                "complete_pair_correct": len(items) == 2 and all(item.get("correct") for item in items),
                "domain": items[0].get("domain") if items else None,
                "seam_class": items[0].get("seam_class") if items else None,
                "rows": sorted(items, key=lambda item: str(item.get("sibling"))),
            }
        )
    return output


def posthoc_score(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    trace_calls = run_dir / "TRACE_CALLS.jsonl"
    provider_trace = run_dir / "TRACE_PROVIDER_CALLS.jsonl"
    runtime_results = run_dir / "blind_canary_runtime_results.json"
    summary_path = run_dir / "blind_canary_live_summary.json"
    required = (trace_calls, provider_trace, runtime_results, summary_path)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required frozen trace artifacts: {missing}")

    scoring_map_sha256 = sha256_file(SCORING_MAP)
    if scoring_map_sha256 != EXPECTED_SCORING_MAP_SHA256:
        raise RuntimeError(f"scoring_map_hash_mismatch:{scoring_map_sha256}")

    scoring = load_json(SCORING_MAP)
    runtime_result = load_json(runtime_results)
    provider_rows = load_jsonl(provider_trace)
    truth_by_opaque = {row["opaque_runtime_id"]: row for row in scoring.get("scoring_rows", [])}

    scored_rows: list[dict[str, Any]] = []
    for row in runtime_result.get("results", []):
        packet_id = row.get("packet_id")
        final = row.get("final") or {}
        truth_meta = truth_by_opaque.get(packet_id, {})
        truth = truth_meta.get("legacy_truth")
        verdict = final.get("verdict")
        scored_rows.append(
            {
                "opaque_runtime_id": packet_id,
                "legacy_packet_id": truth_meta.get("legacy_packet_id"),
                "pair_id": truth_meta.get("pair_id"),
                "sibling": truth_meta.get("sibling"),
                "truth": truth,
                "final_verdict": verdict,
                "correct": verdict == truth,
                "domain": truth_meta.get("domain"),
                "seam_class": truth_meta.get("seam_class"),
                "final_artifact_id": final.get("artifact_id"),
                "deterministic_clean": final.get("deterministic_clean"),
                "unresolved_blocker_count": final.get("unresolved_blocker_count"),
                "invalid_closure_count": final.get("invalid_closure_count"),
            }
        )

    pairs = pair_rows(scored_rows)
    provider_failures = [
        row
        for row in provider_rows
        if row.get("provider_failure") or row.get("error") or row.get("exception") or not row.get("provider_call_ok", True)
    ]
    correct_count = sum(1 for row in scored_rows if row.get("correct"))
    pair_correct_count = sum(1 for row in pairs if row.get("complete_pair_correct"))
    passed_patch_validation = (
        len(scored_rows) == EXPECTED_PACKET_COUNT
        and len(pairs) == EXPECTED_PAIR_COUNT
        and correct_count == EXPECTED_PACKET_COUNT
        and pair_correct_count == EXPECTED_PAIR_COUNT
        and len(provider_rows) == EXPECTED_PROVIDER_CALL_COUNT
        and not provider_failures
    )

    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    token_totals_by_slot: dict[str, dict[str, int]] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    role_counts = Counter()
    for provider_row in provider_rows:
        slot = str(provider_row.get("slot"))
        role_counts[str(provider_row.get("role"))] += 1
        for key in token_totals:
            value = provider_row.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                token_totals_by_slot[slot][key] += value

    report = {
        "classification": "HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_POSTHOC_SCORE_TRACE_BOUND_V0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "scoring_map_loaded_after_trace_hash_binding": True,
        "tiny_patch_validation_only": True,
        "trace_binding": {
            "trace_calls_sha256": sha256_file(trace_calls),
            "trace_provider_calls_sha256": sha256_file(provider_trace),
            "runtime_results_sha256": sha256_file(runtime_results),
            "live_summary_sha256": sha256_file(summary_path),
            "scoring_map_sha256": scoring_map_sha256,
        },
        "packet_count": len(scored_rows),
        "pair_count": len(pairs),
        "correct_packet_count": correct_count,
        "incorrect_packet_count": len(scored_rows) - correct_count,
        "complete_pair_correct_count": pair_correct_count,
        "provider_call_count": len(provider_rows),
        "provider_failure_count": len(provider_failures),
        "passed_patch_validation": passed_patch_validation,
        "result_classification": (
            "V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_PASSED"
            if passed_patch_validation
            else "V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_FAILED"
        ),
        "selected_pairs": scoring.get("selected_pairs"),
        "score_rows": sorted(scored_rows, key=lambda item: str(item.get("legacy_packet_id"))),
        "pair_rows": pairs,
        "failed_packets": sorted([row for row in scored_rows if not row.get("correct")], key=lambda item: str(item.get("legacy_packet_id"))),
        "token_totals": token_totals,
        "token_totals_by_slot": dict(token_totals_by_slot),
        "role_counts": dict(role_counts),
        "claim_boundary": {
            "tiny_patch_validation_only": True,
            "public_benchmark_evidence": False,
            "holo_win": False,
            "global_fpr_or_fnr_claim": False,
            "fp_precision_evidence": False,
            "production_safety_certification": False,
        },
    }
    write_json(run_dir / "v7_false_blocker_suppression_tiny_patch_validation_posthoc_score_trace_bound_v0.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(posthoc_score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
