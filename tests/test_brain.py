"""
Tests for project_brain.py — the Holo persistent memory layer.

Unit tests use a fully mocked Supabase client (no network calls).
Integration tests run only when SUPABASE_URL + SUPABASE_KEY are set in the
environment.  To run them:

    SUPABASE_URL=https://... SUPABASE_KEY=... pytest tests/test_brain.py -v -m integration
"""
import os
import uuid
import pytest
from copy import deepcopy
from unittest.mock import MagicMock, patch, call

from project_brain import ProjectBrain, VENDOR_EVAL_LIMIT, VENDOR_FINDING_LIMIT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TEST_VENDOR_DOMAIN = "acme-vendor.com"
TEST_VENDOR_EMAIL  = f"billing@{TEST_VENDOR_DOMAIN}"


def _make_result(
    decision="ALLOW",
    high_categories=None,
    medium_categories=None,
    findings=None,
):
    """Minimal evaluation result dict that ProjectBrain.save_evaluation expects."""
    eval_id = f"holo_{uuid.uuid4().hex[:12]}"
    high_cats = high_categories or []
    med_cats  = medium_categories or []

    # Build a fake coverage_matrix from the category lists
    coverage = {}
    for cat in high_cats:
        coverage[cat] = {"addressed": True, "max_severity": "HIGH"}
    for cat in med_cats:
        if cat not in coverage:
            coverage[cat] = {"addressed": True, "max_severity": "MEDIUM"}

    turn_history = [
        {
            "turn_number": 1,
            "provider":    "openai",
            "role":        "Initial Assessment",
            "verdict":     decision,
            "findings":    findings or [],
        }
    ]

    return {
        "evaluation_id":   eval_id,
        "decision":        decision,
        "exit_reason":     "converged",
        "turns_completed": len(turn_history),
        "elapsed_ms":      1234,
        "converged":       True,
        "oscillation":     False,
        "decay":           False,
        "decision_reason": "No anomalies detected.",
        "coverage_matrix": coverage,
        "turn_history":    turn_history,
    }


def _make_request(vendor_email=TEST_VENDOR_EMAIL):
    return {
        "action":  {"type": "invoice_payment", "amount_usd": 5000},
        "context": {
            "vendor_record": {
                "vendor_name":  "Acme Supplies",
                "vendor_email": vendor_email,
            },
            "email_chain": [],
        },
    }


def _make_profile(
    domain=TEST_VENDOR_DOMAIN,
    total=1,
    allow_cnt=1,
    esc_cnt=0,
    highest="LOW",
):
    return {
        "vendor_domain":      domain,
        "vendor_name":        "Acme Supplies",
        "first_seen":         "2026-03-01T00:00:00+00:00",
        "last_seen":          "2026-03-17T00:00:00+00:00",
        "total_evaluations":  total,
        "allow_count":        allow_cnt,
        "escalate_count":     esc_cnt,
        "highest_risk_seen":  highest,
        "last_decision":      "ALLOW",
        "last_exit_reason":   "converged",
        "last_brief":         "ALLOW (converged) after 3 turns.",
    }


def _make_eval_row():
    return {
        "evaluation_id":   "holo_abc000",
        "created_at":      "2026-03-15T10:00:00+00:00",
        "decision":        "ALLOW",
        "exit_reason":     "converged",
        "turns_completed": 3,
        "evaluation_brief": "ALLOW (converged) after 3 turns.",
        "high_categories": [],
        "oscillation":     False,
        "decay":           False,
    }


# ---------------------------------------------------------------------------
# Fixture: brain with fully mocked Supabase client
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_client():
    """Return a MagicMock that satisfies the fluent query-builder pattern."""
    client = MagicMock()
    # Make every chained method return the same mock so chains work
    for method in ("table", "select", "eq", "order", "limit", "single",
                   "insert", "update", "upsert"):
        getattr(client, method).return_value = client
    return client


