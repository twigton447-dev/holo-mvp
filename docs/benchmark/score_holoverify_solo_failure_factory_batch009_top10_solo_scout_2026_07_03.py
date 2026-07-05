#!/usr/bin/env python3
"""Post-hoc scorer for the Batch009 top-10 solo-failure scout."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))

import score_holoverify_blind_120_solo_posthoc_2026_07_03 as SOLO_SCORE  # noqa: E402


SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_solo_failure_factory_batch009_top10_2026_07_03"
    / "holoverify_solo_failure_factory_batch009_top10_scoring_map_2026_07_03.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configure_base() -> None:
    SOLO_SCORE.SCORING_MAP = SCORING_MAP
    SOLO_SCORE.EXPECTED_SCORING_MAP_SHA256 = sha256_file(SCORING_MAP)


def score(run_dir: Path) -> dict:
    configure_base()
    report = SOLO_SCORE.score(run_dir)
    report["classification"] = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH009_TOP10_SOLO_SCOUT_POSTHOC_SCORE_V1"
    report["solo_failure_factory_batch"] = "BATCH009_TOP10"
    report["stacked_failure_classes"] = True
    report["scoring_map"] = str(SCORING_MAP.relative_to(BENCHMARK_ROOT.parents[1]))
    report["scoring_map_sha256_expected"] = sha256_file(SCORING_MAP)
    out_json = run_dir / "solo_failure_factory_batch009_top10_solo_posthoc_score.json"
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n")
    model_summary = report.get("summary_by_model", {})
    (run_dir / "solo_failure_factory_batch009_top10_solo_posthoc_score.md").write_text(
        "\n".join(
            [
                "# Solo Failure Factory Batch009 Top-10 Post-Hoc Score",
                "",
                f"- Packets: `{report.get('packet_count')}`",
                f"- Solo calls: `{report.get('solo_call_count')}`",
                f"- Scoring map hash: `{report.get('trace_binding', {}).get('scoring_map_sha256')}`",
                f"- Packet collapse summary: `{report.get('packet_collapse_summary', {})}`",
                "",
                "## Model Summary",
                "",
                "```json",
                json.dumps(model_summary, indent=2, sort_keys=True),
                "```",
            ]
        )
        + "\n"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(score(Path(args.run_dir)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
