#!/usr/bin/env python3
"""Run the V6 broader validation Option B lane.

This wrapper binds live execution to a 20-packet runtime-only manifest.
It does not import or read mixed registration JSON or scoring maps during
live execution. Post-hoc scoring remains separate and may run only after
trace freeze.
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


RUNTIME_MANIFEST = BENCHMARK_ROOT / "HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json"
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_v6_broader_validation_option_b_2026_07_05" / "live_runs"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_v6_broader_validation_option_b_posthoc_2026_07_05.py"

EXPECTED_RUNTIME_MANIFEST_SHA256 = "a849152c6e2c86835f7108b95aa1f168242908e169ffe3fcf35274fd3b10cfd0"
EXPECTED_SCORING_MAP_SHA256 = "453041b825f7052b33d1c5b343d62ff2fdfb842f11e96b0308a723a870285f7d"
EXPECTED_PACKET_COUNT = 20
EXPECTED_CALL_COUNT = 100
LANE_LABEL = "HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_V0"
EVIDENCE_SCOPE = (
    "INTERNAL BROADER V6 VALIDATION ONLY across separated source-field FN, "
    "blocker-closure, exact-boundary FP overblock, parse/admissibility held-out, "
    "and packet-key quarantine lanes; not public benchmark evidence, not a global "
    "FNR/FPR claim, not FP precision evidence, not general model superiority, and "
    "the strict public denominator remains blind-120 only."
)
SCORING_MAP_READ_GUARD_TEST = (
    "manual_no_provider_preflight:"
    "v6_broader_validation_option_b_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map"
)
WRAPPER_SCORING_SPLIT_TEST = (
    "manual_no_provider_preflight:"
    "v6_broader_validation_option_b_live_wrapper_does_not_keep_mixed_registration_json_path"
)
LANE_COMPOSITION = {
    "source_field_authority_scope_fn": {"pairs": 4, "packets": 8},
    "blocker_closure": {"pairs": 2, "packets": 4},
    "exact_boundary_fp_overblock": {"pairs": 2, "packets": 4},
    "parse_admissibility_held_out": {"pairs": 1, "packets": 2},
    "packet_key_defect_quarantine": {"pairs": 1, "packets": 2},
}


def scoped_approval_sentence() -> str:
    selector = CANARY.BLIND.selector_policy_identity()
    worker = CANARY.BLIND.worker_contract_identity()
    return (
        f"I approve live provider execution for {LANE_LABEL} using only runtime-only manifest "
        f"docs/benchmark/{RUNTIME_MANIFEST.name} with SHA-256 {EXPECTED_RUNTIME_MANIFEST_SHA256}, "
        f"selector {selector['selector_policy_version']} hash {selector['selector_policy_sha256']}, "
        f"worker contract {worker['worker_contract_version']} hash {worker['worker_contract_sha256']}, "
        "and exactly 100 provider calls: W1 xai/grok-3-mini x20, "
        "G1 minimax/MiniMax-M2.5-highspeed x20, W2 openai/gpt-5.4-mini x20, "
        "G2 minimax/MiniMax-M2.5-highspeed x20, W3 minimax/MiniMax-M2.5-highspeed x20. "
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
    report["classification"] = "HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_PREFLIGHT_V0"
    report["lane_label"] = LANE_LABEL
    report["internal_validation_only"] = True
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
    report["lane_composition"] = LANE_COMPOSITION
    report["scope_boundary"] = {
        "internal_broader_v6_validation_only": True,
        "public_benchmark_evidence": False,
        "global_fnr_or_fpr_claim": False,
        "fp_precision_evidence": False,
        "general_model_superiority": False,
        "strict_public_denominator": "blind-120 only",
    }
    report["live_command"] = (
        "python3 docs/benchmark/run_holoverify_v6_broader_validation_option_b_live_2026_07_05.py "
        "--run-live --approval-statement \"$APPROVAL\""
    )
    report["approval_sentence"] = scoped_approval_sentence()
    CANARY.write_json(run_dir / "v6_broader_validation_option_b_live_preflight.json", report)
    return report


def run_preflight_only() -> dict[str, Any]:
    configure_runtime()
    run_dir = LIVE_ROOT / f"preflight_{CANARY.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return preflight(run_dir)


def run_live(approval_statement: str) -> dict[str, Any]:
    configure_runtime()
    summary = CANARY.run_live(approval_statement)
    summary["classification"] = "HOLOVERIFY_V6_BROADER_VALIDATION_OPTION_B_LIVE_RUN_SUMMARY_V0"
    summary["lane_label"] = LANE_LABEL
    summary["internal_validation_only"] = True
    summary["evidence_scope"] = EVIDENCE_SCOPE
    summary["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    summary["mixed_registration_json_loaded_before_trace_freeze"] = False
    summary["lane_composition"] = LANE_COMPOSITION
    run_dir = REPO_ROOT / summary["run_dir"]
    CANARY.write_json(run_dir / "v6_broader_validation_option_b_live_summary.json", summary)
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