@pytest.fixture
def brain(mock_client):
    """ProjectBrain with a pre-wired mock client (no Supabase connection needed)."""
    b = ProjectBrain.__new__(ProjectBrain)
    b._client = mock_client
    return b


# ---------------------------------------------------------------------------
# _extract_vendor_domain
# ---------------------------------------------------------------------------

class TestExtractVendorDomain:

    def test_extracts_domain_from_email(self, brain):
        ctx = {"vendor_record": {"vendor_email": "alice@vendor.co"}}
        assert brain._extract_vendor_domain(ctx) == "vendor.co"

    def test_lowercases_domain(self, brain):
        ctx = {"vendor_record": {"vendor_email": "bob@UPPER.COM"}}
        assert brain._extract_vendor_domain(ctx) == "upper.com"

    def test_missing_email_returns_none(self, brain):
        assert brain._extract_vendor_domain({}) is None

    def test_no_at_sign_returns_none(self, brain):
        ctx = {"vendor_record": {"vendor_email": "not-an-email"}}
        assert brain._extract_vendor_domain(ctx) is None

    def test_empty_string_returns_none(self, brain):
        ctx = {"vendor_record": {"vendor_email": ""}}
        assert brain._extract_vendor_domain(ctx) is None


# ---------------------------------------------------------------------------
# retrieve_context — no-client path
# ---------------------------------------------------------------------------

class TestRetrieveContextNoClient:

    def test_returns_none_when_no_client(self):
        b = ProjectBrain.__new__(ProjectBrain)
        b._client = None
        result = b.retrieve_context({}, _make_request()["context"])
        assert result is None

    def test_returns_none_when_no_vendor_domain(self, brain):
        result = brain.retrieve_context({}, {})
        assert result is None


# ---------------------------------------------------------------------------
# retrieve_context — first-time vendor (no prior profile)
# ---------------------------------------------------------------------------

class TestRetrieveContextFirstTime:

    def test_returns_none_for_new_vendor(self, brain, mock_client):
        # single() returns None → no prior profile
        mock_client.execute.return_value = MagicMock(data=None)
        result = brain.retrieve_context({}, _make_request()["context"])
        assert result is None


# ---------------------------------------------------------------------------
# retrieve_context — known vendor with history
# ---------------------------------------------------------------------------

class TestRetrieveContextKnownVendor:

    def _setup_execute(self, mock_client, profile, evals, findings):
        """Wire mock_client.execute to return profile → evals → findings in order."""
        mock_client.execute.side_effect = [
            MagicMock(data=profile),
            MagicMock(data=evals),
            MagicMock(data=findings),
        ]

    def test_returns_dict_with_expected_keys(self, brain, mock_client):
        profile  = _make_profile()
        evals    = [_make_eval_row()]
        findings = []
        self._setup_execute(mock_client, profile, evals, findings)

        result = brain.retrieve_context({}, _make_request()["context"])

        assert result is not None
        for key in (
            "vendor_domain", "vendor_name", "first_seen", "last_seen",
            "total_evaluations", "allow_count", "escalate_count",
            "highest_risk_seen", "last_decision", "last_brief",
            "recent_evaluations", "prior_high_findings", "context_note",
        ):
            assert key in result, f"missing key: {key}"

    def test_vendor_domain_matches(self, brain, mock_client):
        profile = _make_profile()
        self._setup_execute(mock_client, profile, [], [])
        result = brain.retrieve_context({}, _make_request()["context"])
        assert result["vendor_domain"] == TEST_VENDOR_DOMAIN

    def test_counters_populated(self, brain, mock_client):
        profile = _make_profile(total=5, allow_cnt=4, esc_cnt=1, highest="MEDIUM")
        self._setup_execute(mock_client, profile, [], [])
        result = brain.retrieve_context({}, _make_request()["context"])
        assert result["total_evaluations"] == 5
        assert result["allow_count"] == 4
        assert result["escalate_count"] == 1
        assert result["highest_risk_seen"] == "MEDIUM"

    def test_recent_evaluations_mapped(self, brain, mock_client):
        profile  = _make_profile()
        evals    = [_make_eval_row()]
        self._setup_execute(mock_client, profile, evals, [])
        result = brain.retrieve_context({}, _make_request()["context"])
        assert len(result["recent_evaluations"]) == 1
        e = result["recent_evaluations"][0]
        assert e["decision"] == "ALLOW"
        assert e["evaluation_id"] == "holo_abc000"

    def test_context_note_warns_about_prior_allow(self, brain, mock_client):
        profile = _make_profile()
        self._setup_execute(mock_client, profile, [], [])
        result = brain.retrieve_context({}, _make_request()["context"])
        assert "prior ALLOW does NOT immunize" in result["context_note"]

    def test_date_truncated_to_10_chars(self, brain, mock_client):
        profile = _make_profile()
        self._setup_execute(mock_client, profile, [_make_eval_row()], [])
        result = brain.retrieve_context({}, _make_request()["context"])
        assert len(result["first_seen"]) == 10
        assert len(result["last_seen"])  == 10

    def test_exception_returns_none(self, brain, mock_client):
        mock_client.execute.side_effect = Exception("network error")
        result = brain.retrieve_context({}, _make_request()["context"])
        assert result is None


