"""
Unit tests for context_governor.py — coverage matrix helpers,
convergence logic, clean-bill-of-health, and ContextGovernor with mocks.
"""
import pytest
from copy import deepcopy
from unittest.mock import patch

from llm_adapters import BEC_CATEGORIES, SEVERITY_RANK
from context_governor import (
    MIN_TURNS,
    MAX_TURNS,
    _init_coverage,
    _update_coverage,
    _any_high,
    _convergence_check,
    _is_clean_bill_of_health,
    _build_initial_state,
    _coverage_summary,
    ContextGovernor,
)
from tests.conftest import MockAdapter, make_turn_result, make_escalate_result


# ---------------------------------------------------------------------------
# _init_coverage
# ---------------------------------------------------------------------------

class TestInitCoverage:

    def test_has_all_categories(self):
        cov = _init_coverage()
        assert set(cov.keys()) == set(BEC_CATEGORIES)

    def test_all_unaddressed_at_start(self):
        cov = _init_coverage()
        for cat in BEC_CATEGORIES:
            assert cov[cat]["addressed"] is False

    def test_all_none_severity_at_start(self):
        cov = _init_coverage()
        for cat in BEC_CATEGORIES:
            assert cov[cat]["max_severity"] == "NONE"


# ---------------------------------------------------------------------------
# _update_coverage
# ---------------------------------------------------------------------------

class TestUpdateCoverage:

    def test_first_flag_marks_addressed(self):
        cov = _init_coverage()
        flags = {"payment_routing": "MEDIUM"}
        updated, delta = _update_coverage(cov, flags)
        assert updated["payment_routing"]["addressed"] is True
        assert updated["payment_routing"]["max_severity"] == "MEDIUM"

    def test_first_flag_increments_delta(self):
        cov = _init_coverage()
        _, delta = _update_coverage(cov, {"payment_routing": "LOW"})
        assert delta == 1

    def test_same_severity_no_delta(self):
        cov = _init_coverage()
        cov["payment_routing"] = {"addressed": True, "max_severity": "MEDIUM"}
        _, delta = _update_coverage(cov, {"payment_routing": "MEDIUM"})
        assert delta == 0

    def test_severity_escalation_increments_delta(self):
        cov = _init_coverage()
        cov["payment_routing"] = {"addressed": True, "max_severity": "LOW"}
        updated, delta = _update_coverage(cov, {"payment_routing": "HIGH"})
        assert delta == 1
        assert updated["payment_routing"]["max_severity"] == "HIGH"

    def test_severity_downgrade_no_delta(self):
        """A lower severity on an already-addressed category should not change anything."""
        cov = _init_coverage()
        cov["payment_routing"] = {"addressed": True, "max_severity": "HIGH"}
        updated, delta = _update_coverage(cov, {"payment_routing": "LOW"})
        assert delta == 0
        assert updated["payment_routing"]["max_severity"] == "HIGH"

    def test_none_flag_ignored(self):
        cov = _init_coverage()
        updated, delta = _update_coverage(cov, {"payment_routing": "NONE"})
        assert updated["payment_routing"]["addressed"] is False
        assert delta == 0

    def test_multiple_new_flags(self):
        cov = _init_coverage()
        flags = {
            "sender_identity": "LOW",
            "payment_routing": "HIGH",
            "approval_chain": "MEDIUM",
        }
        _, delta = _update_coverage(cov, flags)
        assert delta == 3

    def test_does_not_mutate_original(self):
        cov = _init_coverage()
        original = deepcopy(cov)
        _update_coverage(cov, {"payment_routing": "HIGH"})
        assert cov == original


# ---------------------------------------------------------------------------
# _any_high
# ---------------------------------------------------------------------------

class TestAnyHigh:

    def test_returns_false_on_clean_matrix(self):
        cov = _init_coverage()
        assert _any_high(cov) is False

    def test_returns_true_when_one_category_is_high(self):
        cov = _init_coverage()
        cov["payment_routing"]["max_severity"] = "HIGH"
        assert _any_high(cov) is True

    def test_medium_is_not_high(self):
        cov = _init_coverage()
        for cat in BEC_CATEGORIES:
            cov[cat]["max_severity"] = "MEDIUM"
        assert _any_high(cov) is False


# ---------------------------------------------------------------------------
# _convergence_check
# ---------------------------------------------------------------------------

class TestConvergenceCheck:

    def test_no_convergence_before_min_turns(self):
        deltas = [0, 0]
        for turns in range(1, MIN_TURNS):
            assert _convergence_check(deltas, turns) is False

    def test_convergence_fires_at_min_turns_with_two_zeros(self):
        deltas = [1, 0, 0]  # 3 turns, last two are zero
        assert _convergence_check(deltas, MIN_TURNS) is True

    def test_no_convergence_with_only_one_zero(self):
        deltas = [1, 2, 0]
        assert _convergence_check(deltas, MIN_TURNS) is False

    def test_no_convergence_with_nonzero_last_delta(self):
        deltas = [0, 0, 1]
        assert _convergence_check(deltas, MIN_TURNS) is False

    def test_convergence_fires_after_min_turns(self):
        deltas = [1, 1, 1, 0, 0]
        assert _convergence_check(deltas, 5) is True

    def test_insufficient_deltas_list(self):
        """If fewer than 2 deltas, convergence cannot fire even after min turns."""
        assert _convergence_check([0], MIN_TURNS) is False
        assert _convergence_check([], MIN_TURNS) is False


