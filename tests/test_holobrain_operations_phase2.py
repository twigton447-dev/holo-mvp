from pathlib import Path
import hashlib
import subprocess

from holobrain.operations.ledger import (
    BENCHMARK_GATE_RULE,
    DAILY_CHECKLIST_KEYS,
    build_daily_status_report,
)
from holobrain.operations.sentinel import (
    DEFAULT_REQUIRED_ARTIFACTS,
    ArtifactRequirement,
    MetadataMarker,
    run_integrity_checks,
)


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_STATE = ROOT / "docs" / "benchmark" / "CANONICAL_BENCHMARK_STATE_2026-06-25.md"
OPERATIONS_POLICY_REF = "holobrain/operations/HoloBrain_Daily_Operations_Policy_v0.1.md"


def test_sentinel_required_artifacts_present():
    report = run_integrity_checks(ROOT)

    assert report.required_artifacts_present is True
    assert report.missing_artifacts == ()
    assert {check.path for check in report.artifact_checks} == {
        requirement.path for requirement in DEFAULT_REQUIRED_ARTIFACTS
    }


def test_sentinel_required_artifacts_are_tracked():
    report = run_integrity_checks(ROOT)

    assert report.required_artifacts_tracked is True
    assert report.untracked_artifacts == ()


def test_sentinel_locked_metadata_present():
    report = run_integrity_checks(ROOT)

    assert report.locked_metadata_present is True
    assert report.metadata_gaps == {}


def test_sentinel_detects_missing_artifact(tmp_path):
    requirement = ArtifactRequirement(
        path="missing_control_artifact.md",
        metadata_markers=(MetadataMarker("version", "Version: `0.1`"),),
    )

    report = run_integrity_checks(tmp_path, requirements=(requirement,))

    assert report.required_artifacts_present is False
    assert report.missing_artifacts == ("missing_control_artifact.md",)
    assert report.metadata_gaps == {
        "missing_control_artifact.md": ("version",)
    }


def test_sentinel_detects_untracked_required_artifact(tmp_path):
    subprocess.run(
        ("git", "init"),
        cwd=tmp_path,
        capture_output=True,
        check=True,
        text=True,
    )
    artifact = tmp_path / "untracked_control_artifact.md"
    artifact.write_text("Version: `0.1`\n", encoding="utf-8")
    requirement = ArtifactRequirement(
        path="untracked_control_artifact.md",
        metadata_markers=(MetadataMarker("version", "Version: `0.1`"),),
    )

    report = run_integrity_checks(tmp_path, requirements=(requirement,))

    assert report.required_artifacts_tracked is False
    assert report.untracked_artifacts == ("untracked_control_artifact.md",)
    assert "1 required artifact(s) are untracked" in report.local_only_fragility


def test_ledger_daily_status_includes_required_sections():
    report = build_daily_status_report(ROOT, report_date="2026-06-25")
    payload = report.to_dict()

    assert payload["report_date"] == "2026-06-25"
    assert payload["sections"] == (
        "locked_artifacts",
        "git_fragility",
        "daily_checklist",
        "benchmark_gate",
    )
    assert payload["locked_artifacts"]["present"] is True
    assert payload["locked_artifacts"]["tracked"] is True
    assert payload["locked_artifacts"]["metadata_present"] is True
    assert set(payload["daily_checklist"]) == set(DAILY_CHECKLIST_KEYS)
    assert payload["benchmark_gate"]["rule"] == BENCHMARK_GATE_RULE
    assert "# HoloBrain Daily Status - 2026-06-25" in report.render_compact_markdown()


def test_ledger_reports_no_benchmark_when_daily_checklist_incomplete():
    checklist = {key: True for key in DAILY_CHECKLIST_KEYS}
    checklist["remote_push_verified"] = False

    report = build_daily_status_report(
        ROOT,
        checklist=checklist,
        report_date="2026-06-25",
    )

    assert report.daily_checklist_complete is False
    assert report.benchmark_execution_allowed is False
    assert report.to_dict()["benchmark_gate"] == {
        "rule": BENCHMARK_GATE_RULE,
        "benchmark_execution_allowed": False,
    }


def test_ledger_does_not_modify_canonical_truth():
    before = hashlib.sha256(CANONICAL_STATE.read_bytes()).hexdigest()

    report = build_daily_status_report(ROOT, report_date="2026-06-25")
    report.to_dict()
    report.render_compact_markdown()

    after = hashlib.sha256(CANONICAL_STATE.read_bytes()).hexdigest()
    assert after == before


def test_operations_policy_is_referenced_by_canonical_state():
    text = CANONICAL_STATE.read_text(encoding="utf-8")

    assert OPERATIONS_POLICY_REF in text
    assert "benchmark execution is governed by the locked daily operations policy" in text
    assert "if the daily checklist is not completed, no benchmark execution may run that day" in text