# ---------------------------------------------------------------------------
# save_evaluation — write order and table calls
# ---------------------------------------------------------------------------

class TestSaveEvaluation:

    def test_no_op_when_no_client(self):
        b = ProjectBrain.__new__(ProjectBrain)
        b._client = None
        # Should not raise
        b.save_evaluation(_make_result(), _make_request())

    def test_inserts_evaluation_record(self, brain, mock_client):
        mock_client.execute.return_value = MagicMock(data={"total_evaluations": 0,
                                                            "allow_count": 0,
                                                            "escalate_count": 0,
                                                            "highest_risk_seen": "NONE",
                                                            "first_seen": None})
        result  = _make_result(decision="ALLOW")
        request = _make_request()
        brain.save_evaluation(result, request)

        # Check holo_evaluations insert was called
        insert_calls = [
            c for c in mock_client.table.call_args_list
            if c.args[0] == "holo_evaluations"
        ]
        assert len(insert_calls) >= 1

    def test_upserts_vendor_profile(self, brain, mock_client):
        mock_client.execute.return_value = MagicMock(data={"total_evaluations": 0,
                                                            "allow_count": 0,
                                                            "escalate_count": 0,
                                                            "highest_risk_seen": "NONE",
                                                            "first_seen": None})
        brain.save_evaluation(_make_result(), _make_request())
        profile_calls = [
            c for c in mock_client.table.call_args_list
            if c.args[0] == "holo_vendor_profiles"
        ]
        assert len(profile_calls) >= 1

    def test_inserts_high_findings(self, brain, mock_client):
        mock_client.execute.return_value = MagicMock(data={"total_evaluations": 0,
                                                            "allow_count": 0,
                                                            "escalate_count": 0,
                                                            "highest_risk_seen": "NONE",
                                                            "first_seen": None})
        finding = {
            "category":  "payment_routing",
            "severity":  "HIGH",
            "fact_type": "SUBMITTED_DATA",
            "evidence":  "Bank account changed 2 days ago.",
            "detail":    "New account registered offshore.",
        }
        result  = _make_result(decision="ESCALATE", high_categories=["payment_routing"],
                                findings=[finding])
        request = _make_request()
        brain.save_evaluation(result, request)

        findings_calls = [
            c for c in mock_client.table.call_args_list
            if c.args[0] == "holo_findings"
        ]
        assert len(findings_calls) >= 1

    def test_no_findings_insert_when_all_low(self, brain, mock_client):
        """If there are no HIGH/MEDIUM findings, holo_findings should not be touched."""
        mock_client.execute.return_value = MagicMock(data={"total_evaluations": 0,
                                                            "allow_count": 0,
                                                            "escalate_count": 0,
                                                            "highest_risk_seen": "NONE",
                                                            "first_seen": None})
        result  = _make_result(decision="ALLOW", findings=[])   # no findings in turns
        request = _make_request()
        brain.save_evaluation(result, request)

        findings_calls = [
            c for c in mock_client.table.call_args_list
            if c.args[0] == "holo_findings"
        ]
        assert len(findings_calls) == 0

    def test_exception_does_not_propagate(self, brain, mock_client):
        mock_client.execute.side_effect = Exception("DB unavailable")
        # Should silently swallow the error
        brain.save_evaluation(_make_result(), _make_request())


