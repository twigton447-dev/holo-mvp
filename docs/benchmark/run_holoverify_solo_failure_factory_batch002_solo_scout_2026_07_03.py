#!/usr/bin/env python3
"""Run the Batch002 solo-failure factory scout.

This is a solo-discovery runner only:
- no Holo
- no Gov
- no state brief
- no baton
- no artifact registry
- no final selector
- no scoring map before trace freeze
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))

import run_holoverify_blind_120_solo_one_shot_2026_07_03 as SOLO_BASE  # noqa: E402


LANE_LABEL = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_10PAIR_SOLO_SCOUT_V0"
FREEZE_ROOT_SHA256 = "24fd390e0482d353f410915aa39a6de0a2bd9c6fb6ca71874e58e3f0d9395345"
RUNTIME_MANIFEST_SHA256 = "37238e2ef97069344121c0ca02b5a5c3b227885d41d7356d58366ebad7f2f301"
SCORING_MAP_SHA256 = "2b3ee50bdbecac53b7b754bda73ba73b94ad5ac2b1f139bedc793c6765df3423"
PACKET_COUNT = 20
EXPECTED_CALL_COUNT = 60

RUNTIME_MANIFEST = (
    BENCHMARK_ROOT
    / "holoverify_solo_failure_factory_batch002_2026_07_03"
    / "holoverify_solo_failure_factory_batch002_runtime_manifest_2026_07_03.json"
)
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch002_solo_scout_runs_2026_07_03"
POSTHOC_SCORING_SCRIPT = (
    BENCHMARK_ROOT / "score_holoverify_solo_failure_factory_batch002_solo_scout_2026_07_03.py"
)

EXACT_APPROVAL_SENTENCE = (
    "I approve live provider execution for HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_10PAIR_SOLO_SCOUT_V0 "
    "using freeze root 24fd390e0482d353f410915aa39a6de0a2bd9c6fb6ca71874e58e3f0d9395345, "
    "runtime manifest 37238e2ef97069344121c0ca02b5a5c3b227885d41d7356d58366ebad7f2f301, "
    "and exactly 60 provider calls: xai/grok-3-mini x20, openai/gpt-5.4-mini x20, "
    "minimax/MiniMax-M2.5-highspeed x20. No Holo, no Gov, no judges, no scoring map before "
    "trace freeze, no substitutions, no public claims."
)


def parse_packet_indices(value: str) -> list[int] | None:
    if not value.strip():
        return None
    indices = [int(part.strip()) for part in value.split(",") if part.strip()]
    if not indices:
        return None
    if len(set(indices)) != len(indices):
        raise ValueError("packet indices must be unique")
    for index in indices:
        if index <= 0 or index > PACKET_COUNT:
            raise ValueError(f"packet index out of range: {index}")
    return indices


def approval_sentence(
    packet_start_index: int = 1,
    packet_limit: int | None = None,
    packet_indices: list[int] | None = None,
) -> str:
    if packet_indices:
        indices_text = ",".join(str(index) for index in packet_indices)
        packet_count = len(packet_indices)
        return (
            "I approve live provider execution for HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_10PAIR_SOLO_SCOUT_V0 "
            "using freeze root 24fd390e0482d353f410915aa39a6de0a2bd9c6fb6ca71874e58e3f0d9395345, "
            "runtime manifest 37238e2ef97069344121c0ca02b5a5c3b227885d41d7356d58366ebad7f2f301, "
            f"runtime manifest packet indices {indices_text} only, "
            f"and exactly {packet_count * 3} provider calls: xai/grok-3-mini x{packet_count}, "
            f"openai/gpt-5.4-mini x{packet_count}, minimax/MiniMax-M2.5-highspeed x{packet_count}. "
            "No Holo, no Gov, no judges, no scoring map before trace freeze, no substitutions, no public claims."
        )
    if packet_limit is None or (packet_start_index == 1 and packet_limit == PACKET_COUNT):
        return EXACT_APPROVAL_SENTENCE
    if packet_start_index <= 0 or packet_limit <= 0:
        raise ValueError("packet_start_index and packet_limit must be positive")
    packet_end_index = packet_start_index + packet_limit - 1
    if packet_end_index > PACKET_COUNT:
        raise ValueError("requested packet range exceeds Batch002 packet count")
    return (
        "I approve live provider execution for HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH002_10PAIR_SOLO_SCOUT_V0 "
        "using freeze root 24fd390e0482d353f410915aa39a6de0a2bd9c6fb6ca71874e58e3f0d9395345, "
        "runtime manifest 37238e2ef97069344121c0ca02b5a5c3b227885d41d7356d58366ebad7f2f301, "
        f"runtime manifest packet indices {packet_start_index}-{packet_end_index} only, "
        f"and exactly {packet_limit * 3} provider calls: xai/grok-3-mini x{packet_limit}, "
        f"openai/gpt-5.4-mini x{packet_limit}, minimax/MiniMax-M2.5-highspeed x{packet_limit}. "
        "No Holo, no Gov, no judges, no scoring map before trace freeze, no substitutions, no public claims."
    )


def configure_base() -> None:
    SOLO_BASE.LANE_LABEL = LANE_LABEL
    SOLO_BASE.FREEZE_ROOT_SHA256 = FREEZE_ROOT_SHA256
    SOLO_BASE.RUNTIME_MANIFEST = RUNTIME_MANIFEST
    SOLO_BASE.LIVE_ROOT = LIVE_ROOT
    SOLO_BASE.POSTHOC_SCORING_SCRIPT = POSTHOC_SCORING_SCRIPT
    SOLO_BASE.EXPECTED_RUNTIME_MANIFEST_SHA256 = RUNTIME_MANIFEST_SHA256
    SOLO_BASE.EXPECTED_SCORING_MAP_SHA256 = SCORING_MAP_SHA256
    SOLO_BASE.EXPECTED_PACKET_COUNT = PACKET_COUNT
    SOLO_BASE.EXPECTED_CALL_COUNT = EXPECTED_CALL_COUNT
    SOLO_BASE.EXACT_APPROVAL_SENTENCE = EXACT_APPROVAL_SENTENCE


def run_preflight_only(
    packet_start_index: int = 1,
    packet_limit: int | None = None,
    packet_indices: list[int] | None = None,
) -> dict:
    run_dir = SOLO_BASE.LIVE_ROOT / f"preflight_{SOLO_BASE.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    if packet_indices:
        runtime_manifest = SOLO_BASE.materialize_runtime_indices(run_dir, packet_indices)
    else:
        runtime_manifest = SOLO_BASE.materialize_runtime_subset(run_dir, packet_limit, packet_start_index)
    return SOLO_BASE.preflight(run_dir, runtime_manifest)


def main() -> int:
    configure_base()
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--print-approval", action="store_true")
    parser.add_argument("--approval-statement", default="")
    parser.add_argument("--packet-start-index", type=int, default=1)
    parser.add_argument("--packet-limit", type=int)
    parser.add_argument("--packet-indices", default="")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.preflight, args.run_live, args.print_approval)) != 1:
        raise SystemExit("choose exactly one of --preflight, --run-live, or --print-approval")
    packet_indices = parse_packet_indices(args.packet_indices)
    if packet_indices and (args.packet_limit is not None or args.packet_start_index != 1):
        raise SystemExit("use --packet-indices or --packet-start-index/--packet-limit, not both")
    exact_approval = approval_sentence(args.packet_start_index, args.packet_limit, packet_indices)
    SOLO_BASE.EXACT_APPROVAL_SENTENCE = exact_approval
    if args.print_approval:
        print(exact_approval)
        return 0
    if args.preflight:
        print(
            json.dumps(
                run_preflight_only(args.packet_start_index, args.packet_limit, packet_indices),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    print(
        json.dumps(
            SOLO_BASE.run_live(
                args.approval_statement,
                packet_limit=args.packet_limit,
                packet_index=args.packet_start_index,
                packet_indices=packet_indices,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

