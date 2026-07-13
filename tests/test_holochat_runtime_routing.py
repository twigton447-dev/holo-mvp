import json
from dataclasses import dataclass
from types import SimpleNamespace
from uuid import uuid4

import pytest

import chat_engine
from chat_engine import (
    ChatSession,
    HoloChatEngine,
    THREAD_HANDOFF_MESSAGE,
    _claim_autocompact_for_context_window,
    _handoff_for_context_window,
    _save_thread_handoff_artifact,
    _safe_handoff_transition,
    _thread_handoff_markdown,
    _runtime_metadata,
    _adapter_candidate_order,
    _select_analyst_adapter,
    _select_runtime_pools,
)
from holochat_context_governor import (
    HOLOCHAT_STATE_CONTEXT_KEY,
    HoloBrainInjectionMode,
    build_holochat_state,
    state_context_value,
)
from holo_state import GovArcState
from llm_adapters import (
    AnthropicAdapter,
    GOVERNOR_SYSTEM_PROMPT,
    HOLO_CHAT_SYSTEM_PROMPT,
    _FAST_MODEL_REGISTRY,
    _MODEL_REGISTRY,
    _normalized_provider_allowlist,
)


@dataclass
class FakeAdapter:
    provider: str
    model_id: str

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        return f"{self.provider} mini answer", 3, 2


class FakeGovernor:
    provider = "governor"
    model_id = "governor-mini"

    def prepare_for_turn(self, adapter):
        self.provider = "governor"

    def lock_to_provider(self, provider):
        self.provider = provider or "governor"

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
        return [
            "Separate the architecture question from the product decision",
            "Map exactly what Gov sees before the analyst responds",
            "Decide which Gov actions must stay deterministic",
        ]


class NoPathGovernor(FakeGovernor):
    def generate_conversation_paths(self, **kwargs):
        return []


class FakeBrain:
    def __init__(self):
        self.saved_artifacts = []

    def load_chat_history(self, session_id):
        return []

    def get_capsule_context(self, capsule_id):
        return {}

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

    def save_artifact(self, **kwargs):
        self.saved_artifacts.append(kwargs)
        return "artifact-1"


class MemoryHeavyBrain(FakeBrain):
    def get_capsule_context(self, capsule_id):
        return {
            "project_holochat": "attached old memory",
            **{f"noise_{idx}": "x" * 1000 for idx in range(30)},
            "_password_hash": "must-not-leak",
        }

    def load_life_context(self, capsule_id):
        return [
            {
                "category": "work",
                "key": f"memory_{idx}",
                "value": f"life-memory-{idx} " + ("y" * 1000),
                "confidence": 0.95,
            }
            for idx in range(30)
        ]


class DurableStateBrain(FakeBrain):
    def __init__(self):
        super().__init__()
        self.persisted_context = {}
        self.seed_state = build_holochat_state(
            session_id="prior-session",
            capsule_id="capsule-1",
            turn_number=8,
            user_message="New goal: recover HoloChat auto-reseed. Do not leak env vars.",
            response_text="Next action is validate the first prompt seed.",
        )

    def get_capsule_context(self, capsule_id):
        return {HOLOCHAT_STATE_CONTEXT_KEY: state_context_value(self.seed_state)}

    def set_capsule_context(self, capsule_id, key, value):
        self.persisted_context[key] = value


class SecretStateBrain(DurableStateBrain):
    def __init__(self):
        super().__init__()
        self.seed_state = build_holochat_state(
            session_id="prior-session",
            capsule_id="capsule-1",
            turn_number=8,
            user_message="New goal: keep continuity. Use OPENAI_API_KEY=sk-testsecret123456789 but do not leak it.",
            response_text="Next action is validate redaction.",
        )


class StableStateBrain(DurableStateBrain):
    def __init__(self):
        super().__init__()
        self.seed_state = build_holochat_state(
            session_id="prior-session",
            capsule_id="capsule-1",
            turn_number=8,
            user_message="New goal: keep the state gate narrow.",
            response_text="ok",
        )

class CapturingAdapter(FakeAdapter):
    last_system_prompt: str = ""
    last_history: list = None

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        self.last_history = list(history)
        return super().chat_call(system_prompt, history, user_message, temperature, images=images)


class CapturingStreamAdapter(CapturingAdapter):
    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        self.last_history = list(history)
        yield f"{self.provider} stream answer"
        yield {"done": True, "in_tok": 4, "out_tok": 3}


class NoUsageAdapter(FakeAdapter):
    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        return "estimated token answer", 0, 0


class FailingAdapter(FakeAdapter):
    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        raise RuntimeError("provider body should not surface")


class RestoredLongHistoryBrain(FakeBrain):
    def load_chat_history(self, session_id):
        history = []
        for idx in range(18):
            history.append({
                "role": "user",
                "content": f"restored user {idx} " + ("old raw transcript " * 120),
            })
            history.append({
                "role": "assistant",
                "content": f"restored assistant {idx} " + ("Randall felt right continuity " * 120),
            })
        return history

    def get_capsule_context(self, capsule_id):
        return {
            "project_holochat_randall_voice_anchor": "Randall felt right; keep HoloChat warm, direct, precise, and non-generic.",
            **{f"noise_{idx}": "n" * 400 for idx in range(12)},
        }

    def load_life_context(self, capsule_id):
        return [
            {
                "category": "work",
                "key": "holochat_context_governor_recovery",
                "value": "[FACT] HoloChat recovery QA must preserve Randall continuity and project-aware voice.",
                "confidence": 0.7,
            },
            *[
                {
                    "category": "patterns",
                    "key": f"generic_high_conf_{idx}",
                    "value": "generic stable memory " + ("x" * 300),
                    "confidence": 0.99,
                    "reinforcement_count": 10,
                }
                for idx in range(12)
            ],
        ]


