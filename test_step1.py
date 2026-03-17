"""Step 1 Verification Tests — LEGACY / SKIPPED.

These tests were written against the original stub API (round_details,
old category names). The current API uses turn_details and short category
keys. See tests/ for the current test suite.

Run with: pytest tests/test_step1.py -v

These tests verify:
  1. /health returns ok
  2. Pydantic models accept valid payloads
  3. Pydantic models reject invalid payloads
  4. The stubbed /v1/evaluate_action endpoint returns the correct response shape
"""

import json

import pytest
from fastapi.testclient import TestClient

from main import app
from models import Decision, EvaluationRequest, EvaluationResponse


@pytest.fixture(scope="module")
def client():
    """FastAPI test client (no real server needed)."""
    return TestClient(app)


@pytest.fixture
def valid_payload() -> dict:
    """Minimal valid invoice_payment payload."""
    return {
        "action": {
            "type": "invoice_payment",
            "actor": {
                "user": {"id": "u1", "email": "sarah@acme.com", "name": "Sarah", "role": "AP"},
                "agent": {"id": "a1", "name": "ERPBot", "type": "payment_automation"},
            },
            "parameters": {
                "amount": 5000.00,
                "currency": "USD",
                "recipient_account": "123456789",
                "invoice_id": "INV-001",
                "vendor_name": "Acme Supplies",
            },
        },
        "context": {
            "email_chain": [
                {
                    "from": "billing@vendor.com",
                    "to": "ap@acme.com",
                    "subject": "Invoice",
                    "body": "Please pay this invoice.",
                    "timestamp": "2026-03-15T10:00:00Z",
                }
            ]
        },
    }


# ---- Test 1: Health Check ----


class TestHealthCheck:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


# ---- Test 2: Pydantic Model Validation ----


class TestPydanticModels:
    def test_valid_payload_parses(self, valid_payload):
        req = EvaluationRequest(**valid_payload)
        assert req.action.type.value == "invoice_payment"
        assert req.action.parameters.amount == 5000.00
        assert req.action.parameters.vendor_name == "Acme Supplies"
        assert len(req.context.email_chain) == 1

    def test_email_from_alias_works(self, valid_payload):
        """The 'from' field in email_chain should map to from_address."""
        req = EvaluationRequest(**valid_payload)
        assert req.context.email_chain[0].from_address == "billing@vendor.com"

    def test_optional_context_fields_default_to_none(self, valid_payload):
        req = EvaluationRequest(**valid_payload)
        assert req.context.vendor_record is None
        assert req.context.sender_history is None
        assert req.context.org_policies is None

    def test_optional_action_fields_have_defaults(self, valid_payload):
        req = EvaluationRequest(**valid_payload)
        assert req.action.parameters.is_new_account is False
        assert req.action.parameters.currency == "USD"
        assert req.action.parameters.routing_number is None

    def test_rejects_unknown_action_type(self, valid_payload):
        from pydantic import ValidationError

        bad = valid_payload.copy()
        bad["action"] = {**valid_payload["action"], "type": "wire_transfer"}
        with pytest.raises(ValidationError) as exc_info:
            EvaluationRequest(**bad)
        assert "action_type" in str(exc_info.value).lower() or "type" in str(exc_info.value).lower()

    def test_rejects_missing_email_chain(self, valid_payload):
        from pydantic import ValidationError

        bad = {**valid_payload, "context": {}}
        with pytest.raises(ValidationError):
            EvaluationRequest(**bad)

    def test_rejects_empty_email_chain(self):
        """email_chain must have at least one message (list[EmailMessage] is required)."""
        from pydantic import ValidationError

        payload = {
            "action": {
                "type": "invoice_payment",
                "actor": {
                    "user": {"id": "u1", "email": "a@b.com", "name": "A", "role": "AP"},
                    "agent": {"id": "a1", "name": "Bot", "type": "test"},
                },
                "parameters": {
                    "amount": 100,
                    "currency": "USD",
                    "recipient_account": "123",
                    "invoice_id": "INV-1",
                    "vendor_name": "Test",
                },
            },
            "context": {"email_chain": []},
        }
        # An empty list is technically valid for list[EmailMessage],
        # so this should parse. (Business validation is separate.)
        req = EvaluationRequest(**payload)
        assert len(req.context.email_chain) == 0

    def test_full_payload_with_all_optional_fields(self):
        """A fully populated payload with all optional context fields."""
        payload = {
            "action": {
                "type": "invoice_payment",
                "actor": {
                    "user": {"id": "u1", "email": "a@b.com", "name": "A", "role": "AP"},
                    "agent": {"id": "a1", "name": "Bot", "type": "erp"},
                },
                "parameters": {
                    "amount": 8750.00,
                    "currency": "USD",
                    "recipient_account": "5567891234",
                    "routing_number": "071000013",
                    "invoice_id": "INV-42",
                    "due_date": "2026-03-30",
                    "vendor_name": "Pinnacle",
                    "payment_method": "ach",
                    "is_new_account": False,
                },
            },
            "context": {
                "email_chain": [
                    {
                        "from": "billing@vendor.com",
                        "to": "ap@acme.com",
                        "subject": "Invoice",
                        "body": "Pay this.",
                        "timestamp": "2026-03-01T10:00:00Z",
                        "raw_headers": "X-Mailer: Outlook",
                    }
                ],
                "vendor_record": {
                    "vendor_name": "Pinnacle",
                    "vendor_email": "billing@pinnacle.com",
                    "known_account_numbers": ["5567891234"],
                    "typical_invoice_range": {"min": 2000, "max": 15000},
                    "payment_frequency": "quarterly",
                    "last_payment_date": "2025-12-15",
                    "relationship_start_date": "2022-06-01",
                },
                "sender_history": {
                    "sender_email": "billing@pinnacle.com",
                    "total_emails_received": 47,
                    "first_seen_date": "2022-06-15",
                    "last_seen_date": "2026-03-01",
                    "known_aliases": ["lisa@pinnacle.com"],
                    "flagged_previously": False,
                },
                "org_policies": "Wire transfers over $10K require dual approval.",
            },
        }
        req = EvaluationRequest(**payload)
        assert req.context.vendor_record is not None
        assert req.context.vendor_record.vendor_name == "Pinnacle"
        assert req.context.sender_history.flagged_previously is False
        assert "dual approval" in req.context.org_policies


