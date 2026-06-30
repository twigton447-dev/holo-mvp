from __future__ import annotations

import json
from dataclasses import dataclass, field
from uuid import uuid4

import chat_engine
from chat_engine import HoloChatEngine, _runtime_metadata
from holo_governed_shadow import (
    parse_gov_baton,
    governed_shadow_trigger,
    run_governed_shadow,
    select_best_artifact,
)
from holo_state import HoloState


@dataclass
class ShadowAdapter:
    provider: str
    model_id: str
    fail: bool = False
    worker_text: str = (
        "This private shadow answer preserves the user goal, names unresolved risk, "
        "and improves the argument structure without exposing hidden context."
    )
    calls: list[dict[str, str]] = field(default_factory=list)

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.calls.append(
            {
                "system": system_prompt,
                "user": user_message,
                "temperature": str(temperature),
            }
        )
        if self.fail:
            raise RuntimeError("provider raw body should not surface")
        if "Copy these lines exactly:" in user_message:
            return user_message.split("Copy these lines exactly:\n", 1)[1], 17, 11
        return self.worker_text, 23, 13


class FakeGovernor:
    provider = "governor"
    model_id = "governor-mini"

    def prepare_for_turn(self, adapter):
        pass

    def assess_chat_temperature(self, user_message, history):
        return 0.2

    def should_search(self, user_message, history):
        return None

    def surface_thought(self, history, capsule_context, baton_pass=None):
        return None

    def assess_tenor(self, history, capsule_context, **kwargs):
        return None

    def verify_claims(self, response_text, search_fn):
        return response_text, []

    def extract_context_updates(self, history, capsule_context):
        return {}

    def generate_conversation_paths(self, **kwargs):
        return ["Hold the core argument", "Stress test the weak link"]


class FakeBrain:
    def load_chat_history(self, session_id):
        return []

    def get_capsule_context(self, capsule_id):
        return {"project": "bounded memory", "api_key": "must-not-leak"}

    def load_life_context(self, capsule_id):
        return []

    def load_last_consolidation(self, capsule_id):
        return None

    def set_capsule_context(self, capsule_id, key, value):
        pass

    def append_session_history(self, capsule_id, session_id, user_message):
        pass

    def save_chat_turn(self, **kwargs):
        pass


def benchmark_roster(*, failing_w2: bool = False):
    return [
        ShadowAdapter("xai", "grok-3-mini"),
        ShadowAdapter("openai", "gpt-5.4-mini", fail=failing_w2),
        ShadowAdapter("minimax", "MiniMax-M2.5-highspeed"),
    ]


def test_governed_shadow_trigger_targets_hard_chats_only():
    assert governed_shadow_trigger("Please verify this decision and risk.").should_run is True
    assert governed_shadow_trigger("hello").should_run is False
    assert governed_shadow_trigger("short", thread_health_level="RED").reason == "thread_health_red"
    assert governed_shadow_trigger("This does not feel like the Holo voice.").reason == "hard_chat_term:holo voice"


def test_gov_baton_rejects_model_selection_fields():
    try:
        parse_gov_baton("route_verdict=CONTINUE_WORKER\nselected_model=openai/gpt-5.4-mini")
    except ValueError as exc:
        assert "gov_model_selection_forbidden" in str(exc)
    else:
        raise AssertionError("Gov model selection must fail closed")


