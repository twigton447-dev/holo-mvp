#!/usr/bin/env python3
"""Run the 300-dot V8 FP-overblock balanced five-pair Holo rescue rerun lane.

This wrapper is for internal Holo/V8 rescue rerun validation only. It binds live
execution to a runtime-only manifest and leaves truth/scoring data to the
separate post-hoc scorer after trace freeze.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))

import run_holoverify_blind_canary_live_2026_07_02 as CANARY  # noqa: E402


RUNTIME_MANIFEST = (
    BENCHMARK_ROOT
    / "HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json"
)
LIVE_ROOT = (
    BENCHMARK_ROOT
    / "holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06"
    / "live_runs"
)
POSTHOC_SCORING_SCRIPT = (
    BENCHMARK_ROOT
    / "score_holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_posthoc_2026_07_06.py"
)

EXPECTED_RUNTIME_MANIFEST_SHA256 = "5853f5d8257109199b4a98a18b11f8a9b339d5555093b8c1d89fccb89acd2f3c"
EXPECTED_SCORING_MAP_SHA256 = "bae892dad8398ed5ea18bfe0294d3c93e039ab1589bbe11c5f4384d370634f0b"
EXPECTED_PACKET_COUNT = 10
EXPECTED_CALL_COUNT = 50
LANE_LABEL = "HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_V0"
SELECTION_BASIS = (
    "Selected from observed 300-dot solo outcomes as pure FP-overblock all-three-collapse "
    "ALLOW cases, regardless of original authoring target lane; rerun under V8 after tiny validation passed."
)
EVIDENCE_SCOPE = (
    "INTERNAL HOLO/V8 RESCUE RERUN ONLY from the 300-dot stress baseline; "
    "not public benchmark evidence, not a global FPR/FNR claim, not production-rate "
    "evidence, not FP precision evidence, and not a Holo win until measured."
)
SCORING_MAP_READ_GUARD_TEST = (
    "manual_no_provider_preflight:"
    "300dot_v8_fp_overblock_balanced_5pair_rerun_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map"
)
WRAPPER_SCORING_SPLIT_TEST = (
    "manual_no_provider_preflight:"
    "300dot_v8_fp_overblock_balanced_5pair_rerun_live_wrapper_does_not_keep_mixed_registration_json_path"
)
SELECTED_PAIRS = [
    "HVSM-W2-009",
    "HVSM-W2-010",
    "HVSM-W2-020",
    "HVSM-W2-027",
    "HVSM-W2-030",
]
SELECTED_PACKETS = [
    "HVSM-W2-009-A",
    "HVSM-W2-009-E",
    "HVSM-W2-010-A",
    "HVSM-W2-010-E",
    "HVSM-W2-020-A",
    "HVSM-W2-020-E",
    "HVSM-W2-027-A",
    "HVSM-W2-027-E",
    "HVSM-W2-030-A",
    "HVSM-W2-030-E",
]


def scoped_approval_sentence() -> str:
    selector = CANARY.BLIND.selector_policy_identity()
    worker = CANARY.BLIND.worker_contract_identity()
    return (
        f"I approve live provider execution for {LANE_LABEL} using only runtime-only manifest "
        f"docs/benchmark/{RUNTIME_MANIFEST.name} with SHA-256 {EXPECTED_RUNTIME_MANIFEST_SHA256}, "
        f"selector {selector['selector_policy_version']} hash {selector['selector_policy_sha256']}, "
        f"worker contract {worker['worker_contract_version']} hash {worker['worker_contract_sha256']}, "
        "and exactly 50 provider calls: W1 xai/grok-3-mini x10, "
        "G1 minimax/MiniMax-M2.5-highspeed x10, W2 openai/gpt-5.4-mini x10, "
        "G2 minimax/MiniMax-M2.5-highspeed x10, W3 minimax/MiniMax-M2.5-highspeed x10. "
        f"{EVIDENCE_SCOPE} {SELECTION_BASIS} No solo, no judges, no scoring map before trace freeze, "
        "no mixed registration JSON before trace freeze, no substitutions, no public claims."
    )


def configure_runtime() -> None:
    CANARY.RUNTIME_MANIFEST = RUNTIME_MANIFEST
    CANARY.LIVE_ROOT = LIVE_ROOT
    CANARY.EXPECTED_RUNTIME_MANIFEST_SHA256 = EXPECTED_RUNTIME_MANIFEST_SHA256
    CANARY.EXPECTED_SCORING_MAP_SHA256 = EXPECTED_SCORING_MAP_SHA256
    CANARY.EXPECTED_PACKET_COUNT = EXPECTED_PACKET_COUNT
    CANARY.EXPECTED_CALL_COUNT = EXPECTED_CALL_COUNT
    CANARY.POSTHOC_SCORING_SCRIPT = POSTHOC_SCORING_SCRIPT
    CANARY.SCORING_MAP_READ_GUARD_TEST = SCORING_MAP_READ_GUARD_TEST
    CANARY.WRAPPER_SCORING_SPLIT_TEST = WRAPPER_SCORING_SPLIT_TEST
    CANARY.EXACT_APPROVAL_SENTENCE = scoped_approval_sentence()
    CANARY.scoped_approval_sentence = lambda packet_limit=None, packet_index=1: scoped_approval_sentence()


def preflight(run_dir: Path) -> dict[str, Any]:
    configure_runtime()
    report = CANARY.preflight(run_dir, RUNTIME_MANIFEST)
    report["classification"] = "HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_PREFLIGHT_V0"
    report["lane_label"] = LANE_LABEL
    report["internal_holo_v8_rescue_rerun_only"] = True
    report["evidence_scope"] = EVIDENCE_SCOPE
    report["selection_basis"] = SELECTION_BASIS
    report["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    report["mixed_registration_json_loaded_before_trace_freeze"] = False
    report["registration_json_live_input"] = False
    report["expected_provider_calls"] = EXPECTED_CALL_COUNT
    report["expected_call_sequence"] = ["W1", "G1", "W2", "G2", "W3"]
    report["expected_provider_calls_by_slot"] = {
        "W1": {"provider": "xai", "model": "grok-3-mini", "calls": EXPECTED_PACKET_COUNT},
        "G1": {"provider": "minimax", "model": "MiniMax-M2.5-highspeed", "calls": EXPECTED_PACKET_COUNT},
        "W2": {"provider": "openai", "model": "gpt-5.4-mini", "calls": EXPECTED_PACKET_COUNT},
        "G2": {"provider": "minimax", "model": "MiniMax-M2.5-highspeed", "calls": EXPECTED_PACKET_COUNT},
        "W3": {"provider": "minimax", "model": "MiniMax-M2.5-highspeed", "calls": EXPECTED_PACKET_COUNT},
    }
    report["selected_pairs"] = SELECTED_PAIRS
    report["selected_packets"] = SELECTED_PACKETS
    report["pass_condition"] = {
        "provider_calls": "50/50",
        "provider_failures": 0,
        "packet_score": "10/10",
        "pair_score": "5/5",
        "allow_siblings_final_allow": True,
        "escalate_siblings_final_escalate": True,
        "no_null_or_no_select": True,
    }
    report["patch_required_if"] = [
        "Any ALLOW sibling returns ESCALATE or null/no-select.",
        "Any ESCALATE sibling returns ALLOW.",
        "Any control, trace-freeze, substitution, or scoring-order invariant fails.",
    ]
    report["scope_boundary"] = {
        "internal_holo_v8_rescue_rerun_only": True,
        "public_benchmark_evidence": False,
        "global_fpr_or_fnr_claim": False,
        "production_rate_evidence": False,
        "fp_precision_evidence": False,
        "holo_win_until_measured": False,
    }
    report["live_command"] = (
        "python3 docs/benchmark/run_holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_live_2026_07_06.py "
        "--run-live --approval-statement \"$APPROVAL\""
    )
    report["approval_sentence"] = scoped_approval_sentence()
    CANARY.write_json(run_dir / "300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_preflight.json", report)
    return report


def run_preflight_only() -> dict[str, Any]:
    configure_runtime()
    run_dir = LIVE_ROOT / f"preflight_{CANARY.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return preflight(run_dir)


def run_live(approval_statement: str) -> dict[str, Any]:
    configure_runtime()
    summary = CANARY.run_live(approval_statement)
    summary["classification"] = "HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_LIVE_SUMMARY_V0"
    summary["lane_label"] = LANE_LABEL
    summary["internal_holo_v8_rescue_rerun_only"] = True
    summary["evidence_scope"] = EVIDENCE_SCOPE
    summary["selection_basis"] = SELECTION_BASIS
    summary["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    summary["mixed_registration_json_loaded_before_trace_freeze"] = False
    summary["selected_pairs"] = SELECTED_PAIRS
    summary["selected_packets"] = SELECTED_PACKETS
    run_dir = REPO_ROOT / summary["run_dir"]
    CANARY.write_json(run_dir / "300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_live_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--print-approval", action="store_true")
    parser.add_argument("--approval-statement", default="")
    args = parser.parse_args()

    if sum(bool(value) for value in (args.preflight, args.run_live, args.print_approval)) != 1:
        raise SystemExit("choose exactly one of --preflight, --run-live, or --print-approval")
    if args.print_approval:
        configure_runtime()
        print(scoped_approval_sentence())
        return 0
    if args.preflight:
        print(json.dumps(run_preflight_only(), indent=2, sort_keys=True))
        return 0
    print(json.dumps(run_live(args.approval_statement), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
