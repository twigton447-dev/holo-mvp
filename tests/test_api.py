"""
Functional/integration tests for main.py — API endpoints with the
ContextGovernor mocked so no real LLM calls are made.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from tests.conftest import (
    MINIMAL_PAYLOAD,
    VALID_HEADERS,
    MockAdapter,
    make_turn_result,
    make_escalate_result,
)
from llm_adapters import BEC_CATEGORIES
from holo_release import APP_VERSION, ARCHITECTURE_VERSION


# ---------------------------------------------------------------------------
# App fixture — patches load_adapters so the governor uses MockAdapters
# ---------------------------------------------------------------------------

def _make_mock_adapters(results):
    adapter = MockAdapter(results)
    return [adapter, adapter, adapter]


@pytest.fixture
def allow_client():
    """Client wired to return 3x ALLOW / all-LOW turns."""
    results = [make_turn_result(verdict="ALLOW", turn_number=i) for i in range(1, 4)]
    with patch("context_governor.load_adapters", return_value=(_make_mock_adapters(results), [])):
        from main import app
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


@pytest.fixture
def escalate_client():
    """Client wired to escalate on turn 1 with a HIGH payment_routing flag."""
    results = [
        make_escalate_result(turn_number=1, high_category="payment_routing"),
        make_turn_result(verdict="ESCALATE", turn_number=2),
        make_turn_result(verdict="ESCALATE", turn_number=3),
    ]
    with patch("context_governor.load_adapters", return_value=(_make_mock_adapters(results), [])):
        from main import app
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth:

    def test_health_returns_200(self, allow_client):
        resp = allow_client.get("/health")
        assert resp.status_code == 200

    def test_health_status_ok(self, allow_client):
        data = allow_client.get("/health").json()
        assert data["status"] == "ok"

    def test_health_version(self, allow_client):
        data = allow_client.get("/health").json()
        assert data["version"] == APP_VERSION
        assert data["release"]["app_version"] == APP_VERSION
        assert data["release"]["architecture_version"] == ARCHITECTURE_VERSION

    def test_version_endpoint_reports_release_identity(self, allow_client):
        data = allow_client.get("/version").json()
        assert data["app_version"] == APP_VERSION
        assert data["architecture_version"] == ARCHITECTURE_VERSION
        assert data["build_label"].startswith(APP_VERSION)

    def test_runtime_status_reports_safe_live_roster(self, allow_client):
        data = allow_client.get("/runtime-status").json()
        assert data["release"]["app_version"] == APP_VERSION
        assert data["truth_contract"]["raw_prompts_exposed"] is False
        assert data["truth_contract"]["api_keys_exposed"] is False
        holochat = data["holochat"]
        assert holochat["visible_chat_lane"]["gov_can_choose_models"] is False
        assert holochat["visible_chat_lane"]["model_selection"] == "fixed_manifest_order"
        assert holochat["governed_shadow_lane"]["gov_can_choose_models"] is False
        assert holochat["governed_shadow_lane"]["visible_answer_replaced"] is False
        assert holochat["visible_chat_lane"]["analyst_rotation_order"]

    def test_runtime_page_available(self, allow_client):
        resp = allow_client.get("/runtime")
        assert resp.status_code == 200
        html = resp.text
        assert "HoloChat Runtime" in html
        assert "/runtime-status" in html
        assert "Raw prompts exposed" in html
        assert "API keys exposed" in html
        assert "bearer " not in html.lower()
        assert "secret-value" not in html.lower()

    def test_health_engine_live(self, allow_client):
        data = allow_client.get("/health").json()
        assert data["engine"] == "LIVE"

    def test_health_no_auth_required(self, allow_client):
        """Health endpoint must be publicly accessible — no API key needed."""
        resp = allow_client.get("/health")  # no headers
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# /v1/evaluate_action — Authentication
# ---------------------------------------------------------------------------

class TestAuthentication:

    def test_missing_api_key_returns_401(self, allow_client):
        resp = allow_client.post("/v1/evaluate_action", json=MINIMAL_PAYLOAD)
        assert resp.status_code == 401

    def test_wrong_api_key_returns_401(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers={"x-api-key": "wrong-key"},
        )
        assert resp.status_code == 401

    def test_valid_api_key_returns_200(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers=VALID_HEADERS,
        )
        assert resp.status_code == 200

    def test_valid_env_key_survives_db_validation_error(self, allow_client, monkeypatch):
        import main

        class BrokenDB:
            def validate_api_key(self, _raw_key):
                raise RuntimeError("db unavailable")

            def log_api_usage(self, _row):
                raise RuntimeError("db unavailable")

        monkeypatch.setattr(main, "_db", BrokenDB())
        monkeypatch.setenv("HOLO_MAX_RPM", "60")
        main._rate_limiter._requests.clear()

        resp = allow_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers=VALID_HEADERS,
        )

        assert resp.status_code == 200

    def test_invalid_holo_max_rpm_falls_back_to_default(self, allow_client, monkeypatch):
        import main

        monkeypatch.setattr(main, "_db", None)
        monkeypatch.setenv("HOLO_MAX_RPM", "# Optional: requests-per-minute cap")
        main._rate_limiter._requests.clear()

        resp = allow_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers=VALID_HEADERS,
        )

        assert resp.status_code == 200

    def test_401_detail_does_not_leak_expected_key(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers={"x-api-key": "wrong"},
        )
        body = resp.text
        assert "test-holo-key-secret" not in body


# ---------------------------------------------------------------------------
# /v1/evaluate_action — Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:

    def test_missing_action_field_returns_400(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            json={"context": {"email_chain": []}},
            headers=VALID_HEADERS,
        )
        assert resp.status_code == 400

    def test_missing_email_chain_returns_400(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            json={"action": {"type": "invoice_payment"}, "context": {}},
            headers=VALID_HEADERS,
        )
        assert resp.status_code == 400

    def test_invalid_json_body_returns_400(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            content="not-json",
            headers={**VALID_HEADERS, "Content-Type": "application/json"},
        )
        assert resp.status_code == 400

    def test_empty_body_returns_400(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            json={},
            headers=VALID_HEADERS,
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /v1/evaluate_action — Response shape (ALLOW path)
# ---------------------------------------------------------------------------

class TestResponseShape:

    @pytest.fixture(autouse=True)
    def _response(self, allow_client):
        resp = allow_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers=VALID_HEADERS,
        )
        assert resp.status_code == 200
        self.data = resp.json()

    def test_audit_id_has_holo_prefix(self):
        assert self.data["audit_id"].startswith("holo_")

    def test_decision_is_allow_or_escalate(self):
        assert self.data["decision"] in ("ALLOW", "ESCALATE")

    def test_decision_reason_is_string(self):
        assert isinstance(self.data["decision_reason"], str)
        assert len(self.data["decision_reason"]) > 0

    def test_convergence_info_present(self):
        conv = self.data["convergence_info"]
        assert "converged" in conv
        assert "turns_completed" in conv
        assert "partial" in conv
        assert "deltas" in conv
        assert "elapsed_ms" in conv

    def test_risk_profile_has_all_six_categories(self):
        profile = self.data["risk_profile"]
        assert set(BEC_CATEGORIES).issubset(set(profile.keys()))

    def test_risk_profile_category_shape(self):
        for cat, info in self.data["risk_profile"].items():
            assert "label" in info
            assert "severity" in info
            assert "assessed" in info
            assert info["severity"] in ("NONE", "LOW", "MEDIUM", "HIGH")

    def test_turn_details_is_list(self):
        assert isinstance(self.data["turn_details"], list)

    def test_turn_details_not_empty(self):
        assert len(self.data["turn_details"]) >= 1

    def test_token_usage_present(self):
        usage = self.data["token_usage"]
        assert "total" in usage
        assert "input" in usage["total"]
        assert "output" in usage["total"]

    def test_allow_decision_on_clean_payload(self):
        assert self.data["decision"] == "ALLOW"


# ---------------------------------------------------------------------------
# /v1/evaluate_action — ESCALATE path
# ---------------------------------------------------------------------------

class TestEscalatePath:

    def test_high_severity_produces_escalate(self, escalate_client):
        resp = escalate_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers=VALID_HEADERS,
        )
        assert resp.status_code == 200
        assert resp.json()["decision"] == "ESCALATE"

    def test_escalate_risk_profile_has_high(self, escalate_client):
        resp = escalate_client.post(
            "/v1/evaluate_action",
            json=MINIMAL_PAYLOAD,
            headers=VALID_HEADERS,
        )
        profile = resp.json()["risk_profile"]
        severities = {info["severity"] for info in profile.values()}
        assert "HIGH" in severities

    def test_500_error_does_not_leak_internals(self, allow_client):
        """When the governor crashes, the 500 response must not include the exception message."""
        with patch("main._governor") as mock_gov:
            mock_gov.evaluate.side_effect = RuntimeError("secret internal details xyz")
            resp = allow_client.post(
                "/v1/evaluate_action",
                json=MINIMAL_PAYLOAD,
                headers=VALID_HEADERS,
            )
        assert resp.status_code == 500
        assert "secret internal details xyz" not in resp.text


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class TestRateLimiting:

    def test_rate_limit_fires_after_max_rpm(self, allow_client):
        """After exceeding HOLO_MAX_RPM requests, the API should return 429."""
        with patch.dict(os.environ, {"HOLO_MAX_RPM": "3"}):
            # Reset rate limiter state
            import main
            main._rate_limiter._requests.clear()

            responses = []
            for _ in range(5):
                r = allow_client.post(
                    "/v1/evaluate_action",
                    json=MINIMAL_PAYLOAD,
                    headers=VALID_HEADERS,
                )
                responses.append(r.status_code)

        # At least one request should have been rate-limited
        assert 429 in responses

    def test_rate_limit_resets_after_window(self):
        """Expired entries are pruned, so old traffic doesn't block new requests."""
        import time
        from auth import RateLimiter
        rl = RateLimiter()
        # Fill the window with timestamps older than 60s
        rl._requests["key"] = [time.time() - 61] * 5
        assert rl.check("key", max_rpm=5) is True
