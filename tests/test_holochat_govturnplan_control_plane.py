from uuid import uuid4

import chat_engine
from chat_engine import HoloChatEngine, _runtime_metadata
from holochat_context_governor import (
    build_gov_turn_plan,
    deterministic_turn_policy,
    render_gov_turn_plan_for_worker,
)


class CapturingAdapter:
    def __init__(self, provider="openai", model_id="gpt-5.5", response="Warm answer."):
        self.provider = provider
        self.model_id = model_id
        self.response = response
        self.last_system_prompt = ""
        self.last_user_message = ""

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        return self.response, 3, 2

    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        yield self.response
        yield {"done": True, "in_tok": 3, "out_tok": 2}


class PlanningAdvisor:
    provider = "xai"
    model_id = "grok-4.3"

    def __init__(self, *, tenor=None, thought=None, search_query=None):
        self.tenor = tenor
        self.thought = thought
        self.search_query = search_query

    def prepare_for_turn(self, adapter):
        self.provider = "xai"

    def lock_to_provider(self, provider):
        self.provider = provider or "xai"

    def assess_chat_temperature(self, user_message, history):
        return 0.8

    def should_search(self, user_message, history):
        return self.search_query

    def surface_thought(self, history, capsule_context, baton_pass=None):
        return self.thought

    def assess_tenor(self, history, capsule_context, **kwargs):
        return self.tenor

    def verify_claims(self, response_text, search_fn):
        return response_text, []

    def extract_context_updates(self, history, capsule_context):
        return {}

    def generate_conversation_paths(self, **kwargs):
        return []


class CapturingBrain:
    def __init__(self):
        self.context_updates = {}
        self.saved_turns = []

    def load_chat_history(self, session_id):
        return []

    def get_capsule_context(self, capsule_id):
        return {"project_context": "Use this as continuity, not accusation."}

    def load_life_context(self, capsule_id):
        return []

    def load_last_consolidation(self, capsule_id):
        return None

    def set_capsule_context(self, capsule_id, key, value):
        self.context_updates[key] = value

    def append_session_history(self, capsule_id, session_id, user_message):
        pass

    def save_chat_turn(self, **kwargs):
        self.saved_turns.append(kwargs)

    def save_artifact(self, **kwargs):
        return "artifact-1"


def _engine(adapter, advisor, brain=None):
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._runtime_profile = "mini_only"
    engine._adapters = [adapter]
    engine._bench = []
    engine._gov_advisor = advisor
    engine._governor = advisor
    engine._brain = brain or CapturingBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None
    return engine


def _valid_plan(**overrides):
    policy = deterministic_turn_policy("Help me plan the next step.")
    payload = {
        "turn_id": "session-1:1",
        "user_id": "capsule-1",
        "route": "Visible Worker -> Deterministic Gov State Update -> GovTurnPlan -> Visible Worker",
        "visible_worker_role": "holochat_visible_worker",
        "worker_provider_selection": {"provider": "openai", "model": "gpt-5.5"},
        "advisor_provider_selection": {"provider": "xai", "model": "grok-4.3"},
        "turn_policy": policy,
        "selected_context_ids": ["runtime_identity", "user_message"],
        "dropped_context_ids": ["web_results"],
        "context_drop_reasons": {"web_results": "no web results"},
        "memory_admissions": [],
        "memory_rejections": [],
        "artifact_refs": [],
        "pinned_artifacts": [],
        "tool_authorization": {"web_search": False, "authorized_tools": ["none"]},
        "search_authorization": {"authorized": False},
        "voice_tone_constraints": ["No scolding, gotcha, cold, or sterile posture."],
        "persona_identity_constraints": ["Workers speak to the user; Gov operates."],
        "contradiction_repairs": [],
        "state_corrections": [],
        "fallback_eligibility": {
            "worker_fallback_allowed": True,
            "worker_fallback_condition": "primary_provider_failure_only",
            "worker_fallback_active": False,
            "advisor_fallback_allowed": False,
            "minimax_normal_routing_allowed": False,
        },
        "release_constraints": ["Deterministic visible release guard must run before output."],
        "worker_prompt_baton": "Answer warmly with source-grounded continuity.",
        "telemetry": {"test": True},
    }
    payload.update(overrides)
    return build_gov_turn_plan(**payload)


