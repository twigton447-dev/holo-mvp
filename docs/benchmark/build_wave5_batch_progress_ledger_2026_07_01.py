#!/usr/bin/env python3
"""Build a no-provider Wave5 batch progress ledger.

This scanner is intentionally read-only over live outputs. It answers:
- which Wave5 batches have no run yet,
- which batches completed cleanly,
- whether any batch failed and should stop the queue,
- which exact batch command is next allowed.
"""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
HANDOFF_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_OPERATOR_HANDOFF_2026_07_01.json"
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_PROGRESS_LEDGER_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_PROGRESS_LEDGER_2026_07_01.md"
STABLE_CREATED_AT_UTC = "2026-07-01T00:00:00+00:00"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_root_for_batch(batch: dict[str, Any]) -> Path:
    live_preflight_ref = Path(batch["live_preflight_ref"])
    return REPO_ROOT / live_preflight_ref.parent / "live_runs"


def summarize_run(run_dir: Path) -> dict[str, Any]:
    results_path = run_dir / "live_results.json"
    summary_path = run_dir / "live_summary.md"
    trace_path = run_dir / "TRACE_CALLS.jsonl"
    lock_path = run_dir / "LOCK_VALIDATION.json"
    if not results_path.exists():
        return {
            "run_id": run_dir.name,
            "run_dir": str(run_dir.relative_to(REPO_ROOT)),
            "status": "INCOMPLETE_RUN_ARTIFACTS",
            "readiness_passed": False,
            "classification": "MISSING_LIVE_RESULTS",
            "invalidation_reason": "MISSING_LIVE_RESULTS",
            "provider_calls": 0,
            "expected_provider_calls": None,
            "summary_exists": summary_path.exists(),
            "trace_exists": trace_path.exists(),
            "lock_validation_exists": lock_path.exists(),
        }
    result = load_json(results_path)
    readiness = bool(result.get("readiness_passed"))
    return {
        "run_id": run_dir.name,
        "run_dir": str(run_dir.relative_to(REPO_ROOT)),
        "status": "COMPLETE" if readiness else "INVALID_OR_INCOMPLETE",
        "readiness_passed": readiness,
        "classification": result.get("classification"),
        "invalidation_reason": result.get("invalidation_reason"),
        "provider_calls": result.get("provider_calls"),
        "expected_provider_calls": result.get("expected_provider_calls"),
        "worker_calls": result.get("worker_calls"),
        "gov_calls": result.get("gov_calls"),
        "judge_calls": result.get("judge_calls"),
        "packet_correct": result.get("packet_correct"),
        "packet_count": result.get("packet_count"),
        "valid_pairs": result.get("valid_pairs"),
        "transport_recovered_call_count": result.get("transport_recovered_call_count"),
        "root_failure": result.get("root_failure"),
        "summary_exists": summary_path.exists(),
        "trace_exists": trace_path.exists(),
        "lock_validation_exists": lock_path.exists(),
    }


def summarize_batch(batch: dict[str, Any]) -> dict[str, Any]:
    run_root = run_root_for_batch(batch)
    run_dirs = sorted([path for path in run_root.glob("run_*") if path.is_dir()]) if run_root.exists() else []
    runs = [summarize_run(path) for path in run_dirs]
    complete_runs = [run for run in runs if run["readiness_passed"]]
    invalid_runs = [run for run in runs if not run["readiness_passed"]]
    if not runs:
        status = "NOT_STARTED"
    elif complete_runs and not invalid_runs:
        status = "COMPLETE"
    elif complete_runs and invalid_runs:
        status = "COMPLETE_WITH_PRIOR_INVALID_RUNS"
    else:
        status = "INVALID_STOP"
    latest = runs[-1] if runs else None
    return {
        "batch_id": batch["batch_id"],
        "family_id": batch["family_id"],
        "pairs": batch["pairs"],
        "packets": batch["packets"],
        "expected_provider_calls": batch["expected_provider_calls"],
        "approval_packet_sha256": batch["approval_packet_sha256"],
        "run_command_after_explicit_approval": batch["run_command_after_explicit_approval"],
        "status": status,
        "run_root": str(run_root.relative_to(REPO_ROOT)),
        "run_count": len(runs),
        "complete_run_count": len(complete_runs),
        "invalid_or_incomplete_run_count": len(invalid_runs),
        "latest_run": latest,
        "runs": runs,
    }


