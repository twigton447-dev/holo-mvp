#!/usr/bin/env python3
"""Run the Batch013 exact-boundary top-10 solo scout.

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


LANE_LABEL = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH013_EXACT_BOUNDARY_TOP10_SOLO_SCOUT_V0"
PACKET_COUNT = 40
TOP_10_PACKET_COUNT = 20
EXPECTED_CALL_COUNT = 60

AUDIT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH013_EXACT_BOUNDARY_PACKET_FREEZE_CANDIDATE_2026_07_04.json"
RUNTIME_MANIFEST = (
    BENCHMARK_ROOT
    / "holoverify_solo_failure_factory_batch013_exact_boundary_2026_07_04"
    / "holoverify_solo_failure_factory_batch013_exact_boundary_runtime_manifest_2026_07_04.json"
)
SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_solo_failure_factory_batch013_exact_boundary_2026_07_04"
    / "holoverify_solo_failure_factory_batch013_exact_boundary_scoring_map_2026_07_04.json"
)
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_solo_failure_factory_batch013_exact_boundary_top10_solo_scout_runs_2026_07_04"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_solo_failure_factory_batch013_exact_boundary_top10_solo_scout_2026_07_04.py"


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


def top_10_packet_indices() -> list[int]:
    audit = load_json(AUDIT_JSON)
    runtime = load_json(RUNTIME_MANIFEST)
    top_pairs = {
        str(row["pair_id"])
        for row in audit.get("design_report", [])
        if row.get("recommended_for_top_10_scout") is True
    }
    if len(top_pairs) != 10:
        raise RuntimeError(f"top_10_pair_count_mismatch:{len(top_pairs)}")
    top_runtime_ids = {
        str(row["opaque_runtime_id"])
        for row in audit.get("selected_rows", [])
        if str(row.get("pair_id")) in top_pairs
    }
    if len(top_runtime_ids) != TOP_10_PACKET_COUNT:
        raise RuntimeError(f"top_10_packet_count_mismatch:{len(top_runtime_ids)}")
    indices = [
        index
        for index, row in enumerate(runtime.get("packets", []), start=1)
        if str(row.get("opaque_runtime_id")) in top_runtime_ids
    ]
    if len(indices) != TOP_10_PACKET_COUNT:
        raise RuntimeError(f"top_10_runtime_index_count_mismatch:{len(indices)}")
    return indices


def approval_sentence(packet_indices: list[int]) -> str:
    root = freeze_root_sha256()
    runtime_hash = runtime_manifest_sha256()
    indices_text = ",".join(str(index) for index in packet_indices)
    return (
        f"I approve live provider execution for {LANE_LABEL} using export-safe synthetic Batch013 exact-boundary top-10 packet contents, "
        f"freeze root {root}, runtime manifest {runtime_hash}, "
        f"runtime manifest packet indices {indices_text} only, "
        "and exactly 60 provider calls: xai/grok-3-mini x20, openai/gpt-5.4-mini x20, "
        "minimax/MiniMax-M2.5-highspeed x20. No private packet export, no Holo, no Gov, no judges, "
        "no scoring map before trace freeze, no substitutions, no public claims."
    )


def configure_base(exact_approval: str) -> None:
    audit = load_json(AUDIT_JSON)
    if audit.get("export_safety", {}).get("runtime_content_synthetic") is not True:
        raise RuntimeError("export_safe_runtime_content_not_confirmed")
    if audit.get("export_safety", {}).get("private_packet_text_copied") is not False:
        raise RuntimeError("private_packet_text_copy_flag_not_false")
    if audit.get("validation", {}).get("focused_exact_boundary_design") is not True:
        raise RuntimeError("focused_exact_boundary_design_validation_missing")
    if audit.get("validation", {}).get("runtime_leakage_clean") is not True:
        raise RuntimeError("runtime_leakage_clean_validation_missing")
    SOLO_BASE.LANE_LABEL = LANE_LABEL
    SOLO_BASE.FREEZE_ROOT_SHA256 = freeze_root_sha256()
    SOLO_BASE.RUNTIME_MANIFEST = RUNTIME_MANIFEST
    SOLO_BASE.LIVE_ROOT = LIVE_ROOT
    SOLO_BASE.POSTHOC_SCORING_SCRIPT = POSTHOC_SCORING_SCRIPT
    SOLO_BASE.EXPECTED_RUNTIME_MANIFEST_SHA256 = runtime_manifest_sha256()
    SOLO_BASE.EXPECTED_SCORING_MAP_SHA256 = scoring_map_sha256()
    SOLO_BASE.EXPECTED_PACKET_COUNT = TOP_10_PACKET_COUNT
    SOLO_BASE.EXPECTED_CALL_COUNT = EXPECTED_CALL_COUNT
    SOLO_BASE.EXACT_APPROVAL_SENTENCE = exact_approval


def run_preflight_only(packet_indices: list[int]) -> dict:
    run_dir = SOLO_BASE.LIVE_ROOT / f"preflight_{SOLO_BASE.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    runtime_manifest = SOLO_BASE.materialize_runtime_indices(run_dir, packet_indices)
    return SOLO_BASE.preflight(run_dir, runtime_manifest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--print-approval", action="store_true")
    parser.add_argument("--approval-statement", default="")
    parser.add_argument("--packet-indices", default="")
    args = parser.parse_args()
    if sum(bool(value) for value in (args.preflight, args.run_live, args.print_approval)) != 1:
        raise SystemExit("choose exactly one of --preflight, --run-live, or --print-approval")
    packet_indices = parse_packet_indices(args.packet_indices) or top_10_packet_indices()
    if len(packet_indices) != TOP_10_PACKET_COUNT:
        raise SystemExit(f"expected exactly {TOP_10_PACKET_COUNT} packet indices for this top-10 scout")
    exact_approval = approval_sentence(packet_indices)
    configure_base(exact_approval)
    if args.print_approval:
        print(exact_approval)
        return 0
    if args.preflight:
        print(json.dumps(run_preflight_only(packet_indices), indent=2, sort_keys=True))
        return 0
    print(
        json.dumps(
            SOLO_BASE.run_live(
                args.approval_statement,
                packet_indices=packet_indices,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
