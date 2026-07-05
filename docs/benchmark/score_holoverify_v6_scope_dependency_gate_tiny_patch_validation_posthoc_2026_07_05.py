#!/usr/bin/env python3
"""Post-hoc scorer for the V6 scope-dependency tiny patch-validation lane.

The live wrapper freezes runtime traces only. This scorer may be run after
trace freeze to load the hidden scoring map and bind the score artifact to
the exact trace hashes.
"""

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
    / "holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05"
    / "holoverify_v6_scope_dependency_gate_tiny_patch_validation_scoring_map_2026_07_05.json"
)
EXPECTED_SCORING_MAP_SHA256 = "21331ccae3d2d3626b6ce1fb3429d47f9bff5f69dcdb9fddf65a7cec37b90f5e"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(errors="replace"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(errors="replace").splitlines() if line.strip()]


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


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

    trace_hashes = {
        "trace_calls_sha256": sha256_file(trace_calls),
        "trace_provider_calls_sha256": sha256_file(provider_trace),
        "runtime_results_sha256": sha256_file(runtime_results),
        "live_summary_sha256": sha256_file(summary_path),
    }

    scoring_map_sha256 = sha256_file(SCORING_MAP)
    if scoring_map_sha256 != EXPECTED_SCORING_MAP_SHA256:
        raise RuntimeError(f"scoring_map_hash_mismatch:{scoring_map_sha256}")

    scoring = load_json(SCORING_MAP)
    runtime_result = load_json(runtime_results)
    provider_rows = load_jsonl(provider_trace)
    truth_by_opaque = {row["opaque_runtime_id"]: row for row in scoring.get("scoring_rows", [])}

    scored_rows: list[dict[str, Any]] = []
    correct = 0
    pair_results: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in runtime_result.get("results", []):
        packet_id = row.get("packet_id")
        final = row.get("final") or {}
        verdict = final.get("verdict")
        truth_meta = truth_by_opaque.get(packet_id, {})
        truth = truth_meta.get("legacy_truth")
        is_correct = verdict == truth
        correct += 1 if is_correct else 0
        scored = {
            "opaque_runtime_id": packet_id,
            "legacy_packet_id": truth_meta.get("legacy_packet_id"),
            "pair_id": truth_meta.get("pair_id"),
            "sibling": truth_meta.get("sibling"),
            "truth": truth,
            "final_verdict": verdict,
            "correct": is_correct,
            "domain": truth_meta.get("domain"),
            "source_batch": truth_meta.get("source_batch"),
            "v6_expected_check_id": truth_meta.get("v6_expected_check_id"),
            "final_artifact_id": final.get("artifact_id"),
        }
        scored_rows.append(scored)
        pair_results[str(truth_meta.get("pair_id"))].append(scored)

    pair_rows: list[dict[str, Any]] = []
    complete_pair_count = 0
    pairs_both_siblings_correct = 0
    for pair_id, rows in sorted(pair_results.items()):
        pair_complete = len(rows) == 2
        complete_pair_count += 1 if pair_complete else 0
        pair_correct = pair_complete and all(row["correct"] for row in rows)
        pairs_both_siblings_correct += 1 if pair_correct else 0
        pair_rows.append(
            {
                "pair_id": pair_id,
                "packet_count": len(rows),
                "pair_group_complete": pair_complete,
                "complete_pair_correct": pair_correct,
                "rows": sorted(rows, key=lambda item: str(item.get("sibling"))),
            }
        )

    incorrect_rows = [row for row in scored_rows if not row["correct"]]
    passed_patch_validation = (
        len(scored_rows) == 4
        and correct == 4
        and complete_pair_count == 2
        and pairs_both_siblings_correct == 2
    )

    token_totals: dict[str, int] = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    token_totals_by_slot: dict[str, dict[str, int]] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    token_totals_by_provider: dict[str, dict[str, int]] = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
    role_counts = Counter()
    for row in provider_rows:
        slot = str(row.get("slot"))
        provider = str(row.get("provider"))
        role = str(row.get("role"))
        role_counts[role] += 1
        for key in token_totals:
            value = row.get(key)
            if isinstance(value, int):
                token_totals[key] += value
                token_totals_by_slot[slot][key] += value
                token_totals_by_provider[provider][key] += value

    report = {
        "classification": "HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_POSTHOC_SCORE_TRACE_BOUND_V1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "scoring_map_loaded_after_trace_hash_binding": True,
        "patch_validation_only": True,
        "trace_binding": {
            **trace_hashes,
            "scoring_map_sha256": scoring_map_sha256,
        },
        "packet_count": len(scored_rows),
        "correct_count": correct,
        "incorrect_count": len(scored_rows) - correct,
        "pair_count": complete_pair_count,
        "complete_pair_count": complete_pair_count,
        "pairs_both_siblings_correct": pairs_both_siblings_correct,
        "passed_patch_validation": passed_patch_validation,
        "result_classification": (
            "V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_PASSED"
            if passed_patch_validation
            else "V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_FAILED"
        ),
        "failed_packets": sorted(incorrect_rows, key=lambda item: str(item.get("legacy_packet_id"))),
        "score_rows": sorted(scored_rows, key=lambda item: str(item.get("legacy_packet_id"))),
        "pair_rows": pair_rows,
        "token_totals": token_totals,
        "token_totals_by_slot": dict(token_totals_by_slot),
        "token_totals_by_provider": dict(token_totals_by_provider),
        "role_counts": dict(role_counts),
        "claim_boundary": {
            "allowed_internal_claim": (
                "V6 corrected the two known Tier 3 scope-dependency fixtures under tiny patch validation."
                if passed_patch_validation
                else None
            ),
            "not_allowed": [
                "public benchmark claim",
                "general model superiority claim",
                "global FNR claim",
                "FP precision claim",
                "claim outside this four-packet patch-validation lane",
                "claim before independent audit reviews trace and scorer",
            ],
        },
    }
    write_json(run_dir / "v6_scope_dependency_gate_tiny_patch_validation_posthoc_score_trace_bound_v1.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(posthoc_score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
