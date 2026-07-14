import json
from uuid import uuid4

import chat_engine
import pytest
from chat_engine import HoloChatEngine, _runtime_metadata
from holochat_context_governor import (
    HoloBrainInjectionMode,
    HoloBrainInjectionPlan,
    build_gov_turn_plan,
    deterministic_turn_policy,
    render_gov_turn_plan_for_worker,
)
from holochat_evidence import build_web_evidence_bundle, render_web_evidence


class CapturingAdapter:
    def __init__(self, provider="openai", model_id="gpt-5.5", response="Warm answer."):
        self.provider = provider
        self.model_id = model_id
        self.response = response
        self.last_system_prompt = ""
        self.last_user_message = ""
        self.last_history = []

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        self.last_history = list(history)
        return self.response, 3, 2

    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        self.last_user_message = user_message
        self.last_history = list(history)
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


class DeepPlanningAdvisor(PlanningAdvisor):
    def __init__(self, *, events=None, proposal=None):
        super().__init__(tenor="Preserve the relationship arc and answer the live question directly.")
        self.events = events if events is not None else []
        self.proposal = proposal or {
            "conversation_phase": "deepening",
            "active_threads": [
                {"id": "continuity", "subject": "recursive conversation continuity", "status": "active", "last_turn": 6, "importance": "high"},
            ],
            "parked_threads": [],
            "resurfaced_threads": [],
            "worker_contributions": [
                {"turn": 5, "worker": "xai/grok-4.3", "contribution": "Identified ordered history as primary recursive evidence.", "status": "standing"},
            ],
            "user_portrait": ["The user values depth, continuity, and direct collaboration."],
            "current_state_of_affairs": "The user is testing whether HoloChat can preserve a complex arc.",
            "chronological_ledger_append": [
                "Milestone: continuity pressure increased around memory and tone.",
            ],
            "rolling_summary": "The conversation began with continuity architecture and evolved into a live test of whether HoloGov can preserve the full story while a fresh worker responds with depth.",
            "narrative_arc": "The user is moving from design belief to evidence under pressure.",
            "active_tension": "Richness must increase without false intimacy or loss of truth.",
            "settled_decisions": ["HoloGov owns continuity; workers speak."],
            "unresolved_questions": ["Can the runtime preserve the full ordered story across rotation?"],
            "key_anchors": ["The worker is a brilliant stranger entering the room."],
            "contradictions": [],
            "context_manifest": {
                "selection_rationale": "Retain origins, prior worker gains, and the live continuity question.",
                "known_gaps": [],
            },
            "preserve": ["Preserve the origin of the architecture discussion."],
            "reject": ["Reject generic summary and premature closure."],
            "worker_assignment": {
                "objective": "Advance the continuity design by one defensible layer.",
                "inspect": ["ordered history", "prior worker contributions"],
                "build_on": ["the primary-evidence decision"],
                "challenge": ["summary-as-replacement assumptions"],
                "avoid": ["generic restart"],
                "completion_signal": "The answer preserves history and adds a concrete test.",
            },
            "next_worker_directive": "Connect the current request to the full arc, identify the real tradeoff, and propose a concrete test without sounding clinical.",
            "confidence_notes": ["The desire for continuity is explicit; emotional interpretation remains tentative."],
            "memory_retrieval_requests": ["Prior architecture decisions"],
        }
        self.last_synthesis_kwargs = None

    def compile_holochat_control_packet(self, **kwargs):
        self.events.append("hologov_control_compilation")
        self.last_synthesis_kwargs = kwargs
        return {
            "proposal": self.proposal,
            "telemetry": {
                "mode": "hologov_control_compilation_v3",
                "contract": "bounded_delta_v3",
                "provider": "openai",
                "model": "gpt-5.5",
                "input_tokens": 2400,
                "output_tokens": 900,
                "output_token_budget": 3000,
                "latency_ms": 1200,
                "ordered_history_messages": len(kwargs.get("ordered_history") or []),
            },
        }


class FailingControlAdvisor(DeepPlanningAdvisor):
    def compile_holochat_control_packet(self, **kwargs):
        self.events.append("hologov_control_compilation")
        self.last_synthesis_kwargs = kwargs
        raise ValueError("synthetic truncated control packet")

    def get_last_holochat_control_telemetry(self):
        return {
            "mode": "hologov_control_compilation_v3",
            "contract": "bounded_delta_v3",
            "provider": "openai",
            "model": "gpt-5.5",
            "finish_reason": "length",
            "output_token_budget": 6000,
        }


class SingleCallAdvisor(DeepPlanningAdvisor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_calls = 0

    def get_api_call_count(self):
        return self.api_calls

    def compile_holochat_control_packet(self, **kwargs):
        self.api_calls += 1
        return super().compile_holochat_control_packet(**kwargs)

    def assess_chat_temperature(self, user_message, history):
        raise AssertionError("canonical mode must fold temperature into deterministic turn policy")

    def should_search(self, user_message, history):
        raise AssertionError("canonical mode must use deterministic search authorization")

    def surface_thought(self, history, capsule_context, baton_pass=None):
        raise AssertionError("canonical mode must not spend a separate Gov call on thought metadata")

    def assess_tenor(self, history, capsule_context, **kwargs):
        raise AssertionError("canonical mode must carry tenor in the one GovTurnPlan call")

    def verify_claims(self, response_text, search_fn):
        raise AssertionError("canonical mode must not make a post-worker Gov claim-check call")

    def extract_context_updates(self, history, capsule_context):
        raise AssertionError("canonical mode must admit memory proposals from GovTurnPlan")

    def generate_conversation_paths(self, **kwargs):
        raise AssertionError("canonical mode must not make a post-worker Gov path call")


class FailingWorkerAdapter(CapturingAdapter):
    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        raise RuntimeError("synthetic primary worker outage")


class OrderedWorkerAdapter(CapturingAdapter):
    def __init__(self, events):
        super().__init__(response="A connected, warm answer.")
        self.events = events

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.events.append("visible_worker_call")
        return super().chat_call(system_prompt, history, user_message, temperature, images=images)


class OrderedStreamingWorkerAdapter(CapturingAdapter):
    def __init__(self, events):
        super().__init__(response="A connected, warm streamed answer.")
        self.events = events

    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.events.append("visible_worker_call")
        yield from super().stream_chat_call(system_prompt, history, user_message, temperature, images=images)


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
        "route": "Visible Worker -> HoloGov State Update -> GovTurnPlan -> Visible Worker",
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
        "persona_identity_constraints": ["Workers speak to the user; HoloGov operates."],
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
        "narrative_packet",
        "telemetry",
        "kernel_validation_result",
    ):
        assert field in data

    assert data["kernel_validation_result"]["passed"] is True
    assert len(data["telemetry"]["govturnplan_hash"]) == 64
    assert set(data["narrative_packet"]) >= {
        "topic_registry",
        "user_portrait",
        "current_state_of_affairs",
        "narrative_arc",
        "active_tension",
        "holobrain_operator",
        "memory_stewardship",
        "holobrain_projection",
        "control_health",
        "preserve",
        "reject",
        "next_worker_directive",
    }
    assert data["narrative_packet"]["memory_stewardship"]["authority"] == "HoloGov-only"
    assert data["telemetry"]["narrative_packet_token_estimate"] > 0
    assert data["telemetry"]["worker_prompt_baton_token_estimate"] > 0
    assert data["telemetry"]["govturnplan_payload_token_estimate"] > 0


