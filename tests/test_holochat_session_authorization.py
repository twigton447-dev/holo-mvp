from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import pytest

import chat_engine
import main
from chat_engine import ChatSession, HoloChatEngine, SessionOwnershipError
from holochat_scope import AccessContext, ScopeKind
from project_brain import ProjectBrain


class FakeBrain:
    def __init__(self, owners=None, last_session=None):
        self.owners = owners or {}
        self.last_session = last_session

    def get_chat_session(self, session_id):
        if session_id not in self.owners:
            return None
        return {"session_id": session_id, "capsule_id": self.owners[session_id]}

    def get_capsule_context(self, capsule_id):
        return {"last_session_id": self.last_session} if self.last_session else {}


class FakeChatEngine:
    def __init__(self):
        self.send_calls = []
        self.restore_calls = []
        self.clear_calls = []
        self.reject_send = False
        self.reject_restore = False
        self.error_to_raise = None

    def send_message(self, session_id, message, **kwargs):
        if self.error_to_raise is not None:
            raise self.error_to_raise
        if self.reject_send:
            raise SessionOwnershipError("memory-only owner mismatch")
        self.send_calls.append((session_id, message, kwargs))
        return {
            "session_id": session_id or "new-session",
            "response": "safe response",
            "turn_number": 1,
            "thread_health_score": 1.0,
            "thread_health_level": "GREEN",
            "elapsed_ms": 0,
            "tokens": {"input": 0, "output": 0},
        }

    def get_or_create_session(self, session_id, *, capsule_id=None, incognito=False):
        if self.reject_restore:
            raise SessionOwnershipError("memory-only owner mismatch")
        self.restore_calls.append(session_id)
        return type("Session", (), {"history": [{"role": "user", "content": "private history"}]})()

    def clear_session(self, session_id, *, capsule_id=None, incognito=False):
        self.clear_calls.append(session_id)
        return True


class FakeDatabase:
    def __init__(self, key_capsule_id=None):
        self.key_capsule_id = key_capsule_id

    def validate_api_key(self, raw_key):
        return {"max_requests_per_minute": 100}

    def get_capsule_id_for_key(self, raw_key):
        return self.key_capsule_id


def _client(monkeypatch, *, owner="capsule-a", jwt_capsule="capsule-a", key_capsule=None):
    engine = FakeChatEngine()
    monkeypatch.setattr(main, "_chat_engine", engine)
    monkeypatch.setattr(main, "_capsule_brain", FakeBrain({"victim-session": owner}, "victim-session"))
    monkeypatch.setattr(main, "_db", FakeDatabase(key_capsule))
    monkeypatch.setattr(
        main,
        "get_capsule_from_request",
        lambda header: {"sub": jwt_capsule} if jwt_capsule else None,
    )
    return TestClient(main.app), engine


def test_cross_capsule_chat_cannot_restore_or_reassign_session(monkeypatch):
    client, engine = _client(monkeypatch, owner="capsule-b")

    response = client.post(
        "/v1/chat",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "continue", "session_id": "victim-session"},
    )

    assert response.status_code == 404
    assert "private history" not in response.text
    assert engine.send_calls == []
    assert engine.restore_calls == []

    stream_response = client.post(
        "/v1/chat/stream",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "continue", "session_id": "victim-session"},
    )
    assert stream_response.status_code == 404
    assert engine.restore_calls == []

    incognito_response = client.post(
        "/v1/chat",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "continue", "session_id": "victim-session", "incognito": True},
    )
    assert incognito_response.status_code == 404
    assert engine.send_calls == []


def test_cross_capsule_history_summary_clear_and_delete_do_not_touch_session(monkeypatch):
    client, engine = _client(monkeypatch, owner="capsule-b")
    headers = {"x-api-key": "test-key", "Authorization": "Bearer capsule-a"}

    for method, path in (
        (client.get, "/v1/chat/victim-session/history"),
        (client.get, "/v1/chat/victim-session/summary"),
        (client.delete, "/v1/chat/victim-session"),
        (client.delete, "/v1/session/victim-session"),
        (client.get, "/v1/capsule/last-session"),
    ):
        response = method(path, headers=headers)
        assert response.status_code == 404
        assert "private history" not in response.text

    assert engine.restore_calls == []
    assert engine.clear_calls == []


