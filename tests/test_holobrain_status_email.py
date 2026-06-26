from pathlib import Path

from holobrain.operations.daily_control import DailyControlReport, build_daily_control_report
from holobrain.operations.status_email import (
    config_from_env,
    deliver_status_email,
    redact_secret_like_values,
    render_status_email,
)


ROOT = Path(__file__).resolve().parents[1]


def _fake_report(**overrides):
    real = build_daily_control_report(ROOT, report_date="2026-06-26")
    values = {
        "report_date": "2026-06-26",
        "benchmark_gate": "BLOCK",
        "branch": "recovery/test",
        "local_head": "localsha",
        "remote_sha": "remotesha",
        "sync_status": "synced",
        "dirty_tracked_count": 2,
        "untracked_count": 1,
        "protected_artifacts_status": "ok",
        "phase_1_2_test_status": "not_run",
        "recovery_backup_gaps": ("daily checklist incomplete",),
        "recommended_next_action": "Resolve parked local-only gaps.",
        "ledger_status": real.ledger_status,
    }
    values.update(overrides)
    return DailyControlReport(**values)


def test_email_config_uses_env_var_names_without_requiring_secrets():
    env = {
        "HOLOBRAIN_STATUS_EMAIL_TO": "to@example.com",
        "HOLOBRAIN_STATUS_EMAIL_FROM": "from@example.com",
        "HOLOBRAIN_STATUS_EMAIL_PROVIDER": "smtp",
    }

    config = config_from_env(env)

    assert config.to == "to@example.com"
    assert config.from_ == "from@example.com"
    assert config.provider == "smtp"
    assert config.smtp_secret_present is False
    assert config.missing_required == ()


def test_no_send_mode_does_not_send_email():
    result = deliver_status_email(_fake_report(), dry_run=False, no_send=True)

    assert result.sent is False
    assert result.no_send is True
    assert result.reason == "no_send"


def test_dry_run_mode_does_not_send_email():
    result = deliver_status_email(_fake_report(), dry_run=True, no_send=False)

    assert result.sent is False
    assert result.dry_run is True
    assert result.reason == "dry_run"


def test_email_body_redacts_secret_like_values():
    report = _fake_report(
        recommended_next_action="Do not expose api_key=sk-testsecret123456 token=abc123.",
    )
    env = {"HOLOBRAIN_STATUS_SMTP_SECRET": "smtp-secret-value"}

    body = render_status_email(report, env=env).body
    redacted = redact_secret_like_values("password=hunter2 sk-testsecret123456", env=env)

    assert "sk-testsecret123456" not in body
    assert "abc123" not in body
    assert "smtp-secret-value" not in body
    assert "[REDACTED]" in body
    assert "hunter2" not in redacted


def test_email_body_excludes_raw_packets_traces_secrets_and_full_diffs():
    report = _fake_report(
        recovery_backup_gaps=(
            "diff --git a/private b/private",
            "raw_trace_dump: hidden",
            "benchmark packet contents: hidden",
            "worktree has 2 dirty tracked path(s)",
        ),
        recommended_next_action="No full diffs or secrets should be included.",
    )

    body = render_status_email(report).body.lower()

    assert "diff --git" not in body
    assert "raw_trace" not in body
    assert "raw trace" not in body
    assert "benchmark packet contents" not in body
    assert "sk-" not in body
    assert "worktree has 2 dirty tracked path(s)" in body


def test_email_benchmark_gate_is_open_or_block():
    message = render_status_email(_fake_report(benchmark_gate="OPEN"))

    assert "Benchmark gate: OPEN" in message.body
    assert message.subject.endswith(": OPEN")
