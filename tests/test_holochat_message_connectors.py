from fastapi.testclient import TestClient
from fastapi import HTTPException
from pathlib import Path
import json
import subprocess
import sys
import pytest

import main
from holochat_message_connectors import (
    MessageConnectorError,
    normalize_connector_request,
    normalize_message_event,
)
from holochat_scope import AccessContext, ScopeKind


def test_message_event_rejects_raw_message_fields():
    with pytest.raises(MessageConnectorError, match="raw message data"):
        normalize_message_event({
            "source_event_id": "imsg-1",
            "occurred_at": "2026-07-17T10:00:00Z",
            "event_type": "message_received",
            "signal_type": "care_coordination",
            "body": "The original private message must never be accepted here.",
        })


def test_message_event_accepts_only_bounded_context_shape():
    event = normalize_message_event({
        "source_event_id": "android-1",
        "occurred_at": "2026-07-17T10:00:00-07:00",
        "event_type": "message_received",
        "signal_type": "care_coordination",
        "context_shape": {
            "capacity": "constrained",
            "availability": "async_first",
            "approach": ["supportive", "concise"],
            "decision_load": "reduced",
            "timing": "today",
        },
    })

    assert event["occurred_at"] == "2026-07-17T17:00:00Z"
    assert event["context_shape"] == {
        "capacity": "constrained",
        "availability": "async_first",
        "approach": ["concise", "supportive"],
        "decision_load": "reduced",
        "timing": "today",
    }
    assert event["summary"] == "A personal care coordination need may affect availability."


def test_message_connector_request_is_limited_to_supported_phone_providers():
    assert normalize_connector_request({"provider": "openclaw_imessage"}) == {
        "provider": "openclaw_imessage",
        "label": "iMessage",
    }
    with pytest.raises(MessageConnectorError, match="unsupported"):
        normalize_connector_request({"provider": "gmail"})


class FakeConnectorStore:
    def __init__(self):
        self.created = []
        self.events = []

    def list_for_scope(self, scope_id):
        return [{
            "connector_id": "connector-1",
            "provider": "openclaw_imessage",
            "label": "Personal iPhone",
            "status": "pending",
            "capabilities": ["message_context_ingest"],
            "created_at": None,
            "last_event_at": None,
            "paused_at": None,
            "revoked_at": None,
        }]

    def create_pending(self, **kwargs):
        self.created.append(kwargs)
        return {
            **self.list_for_scope(kwargs["scope_id"])[0],
            "provider": kwargs["provider"],
            "label": kwargs["label"],
        }, "connector-secret"

    def pause(self, **kwargs):
        return self.list_for_scope(kwargs["scope_id"])[0]

    def revoke(self, **kwargs):
        return self.list_for_scope(kwargs["scope_id"])[0]

    def ingest_event(self, **kwargs):
        self.events.append(kwargs)
        return {"event_id": "event-1", "status": "accepted"}, False


def _client(monkeypatch):
    store = FakeConnectorStore()
    access = AccessContext(
        principal_id="principal-1",
        scope_id="personal-scope",
        scope_kind=ScopeKind.PERSONAL,
    )
    monkeypatch.setattr(main, "_message_connector_store", store)
    monkeypatch.setattr(main, "get_capsule_from_request", lambda _header: {"sub": "capsule-1"})
    monkeypatch.setattr(main, "_personal_message_access", lambda *_args, **_kwargs: access)
    return TestClient(main.app), store