def test_mismatched_jwt_and_api_key_principals_are_rejected_before_chat(monkeypatch):
    client, engine = _client(monkeypatch, key_capsule="capsule-b")

    response = client.post(
        "/v1/chat",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "new conversation"},
    )

    assert response.status_code == 403
    assert engine.send_calls == []


def test_engine_session_ownership_denial_becomes_a_non_disclosing_404(monkeypatch):
    client, engine = _client(monkeypatch)
    engine.reject_send = True

    response = client.post(
        "/v1/chat",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "continue", "session_id": "memory-only"},
    )

    assert response.status_code == 404
    assert "owner mismatch" not in response.text
    assert "DEBUG" not in response.text


def test_chat_failure_does_not_expose_internal_exception_text(monkeypatch):
    client, engine = _client(monkeypatch)
    engine.error_to_raise = RuntimeError("provider-secret-diagnostic")

    response = client.post(
        "/v1/chat",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "new conversation"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "HoloChat could not complete this turn."
    assert "provider-secret-diagnostic" not in response.text


def test_streaming_session_ownership_denial_is_an_http_404(monkeypatch):
    client, engine = _client(monkeypatch)
    engine.reject_restore = True

    response = client.post(
        "/v1/chat/stream",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "continue", "session_id": "memory-only", "incognito": True},
    )

    assert response.status_code == 404
    assert "owner mismatch" not in response.text


def test_summary_and_history_recheck_in_memory_session_ownership(monkeypatch):
    client, engine = _client(monkeypatch, owner="capsule-a")
    engine.reject_restore = True
    main._summary_cache.pop("victim-session", None)
    headers = {"x-api-key": "test-key", "Authorization": "Bearer capsule-a"}

    for path in (
        "/v1/chat/victim-session/history",
        "/v1/chat/victim-session/summary",
    ):
        response = client.get(path, headers=headers)
        assert response.status_code == 404
        assert "private history" not in response.text


def test_incognito_new_session_remains_unbound_to_a_capsule(monkeypatch):
    client, engine = _client(monkeypatch)

    response = client.post(
        "/v1/chat",
        headers={"x-api-key": "test-key", "Authorization": "Bearer capsule-a"},
        json={"message": "blind turn", "session_id": "incognito-session", "incognito": True},
    )

    assert response.status_code == 200
    assert engine.send_calls[0][2]["capsule_id"] is None
    assert engine.send_calls[0][2]["incognito"] is True


def test_persistence_refuses_to_reassign_an_existing_session_owner():
    brain = ProjectBrain.__new__(ProjectBrain)
    brain._client = MagicMock()
    brain.get_chat_session = lambda session_id: {
        "session_id": session_id,
        "capsule_id": "capsule-b",
    }

    brain.save_chat_turn(
        session_id="victim-session",
        turn_number=1,
        user_message="attempted takeover",
        holo_response="must not save",
        provider="test",
        temperature=0.0,
        capsule_id="capsule-a",
    )

    brain._client.table.assert_not_called()


def test_persistence_skips_incognito_or_anonymous_sessions():
    brain = ProjectBrain.__new__(ProjectBrain)
    brain._client = MagicMock()

    brain.save_chat_turn(
        session_id="incognito-session",
        turn_number=1,
        user_message="blind turn",
        holo_response="must stay transient",
        provider="test",
        temperature=0.0,
        capsule_id=None,
    )

    brain._client.table.assert_not_called()


class SessionBrain:
    def __init__(self, stored=None):
        self.stored = stored
        self.history_loads = []

    def get_chat_session(self, session_id):
        return self.stored

    def load_chat_history(self, session_id):
        self.history_loads.append(session_id)
        return [{"role": "user", "content": "private history"}]


