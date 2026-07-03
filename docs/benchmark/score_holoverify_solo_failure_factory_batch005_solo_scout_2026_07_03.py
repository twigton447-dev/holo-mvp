#!/usr/bin/env python3
"""Post-hoc scorer for the Batch005 solo-failure factory scout."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))

import score_holoverify_blind_120_solo_posthoc_2026_07_03 as SOLO_SCORE  # noqa: E402


SCORING_MAP = (
    BENCHMARK_ROOT
    / "holoverify_solo_failure_factory_batch005_2026_07_03"
    / "holoverify_solo_failure_factory_batch005_scoring_map_2026_07_03.json"
)
EXPECTED_SCORING_MAP_SHA256 = "91efdfa719ab234644831005c3fc875a56c7be7d13a6de15e90361266dcdf0c5"


def configure_base() -> None:
    SOLO_SCORE.SCORING_MAP = SCORING_MAP
    SOLO_SCORE.EXPECTED_SCORING_MAP_SHA256 = EXPECTED_SCORING_MAP_SHA256


def score(run_dir: Path) -> dict:
    configure_base()
    report = SOLO_SCORE.score(run_dir)
    report["classification"] = "HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH005_SOLO_SCOUT_POSTHOC_SCORE_V1"
    report["solo_failure_factory_batch"] = "BATCH005"
    report["scoring_map"] = str(SCORING_MAP.relative_to(BENCHMARK_ROOT.parents[1]))
    report["scoring_map_sha256_expected"] = EXPECTED_SCORING_MAP_SHA256
    out_json = run_dir / "solo_failure_factory_batch005_solo_posthoc_score.json"
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n")
    model_summary = report.get("summary_by_model", {})
    (run_dir / "solo_failure_factory_batch005_solo_posthoc_score.md").write_text(
        "\n".join(
            [
                "# Solo Failure Factory Batch005 Post-Hoc Score",
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
