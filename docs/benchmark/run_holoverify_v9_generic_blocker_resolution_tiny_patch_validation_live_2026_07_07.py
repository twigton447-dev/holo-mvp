#!/usr/bin/env python3
"""Run the V9 generic blocker-resolution tiny patch-validation lane.

This wrapper binds live execution to a six-packet runtime-only manifest.
Truth and scoring data stay in the separate post-hoc scorer after trace
freeze. Preflight and prompt probe are no-provider only.
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


RUNTIME_MANIFEST = BENCHMARK_ROOT / "HOLOVERIFY_V9_GENERIC_BLOCKER_RESOLUTION_TINY_PATCH_VALIDATION_RUNTIME_MANIFEST_NO_TRUTH_2026_07_07.json"
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_v9_generic_blocker_resolution_tiny_patch_validation_2026_07_07" / "live_runs"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_v9_generic_blocker_resolution_tiny_patch_validation_posthoc_2026_07_07.py"

EXPECTED_RUNTIME_MANIFEST_SHA256 = "c9087ce57bd39aab8e3e202192c1aea6df31ee2a6b3d7842f1a7832a6c829da5"
EXPECTED_SCORING_MAP_SHA256 = "a3f97a0764add4b6dd20ae222e92b8040f8406c748fba8a9c655dab7124fa331"
EXPECTED_PACKET_COUNT = 6
EXPECTED_CALL_COUNT = 30
EXPECTED_SELECTOR_VERSION = "SELECTOR_V9_GENERIC_BLOCKER_RESOLUTION_2026_07_06"
EXPECTED_SELECTOR_SHA256 = "cb53549bcc01d882836fc47e68e1ec5610b302cdbd8ddfd1967f7fac5a235416"
EXPECTED_DIMENSION_EQUIVALENCE_TABLE_SHA256 = "3cbd70cf843b4c050a3fe4c51d7910b2c25c0f41a18c053ab6d6260d4879a450"
EXPECTED_GENERIC_PHRASE_FAMILY_SHA256 = "de6cc3a4082fc0f5a5b8098bbb264edd6c85711265d8ecf19263aeb456dabfed"
LANE_LABEL = "HOLOVERIFY_V9_GENERIC_BLOCKER_RESOLUTION_TINY_PATCH_VALIDATION_V0"
EVIDENCE_SCOPE = (
    "TINY SAME-SET V9 VALIDATION ONLY for V9 generic blocker resolution across "
    "HVSM-W2-010 and HVSM-W2-027 remaining V8 ALLOW failures, HVSM-W2-009 "
    "ALLOW stability control, and the three matched ESCALATE catastrophic-direction controls; "
    "not public benchmark evidence, not a Holo win, not a global FPR/FNR claim, "
    "not FP precision evidence, not production-rate evidence, and not production-safety evidence."
)
SCORING_MAP_READ_GUARD_TEST = (
    "manual_no_provider_preflight:"
    "v9_generic_blocker_resolution_tiny_patch_validation_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map"
)
WRAPPER_SCORING_SPLIT_TEST = (
    "manual_no_provider_preflight:"
    "v9_generic_blocker_resolution_tiny_patch_validation_live_wrapper_does_not_keep_mixed_registration_json_path"
)
SELECTED_PAIRS = [
    "HVSM-W2-009",
    "HVSM-W2-010",
    "HVSM-W2-027"
]
SELECTED_PACKETS = [
    "HVSM-W2-009-A",
    "HVSM-W2-009-E",
    "HVSM-W2-010-A",
    "HVSM-W2-010-E",
    "HVSM-W2-027-A",
    "HVSM-W2-027-E"
]


def scoped_approval_sentence() -> str:
    selector = CANARY.BLIND.selector_policy_identity()
    worker = CANARY.BLIND.worker_contract_identity()
    if selector.get("selector_policy_version") != EXPECTED_SELECTOR_VERSION:
        raise RuntimeError(f"selector_version_mismatch:{selector.get('selector_policy_version')}")
    if selector.get("selector_policy_sha256") != EXPECTED_SELECTOR_SHA256:
        raise RuntimeError(f"selector_hash_mismatch:{selector.get('selector_policy_sha256')}")
    return (
        f"I approve live provider execution for {LANE_LABEL} using only runtime-only manifest "
        f"docs/benchmark/{RUNTIME_MANIFEST.name} with SHA-256 {EXPECTED_RUNTIME_MANIFEST_SHA256}, "
        f"selector {selector['selector_policy_version']} hash {selector['selector_policy_sha256']}, "
        f"worker contract {worker['worker_contract_version']} hash {worker['worker_contract_sha256']}, "
        "and exactly 30 provider calls: W1 xai/grok-3-mini x6, "
        "G1 minimax/MiniMax-M2.5-highspeed x6, W2 openai/gpt-5.4-mini x6, "
        "G2 minimax/MiniMax-M2.5-highspeed x6, W3 minimax/MiniMax-M2.5-highspeed x6. "
        f"{EVIDENCE_SCOPE} No solo, no judges, no scoring map before trace freeze, "
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
    selector = CANARY.BLIND.selector_policy_identity()
    report["classification"] = "HOLOVERIFY_V9_GENERIC_BLOCKER_RESOLUTION_TINY_PATCH_VALIDATION_PREFLIGHT_V0"
    report["lane_label"] = LANE_LABEL
    report["tiny_same_set_v9_validation_only"] = True
    report["evidence_scope"] = EVIDENCE_SCOPE
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
    report["selector_expected"] = {
        "selector_policy_version": EXPECTED_SELECTOR_VERSION,
        "selector_policy_sha256": EXPECTED_SELECTOR_SHA256,
        "dimension_equivalence_table_sha256": EXPECTED_DIMENSION_EQUIVALENCE_TABLE_SHA256,
        "generic_phrase_family_sha256": EXPECTED_GENERIC_PHRASE_FAMILY_SHA256,
    }
    report["selector_observed"] = selector
    report["scope_boundary"] = {
        "tiny_same_set_v9_validation_only": True,
        "public_benchmark_evidence": False,
        "holo_win": False,
        "global_fpr_or_fnr_claim": False,
        "fp_precision_evidence": False,
        "production_rate_evidence": False,
        "production_safety_evidence": False,
        "generalized_holo_win": False,
    }
    report["pass_condition_for_future_live"] = {
        "provider_calls": "30/30",
        "provider_failures": 0,
        "substitutions": 0,
        "trace_frozen_before_scoring": True,
        "packet_score": "6/6",
        "pair_score": "3/3",
        "allow_siblings_final_allow": True,
        "escalate_siblings_final_escalate": True,
        "null_or_no_select": 0,
    }
    report["live_command"] = (
        "python3 docs/benchmark/run_holoverify_v9_generic_blocker_resolution_tiny_patch_validation_live_2026_07_07.py "
        "--run-live --approval-statement \"$APPROVAL\""
    )
    report["approval_sentence"] = scoped_approval_sentence()
    CANARY.write_json(run_dir / "v9_generic_blocker_resolution_tiny_patch_validation_preflight.json", report)
    return report


def run_preflight_only() -> dict[str, Any]:
    configure_runtime()
    run_dir = LIVE_ROOT / f"preflight_{CANARY.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return preflight(run_dir)


def run_live(approval_statement: str) -> dict[str, Any]:
    configure_runtime()
    summary = CANARY.run_live(approval_statement)
    summary["classification"] = "HOLOVERIFY_V9_GENERIC_BLOCKER_RESOLUTION_TINY_PATCH_VALIDATION_LIVE_SUMMARY_V0"
    summary["lane_label"] = LANE_LABEL
    summary["tiny_same_set_v9_validation_only"] = True
    summary["evidence_scope"] = EVIDENCE_SCOPE
    summary["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    summary["mixed_registration_json_loaded_before_trace_freeze"] = False
    summary["selected_pairs"] = SELECTED_PAIRS
    summary["selected_packets"] = SELECTED_PACKETS
    run_dir = REPO_ROOT / summary["run_dir"]
    CANARY.write_json(run_dir / "v9_generic_blocker_resolution_tiny_patch_validation_live_summary.json", summary)
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