# ---------------------------------------------------------------------------
# Vendor counter logic
# ---------------------------------------------------------------------------

class TestUpsertVendorProfile:

    def _setup_profile(self, mock_client, current):
        """First execute = upsert response, second = select for counter fetch."""
        mock_client.execute.side_effect = [
            MagicMock(data=None),    # upsert call
            MagicMock(data=current), # select for counters
            MagicMock(data=None),    # update call
        ]

    def test_allow_increments_allow_count(self, brain, mock_client):
        current = {"total_evaluations": 2, "allow_count": 2,
                   "escalate_count": 0, "highest_risk_seen": "LOW",
                   "first_seen": "2026-01-01"}
        self._setup_profile(mock_client, current)
        brain._upsert_vendor_profile(
            vendor_domain=TEST_VENDOR_DOMAIN,
            vendor_name="Acme",
            decision="ALLOW",
            exit_reason="converged",
            high_cats=[],
            brief="ALLOW (converged) after 3 turns.",
        )
        # Last update call should carry allow_count=3, total=3
        update_data = mock_client.update.call_args[0][0]
        assert update_data["total_evaluations"] == 3
        assert update_data["allow_count"] == 3
        assert update_data["escalate_count"] == 0

    def test_escalate_increments_escalate_count(self, brain, mock_client):
        current = {"total_evaluations": 1, "allow_count": 1,
                   "escalate_count": 0, "highest_risk_seen": "NONE",
                   "first_seen": "2026-01-01"}
        self._setup_profile(mock_client, current)
        brain._upsert_vendor_profile(
            vendor_domain=TEST_VENDOR_DOMAIN,
            vendor_name="Acme",
            decision="ESCALATE",
            exit_reason="high_severity",
            high_cats=["payment_routing"],
            brief="ESCALATE (high_severity) after 4 turns. HIGH: payment_routing.",
        )
        update_data = mock_client.update.call_args[0][0]
        assert update_data["escalate_count"] == 1

    def test_highest_risk_seen_ratchets_up(self, brain, mock_client):
        current = {"total_evaluations": 1, "allow_count": 1,
                   "escalate_count": 0, "highest_risk_seen": "MEDIUM",
                   "first_seen": "2026-01-01"}
        self._setup_profile(mock_client, current)
        brain._upsert_vendor_profile(
            vendor_domain=TEST_VENDOR_DOMAIN,
            vendor_name="Acme",
            decision="ESCALATE",
            exit_reason="converged",
            high_cats=["sender_identity"],   # HIGH this time
            brief="ESCALATE.",
        )
        update_data = mock_client.update.call_args[0][0]
        assert update_data["highest_risk_seen"] == "HIGH"

    def test_highest_risk_seen_does_not_drop(self, brain, mock_client):
        current = {"total_evaluations": 3, "allow_count": 2,
                   "escalate_count": 1, "highest_risk_seen": "HIGH",
                   "first_seen": "2026-01-01"}
        self._setup_profile(mock_client, current)
        brain._upsert_vendor_profile(
            vendor_domain=TEST_VENDOR_DOMAIN,
            vendor_name="Acme",
            decision="ALLOW",
            exit_reason="converged",
            high_cats=[],   # no HIGH findings this time
            brief="ALLOW.",
        )
        update_data = mock_client.update.call_args[0][0]
        # "HIGH" from history should be preserved
        assert update_data["highest_risk_seen"] == "HIGH"


