"""Manual HoloBrain daily control command.

This module is intentionally offline-only. It reads HoloSentinel and
HoloLedger state, renders a compact status report, and can optionally write a
draft report under recovery/daily_status/. It does not send email by default
and does not modify canonical truth files.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import subprocess
from typing import Sequence

from holobrain.operations.ledger import DailyStatusReport, build_daily_status_report


NOT_RUN = "not_run"
UNKNOWN = "unknown"


@dataclass(frozen=True)
class DailyControlReport:
    report_date: str
    benchmark_gate: str
    branch: str
    local_head: str
    remote_sha: str
    sync_status: str
    dirty_tracked_count: int
    untracked_count: int
    protected_artifacts_status: str
    phase_1_2_test_status: str
    recovery_backup_gaps: tuple[str, ...]
    recommended_next_action: str
    ledger_status: DailyStatusReport

    def to_dict(self) -> dict[str, object]:
        return {
            "report_date": self.report_date,
            "benchmark_gate": self.benchmark_gate,
            "branch": self.branch,
            "local_head": self.local_head,
            "remote_sha": self.remote_sha,
            "sync_status": self.sync_status,
            "dirty_tracked_count": self.dirty_tracked_count,
            "untracked_count": self.untracked_count,
            "protected_artifacts_status": self.protected_artifacts_status,
            "phase_1_2_test_status": self.phase_1_2_test_status,
            "recovery_backup_gaps": self.recovery_backup_gaps,
            "recommended_next_action": self.recommended_next_action,
        }


@dataclass(frozen=True)
class DailyControlRunResult:
    report: DailyControlReport
    terminal_report: str
    report_path: Path | None = None
    email_delivery: object | None = None


def build_daily_control_report(
    root: str | Path = ".",
    *,
    report_date: str | None = None,
    phase_1_2_test_status: str = NOT_RUN,
) -> DailyControlReport:
    root_path = Path(root).resolve()
    ledger_status = build_daily_status_report(
        root_path,
        report_date=report_date or date.today().isoformat(),
    )
    sentinel = ledger_status.sentinel
    branch_status = sentinel.branch_status
    local_head = _git_value(root_path, ("rev-parse", "HEAD"))
    remote_sha = _read_remote_sha(root_path, branch_status.upstream)
    sync_status = _sync_status(
        local_head=local_head,
        remote_sha=remote_sha,
        ahead=branch_status.ahead,
        behind=branch_status.behind,
    )
    benchmark_gate = "OPEN" if ledger_status.benchmark_execution_allowed else "BLOCK"
    protected_status = "ok" if sentinel.control_artifacts_ok else "attention"
    gaps = _recovery_backup_gaps(ledger_status)

    return DailyControlReport(
        report_date=ledger_status.report_date,
        benchmark_gate=benchmark_gate,
        branch=branch_status.branch or UNKNOWN,
        local_head=local_head,
        remote_sha=remote_sha,
        sync_status=sync_status,
        dirty_tracked_count=len(branch_status.dirty_paths),
        untracked_count=len(branch_status.untracked_paths),
        protected_artifacts_status=protected_status,
        phase_1_2_test_status=phase_1_2_test_status,
        recovery_backup_gaps=gaps,
        recommended_next_action=_recommended_next_action(
            benchmark_gate=benchmark_gate,
            protected_artifacts_status=protected_status,
            gaps=gaps,
        ),
        ledger_status=ledger_status,
    )


def render_terminal_report(report: DailyControlReport) -> str:
    gaps = "; ".join(report.recovery_backup_gaps) if report.recovery_backup_gaps else "none"
    lines = [
        f"HoloBrain Daily Control - {report.report_date}",
        f"benchmark_gate: {report.benchmark_gate}",
        f"branch: {report.branch}",
        f"local_head: {report.local_head}",
        f"remote_sha: {report.remote_sha}",
        f"sync_status: {report.sync_status}",
        f"dirty_tracked_count: {report.dirty_tracked_count}",
        f"untracked_count: {report.untracked_count}",
        f"protected_artifacts_status: {report.protected_artifacts_status}",
        f"phase_1_2_test_status: {report.phase_1_2_test_status}",
        f"recovery_backup_gaps: {gaps}",
        f"recommended_next_action: {report.recommended_next_action}",
    ]
    return "\n".join(lines)


def render_markdown_report(report: DailyControlReport) -> str:
    gaps = report.recovery_backup_gaps or ("none",)
    lines = [
        f"# HoloBrain Daily Control - {report.report_date}",
        "",
        f"- Benchmark gate: `{report.benchmark_gate}`",
        f"- Branch: `{report.branch}`",
        f"- Local HEAD: `{report.local_head}`",
        f"- Remote SHA: `{report.remote_sha}`",
        f"- Sync status: `{report.sync_status}`",
        f"- Dirty tracked count: `{report.dirty_tracked_count}`",
        f"- Untracked count: `{report.untracked_count}`",
        f"- Protected artifacts status: `{report.protected_artifacts_status}`",
        f"- Phase 1/2 test status: `{report.phase_1_2_test_status}`",
        "- Recovery/backup gaps:",
    ]
    lines.extend(f"  - {gap}" for gap in gaps)
    lines.extend(
        [
            f"- Recommended next action: {report.recommended_next_action}",
            "",
            "This report is a draft status artifact. It does not update canonical benchmark state, doctrine, manifests, or memory objects.",
        ]
    )
    return "\n".join(lines)


def write_daily_report(report: DailyControlReport, root: str | Path = ".") -> Path:
    root_path = Path(root).resolve()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", report.report_date):
        raise ValueError("report_date must use YYYY-MM-DD")
    report_dir = root_path / "recovery" / "daily_status"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = (report_dir / f"{report.report_date}.md").resolve()
    if report_dir.resolve() not in report_path.parents:
        raise ValueError("daily report path escaped recovery/daily_status")
    report_path.write_text(render_markdown_report(report) + "\n", encoding="utf-8")
    return report_path


def run_daily_control(
    root: str | Path = ".",
    *,
    report_date: str | None = None,
    phase_1_2_test_status: str = NOT_RUN,
    dry_run: bool = True,
    no_send: bool = True,
    write_report: bool = False,
    email: bool = False,
) -> DailyControlRunResult:
    report = build_daily_control_report(
        root,
        report_date=report_date,
        phase_1_2_test_status=phase_1_2_test_status,
    )
    report_path = write_daily_report(report, root) if write_report else None
    email_delivery = None
    if email:
        from holobrain.operations.status_email import deliver_status_email

        email_delivery = deliver_status_email(report, dry_run=dry_run, no_send=no_send)
    return DailyControlRunResult(
        report=report,
        terminal_report=render_terminal_report(report),
        report_path=report_path,
        email_delivery=email_delivery,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run offline HoloBrain daily control.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--date", dest="report_date", default=None, help="Report date in YYYY-MM-DD format.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Safe default; no live delivery.")
    parser.add_argument("--no-send", action="store_true", default=True, help="Safe default; do not send email.")
    parser.add_argument("--email", action="store_true", help="Render email adapter output without sending.")
    parser.add_argument("--write-report", action="store_true", help="Write draft report under recovery/daily_status/.")
    parser.add_argument(
        "--phase-1-2-test-status",
        default=NOT_RUN,
        help="Status label for Phase 1/2 tests, for example pass, fail, or not_run.",
    )
    args = parser.parse_args(argv)

    result = run_daily_control(
        args.root,
        report_date=args.report_date,
        phase_1_2_test_status=args.phase_1_2_test_status,
        dry_run=args.dry_run,
        no_send=args.no_send,
        write_report=args.write_report,
        email=args.email,
    )
    print(result.terminal_report)
    if result.report_path is not None:
        print(f"draft_report_path: {result.report_path}")
    if result.email_delivery is not None:
        print(f"email_delivery: {result.email_delivery.reason}")
    return 0


def _git_value(root: Path, args: Sequence[str]) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return UNKNOWN
    return result.stdout.strip() or UNKNOWN


def _read_remote_sha(root: Path, upstream: str | None) -> str:
    if not upstream:
        return UNKNOWN
    return _git_value(root, ("rev-parse", upstream))


def _sync_status(*, local_head: str, remote_sha: str, ahead: int, behind: int) -> str:
    if local_head == UNKNOWN or remote_sha == UNKNOWN:
        return UNKNOWN
    if ahead and behind:
        return "diverged"
    if ahead:
        return "ahead"
    if behind:
        return "behind"
    if local_head == remote_sha:
        return "synced"
    return "mismatch"


def _recovery_backup_gaps(status: DailyStatusReport) -> tuple[str, ...]:
    gaps = list(status.sentinel.local_only_fragility)
    if not status.daily_checklist_complete:
        gaps.append("daily checklist incomplete")
    return tuple(gaps)


def _recommended_next_action(
    *,
    benchmark_gate: str,
    protected_artifacts_status: str,
    gaps: tuple[str, ...],
) -> str:
    if protected_artifacts_status != "ok":
        return "Repair or restore locked control artifacts before other work."
    if benchmark_gate == "BLOCK":
        if gaps:
            return "Resolve, protect, or explicitly park local-only gaps before benchmark execution."
        return "Complete the daily checklist before benchmark execution."
    return "Daily control is open; proceed only within the approved lane."


if __name__ == "__main__":
    raise SystemExit(main())
