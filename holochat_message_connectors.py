"""Personal-only phone-message connector contracts for HoloChat.

OpenClaw or a future mobile bridge may read user-approved messages locally, but
HoloChat only accepts a bounded context event. Raw message bodies, attachments,
contact identifiers, and recipient details never belong in this ingress API.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import re
import secrets
from typing import Any


class MessageConnectorError(ValueError):
    """Raised when a connector request violates the phone-message contract."""


class MessageConnectorAuthenticationError(MessageConnectorError):
    """Raised when a local bridge cannot authenticate to a connector."""


SUPPORTED_PROVIDERS = frozenset({"openclaw_imessage", "openclaw_android"})
DEFAULT_PROVIDER_LABELS = {
    "openclaw_imessage": "iMessage",
    "openclaw_android": "Android Messages",
}
EVENT_TYPES = frozenset({"message_received", "message_sent"})
SIGNAL_SUMMARIES = {
    "schedule_change": "An approved personal scheduling change may affect availability.",
    "care_coordination": "A personal care coordination need may affect availability.",
    "practical_constraint": "A practical home or travel commitment may affect availability.",
    "support_needed": "A significant personal event may call for a calmer, supportive approach.",
    "urgent_reply": "A time-sensitive personal response may need attention.",
    "celebration": "A personal positive event is worth recognizing.",
}
RAW_MESSAGE_FIELDS = frozenset({
    "body", "text", "message", "message_body", "raw_message", "content",
    "summary", "attachments", "attachment", "media", "contact", "phone_number",
})
ALLOWED_SHAPE_KEYS = frozenset({
    "capacity", "timing", "approach", "decision_load", "availability",
    "celebration",
})
SHAPE_ENUMS = {
    "capacity": {"normal", "constrained", "protected"},
    "decision_load": {"normal", "reduced"},
    "availability": {"normal", "async_first", "unpredictable"},
    "timing": {"none", "today", "this_afternoon", "this_evening", "tomorrow_morning", "this_week"},
    "celebration": {"none", "positive", "milestone"},
}
ALLOWED_APPROACHES = {"standard", "calm", "concise", "supportive", "low_pressure"}
_EVENT_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,180}$")


def _string(value: Any, field: str, *, maximum: int, required: bool = False) -> str:
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise MessageConnectorError(f"{field} must be a string")
    cleaned = " ".join(value.split())
    if required and not cleaned:
        raise MessageConnectorError(f"{field} is required")
    if len(cleaned) > maximum:
        raise MessageConnectorError(f"{field} is too long")
    return cleaned


def normalize_connector_request(body: Any) -> dict[str, str]:
    if not isinstance(body, dict):
        raise MessageConnectorError("request body must be an object")
    provider = _string(body.get("provider"), "provider", maximum=64, required=True)
    if provider not in SUPPORTED_PROVIDERS:
        raise MessageConnectorError("unsupported message provider")
    label = _string(body.get("label"), "label", maximum=100)
    return {"provider": provider, "label": label or DEFAULT_PROVIDER_LABELS[provider]}


def _normalize_shape(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise MessageConnectorError("context_shape must be an object")
    unexpected = set(value) - ALLOWED_SHAPE_KEYS
    if unexpected:
        raise MessageConnectorError("context_shape contains unsupported fields")

    shape: dict[str, Any] = {}
    for key, allowed in SHAPE_ENUMS.items():
        if key not in value:
            continue
        normalized = _string(value[key], f"context_shape.{key}", maximum=40, required=True)
        if normalized not in allowed:
            raise MessageConnectorError(f"context_shape.{key} is invalid")
        shape[key] = normalized

    if "approach" in value:
        approach = value["approach"]
        if not isinstance(approach, list) or not 1 <= len(approach) <= 3:
            raise MessageConnectorError("context_shape.approach must contain one to three values")
        normalized_approach = [
            _string(item, "context_shape.approach", maximum=40, required=True)
            for item in approach
        ]
        if any(item not in ALLOWED_APPROACHES for item in normalized_approach):
            raise MessageConnectorError("context_shape.approach is invalid")
        shape["approach"] = sorted(set(normalized_approach))

    return shape


def normalize_message_event(body: Any) -> dict[str, Any]:
    if not isinstance(body, dict):
        raise MessageConnectorError("event body must be an object")
    raw_keys = RAW_MESSAGE_FIELDS & set(body)
    if raw_keys:
        raise MessageConnectorError("raw message data is not accepted")
    allowed_keys = {"source_event_id", "occurred_at", "event_type", "signal_type", "context_shape"}
    unexpected = set(body) - allowed_keys
    if unexpected:
        raise MessageConnectorError("event body contains unsupported fields")

    source_event_id = _string(body.get("source_event_id"), "source_event_id", maximum=180, required=True)
    if not _EVENT_ID_RE.fullmatch(source_event_id):
        raise MessageConnectorError("source_event_id contains unsupported characters")
    event_type = _string(body.get("event_type"), "event_type", maximum=64, required=True)
    if event_type not in EVENT_TYPES:
        raise MessageConnectorError("unsupported event_type")
    signal_type = _string(body.get("signal_type"), "signal_type", maximum=64, required=True)
    if signal_type not in SIGNAL_SUMMARIES:
        raise MessageConnectorError("unsupported signal_type")
    occurred_at = _string(body.get("occurred_at"), "occurred_at", maximum=40, required=True)
    try:
        parsed_time = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MessageConnectorError("occurred_at must be an ISO-8601 timestamp") from exc
    if parsed_time.tzinfo is None:
        raise MessageConnectorError("occurred_at must include a timezone")
    return {
        "source_event_id": source_event_id,
        "occurred_at": parsed_time.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event_type": event_type,
        # The source never supplies human-readable text. This closes the route
        # by which a raw message could be passed as a supposedly safe summary.
        "summary": SIGNAL_SUMMARIES[signal_type],
        "signal_type": signal_type,
        "context_shape": _normalize_shape(body.get("context_shape")),
    }


def hash_connector_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def new_connector_secret() -> str:
    return secrets.token_urlsafe(32)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_connector_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return browser-safe connector metadata without secret material."""
    return {
        "connector_id": str(record.get("connector_id") or ""),
        "provider": str(record.get("provider") or ""),
        "label": str(record.get("label") or ""),
        "status": str(record.get("status") or ""),
        "capabilities": list(record.get("capabilities") or []),
        "created_at": record.get("created_at"),
        "last_event_at": record.get("last_event_at"),
        "paused_at": record.get("paused_at"),
        "revoked_at": record.get("revoked_at"),
    }