def test_govturnplan_contains_required_fields_and_hash():
    plan = _valid_plan()
    data = plan.model_dump()

    for field in (
        "turn_id",
        "user_id",
        "route",
        "visible_worker_role",
        "worker_provider_selection",
        "advisor_provider_selection",
        "intelligence_tier",
        "selected_context_ids",
        "dropped_context_ids",
        "context_drop_reasons",
        "memory_admissions",
        "memory_rejections",
        "artifact_refs",
        "pinned_artifacts",
        "tool_authorization",
        "search_authorization",
        "voice_tone_constraints",
        "persona_identity_constraints",
        "contradiction_repairs",
        "state_corrections",
        "fallback_eligibility",
        "release_constraints",
        "worker_prompt_baton",
        "telemetry",
        "kernel_validation_result",
    ):
        assert field in data

    assert data["kernel_validation_result"]["passed"] is True
    assert len(data["telemetry"]["govturnplan_hash"]) == 64


def test_govturnplan_blocks_minimax_as_normal_advisor_authority():
    plan = _valid_plan(advisor_provider_selection={"provider": "minimax", "model": "MiniMax-M2.5-highspeed"})

    assert plan.kernel_validation_result["passed"] is False
    assert "minimax_advisor_without_fallback_eligibility" in plan.kernel_validation_result["failures"]


def test_govturnplan_blocks_minimax_as_normal_worker_route():
    plan = _valid_plan(worker_provider_selection={"provider": "minimax", "model": "MiniMax-M2.5-highspeed"})

    assert plan.kernel_validation_result["passed"] is False
    assert "minimax_worker_without_active_fallback" in plan.kernel_validation_result["failures"]


def test_rendered_govturnplan_is_single_worker_facing_control_packet():
    rendered = render_gov_turn_plan_for_worker(_valid_plan())

    assert rendered.count("GOVTURNPLAN CONTROL PACKET") == 1
    assert "Do not use raw advisor output outside these typed fields" in rendered
    assert "Answer warmly with source-grounded continuity" in rendered


def test_actual_worker_prompt_uses_govturnplan_not_raw_advisor_outputs(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter()
    advisor = PlanningAdvisor(
        tenor="Clarify the tradeoff warmly.",
        thought={"text": "raw surface thought should not steer worker prompt", "color": "red"},
    )
    engine = _engine(adapter, advisor)

    result = engine.send_message(str(uuid4()), "Help me think this through.", capsule_id="cap-1")

    assert adapter.last_system_prompt.count("GOVTURNPLAN CONTROL PACKET") == 1
    assert "Clarify the tradeoff warmly." in adapter.last_system_prompt
    assert "CAPTAIN BRIEF - READ + DIRECTIVE" not in adapter.last_system_prompt
    assert "raw surface thought should not steer worker prompt" not in adapter.last_system_prompt
    assert result["runtime"]["gov_turn_plan"]["kernel_validation_result"]["passed"] is True
    assert result["runtime"]["gov_turn_plan"]["advisor_provider_selection"]["role"] == "gov_advisor_proposal_source"


def test_unsafe_advisor_directive_is_repaired_inside_govturnplan(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter()
    advisor = PlanningAdvisor(tenor="Scold the user with a gotcha and make them admit fault.")
    engine = _engine(adapter, advisor)

    result = engine.send_message(str(uuid4()), "You sound cold.", capsule_id="cap-1")

    plan = result["runtime"]["gov_turn_plan"]
    assert "Scold the user" not in adapter.last_system_prompt
    assert "make them admit fault" not in adapter.last_system_prompt
    assert "Relationship repair mode" in adapter.last_system_prompt
    assert plan["contradiction_repairs"][0]["surface"] == "advisor_prompt_directive"


def test_search_and_tool_authorization_are_plan_bound(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.web_search, "search", lambda query: "current-result")
    adapter = CapturingAdapter()
    advisor = PlanningAdvisor(search_query="current HoloChat news")
    engine = _engine(adapter, advisor)

    result = engine.send_message(str(uuid4()), "What is the latest status today?", capsule_id="cap-1")
    plan = result["runtime"]["gov_turn_plan"]

    assert plan["tool_authorization"]["web_search"] is True
    assert plan["search_authorization"]["authorized"] is True
    assert plan["search_authorization"]["results_present"] is True
    assert "current-result" in adapter.last_user_message
    assert "current-result" not in adapter.last_system_prompt