def _mini_pool(provider_allowlist=None):
    adapters = [
        FakeAdapter("openai", "gpt-5.5"),
        FakeAdapter("xai", "grok-4.3"),
        FakeAdapter("minimax", "MiniMax-M2.5-highspeed"),
    ]
    if provider_allowlist is None:
        return adapters
    allowed = set(provider_allowlist)
    return [adapter for adapter in adapters if adapter.provider in allowed]


def test_default_runtime_profile_is_mini_only(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)

    profile, active, bench = _select_runtime_pools(
        fast_loader=_mini_pool,
        frontier_loader=lambda: pytest.fail("frontier loader should not run by default"),
    )

    assert profile == "mini_only"
    assert [adapter.model_id for adapter in active] == [
        "gpt-5.5",
        "grok-4.3",
        "MiniMax-M2.5-highspeed",
    ]
    assert bench == []


def test_holochat_default_model_provider_allowlist_keeps_minimax_loaded_as_fallback(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_MODEL_PROVIDERS", raising=False)
    seen = {}

    def filtered_fast_loader(provider_allowlist=None):
        seen["provider_allowlist"] = provider_allowlist
        return [
            FakeAdapter(provider, f"{provider}-model")
            for provider in provider_allowlist
        ]

    profile, active, bench = _select_runtime_pools(
        fast_loader=filtered_fast_loader,
        frontier_loader=lambda: pytest.fail("frontier loader should not run by default"),
    )

    assert profile == "mini_only"
    assert seen["provider_allowlist"] == ("openai", "xai", "minimax")
    assert [adapter.provider for adapter in active] == ["openai", "xai", "minimax"]
    assert bench == []


def test_holochat_normal_rotation_skips_minimax_fallback_provider():
    session = ChatSession(session_id="rotation-test")
    adapters = _mini_pool()

    selected = [
        _select_analyst_adapter(session, adapters).provider
        for _ in range(5)
    ]
    order_from_xai = [
        adapter.provider for adapter in _adapter_candidate_order(adapters, adapters[1])
    ]

    assert selected == ["openai", "xai", "openai", "xai", "openai"]
    assert order_from_xai == ["xai", "openai", "minimax"]


def test_holochat_model_provider_allowlist_can_be_overridden(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_MODEL_PROVIDERS", "xai, openai")

    def filtered_fast_loader(provider_allowlist=None):
        return [
            FakeAdapter(provider, f"{provider}-model")
            for provider in provider_allowlist
        ]

    _, active, _ = _select_runtime_pools(
        fast_loader=filtered_fast_loader,
        frontier_loader=lambda: pytest.fail("frontier loader should not run by default"),
    )

    assert [adapter.provider for adapter in active] == ["xai", "openai"]


def test_restored_history_is_bounded_and_recovery_pack_is_telemetered(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "4")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "1800")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "500")
    adapter = CapturingAdapter("openai", "gpt-5.5")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = RestoredLongHistoryBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(
        "restored-session",
        "Why do you feel different after recovery?",
        capsule_id="capsule-1",
    )

    assert 0 < len(adapter.last_history) <= 4
    assert "HOLOBRAIN PINNED MEMORY PACK" in adapter.last_system_prompt
    assert "Randall felt right" in adapter.last_system_prompt
    history = result["context_budget"]["history_context"]
    assert history["raw_history_messages"] == 36
    assert history["bounded_history_messages"] == len(adapter.last_history)
    assert history["omitted_history_messages"] == 36 - len(adapter.last_history)
    assert history["bounded_history_token_estimate"] < history["raw_history_token_estimate"]
    rows = {row["block_name"]: row for row in result["context_budget"]["rows"]}
    assert rows["recent_session_history"]["omitted_history_marker_inserted"] is True
    telemetry = result["runtime"]["context_telemetry"]
    assert telemetry["selected_model"] == {"provider": "openai", "model": "gpt-5.5"}
    assert telemetry["gov_model"] == {"provider": "governor", "model": "governor-mini"}
    assert telemetry["memory_context"]["memory_pack_version"] == "holochat_recovery_pack_v0.1"
    assert telemetry["history_context"]["omitted_history_messages"] == 36 - len(adapter.last_history)
    assert "provider_history_bounded" in telemetry["thread_health"]["reasons"]


def test_holochat_registry_supports_openai_xai_minimax_models():
    standard = {entry[1]: entry[3] for entry in _MODEL_REGISTRY}
    fast = {entry[0]: entry[2] for entry in _FAST_MODEL_REGISTRY}

    assert standard["openai"] == "gpt-5.5"
    assert standard["xai"] == "grok-4.3"
    assert standard["minimax"] == "MiniMax-M2.5-highspeed"
    assert fast["openai"] == "gpt-5.5"
    assert fast["xai"] == "grok-4.3"
    assert fast["minimax"] == "MiniMax-M2.5-highspeed"


def test_holochat_provider_allowlist_normalizes_csv_and_sequences():
    assert _normalized_provider_allowlist("OpenAI, xAI, minimax") == {
        "openai",
        "xai",
        "minimax",
    }
    assert _normalized_provider_allowlist([" openai ", ""]) == {"openai"}
    assert _normalized_provider_allowlist(None) is None


