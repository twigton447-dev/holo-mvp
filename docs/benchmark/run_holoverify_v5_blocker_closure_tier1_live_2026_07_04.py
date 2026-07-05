#!/usr/bin/env python3
"""Run the V5 blocker-closure Tier 1 patch-validation lane.

This wrapper binds the blind runtime path to a two-packet runtime-only
manifest. It does not import or read mixed registration JSON during live
execution. Post-hoc scoring remains separate and may run only after trace
freeze.
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


RUNTIME_MANIFEST = BENCHMARK_ROOT / "HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER1_RUNTIME_MANIFEST_NO_TRUTH_2026_07_04.json"
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_v5_blocker_closure_tier1_2026_07_04" / "live_runs"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_solo_failure_factory_batch016_hard_authority_ambiguity_holo_rescue_posthoc_2026_07_04.py"

EXPECTED_RUNTIME_MANIFEST_SHA256 = "edd7ed59e0647c7695c62cf76ecb2f27b6d0b9b8ac8c25a21977607130c63a8d"
EXPECTED_SCORING_MAP_SHA256 = "8afbd63c792d12c26deb781b1de16d3db0c94e0414091e05e2cc4338975407be"
EXPECTED_PACKET_COUNT = 2
EXPECTED_CALL_COUNT = 10
LANE_LABEL = "HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER1_PATCH_VALIDATION_V0"
EVIDENCE_SCOPE = (
    "PATCH VALIDATION ONLY for V5 blocker closure validation on two Batch016 false-closure "
    "packets; not benchmark evidence, not pair-level evidence, and not public claim material."
)
SCORING_MAP_READ_GUARD_TEST = (
    "manual_no_provider_preflight:"
    "v5_tier1_live_wrapper_uses_runtime_only_manifest_and_does_not_read_registration_json"
)
WRAPPER_SCORING_SPLIT_TEST = (
    "manual_no_provider_preflight:"
    "v5_tier1_live_wrapper_does_not_keep_mixed_registration_json_path"
)


def scoped_approval_sentence() -> str:
    selector = CANARY.BLIND.selector_policy_identity()
    worker = CANARY.BLIND.worker_contract_identity()
    return (
        f"I approve live provider execution for {LANE_LABEL} using only runtime-only manifest "
        f"docs/benchmark/{RUNTIME_MANIFEST.name} with SHA-256 {EXPECTED_RUNTIME_MANIFEST_SHA256}, "
        f"selector {selector['selector_policy_version']} hash {selector['selector_policy_sha256']}, "
        f"worker contract {worker['worker_contract_version']} hash {worker['worker_contract_sha256']}, "
        "and exactly 10 provider calls: W1 xai/grok-3-mini x2, "
        "G1 minimax/MiniMax-M2.5-highspeed x2, W2 openai/gpt-5.4-mini x2, "
        "G2 minimax/MiniMax-M2.5-highspeed x2, W3 minimax/MiniMax-M2.5-highspeed x2. "
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
    report["classification"] = "HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER1_LIVE_PREFLIGHT_V0"
    report["lane_label"] = LANE_LABEL
    report["patch_validation_only"] = True
    report["evidence_scope"] = EVIDENCE_SCOPE
    report["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    report["mixed_registration_json_loaded_before_trace_freeze"] = False
    report["registration_json_live_input"] = False
    report["expected_provider_calls"] = EXPECTED_CALL_COUNT
    report["expected_call_sequence"] = ["W1", "G1", "W2", "G2", "W3"]
    report["live_command"] = (
        "python3 docs/benchmark/run_holoverify_v5_blocker_closure_tier1_live_2026_07_04.py "
        "--run-live --approval-statement \"$APPROVAL\""
    )
    report["approval_sentence"] = scoped_approval_sentence()
    CANARY.write_json(run_dir / "v5_blocker_closure_tier1_live_preflight.json", report)
    return report


def run_preflight_only() -> dict[str, Any]:
    configure_runtime()
    run_dir = LIVE_ROOT / f"preflight_{CANARY.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return preflight(run_dir)


def run_live(approval_statement: str) -> dict[str, Any]:
    configure_runtime()
    summary = CANARY.run_live(approval_statement)
    summary["classification"] = "HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER1_LIVE_RUN_SUMMARY_V0"
    summary["lane_label"] = LANE_LABEL
    summary["patch_validation_only"] = True
    summary["evidence_scope"] = EVIDENCE_SCOPE
    summary["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    summary["mixed_registration_json_loaded_before_trace_freeze"] = False
    run_dir = REPO_ROOT / summary["run_dir"]
    CANARY.write_json(run_dir / "v5_blocker_closure_tier1_live_summary.json", summary)
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
