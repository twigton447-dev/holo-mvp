#!/usr/bin/env python3
"""Post-hoc scorer for the V6 broader validation Option B lane.

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
    / "holoverify_v6_broader_validation_option_b_2026_07_05"
    / "holoverify_v6_broader_validation_option_b_scoring_map_2026_07_05.json"
)
EXPECTED_SCORING_MAP_SHA256 = "453041b825f7052b33d1c5b343d62ff2fdfb842f11e96b0308a723a870285f7d"
EXPECTED_PACKET_COUNT = 20
EXPECTED_PAIR_COUNT = 10
EXPECTED_PROVIDER_CALL_COUNT = 100
CLEAN_VERDICT_TREATMENTS = {
    "clean_verdict_lane",
    "clean_verdict_lane_blocker_closure",
    "clean_verdict_lane_fp_overblock",
}
HELD_OUT_TREATMENTS = {
    "held_out_parse_admissibility",
    "quarantine_review_only_visible_key_sentinel",
}


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


def _pair_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_pair[str(row.get("pair_id"))].append(row)
    pair_rows = []
    for pair_id, items in sorted(by_pair.items()):
        pair_complete = len(items) == 2
        pair_rows.append(
            {
                "pair_id": pair_id,
                "packet_count": len(items),
                "pair_group_complete": pair_complete,
                "complete_pair_correct": pair_complete and all(item.get("correct") for item in items),
                "validation_lane": items[0].get("validation_lane") if items else None,
                "denominator_treatment": items[0].get("denominator_treatment") if items else None,
                "pair_credit": bool(items[0].get("pair_credit")) if items else False,
                "rows": sorted(items, key=lambda item: str(item.get("sibling"))),
            }
        )
    return pair_rows


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
    for row in runtime_result.get("results", []):
        packet_id = row.get("packet_id")
        final = row.get("final") or {}
        verdict = final.get("verdict")
        truth_meta = truth_by_opaque.get(packet_id, {})
        truth = truth_meta.get("legacy_truth")
        denominator_treatment = truth_meta.get("denominator_treatment")
        is_correct = verdict == truth
        scored_rows.append(
            {
                "opaque_runtime_id": packet_id,
                "legacy_packet_id": truth_meta.get("legacy_packet_id"),
                "pair_id": truth_meta.get("pair_id"),
                "sibling": truth_meta.get("sibling"),
                "truth": truth,
                "final_verdict": verdict,
                "correct": is_correct,
                "domain": truth_meta.get("domain"),
                "validation_lane": truth_meta.get("validation_lane"),
                "denominator_treatment": denominator_treatment,
                "pair_credit": truth_meta.get("pair_credit"),
                "visible_basis": truth_meta.get("visible_basis"),
                "final_artifact_id": final.get("artifact_id"),
                "deterministic_clean": final.get("deterministic_clean"),
                "unresolved_blocker_count": final.get("unresolved_blocker_count"),
                "invalid_closure_count": final.get("invalid_closure_count"),
            }
        )

    clean_rows = [row for row in scored_rows if row.get("denominator_treatment") in CLEAN_VERDICT_TREATMENTS]
    held_out_rows = [row for row in scored_rows if row.get("denominator_treatment") in HELD_OUT_TREATMENTS]
    clean_pair_rows = _pair_rows(clean_rows)
    all_pair_rows = _pair_rows(scored_rows)
    held_out_pair_rows = _pair_rows(held_out_rows)

    clean_correct = sum(1 for row in clean_rows if row.get("correct"))
    clean_incorrect_rows = [row for row in clean_rows if not row.get("correct")]
    clean_pairs_correct = sum(1 for row in clean_pair_rows if row.get("complete_pair_correct"))
    provider_failures = [
        row for row in provider_rows if row.get("provider_failure") or row.get("error") or row.get("exception") or not row.get("provider_call_ok", True)
    ]
    held_out_preserved = len(held_out_rows) == 4 and len(held_out_pair_rows) == 2
    passed_internal_validation = (
        len(scored_rows) == EXPECTED_PACKET_COUNT
        and len(all_pair_rows) == EXPECTED_PAIR_COUNT
        and len(clean_rows) == 16
        and clean_correct == 16
        and len(clean_pair_rows) == 8
        and clean_pairs_correct == 8
        and held_out_preserved
        and len(provider_rows) == EXPECTED_PROVIDER_CALL_COUNT
        and not provider_failures
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
        "classification": "HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_POSTHOC_SCORE_TRACE_BOUND_V1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "scoring_map_loaded_after_trace_hash_binding": True,
        "internal_validation_only": True,
        "trace_binding": {
            **trace_hashes,
            "scoring_map_sha256": scoring_map_sha256,
        },
        "packet_count": len(scored_rows),
        "pair_count": len(all_pair_rows),
        "clean_verdict_packet_count": len(clean_rows),
        "clean_verdict_correct_count": clean_correct,
        "clean_verdict_incorrect_count": len(clean_rows) - clean_correct,
        "clean_verdict_pair_count": len(clean_pair_rows),
        "clean_verdict_pairs_correct": clean_pairs_correct,
        "held_out_packet_count": len(held_out_rows),
        "held_out_pair_count": len(held_out_pair_rows),
        "held_out_preserved": held_out_preserved,
        "provider_call_count": len(provider_rows),
        "provider_failure_count": len(provider_failures),
        "passed_internal_validation": passed_internal_validation,
        "result_classification": (
            "V6_BROADER_INTERNAL_VALIDATION_OPTION_B_PASSED"
            if passed_internal_validation
            else "V6_BROADER_INTERNAL_VALIDATION_OPTION_B_FAILED"
        ),
        "failed_clean_packets": sorted(clean_incorrect_rows, key=lambda item: str(item.get("legacy_packet_id"))),
        "score_rows": sorted(scored_rows, key=lambda item: str(item.get("legacy_packet_id"))),
        "pair_rows": all_pair_rows,
        "clean_pair_rows": clean_pair_rows,
        "held_out_pair_rows": held_out_pair_rows,
        "lane_composition": scoring.get("lane_composition"),
        "token_totals": token_totals,
        "token_totals_by_slot": dict(token_totals_by_slot),
        "token_totals_by_provider": dict(token_totals_by_provider),
        "role_counts": dict(role_counts),
        "claim_boundary": {
            "allowed_internal_claim": (
                "V6 broader internal Option B validation passed with clean lanes separated from held-out lanes."
                if passed_internal_validation
                else None
            ),
            "not_allowed": [
                "public benchmark claim",
                "strict public denominator expansion",
                "global FNR claim",
                "global FPR claim",
                "FP precision claim",
                "general model superiority claim",
                "claim outside this internal broader V6 validation lane",
            ],
            "strict_public_denominator": "blind-120 only",
        },
    }
    write_json(run_dir / "v6_broader_validation_option_b_posthoc_score_trace_bound_v1.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(posthoc_score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