def test_mini_only_does_not_fall_back_to_frontier_when_empty():
    with pytest.raises(RuntimeError, match="frontier fallback is disabled"):
        _select_runtime_pools(
            "mini_only",
            fast_loader=lambda: [],
            frontier_loader=lambda: pytest.fail("frontier loader should not run"),
        )


def test_explicit_frontier_profile_uses_legacy_loader():
    frontier_active = [FakeAdapter("openai", "gpt-5.5")]
    frontier_bench = [FakeAdapter("xai", "grok-4.3")]

    profile, active, bench = _select_runtime_pools(
        "frontier_active",
        fast_loader=lambda: pytest.fail("fast loader should not run"),
        frontier_loader=lambda: (frontier_active, frontier_bench),
    )

    assert profile == "frontier_active"
    assert active == frontier_active
    assert bench == frontier_bench


def test_balanced_profile_uses_mini_pool_with_frontier_assist_pool():
    mini_pool = _mini_pool()
    frontier_active = [FakeAdapter("openai", "gpt-5.5")]
    frontier_bench = [FakeAdapter("xai", "grok-4.3")]

    profile, active, bench = _select_runtime_pools(
        "balanced",
        fast_loader=lambda: mini_pool,
        frontier_loader=lambda: (frontier_active, frontier_bench),
    )

    assert profile == "balanced"
    assert active == mini_pool
    assert bench == frontier_active + frontier_bench


def test_runtime_metadata_reports_mini_only_without_frontier_fallback():
    metadata = _runtime_metadata("mini_only", _mini_pool(), [])

    assert metadata["runtime_profile"] == "mini_only"
    assert metadata["frontier_enabled"] is False
    assert metadata["frontier_assist_enabled"] is False
    assert metadata["fallback_policy"] == "no_frontier_fallback"
    assert metadata["serial_call"] is True
    assert metadata["parallel_fanout"] is False
    assert metadata["bench_pool"] == []


def test_runtime_metadata_reports_balanced_frontier_assist():
    metadata = _runtime_metadata(
        "balanced",
        _mini_pool(),
        [FakeAdapter("openai", "gpt-5.5"), FakeAdapter("xai", "grok-4.3")],
    )

    assert metadata["runtime_profile"] == "balanced"
    assert metadata["frontier_enabled"] is True
    assert metadata["frontier_assist_enabled"] is True
    assert metadata["fallback_policy"] == "gov_triggered_frontier_assist"
    assert len(metadata["active_pool"]) == 3
    assert len(metadata["bench_pool"]) == 2