def _session_engine(brain):
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._brain = brain
    engine._adapters = [object()]
    return engine


def test_in_memory_session_owner_blocks_cross_capsule_and_incognito_reuse():
    chat_engine._sessions.clear()
    engine = _session_engine(SessionBrain())
    engine.get_or_create_session("memory-only", capsule_id="capsule-a")

    with pytest.raises(AttributeError):
        chat_engine._sessions["memory-only"].owner_capsule_id = "capsule-b"

    with pytest.raises(SessionOwnershipError):
        engine.get_or_create_session("memory-only", capsule_id="capsule-b")
    with pytest.raises(SessionOwnershipError):
        engine.get_or_create_session("memory-only", capsule_id=None, incognito=True)
    with pytest.raises(SessionOwnershipError):
        engine.send_message("memory-only", "continue", capsule_id="capsule-b")
    with pytest.raises(SessionOwnershipError):
        next(engine.stream_message("memory-only", "continue", capsule_id="capsule-b"))


def test_durable_owner_is_checked_before_history_restore():
    chat_engine._sessions.clear()
    brain = SessionBrain({"session_id": "durable", "capsule_id": "capsule-b"})
    engine = _session_engine(brain)

    with pytest.raises(SessionOwnershipError):
        engine.get_or_create_session("durable", capsule_id="capsule-a")

    assert brain.history_loads == []


def test_hybrid_scope_is_server_resolved_and_passed_to_engine(monkeypatch, caplog):
    client, engine = _client(monkeypatch, owner="capsule-a")
    main._capsule_brain._client = object()
    main._capsule_brain.get_chat_session = lambda session_id: {
        "session_id": session_id,
        "capsule_id": "capsule-a",
        "scope_id": "work-a",
    }

    class Resolver:
        def __init__(self, db_client):
            assert db_client is main._capsule_brain._client

        def resolve(self, capsule_id, requested_scope_id=None):
            assert capsule_id == "capsule-a"
            assert requested_scope_id == "work-a"
            return AccessContext(
                "principal-a", "work-a", ScopeKind.ENTERPRISE,
                tenant_id="tenant-a", membership_id="member-a",
                workspace_id=None, roles=("member", "researcher"), authz_version=4,
            )

    monkeypatch.setattr(main, "HoloChatScopeStore", Resolver)
    monkeypatch.setenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", "1")
    caplog.set_level("INFO", logger="holo.main")

    response = client.post(
        "/v1/chat",
        headers={
            "x-api-key": "test-key",
            "Authorization": "Bearer capsule-a",
            "X-Holo-Scope-Id": "work-a",
        },
        json={"message": "continue", "session_id": "work-session"},
    )

    assert response.status_code == 200
    assert engine.send_calls[0][2]["scope_id"] == "work-a"
    assert engine.send_calls[0][2]["capsule_id"] == "capsule-a"
    assert "principal_id" not in response.json()
    assert "membership_id" not in response.json()
    assert any(
        getattr(record, "holochat_access", None) == {
            "principal_id": "principal-a",
            "scope_id": "work-a",
            "scope_kind": "enterprise",
            "tenant_id": "tenant-a",
            "workspace_id": None,
            "membership_id": "member-a",
            "roles": ["member", "researcher"],
            "authz_version": 4,
            "session_id": "work-session",
        }
        for record in caplog.records
    )


def test_scope_selection_is_rejected_until_hybrid_schema_is_enabled(monkeypatch):
    client, engine = _client(monkeypatch)
    monkeypatch.delenv("HOLOCHAT_HYBRID_SCOPES_ENABLED", raising=False)

    response = client.post(
        "/v1/chat",
        headers={
            "x-api-key": "test-key",
            "Authorization": "Bearer capsule-a",
            "X-Holo-Scope-Id": "work-a",
        },
        json={"message": "new conversation"},
    )

    assert response.status_code == 409
    assert engine.send_calls == []