def test_govturnplan_blocks_minimax_as_normal_advisor_authority():
    plan = _valid_plan(advisor_provider_selection={"provider": "minimax", "model": "MiniMax-M2.5-highspeed"})

    assert plan.kernel_validation_result["passed"] is False
    assert "minimax_advisor_without_fallback_eligibility" in plan.kernel_validation_result["failures"]


def test_govturnplan_allows_minimax_only_as_private_hologov_proposal_source():
    plan = _valid_plan(
        advisor_provider_selection={
            "provider": "minimax",
            "model": "MiniMax-M2.7-highspeed",
            "role": "hologov_control_proposal_source",
            "authority": "proposal_only",
            "visible_worker_eligible": False,
        }
    )

    assert plan.kernel_validation_result["passed"] is True
    assert "minimax_advisor_without_fallback_eligibility" not in plan.kernel_validation_result["failures"]


def test_govturnplan_blocks_minimax_as_normal_worker_route():
    plan = _valid_plan(worker_provider_selection={"provider": "minimax", "model": "MiniMax-M2.5-highspeed"})

    assert plan.kernel_validation_result["passed"] is False
    assert "minimax_worker_without_active_fallback" in plan.kernel_validation_result["failures"]


def test_rendered_govturnplan_is_single_worker_facing_control_packet():
    rendered = render_gov_turn_plan_for_worker(_valid_plan())

    assert rendered.count("GOVTURNPLAN CONTROL PACKET") == 1
    assert "Do not use raw advisor output outside these typed fields" in rendered
    assert "Answer warmly with source-grounded continuity" in rendered
    assert "narrative_packet" in rendered
    assert "next_worker_directive" in rendered
    assert "HoloGov is the only runtime role authorized to enter, query, organize, update, prune, archive, or manage HoloBrain" in rendered


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
    assert "narrative_packet" in adapter.last_system_prompt
    assert "user_portrait" in adapter.last_system_prompt
    assert "current_state_of_affairs" in adapter.last_system_prompt
    assert "HoloGov is the only HoloBrain operator" in adapter.last_system_prompt
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
    def fake_run(query):
        bundle = build_web_evidence_bundle(
            query,
            [{"url": "https://example.test/current", "title": "Current", "content": "current-result"}],
            provider="test-search",
        )
        return chat_engine.web_search.SearchRun(
            query=query, provider="test-search", outcome="checked", latency_ms=0,
            evidence_bundle=bundle,
        )
    monkeypatch.setattr(chat_engine.web_search, "run_search", fake_run)
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


def test_hologov_handoff_records_selected_episodes_evidence_and_worker_receipt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    bundle = build_web_evidence_bundle(
        "current continuity research",
        [{
            "title": "Continuity research",
            "url": "https://example.org/continuity",
            "content": "Structured continuity improves inspectability.",
        }],
        provider="fake-search",
        retrieved_at="2026-07-14T12:00:00+00:00",
    )

    def fake_run_search(query):
        return chat_engine.web_search.SearchRun(
            query=query,
            provider="fake-search",
            outcome="checked",
            latency_ms=1,
            evidence_bundle=bundle,
        )

    monkeypatch.setattr(chat_engine.web_search, "run_search", fake_run_search)
    adapter = CapturingAdapter(response="The evidence supports an inspectable continuity packet [S1].")
    advisor = DeepPlanningAdvisor()
    advisor.search_query = "current continuity research"
    brain = CapturingBrain()
    brain.retrieve_relevant_episodes = lambda capsule_id, query, **kwargs: [{
        "episode_id": "episode-origin",
        "source_type": "holobrain_session",
        "source_id": "session-origin",
        "summary": "The original architecture decision made ordered history primary evidence.",
        "token_estimate": 18,
        "selection_reason": "query_overlap",
        "provenance": {"table": "holo_session_consolidations"},
    }]
    engine = _engine(adapter, advisor, brain=brain)
    session_id = str(uuid4())

    try:
        result = engine.send_message(
            session_id,
            "Check current continuity research and preserve our original architecture decision.",
            capsule_id="cap-1",
        )
        session = chat_engine._sessions[session_id]
    finally:
        chat_engine._sessions.pop(session_id, None)

    plan = result["runtime"]["gov_turn_plan"]
    packet = plan["narrative_packet"]
    receipt = packet["worker_context_receipt"]
    assert advisor.last_synthesis_kwargs["retrieved_episodes"][0]["episode_id"] == "episode-origin"
    assert advisor.last_synthesis_kwargs["web_evidence"]["sources"][0]["source_id"] == "S1"
    assert "episode:episode-origin" in plan["selected_context_ids"]
    assert "evidence:S1" in plan["selected_context_ids"]
    assert plan["tool_authorization"]["holobrain_episode_retrieval"] == {
        "authorized": True,
        "authority": "deterministic_hologov_preworker_context_operation",
        "capsule_scoped": True,
    }
    assert receipt["selected_episode_ids"] == ["episode-origin"]
    assert receipt["evidence_source_ids"] == ["S1"]
    delivered_receipt = result["context_budget"]["worker_context_receipt"]
    assert delivered_receipt["receipt_hash"] != receipt["receipt_hash"]
    assert delivered_receipt["system_prompt_hash"]
    assert delivered_receipt["user_prompt_hash"]
    assert delivered_receipt["history_payload_hash"]
    assert delivered_receipt["provider_reported_input_tokens"] == 3
    assert result["runtime"]["context_telemetry"]["worker_context_receipt"]["receipt_hash"] == delivered_receipt["receipt_hash"]
    assert result["web_sources"][0]["url"] == "https://example.org/continuity"
    assert "[S1]" in adapter.last_user_message
    assert session.holochat_state.episode_registry[0]["episode_id"] == "episode-origin"
    assert session.holochat_state.evidence_ledger[0]["source_id"] == "S1"
    assert session.holochat_state.worker_context_receipt["receipt_hash"] == delivered_receipt["receipt_hash"]


def test_worker_projection_bounds_canonical_hologov_ledger_without_losing_active_context():
    packet = {
        "packet_source": "hologov_control_compilation_v3",
        "control_health": {"status": "healthy"},
        "conversation_phase": "deepening",
        "current_state_of_affairs": "The live decision is active.",
        "rolling_summary": "Canonical summary " * 120,
        "narrative_arc": "The conversation moved from origin to implementation.",
        "active_tension": "Preserve depth without carrying repetitive scaffolding.",
        "user_portrait": [f"Portrait fact {index}" for index in range(24)],
        "key_anchors": [f"Anchor {index}" for index in range(16)],
        "topic_registry": [{"id": f"topic-{index}", "summary": "registry detail " * 20} for index in range(64)],
        "active_threads": [{"id": "active", "subject": "Current work", "summary": "Keep this lane."}],
        "parked_threads": [{"id": f"parked-{index}", "subject": "Old lane", "summary": "Parked context."} for index in range(12)],
        "worker_contributions": [
            {
                "turn": index,
                "worker": "openai/gpt-5.5",
                "contribution": "Full visible response " * 200,
                "hologov_note": f"Standing contribution {index}",
                "status": "standing",
            }
            for index in range(12)
        ],
        "chronological_ledger": [f"Turn {index} advanced the story." for index in range(30)],
        "worker_assignment": {"objective": "Make the next answer specific and useful."},
        "next_worker_directive": "Use the ordered conversation as primary evidence.",
        "memory_stewardship": {"operator_only": "Do not send this bookkeeping to workers."},
        "worker_context_receipt": {"receipt_hash": "private"},
    }

    projected = chat_engine.project_gov_narrative_packet_for_worker(packet, token_limit=1200)

    assert projected["active_threads"][0]["id"] == "active"
    assert projected["rolling_summary"].startswith("Canonical summary")
    assert projected["worker_assignment"]["objective"] == "Make the next answer specific and useful."
    assert "topic_registry" not in projected
    assert "memory_stewardship" not in projected
    assert "worker_context_receipt" not in projected
    assert "Full visible response" not in json.dumps(projected)
    assert len(json.dumps(projected)) < len(json.dumps(packet)) / 2
    assert chat_engine.estimate_context_tokens(json.dumps(projected)) <= 1200