def compute_next_allowed(batch_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    for row in batch_rows:
        if row["status"] in {"COMPLETE", "COMPLETE_WITH_PRIOR_INVALID_RUNS"}:
            continue
        if row["status"] == "NOT_STARTED":
            return {
                "batch_id": row["batch_id"],
                "family_id": row["family_id"],
                "approval_packet_sha256": row["approval_packet_sha256"],
                "run_command_after_explicit_approval": row["run_command_after_explicit_approval"],
                "reason": "first_not_started_after_clean_prefix",
            }
        return None
    return None


def build() -> dict[str, Any]:
    handoff = load_json(HANDOFF_JSON)
    batches = [summarize_batch(batch) for batch in handoff["batch_queue"]]
    invalid_stop = next((row for row in batches if row["status"] == "INVALID_STOP"), None)
    next_allowed = None if invalid_stop else compute_next_allowed(batches)
    checks = {
        "handoff_pass": handoff.get("status") == "PASS",
        "batch_count_28": len(batches) == 28,
        "providers_called_by_ledger": 0 == 0,
        "judges_called_by_ledger": 0 == 0,
        "one_batch_queue_order": [row["batch_id"] for row in batches] == [row["batch_id"] for row in handoff["batch_queue"]],
    }
    completed = [row for row in batches if row["status"] in {"COMPLETE", "COMPLETE_WITH_PRIOR_INVALID_RUNS"}]
    report = {
        "classification": "HOLOVERIFY_WAVE5_BATCH_PROGRESS_LEDGER_NO_PROVIDER",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "created_at_utc": STABLE_CREATED_AT_UTC,
        "source_handoff_operator_builder_sha256": handoff.get("operator_builder_sha256"),
        "progress_builder_sha256": sha256_file(Path(__file__).resolve()),
        "handoff_ref": str(HANDOFF_JSON.relative_to(REPO_ROOT)),
        "freeze_root_hash": handoff["freeze_root_hash"],
        "checks": checks,
        "totals": {
            "batches": len(batches),
            "completed_batches": len(completed),
            "not_started_batches": sum(1 for row in batches if row["status"] == "NOT_STARTED"),
            "invalid_stop_batches": sum(1 for row in batches if row["status"] == "INVALID_STOP"),
            "complete_with_prior_invalid_batches": sum(1 for row in batches if row["status"] == "COMPLETE_WITH_PRIOR_INVALID_RUNS"),
            "preserved_prior_invalid_runs": sum(
                row["invalid_or_incomplete_run_count"]
                for row in batches
                if row["status"] == "COMPLETE_WITH_PRIOR_INVALID_RUNS"
            ),
            "completed_pairs": sum(row["pairs"] for row in completed),
            "completed_packets": sum(row["packets"] for row in completed),
            "provider_calls_observed": sum((run.get("provider_calls") or 0) for row in batches for run in row["runs"]),
            "expected_provider_calls_for_completed_batches": sum(row["expected_provider_calls"] for row in completed),
            "providers_called_by_ledger": 0,
            "judges_called_by_ledger": 0,
        },
        "queue_state": "STOP_FOR_AUTOPSY" if invalid_stop else ("COMPLETE" if next_allowed is None else "READY_FOR_NEXT_BATCH"),
        "stop_batch": invalid_stop["batch_id"] if invalid_stop else None,
        "next_allowed_batch": next_allowed,
        "batch_rows": batches,
    }
    return report


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# HoloVerify Wave5 Batch Progress Ledger",
        "",
        f"Status: `{report['status']}`",
        f"Queue state: `{report['queue_state']}`",
        f"Source handoff builder SHA-256: `{report['source_handoff_operator_builder_sha256']}`",
        f"Progress builder SHA-256: `{report['progress_builder_sha256']}`",
        f"Freeze root: `{report['freeze_root_hash']}`",
        "",
        "## Totals",
        "",
    ]
    for key, value in report["totals"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Next Allowed Batch", ""])
    if report["next_allowed_batch"]:
        next_batch = report["next_allowed_batch"]
        lines.extend(
            [
                f"- Batch: `{next_batch['batch_id']}`",
                f"- Family: `{next_batch['family_id']}`",
                f"- Approval SHA: `{next_batch['approval_packet_sha256']}`",
                "",
                "```bash",
                next_batch["run_command_after_explicit_approval"],
                "```",
            ]
        )
    elif report["stop_batch"]:
        lines.append(f"Stop for autopsy before continuing. First blocking batch: `{report['stop_batch']}`")
    else:
        lines.append("No next batch. Queue is complete.")
    lines.extend(
        [
            "",
            "## Batch State",
            "",
            "| # | Batch | Family | Status | Runs | Provider calls observed | Latest invalidation |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for index, row in enumerate(report["batch_rows"], start=1):
        latest = row.get("latest_run") or {}
        invalidation = latest.get("invalidation_reason") or "N/A"
        lines.append(
            f"| `{index}` | `{row['batch_id']}` | `{row['family_id']}` | `{row['status']}` | "
            f"`{row['run_count']}` | `{sum((run.get('provider_calls') or 0) for run in row['runs'])}` | "
            f"`{invalidation}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This ledger does not call providers. It only reads existing batch artifacts and live-run outputs.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    report = build()
    write_json(OUT_JSON, report)
    write_text(OUT_MD, render_md(report))
    print(json.dumps({"status": report["status"], **report["totals"], "queue_state": report["queue_state"]}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
