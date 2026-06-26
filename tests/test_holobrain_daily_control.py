import hashlib
from pathlib import Path

from holobrain.operations.daily_control import (
    DailyControlReport,
    build_daily_control_report,
    main,
    render_markdown_report,
    run_daily_control,
    write_daily_report,
)


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_FILES = (
    ROOT / "docs" / "benchmark" / "CANONICAL_BENCHMARK_STATE_2026-06-25.md",
    ROOT / "holobrain" / "memory" / "HoloGov_Memory_Doctrine_v0.1.md",
    ROOT / "holobrain" / "memory" / "HoloBrainMaintenanceRoster_v0.1.md",
    ROOT / "holobrain" / "operations" / "HoloBrain_Daily_Operations_Policy_v0.1.md",
)


def _fake_report() -> DailyControlReport:
    real = build_daily_control_report(ROOT, report_date="2026-06-26")
    return DailyControlReport(
        report_date="2026-06-26",
        benchmark_gate="BLOCK",
        branch="recovery/test",
        local_head="localsha",
        remote_sha="remotesha",
        sync_status="synced",
        dirty_tracked_count=2,
        untracked_count=1,
        protected_artifacts_status="ok",
        phase_1_2_test_status="not_run",
        recovery_backup_gaps=("daily checklist incomplete",),
        recommended_next_action="Resolve parked local-only gaps.",
        ledger_status=real.ledger_status,
    )


def test_daily_control_report_schema_contains_required_fields():
    report = build_daily_control_report(ROOT, report_date="2026-06-26")
    payload = report.to_dict()

    assert set(payload) == {
        "report_date",
        "benchmark_gate",
        "branch",
        "local_head",
        "remote_sha",
        "sync_status",
        "dirty_tracked_count",
        "untracked_count",
        "protected_artifacts_status",
        "phase_1_2_test_status",
        "recovery_backup_gaps",
        "recommended_next_action",
    }
    assert payload["benchmark_gate"] in {"OPEN", "BLOCK"}
    assert payload["phase_1_2_test_status"] == "not_run"


def test_daily_control_default_mode_does_not_send_email():
    result = run_daily_control(ROOT, report_date="2026-06-26", email=True)

    assert result.email_delivery is not None
    assert result.email_delivery.sent is False
    assert result.email_delivery.reason == "no_send"
    assert result.report_path is None


def test_daily_control_terminal_output_contains_required_fields(capsys):
    exit_code = main(["--root", str(ROOT), "--date", "2026-06-26", "--dry-run"])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "benchmark_gate:" in out
    assert "branch:" in out
    assert "local_head:" in out
    assert "remote_sha:" in out
    assert "recommended_next_action:" in out


def test_write_report_writes_only_under_recovery_daily_status(tmp_path):
    report = _fake_report()

    report_path = write_daily_report(report, tmp_path)

    assert report_path == tmp_path / "recovery" / "daily_status" / "2026-06-26.md"
    assert report_path.exists()
    assert "HoloBrain Daily Control" in report_path.read_text(encoding="utf-8")
    assert render_markdown_report(report).startswith("# HoloBrain Daily Control")


def test_daily_control_does_not_modify_canonical_truth():
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in CANONICAL_FILES
    }

    run_daily_control(ROOT, report_date="2026-06-26", write_report=False, email=True)

    after = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in CANONICAL_FILES
    }
    assert after == before
