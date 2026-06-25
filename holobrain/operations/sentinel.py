"""Offline integrity checks for locked HoloBrain control artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class MetadataMarker:
    label: str
    marker: str


@dataclass(frozen=True)
class ArtifactRequirement:
    path: str
    metadata_markers: tuple[MetadataMarker, ...]


@dataclass(frozen=True)
class ArtifactCheck:
    path: str
    exists: bool
    tracked: bool
    missing_metadata: tuple[str, ...]


@dataclass(frozen=True)
class BranchStatus:
    branch: str | None
    upstream: str | None
    ahead: int
    behind: int
    dirty_paths: tuple[str, ...]
    untracked_paths: tuple[str, ...]
    raw: str
    git_available: bool

    @property
    def local_only_fragility(self) -> tuple[str, ...]:
        warnings: list[str] = []
        if not self.git_available:
            warnings.append("git status unavailable")
        if self.upstream is None:
            warnings.append("no upstream branch detected")
        if self.ahead:
            warnings.append(f"branch ahead of upstream by {self.ahead} commit(s)")
        if self.behind:
            warnings.append(f"branch behind upstream by {self.behind} commit(s)")
        if self.dirty_paths:
            warnings.append(f"worktree has {len(self.dirty_paths)} dirty tracked path(s)")
        if self.untracked_paths:
            warnings.append(f"worktree has {len(self.untracked_paths)} untracked path(s)")
        return tuple(warnings)


@dataclass(frozen=True)
class SentinelReport:
    root: Path
    artifact_checks: tuple[ArtifactCheck, ...]
    branch_status: BranchStatus

    @property
    def missing_artifacts(self) -> tuple[str, ...]:
        return tuple(check.path for check in self.artifact_checks if not check.exists)

    @property
    def untracked_artifacts(self) -> tuple[str, ...]:
        return tuple(
            check.path
            for check in self.artifact_checks
            if check.exists and not check.tracked
        )

    @property
    def metadata_gaps(self) -> Mapping[str, tuple[str, ...]]:
        return {
            check.path: check.missing_metadata
            for check in self.artifact_checks
            if check.missing_metadata
        }

    @property
    def required_artifacts_present(self) -> bool:
        return not self.missing_artifacts

    @property
    def required_artifacts_tracked(self) -> bool:
        return not self.untracked_artifacts

    @property
    def locked_metadata_present(self) -> bool:
        return not self.metadata_gaps

    @property
    def local_only_fragility(self) -> tuple[str, ...]:
        warnings = list(self.branch_status.local_only_fragility)
        if self.untracked_artifacts:
            warnings.append(
                f"{len(self.untracked_artifacts)} required artifact(s) are untracked"
            )
        return tuple(warnings)

    @property
    def control_artifacts_ok(self) -> bool:
        return (
            self.required_artifacts_present
            and self.required_artifacts_tracked
            and self.locked_metadata_present
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "required_artifacts_present": self.required_artifacts_present,
            "required_artifacts_tracked": self.required_artifacts_tracked,
            "locked_metadata_present": self.locked_metadata_present,
            "control_artifacts_ok": self.control_artifacts_ok,
            "missing_artifacts": self.missing_artifacts,
            "untracked_artifacts": self.untracked_artifacts,
            "metadata_gaps": self.metadata_gaps,
            "branch_status": {
                "branch": self.branch_status.branch,
                "upstream": self.branch_status.upstream,
                "ahead": self.branch_status.ahead,
                "behind": self.branch_status.behind,
                "dirty_paths": self.branch_status.dirty_paths,
                "untracked_paths": self.branch_status.untracked_paths,
                "git_available": self.branch_status.git_available,
            },
            "local_only_fragility": self.local_only_fragility,
        }


LOCKED_METADATA_MARKERS = (
    MetadataMarker("version", "Version: `0.1`"),
    MetadataMarker("status", "Status: `locked`"),
    MetadataMarker("effective_date", "Effective date: `2026-06-25`"),
    MetadataMarker("supersedes", "Supersedes: `none`"),
    MetadataMarker("superseded_by", "Superseded by: `none`"),
    MetadataMarker("source_of_truth", "Source of truth: this file"),
)

DEFAULT_REQUIRED_ARTIFACTS = (
    ArtifactRequirement(
        path="holo_profiles/locked_architecture_profiles.json",
        metadata_markers=(
            MetadataMarker("schema_version", '"schema_version": "holo.architecture_profiles.v1"'),
            MetadataMarker("manifest_version", '"manifest_version": "2026-06-25.1"'),
            MetadataMarker("profile_status", '"status": "locked"'),
            MetadataMarker(
                "profile_id",
                '"profile_id": "frontier_holo_optimized_opus_gpt55_v1"',
            ),
        ),
    ),
    ArtifactRequirement(
        path="holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md",
        metadata_markers=LOCKED_METADATA_MARKERS,
    ),
    ArtifactRequirement(
        path="holobrain/memory/HoloBrainMaintenanceRoster_v0.1.md",
        metadata_markers=LOCKED_METADATA_MARKERS
        + (
            MetadataMarker(
                "governing_doctrine",
                "Governing doctrine: `holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md`",
            ),
        ),
    ),
    ArtifactRequirement(
        path="holobrain/operations/HoloBrain_Daily_Operations_Policy_v0.1.md",
        metadata_markers=LOCKED_METADATA_MARKERS
        + (
            MetadataMarker(
                "benchmark_gate",
                "If the daily checklist is not completed, no benchmark execution may run that day.",
            ),
        ),
    ),
    ArtifactRequirement(
        path="docs/benchmark/CANONICAL_BENCHMARK_STATE_2026-06-25.md",
        metadata_markers=(
            MetadataMarker("title", "# Canonical Benchmark State - 2026-06-25"),
            MetadataMarker(
                "doctrine_ref",
                "holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md",
            ),
            MetadataMarker(
                "roster_ref",
                "holobrain/memory/HoloBrainMaintenanceRoster_v0.1.md",
            ),
            MetadataMarker(
                "operations_policy_ref",
                "holobrain/operations/HoloBrain_Daily_Operations_Policy_v0.1.md",
            ),
            MetadataMarker(
                "benchmark_gate",
                "if the daily checklist is not completed, no benchmark execution may run that day",
            ),
        ),
    ),
)


def run_integrity_checks(
    root: str | Path = ".",
    requirements: Sequence[ArtifactRequirement] = DEFAULT_REQUIRED_ARTIFACTS,
) -> SentinelReport:
    root_path = Path(root).resolve()
    tracked_paths = _git_tracked_paths(root_path, [requirement.path for requirement in requirements])
    artifact_checks = tuple(
        _check_artifact(root_path, requirement, tracked_paths)
        for requirement in requirements
    )
    return SentinelReport(
        root=root_path,
        artifact_checks=artifact_checks,
        branch_status=read_branch_status(root_path),
    )


def read_branch_status(root: str | Path = ".") -> BranchStatus:
    root_path = Path(root).resolve()
    result = _run_git(root_path, ("status", "--short", "--branch"))
    if result.returncode != 0:
        return BranchStatus(
            branch=None,
            upstream=None,
            ahead=0,
            behind=0,
            dirty_paths=(),
            untracked_paths=(),
            raw=result.stderr.strip(),
            git_available=False,
        )

    raw = result.stdout.strip()
    lines = raw.splitlines()
    branch, upstream, ahead, behind = _parse_branch_line(lines[0] if lines else "")
    dirty_paths: list[str] = []
    untracked_paths: list[str] = []
    for line in lines[1:]:
        if line.startswith("?? "):
            untracked_paths.append(line[3:])
        elif line:
            dirty_paths.append(line[3:] if len(line) > 3 else line)

    return BranchStatus(
        branch=branch,
        upstream=upstream,
        ahead=ahead,
        behind=behind,
        dirty_paths=tuple(dirty_paths),
        untracked_paths=tuple(untracked_paths),
        raw=raw,
        git_available=True,
    )


def _check_artifact(
    root: Path,
    requirement: ArtifactRequirement,
    tracked_paths: set[str],
) -> ArtifactCheck:
    path = root / requirement.path
    exists = path.exists()
    missing_metadata: tuple[str, ...] = tuple(marker.label for marker in requirement.metadata_markers)
    if exists:
        text = path.read_text(encoding="utf-8")
        missing_metadata = tuple(
            marker.label
            for marker in requirement.metadata_markers
            if marker.marker not in text
        )
    return ArtifactCheck(
        path=requirement.path,
        exists=exists,
        tracked=requirement.path in tracked_paths,
        missing_metadata=missing_metadata,
    )


def _git_tracked_paths(root: Path, paths: Iterable[str]) -> set[str]:
    tracked: set[str] = set()
    for path in paths:
        result = _run_git(root, ("ls-files", "--error-unmatch", path))
        if result.returncode == 0:
            tracked.add(path)
    return tracked


def _run_git(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )


def _parse_branch_line(line: str) -> tuple[str | None, str | None, int, int]:
    if not line.startswith("## "):
        return None, None, 0, 0

    body = line[3:]
    status_text = ""
    if " [" in body and body.endswith("]"):
        body, status_text = body.rsplit(" [", 1)
        status_text = status_text[:-1]

    branch = body
    upstream = None
    if "..." in body:
        branch, upstream = body.split("...", 1)

    ahead = _parse_count(status_text, "ahead")
    behind = _parse_count(status_text, "behind")
    return branch or None, upstream or None, ahead, behind


def _parse_count(status_text: str, label: str) -> int:
    match = re.search(rf"{label} (\d+)", status_text)
    return int(match.group(1)) if match else 0