# ---------------------------------------------------------------------------
# Integration tests — only run when real Supabase creds are present
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestProjectBrainIntegration:
    """
    Runs against a real Supabase instance.  Requires:
        SUPABASE_URL and SUPABASE_KEY set in environment.

    These tests write real rows tagged with a unique test prefix and
    clean them up afterwards.  Run with:
        pytest tests/test_brain.py -v -m integration
    """

    TEST_DOMAIN = f"holo-test-{uuid.uuid4().hex[:8]}.example.com"

    @pytest.fixture(autouse=True)
    def require_supabase(self):
        if not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")):
            pytest.skip("SUPABASE_URL / SUPABASE_KEY not set")

    @pytest.fixture
    def live_brain(self):
        b = ProjectBrain()
        if b._client is None:
            pytest.skip("ProjectBrain could not connect to Supabase")
        return b

    @pytest.fixture(autouse=True)
    def cleanup(self, live_brain):
        yield
        # Remove test rows after each test
        try:
            c = live_brain._client
            eval_ids = [
                r["evaluation_id"]
                for r in (c.table("holo_evaluations")
                            .select("evaluation_id")
                            .eq("vendor_domain", self.TEST_DOMAIN)
                            .execute().data or [])
            ]
            if eval_ids:
                c.table("holo_findings").delete().in_("evaluation_id", eval_ids).execute()
            c.table("holo_evaluations").delete().eq("vendor_domain", self.TEST_DOMAIN).execute()
            c.table("holo_vendor_profiles").delete().eq("vendor_domain", self.TEST_DOMAIN).execute()
        except Exception:
            pass

    def _test_request(self):
        return {
            "action":  {"type": "invoice_payment", "amount_usd": 9999},
            "context": {
                "vendor_record": {
                    "vendor_name":  "Holo Test Vendor",
                    "vendor_email": f"billing@{self.TEST_DOMAIN}",
                },
                "email_chain": [],
            },
        }

    def test_first_evaluation_returns_no_prior_context(self, live_brain):
        ctx = self._test_request()["context"]
        result = live_brain.retrieve_context({}, ctx)
        assert result is None, "Expected None for a brand-new vendor"

    def test_save_then_retrieve_returns_context(self, live_brain):
        request = self._test_request()
        result1 = _make_result(
            decision="ESCALATE",
            high_categories=["payment_routing"],
            findings=[{
                "category":  "payment_routing",
                "severity":  "HIGH",
                "fact_type": "SUBMITTED_DATA",
                "evidence":  "Bank changed 2 days ago.",
                "detail":    "Offshore account.",
            }],
        )
        live_brain.save_evaluation(result1, request)

        ctx     = request["context"]
        context = live_brain.retrieve_context({}, ctx)

        assert context is not None
        assert context["vendor_domain"] == self.TEST_DOMAIN
        assert context["total_evaluations"] == 1
        assert context["escalate_count"] == 1
        assert context["highest_risk_seen"] == "HIGH"
        assert len(context["recent_evaluations"]) == 1
        assert context["recent_evaluations"][0]["decision"] == "ESCALATE"
        assert len(context["prior_high_findings"]) == 1
        assert context["prior_high_findings"][0]["category"] == "payment_routing"

    def test_second_evaluation_compounds_counters(self, live_brain):
        request = self._test_request()
        result1 = _make_result(decision="ALLOW")
        result2 = _make_result(decision="ALLOW")
        live_brain.save_evaluation(result1, request)
        live_brain.save_evaluation(result2, request)

        ctx     = request["context"]
        context = live_brain.retrieve_context({}, ctx)

        assert context["total_evaluations"] == 2
        assert context["allow_count"] == 2

    def test_context_note_is_present(self, live_brain):
        request = self._test_request()
        live_brain.save_evaluation(_make_result(), request)
        ctx     = request["context"]
        context = live_brain.retrieve_context({}, ctx)
        assert "context_note" in context
        assert len(context["context_note"]) > 20
