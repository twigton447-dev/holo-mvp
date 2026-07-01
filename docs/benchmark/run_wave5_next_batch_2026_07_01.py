#!/usr/bin/env python3
"""Guarded launcher for the next Wave5 Holo batch.

Default behavior is no-provider: read the progress ledger and print/write the
next exact batch command. Live execution is only available with --run-live plus
the exact approval statement and approval packet SHA from the ledger.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
LEDGER_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_PROGRESS_LEDGER_2026_07_01.json"
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_NEXT_BATCH_LAUNCHER_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_NEXT_BATCH_LAUNCHER_2026_07_01.md"
DATE_STAMP = "2026_07_01"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


def expected_statement(batch_id: str) -> str:
    return (
        f"I explicitly approve provider calls for {batch_id} only, exactly as scoped in "
        f"{batch_id}_PROVIDER_APPROVAL_PACKET_{DATE_STAMP}."
    )


def batch_number(batch_id: str) -> int:
    return int(batch_id.rsplit("_", 1)[1])


def next_batch() -> dict[str, Any]:
    ledger = load_json(LEDGER_JSON)
    if ledger.get("status") != "PASS":
        raise RuntimeError(f"wave5_progress_ledger_not_pass:{ledger.get('status')}")
    if ledger.get("queue_state") != "READY_FOR_NEXT_BATCH":
        raise RuntimeError(f"wave5_queue_not_ready:{ledger.get('queue_state')}")
    batch = ledger.get("next_allowed_batch")
    if not batch:
        raise RuntimeError("wave5_next_allowed_batch_missing")
    return batch


def build_report() -> dict[str, Any]:
    batch = next_batch()
    statement = expected_statement(batch["batch_id"])
    return {
        "classification": "HOLOVERIFY_WAVE5_NEXT_BATCH_LAUNCHER_NO_PROVIDER",
        "status": "PASS",
        "provider_calls_by_this_launcher_report": 0,
        "judge_calls_by_this_launcher_report": 0,
        "ledger_ref": str(LEDGER_JSON.relative_to(REPO_ROOT)),
        "next_batch": {
            "batch_id": batch["batch_id"],
            "family_id": batch["family_id"],
            "batch_number": batch_number(batch["batch_id"]),
            "approval_packet_sha256": batch["approval_packet_sha256"],
            "approval_statement_required": statement,
            "run_command_after_explicit_approval": batch["run_command_after_explicit_approval"],
        },
        "live_execution_rule": {
            "one_batch_only": True,
            "requires_run_live_flag": True,
            "requires_exact_approval_statement": True,
            "requires_exact_approval_packet_sha256": True,
            "no_solo": True,
            "no_judges": True,
            "no_fallback_or_substitution": True,
        },
    }


def render_md(report: dict[str, Any]) -> str:
    batch = report["next_batch"]
    lines = [
        "# HoloVerify Wave5 Next Batch Launcher",
        "",
        f"Status: `{report['status']}`",
        f"Provider calls by this report: `{report['provider_calls_by_this_launcher_report']}`",
        f"Judge calls by this report: `{report['judge_calls_by_this_launcher_report']}`",
        "",
        "## Next Batch",
        "",
        f"- Batch: `{batch['batch_id']}`",
        f"- Family: `{batch['family_id']}`",
        f"- Batch number: `{batch['batch_number']}`",
        f"- Approval SHA: `{batch['approval_packet_sha256']}`",
        "",
        "Required approval statement:",
        "",
        f"`{batch['approval_statement_required']}`",
        "",
        "Command after explicit approval:",
        "",
        "```bash",
        batch["run_command_after_explicit_approval"],
        "```",
        "",
        "## Boundary",
        "",
        "This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.",
    ]
    return "\n".join(lines) + "\n"


def write_report() -> dict[str, Any]:
    report = build_report()
    write_json(OUT_JSON, report)
    write_text(OUT_MD, render_md(report))
    return report


def run_live(approval_statement: str | None, approval_packet_sha256: str | None) -> int:
    batch = next_batch()
    required_statement = expected_statement(batch["batch_id"])
    required_sha = batch["approval_packet_sha256"]
    if approval_statement != required_statement:
        raise RuntimeError("wave5_next_batch_approval_statement_mismatch")
    if approval_packet_sha256 != required_sha:
        raise RuntimeError("wave5_next_batch_approval_sha_mismatch")
    cmd = [
        "python3",
        "-B",
        "docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py",
        "--family",
        batch["family_id"],
        "--batch-number",
        str(batch_number(batch["batch_id"])),
        "--run-live",
        "--approval-packet-sha256",
        required_sha,
        "--approval-statement",
        required_statement,
    ]
    return subprocess.call(cmd, cwd=REPO_ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-handoff", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--approval-statement")
    parser.add_argument("--approval-packet-sha256")
    args = parser.parse_args()

    if args.run_live:
        try:
            return run_live(args.approval_statement, args.approval_packet_sha256)
        except RuntimeError as exc:
            print(
                json.dumps(
                    {
                        "status": "LOCKED",
                        "error": str(exc),
                        "provider_calls_started": False,
                        "judge_calls_started": False,
                    },
                    indent=2,
                    sort_keys=True,
                ),
                file=sys.stderr,
            )
            return 2

    report = write_report() if args.write_handoff else build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
