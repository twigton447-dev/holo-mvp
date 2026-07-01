#!/usr/bin/env python3
"""Read-only Wave5 live batch status checker.

This is an operator tool, not a runner. It never calls providers or judges.
It inspects the Wave5 batch queue and any existing live-run folders, including
partial artifacts, so an in-progress or failed batch can be classified without
rerunning anything.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
HANDOFF_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_OPERATOR_HANDOFF_2026_07_01.json"
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_STATUS_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_STATUS_2026_07_01.md"
STABLE_CREATED_AT_UTC = "2026-07-01T00:00:00+00:00"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def trace_line_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as handle:
        return sum(1 for line in handle if line.strip())


def run_root_for_batch(batch: dict[str, Any]) -> Path:
    live_preflight_ref = Path(batch["live_preflight_ref"])
    return REPO_ROOT / live_preflight_ref.parent / "live_runs"


def summarize_run(run_dir: Path) -> dict[str, Any]:
    live_results_path = run_dir / "live_results.json"
    live_summary_path = run_dir / "live_summary.md"
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    lock_path = run_dir / "LOCK_VALIDATION.json"
    leakage_paths = sorted(run_dir.glob("*NO_LEAKAGE_AUDIT.json"))
    trace_lines = trace_line_count(trace_path)
    artifact_flags = {
        "live_results_exists": live_results_path.exists(),
        "live_summary_exists": live_summary_path.exists(),
        "trace_exists": trace_path.exists(),
        "lock_validation_exists": lock_path.exists(),
        "no_leakage_audit_exists": bool(leakage_paths),
    }
    if not live_results_path.exists():
        return {
            "run_id": run_dir.name,
            "run_dir": rel(run_dir),
            "status": "RUN_ARTIFACTS_IN_PROGRESS_OR_INCOMPLETE",
            "readiness_passed": False,
            "classification": "LIVE_RESULTS_NOT_PRESENT",
            "invalidation_reason": "LIVE_RESULTS_NOT_PRESENT",
            "provider_calls": trace_lines,
            "expected_provider_calls": None,
            "worker_calls": None,
            "gov_calls": None,
            "judge_calls": None,
            "root_failure": None,
            "trace_line_count": trace_lines,
            "artifact_flags": artifact_flags,
        }

    result = load_json(live_results_path)
    readiness = result.get("readiness_passed") is True
    return {
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "status": "COMPLETE" if readiness else "INVALID_OR_INCOMPLETE",
        "readiness_passed": readiness,
        "classification": result.get("classification"),
        "invalidation_reason": result.get("invalidation_reason"),
        "provider_calls": result.get("provider_calls"),
        "expected_provider_calls": result.get("expected_provider_calls"),
        "worker_calls": result.get("worker_calls"),
        "gov_calls": result.get("gov_calls"),
        "judge_calls": result.get("judge_calls"),
        "root_failure": result.get("root_failure"),
        "trace_line_count": trace_lines,
        "artifact_flags": artifact_flags,
    }


def summarize_batch(batch: dict[str, Any]) -> dict[str, Any]:
    run_root = run_root_for_batch(batch)
    run_dirs = sorted([path for path in run_root.glob("run_*") if path.is_dir()]) if run_root.exists() else []
    runs = [summarize_run(path) for path in run_dirs]
    ready_runs = [run for run in runs if run["readiness_passed"] is True]
    nonready_runs = [run for run in runs if run["readiness_passed"] is not True]
    if not runs:
        status = "NOT_STARTED"
    elif ready_runs and not nonready_runs:
        status = "COMPLETE"
    elif ready_runs and nonready_runs:
        status = "COMPLETE_WITH_PRIOR_INVALID_OR_INCOMPLETE_RUNS"
    elif any(run["status"] == "RUN_ARTIFACTS_IN_PROGRESS_OR_INCOMPLETE" for run in runs):
        status = "RUN_IN_PROGRESS_OR_INCOMPLETE"
    else:
        status = "INVALID_STOP"
    return {
        "batch_id": batch["batch_id"],
        "family_id": batch["family_id"],
        "pairs": batch["pairs"],
        "packets": batch["packets"],
        "expected_provider_calls": batch["expected_provider_calls"],
        "approval_packet_sha256": batch["approval_packet_sha256"],
        "run_command_after_explicit_approval": batch["run_command_after_explicit_approval"],
        "run_root": rel(run_root),
        "status": status,
        "run_count": len(runs),
        "ready_run_count": len(ready_runs),
        "nonready_run_count": len(nonready_runs),
        "latest_run": runs[-1] if runs else None,
        "runs": runs,
    }


def filtered_batches(handoff: dict[str, Any], family_id: str | None, batch_number: int | None) -> list[dict[str, Any]]:
    rows = handoff["batch_queue"]
    if family_id:
        rows = [row for row in rows if row["family_id"] == family_id]
    if batch_number is not None:
        suffix = f"_{batch_number:03d}"
        rows = [row for row in rows if row["batch_id"].endswith(suffix)]
    return rows


def queue_state(rows: list[dict[str, Any]]) -> tuple[str, dict[str, Any] | None]:
    for row in rows:
        if row["status"] == "COMPLETE":
            continue
        if row["status"] == "NOT_STARTED":
            return "READY_FOR_NEXT_BATCH", row
        if row["status"] == "RUN_IN_PROGRESS_OR_INCOMPLETE":
            return "RUN_IN_PROGRESS_OR_INCOMPLETE", row
        return "STOP_FOR_AUTOPSY", row
    return "COMPLETE", None


def build_report(family_id: str | None = None, batch_number: int | None = None) -> dict[str, Any]:
    handoff = load_json(HANDOFF_JSON)
    rows = [summarize_batch(batch) for batch in filtered_batches(handoff, family_id, batch_number)]
    state, blocking_or_next = queue_state(rows)
    checks = {
        "handoff_status_pass": handoff.get("status") == "PASS",
        "selected_batches_present": bool(rows),
        "provider_calls_by_status_checker": True,
        "judge_calls_by_status_checker": True,
    }
    return {
        "classification": "HOLOVERIFY_WAVE5_BATCH_STATUS_NO_PROVIDER",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "created_at_utc": STABLE_CREATED_AT_UTC,
        "provider_calls_by_this_status_check": 0,
        "judge_calls_by_this_status_check": 0,
        "filters": {"family_id": family_id, "batch_number": batch_number},
        "checks": checks,
        "queue_state": state,
        "next_or_blocking_batch": {
            "batch_id": blocking_or_next["batch_id"],
            "family_id": blocking_or_next["family_id"],
            "status": blocking_or_next["status"],
            "approval_packet_sha256": blocking_or_next["approval_packet_sha256"],
            "run_command_after_explicit_approval": blocking_or_next["run_command_after_explicit_approval"],
        }
        if blocking_or_next
        else None,
        "totals": {
            "selected_batches": len(rows),
            "run_folders": sum(row["run_count"] for row in rows),
            "completed_batches": sum(1 for row in rows if row["status"] == "COMPLETE"),
            "not_started_batches": sum(1 for row in rows if row["status"] == "NOT_STARTED"),
            "invalid_stop_batches": sum(1 for row in rows if row["status"] == "INVALID_STOP"),
            "in_progress_or_incomplete_batches": sum(1 for row in rows if row["status"] == "RUN_IN_PROGRESS_OR_INCOMPLETE"),
            "provider_calls_observed_from_artifacts": sum(
                int(run.get("provider_calls") or run.get("trace_line_count") or 0)
                for row in rows
                for run in row["runs"]
            ),
        },
        "batch_rows": rows,
    }


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# HoloVerify Wave5 Batch Status",
        "",
        f"Status: `{report['status']}`",
        f"Queue state: `{report['queue_state']}`",
        f"Provider calls by this status check: `{report['provider_calls_by_this_status_check']}`",
        f"Judge calls by this status check: `{report['judge_calls_by_this_status_check']}`",
        "",
        "## Totals",
        "",
    ]
    for key, value in report["totals"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Next Or Blocking Batch", ""])
    batch = report.get("next_or_blocking_batch")
    if batch:
        lines.extend(
            [
                f"- Batch: `{batch['batch_id']}`",
                f"- Family: `{batch['family_id']}`",
                f"- Status: `{batch['status']}`",
                f"- Approval SHA: `{batch['approval_packet_sha256']}`",
                "",
                "```bash",
                batch["run_command_after_explicit_approval"],
                "```",
            ]
        )
    else:
        lines.append("No next or blocking batch. Selected queue is complete.")
    lines.extend(
        [
            "",
            "## Batch Rows",
            "",
            "| Batch | Family | Status | Runs | Latest run | Provider calls observed | Invalidation |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["batch_rows"]:
        latest = row.get("latest_run") or {}
        latest_run = latest.get("run_id") or "N/A"
        calls = latest.get("provider_calls") or latest.get("trace_line_count") or 0
        invalidation = latest.get("invalidation_reason") or "N/A"
        lines.append(
            f"| `{row['batch_id']}` | `{row['family_id']}` | `{row['status']}` | `{row['run_count']}` | "
            f"`{latest_run}` | `{calls}` | `{invalidation}` |"
        )
    lines.extend(["", "## Boundary", "", "This status check is read-only and no-provider. It never runs Holo, solo, or judges."])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family")
    parser.add_argument("--batch-number", type=int)
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    report = build_report(args.family, args.batch_number)
    if args.write_report:
        write_json(OUT_JSON, report)
        write_text(OUT_MD, render_md(report))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
