"""No-send email rendering for HoloBrain daily status reports."""

from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
import os
import re
import smtplib
from typing import Mapping


EMAIL_ENV_VARS = (
    "HOLOBRAIN_STATUS_EMAIL_TO",
    "HOLOBRAIN_STATUS_EMAIL_FROM",
    "HOLOBRAIN_STATUS_EMAIL_PROVIDER",
    "HOLOBRAIN_STATUS_SMTP_HOST",
    "HOLOBRAIN_STATUS_SMTP_USER",
    "HOLOBRAIN_STATUS_SMTP_SECRET",
)

OMITTED_MARKERS = (
    "raw trace",
    "raw_trace",
    "trace dump",
    "diff --git",
    "benchmark packet",
    "private key",
)


@dataclass(frozen=True)
class EmailConfig:
    to: str | None
    from_: str | None
    provider: str | None
    smtp_host: str | None
    smtp_user: str | None
    smtp_secret_present: bool

    @property
    def missing_required(self) -> tuple[str, ...]:
        missing: list[str] = []
        if not self.to:
            missing.append("HOLOBRAIN_STATUS_EMAIL_TO")
        if not self.from_:
            missing.append("HOLOBRAIN_STATUS_EMAIL_FROM")
        if not self.provider:
            missing.append("HOLOBRAIN_STATUS_EMAIL_PROVIDER")
        return tuple(missing)


@dataclass(frozen=True)
class StatusEmail:
    subject: str
    body: str
    config: EmailConfig


@dataclass(frozen=True)
class EmailDeliveryResult:
    sent: bool
    dry_run: bool
    no_send: bool
    reason: str
    message: StatusEmail


def config_from_env(env: Mapping[str, str] | None = None) -> EmailConfig:
    source = env if env is not None else os.environ
    return EmailConfig(
        to=source.get("HOLOBRAIN_STATUS_EMAIL_TO"),
        from_=source.get("HOLOBRAIN_STATUS_EMAIL_FROM"),
        provider=source.get("HOLOBRAIN_STATUS_EMAIL_PROVIDER"),
        smtp_host=source.get("HOLOBRAIN_STATUS_SMTP_HOST"),
        smtp_user=source.get("HOLOBRAIN_STATUS_SMTP_USER"),
        smtp_secret_present=bool(source.get("HOLOBRAIN_STATUS_SMTP_SECRET")),
    )


def render_status_email(
    report: object,
    *,
    env: Mapping[str, str] | None = None,
) -> StatusEmail:
    payload = _payload(report)
    config = config_from_env(env)
    gate = str(payload.get("benchmark_gate", "UNKNOWN"))
    date = str(payload.get("report_date", "unknown-date"))
    subject = f"HoloBrain Daily Status {date}: {gate}"
    gaps = _safe_join(payload.get("recovery_backup_gaps", ()))
    body = "\n".join(
        [
            f"HoloBrain Daily Status - {date}",
            "",
            f"Benchmark gate: {gate}",
            f"Branch: {payload.get('branch', 'unknown')}",
            f"Local HEAD: {payload.get('local_head', 'unknown')}",
            f"Remote SHA: {payload.get('remote_sha', 'unknown')}",
            f"Sync status: {payload.get('sync_status', 'unknown')}",
            f"Dirty tracked count: {payload.get('dirty_tracked_count', 'unknown')}",
            f"Untracked count: {payload.get('untracked_count', 'unknown')}",
            f"Protected artifacts status: {payload.get('protected_artifacts_status', 'unknown')}",
            f"Phase 1/2 test status: {payload.get('phase_1_2_test_status', 'not_run')}",
            f"Recovery/backup gaps: {gaps}",
            f"Recommended next action: {payload.get('recommended_next_action', 'none')}",
            "",
            "Unsafe private details are intentionally omitted from this email.",
        ]
    )
    body = redact_secret_like_values(body, env=env)
    subject = redact_secret_like_values(subject, env=env)
    return StatusEmail(subject=subject, body=body, config=config)


