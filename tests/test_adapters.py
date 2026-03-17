"""
Unit tests for llm_adapters.py — pure functions only (no API calls).
"""
import json
import pytest
from llm_adapters import (
    BEC_CATEGORIES,
    SEVERITY_RANK,
    SEVERITY_VALUES,
    TurnResult,
    get_role_for_turn,
    build_system_prompt,
    build_user_message,
    _parse_json_response,
    _flags_summary,
)


# ---------------------------------------------------------------------------
# get_role_for_turn
# ---------------------------------------------------------------------------

class TestGetRoleForTurn:

    def test_turn_1_is_initial_assessment(self):
        assert get_role_for_turn(1) == "Initial Assessment"

    def test_turn_2_is_assumption_attacker(self):
        assert get_role_for_turn(2) == "Assumption Attacker"

    def test_turn_3_is_edge_case_hunter(self):
        assert get_role_for_turn(3) == "Edge Case Hunter"

    def test_turn_4_is_evidence_pressure_tester(self):
        assert get_role_for_turn(4) == "Evidence Pressure Tester"

    def test_turn_5_is_devils_advocate(self):
        assert get_role_for_turn(5) == "Devil's Advocate"

    def test_turn_6_cycles_back_to_attacker(self):
        assert get_role_for_turn(6) == "Assumption Attacker"

    def test_turn_7_is_edge_case_hunter(self):
        assert get_role_for_turn(7) == "Edge Case Hunter"

    def test_turn_8_is_evidence_pressure_tester(self):
        assert get_role_for_turn(8) == "Evidence Pressure Tester"

    def test_turn_9_cycles_to_attacker(self):
        assert get_role_for_turn(9) == "Assumption Attacker"

    def test_all_named_roles_are_non_empty_strings(self):
        for i in range(1, 10):
            role = get_role_for_turn(i)
            assert isinstance(role, str) and len(role) > 0


# ---------------------------------------------------------------------------
# build_system_prompt
# ---------------------------------------------------------------------------

class TestBuildSystemPrompt:

    def test_contains_role_name(self):
        prompt = build_system_prompt("Initial Assessment")
        assert "Initial Assessment" in prompt

    def test_contains_all_six_categories(self):
        prompt = build_system_prompt("Synthesis")
        for cat in BEC_CATEGORIES:
            assert cat in prompt

    def test_contains_required_json_schema(self):
        prompt = build_system_prompt("Synthesis")
        assert '"verdict"' in prompt
        assert '"severity_flags"' in prompt
        assert '"findings"' in prompt

    def test_unknown_role_falls_back_gracefully(self):
        """Unknown roles should fall back to Assumption Attacker instructions."""
        prompt = build_system_prompt("NonExistentRole")
        assert isinstance(prompt, str) and len(prompt) > 100

    def test_synthesis_role_contains_synthesis_instructions(self):
        prompt = build_system_prompt("Synthesis")
        assert "FINAL synthesizer" in prompt or "Synthesis" in prompt


# ---------------------------------------------------------------------------
# build_user_message
# ---------------------------------------------------------------------------

class TestBuildUserMessage:

    def _make_state(self, turns=None):
        return {
            "action": {"type": "invoice_payment", "amount_usd": 5000},
            "context": {"email_chain": [{"from": "a@b.com", "body": "pay this"}]},
            "turn_history": turns or [],
            "coverage_matrix": {},
        }

    def test_first_turn_has_no_prior_turns(self):
        state = self._make_state()
        msg = build_user_message(state, 1)
        assert "None. You are the first analyst" in msg

    def test_first_turn_contains_action(self):
        state = self._make_state()
        msg = build_user_message(state, 1)
        assert "invoice_payment" in msg

    def test_subsequent_turn_includes_prior_reasoning(self):
        prior = {
            "turn_number": 1,
            "provider": "openai",
            "model_id": "gpt-4o",
            "role": "Initial Assessment",
            "verdict": "ALLOW",
            "reasoning": "Everything looks fine.",
            "severity_flags": {cat: "LOW" for cat in BEC_CATEGORIES},
            "findings": [],
            "input_tokens": 100,
            "output_tokens": 50,
        }
        state = self._make_state(turns=[prior])
        msg = build_user_message(state, 2)
        assert "Everything looks fine." in msg
        assert "PRIOR ANALYST TURNS" in msg

    def test_turn_number_appears_in_message(self):
        state = self._make_state()
        msg = build_user_message(state, 3)
        assert "Turn 3" in msg


# ---------------------------------------------------------------------------
# _parse_json_response
# ---------------------------------------------------------------------------

VALID_RESPONSE = json.dumps({
    "verdict": "ALLOW",
    "reasoning_summary": "All looks clean.",
    "severity_flags": {
        "sender_identity":  "LOW",
        "invoice_amount":   "LOW",
        "payment_routing":  "LOW",
        "urgency_pressure": "NONE",
        "domain_spoofing":  "LOW",
        "approval_chain":   "LOW",
    },
    "findings": [
        {
            "category": "sender_identity",
            "severity": "LOW",
            "evidence": "Domain matches vendor record.",
            "detail": "Sender verified.",
        }
    ],
})