# ---------------------------------------------------------------------------
# _is_clean_bill_of_health
# ---------------------------------------------------------------------------

class TestIsCleanBillOfHealth:

    def _clean_state(self):
        """State after 2 turns, both ALLOW, all LOW/NONE."""
        turns = [
            {
                "verdict": "ALLOW",
                "severity_flags": {cat: "LOW" for cat in BEC_CATEGORIES},
            },
            {
                "verdict": "ALLOW",
                "severity_flags": {cat: "LOW" for cat in BEC_CATEGORIES},
            },
        ]
        cov = _init_coverage()
        for cat in BEC_CATEGORIES:
            cov[cat] = {"addressed": True, "max_severity": "LOW"}
        return {"turn_history": turns, "coverage_matrix": cov}

    def test_clean_state_returns_true(self):
        state = self._clean_state()
        assert _is_clean_bill_of_health(state) is True

    def test_fewer_than_two_turns_returns_false(self):
        state = self._clean_state()
        state["turn_history"] = state["turn_history"][:1]
        assert _is_clean_bill_of_health(state) is False

    def test_one_escalate_verdict_returns_false(self):
        state = self._clean_state()
        state["turn_history"][0]["verdict"] = "ESCALATE"
        assert _is_clean_bill_of_health(state) is False

    def test_medium_flag_in_turn_history_returns_false(self):
        state = self._clean_state()
        state["turn_history"][1]["severity_flags"]["payment_routing"] = "MEDIUM"
        assert _is_clean_bill_of_health(state) is False

    def test_high_flag_in_coverage_matrix_returns_false(self):
        state = self._clean_state()
        state["coverage_matrix"]["payment_routing"]["max_severity"] = "HIGH"
        assert _is_clean_bill_of_health(state) is False

    def test_medium_in_coverage_matrix_returns_false(self):
        state = self._clean_state()
        state["coverage_matrix"]["sender_identity"]["max_severity"] = "MEDIUM"
        assert _is_clean_bill_of_health(state) is False


# ---------------------------------------------------------------------------
# _build_initial_state
# ---------------------------------------------------------------------------

class TestBuildInitialState:

    def test_contains_evaluation_id(self):
        state = _build_initial_state({}, "holo_abc123")
        assert state["evaluation_id"] == "holo_abc123"

    def test_turn_history_starts_empty(self):
        state = _build_initial_state({}, "test")
        assert state["turn_history"] == []

    def test_coverage_matrix_initialized(self):
        state = _build_initial_state({}, "test")
        assert set(state["coverage_matrix"].keys()) == set(BEC_CATEGORIES)

    def test_action_and_context_extracted(self):
        request = {"action": {"type": "invoice"}, "context": {"email_chain": []}}
        state = _build_initial_state(request, "test")
        assert state["action"]["type"] == "invoice"
        assert state["context"]["email_chain"] == []


# ---------------------------------------------------------------------------
# ContextGovernor with mock adapters — functional tests
# ---------------------------------------------------------------------------

