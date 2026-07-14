#!/usr/bin/env python3
"""CLI for deterministic, dry-run-first HoloChat experiment manifests."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from holochat_experiments import CONDITIONS, LANES, build_manifest, run_live_smoke, write_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan HoloChat cost/intelligence experiments (dry-run by default).")
    parser.add_argument("--lane", choices=sorted(LANES), default="balanced")
    parser.add_argument("--condition", choices=sorted(CONDITIONS), default="C")
    parser.add_argument("--rotations", type=int, default=2)
    parser.add_argument("--scenario", default="runtime")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--live", action="store_true", help="First explicit live execution gate.")
    parser.add_argument("--confirm-live", action="store_true", help="Second explicit live execution gate.")
    parser.add_argument(
        "--max-estimated-cost-usd",
        type=float,
        default=None,
        help="Stop the live child before the next projected turn would cross this estimate.",
    )
    args = parser.parse_args()
    if (args.live or args.confirm_live) and args.max_estimated_cost_usd is None:
        parser.error("live execution requires --max-estimated-cost-usd")

    manifest = build_manifest(lane=args.lane, condition=args.condition, rotations=args.rotations, scenario=args.scenario)
    if args.output:
        write_manifest(manifest, args.output)
    if args.live or args.confirm_live:
        credential_env = {
            name: os.environ[name]
            for name in ("OPENAI_API_KEY", "XAI_API_KEY", "MINIMAX_API_KEY", "SUPABASE_URL", "SUPABASE_KEY")
            if os.environ.get(name)
        }
        run_live_smoke(
            manifest=manifest,
            live=args.live,
            confirm_live=args.confirm_live,
            credential_env=credential_env,
            max_estimated_cost_usd=args.max_estimated_cost_usd,
        )
        manifest["mode"] = "live_smoke_launched"
        manifest["provider_calls_made"] = True
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
