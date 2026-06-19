#!/usr/bin/env python3
"""Build a cross-run lift rollup from analyzed finance benchmark runs."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


PACKET_DIR = Path(__file__).resolve().parent
RUNS_DIR = PACKET_DIR / "runs"
ROLLUP_DIR = PACKET_DIR / "suite_rollups"

MANIFEST_HASH_TO_LOCK_FILE = {
    "source_pack": "source_pack.json",
    "report_brief": "report_brief.json",
    "gov_protocol": "gov_technical_probe_protocol.json",
    "role_flow": "finance_algo_adversarial_role_flow.json",
    "routing_configs": "holo_routing_configs.json",
    "judge_rubric": "judge_rubric_8criteria.json",
    "judge_panel": "judge_panel_frontier_blind.json",
    "run_prompt": "holo_frontier_run_prompt.md",
    "judge_brief": "judge_brief.md",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def pct(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round((numerator / denominator) * 100, 3)


def round_or_none(value: Any, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def current_hash_match(manifest: dict[str, Any], lock: dict[str, Any]) -> dict[str, Any]:
    declared_hashes = manifest.get("hashes") or {}
    packet_hashes = lock.get("packet_file_sha256") or {}
    checked: dict[str, dict[str, Any]] = {}
    for manifest_key, lock_file in MANIFEST_HASH_TO_LOCK_FILE.items():
        declared = declared_hashes.get(manifest_key)
        expected = packet_hashes.get(lock_file)
        checked[manifest_key] = {
            "declared": declared,
            "expected": expected,
            "matches_current_lock": bool(declared and expected and declared == expected),
        }
    required = ["source_pack", "report_brief", "gov_protocol", "role_flow", "judge_rubric", "judge_panel", "run_prompt", "judge_brief"]
    if "routing_configs" in declared_hashes:
        required.append("routing_configs")
    return {
        "matches_current_lock": all(checked[item]["matches_current_lock"] for item in required),
        "checked": checked,
        "required_manifest_hash_keys": required,
    }


def load_completed_run(run_dir: Path, lock: dict[str, Any]) -> dict[str, Any] | None:
    analysis_path = run_dir / "analysis" / "analysis_summary.json"
    manifest_path = run_dir / "run_manifest.json"
    if not analysis_path.exists() or not manifest_path.exists():
        return None
    analysis = read_json(analysis_path)
    manifest = read_json(manifest_path)
    if analysis.get("status") != "analysis_complete":
        return None

    overall = analysis.get("overall") or {}
    solo_mean = round_or_none(overall.get("solo_mean"))
    gap_all = round_or_none(overall.get("gap_holo_minus_solo"))
    gap_clean = round_or_none(analysis.get("overall_gap_clean_only"))
    hash_status = current_hash_match(manifest, lock)

    pair_rows = []
    for pair in analysis.get("pair_summaries") or []:
        pair_solo = round_or_none(pair.get("solo_mean_all"))
        pair_gap_all = round_or_none(pair.get("gap_all"))
        pair_gap_clean = round_or_none(pair.get("gap_clean_only"))
        pair_rows.append(
            {
                "pair_id": pair.get("pair_id"),
                "solo_condition": pair.get("solo_condition"),
                "holo_mean_all": round_or_none(pair.get("holo_mean_all")),
                "solo_mean_all": pair_solo,
                "gap_all": pair_gap_all,
                "gap_clean_only": pair_gap_clean,
                "percent_lift_all": pct(pair_gap_all, pair_solo),
                "percent_lift_clean": pct(pair_gap_clean, pair_solo),
                "judge_count": pair.get("judge_count"),
                "flagged_judge_count": pair.get("flagged_judge_count"),
            }
        )

    return {
        "run_id": analysis.get("run_id") or manifest.get("run_id") or run_dir.name,
        "run_dir": str(run_dir),
        "run_status": analysis.get("run_status") or manifest.get("status"),
        "benchmark_credit": analysis.get("benchmark_credit"),
        "public_claim": analysis.get("public_claim"),
        "routing_config_id": manifest.get("routing_config_id"),
        "solo_suite_id": manifest.get("solo_suite_id"),
        "holo_cohort_lane": manifest.get("holo_cohort_lane"),
        "holo_governor_model": manifest.get("holo_governor_model"),
        "holo_mean": round_or_none(overall.get("holo_mean")),
        "solo_mean": solo_mean,
        "gap_all": gap_all,
        "gap_clean_only": gap_clean,
        "percent_lift_all": pct(gap_all, solo_mean),
        "percent_lift_clean": pct(gap_clean, solo_mean),
        "judge_observations": overall.get("judge_observations"),
        "clean_judge_row_count": analysis.get("clean_judge_row_count"),
        "flagged_judge_row_count": analysis.get("flagged_judge_row_count"),
        "matches_current_lock": hash_status["matches_current_lock"],
        "hash_status": hash_status,
        "pair_rows": pair_rows,
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def vals(key: str) -> list[float]:
        return [float(row[key]) for row in rows if row.get(key) is not None]

    return {
        "run_count": len(rows),
        "mean_gap_all": round(mean(vals("gap_all")), 3) if vals("gap_all") else None,
        "mean_gap_clean_only": round(mean(vals("gap_clean_only")), 3) if vals("gap_clean_only") else None,
        "mean_percent_lift_all": round(mean(vals("percent_lift_all")), 3) if vals("percent_lift_all") else None,
        "mean_percent_lift_clean": round(mean(vals("percent_lift_clean")), 3) if vals("percent_lift_clean") else None,
        "min_percent_lift_clean": round(min(vals("percent_lift_clean")), 3) if vals("percent_lift_clean") else None,
        "max_percent_lift_clean": round(max(vals("percent_lift_clean")), 3) if vals("percent_lift_clean") else None,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "run_id",
        "run_status",
        "routing_config_id",
        "solo_suite_id",
        "holo_cohort_lane",
        "holo_governor_model",
        "holo_mean",
        "solo_mean",
        "gap_all",
        "gap_clean_only",
        "percent_lift_all",
        "percent_lift_clean",
        "judge_observations",
        "clean_judge_row_count",
        "flagged_judge_row_count",
        "matches_current_lock",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def write_markdown(path: Path, payload: dict[str, Any]) -> None:
    all_runs = payload["aggregate_all_completed_analyzed_runs"]
    current = payload["aggregate_current_lock_matching_runs"]
    lines = [
        "# Hash-Locked Lift Rollup",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Hash lock: `{payload['hash_lock_id']}`",
        f"Current execution lock: `{payload['combined_execution_lock_hash']}`",
        "",
        "## Mean Lift",
        "",
        f"- All completed analyzed runs: `{all_runs['run_count']}` runs, mean clean lift `{all_runs['mean_percent_lift_clean']}`%",
        f"- Current-lock matching runs: `{current['run_count']}` runs, mean clean lift `{current['mean_percent_lift_clean']}`%",
        "",
        "Use current-lock matching numbers for strict claims. Older completed runs remain useful diagnostics but should be labeled by their declared manifest hashes.",
        "",
        "## Runs",
        "",
        "| Run | Route | Suite | Gov | Clean Gap | Clean Lift | Current Lock |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in payload["runs"]:
        lines.append(
            "| {run_id} | {route} | {suite} | {gov} | {gap} | {lift}% | {match} |".format(
                run_id=row["run_id"],
                route=row.get("routing_config_id") or "",
                suite=row.get("solo_suite_id") or "",
                gov=row.get("holo_governor_model") or "",
                gap=row.get("gap_clean_only"),
                lift=row.get("percent_lift_clean"),
                match="yes" if row.get("matches_current_lock") else "no",
            )
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROLLUP_DIR))
    args = parser.parse_args()

    lock = read_json(PACKET_DIR / "hash_lock.json")
    rows = []
    if RUNS_DIR.exists():
        for run_dir in sorted(path for path in RUNS_DIR.iterdir() if path.is_dir()):
            row = load_completed_run(run_dir, lock)
            if row:
                rows.append(row)

    current_rows = [row for row in rows if row["matches_current_lock"]]
    payload = {
        "status": "rollup_complete",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "hash_lock_id": lock["hash_lock_id"],
        "combined_packet_hash": lock.get("combined_packet_hash"),
        "combined_runner_hash": lock.get("combined_runner_hash"),
        "combined_execution_lock_hash": lock.get("combined_execution_lock_hash"),
        "aggregate_all_completed_analyzed_runs": aggregate(rows),
        "aggregate_current_lock_matching_runs": aggregate(current_rows),
        "claim_rule": "Use current-lock matching runs for strict public claims. Use older completed analyzed runs only as labeled diagnostics.",
        "runs": rows,
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "hash_locked_lift_rollup.json"
    md_path = out_dir / "hash_locked_lift_rollup.md"
    csv_path = out_dir / "hash_locked_lift_rollup.csv"
    json_path.write_text(json.dumps(payload, indent=2) + "\n")
    write_markdown(md_path, payload)
    write_csv(csv_path, rows)
    print(json.dumps({
        "status": "ROLLUP_COMPLETE",
        "run_count": len(rows),
        "current_lock_matching_run_count": len(current_rows),
        "mean_percent_lift_clean_all_completed": payload["aggregate_all_completed_analyzed_runs"]["mean_percent_lift_clean"],
        "mean_percent_lift_clean_current_lock": payload["aggregate_current_lock_matching_runs"]["mean_percent_lift_clean"],
        "json": str(json_path),
        "md": str(md_path),
        "csv": str(csv_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