class TestContextGovernorWithMocks:

    def _governor_with(self, results):
        """Create a ContextGovernor wired to a single MockAdapter repeating results."""
        adapter = MockAdapter(results)
        gov = ContextGovernor.__new__(ContextGovernor)
        gov._adapters = [adapter, adapter, adapter]
        return gov

    def _minimal_request(self):
        return {
            "action": {"type": "invoice_payment", "amount_usd": 5000},
            "context": {
                "email_chain": [{"from": "a@b.com", "body": "pay"}]
            },
        }

    def test_all_allow_low_returns_allow(self):
        """3 turns of ALLOW with all LOW flags should produce ALLOW."""
        results = [make_turn_result(verdict="ALLOW", turn_number=i) for i in range(1, 4)]
        gov = self._governor_with(results)
        result = gov.evaluate(self._minimal_request())
        assert result["decision"] == "ALLOW"

    def test_high_severity_forces_escalate(self):
        """HIGH in coverage matrix escalates when synthesis doesn't explicitly clear it."""
        high_flags = {cat: "LOW" for cat in BEC_CATEGORIES}
        high_flags["payment_routing"] = "HIGH"
        # Synthesis still carries the HIGH flag in its own output → override blocked
        synth_with_high = make_turn_result(
            verdict="ALLOW", turn_number=4, role="Synthesis", severities=high_flags
        )
        results = [
            make_escalate_result(turn_number=1, high_category="payment_routing"),
            make_turn_result(verdict="ALLOW", turn_number=2),
            make_turn_result(verdict="ALLOW", turn_number=3),
            synth_with_high,
        ]
        gov = self._governor_with(results)
        result = gov.evaluate(self._minimal_request())
        assert result["decision"] == "ESCALATE"

    def test_partial_evaluation_on_adapter_failure(self):
        """If an adapter raises on every attempt, the loop should auto-ESCALATE."""
        from llm_adapters import BaseAdapter

        class FailAdapter(BaseAdapter):
            provider = "fail"
            model_id = "fail"
            def call(self, s, u):
                raise RuntimeError("API down")

        gov = ContextGovernor.__new__(ContextGovernor)
        gov._adapters = [FailAdapter(), FailAdapter(), FailAdapter()]
        result = gov.evaluate(self._minimal_request())
        assert result["decision"] == "ESCALATE"
        assert result["partial"] is True

    def test_result_contains_required_keys(self):
        results = [make_turn_result(turn_number=i) for i in range(1, 4)]
        gov = self._governor_with(results)
        result = gov.evaluate(self._minimal_request())
        required = {
            "evaluation_id", "decision", "decision_reason", "turns_completed",
            "converged", "partial", "deltas", "turn_history",
            "coverage_matrix", "elapsed_ms", "total_tokens",
        }
        assert required.issubset(result.keys())

    def test_evaluation_id_has_holo_prefix(self):
        results = [make_turn_result(turn_number=i) for i in range(1, 4)]
        gov = self._governor_with(results)
        result = gov.evaluate(self._minimal_request())
        assert result["evaluation_id"].startswith("holo_")

    def test_turn_history_grows_per_turn(self):
        """Loop must run at least MIN_TURNS before convergence can fire."""
        # Use a MEDIUM flag so clean-bill-of-health early exit doesn't fire after turn 2
        medium_flags = {cat: "LOW" for cat in BEC_CATEGORIES}
        medium_flags["payment_routing"] = "MEDIUM"
        results = [
            make_turn_result(verdict="ALLOW", turn_number=1, severities=medium_flags),
            make_turn_result(verdict="ALLOW", turn_number=2, severities=medium_flags),
            make_turn_result(verdict="ALLOW", turn_number=3),
        ]
        gov = self._governor_with(results)
        result = gov.evaluate(self._minimal_request())
        assert len(result["turn_history"]) >= MIN_TURNS

    def test_total_tokens_aggregated(self):
        """total_tokens should sum input/output across all turns."""
        results = [make_turn_result(turn_number=i) for i in range(1, 4)]
        gov = self._governor_with(results)
        result = gov.evaluate(self._minimal_request())
        expected_input  = sum(t.get("input_tokens",  0) for t in result["turn_history"])
        expected_output = sum(t.get("output_tokens", 0) for t in result["turn_history"])
        assert result["total_tokens"]["input"]  == expected_input
        assert result["total_tokens"]["output"] == expected_output

    def test_clean_bill_of_health_exits_after_turn_2(self):
        """Two ALLOW turns with all LOW flags should exit before turn 3."""
        allow_result = make_turn_result(verdict="ALLOW")
        allow_result2 = make_turn_result(verdict="ALLOW", turn_number=2)
        gov = self._governor_with([allow_result, allow_result2])
        result = gov.evaluate(self._minimal_request())
        assert result["decision"] == "ALLOW"
        assert result["turns_completed"] == 2

    def test_synthesis_override_of_high_severity(self):
        """
        If Synthesis returns ALLOW with all LOW/NONE flags, it should be able to
        override a HIGH that was set earlier.
        """
        high_flags = {cat: "LOW" for cat in BEC_CATEGORIES}
        high_flags["payment_routing"] = "HIGH"

        from llm_adapters import TurnResult
        from dataclasses import replace

        turn1 = make_turn_result(verdict="ESCALATE", turn_number=1, severities=high_flags)
        turn2 = make_turn_result(verdict="ALLOW", turn_number=2)
        # Synthesis turn with all LOW flags and ALLOW verdict
        synthesis = make_turn_result(verdict="ALLOW", turn_number=3, role="Synthesis")
        synthesis = replace(synthesis, severity_flags={cat: "LOW" for cat in BEC_CATEGORIES})

        gov = self._governor_with([turn1, turn2, synthesis])
        result = gov.evaluate(self._minimal_request())
        # Synthesis ALLOW with all LOW overrides the HIGH
        assert result["decision"] == "ALLOW"


# ---------------------------------------------------------------------------
# _coverage_summary
# ---------------------------------------------------------------------------

class TestCoverageSummary:

    def test_returns_string(self):
        cov = _init_coverage()
        assert isinstance(_coverage_summary(cov), str)

    def test_unaddressed_shown_as_dash(self):
        cov = _init_coverage()
        summary = _coverage_summary(cov)
        assert "-" in summary

    def test_addressed_category_shows_first_letter(self):
        cov = _init_coverage()
        cov["payment_routing"]["addressed"] = True
        cov["payment_routing"]["max_severity"] = "HIGH"
        summary = _coverage_summary(cov)
        assert "RTE=H" in summary