def test_governed_shadow_runs_exact_five_call_sequence_with_gov_sandwich(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_GOVERNED_SHADOW", "1")
    adapters = benchmark_roster()
    state = HoloState.from_chat_turn(
        session_id="session-1",
        turn_number=3,
        user_message="Please verify this strategic decision and stress test the risks.",
        rolling_summary="Prior turn asked for architecture quality.",
        continuity_ledger={"open_issues": ["unresolved risk"]},
    )

    result = run_governed_shadow(
        adapters=adapters,
        user_message="Please verify this strategic decision and stress test the risks.",
        holo_state=state,
        capsule_context={"project": "bounded memory", "secret-value": "must-not-leak"},
        visible_answer="Visible answer stays unchanged.",
    )

    assert result["status"] == "complete"
    assert result["call_count"] == 5
    assert [(row["slot"], row["role"], row["provider"], row["model"]) for row in result["call_sequence"]] == [
        ("W1", "worker", "xai", "grok-3-mini"),
        ("G1", "gov", "minimax", "MiniMax-M2.5-highspeed"),
        ("W2", "worker", "openai", "gpt-5.4-mini"),
        ("G2", "gov", "minimax", "MiniMax-M2.5-highspeed"),
        ("W3", "worker", "minimax", "MiniMax-M2.5-highspeed"),
    ]
    assert result["token_totals"]["gov_total"] > 0
    assert result["token_totals"]["worker_total"] > 0
    assert result["final_selector"]["selection_reason"] == "FINAL_ARTIFACT_SELECTED"
    assert result["visible_answer_replaced"] is False

    first_worker_prompt = adapters[0].calls[0]["user"]
    assert first_worker_prompt.index("GOV ROUTING LENS") < first_worker_prompt.index("STATE_BRIEF")
    assert first_worker_prompt.index("STATE_BRIEF") < first_worker_prompt.index("FULL LATEST GOV BATON")
    encoded = json.dumps(result, sort_keys=True).lower()
    assert "must-not-leak" not in encoded
    assert "raw prompt" not in encoded


def test_final_selector_preserves_best_admissible_prior_artifact():
    selected = select_best_artifact(
        [
            {"artifact_id": "A1", "slot": "W1", "gate_result": {"passed": True}},
            {"artifact_id": "A2", "slot": "W2", "gate_result": {"passed": False}},
        ]
    )

    assert selected["selected_artifact_id"] == "A1"
    assert selected["selection_reason"] == "BEST_PRIOR_ADMISSIBLE_SELECTED"
    assert selected["final_regressed"] is True


def test_provider_failure_preserves_invalid_shadow_without_raw_error(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_GOVERNED_SHADOW", "1")
    adapters = benchmark_roster(failing_w2=True)
    state = HoloState.from_chat_turn(
        session_id="session-1",
        turn_number=3,
        user_message="Please verify this decision.",
    )

    result = run_governed_shadow(
        adapters=adapters,
        user_message="Please verify this decision.",
        holo_state=state,
        capsule_context={},
        visible_answer="Visible answer stays unchanged.",
    )

    assert result["status"] == "invalid"
    assert result["invalidation_reason"] == "WORKER_FAILURE"
    assert result["root_failure"]["slot"] == "W2"
    assert result["root_failure"]["error"] == {"type": "RuntimeError"}
    assert "provider raw body" not in json.dumps(result)
    assert result["visible_answer_replaced"] is False


def test_holochat_runtime_reports_governed_shadow_without_replacing_answer(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_GOVERNED_SHADOW", "1")
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapters = benchmark_roster()
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = adapters
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Please verify this strategy and argument.")

    assert result["response"] == adapters[0].worker_text
    shadow = result["runtime"]["governed_shadow"]
    assert shadow["status"] == "complete"
    assert shadow["call_count"] == 5
    assert shadow["visible_answer_replaced"] is False
    assert shadow["roster"][1]["provider"] == "minimax"
    assert shadow["roster"][1]["role"] == "gov"
    assert "must-not-leak" not in json.dumps(result["runtime"]).lower()


def test_holochat_shadow_skips_when_exact_roster_missing(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_GOVERNED_SHADOW", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [ShadowAdapter("xai", "grok-3-mini")]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Please verify this strategy.")
    shadow = result["runtime"]["governed_shadow"]

    assert result["response"] == engine._adapters[0].worker_text
    assert shadow["status"] == "skipped"
    assert "openai/gpt-5.4-mini" in shadow["missing_roster"]
    assert shadow["visible_answer_replaced"] is False
