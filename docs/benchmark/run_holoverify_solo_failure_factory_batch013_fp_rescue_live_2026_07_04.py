#!/usr/bin/env python3
"""Run the Batch013 false-positive Holo rescue runtime-firewall lane.

This wrapper binds the blind canary live runtime path to the 5-pair Batch013
exact-boundary false-positive rescue bank. It does not load the scoring map
during live execution; scoring is a separate post-freeze step.
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


OUT_DIR = BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch013_fp_rescue_2026_07_04"
RUNTIME_MANIFEST = OUT_DIR / "holoverify_solo_failure_factory_batch013_fp_rescue_runtime_manifest_2026_07_04.json"
HASH_MANIFEST = OUT_DIR / "holoverify_solo_failure_factory_batch013_fp_rescue_hash_manifest_2026_07_04.json"
LIVE_ROOT = OUT_DIR / "live_runs"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_solo_failure_factory_batch013_fp_rescue_posthoc_2026_07_04.py"

# These are patched after build by the no-provider freeze step.
FREEZE_ROOT_SHA256 = "00d5552bb1dbf93b5abeb661989ba432e46502b1161a250ceb57919b78b7d7ef"
EXPECTED_RUNTIME_MANIFEST_SHA256 = "39fcdb352ecce3b3ede2579216a422714c2af197772b7f0e67068daa7f80ac65"
EXPECTED_SCORING_MAP_SHA256 = "c4dcd51b3a193c4bff7f199556d0e7d5e25eea4ce53adeafea37cb0dc32332e7"
EXPECTED_PACKET_COUNT = 10
EXPECTED_CALL_COUNT = 50
LANE_LABEL = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH013_FP_RESCUE_5PAIR_RUNTIME_FIREWALL_V0"
EVIDENCE_SCOPE = (
    "FRESH DIRECTIONAL FALSE-POSITIVE HOLO RESCUE SIGNAL ONLY for selected Batch013 "
    "exact-boundary solo overblock pairs; not public benchmark evidence and not an "
    "error-rate denominator."
)

SCORING_MAP_READ_GUARD_TEST = (
    "manual_no_provider_preflight:"
    "batch013_fp_rescue_live_wrapper_does_not_read_scoring_map_bytes"
)
WRAPPER_SCORING_SPLIT_TEST = (
    "manual_no_provider_preflight:"
    "batch013_fp_rescue_live_wrapper_does_not_keep_scoring_map_path"
)


def scoped_approval_sentence(packet_limit: int | None = None, packet_index: int = 1) -> str:
    selector_policy = CANARY.BLIND.selector_policy_identity()
    selector_version = selector_policy["selector_policy_version"]
    selector_hash = selector_policy["selector_policy_sha256"]
    worker_contract = CANARY.BLIND.worker_contract_identity()
    worker_contract_version = worker_contract["worker_contract_version"]
    worker_contract_hash = worker_contract["worker_contract_sha256"]
    if packet_limit is None:
        packet_limit = EXPECTED_PACKET_COUNT
        packet_index = 1
    if packet_limit <= 0:
        raise ValueError("packet_limit must be positive")
    end_index = packet_index + packet_limit - 1
    total_calls = packet_limit * len(CANARY.CALL_SEQUENCE)
    return (
        f"I approve live provider execution for {LANE_LABEL} using freeze root {FREEZE_ROOT_SHA256}, "
        f"runtime manifest {EXPECTED_RUNTIME_MANIFEST_SHA256}, opaque packet indices {packet_index}-{end_index} only, "
        f"and exactly {total_calls} provider calls: W1 xai/grok-3-mini x{packet_limit}, "
        f"G1 minimax/MiniMax-M2.5-highspeed x{packet_limit}, W2 openai/gpt-5.4-mini x{packet_limit}, "
        f"G2 minimax/MiniMax-M2.5-highspeed x{packet_limit}, W3 minimax/MiniMax-M2.5-highspeed x{packet_limit}. "
        f"Selector policy {selector_version} hash {selector_hash}. "
        f"Worker contract {worker_contract_version} hash {worker_contract_hash}. {EVIDENCE_SCOPE} "
        "No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims."
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
    CANARY.scoped_approval_sentence = scoped_approval_sentence


def freeze_root_from_hash_manifest() -> str:
    data = json.loads(HASH_MANIFEST.read_text(errors="replace"))
    return str(data.get("freeze_root_sha256") or "")


def preflight(run_dir: Path, runtime_manifest_path: Path = RUNTIME_MANIFEST) -> dict[str, Any]:
    configure_runtime()
    report = CANARY.preflight(run_dir, runtime_manifest_path)
    report["classification"] = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH013_FP_RESCUE_LIVE_PREFLIGHT_V0"
    report["freeze_root_sha256"] = FREEZE_ROOT_SHA256
    report["freeze_root_matches_hash_manifest"] = freeze_root_from_hash_manifest() == FREEZE_ROOT_SHA256
    report["lane_label"] = LANE_LABEL
    report["directional_evidence_only"] = True
    report["evidence_scope"] = EVIDENCE_SCOPE
    report["rescue_falsifier"] = (
        "If Holo fails to ALLOW any selected clean A sibling or fails to ESCALATE any selected "
        "bad B sibling, this lane does not support false-positive rescue for that pair."
    )
    report["both_siblings_per_pair_required_after_scoring"] = True
    report["checks"]["freeze_root_matches_hash_manifest"] = report["freeze_root_matches_hash_manifest"]
    CANARY.write_json(run_dir / "solo_failure_factory_batch013_fp_rescue_live_preflight.json", report)
    return report


def run_preflight_only(packet_limit: int | None = None, packet_index: int = 1) -> dict[str, Any]:
    configure_runtime()
    run_dir = LIVE_ROOT / f"preflight_{CANARY.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    runtime_manifest_path = CANARY.materialize_runtime_subset(run_dir, packet_limit, packet_index)
    return preflight(run_dir, runtime_manifest_path)


def run_live(approval_statement: str, packet_limit: int | None = None, packet_index: int = 1) -> dict[str, Any]:
    configure_runtime()
    summary = CANARY.run_live(approval_statement, packet_limit=packet_limit, packet_index=packet_index)
    summary["classification"] = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH013_FP_RESCUE_LIVE_RUN_SUMMARY_V0"
    summary["freeze_root_sha256"] = FREEZE_ROOT_SHA256
    summary["lane_label"] = LANE_LABEL
    summary["directional_evidence_only"] = True
    summary["evidence_scope"] = EVIDENCE_SCOPE
    summary["rescue_falsifier"] = (
        "If Holo fails to ALLOW any selected clean A sibling or fails to ESCALATE any selected "
        "bad B sibling, this lane does not support false-positive rescue for that pair."
    )
    run_dir = REPO_ROOT / summary["run_dir"]
    CANARY.write_json(run_dir / "solo_failure_factory_batch013_fp_rescue_live_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--print-approval", action="store_true")
    parser.add_argument("--packet-limit", type=int, default=None)
    parser.add_argument("--packet-index", type=int, default=1)
    parser.add_argument("--approval-statement", default="")
    args = parser.parse_args()

    if sum(bool(value) for value in (args.preflight, args.run_live, args.print_approval)) != 1:
        raise SystemExit("choose exactly one of --preflight, --run-live, or --print-approval")
    if args.print_approval:
        print(scoped_approval_sentence(args.packet_limit, args.packet_index))
        return 0
    if args.preflight:
        print(json.dumps(run_preflight_only(args.packet_limit, args.packet_index), indent=2, sort_keys=True))
        return 0
    print(json.dumps(run_live(args.approval_statement, args.packet_limit, args.packet_index), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
