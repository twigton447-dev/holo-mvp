"""
Shared fixtures and mock utilities for the Holo test suite.
"""
import os
import pytest

# ---------------------------------------------------------------------------
# Environment setup — must happen before importing app modules
# ---------------------------------------------------------------------------

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("GOOGLE_API_KEY", "test-google-key")
os.environ.setdefault("HOLO_API_KEY", "test-holo-key-secret")

# ---------------------------------------------------------------------------
# Minimal valid API payload (matches current main.py expectations)
# ---------------------------------------------------------------------------

MINIMAL_PAYLOAD = {
    "action": {
        "type": "invoice_payment",
        "amount_usd": 5000.00,
        "recipient_name": "Acme Supplies",
        "recipient_bank_account": "****1234",
        "invoice_number": "INV-001",
        "due_date": "2026-04-01",
    },
    "context": {
        "email_chain": [
            {
                "from": "billing@vendor.com",
                "to": "ap@acme.com",
                "subject": "Invoice INV-001",
                "body": "Please pay invoice INV-001 for $5,000.",
                "timestamp": "2026-03-15T10:00:00Z",
            }
        ]
    },
}

VALID_HEADERS = {"x-api-key": "test-holo-key-secret"}


# ---------------------------------------------------------------------------
# Mock TurnResult factory
# ---------------------------------------------------------------------------

from llm_adapters import TurnResult, BEC_CATEGORIES


def make_turn_result(
    verdict="ALLOW",
    turn_number=1,
    role="Initial Assessment",
    provider="mock",
    model_id="mock-model",
    severities=None,
):
    """Return a TurnResult with all categories set to the given severity (default LOW)."""
    sev = severities or {cat: "LOW" for cat in BEC_CATEGORIES}
    return TurnResult(
        provider=provider,
        model_id=model_id,
        role=role,
        turn_number=turn_number,
        verdict=verdict,
        reasoning="Mock reasoning for testing.",
        severity_flags=sev,
        findings=[],
        raw_response="{}",
        input_tokens=100,
        output_tokens=50,
    )


def make_escalate_result(turn_number=1, high_category="payment_routing"):
    """Return a TurnResult that escalates with one HIGH-severity flag."""
    sev = {cat: "LOW" for cat in BEC_CATEGORIES}
    sev[high_category] = "HIGH"
    return make_turn_result(
        verdict="ESCALATE",
        turn_number=turn_number,
        severities=sev,
    )


# ---------------------------------------------------------------------------
# MockAdapter
# ---------------------------------------------------------------------------

from llm_adapters import BaseAdapter


class MockAdapter(BaseAdapter):
    """Adapter that returns pre-canned TurnResults without any API call."""

    provider = "mock"
    model_id = "mock-model"

    def __init__(self, results):
        """
        results: list of TurnResult to return in order.
        If the list is exhausted, the last result is repeated.
        """
        self._results = list(results)
        self._call_count = 0

    def call(self, system: str, user: str):
        # Not used directly — run_turn is overridden
        raise NotImplementedError

    def run_turn(self, state, turn_number, role, temperature=0.2):
        idx = min(self._call_count, len(self._results) - 1)
        self._call_count += 1
        r = self._results[idx]
        # Patch turn_number/role so the state gets correct metadata
        from dataclasses import replace
        return replace(r, turn_number=turn_number, role=role)