def deliver_status_email(
    report: object,
    *,
    env: Mapping[str, str] | None = None,
    dry_run: bool = True,
    no_send: bool = True,
    transport_factory: object | None = None,
) -> EmailDeliveryResult:
    message = render_status_email(report, env=env)
    if no_send:
        return EmailDeliveryResult(
            sent=False,
            dry_run=dry_run,
            no_send=True,
            reason="no_send",
            message=message,
        )
    if dry_run:
        return EmailDeliveryResult(
            sent=False,
            dry_run=True,
            no_send=False,
            reason="dry_run",
            message=message,
        )
    missing = _missing_send_config(message.config)
    if missing:
        return EmailDeliveryResult(
            sent=False,
            dry_run=False,
            no_send=False,
            reason=f"missing_config:{','.join(missing)}",
            message=message,
        )
    _send_with_smtp(message, env=env, transport_factory=transport_factory)
    return EmailDeliveryResult(
        sent=True,
        dry_run=False,
        no_send=False,
        reason="sent",
        message=message,
    )


def redact_secret_like_values(text: str, *, env: Mapping[str, str] | None = None) -> str:
    redacted = text
    source = env if env is not None else os.environ
    for key in EMAIL_ENV_VARS:
        value = source.get(key)
        if value and key.endswith(("SECRET", "TOKEN", "KEY")):
            redacted = redacted.replace(value, "[REDACTED]")
    patterns = (
        r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*[^\s,;]+",
        r"sk-[A-Za-z0-9_-]{8,}",
        r"ghp_[A-Za-z0-9_]{8,}",
        r"xox[baprs]-[A-Za-z0-9-]{8,}",
    )
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED]", redacted)
    return redacted


def _payload(report: object) -> Mapping[str, object]:
    if hasattr(report, "to_dict"):
        payload = report.to_dict()
        if isinstance(payload, Mapping):
            return payload
    if isinstance(report, Mapping):
        return report
    raise TypeError("report must be a mapping or expose to_dict()")


def _missing_send_config(config: EmailConfig) -> tuple[str, ...]:
    missing = list(config.missing_required)
    if config.provider and config.provider.lower() != "smtp":
        missing.append("HOLOBRAIN_STATUS_EMAIL_PROVIDER=smtp")
    if not config.smtp_host:
        missing.append("HOLOBRAIN_STATUS_SMTP_HOST")
    if not config.smtp_user:
        missing.append("HOLOBRAIN_STATUS_SMTP_USER")
    if not config.smtp_secret_present:
        missing.append("HOLOBRAIN_STATUS_SMTP_SECRET")
    return tuple(missing)


def _send_with_smtp(
    message: StatusEmail,
    *,
    env: Mapping[str, str] | None = None,
    transport_factory: object | None = None,
) -> None:
    source = env if env is not None else os.environ
    smtp_host = source["HOLOBRAIN_STATUS_SMTP_HOST"]
    smtp_user = source["HOLOBRAIN_STATUS_SMTP_USER"]
    smtp_secret = source["HOLOBRAIN_STATUS_SMTP_SECRET"]
    email_message = EmailMessage()
    email_message["Subject"] = message.subject
    email_message["To"] = message.config.to or ""
    email_message["From"] = message.config.from_ or ""
    email_message.set_content(message.body)

    factory = transport_factory or smtplib.SMTP_SSL
    with factory(smtp_host) as smtp:
        smtp.login(smtp_user, smtp_secret)
        smtp.send_message(email_message)


def _safe_join(value: object) -> str:
    if isinstance(value, str):
        items = (value,)
    else:
        try:
            items = tuple(str(item) for item in value)  # type: ignore[arg-type]
        except TypeError:
            items = (str(value),)
    safe_items = [_sanitize_line(item) for item in items]
    return "; ".join(item for item in safe_items if item) or "none"


def _sanitize_line(text: str) -> str:
    lowered = text.lower()
    if any(marker in lowered for marker in OMITTED_MARKERS):
        return "[omitted unsafe detail]"
    return redact_secret_like_values(text)
