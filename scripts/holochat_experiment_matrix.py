#!/usr/bin/env python3
"""Generate a deterministic three-lane by four-condition dry-run matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from holochat_experiments import CONDITIONS, LANES, build_manifest, write_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build HoloChat A/B/C/D experiment manifests without provider calls.")
    parser.add_argument("--lane", choices=["all", *sorted(LANES)], default="all")
    parser.add_argument("--rotations", type=int, default=8)
    parser.add_argument("--scenario", default="runtime")
    parser.add_argument("--output-dir", type=Path, default=Path("/tmp/holochat-experiment-matrix"))
    args = parser.parse_args()

    lanes = sorted(LANES) if args.lane == "all" else [args.lane]
    manifests = []
    for lane in lanes:
        for condition in sorted(CONDITIONS):
            manifest = build_manifest(
                lane=lane,
                condition=condition,
                rotations=args.rotations,
                scenario=args.scenario,
            )
            write_manifest(manifest, args.output_dir / f"{lane}-{condition}.json")
            manifests.append(manifest)

    summary = {
        "mode": "dry_run",
        "provider_calls_made": False,
        "lane_count": len(lanes),
        "condition_count": len(CONDITIONS),
        "run_count": len(manifests),
        "runs": [
            {
                "run_id": item["run_id"],
                "lane": item["lane"]["name"],
                "condition": item["condition"]["id"],
                "estimated_cost_usd": item["aggregate"]["estimated_cost_usd"],
                "manifest": str(args.output_dir / f"{item['lane']['name']}-{item['condition']['id']}.json"),
            }
            for item in manifests
        ],
    }
    write_manifest(summary, args.output_dir / "matrix-summary.json")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