class TestParseJsonResponse:

    def test_parses_valid_response(self):
        parsed = _parse_json_response(VALID_RESPONSE, "test")
        assert parsed["verdict"] == "ALLOW"
        assert parsed["severity_flags"]["sender_identity"] == "LOW"
        assert len(parsed["findings"]) == 1

    def test_normalizes_verdict_to_uppercase(self):
        raw = json.dumps({
            "verdict": "allow",
            "reasoning_summary": "ok",
            "severity_flags": {cat: "LOW" for cat in BEC_CATEGORIES},
            "findings": [],
        })
        parsed = _parse_json_response(raw, "test")
        assert parsed["verdict"] == "ALLOW"

    def test_unknown_verdict_defaults_to_escalate(self):
        raw = json.dumps({
            "verdict": "MAYBE",
            "reasoning_summary": "uncertain",
            "severity_flags": {cat: "LOW" for cat in BEC_CATEGORIES},
            "findings": [],
        })
        parsed = _parse_json_response(raw, "test")
        assert parsed["verdict"] == "ESCALATE"

    def test_missing_category_defaults_to_none(self):
        raw = json.dumps({
            "verdict": "ALLOW",
            "reasoning_summary": "ok",
            "severity_flags": {},  # missing all categories
            "findings": [],
        })
        parsed = _parse_json_response(raw, "test")
        for cat in BEC_CATEGORIES:
            assert parsed["severity_flags"][cat] == "NONE"

    def test_invalid_severity_defaults_to_none(self):
        raw = json.dumps({
            "verdict": "ALLOW",
            "reasoning_summary": "ok",
            "severity_flags": {cat: "CRITICAL" for cat in BEC_CATEGORIES},
            "findings": [],
        })
        parsed = _parse_json_response(raw, "test")
        for cat in BEC_CATEGORIES:
            assert parsed["severity_flags"][cat] == "NONE"

    def test_strips_markdown_fences(self):
        raw = "```json\n" + VALID_RESPONSE + "\n```"
        parsed = _parse_json_response(raw, "test")
        assert parsed["verdict"] == "ALLOW"

    def test_missing_findings_defaults_to_empty_list(self):
        raw = json.dumps({
            "verdict": "ALLOW",
            "reasoning_summary": "ok",
            "severity_flags": {cat: "LOW" for cat in BEC_CATEGORIES},
        })
        parsed = _parse_json_response(raw, "test")
        assert parsed["findings"] == []

    def test_missing_reasoning_defaults_to_string(self):
        raw = json.dumps({
            "verdict": "ALLOW",
            "severity_flags": {cat: "LOW" for cat in BEC_CATEGORIES},
            "findings": [],
        })
        parsed = _parse_json_response(raw, "test")
        assert isinstance(parsed["reasoning_summary"], str)

    def test_raises_on_no_json_object(self):
        with pytest.raises(ValueError, match="No JSON object"):
            _parse_json_response("not json at all", "test")

    def test_raises_on_malformed_json(self):
        with pytest.raises(ValueError, match="JSON parse failed"):
            _parse_json_response("{invalid json}", "test")

    def test_json_with_preamble_text(self):
        """Model sometimes outputs text before the JSON block."""
        raw = "Here is my analysis:\n" + VALID_RESPONSE
        parsed = _parse_json_response(raw, "test")
        assert parsed["verdict"] == "ALLOW"


# ---------------------------------------------------------------------------
# TurnResult.to_dict
# ---------------------------------------------------------------------------

class TestTurnResult:

    def test_to_dict_contains_required_keys(self):
        tr = TurnResult(
            provider="openai",
            model_id="gpt-4o",
            role="Initial Assessment",
            turn_number=1,
            verdict="ALLOW",
            reasoning="Looks clean.",
            severity_flags={cat: "LOW" for cat in BEC_CATEGORIES},
            findings=[],
        )
        d = tr.to_dict()
        required = {"turn_number", "provider", "model_id", "role", "verdict",
                    "reasoning", "severity_flags", "findings",
                    "input_tokens", "output_tokens"}
        assert required.issubset(d.keys())

    def test_to_dict_verdict_preserved(self):
        tr = TurnResult(
            provider="anthropic", model_id="claude", role="Synthesis",
            turn_number=3, verdict="ESCALATE",
            reasoning="Bank mismatch detected.",
            severity_flags={cat: "HIGH" if cat == "payment_routing" else "LOW"
                            for cat in BEC_CATEGORIES},
            findings=[],
        )
        assert tr.to_dict()["verdict"] == "ESCALATE"


# ---------------------------------------------------------------------------
# SEVERITY_RANK ordering
# ---------------------------------------------------------------------------

class TestSeverityRank:

    def test_none_is_lowest(self):
        assert SEVERITY_RANK["NONE"] < SEVERITY_RANK["LOW"]

    def test_high_is_highest(self):
        assert SEVERITY_RANK["HIGH"] > SEVERITY_RANK["MEDIUM"]
        assert SEVERITY_RANK["HIGH"] > SEVERITY_RANK["LOW"]
        assert SEVERITY_RANK["HIGH"] > SEVERITY_RANK["NONE"]

    def test_all_four_values_present(self):
        assert set(SEVERITY_RANK.keys()) == SEVERITY_VALUES