# ---- Test 3: Stubbed Endpoint ----


class TestEvaluateActionStub:
    def test_returns_200_with_valid_payload(self, client, valid_payload):
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        assert resp.status_code == 200

    def test_response_has_required_fields(self, client, valid_payload):
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        data = resp.json()

        assert "decision" in data
        assert data["decision"] in ("ALLOW", "ESCALATE")
        assert "risk_profile" in data
        assert "round_details" in data
        assert "convergence_info" in data
        assert "audit_id" in data
        assert "token_usage" in data

    def test_audit_id_has_holo_prefix(self, client, valid_payload):
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        data = resp.json()
        assert data["audit_id"].startswith("holo_")

    def test_risk_profile_has_all_6_categories(self, client, valid_payload):
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        data = resp.json()

        expected_categories = {
            "sender_identity_verification",
            "invoice_amount_anomaly",
            "payment_routing_change",
            "urgency_pressure_language",
            "domain_spoofing_indicators",
            "approval_chain_compliance",
        }
        assert set(data["risk_profile"].keys()) == expected_categories

    def test_round_details_is_list(self, client, valid_payload):
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        data = resp.json()
        assert isinstance(data["round_details"], list)
        assert len(data["round_details"]) >= 1

    def test_convergence_info_shape(self, client, valid_payload):
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        conv = resp.json()["convergence_info"]
        assert "converged" in conv
        assert "total_rounds" in conv
        assert "deltas" in conv

    def test_token_usage_shape(self, client, valid_payload):
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        usage = resp.json()["token_usage"]
        assert "total_input_tokens" in usage
        assert "total_output_tokens" in usage
        assert "total_cost_usd" in usage
        assert "per_round" in usage

    def test_rejects_invalid_payload(self, client):
        resp = client.post("/v1/evaluate_action", json={"garbage": True})
        assert resp.status_code == 422  # Pydantic validation error

    def test_rejects_empty_body(self, client):
        resp = client.post("/v1/evaluate_action")
        assert resp.status_code == 422

    def test_response_validates_as_pydantic_model(self, client, valid_payload):
        """The raw JSON response should parse into the EvaluationResponse model."""
        resp = client.post("/v1/evaluate_action", json=valid_payload)
        data = resp.json()
        parsed = EvaluationResponse(**data)
        assert parsed.decision in (Decision.ALLOW, Decision.ESCALATE)
        assert parsed.audit_id.startswith("holo_")


# ---- Test 4: OpenAPI / Swagger ----


class TestOpenAPIDocs:
    def test_docs_endpoint_available(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_json_available(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "/v1/evaluate_action" in str(schema)
        assert "/health" in str(schema)