def test_holochat_engine_init_uses_mini_loader(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    monkeypatch.setattr(chat_engine, "load_fast_adapters", _mini_pool)
    monkeypatch.setattr(
        chat_engine,
        "load_adapters",
        lambda: pytest.fail("frontier loader should not run"),
    )
    monkeypatch.setattr(chat_engine, "GovernorAdapter", lambda pool: FakeGovernor())
    monkeypatch.setattr(chat_engine, "ProjectBrain", FakeBrain)

    engine = HoloChatEngine()

    assert engine._runtime_profile == "mini_only"
    assert [adapter.model_id for adapter in engine._adapters] == [
        "gpt-5.5",
        "grok-4.3",
        "MiniMax-M2.5-highspeed",
    ]
    assert engine._bench == []


def test_browser_chat_path_remains_serial_and_reports_runtime(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = _mini_pool()
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Stay mini.")

    assert result["_provider"] == "openai"
    assert result["response"] == "openai mini answer"
    assert result["conversation_paths"] == [
        "Separate the architecture question from the product decision",
        "Map exactly what Gov sees before the analyst responds",
        "Decide which Gov actions must stay deterministic",
    ]
    assert result["runtime"]["runtime_profile"] == "mini_only"
    assert result["runtime"]["serial_call"] is True
    assert result["runtime"]["parallel_fanout"] is False
    assert result["runtime"]["frontier_enabled"] is False
    assert result["runtime"]["frontier_assist"]["enabled"] is False
    assert result["runtime"]["frontier_assist"]["triggered"] is False
    assert result["runtime"]["analyst_pool_role"] == "analyst"
    assert result["runtime"]["analyst_call_mode"] == "serial_one_per_turn"
    assert result["runtime"]["selection_mode"] == "round_robin"
    assert result["runtime"]["active_pool_count"] == len(engine._adapters)
    assert result["runtime"]["active_pool_count"] == len(result["runtime"]["active_pool"])
    assert result["runtime"]["selected_analyst"] == {
        "provider": "openai",
        "model": "gpt-5.5",
    }
    assert result["runtime"]["selected_provider"] == "openai"
    assert result["runtime"]["selected_model"] == "gpt-5.5"
    assert result["runtime"]["governor_present"] is True
    assert result["runtime"]["governor_checked_this_turn"] is True
    assert result["runtime"]["governor_mode"] == "active"
    assert result["runtime"]["governor_provider"] == "governor"
    assert result["runtime"]["governor_model"] == "governor-mini"
    assert result["runtime"]["governor_status"] == "checked_this_turn"
    assert result["runtime"]["governor_role"] == "controller_check_layer"
    assert result["runtime"]["context_delivery_mode"] == "capped_ranked_prompt_slice"
    assert result["runtime"]["lossless_memory_store"] == "HoloBrain/capsule"
    assert result["runtime"]["analyst_receives_full_memory"] is False
    assert result["runtime"]["structured_state_object_mode"] == "active"
    assert result["runtime"]["baton_pass_mode"] == "active"
    assert result["runtime"]["holo4dna_mode"] == "off"
    assert result["runtime"]["reseed_present"] is False
    assert result["runtime"]["reseed_mode"] == "off"
    assert result["runtime"]["autoreseed_enabled"] is True
    assert result["runtime"]["state_object_present"] is True
    assert result["runtime"]["state_object_hash"]
    assert result["runtime"]["baton_hash"]
    assert result["runtime"]["state_audit_trusted"] is True
    assert result["runtime"]["failover"]["attempted"] is False
    assert result["runtime"]["failover"]["count"] == 0
    assert result["runtime"]["governor_trace"]["temperature"] == "checked"
    assert result["runtime"]["governor_trace"]["web_decision"] == "off"
    assert result["runtime"]["governor_trace"]["web_search"]["attempted"] is False
    assert result["runtime"]["governor_trace"]["web_search"]["provider"] == "tavily"
    assert result["runtime"]["governor_trace"]["claim_check"] == "checked"
    assert result["runtime"]["governor_trace"]["conversation_paths"] == "generated"
    assert result["runtime"]["gov_arc_state_mode"] == "active_private"
    assert result["runtime"]["gov_arc_state"]["current_topic"] == "Stay mini."
    assert result["runtime"]["gov_arc_state"]["next_paths"] == result["conversation_paths"]
    assert result["usage"] == result["runtime"]["usage"]
    usage = result["runtime"]["usage"]
    assert usage["input_token_estimate"] == result["context_budget"]["total_token_estimate"]
    assert usage["input_token_source"] == "context_budget_estimate"
    assert usage["output_token_estimate"] == 2
    assert usage["output_token_source"] == "provider_usage"
    assert usage["total_token_estimate"] == usage["input_token_estimate"] + 2
    assert usage["latency_ms"] >= 0
    assert usage["cost_is_estimate"] is True
    assert usage["pricing_note"] == "Exact provider billing may differ."
    timing = result["runtime"]["timing_breakdown"]
    for key in (
        "memory_context_ms",
        "governor_pre_ms",
        "web_search_ms",
        "context_assembly_ms",
        "analyst_ms",
        "governor_post_ms",
        "persistence_ms",
        "total_server_ms",
    ):
        assert timing[key] >= 0
    assert timing["primary_time_owner"] in {
        "memory",
        "governor",
        "web",
        "analyst",
        "persistence",
    }
    assert timing["primary_time_owner_ms"] >= 0
    assert "Safe stage timings only" in timing["note"]
    runtime_text = json.dumps(result["runtime"])
    for forbidden in (
        "raw-capsule-id",
        "capsule_token",
        "cookie",
        "password",
        "supabase",
        "secret",
    ):
        assert forbidden not in runtime_text.lower()


def test_fresh_thread_handoff_seed_reaches_first_turn_prompt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    transition = {
        "source": "thread_handoff",
        "topic": "mobile continuity controls",
        "goal": "repair the fresh-thread reseed so the next thread remembers the arc",
        "tension": "the welcome note appeared, but the new model turn had no seed",
        "next_paths": [
            "Prove the seed reaches the private prompt",
            "Keep raw transcript out of the request",
            "Show the handoff block in Engine data",
            "Drop this extra path",
        ],
        "raw_prompt": "SHOULD NOT APPEAR",
        "raw_memory": "SHOULD NOT APPEAR",
    }

    result = engine.send_message(
        str(uuid4()),
        "Continue from there.",
        capsule_id="test-capsule",
        handoff_transition=transition,
    )

    assert "THREAD HANDOFF SEED" in adapter.last_system_prompt
    assert "prior_topic: mobile continuity controls" in adapter.last_system_prompt
    assert "prior_goal: repair the fresh-thread reseed" in adapter.last_system_prompt
    assert "unresolved_tension: the welcome note appeared" in adapter.last_system_prompt
    assert "Prove the seed reaches the private prompt" in adapter.last_system_prompt
    assert "Drop this extra path" not in adapter.last_system_prompt
    assert "SHOULD NOT APPEAR" not in adapter.last_system_prompt
    assert "raw_prompt" not in adapter.last_system_prompt
    assert result["runtime"]["reseed_present"] is True
    assert result["runtime"]["reseed_mode"] == "thread_handoff_seed"
    assert result["runtime"]["thread_handoff_seed_present"] is True
    assert result["runtime"]["autoreseed_enabled"] is True
    assert result["runtime"]["gov_arc_state"]["current_tension"] == transition["tension"]
    assert result["runtime"]["gov_arc_state"]["user_goal"] == transition["goal"]
    handoff_rows = [
        row for row in result["context_budget"]["rows"]
        if row["block_name"] == "thread_handoff_seed"
    ]
    assert handoff_rows and handoff_rows[0]["included"] is True


def test_durable_state_auto_reseed_reaches_first_turn_prompt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    brain = DurableStateBrain()
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = brain
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Continue.", capsule_id="capsule-1")

    assert "HOLOCHAT AUTO-RESEED" in adapter.last_system_prompt
    assert "recover HoloChat auto-reseed" in adapter.last_system_prompt
    assert "OPENAI_API_KEY" not in adapter.last_system_prompt
    assert result["runtime"]["reseed_present"] is True
    assert result["runtime"]["reseed_mode"] == "durable_state_auto_reseed"
    assert result["runtime"]["durable_state_auto_reseed_present"] is True
    assert result["runtime"]["holobrain_injection_mode"] == HoloBrainInjectionMode.FULL_RESEED.value
    assert result["runtime"]["holobrain_injected_chars"] > 0
    assert result["runtime"]["holobrain_injected_token_estimate"] > 0
    assert result["runtime"]["state_object_present"] is True
    assert HOLOCHAT_STATE_CONTEXT_KEY in brain.persisted_context
    reseed_rows = [
        row for row in result["context_budget"]["rows"]
        if row["block_name"] == "holochat_state_object"
    ]
    assert reseed_rows and reseed_rows[0]["included"] is True
    assert reseed_rows[0]["injection_mode"] == HoloBrainInjectionMode.FULL_RESEED.value
    assert reseed_rows[0]["char_count"] == result["runtime"]["holobrain_injected_chars"]
    assert reseed_rows[0]["token_estimate"] == result["runtime"]["holobrain_injected_token_estimate"]
    assert result["context_budget"]["holobrain_injection"]["mode"] == HoloBrainInjectionMode.FULL_RESEED.value


def test_holobrain_baton_only_on_normal_turn_reaches_prompt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None
    session_id = str(uuid4())

    first = engine.send_message(session_id, "New goal: preserve HoloBrain baton state.")
    second = engine.send_message(session_id, "Continue.")

    assert first["runtime"]["holobrain_injection_mode"] == HoloBrainInjectionMode.NONE.value
    assert "HOLOGOV-C HOLOBRAIN BATON" in adapter.last_system_prompt
    assert "HOLOCHAT AUTO-RESEED" not in adapter.last_system_prompt
    assert second["runtime"]["holobrain_injection_mode"] == HoloBrainInjectionMode.BATON_ONLY.value
    assert second["runtime"]["reseed_present"] is False
    assert second["runtime"]["durable_state_auto_reseed_present"] is False
    row = next(
        row for row in second["context_budget"]["rows"]
        if row["block_name"] == "holochat_state_object"
    )
    assert row["included"] is True
    assert row["injection_mode"] == HoloBrainInjectionMode.BATON_ONLY.value


def test_holobrain_private_state_not_user_visible(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = DurableStateBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Continue.", capsule_id="capsule-1")

    assert "HOLOGOV-C HOLOBRAIN" in adapter.last_system_prompt or "HOLOCHAT AUTO-RESEED" in adapter.last_system_prompt
    assert "HOLOGOV-C HOLOBRAIN" not in result["response"]
    assert "HOLOCHAT AUTO-RESEED" not in result["response"]
    assert "_holochat_state_object" not in result["response"]


def test_holobrain_secret_patterns_do_not_enter_prompt_capture(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = SecretStateBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    engine.send_message(str(uuid4()), "Continue.", capsule_id="capsule-1")

    assert "sk-testsecret" not in adapter.last_system_prompt
    assert "OPENAI_API_KEY=sk" not in adapter.last_system_prompt


def test_durable_holobrain_state_persists_only_on_meaningful_delta(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    brain = StableStateBrain()
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = NoPathGovernor()
    engine._brain = brain
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Continue.", capsule_id="capsule-1")

    assert result["runtime"]["holobrain_state_persisted"] is False
    assert HOLOCHAT_STATE_CONTEXT_KEY not in brain.persisted_context


def test_streaming_fresh_thread_handoff_seed_reaches_first_turn_prompt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingStreamAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    events = list(engine.stream_message(
        str(uuid4()),
        "Pick up the thread.",
        capsule_id="test-capsule",
        handoff_transition={
            "source": "thread_handoff",
            "topic": "Gov doctrine",
            "goal": "make continuity explicit enough to survive a fresh thread",
            "tension": "visual reseed without runtime context is not enough",
            "next_paths": ["Wire prompt context", "Verify Engine data", "Keep it bounded"],
        },
    ))

    assert events[0] == "openai stream answer"
    done = events[-1]
    assert done["done"] is True
    assert "THREAD HANDOFF SEED" in adapter.last_system_prompt
    assert "prior_topic: Gov doctrine" in adapter.last_system_prompt
    assert "visual reseed without runtime context is not enough" in adapter.last_system_prompt
    assert done["runtime"]["reseed_present"] is True
    assert done["runtime"]["reseed_mode"] == "thread_handoff_seed"
    assert done["runtime"]["thread_handoff_seed_present"] is True
    handoff_rows = [
        row for row in done["context_budget"]["rows"]
        if row["block_name"] == "thread_handoff_seed"
    ]
    assert handoff_rows and handoff_rows[0]["included"] is True


def test_streaming_restored_history_is_bounded_and_recovery_pack_is_telemetered(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "4")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "1800")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "500")
    adapter = CapturingStreamAdapter("openai", "gpt-5.5")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = RestoredLongHistoryBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    events = list(engine.stream_message(
        "restored-stream-session",
        "Why do you feel different after recovery?",
        capsule_id="capsule-1",
    ))

    assert events[0] == "openai stream answer"
    assert 0 < len(adapter.last_history) <= 4
    assert "HOLOBRAIN PINNED MEMORY PACK" in adapter.last_system_prompt
    assert "Randall felt right" in adapter.last_system_prompt
    done = events[-1]
    assert done["done"] is True
    history = done["context_budget"]["history_context"]
    assert history["raw_history_messages"] == 36
    assert history["bounded_history_messages"] == len(adapter.last_history)
    assert history["omitted_history_messages"] == 36 - len(adapter.last_history)
    assert history["bounded_history_token_estimate"] < history["raw_history_token_estimate"]
    rows = {row["block_name"]: row for row in done["context_budget"]["rows"]}
    assert rows["recent_session_history"]["omitted_history_marker_inserted"] is True
    telemetry = done["runtime"]["context_telemetry"]
    assert telemetry["selected_model"] == {"provider": "openai", "model": "gpt-5.5"}
    assert telemetry["gov_model"] == {"provider": "governor", "model": "governor-mini"}
    assert telemetry["memory_context"]["memory_pack_version"] == "holochat_recovery_pack_v0.1"
    assert telemetry["history_context"]["omitted_history_messages"] == 36 - len(adapter.last_history)
    assert "provider_history_bounded" in telemetry["thread_health"]["reasons"]


def test_handoff_transition_sanitizer_keeps_only_synthesized_fields():
    safe = _safe_handoff_transition({
        "source": "wrong",
        "topic": "topic",
        "goal": "goal",
        "tension": "tension",
        "next_paths": ["one", "two", "three", "four"],
        "raw_prompt": "no",
        "provider_request_body": "no",
    })

    assert safe == {
        "source": "thread_handoff",
        "topic": "topic",
        "goal": "goal",
        "tension": "tension",
        "next_paths": ["one", "two", "three"],
        "at": "",
    }
    assert _safe_handoff_transition({"raw_prompt": "no"}) is None


def test_pdf_turn_prefers_native_pdf_capable_adapter(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [
        FakeAdapter("openai", "gpt-4o-mini"),
        FakeAdapter("anthropic", "claude-haiku-4-5-20251001"),
        FakeAdapter("google", "gemini-2.5-flash-lite"),
    ]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(
        str(uuid4()),
        "Please read this PDF.",
        images=[{"name": "brief.pdf", "mimeType": "application/pdf", "data": "JVBERi0x"}],
    )

    assert result["_provider"] == "anthropic"
    assert result["response"] == "anthropic mini answer"
    assert result["runtime"]["selected_provider"] == "anthropic"
    assert result["runtime"]["selected_model"] == "claude-haiku-4-5-20251001"
    assert result["runtime"]["failover"]["attempted"] is False
    attachment_rows = [
        row for row in result["context_budget"]["rows"]
        if row["block_name"] == "image_attachments"
    ]
    assert attachment_rows and attachment_rows[0]["included"] is True


class FakeAnthropicStream:
    text_stream = ["streamed answer"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get_final_message(self):
        return SimpleNamespace(
            usage=SimpleNamespace(input_tokens=11, output_tokens=5)
        )


class FakeAnthropicMessages:
    def __init__(self):
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeAnthropicStream()


def test_anthropic_pdf_stream_uses_pdf_beta_endpoint():
    adapter = AnthropicAdapter.__new__(AnthropicAdapter)
    adapter.provider = "anthropic"
    adapter.model_id = "claude-haiku-4-5-20251001"
    regular_messages = FakeAnthropicMessages()
    beta_messages = FakeAnthropicMessages()
    adapter._client = SimpleNamespace(
        messages=regular_messages,
        beta=SimpleNamespace(messages=beta_messages),
    )

    events = list(adapter.stream_chat_call(
        "system",
        [],
        "Please read this.",
        0.2,
        images=[{"name": "brief.pdf", "mimeType": "application/pdf", "data": "JVBERi0x"}],
    ))

    assert events == ["streamed answer", {"done": True, "in_tok": 11, "out_tok": 5}]
    assert regular_messages.calls == []
    assert len(beta_messages.calls) == 1
    call = beta_messages.calls[0]
    assert call["betas"] == ["pdfs-2024-09-25"]
    assert call["messages"][0]["content"][1]["source"]["media_type"] == "application/pdf"


def test_balanced_runtime_uses_frontier_assist_for_complex_turn(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.random, "choice", lambda seq: seq[0])
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._runtime_profile = "balanced"
    engine._adapters = _mini_pool()
    engine._bench = [
        FakeAdapter("openai", "gpt-5.5"),
        FakeAdapter("anthropic", "claude-sonnet-4-6"),
    ]
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("balanced", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Design the HoloChat routing doctrine and architecture.")

    assert result["_provider"] == "anthropic"
    assert result["response"] == "anthropic mini answer"
    assert result["runtime"]["runtime_profile"] == "balanced"
    assert result["runtime"]["frontier_assist_enabled"] is True
    assert result["runtime"]["frontier_assist"] == {
        "enabled": True,
        "triggered": True,
        "reason": "complexity_or_high_stakes",
        "source": "balanced_runtime",
        "selected": {"provider": "anthropic", "model": "claude-sonnet-4-6"},
    }
    assert result["runtime"]["selected_analyst"] == {
        "provider": "anthropic",
        "model": "claude-sonnet-4-6",
    }
    assert result["runtime"]["failover"]["policy"] == "balanced_frontier_assist_then_next_mini"


def test_browser_chat_skips_failed_mini_and_reports_safe_failover(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [
        FailingAdapter("google", "gemini-2.5-flash-lite"),
        FakeAdapter("anthropic", "claude-haiku-4-5-20251001"),
        FakeAdapter("openai", "gpt-4o-mini"),
    ]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Skip outages.")

    assert result["_provider"] == "anthropic"
    assert result["response"] == "anthropic mini answer"
    failover = result["runtime"]["failover"]
    assert failover["attempted"] is True
    assert failover["count"] == 1
    assert failover["initial"] == {"provider": "google", "model": "gemini-2.5-flash-lite"}
    assert failover["final"] == {
        "provider": "anthropic",
        "model": "claude-haiku-4-5-20251001",
    }
    assert failover["skipped"] == [
        {
            "provider": "google",
            "model": "gemini-2.5-flash-lite",
            "error_type": "RuntimeError",
        }
    ]
    runtime_text = json.dumps(result["runtime"]).lower()
    assert "provider body should not surface" not in runtime_text
    assert ("raw " + "prompt") not in runtime_text


def test_browser_chat_uses_minimax_only_after_primary_failures(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [
        FailingAdapter("openai", "gpt-5.5"),
        FailingAdapter("xai", "grok-4.3"),
        FakeAdapter("minimax", "MiniMax-M2.5-highspeed"),
    ]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Use fallback if primaries are out.")

    assert result["_provider"] == "minimax"
    assert result["response"] == "minimax mini answer"
    failover = result["runtime"]["failover"]
    assert failover["attempted"] is True
    assert failover["count"] == 2
    assert failover["initial"] == {"provider": "openai", "model": "gpt-5.5"}
    assert failover["final"] == {
        "provider": "minimax",
        "model": "MiniMax-M2.5-highspeed",
    }
    assert failover["skipped"] == [
        {
            "provider": "openai",
            "model": "gpt-5.5",
            "error_type": "RuntimeError",
        },
        {
            "provider": "xai",
            "model": "grok-4.3",
            "error_type": "RuntimeError",
        },
    ]


def test_browser_chat_prompt_includes_runtime_identity_and_capped_memory(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_LIFE_CONTEXT_CHARS", "1200")
    monkeypatch.setenv("HOLOCHAT_CAPSULE_CONTEXT_CHARS", "900")
    monkeypatch.setattr(chat_engine.random, "randrange", lambda size: 0)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = MemoryHeavyBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Stay attached.", capsule_id="raw-capsule-id")
    budget_rows = {row["block_name"]: row for row in result["context_budget"]["rows"]}

    assert "HOLOCHAT RUNTIME IDENTITY" in adapter.last_system_prompt
    assert "capsule_attached: true" in adapter.last_system_prompt
    assert "local memory-attached workspace and chat surface" in adapter.last_system_prompt
    assert "HoloChat itself is not the irreversible-action adjudicator" in adapter.last_system_prompt
    assert "raw-capsule-id" not in adapter.last_system_prompt
    assert "must-not-leak" not in adapter.last_system_prompt
    assert "life-memory-29" not in adapter.last_system_prompt
    assert "[context_budget] omitted" in adapter.last_system_prompt
    assert budget_rows["runtime_identity"]["included"] is True
    assert budget_rows["life_context"]["token_estimate"] < 500
    assert budget_rows["capsule_context"]["token_estimate"] < 400
    assert result["runtime"]["runtime_profile"] == "mini_only"
    assert result["runtime"]["governor_checked_this_turn"] is True
    assert result["runtime"]["governor_role"] == "controller_check_layer"
    assert result["runtime"]["context_delivery_mode"] == "capped_ranked_prompt_slice"
    assert result["runtime"]["analyst_receives_full_memory"] is False


def test_currentness_query_forces_web_search_without_gov_gate(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("TAVILY_API_KEY", "present-but-not-printed")
    captured = {}

    def fake_search(query):
        captured["query"] = query
        return "Source: https://example.test\nTitle: Current result\nshort"

    monkeypatch.setattr(chat_engine.web_search, "search", fake_search)
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = _mini_pool()
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "What is the latest HoloChat deploy status?")

    assert captured["query"] == "What is the latest HoloChat deploy status?"
    assert result["searched"] is True
    assert result["web_status"] == "checked"
    web_trace = result["runtime"]["governor_trace"]["web_search"]
    assert web_trace["decision"] == "forced_currentness_trigger"
    assert web_trace["source"] == "deterministic"
    assert web_trace["attempted"] is True
    assert web_trace["status"] == "checked"
    assert web_trace["result_count"] == 1
    assert web_trace["unavailable_reason"] is None
    assert result["runtime"]["gov_arc_state"]["web_decision"] == "checked via deterministic"


def test_prompt_assembly_loads_canonical_doctrine_docs():
    assert "Canonical HoloChat Doctrine" in HOLO_CHAT_SYSTEM_PROMPT
    assert "HoloChat is not omniscient." in HOLO_CHAT_SYSTEM_PROMPT
    assert "Use short bold section headers" in HOLO_CHAT_SYSTEM_PROMPT
    assert "Stay warm and human" in HOLO_CHAT_SYSTEM_PROMPT
    assert "I want you to do a deep calibration pass on me." in HOLO_CHAT_SYSTEM_PROMPT
    assert "inspiring, creative, pragmatic, and hopeful" in HOLO_CHAT_SYSTEM_PROMPT
    assert "No bullets. No headers." not in HOLO_CHAT_SYSTEM_PROMPT
    assert "Gov continuity comes from Holo-owned state" in GOVERNOR_SYSTEM_PROMPT
    assert "Python enforces." in GOVERNOR_SYSTEM_PROMPT
    assert "Gov should push harder than a normal assistant." in GOVERNOR_SYSTEM_PROMPT
    assert "at least one path should be a pressure path" in GOVERNOR_SYSTEM_PROMPT


def test_thread_handoff_markdown_is_clean_reseed_not_raw_chat():
    session = ChatSession(session_id="session-1")
    session.history = [
        {"role": "user", "content": "raw user details should stay in chat"},
        {"role": "assistant", "content": "raw assistant answer should stay in chat"},
    ]
    session.gov_arc_state = GovArcState(
        last_gov_read="Gov read the thread arc.",
        next_paths=["Decide the storage boundary", "Inspect the source tether"],
    )
    consolidation = {
        "session_note": {
            "what_changed": "The architecture moved toward clean handoff artifacts.",
            "what_surfaced": "Raw chat and synthesis should have different jobs.",
            "open_threads": ["make the reseed retrievable", "avoid raw transcript leakage"],
            "captain_note": "Use the handoff as the next thread seed.",
        },
        "life_context": [
            {
                "key": "memory_architecture_preference",
                "value": "[SELF-DESCRIPTION] Prefers raw records plus clean synthesized artifacts.",
            }
        ],
    }

    markdown = _thread_handoff_markdown(
        session=session,
        consolidation=consolidation,
        gov_arc_state=session.gov_arc_state,
    )

    assert markdown.startswith("# Thread Handoff")
    assert "Raw chat remains the source record" in markdown
    assert "memory_architecture_preference" in markdown
    assert "raw user details should stay in chat" not in markdown
    assert "raw assistant answer should stay in chat" not in markdown


def test_thread_handoff_artifact_is_tethered_to_source_session():
    brain = FakeBrain()
    session = ChatSession(session_id="source-session")
    session.turn_count = 16
    session.gov_arc_state = GovArcState(next_paths=["Use the reseed"])

    artifact_id = _save_thread_handoff_artifact(
        brain,
        capsule_id="capsule-1",
        session=session,
        consolidation={
            "session_note": {
                "what_changed": "Changed",
                "what_surfaced": "Surfaced",
                "open_threads": ["Open loop"],
                "captain_note": "Carry this forward.",
            },
            "life_context": [],
        },
    )

    assert artifact_id == "artifact-1"
    assert session.handoff_artifact_saved is True
    assert brain.saved_artifacts == [
        {
            "capsule_id": "capsule-1",
            "session_id": "source-session",
            "turn_number": 16,
            "title": "Thread handoff reseed",
            "content": brain.saved_artifacts[0]["content"],
            "artifact_type": "thread_handoff_md",
        }
    ]
    assert "Open loop" in brain.saved_artifacts[0]["content"]

    second = _save_thread_handoff_artifact(
        brain,
        capsule_id="capsule-1",
        session=session,
        consolidation={"session_note": {}, "life_context": []},
    )
    assert second is None
    assert len(brain.saved_artifacts) == 1


def test_handoff_prompt_is_once_per_context_window():
    session = ChatSession(session_id="session-1")
    session.turn_count = 24
    session.gov_arc_state = GovArcState(
        current_topic="mobile controls and reseed continuity",
        user_goal="make the fresh thread feel continuous",
        current_tension="avoid generic transition copy",
        next_paths=["carry the source arc into the welcome"],
    )

    first = _handoff_for_context_window(session)
    second = _handoff_for_context_window(session)

    assert first["suggested"] is True
    assert first["message"] == THREAD_HANDOFF_MESSAGE
    assert first["new_thread"] == "/chat"
    assert first["arc"] == {
        "topic": "mobile controls and reseed continuity",
        "goal": "make the fresh thread feel continuous",
        "tension": "avoid generic transition copy",
        "next_paths": ["carry the source arc into the welcome"],
    }
    assert second is None
    assert session.handoff_suggested is True


def test_handoff_prompt_waits_past_initial_red_zone():
    session = ChatSession(session_id="session-1")
    session.turn_count = 16

    assert session.thread_health_level == "RED"
    assert _handoff_for_context_window(session) is None
    assert session.handoff_suggested is False


def test_autocompact_is_claimed_once_per_context_window():
    session = ChatSession(session_id="session-1")
    session.turn_count = 24

    first = _claim_autocompact_for_context_window(
        session,
        capsule_id="capsule-1",
        incognito=False,
    )
    second = _claim_autocompact_for_context_window(
        session,
        capsule_id="capsule-1",
        incognito=False,
    )

    assert first is True
    assert second is False
    assert session.autocompact_attempted is True

    incognito_session = ChatSession(session_id="session-2")
    incognito_session.turn_count = 24
    assert _claim_autocompact_for_context_window(
        incognito_session,
        capsule_id="capsule-1",
        incognito=True,
    ) is False


def test_autocompact_waits_with_visible_handoff_gate():
    session = ChatSession(session_id="session-1")
    session.turn_count = 16

    assert session.thread_health_level == "RED"
    assert _claim_autocompact_for_context_window(
        session,
        capsule_id="capsule-1",
        incognito=False,
    ) is False
    assert session.autocompact_attempted is False


def test_usage_metadata_falls_back_to_estimates_when_provider_usage_unavailable(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.random, "randrange", lambda size: 0)
    adapter = NoUsageAdapter("unknown_provider", "unknown-model")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Estimate this.")
    usage = result["runtime"]["usage"]

    assert usage["input_token_estimate"] == result["context_budget"]["total_token_estimate"]
    assert usage["input_token_source"] == "context_budget_estimate"
    assert usage["output_token_estimate"] > 0
    assert usage["output_token_source"] == "estimated_chars"
    assert usage["total_token_estimate"] == usage["input_token_estimate"] + usage["output_token_estimate"]
    assert usage["latency_ms"] >= 0
    assert usage["estimated_cost_usd"] is None
    assert usage["cost_source"] == "unknown_pricing"
    assert usage["cost_is_estimate"] is True

    runtime_text = json.dumps(result["runtime"]).lower()
    assert ("actual " + "billed cost") not in runtime_text
    assert ("raw " + "prompt") not in runtime_text
    assert ("raw " + "memory") not in runtime_text
