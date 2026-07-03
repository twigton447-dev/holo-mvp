#!/usr/bin/env python3
"""Run the HoloVerify 120-packet blind runtime-firewall lane.

This wrapper reuses the canary-good live runtime path while pinning it to the
frozen 120-packet blind bank. It does not load the scoring map during live
execution; scoring remains a separate post-freeze step.
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

FREEZE_ROOT_SHA256 = "63cc81e5fd5d9dcc56e054ec5b55e5981d1a3b1d88b90e61e4cf68bb9c5c33ba"
RUNTIME_MANIFEST = (
    BENCHMARK_ROOT
    / "holoverify_blind_120_bank_2026_07_03"
    / "holoverify_blind_120_runtime_manifest_2026_07_03.json"
)
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_blind_120_live_runs_2026_07_03"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_blind_120_posthoc_2026_07_03.py"

EXPECTED_RUNTIME_MANIFEST_SHA256 = "c3a2bbe2ff2b4b4a3d2e4da0112489b3ba19d41147c5eff45cc0f36c5ca940a1"
EXPECTED_SCORING_MAP_SHA256 = "b5f3c219c473aa2821540aca7cf84e5fc8d2441f977f69d9df226aad550ed166"
EXPECTED_PACKET_COUNT = 120
EXPECTED_CALL_COUNT = 600
BATCH_SIZE = 10
BATCH_COUNT = 12
LANE_LABEL = "HOLOVERIFY_BLIND_120_RUNTIME_FIREWALL_V0"

SCORING_MAP_READ_GUARD_TEST = (
    "tests/test_holoverify_blind_120_live_wrapper.py::"
    "test_preflight_does_not_read_120_scoring_map_bytes"
)
WRAPPER_SCORING_SPLIT_TEST = (
    "tests/test_holoverify_blind_120_live_wrapper.py::"
    "test_120_live_wrapper_does_not_keep_scoring_map_path_or_posthoc_scorer"
)

EXACT_APPROVAL_SENTENCE = (
    "I approve live provider execution for HOLOVERIFY_BLIND_120_RUNTIME_FIREWALL_V0 "
    "using committed freeze root 63cc81e5fd5d9dcc56e054ec5b55e5981d1a3b1d88b90e61e4cf68bb9c5c33ba, "
    "runtime manifest c3a2bbe2ff2b4b4a3d2e4da0112489b3ba19d41147c5eff45cc0f36c5ca940a1, and exactly "
    "600 provider calls: W1 xai/grok-3-mini x120, G1 minimax/MiniMax-M2.5-highspeed x120, "
    "W2 openai/gpt-5.4-mini x120, G2 minimax/MiniMax-M2.5-highspeed x120, "
    "W3 minimax/MiniMax-M2.5-highspeed x120. No judges, no solo, no scoring map before "
    "trace freeze, no substitutions, no public claims."
)


def one_packet_approval_sentence(packet_index: int) -> str:
    return (
        "I approve live provider execution for HOLOVERIFY_BLIND_120_1PKT_RUNTIME_FIREWALL_V0 "
        "using committed freeze root 63cc81e5fd5d9dcc56e054ec5b55e5981d1a3b1d88b90e61e4cf68bb9c5c33ba, "
        "runtime manifest c3a2bbe2ff2b4b4a3d2e4da0112489b3ba19d41147c5eff45cc0f36c5ca940a1, "
        f"opaque packet index {packet_index} only, "
        "and exactly 5 provider calls: W1 xai/grok-3-mini x1, G1 minimax/MiniMax-M2.5-highspeed x1, "
        "W2 openai/gpt-5.4-mini x1, G2 minimax/MiniMax-M2.5-highspeed x1, "
        "W3 minimax/MiniMax-M2.5-highspeed x1. No judges, no solo, no scoring map before "
        "trace freeze, no substitutions, no public claims."
    )


def scoped_approval_sentence(packet_limit: int | None = None, packet_index: int = 1) -> str:
    if packet_limit is None:
        return EXACT_APPROVAL_SENTENCE
    if packet_limit == EXPECTED_PACKET_COUNT and packet_index == 1:
        return EXACT_APPROVAL_SENTENCE
    if packet_limit == 1:
        return one_packet_approval_sentence(packet_index)

    end_index = packet_index + packet_limit - 1
    total_calls = packet_limit * len(CANARY.CALL_SEQUENCE)
    return (
        f"I approve live provider execution for HOLOVERIFY_BLIND_120_{packet_limit}PKT_RUNTIME_FIREWALL_V0 "
        "using committed freeze root 63cc81e5fd5d9dcc56e054ec5b55e5981d1a3b1d88b90e61e4cf68bb9c5c33ba, "
        "runtime manifest c3a2bbe2ff2b4b4a3d2e4da0112489b3ba19d41147c5eff45cc0f36c5ca940a1, "
        f"opaque packet indices {packet_index}-{end_index} only, "
        f"and exactly {total_calls} provider calls: W1 xai/grok-3-mini x{packet_limit}, "
        f"G1 minimax/MiniMax-M2.5-highspeed x{packet_limit}, W2 openai/gpt-5.4-mini x{packet_limit}, "
        f"G2 minimax/MiniMax-M2.5-highspeed x{packet_limit}, W3 minimax/MiniMax-M2.5-highspeed x{packet_limit}. "
        "No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims."
    )


def packet_index_for_batch(batch_number: int) -> int:
    if batch_number < 1 or batch_number > BATCH_COUNT:
        raise ValueError(f"batch_number must be 1-{BATCH_COUNT}")
    return ((batch_number - 1) * BATCH_SIZE) + 1


def batch_approval_sentence(batch_number: int) -> str:
    return scoped_approval_sentence(packet_limit=BATCH_SIZE, packet_index=packet_index_for_batch(batch_number))


def batch_scope(batch_number: int) -> dict[str, Any]:
    start = packet_index_for_batch(batch_number)
    return {
        "batch_number": batch_number,
        "batch_count": BATCH_COUNT,
        "batch_size": BATCH_SIZE,
        "packet_index": start,
        "packet_limit": BATCH_SIZE,
        "packet_index_end": start + BATCH_SIZE - 1,
        "expected_provider_calls": BATCH_SIZE * len(CANARY.CALL_SEQUENCE),
        "approval_sentence": batch_approval_sentence(batch_number),
    }


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
    CANARY.EXACT_APPROVAL_SENTENCE = EXACT_APPROVAL_SENTENCE
    CANARY.one_packet_approval_sentence = one_packet_approval_sentence
    CANARY.scoped_approval_sentence = scoped_approval_sentence


def preflight(run_dir: Path, runtime_manifest_path: Path = RUNTIME_MANIFEST) -> dict[str, Any]:
    configure_runtime()
    report = CANARY.preflight(run_dir, runtime_manifest_path)
    report["classification"] = "HOLOVERIFY_BLIND_120_LIVE_PREFLIGHT_V0"
    report["freeze_root_sha256"] = FREEZE_ROOT_SHA256
    report["lane_label"] = LANE_LABEL
    CANARY.write_json(run_dir / "blind_120_live_preflight.json", report)
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
    summary["classification"] = "HOLOVERIFY_BLIND_120_LIVE_RUN_SUMMARY_V0"
    summary["freeze_root_sha256"] = FREEZE_ROOT_SHA256
    summary["lane_label"] = LANE_LABEL
    run_dir = REPO_ROOT / summary["run_dir"]
    CANARY.write_json(run_dir / "blind_120_live_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--print-approval", action="store_true")
    parser.add_argument("--batch-number", type=int, default=None)
    parser.add_argument("--packet-limit", type=int, default=None)
    parser.add_argument("--packet-index", type=int, default=1)
    parser.add_argument("--approval-statement", default="")
    args = parser.parse_args()

    if sum(bool(value) for value in (args.preflight, args.run_live, args.print_approval)) != 1:
        raise SystemExit("choose exactly one of --preflight, --run-live, or --print-approval")
    if args.batch_number is not None:
        if args.packet_limit is not None or args.packet_index != 1:
            raise SystemExit("--batch-number cannot be combined with --packet-limit or --packet-index")
        scope = batch_scope(args.batch_number)
        args.packet_limit = scope["packet_limit"]
        args.packet_index = scope["packet_index"]

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