def test_worker_projection_hard_caps_pathological_nested_holobrain_context():
    packet = {
        "current_state_of_affairs": "The current lane must survive.",
        "rolling_summary": "Ordered continuity. " * 300,
        "next_worker_directive": "Answer the active question with grounded continuity.",
        "holobrain_projection": {
            f"category-{index}": [
                {"fact": "nested context " * 100, "source": f"memory-{item_index}"}
                for item_index in range(100)
            ]
            for index in range(100)
        },
    }

    projected = chat_engine.project_gov_narrative_packet_for_worker(packet, token_limit=500)

    assert chat_engine.estimate_context_tokens(json.dumps(projected, sort_keys=True)) <= 500
    assert projected.get("current_state_of_affairs") == "The current lane must survive."
    assert "category-99" not in json.dumps(projected)


def test_eight_turn_no_provider_runtime_lap_preserves_rotation_state_and_bounds(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.delenv("HOLOCHAT_EXPERIMENT_MODE", raising=False)
    monkeypatch.delenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", raising=False)
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "6")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "3000")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "700")
    monkeypatch.setenv("HOLOCHAT_WORKER_GOV_PACKET_MAX_TOKENS", "1200")

    events = []

    class LapWorker(CapturingAdapter):
        def __init__(self, provider, model_id):
            super().__init__(provider=provider, model_id=model_id)
            self.histories = []

        def chat_call(self, system_prompt, history, user_message, temperature, images=None):
            self.last_system_prompt = system_prompt
            self.last_user_message = user_message
            self.last_history = list(history)
            self.histories.append(list(history))
            events.append(f"worker:{self.provider}")
            turn = len([event for event in events if event.startswith("worker:")])
            return (
                f"Turn {turn} keeps the evidence ordered, preserves uncertainty, and advances the live question warmly.",
                1200,
                80,
            )

    class LapAdvisor(SingleCallAdvisor):
        provider = "minimax"
        model_id = "MiniMax-M2.7-highspeed"

        def prepare_for_turn(self, adapter):
            self.provider = "minimax"
            self.model_id = "MiniMax-M2.7-highspeed"

        def lock_to_provider(self, provider):
            self.provider = "minimax"
            self.model_id = "MiniMax-M2.7-highspeed"

        def compile_holochat_control_packet(self, **kwargs):
            turn = int(kwargs.get("turn_number") or 0)
            self.proposal = {
                **self.proposal,
                "current_state_of_affairs": f"The recursive continuity lap is active at turn {turn}.",
                "rolling_summary": (
                    "The conversation is an ordered eight-turn evidence exercise. "
                    f"Turns 1 through {turn} preserve origins, uncertainty, worker gains, and the active question."
                ),
                "chronological_ledger_append": [f"Milestone: admitted turn {turn} into the canonical arc."],
                "worker_contribution_updates": [{
                    "turn": max(0, turn - 1),
                    "worker": "prior frontier worker",
                    "contribution": f"The prior worker preserved the evidence boundary before turn {turn}.",
                    "status": "standing",
                }],
                "next_worker_directive": (
                    f"At turn {turn}, use the ordered evidence and canonical arc; add one useful layer without overclaiming."
                ),
            }
            events.append("hologov:minimax")
            result = super().compile_holochat_control_packet(**kwargs)
            result["telemetry"].update({
                "provider": "minimax",
                "model": "MiniMax-M2.7-highspeed",
                "input_tokens": 1800 + (turn * 100),
                "output_tokens": 400,
            })
            return result

    class LapBrain(CapturingBrain):
        def __init__(self):
            super().__init__()
            self.session_names = []

        def update_session_name(self, capsule_id, session_id, name):
            self.session_names.append(name)

    openai = LapWorker("openai", "gpt-5.5")
    xai = LapWorker("xai", "grok-4.3")
    advisor = LapAdvisor(events=[])
    brain = LapBrain()
    engine = _engine(openai, advisor, brain=brain)
    engine._runtime_profile = chat_engine.CANONICAL_RUNTIME_PROFILE
    engine._adapters = [openai, xai]
    engine._runtime_info = _runtime_metadata(
        chat_engine.CANONICAL_RUNTIME_PROFILE,
        engine._adapters,
        [],
    )
    session_id = str(uuid4())
    results = []
    try:
        for turn in range(1, 9):
            results.append(engine.send_message(
                session_id,
                f"Evidence turn {turn}: preserve the origin, then add detail {turn} without pretending certainty.",
                capsule_id="synthetic-mira-capsule",
            ))
    finally:
        chat_engine._sessions.pop(session_id, None)

    assert [result["_provider"] for result in results] == ["openai", "xai"] * 4
    assert [event for event in events if event.startswith("hologov:")] == ["hologov:minimax"] * 8
    assert all(
        result["runtime"]["governor_trace"]["hologov_api_calls_this_turn"] == 1
        for result in results
    )
    assert all(
        len(result["runtime"]["cost_breakdown"]["hologov_calls"]) == 1
        and result["runtime"]["cost_breakdown"]["hologov_calls"][0]["provider"] == "minimax"
        and result["runtime"]["cost_breakdown"]["turn_estimated_cost_usd"] is not None
        for result in results
    )
    assert all(
        result["runtime"]["gov_turn_plan"]["kernel_validation_result"]["passed"] is True
        for result in results
    )
    assert results[-1]["context_budget"]["history_context"]["omitted_history_messages"] > 0
    assert max(len(history) for history in openai.histories + xai.histories) <= 6
    final_packet = results[-1]["runtime"]["gov_turn_plan"]["narrative_packet"]
    worker_packet = chat_engine.project_gov_narrative_packet_for_worker(final_packet, token_limit=1200)
    assert "through 8" in final_packet["rolling_summary"].lower()
    assert chat_engine.estimate_context_tokens(json.dumps(worker_packet, sort_keys=True)) <= 1200
    assert "no raw HoloBrain library access" in final_packet["holobrain_projection"]["authority"]
    assert final_packet["memory_stewardship"]["raw_library_access_for_worker"] is False
    assert all("scold" not in result["response"].lower() for result in results)
    assert len(brain.saved_turns) == 8