def test_prepare_phone_connector_is_personal_and_returns_one_time_secret(monkeypatch):
    client, store = _client(monkeypatch)

    response = client.post(
        "/v1/capsule/message-connectors",
        headers={"Authorization": "Bearer capsule-1"},
        json={"provider": "openclaw_android", "label": "My Android"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["connector"]["provider"] == "openclaw_android"
    assert payload["ingest"]["connector_secret"] == "connector-secret"
    assert payload["ingest"]["raw_messages_accepted"] is False
    assert store.created == [{
        "scope_id": "personal-scope",
        "capsule_id": "capsule-1",
        "provider": "openclaw_android",
        "label": "My Android",
    }]


def test_personal_message_access_rejects_enterprise_scope(monkeypatch):
    enterprise_access = AccessContext(
        principal_id="principal-1",
        scope_id="enterprise-scope",
        scope_kind=ScopeKind.ENTERPRISE,
        tenant_id="tenant-1",
        membership_id="membership-1",
    )
    monkeypatch.setattr(main, "_hybrid_scopes_enabled", lambda: True)
    monkeypatch.setattr(main, "_resolve_active_scope", lambda *_args, **_kwargs: enterprise_access)

    with pytest.raises(HTTPException) as exc_info:
        main._personal_message_access(object(), "capsule-1")

    assert exc_info.value.status_code == 403


def test_message_ingress_records_normalized_context_not_raw_message_text(monkeypatch):
    client, store = _client(monkeypatch)

    response = client.post(
        "/v1/connectors/messages/events",
        headers={
            "X-Holo-Connector-Id": "connector-1",
            "X-Holo-Connector-Secret": "connector-secret",
        },
        json={
            "source_event_id": "event-42",
            "occurred_at": "2026-07-17T10:00:00Z",
            "event_type": "message_received",
            "signal_type": "support_needed",
            "context_shape": {"approach": ["calm", "supportive"]},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "event_id": "event-1",
        "status": "accepted",
        "duplicate": False,
        "raw_messages_accepted": False,
    }
    assert store.events[0]["event"]["summary"] == "A significant personal event may call for a calmer, supportive approach."
    assert "body" not in store.events[0]["event"]


def test_message_ingress_rejects_raw_message_body_before_store_access(monkeypatch):
    client, store = _client(monkeypatch)

    response = client.post(
        "/v1/connectors/messages/events",
        headers={
            "X-Holo-Connector-Id": "connector-1",
            "X-Holo-Connector-Secret": "connector-secret",
        },
        json={
            "source_event_id": "event-42",
            "occurred_at": "2026-07-17T10:00:00Z",
            "event_type": "message_received",
            "signal_type": "support_needed",
            "message": "Do not store me.",
        },
    )

    assert response.status_code == 400
    assert store.events == []


def test_local_message_bridge_dry_run_refuses_raw_message_content():
    bridge = Path(__file__).parents[1] / "scripts" / "holochat_message_context_bridge.py"
    allowed = subprocess.run(
        [sys.executable, str(bridge), "--dry-run"],
        input=json.dumps({
            "source_event_id": "event-43",
            "occurred_at": "2026-07-17T10:00:00Z",
            "event_type": "message_received",
            "signal_type": "practical_constraint",
        }),
        capture_output=True,
        text=True,
        check=False,
    )
    blocked = subprocess.run(
        [sys.executable, str(bridge), "--dry-run"],
        input=json.dumps({
            "source_event_id": "event-44",
            "occurred_at": "2026-07-17T10:00:00Z",
            "event_type": "message_received",
            "signal_type": "practical_constraint",
            "body": "Private message text",
        }),
        capture_output=True,
        text=True,
        check=False,
    )

    assert allowed.returncode == 0
    assert '"raw_messages_accepted": false' in allowed.stdout
    assert "personal time constraint" not in allowed.stdout
    assert blocked.returncode == 2
    assert "raw message data" in blocked.stderr


def test_chat_exposes_a_personal_only_message_connection_consent_surface():
    chat = (Path(__file__).parents[1] / "frontend" / "chat.html").read_text()

    assert 'id="rail-connect-messages"' in chat
    assert 'onclick="openMessageConnectorDialog()"' in chat
    assert 'id="message-connector-dialog"' in chat
    assert "Authorize a device, not a phone number." in chat
    assert "body.holo-space-enterprise #rail-connect-messages { display: none; }" in chat
    assert 'fetch("/v1/capsule/message-connectors"' in chat
    assert "derived context only" in chat
