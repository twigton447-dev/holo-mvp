#!/usr/bin/env python3
"""Run the Batch015 focused authority-overblock solo scout.

Solo-discovery only: no Holo, no Gov, no judges, and no scoring map before
trace freeze.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))

import run_holoverify_blind_120_solo_one_shot_2026_07_03 as SOLO_BASE  # noqa: E402


LANE_LABEL = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH015_AUTHORITY_OVERBLOCK_20PAIR_SOLO_SCOUT_V0"
PACKET_COUNT = 40
EXPECTED_CALL_COUNT = 120

AUDIT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH015_AUTHORITY_OVERBLOCK_PACKET_FREEZE_2026_07_04.json"
RUNTIME_MANIFEST = (
    BENCHMARK_ROOT
    / "holoverify_solo_failure_factory_batch015_authority_overblock_2026_07_04"
    / "holoverify_solo_failure_factory_batch015_authority_overblock_runtime_manifest_2026_07_04.json"
)
SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_solo_failure_factory_batch015_authority_overblock_2026_07_04"
    / "holoverify_solo_failure_factory_batch015_authority_overblock_scoring_map_2026_07_04.json"
)
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch015_authority_overblock_solo_scout_runs_2026_07_04"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_solo_failure_factory_batch015_authority_overblock_solo_scout_2026_07_04.py"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(errors="replace"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_root_sha256() -> str:
    return str(load_json(AUDIT_JSON)["freeze_root_sha256"])


def runtime_manifest_sha256() -> str:
    return sha256_file(RUNTIME_MANIFEST)


def scoring_map_sha256() -> str:
    return sha256_file(SCORING_MAP)


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
    root = freeze_root_sha256()
    runtime_hash = runtime_manifest_sha256()
    if packet_indices:
        indices_text = ",".join(str(index) for index in packet_indices)
        packet_count = len(packet_indices)
        return (
            f"I approve live provider execution for {LANE_LABEL} using export-safe synthetic focused authority-overblock packet contents, "
            f"freeze root {root}, runtime manifest {runtime_hash}, "
            f"runtime manifest packet indices {indices_text} only, "
            f"and exactly {packet_count * 3} provider calls: xai/grok-3-mini x{packet_count}, "
            f"openai/gpt-5.4-mini x{packet_count}, minimax/MiniMax-M2.5-highspeed x{packet_count}. "
            "No private packet export, no Holo, no Gov, no judges, no scoring map before trace freeze, "
            "no substitutions, no public claims."
        )
    if packet_limit is None or (packet_start_index == 1 and packet_limit == PACKET_COUNT):
        return (
            f"I approve live provider execution for {LANE_LABEL} using export-safe synthetic focused authority-overblock packet contents, "
            f"freeze root {root}, runtime manifest {runtime_hash}, "
            "and exactly 120 provider calls: xai/grok-3-mini x40, openai/gpt-5.4-mini x40, "
            "minimax/MiniMax-M2.5-highspeed x40. No private packet export, no Holo, no Gov, no judges, "
            "no scoring map before trace freeze, no substitutions, no public claims."
        )
    if packet_start_index <= 0 or packet_limit <= 0:
        raise ValueError("packet_start_index and packet_limit must be positive")
    packet_end_index = packet_start_index + packet_limit - 1
    if packet_end_index > PACKET_COUNT:
        raise ValueError("requested packet range exceeds Batch015 packet count")
    return (
        f"I approve live provider execution for {LANE_LABEL} using export-safe synthetic focused authority-overblock packet contents, "
        f"freeze root {root}, runtime manifest {runtime_hash}, "
        f"runtime manifest packet indices {packet_start_index}-{packet_end_index} only, "
        f"and exactly {packet_limit * 3} provider calls: xai/grok-3-mini x{packet_limit}, "
        f"openai/gpt-5.4-mini x{packet_limit}, minimax/MiniMax-M2.5-highspeed x{packet_limit}. "
        "No private packet export, no Holo, no Gov, no judges, no scoring map before trace freeze, "
        "no substitutions, no public claims."
    )


def configure_base(exact_approval: str) -> None:
    audit = load_json(AUDIT_JSON)
    if audit.get("export_safety", {}).get("runtime_content_synthetic") is not True:
        raise RuntimeError("export_safe_runtime_content_not_confirmed")
    if audit.get("export_safety", {}).get("private_packet_text_copied") is not False:
        raise RuntimeError("private_packet_text_copy_flag_not_false")
    if audit.get("validation", {}).get("focused_false_positive_overblock") is not True:
        raise RuntimeError("focused_false_positive_overblock_validation_missing")
    if audit.get("validation", {}).get("allow_key_completeness_pass") is not True:
        raise RuntimeError("allow_key_completeness_validation_missing")
    SOLO_BASE.LANE_LABEL = LANE_LABEL
    SOLO_BASE.FREEZE_ROOT_SHA256 = freeze_root_sha256()
    SOLO_BASE.RUNTIME_MANIFEST = RUNTIME_MANIFEST
    SOLO_BASE.LIVE_ROOT = LIVE_ROOT
    SOLO_BASE.POSTHOC_SCORING_SCRIPT = POSTHOC_SCORING_SCRIPT
    SOLO_BASE.EXPECTED_RUNTIME_MANIFEST_SHA256 = runtime_manifest_sha256()
    SOLO_BASE.EXPECTED_SCORING_MAP_SHA256 = scoring_map_sha256()
    SOLO_BASE.EXPECTED_PACKET_COUNT = PACKET_COUNT
    SOLO_BASE.EXPECTED_CALL_COUNT = EXPECTED_CALL_COUNT
    SOLO_BASE.EXACT_APPROVAL_SENTENCE = exact_approval


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
    configure_base(exact_approval)
    if args.print_approval:
        print(exact_approval)
        return 0
    if args.preflight:
        print(json.dumps(run_preflight_only(args.packet_start_index, args.packet_limit, packet_indices), indent=2, sort_keys=True))
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