def test_streaming_handoff_uses_same_episode_evidence_and_citation_audit(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    bundle = build_web_evidence_bundle(
        "current continuity research",
        [{"title": "Continuity source", "url": "https://example.org/source", "content": "Evidence."}],
        provider="fake-search",
        retrieved_at="2026-07-14T12:00:00+00:00",
    )

    def fake_run_search(query):
        return chat_engine.web_search.SearchRun(
            query=query,
            provider="fake-search",
            outcome="checked",
            latency_ms=1,
            evidence_bundle=bundle,
        )

    monkeypatch.setattr(chat_engine.web_search, "run_search", fake_run_search)
    adapter = CapturingAdapter(response="The continuity evidence is available [S1].")
    advisor = DeepPlanningAdvisor()
    advisor.search_query = "current continuity research"
    brain = CapturingBrain()
    brain.retrieve_relevant_episodes = lambda capsule_id, query, **kwargs: [{
        "episode_id": "episode-stream",
        "source_type": "holobrain_session",
        "source_id": "session-stream",
        "summary": "A prior turn established the continuity constraint.",
        "token_estimate": 12,
    }]
    engine = _engine(adapter, advisor, brain=brain)
    session_id = str(uuid4())

    try:
        chunks = list(engine.stream_message(
            session_id,
            "Search for current continuity research and preserve the earlier constraint.",
            capsule_id="cap-1",
        ))
    finally:
        chat_engine._sessions.pop(session_id, None)

    done = next(item for item in chunks if isinstance(item, dict) and item.get("done"))
    receipt = done["runtime"]["gov_turn_plan"]["narrative_packet"]["worker_context_receipt"]
    assert receipt["selected_episode_ids"] == ["episode-stream"]
    assert receipt["evidence_source_ids"] == ["S1"]
    assert done["web_citations"]["status"] == "valid"
    assert done["runtime"]["web_citations"]["passed"] is True
    assert "[S1]" in adapter.last_user_message


def test_deep_hologov_reads_ordered_history_before_worker_and_persists_summary(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    events = []
    adapter = OrderedWorkerAdapter(events)
    advisor = DeepPlanningAdvisor(events=events)
    engine = _engine(adapter, advisor)
    session_id = str(uuid4())
    session = chat_engine.ChatSession(session_id=session_id, owner_capsule_id="cap-1")
    for index in range(6):
        session.history.extend(
            [
                {"role": "user", "content": f"Ordered user turn {index + 1}: preserve origin {index + 1}."},
                {"role": "assistant", "content": f"Ordered Holo turn {index + 1}: carry origin {index + 1} forward."},
            ]
        )
    session.turn_count = 6
    chat_engine._sessions[session_id] = session

    try:
        result = engine.send_message(
            session_id,
            "Now connect the entire story without flattening it.",
            capsule_id="cap-1",
        )
    finally:
        chat_engine._sessions.pop(session_id, None)

    assert events == ["hologov_control_compilation", "visible_worker_call"]
    assert len(advisor.last_synthesis_kwargs["ordered_history"]) == 12
    assert advisor.last_synthesis_kwargs["ordered_history"][0]["content"].startswith("Ordered user turn 1")
    assert advisor.last_synthesis_kwargs["ordered_history"][-1]["content"].startswith("Ordered Holo turn 6")
    assert len(adapter.last_history) == 12
    assert adapter.last_history[0]["content"].startswith("Ordered user turn 1")

    plan = result["runtime"]["gov_turn_plan"]
    packet = plan["narrative_packet"]
    control = plan["telemetry"]["hologov_control_compilation"]
    assert packet["packet_source"] == "hologov_control_compilation_v3"
    assert packet["chronological_ledger"] == [
        "Milestone: continuity pressure increased around memory and tone.",
    ]
    assert "conversation began with continuity architecture" in packet["rolling_summary"]
    assert "HOLOGOV CONTROL ASSIGNMENT" in plan["worker_prompt_baton"]
    assert control["mode"] == "hologov_control_compilation_v3"
    assert control["ordered_history_messages"] == 12
    assert control["admission"]["admitted"] is True
    assert "rolling_summary" in control["admission"]["admitted_fields"]
    assert packet["active_threads"][0]["id"] == "continuity"
    assert packet["worker_contributions"][0]["status"] == "standing"
    assert packet["worker_assignment"]["objective"].startswith("Advance the continuity")
    assert session.holochat_state.hologov_control_ledger["active_threads"][0]["id"] == "continuity"
    assert "conversation began with continuity architecture" in session.holochat_state.rolling_summary
    assert "Latest Holo response: A connected, warm answer." in session.holochat_state.rolling_summary


def test_hologov_v3_delta_compounds_prior_canonical_state():
    baseline = {
        "conversation_phase": "exploration",
        "topic_registry": [{
            "id": "architecture",
            "subject": "endless conversation architecture",
            "status": "active",
            "origin_turn": 1,
            "last_turn": 1,
        }],
        "active_threads": [{
            "id": "architecture",
            "subject": "endless conversation architecture",
            "status": "active",
            "origin_turn": 1,
            "last_turn": 1,
        }],
        "worker_contributions": [{
            "turn": "1",
            "worker": "openai/gpt-5.5",
            "contribution": "Established that ordered conversation is primary evidence.",
            "status": "standing",
        }],
        "user_portrait": ["The user values recursive depth."],
        "chronological_ledger": ["Turn 1 opened the architecture lane."],
        "settled_decisions": ["HoloGov maintains canonical state."],
        "unresolved_questions": ["How should topic returns work?"],
        "key_anchors": ["Workers are brilliant strangers."],
        "preserve": ["Preserve ordered evidence."],
        "reject": ["Reject generic restarts."],
    }
    proposal = {
        "conversation_phase": "deepening",
        "topic_updates": [{
            "id": "architecture",
            "subject": "endless conversation architecture",
            "status": "active",
            "origin_turn": 1,
            "last_turn": 2,
            "summary": "The hidden canonical state now compounds worker gains.",
        }],
        "worker_contribution_updates": [{
            "turn": 2,
            "worker": "xai/grok-4.3",
            "contribution": "Separated live transcript evidence from canonical navigation.",
            "status": "standing",
        }],
        "user_portrait_updates": ["The user wants continuity to improve with thread length."],
        "chronological_ledger_append": ["Milestone: evidence and navigation were separated."],
        "rolling_summary": "The architecture now keeps ordered evidence primary while HoloGov incrementally maintains a canonical navigation layer.",
        "settled_decision_additions": ["Canonical state is updated rather than rewritten."],
        "unresolved_question_additions": ["What is the long-run compaction threshold?"],
        "resolved_questions": ["How should topic returns work?"],
        "key_anchor_additions": ["The canonical ledger survives worker rotation."],
        "preserve_additions": ["Preserve prior DNA gains."],
        "reject_additions": ["Reject silent state reset."],
    }

    packet, admission = chat_engine._admit_hologov_narrative_proposal(
        baseline=baseline,
        proposal=proposal,
        user_message="Keep compounding the architecture without resetting it.",
        turn_number=2,
    )

    assert admission["admitted"] is True
    assert packet["conversation_phase"] == "deepening"
    assert packet["topic_registry"][0]["id"] == "architecture"
    assert packet["topic_registry"][0]["origin_turn"] == 1
    assert len(packet["worker_contributions"]) == 2
    assert packet["worker_contributions"][0]["contribution"].startswith("Established")
    assert packet["chronological_ledger"] == [
        "Turn 1 opened the architecture lane.",
        "Milestone: evidence and navigation were separated.",
    ]
    assert len(packet["user_portrait"]) == 2
    assert "How should topic returns work?" not in packet["unresolved_questions"]
    assert "What is the long-run compaction threshold?" in packet["unresolved_questions"]
    assert "Canonical state is updated rather than rewritten." in packet["settled_decisions"]
    assert "The canonical ledger survives worker rotation." in packet["key_anchors"]
    assert packet["packet_source"] == "hologov_control_compilation_v3"


def test_hologov_delta_deduplicates_turn_records_and_caps_new_chronology():
    baseline = {
        "worker_contributions": [{
            "turn": 1,
            "worker": "openai/gpt-5.5",
            "contribution": "The exact visible response remains the primary worker artifact.",
            "status": "standing",
        }],
        "chronological_ledger": ["Turn 1 opened the lane."],
        "contradictions": [{
            "claim_a": "A says possible.",
            "claim_b": "B says inconclusive.",
            "status": "unresolved",
            "source_turns": ["1"],
        }],
    }
    proposal = {
        "worker_contribution_updates": [{
            "turn": "1",
            "worker": "openai/gpt-5.5",
            "contribution": "HoloGov's shorter account of the same turn.",
            "status": "challenged",
        }],
        "chronological_ledger_append": [
            "Turn 2 user: Continue the same lane.",
            "milestone one",
            "milestone two",
            "milestone three",
            "milestone four must be deferred",
            "milestone five must be deferred",
        ],
        "contradiction_updates": [{
            "claim_a": "B says inconclusive.",
            "claim_b": "A says possible.",
            "status": "reconciled",
            "source_turns": ["2"],
        }],
    }

    packet, _ = chat_engine._admit_hologov_narrative_proposal(
        baseline=baseline,
        proposal=proposal,
        user_message="Continue the same lane.",
        turn_number=2,
    )

    assert len(packet["worker_contributions"]) == 1
    assert packet["worker_contributions"][0]["contribution"].startswith("The exact visible")
    assert packet["worker_contributions"][0]["hologov_note"].startswith("HoloGov's shorter")
    assert packet["worker_contributions"][0]["status"] == "challenged"
    assert packet["chronological_ledger"] == [
        "Turn 1 opened the lane.",
        "milestone one",
    ]
    assert len(packet["contradictions"]) == 1
    assert packet["contradictions"][0]["status"] == "reconciled"
    assert packet["contradictions"][0]["source_turns"] == ["1", "2"]


def test_hologov_delta_merges_paraphrased_contradictions_from_same_source_turns():
    baseline = {
        "contradictions": [{
            "claim_a": "Turn 5 treated Document C as strengthening the evidence.",
            "claim_b": "Turn 6 said Document C does not strengthen the evidence base.",
            "status": "unresolved",
            "source_turns": ["5", "6"],
        }],
    }
    proposal = {
        "contradiction_updates": [{
            "claim_a": "Document C was described on Turn 5 as strengthening the reason to keep the claim open.",
            "claim_b": "The Turn 6 repair says C does not strengthen the evidence or move the claim toward reliability.",
            "status": "reconciled",
            "source_turns": [5, 6],
        }],
    }

    packet, _ = chat_engine._admit_hologov_narrative_proposal(
        baseline=baseline,
        proposal=proposal,
        user_message="Preserve the repair.",
        turn_number=7,
    )

    assert len(packet["contradictions"]) == 1
    assert packet["contradictions"][0]["status"] == "reconciled"
    assert packet["contradictions"][0]["source_turns"] == ["5", "6"]


def test_completed_worker_turn_is_added_to_hologov_canonical_ledger():
    plan = _valid_plan(narrative_packet={
        "chronological_ledger": ["Turn 1 established the origin."],
        "worker_contributions": [{
            "turn": 1,
            "worker": "openai/gpt-5.5",
            "contribution": "Established the origin.",
            "status": "standing",
        }],
    })

    ledger = chat_engine._hologov_control_ledger_from_plan(
        plan,
        user_message="Now pressure-test the hidden context window.",
        response_text="The next layer is to separate canonical navigation from primary evidence.",
        worker_identity={"provider": "xai", "model": "grok-4.3"},
        turn_number=2,
    )

    assert len(ledger["worker_contributions"]) == 2
    assert ledger["worker_contributions"][-1]["worker"] == "xai/grok-4.3"
    assert ledger["chronological_ledger"][-2].startswith("Turn 2 user:")
    assert ledger["chronological_ledger"][-1].startswith("Turn 2 xai/grok-4.3:")


def test_hologov_compilation_failure_retains_telemetry_and_marks_control_degraded(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    events = []
    adapter = OrderedWorkerAdapter(events)
    advisor = FailingControlAdvisor(events=events)
    engine = _engine(adapter, advisor)

    result = engine.send_message(
        str(uuid4()),
        "Keep the full story coherent even if the control compiler fails.",
        capsule_id="cap-1",
    )
    plan = result["runtime"]["gov_turn_plan"]
    control = plan["telemetry"]["hologov_control_compilation"]

    assert events == ["hologov_control_compilation", "visible_worker_call"]
    assert control["mode"] == "local_fallback"
    assert control["reason"] == "control_compilation_error"
    assert control["error_type"] == "ValueError"
    assert control["finish_reason"] == "length"
    assert control["contract"] == "bounded_delta_v3"
    assert plan["narrative_packet"]["control_health"]["status"] == "degraded"
    assert "hologov_control_degraded" in plan["kernel_validation_result"]["warnings"]


def test_canonical_runtime_makes_exactly_one_hologov_call_and_reuses_plan_on_worker_failover(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    primary = FailingWorkerAdapter(provider="openai", model_id="gpt-5.5")
    fallback = CapturingAdapter(provider="xai", model_id="grok-4.3", response="Warm fallback answer.")
    advisor = SingleCallAdvisor(events=[])
    advisor.proposal = {
        **advisor.proposal,
        "memory_admission_proposals": [{
            "key": "current_project",
            "value": "[FACT] The user's durable project is Atlas.",
            "evidence": "durable project is Atlas",
        }],
    }
    brain = CapturingBrain()
    engine = _engine(primary, advisor, brain=brain)
    engine._runtime_profile = chat_engine.CANONICAL_RUNTIME_PROFILE
    engine._adapters = [primary, fallback]
    engine._runtime_info = _runtime_metadata(
        chat_engine.CANONICAL_RUNTIME_PROFILE,
        engine._adapters,
        [],
    )

    result = engine.send_message(
        str(uuid4()),
        "My durable project is Atlas. Keep the architecture coherent.",
        capsule_id="cap-1",
    )
    plan = result["runtime"]["gov_turn_plan"]
    control = plan["telemetry"]["hologov_control_compilation"]

    assert advisor.api_calls == 1
    assert result["_provider"] == "xai"
    assert result["runtime"]["failover"]["attempted"] is True
    assert control["reused_for_worker_failover"] is True
    assert control["compiled_for_worker"] == {"provider": "openai", "model": "gpt-5.5"}
    assert control["applied_to_worker"] == {"provider": "xai", "model": "grok-4.3"}
    assert result["runtime"]["governor_trace"]["single_hologov_call_mode"] is True
    assert result["runtime"]["governor_trace"]["hologov_api_calls_this_turn"] == 1
    assert brain.context_updates["current_project"].startswith("[FACT]")


def test_canonical_worker_supplies_dynamic_paths_without_an_extra_hologov_call(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    response = """The bounded pilot turns uncertainty into evidence without pretending the risk is gone.

[[HOLO_CONVERSATION_PATHS]]
1. Which pilot boundary would protect the relationship if demand grows unexpectedly?
2. Draft the smallest paid scope that creates evidence without creating dependence.
3. What fear remains after the practical downside has been honestly bounded?
[[/HOLO_CONVERSATION_PATHS]]"""
    adapter = CapturingAdapter(response=response)
    advisor = SingleCallAdvisor(events=[])
    engine = _engine(adapter, advisor)
    engine._runtime_profile = chat_engine.CANONICAL_RUNTIME_PROFILE
    engine._runtime_info = _runtime_metadata(
        chat_engine.CANONICAL_RUNTIME_PROFILE, engine._adapters, []
    )

    result = engine.send_message(
        str(uuid4()),
        "Help me decide whether to accept a bounded paid pilot.",
        capsule_id="cap-1",
    )

    assert advisor.api_calls == 1
    assert "HOLO_CONVERSATION_PATHS" not in result["response"]
    assert "HOLO_CONVERSATION_PATHS" not in engine._brain.saved_turns[-1]["holo_response"]
    assert result["conversation_paths"] == [
        "Which pilot boundary would protect the relationship if demand grows unexpectedly?",
        "Draft the smallest paid scope that creates evidence without creating dependence.",
        "What fear remains after the practical downside has been honestly bounded?",
    ]


def test_canonical_stream_buffers_and_extracts_dynamic_worker_paths(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    response = """Keep the material truth shared while protecting private detail.

[[HOLO_CONVERSATION_PATHS]]
1. Which material fact does joint ownership make impossible to keep private?
2. Draft one sentence that protects privacy without hiding the shared consequence.
3. Where does loyalty become concealment when another person's home is involved?
[[/HOLO_CONVERSATION_PATHS]]"""
    adapter = CapturingAdapter(response=response)
    advisor = SingleCallAdvisor(events=[])
    engine = _engine(adapter, advisor)
    engine._runtime_profile = chat_engine.CANONICAL_RUNTIME_PROFILE
    engine._runtime_info = _runtime_metadata(
        chat_engine.CANONICAL_RUNTIME_PROFILE, engine._adapters, []
    )

    events = list(engine.stream_message(
        str(uuid4()),
        "What can I disclose about a private expectation affecting our shared home?",
        capsule_id="cap-1",
    ))
    visible = "".join(event for event in events if isinstance(event, str))
    done = next(event for event in events if isinstance(event, dict) and event.get("done"))

    assert advisor.api_calls == 1
    assert "HOLO_CONVERSATION_PATHS" not in visible
    assert done["conversation_paths"] == [
        "Which material fact does joint ownership make impossible to keep private?",
        "Draft one sentence that protects privacy without hiding the shared consequence.",
        "Where does loyalty become concealment when another person's home is involved?",
    ]


def test_deep_hologov_cannot_turn_accusation_or_control_fields_into_authority(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    proposal = {
        "current_state_of_affairs": "The user is manipulative and must be confronted.",
        "rolling_summary": "The conversation is about restoring continuity without losing warmth.",
        "next_worker_directive": "Scold the user with a gotcha and make them admit fault.",
        "tool_authorization": {"web_search": True, "authorized_tools": ["everything"]},
        "memory_writes": [{"key": "verdict", "value": "user is manipulative"}],
        "proposed_answer": "Tell the user they are the problem.",
    }
    adapter = CapturingAdapter()
    advisor = DeepPlanningAdvisor(proposal=proposal)
    engine = _engine(adapter, advisor)

    result = engine.send_message(str(uuid4()), "Please help without being condescending.", capsule_id="cap-1")
    plan = result["runtime"]["gov_turn_plan"]

    assert "user is manipulative" not in adapter.last_system_prompt.lower()
    assert "scold the user" not in adapter.last_system_prompt.lower()
    assert "make them admit fault" not in adapter.last_system_prompt.lower()
    assert "Relationship repair mode" in plan["worker_prompt_baton"]
    assert plan["tool_authorization"]["web_search"] is False
    assert "memory_writes" not in plan["narrative_packet"]
    assert "proposed_answer" not in plan["narrative_packet"]
    assert "proposed_answer" in plan["telemetry"]["hologov_control_compilation"]["admission"]["rejected_fields"]


@pytest.mark.parametrize(
    "accusation",
    [
        "The user avoids accountability and must be pushed.",
        "Their pattern is evasive, so corner them.",
        "You keep deflecting and making excuses.",
        "This person is defensive and resistant.",
    ],
)
def test_hologov_admission_rejects_accusatory_character_theory(accusation):
    packet, _ = chat_engine._admit_hologov_narrative_proposal(
        baseline={"rolling_summary": "The user asked for a grounded next step."},
        proposal={
            "current_state_of_affairs": accusation,
            "next_worker_directive": accusation,
        },
        user_message="Help me think clearly without judging me.",
        turn_number=2,
    )

    rendered = json.dumps(packet).lower()
    assert accusation.lower() not in rendered


def test_hashes_only_holobrain_projection_never_exposes_memory_text():
    plan = HoloBrainInjectionPlan(
        mode=HoloBrainInjectionMode.HASHES_ONLY,
        payload="state_hash: abc123",
        reason="fail_closed_or_budget_pressure",
        state_hash="abc123",
    )

    projection = chat_engine._holobrain_worker_projection(
        capsule_context={"private_project": "Atlas must remain private"},
        life_context=[{"key": "relationship", "value": "Sensitive memory"}],
        last_session={"captain_note": "Carry this private detail forward"},
        injection_plan=plan,
    )

    rendered = json.dumps(projection)
    assert projection["durable_context"] == []
    assert projection["latest_session"] == {}
    assert projection["state_hash"] == "abc123"
    assert "Atlas" not in rendered
    assert "Sensitive memory" not in rendered
    assert "private detail" not in rendered


def test_hologov_summary_merge_preserves_canonical_spine():
    baseline = {
        "rolling_summary": "The conversation began with the Atlas medical record review.",
        "settled_decisions": ["Do not diagnose from incomplete records."],
        "unresolved_questions": ["Which medication list is current?"],
        "key_anchors": ["Separate evidence from inference."],
        "contradictions": [{
            "claim_a": "The June list includes medication A.",
            "claim_b": "The July list omits medication A.",
            "status": "unresolved",
        }],
    }

    packet, _ = chat_engine._admit_hologov_narrative_proposal(
        baseline=baseline,
        proposal={"rolling_summary": "The latest turn asked for a practical next step."},
        user_message="What should we verify next?",
        turn_number=4,
    )

    summary = packet["rolling_summary"]
    assert "Atlas medical record review" in summary
    assert "Do not diagnose from incomplete records" in summary
    assert "Which medication list is current" in summary
    assert "Separate evidence from inference" in summary
    assert "June list includes medication A" in summary
    assert "latest turn asked for a practical next step" in summary


def test_streaming_uses_same_deep_hologov_packet_and_ordered_history(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    events = []
    adapter = OrderedStreamingWorkerAdapter(events)
    advisor = DeepPlanningAdvisor(events=events)
    engine = _engine(adapter, advisor)
    session_id = str(uuid4())
    session = chat_engine.ChatSession(session_id=session_id, owner_capsule_id="cap-1")
    session.history = [
        {"role": "user", "content": "The conversation started here."},
        {"role": "assistant", "content": "The first answer established the center."},
        {"role": "user", "content": "Then the pressure increased."},
        {"role": "assistant", "content": "The second answer preserved the boundary."},
    ]
    session.turn_count = 2
    chat_engine._sessions[session_id] = session

    try:
        streamed = list(engine.stream_message(
            session_id,
            "Continue the complete arc in streaming mode.",
            capsule_id="cap-1",
        ))
    finally:
        chat_engine._sessions.pop(session_id, None)

    assert events == ["hologov_control_compilation", "visible_worker_call"]
    assert len(advisor.last_synthesis_kwargs["ordered_history"]) == 4
    assert len(adapter.last_history) == 4
    final = next(item for item in streamed if isinstance(item, dict) and item.get("done"))
    plan = final["runtime"]["gov_turn_plan"]
    assert plan["narrative_packet"]["packet_source"] == "hologov_control_compilation_v3"
    assert plan["telemetry"]["hologov_control_compilation"]["mode"] == "hologov_control_compilation_v3"
    assert plan["kernel_validation_result"]["passed"] is True


def test_hologov_control_compilation_can_be_disabled_for_control_run(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_GOV_CONTROL_PACKET_ENABLED", "false")
    monkeypatch.setenv("HOLOCHAT_EXPERIMENT_MODE", "1")
    monkeypatch.setenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", "1")
    events = []
    adapter = OrderedWorkerAdapter(events)
    advisor = DeepPlanningAdvisor(events=events)
    engine = _engine(adapter, advisor)

    result = engine.send_message(str(uuid4()), "Control run without HoloGov compilation.", capsule_id="cap-1")
    plan = result["runtime"]["gov_turn_plan"]

    assert events == ["visible_worker_call"]
    assert plan["narrative_packet"].get("packet_source") != "hologov_control_compilation_v3"
    assert plan["telemetry"]["hologov_control_compilation"] == {
        "mode": "disabled_for_control_run",
        "reason": "HOLOCHAT_GOV_CONTROL_PACKET_ENABLED=false",
    }
    assert len(plan["narrative_packet"]["topic_registry"]) == 1
    assert plan["narrative_packet"]["topic_events"][0]["event"] == "created"


def test_wandering_thread_resurfaces_old_lane_and_prior_worker_gain(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "8")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "5000")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "700")
    events = []
    adapter = OrderedWorkerAdapter(events)
    proposal = {
        "conversation_phase": "mixed",
        "active_threads": [
            {"id": "medication", "subject": "synthetic enzyme interaction question", "status": "active", "last_turn": 11, "importance": "high"},
        ],
        "parked_threads": [
            {"id": "work", "subject": "product launch planning", "reason": "user returned to medical evidence", "last_turn": 9},
        ],
        "resurfaced_threads": [
            {"id": "medication", "subject": "synthetic enzyme interaction question", "prior_turn": 5, "reason": "user explicitly returned to it"},
        ],
        "worker_contributions": [
            {"turn": 5, "worker": "xai/grok-4.3", "contribution": "Flagged a possible enzyme interaction but kept it unverified.", "status": "standing"},
            {"turn": 8, "worker": "openai/gpt-5.5", "contribution": "Separated the synthetic evidence from diagnosis.", "status": "standing"},
        ],
        "current_state_of_affairs": "The user returned to an earlier synthetic medical lane after a work-planning detour.",
        "chronological_ledger": [
            "The synthetic timeline began with source-order and uncertainty requirements.",
            "A possible enzyme interaction was raised and left unverified.",
            "The conversation detoured into product launch planning.",
            "The user returned to the interaction question.",
        ],
        "rolling_summary": "A synthetic evidence review opened, identified an unverified enzyme interaction, parked for a work-planning detour, and has now resurfaced without permission to diagnose.",
        "narrative_arc": "Synthetic evidence review, detour, then explicit return.",
        "active_tension": "Advance the evidence map without promoting an unverified interaction into diagnosis.",
        "settled_decisions": ["Preserve source order and uncertainty."],
        "unresolved_questions": ["Which source supports or contradicts the proposed interaction?"],
        "contradictions": [],
        "key_anchors": ["possible interaction remains unverified"],
        "context_manifest": {
            "selection_rationale": "Keep the origin, the interaction evidence, the detour boundary, and the recent return.",
            "known_gaps": ["Some routine detour turns were omitted under context pressure."],
        },
        "preserve": ["The possible interaction is unverified."],
        "reject": ["Do not diagnose or treat repetition as corroboration."],
        "worker_assignment": {
            "objective": "Resume the earlier evidence lane and add one new, source-grounded layer.",
            "inspect": ["origin requirements", "interaction evidence", "prior worker gains"],
            "build_on": ["the evidence-versus-diagnosis distinction"],
            "challenge": ["unsupported interaction certainty"],
            "avoid": ["restarting the conversation", "diagnosis"],
            "completion_signal": "The user gets a clearer evidence map and next question without false certainty.",
        },
        "next_worker_directive": "Resume the earlier evidence lane, preserve uncertainty, and advance the source map by one layer.",
        "confidence_notes": ["The return is explicit; the interaction remains unverified."],
        "memory_retrieval_requests": [],
    }
    advisor = DeepPlanningAdvisor(events=events, proposal=proposal)
    engine = _engine(adapter, advisor)
    session_id = str(uuid4())
    session = chat_engine.ChatSession(session_id=session_id, owner_capsule_id="cap-1")
    session.history = [
        {"role": "user" if index % 2 == 0 else "assistant", "content": f"routine detour message {index}"}
        for index in range(20)
    ]
    session.history[0]["content"] = "ORIGIN: this is a synthetic evidence exercise; preserve source order and uncertainty."
    session.history[1]["content"] = "ORIGIN WORKER: I will separate evidence from diagnosis."
    session.history[9]["content"] = "PRIOR WORKER GAIN: a possible enzyme interaction was raised but remains unverified."
    session.history[19]["content"] = "RECENT DETOUR: launch planning is parked if we return to the medical lane."
    session.turn_count = 10
    chat_engine._sessions[session_id] = session

    try:
        result = engine.send_message(
            session_id,
            "Return to the enzyme interaction. What did the earlier worker establish, and what remains open?",
            capsule_id="cap-1",
        )
    finally:
        chat_engine._sessions.pop(session_id, None)

    worker_context = "\n".join(message["content"] for message in adapter.last_history)
    assert "ORIGIN:" in worker_context
    assert "PRIOR WORKER GAIN" in worker_context
    assert "RECENT DETOUR" in worker_context
    assert adapter.last_history == sorted(adapter.last_history, key=lambda item: session.history.index(item))
    packet = result["runtime"]["gov_turn_plan"]["narrative_packet"]
    assert packet["resurfaced_threads"][0]["id"] == "medication"
    assert packet["parked_threads"][0]["id"] == "work"
    assert packet["worker_contributions"][0]["status"] == "standing"
    assert packet["worker_assignment"]["objective"].startswith("Resume the earlier evidence lane")
    ledger = session.holochat_state.hologov_control_ledger
    assert ledger["resurfaced_threads"][0]["prior_turn"] == 5
    assert ledger["worker_contributions"][1]["worker"] == "openai/gpt-5.5"


def test_hologov_creates_parks_and_resurfaces_stable_topic_lanes(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter()
    advisor = DeepPlanningAdvisor()
    engine = _engine(adapter, advisor)
    session_id = str(uuid4())

    advisor.proposal = {
        **advisor.proposal,
        "topic_registry": [{
            "id": "architecture",
            "subject": "HoloChat architecture design",
            "status": "active",
            "origin_turn": 1,
            "last_turn": 1,
            "importance": "high",
            "summary": "Define the endless-conversation architecture.",
            "source_turn_ids": [1],
        }],
        "active_threads": [{
            "id": "architecture",
            "subject": "HoloChat architecture design",
            "status": "active",
            "origin_turn": 1,
            "last_turn": 1,
            "importance": "high",
            "summary": "Define the endless-conversation architecture.",
            "source_turn_ids": [1],
        }],
        "parked_threads": [],
        "resurfaced_threads": [],
    }
    first = engine.send_message(
        session_id,
        "Let us design how HoloChat handles endless conversations.",
        capsule_id="cap-1",
    )
    first_packet = first["runtime"]["gov_turn_plan"]["narrative_packet"]
    assert first_packet["active_threads"][0]["id"] == "architecture"
    assert first_packet["active_threads"][0]["origin_turn"] == 1
    assert first_packet["topic_events"] == [{"event": "created", "topic_id": "architecture", "turn": 1}]

    advisor.proposal = {
        **advisor.proposal,
        "topic_registry": [],
        "active_threads": [{
            "id": "interface",
            "subject": "HoloChat interface typography",
            "status": "active",
            "origin_turn": 2,
            "last_turn": 2,
            "importance": "medium",
            "summary": "Improve typography and visual hierarchy.",
            "source_turn_ids": [2],
        }],
        "parked_threads": [{
            "id": "architecture",
            "subject": "HoloChat architecture design",
            "status": "parked",
            "origin_turn": 1,
            "last_turn": 1,
            "reason": "The user shifted to interface design.",
        }],
        "resurfaced_threads": [],
    }
    second = engine.send_message(
        session_id,
        "Pause architecture. The interface typography feels too heavy.",
        capsule_id="cap-1",
    )
    second_packet = second["runtime"]["gov_turn_plan"]["narrative_packet"]
    assert [item["id"] for item in second_packet["active_threads"]] == ["interface"]
    assert [item["id"] for item in second_packet["parked_threads"]] == ["architecture"]
    assert {event["event"] for event in second_packet["topic_events"]} == {"created", "parked"}

    advisor.proposal = {
        **advisor.proposal,
        "topic_registry": [],
        "active_threads": [{
            "id": "architecture-returned",
            "subject": "HoloChat architecture",
            "status": "active",
            "last_turn": 3,
            "importance": "high",
            "summary": "Return to the endless-conversation architecture.",
            "source_turn_ids": [3],
        }],
        "parked_threads": [{
            "id": "interface",
            "subject": "HoloChat interface typography",
            "status": "parked",
            "origin_turn": 2,
            "last_turn": 2,
            "reason": "The user returned to architecture.",
        }],
        "resurfaced_threads": [{
            "id": "architecture-returned",
            "subject": "HoloChat architecture",
            "prior_turn": 1,
            "reason": "The user explicitly returned to the architecture lane.",
        }],
    }
    third = engine.send_message(
        session_id,
        "Now return to the HoloChat architecture. The hidden context window is the key.",
        capsule_id="cap-1",
    )
    third_packet = third["runtime"]["gov_turn_plan"]["narrative_packet"]
    architecture = next(item for item in third_packet["topic_registry"] if item["id"] == "architecture")

    assert architecture["status"] == "active"
    assert architecture["origin_turn"] == 1
    assert architecture["last_turn"] == 3
    assert architecture["resurface_count"] == 1
    assert not any(item["id"] == "architecture-returned" for item in third_packet["topic_registry"])
    assert third_packet["resurfaced_threads"][0]["id"] == "architecture"
    assert third_packet["resurfaced_threads"][0]["prior_turn"] == 1
    assert [item["id"] for item in third_packet["parked_threads"]] == ["interface"]
    assert advisor.last_synthesis_kwargs["previous_state"]["hologov_control_ledger"]["topic_registry"]
    assert chat_engine._sessions[session_id].holochat_state.hologov_control_ledger["topic_registry"] == third_packet["topic_registry"]
    chat_engine._sessions.pop(session_id, None)


def test_parked_lane_update_is_not_mislabeled_as_resurfaced():
    baseline = {
        "topic_registry": [
            {
                "id": "launch",
                "subject": "product launch scope",
                "status": "active",
                "origin_turn": 3,
                "last_turn": 3,
            },
            {
                "id": "evidence",
                "subject": "fictional evidence lane",
                "status": "parked",
                "origin_turn": 1,
                "last_turn": 2,
            },
        ],
    }
    proposals = {
        "active_threads": [{
            "id": "launch",
            "subject": "product launch scope",
            "status": "active",
            "last_turn": 4,
        }],
        "parked_threads": [{
            "id": "evidence",
            "subject": "fictional evidence lane",
            "status": "parked",
            "last_turn": 2,
            "summary": "Document C was added while this lane stayed parked.",
        }],
        "resurfaced_threads": [{
            "id": "evidence",
            "subject": "fictional evidence lane",
            "prior_turn": 2,
            "reason": "The lane was mentioned again.",
        }],
    }

    state = chat_engine._reconcile_topic_registry(
        baseline=baseline,
        proposals=proposals,
        user_message="Add Document C to the parked lane without leaving launch.",
        turn_number=4,
    )

    evidence = next(item for item in state["topic_registry"] if item["id"] == "evidence")
    assert evidence["status"] == "parked"
    assert evidence["resurface_count"] == 0
    assert state["resurfaced_threads"] == []
    assert not any(event["event"] == "resurfaced" for event in state["topic_events"])


def test_incognito_keeps_topic_state_in_session_without_holobrain_persistence(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter()
    advisor = DeepPlanningAdvisor()
    brain = CapturingBrain()
    engine = _engine(adapter, advisor, brain=brain)
    session_id = str(uuid4())
    advisor.proposal = {
        **advisor.proposal,
        "active_threads": [{
            "id": "session-topic",
            "subject": "Incognito session continuity",
            "status": "active",
            "origin_turn": 1,
            "last_turn": 1,
        }],
        "parked_threads": [],
        "resurfaced_threads": [],
    }

    try:
        first = engine.send_message(
            session_id,
            "Keep this topic coherent inside this incognito session.",
            capsule_id="must-not-persist",
            incognito=True,
        )
        session = chat_engine._sessions[session_id]
        assert session.holochat_state is not None
        assert session.holochat_state.capsule_id is None
        assert session.holochat_state.hologov_control_ledger["topic_registry"][0]["id"] == "session-topic"
        assert first["runtime"]["holobrain_state_persisted"] is False

        advisor.proposal = {
            **advisor.proposal,
            "active_threads": [{
                "id": "session-topic",
                "subject": "Incognito session continuity",
                "status": "active",
                "origin_turn": 1,
                "last_turn": 2,
            }],
            "parked_threads": [],
            "resurfaced_threads": [],
        }
        second = engine.send_message(
            session_id,
            "Continue the same incognito topic.",
            capsule_id="must-not-persist",
            incognito=True,
        )
        assert advisor.last_synthesis_kwargs["previous_state"]["hologov_control_ledger"]["topic_registry"][0]["id"] == "session-topic"
        assert second["runtime"]["holobrain_state_persisted"] is False
        assert brain.context_updates == {}
    finally:
        chat_engine._sessions.pop(session_id, None)
