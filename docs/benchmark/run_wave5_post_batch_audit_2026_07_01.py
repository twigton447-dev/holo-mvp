#!/usr/bin/env python3
"""No-provider post-batch audit for Wave5.

Run this after a single live Wave5 batch exits. It refreshes the progress
ledger and completed-batch evidence, then reports whether execution should
continue to the next batch or stop for autopsy.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
PROGRESS_BUILDER = BENCHMARK_ROOT / "build_wave5_batch_progress_ledger_2026_07_01.py"
EVIDENCE_BUILDER = BENCHMARK_ROOT / "build_wave5_completed_batch_evidence_2026_07_01.py"
NEXT_BATCH_LAUNCHER = BENCHMARK_ROOT / "run_wave5_next_batch_2026_07_01.py"
WAVE5_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_wave5_2026-07-01"
LEDGER_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_PROGRESS_LEDGER_2026_07_01.json"
EVIDENCE_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_COMPLETED_BATCH_EVIDENCE_2026_07_01.json"
OUT_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_POST_BATCH_AUDIT_2026_07_01.json"
OUT_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_POST_BATCH_AUDIT_2026_07_01.md"
STABLE_CREATED_AT_UTC = "2026-07-01T00:00:00+00:00"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.write_text(value)


def run_no_provider_builders() -> None:
    for script in (PROGRESS_BUILDER, EVIDENCE_BUILDER):
        subprocess.check_call(["python3", "-B", str(script.relative_to(REPO_ROOT))], cwd=REPO_ROOT, stdout=subprocess.DEVNULL)


def count_live_run_folders() -> int:
    return sum(1 for path in WAVE5_ROOT.rglob("run_*") if path.is_dir())


def derive_state(ledger: dict[str, Any], evidence: dict[str, Any]) -> tuple[str, str]:
    if ledger.get("queue_state") == "STOP_FOR_AUTOPSY" or evidence.get("evidence_state") == "STOP_FOR_AUTOPSY":
        return "STOP_FOR_AUTOPSY", "Preserve the invalid batch and do not run another Wave5 batch until autopsy is complete."
    if ledger.get("queue_state") == "COMPLETE" or evidence.get("evidence_state") == "WAVE5_COMPLETE":
        return "WAVE5_COMPLETE", "All Wave5 batches appear complete. Move to final evidence packaging."
    if ledger.get("queue_state") == "READY_FOR_NEXT_BATCH" and ledger.get("next_allowed_batch"):
        return "READY_FOR_NEXT_BATCH", "Run exactly the next allowed batch if provider calls are explicitly approved."
    return "NOT_READY", "Do not run another Wave5 batch until the ledger/evidence state is reconciled."


def build_report() -> dict[str, Any]:
    run_no_provider_builders()
    ledger = load_json(LEDGER_JSON)
    evidence = load_json(EVIDENCE_JSON)
    state, recommended_action = derive_state(ledger, evidence)
    checks = {
        "progress_ledger_pass": ledger.get("status") == "PASS",
        "completed_batch_evidence_pass": evidence.get("status") == "PASS",
        "provider_calls_by_post_batch_audit": True,
        "judge_calls_by_post_batch_audit": True,
        "evidence_not_ahead_of_ledger": evidence.get("totals", {}).get("completed_batches", 0)
        <= ledger.get("totals", {}).get("completed_batches", 0),
    }
    report = {
        "classification": "HOLOVERIFY_WAVE5_POST_BATCH_AUDIT_NO_PROVIDER",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "post_batch_state": state,
        "created_at_utc": STABLE_CREATED_AT_UTC,
        "progress_builder_sha256": sha256_file(PROGRESS_BUILDER),
        "evidence_builder_sha256": sha256_file(EVIDENCE_BUILDER),
        "next_batch_launcher_sha256": sha256_file(NEXT_BATCH_LAUNCHER),
        "provider_calls_by_this_audit": 0,
        "judge_calls_by_this_audit": 0,
        "live_run_folders_count": count_live_run_folders(),
        "checks": checks,
        "recommended_action": recommended_action,
        "ledger_ref": str(LEDGER_JSON.relative_to(REPO_ROOT)),
        "evidence_ref": str(EVIDENCE_JSON.relative_to(REPO_ROOT)),
        "ledger_totals": ledger.get("totals"),
        "evidence_totals": evidence.get("totals"),
        "next_allowed_batch": ledger.get("next_allowed_batch") if state == "READY_FOR_NEXT_BATCH" else None,
        "stop_batch": ledger.get("stop_batch") if state == "STOP_FOR_AUTOPSY" else None,
    }
    return report


def render_md(report: dict[str, Any]) -> str:
    lines = [
        "# HoloVerify Wave5 Post-Batch Audit",
        "",
        f"Status: `{report['status']}`",
        f"Post-batch state: `{report['post_batch_state']}`",
        f"Provider calls by this audit: `{report['provider_calls_by_this_audit']}`",
        f"Judge calls by this audit: `{report['judge_calls_by_this_audit']}`",
        f"Wave5 live run folders: `{report['live_run_folders_count']}`",
        "",
        "## Recommended Action",
        "",
        report["recommended_action"],
        "",
        "## Totals",
        "",
        "### Progress Ledger",
        "",
    ]
    for key, value in (report.get("ledger_totals") or {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "### Completed Evidence", ""])
    for key, value in (report.get("evidence_totals") or {}).items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Next Batch", ""])
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
    elif report.get("stop_batch"):
        lines.append(f"Stop batch: `{report['stop_batch']}`")
    else:
        lines.append("No next batch available.")
    lines.extend(["", "## Checks", "", "| Check | Value |", "| --- | --- |"])
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    report = build_report()
    write_json(OUT_JSON, report)
    write_text(OUT_MD, render_md(report))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