class HoloChatMessageConnectorStore:
    """Persist connector state and normalized message events through Supabase."""

    def __init__(self, client: Any):
        self._client = client

    def list_for_scope(self, scope_id: str) -> list[dict[str, Any]]:
        rows = (
            self._client.table("holo_message_connectors")
            .select("connector_id, provider, label, status, capabilities, created_at, last_event_at, paused_at, revoked_at")
            .eq("scope_id", scope_id)
            .order("created_at", desc=True)
            .execute()
            .data
            or []
        )
        return [safe_connector_record(dict(row)) for row in rows]

    def create_pending(self, *, scope_id: str, capsule_id: str, provider: str, label: str) -> tuple[dict[str, Any], str]:
        existing = (
            self._client.table("holo_message_connectors")
            .select("connector_id")
            .eq("scope_id", scope_id)
            .eq("provider", provider)
            .in_("status", ["pending", "paired", "paused"])
            .limit(1)
            .execute()
            .data
            or []
        )
        if existing:
            raise MessageConnectorError(
                "A connector for this provider is already active in your Personal space. "
                "Pause or revoke it before pairing another."
            )

        secret = new_connector_secret()
        record = {
            "scope_id": scope_id,
            "capsule_id": capsule_id,
            "provider": provider,
            "label": label,
            "status": "pending",
            "capabilities": ["message_context_ingest"],
            "secret_prefix": secret[:12],
            "secret_hash": hash_connector_secret(secret),
        }
        rows = self._client.table("holo_message_connectors").insert(record).execute().data or []
        if not rows:
            raise RuntimeError("message connector could not be created")
        return safe_connector_record(dict(rows[0])), secret

    def pause(self, *, scope_id: str, connector_id: str) -> dict[str, Any] | None:
        rows = (
            self._client.table("holo_message_connectors")
            .update({"status": "paused", "paused_at": _now_iso()})
            .eq("scope_id", scope_id)
            .eq("connector_id", connector_id)
            .in_("status", ["pending", "paired"])
            .execute()
            .data
            or []
        )
        return safe_connector_record(dict(rows[0])) if rows else None

    def revoke(self, *, scope_id: str, connector_id: str) -> dict[str, Any] | None:
        rows = (
            self._client.table("holo_message_connectors")
            .update({"status": "revoked", "revoked_at": _now_iso()})
            .eq("scope_id", scope_id)
            .eq("connector_id", connector_id)
            .neq("status", "revoked")
            .execute()
            .data
            or []
        )
        return safe_connector_record(dict(rows[0])) if rows else None

    def ingest_event(self, *, connector_id: str, secret: str, event: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        rows = (
            self._client.table("holo_message_connectors")
            .select("connector_id, scope_id, capsule_id, provider, status, secret_hash")
            .eq("connector_id", connector_id)
            .limit(1)
            .execute()
            .data
            or []
        )
        if not rows:
            raise MessageConnectorAuthenticationError("connector is unavailable")
        connector = dict(rows[0])
        if connector.get("status") not in {"pending", "paired"}:
            raise MessageConnectorAuthenticationError("connector is not active")
        expected = str(connector.get("secret_hash") or "")
        if not expected or not hmac.compare_digest(expected, hash_connector_secret(secret)):
            raise MessageConnectorAuthenticationError("connector authentication failed")

        existing = (
            self._client.table("holo_message_context_events")
            .select("event_id")
            .eq("connector_id", connector_id)
            .eq("source_event_id", event["source_event_id"])
            .limit(1)
            .execute()
            .data
            or []
        )
        if existing:
            return {"event_id": str(existing[0].get("event_id") or ""), "status": "duplicate"}, True

        payload = {
            "connector_id": connector_id,
            "scope_id": connector["scope_id"],
            "capsule_id": connector.get("capsule_id"),
            "source_event_id": event["source_event_id"],
            "occurred_at": event["occurred_at"],
            "event_type": event["event_type"],
            "summary": event["summary"],
            "context_shape": event["context_shape"],
        }
        inserted = self._client.table("holo_message_context_events").insert(payload).execute().data or []
        if not inserted:
            raise RuntimeError("message context event could not be recorded")
        event_id = str(inserted[0].get("event_id") or "")
        self._client.table("holo_message_connectors").update({
            "status": "paired",
            "last_event_at": event["occurred_at"],
        }).eq("connector_id", connector_id).execute()
        return {"event_id": event_id, "status": "accepted"}, False
