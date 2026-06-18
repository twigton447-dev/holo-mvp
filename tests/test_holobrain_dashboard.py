from pathlib import Path

from fastapi.testclient import TestClient

import main


class FakeBrain:
    _client = None

    def get_capsule(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return {
            "capsule_id": capsule_id,
            "email": "taylor@example.com",
            "name": "Taylor",
            "mode": "personal",
            "created_at": "2026-06-01T00:00:00Z",
            "last_active": "2026-06-17T00:00:00Z",
        }

    def get_capsule_context(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return {
            "_password_hash": "do-not-return-this",
            "project": "HoloChat",
            "api_token_note": "do-not-return-either",
        }

    def load_life_context(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return [{"category": "work", "key": "focus", "value": "Build Holo", "confidence": 0.9}]

    def list_sessions(self, capsule_id, limit=40):
        assert capsule_id == "canonical-capsule"
        return [{
            "session_id": "session-1234567890",
            "created_at": "2026-06-16T00:00:00Z",
            "last_active": "2026-06-17T00:00:00Z",
            "turn_count": 3,
            "title": "Memory repair",
            "preview": "Memory repair",
        }]

    def load_last_consolidation(self, capsule_id):
        assert capsule_id == "canonical-capsule"
        return {
            "session_id": "session-1234567890",
            "created_at": "2026-06-17T00:00:00Z",
            "what_changed": "Memory link verified",
            "what_surfaced": "",
            "open_threads": [],
            "captain_note": "Continue carefully",
        }

    def list_artifacts(self, capsule_id, limit=50):
        assert capsule_id == "canonical-capsule"
        return [{"artifact_id": "artifact-1", "title": "Plan", "artifact_type": "html"}]


def test_holobrain_endpoint_requires_auth(monkeypatch):
    monkeypatch.setattr(main, "get_capsule_from_request", lambda header: None)
    client = TestClient(main.app)

    response = client.get("/v1/holo-brain")

    assert response.status_code == 401


def test_holobrain_endpoint_uses_token_capsule_and_redacts_sensitive_context(monkeypatch):
    monkeypatch.setattr(main, "_capsule_brain", FakeBrain())
    monkeypatch.setattr(
        main,
        "get_capsule_from_request",
        lambda header: {"sub": "canonical-capsule", "email": "alias@example.com", "mode": "personal"},
    )
    client = TestClient(main.app)

    response = client.get("/v1/holo-brain", headers={"Authorization": "Bearer test"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["capsule"]["id"] == "canonical-capsule"
    assert payload["capsule"]["email_masked"] == "t***r@example.com"
    assert payload["capsule_context"]["count"] == 3
    assert payload["capsule_context"]["redacted_count"] == 2
    assert payload["life_context"]["count"] == 1
    assert payload["sessions"]["count"] == 1
    assert payload["consolidations"]["count"] == 1
    assert payload["artifacts"]["count"] == 1
    assert "do-not-return-this" not in str(payload)
    assert "do-not-return-either" not in str(payload)


def test_frontend_has_holobrain_button_and_render_path():
    html = Path("frontend/chat.html").read_text()

    assert 'id="holobrain-toggle"' in html
    assert 'title="Open engine data"' in html
    assert ">Engine data</button>" in html
    assert 'id="holobrain-panel"' in html
    assert "Engine runtime" in html
    assert 'fetch("/v1/holo-brain"' in html
    assert "renderHoloBrain(data)" in html
    assert "buildRuntimeRows(_latestRuntimeData)" in html
    assert "Refresh engine data" in html
    assert "Attached capsule" not in html
    assert "capsule.id_short" not in html


def test_frontend_holobrain_hides_capsule_context_rows_by_default():
    html = Path("frontend/chat.html").read_text()

    assert "Memory details hidden by default" in html
    assert "Context counts stay visible without showing stored rows." in html
    assert "const contextRows = brainRows(ctx.entries" not in html
    assert 'brainSection("Saved memory", `${ctx.count || 0} rows`, contextRows, true)' not in html
    assert 'brainSection("Life context", `${life.count || 0} rows`, lifeRows, true)' not in html
