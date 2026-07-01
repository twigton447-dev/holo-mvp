#!/usr/bin/env python3
"""Build a no-provider Wave5 completed-batch evidence summary.

This is deliberately narrower than the progress ledger:
- it never calls providers or judges,
- it aggregates only clean completed Wave5 batches,
- it stops the evidence line if any batch is invalid or mixed,
- it refuses to describe unrun batches as benchmark evidence.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
LEDGER_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_PROGRESS_LEDGER_2026_07_01.json"
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_COMPLETED_BATCH_EVIDENCE_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_COMPLETED_BATCH_EVIDENCE_2026_07_01.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


def current_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def result_path_for_run(run: dict[str, Any]) -> Path:
    return REPO_ROOT / run["run_dir"] / "live_results.json"


def completed_result_for_batch(batch: dict[str, Any]) -> dict[str, Any] | None:
    clean_runs = [run for run in batch["runs"] if run.get("readiness_passed") is True]
    if len(clean_runs) != 1:
        return None
    path = result_path_for_run(clean_runs[0])
    if not path.exists():
        raise RuntimeError(f"completed_run_missing_live_results:{clean_runs[0]['run_dir']}")
    result = load_json(path)
    if result.get("readiness_passed") is not True:
        raise RuntimeError(f"completed_run_not_ready:{path}")
    return result


def verdict_bucket_counts(results: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        "allow_packets": 0,
        "escalate_packets": 0,
        "allow_correct": 0,
        "escalate_correct": 0,
        "target_packets": 0,
        "guardrail_packets": 0,
    }
    for result in results:
        for row in result.get("benchmark_inventory", []):
            for side in ("target", "guardrail"):
                expected = row.get(f"{side}_expected")
                correct = row.get(f"{side}_final_correct")
                if expected == "ALLOW":
                    counts["allow_packets"] += 1
                    counts["allow_correct"] += int(bool(correct))
                elif expected == "ESCALATE":
                    counts["escalate_packets"] += 1
                    counts["escalate_correct"] += int(bool(correct))
            counts["target_packets"] += 1
            counts["guardrail_packets"] += 1
    return counts


def aggregate_tokens(results: list[dict[str, Any]]) -> dict[str, int]:
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for result in results:
        for key in totals:
            value = result.get("totals", {}).get(key)
            if isinstance(value, int):
                totals[key] += value
    return totals


def run_refs(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for result in results:
        run_dir = Path(result["run_dir"])
        if run_dir.is_absolute():
            try:
                run_ref = str(run_dir.relative_to(REPO_ROOT))
            except ValueError:
                run_ref = str(run_dir)
        else:
            run_ref = str(run_dir)
        refs.append(
            {
                "batch_id": result.get("batch_id"),
                "run_dir": run_ref,
                "live_results_ref": str((REPO_ROOT / run_ref / "live_results.json").relative_to(REPO_ROOT))
                if not Path(run_ref).is_absolute()
                else str(run_dir / "live_results.json"),
                "trace_hash": result.get("trace_hash"),
                "provider_calls": result.get("provider_calls"),
                "packet_correct": result.get("packet_correct"),
                "packet_count": result.get("packet_count"),
                "valid_pairs": result.get("valid_pairs"),
                "transport_recovered_call_count": result.get("transport_recovered_call_count"),
            }
        )
    return refs


def build() -> dict[str, Any]:
    ledger = load_json(LEDGER_JSON)
    batches = ledger["batch_rows"]
    invalid_batches = [
        row
        for row in batches
        if row["status"] in {"INVALID_STOP", "COMPLETE_WITH_PRIOR_INVALID_RUNS"}
    ]
    completed_batches = [row for row in batches if row["status"] == "COMPLETE"]
    completed_results = [completed_result_for_batch(row) for row in completed_batches]
    completed_results = [row for row in completed_results if row is not None]

    token_totals = aggregate_tokens(completed_results)
    verdict_counts = verdict_bucket_counts(completed_results)
    expected_provider_calls = sum(row["expected_provider_calls"] for row in completed_batches)
    observed_provider_calls = sum(int(result.get("provider_calls") or 0) for result in completed_results)
    completed_pairs = sum(int(result.get("valid_pairs") or 0) for result in completed_results)
    completed_packets = sum(int(result.get("packet_count") or 0) for result in completed_results)
    completed_correct = sum(int(result.get("packet_correct") or 0) for result in completed_results)

    checks = {
        "ledger_status_pass": ledger.get("status") == "PASS",
        "ledger_queue_not_invalid": ledger.get("queue_state") != "STOP_FOR_AUTOPSY",
        "invalid_batches_absent": not invalid_batches,
        "completed_results_match_completed_batches": len(completed_results) == len(completed_batches),
        "provider_calls_match_completed_expectation": observed_provider_calls == expected_provider_calls,
        "no_judge_calls": all(int(result.get("judge_calls") or 0) == 0 for result in completed_results),
        "all_completed_batches_ready": all(result.get("readiness_passed") is True for result in completed_results),
        "all_completed_packets_correct": completed_correct == completed_packets,
    }
    if not completed_results:
        checks["provider_calls_match_completed_expectation"] = expected_provider_calls == 0 and observed_provider_calls == 0
        checks["all_completed_packets_correct"] = True

    if invalid_batches:
        evidence_state = "STOP_FOR_AUTOPSY"
    elif not completed_batches:
        evidence_state = "NO_COMPLETED_BATCHES_YET"
    elif len(completed_batches) == len(batches):
        evidence_state = "WAVE5_COMPLETE"
    else:
        evidence_state = "PARTIAL_CLEAN_EVIDENCE"

    report = {
        "classification": "HOLOVERIFY_WAVE5_COMPLETED_BATCH_EVIDENCE_NO_PROVIDER",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "evidence_state": evidence_state,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_from_head": current_head(),
        "ledger_ref": str(LEDGER_JSON.relative_to(REPO_ROOT)),
        "freeze_root_hash": ledger["freeze_root_hash"],
        "claim_boundary": {
            "full_wave5_claim_allowed": evidence_state == "WAVE5_COMPLETE",
            "partial_claim_allowed": evidence_state == "PARTIAL_CLEAN_EVIDENCE",
            "zero_completed_batches_is_not_evidence": evidence_state == "NO_COMPLETED_BATCHES_YET",
            "stop_if_invalid_batch_present": bool(invalid_batches),
            "unrun_batches_count_as_no_evidence": True,
        },
        "checks": checks,
        "totals": {
            "total_batches": len(batches),
            "completed_batches": len(completed_batches),
            "not_started_batches": sum(1 for row in batches if row["status"] == "NOT_STARTED"),
            "invalid_batches": len(invalid_batches),
            "completed_pairs": completed_pairs,
            "completed_packets": completed_packets,
            "completed_correct_packets": completed_correct,
            "expected_provider_calls_for_completed_batches": expected_provider_calls,
            "observed_provider_calls_for_completed_batches": observed_provider_calls,
            "judge_calls": sum(int(result.get("judge_calls") or 0) for result in completed_results),
            "transport_recovered_call_count": sum(
                int(result.get("transport_recovered_call_count") or 0) for result in completed_results
            ),
            **token_totals,
            **verdict_counts,
        },
        "next_allowed_batch": ledger.get("next_allowed_batch") if not invalid_batches else None,
        "invalid_batches": [
            {
                "batch_id": row["batch_id"],
                "family_id": row["family_id"],
                "status": row["status"],
                "latest_run": row.get("latest_run"),
            }
            for row in invalid_batches
        ],
        "completed_run_refs": run_refs(completed_results),
    }
    return report


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# HoloVerify Wave5 Completed Batch Evidence",
        "",
        f"Status: `{report['status']}`",
        f"Evidence state: `{report['evidence_state']}`",
        f"Generated from head: `{report['generated_from_head']}`",
        f"Freeze root: `{report['freeze_root_hash']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for key, value in report["claim_boundary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Totals", ""])
    for key, value in report["totals"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Checks", "", "| Check | Value |", "| --- | --- |"])
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(["", "## Completed Runs", ""])
    if report["completed_run_refs"]:
        lines.extend(["| Batch | Run | Provider calls | Packets | Correct | Valid pairs |", "| --- | --- | --- | --- | --- | --- |"])
        for row in report["completed_run_refs"]:
            lines.append(
                f"| `{row['batch_id']}` | `{row['run_dir']}` | `{row['provider_calls']}` | "
                f"`{row['packet_count']}` | `{row['packet_correct']}` | `{row['valid_pairs']}` |"
            )
    else:
        lines.append("No Wave5 live batch has completed yet. This file is readiness scaffolding, not benchmark evidence.")
    lines.extend(["", "## Next Allowed Batch", ""])
    next_batch = report.get("next_allowed_batch")
    if next_batch:
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
    elif report["invalid_batches"]:
        lines.append("Stop for autopsy before running another Wave5 batch.")
    else:
        lines.append("No next batch is currently queued.")
    return "\n".join(lines) + "\n"


def main() -> int:
    report = build()
    write_json(OUT_JSON, report)
    write_text(OUT_MD, render_md(report))
    print(
        json.dumps(
            {
                "status": report["status"],
                "evidence_state": report["evidence_state"],
                **report["totals"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
