"""Daily HoloBrain operations report builder."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Mapping

from holobrain.operations.sentinel import SentinelReport, run_integrity_checks


DAILY_CHECKLIST_KEYS = (
    "repo_state_verified",
    "canonical_changes_protected",
    "dirty_work_snapshotted",
    "recovery_manifest_updated",
    "remote_push_verified",
    "fresh_clone_viability_confirmed",
    "local_only_gaps_recorded",
)

BENCHMARK_GATE_RULE = (
    "If the daily checklist is not completed, no benchmark execution may run that day."
)


@dataclass(frozen=True)
class DailyStatusReport:
    report_date: str
    sentinel: SentinelReport
    daily_checklist: Mapping[str, bool]
    benchmark_execution_allowed: bool
    benchmark_gate_rule: str = BENCHMARK_GATE_RULE

    @property
    def daily_checklist_complete(self) -> bool:
        return all(self.daily_checklist.values())

    @property
    def sections(self) -> tuple[str, ...]:
        return (
            "locked_artifacts",
            "git_fragility",
            "daily_checklist",
            "benchmark_gate",
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "report_date": self.report_date,
            "sections": self.sections,
            "locked_artifacts": {
                "present": self.sentinel.required_artifacts_present,
                "tracked": self.sentinel.required_artifacts_tracked,
                "metadata_present": self.sentinel.locked_metadata_present,
                "missing_artifacts": self.sentinel.missing_artifacts,
                "untracked_artifacts": self.sentinel.untracked_artifacts,
                "metadata_gaps": self.sentinel.metadata_gaps,
            },
            "git_fragility": {
                "branch": self.sentinel.branch_status.branch,
                "upstream": self.sentinel.branch_status.upstream,
                "ahead": self.sentinel.branch_status.ahead,
                "behind": self.sentinel.branch_status.behind,
                "warnings": self.sentinel.local_only_fragility,
            },
            "daily_checklist": dict(self.daily_checklist),
            "daily_checklist_complete": self.daily_checklist_complete,
            "benchmark_gate": {
                "rule": self.benchmark_gate_rule,
                "benchmark_execution_allowed": self.benchmark_execution_allowed,
            },
        }

    def render_compact_markdown(self) -> str:
        status = "ALLOW" if self.benchmark_execution_allowed else "BLOCK"
        warnings = self.sentinel.local_only_fragility or ("none",)
        lines = [
            f"# HoloBrain Daily Status - {self.report_date}",
            "",
            f"- Benchmark gate: `{status}`",
            f"- Daily checklist complete: `{str(self.daily_checklist_complete).lower()}`",
            f"- Required artifacts present: `{str(self.sentinel.required_artifacts_present).lower()}`",
            f"- Required artifacts tracked: `{str(self.sentinel.required_artifacts_tracked).lower()}`",
            f"- Locked metadata present: `{str(self.sentinel.locked_metadata_present).lower()}`",
            f"- Local-only fragility: `{'; '.join(warnings)}`",
            "",
            self.benchmark_gate_rule,
        ]
        return "\n".join(lines)


def build_daily_status_report(
    root: str | Path = ".",
    *,
    checklist: Mapping[str, bool] | None = None,
    report_date: str | None = None,
) -> DailyStatusReport:
    normalized_checklist = _normalize_checklist(checklist)
    sentinel = run_integrity_checks(root)
    checklist_complete = all(normalized_checklist.values())
    benchmark_execution_allowed = (
        checklist_complete
        and sentinel.control_artifacts_ok
        and not sentinel.local_only_fragility
    )
    return DailyStatusReport(
        report_date=report_date or date.today().isoformat(),
        sentinel=sentinel,
        daily_checklist=normalized_checklist,
        benchmark_execution_allowed=benchmark_execution_allowed,
    )


def _normalize_checklist(checklist: Mapping[str, bool] | None) -> dict[str, bool]:
    provided = checklist or {}
    return {key: bool(provided.get(key, False)) for key in DAILY_CHECKLIST_KEYS}
