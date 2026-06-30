import json
from dataclasses import dataclass
from types import SimpleNamespace
from uuid import uuid4

import pytest

import chat_engine
import llm_adapters
from chat_engine import (
    ChatSession,
    HoloChatEngine,
    DEFAULT_LOCKED_ARCHITECTURE_PROFILE,
    ResolvedArchitectureProfile,
    THREAD_HANDOFF_MESSAGE,
    _claim_autocompact_for_context_window,
    _handoff_for_context_window,
    _save_thread_handoff_artifact,
    _safe_handoff_transition,
    _thread_handoff_markdown,
    _runtime_metadata,
    _select_runtime_pools,
)
from holo_state import GovArcState
from llm_adapters import (
    AnthropicAdapter,
    GOVERNOR_SYSTEM_PROMPT,
    HOLO_CHAT_SYSTEM_PROMPT,
    _api_key_header_invalid_reason,
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

    def __init__(self, *args, fixed_governor=None, **kwargs):
        self.fixed_governor = fixed_governor

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


class TenorGovernor(FakeGovernor):
    def assess_tenor(self, history, capsule_context, **kwargs):
        return "Stay personal, sharp, and specific; preserve the Holo voice."


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


class CapturingAdapter(FakeAdapter):
    last_system_prompt: str = ""
    last_history: list | None = None

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


def _mini_pool():
    return [
        FakeAdapter("openai", "gpt-4o-mini"),
        FakeAdapter("anthropic", "claude-haiku-4-5-20251001"),
        FakeAdapter("google", "gemini-2.5-flash-lite"),
        FakeAdapter("xai", "grok-3-mini"),
        FakeAdapter("mistral", "mistral-small-latest"),
    ]


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        ("sk-ok_123-ABC", None),
        ("sk-bad—dash", "non_ascii"),
        (" sk-bad", "surrounding_whitespace"),
        ("sk-bad value", "embedded_whitespace"),
        ("sk-bad\nvalue", "embedded_whitespace"),
    ],
)
def test_api_key_header_validation_rejects_values_that_crash_httpx(value, reason):
    assert _api_key_header_invalid_reason(value) == reason


def test_load_adapters_skips_malformed_api_keys_without_leaking_value(monkeypatch, caplog):
    bad_key = "sk-test—copied-comment"
    monkeypatch.setenv("BAD_API_KEY", bad_key)
    monkeypatch.setattr(
        llm_adapters,
        "_MODEL_REGISTRY",
        [("bench", "badprovider", "BAD_MODEL", "bad-model", "BAD_API_KEY", "https://example.test/v1")],
    )

    active, bench = llm_adapters.load_adapters()

    assert active == []
    assert bench == []
    assert "BAD_API_KEY is malformed" in caplog.text
    assert bad_key not in caplog.text


def test_default_runtime_profile_loads_locked_manifest(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_ARCHITECTURE_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_PROVIDER_ROTATION", raising=False)
    frontier_active = [
        FakeAdapter("openai", "gpt-5.4"),
        FakeAdapter("anthropic", "claude-sonnet-4-6"),
        FakeAdapter("google", "gemini-2.5-pro"),
    ]
    frontier_bench = [
        FakeAdapter("xai", "grok-4.3"),
        FakeAdapter("minimax", "MiniMax-Text-01"),
    ]

    profile, active, bench = _select_runtime_pools(
        fast_loader=lambda: pytest.fail("fast loader should not run by default"),
        frontier_loader=lambda: (frontier_active, frontier_bench),
    )

    assert isinstance(profile, ResolvedArchitectureProfile)
    assert profile.locked_value() == {
        "architecture_profile": "frontier_holo_optimized_opus_gpt55_v1",
        "alignment_profile": "patent_aligned_v4",
        "registry_profile": "full_registry",
        "governor_lane": "HoloGov-B",
    }
    assert profile.source == "locked_manifest"
    assert [(adapter.provider, adapter.model_id) for adapter in active] == [
        ("xai", "grok-4.3"),
        ("openai", "gpt-5.4"),
        ("minimax", "MiniMax-Text-01"),
    ]
    assert [(adapter.provider, adapter.model_id) for adapter in bench] == [
        ("anthropic", "claude-sonnet-4-6"),
        ("google", "gemini-2.5-pro"),
    ]


def test_legacy_mini_only_profile_is_not_a_runtime_selector():
    with pytest.raises(RuntimeError, match="override is disabled"):
        _select_runtime_pools(
            "mini_only",
            frontier_loader=lambda: pytest.fail("frontier loader should not run"),
        )


def test_explicit_locked_profile_uses_manifest_loader(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_ARCHITECTURE_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_PROVIDER_ROTATION", raising=False)
    frontier_active = [
        FakeAdapter("openai", "gpt-5.4"),
        FakeAdapter("anthropic", "claude-sonnet-4-6"),
    ]
    frontier_bench = [
        FakeAdapter("xai", "grok-4.3"),
        FakeAdapter("minimax", "MiniMax-Text-01"),
    ]

    profile, active, bench = _select_runtime_pools(
        DEFAULT_LOCKED_ARCHITECTURE_PROFILE,
        fast_loader=lambda: pytest.fail("fast loader should not run"),
        frontier_loader=lambda: (frontier_active, frontier_bench),
    )

    assert profile.profile_id == DEFAULT_LOCKED_ARCHITECTURE_PROFILE
    assert profile.source == "locked_manifest"
    assert [(adapter.provider, adapter.model_id) for adapter in active] == [
        ("xai", "grok-4.3"),
        ("openai", "gpt-5.4"),
        ("minimax", "MiniMax-Text-01"),
    ]
    assert [(adapter.provider, adapter.model_id) for adapter in bench] == [
        ("anthropic", "claude-sonnet-4-6"),
    ]


def test_legacy_balanced_profile_is_not_a_runtime_selector():
    frontier_active = [FakeAdapter("openai", "gpt-5.4")]
    frontier_bench = [FakeAdapter("xai", "grok-4.3")]

    with pytest.raises(RuntimeError, match="override is disabled"):
        _select_runtime_pools(
            "balanced",
            frontier_loader=lambda: (frontier_active, frontier_bench),
        )


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
        [FakeAdapter("openai", "gpt-5.4"), FakeAdapter("xai", "grok-4.3")],
    )

    assert metadata["runtime_profile"] == "balanced"
    assert metadata["frontier_enabled"] is True
    assert metadata["frontier_assist_enabled"] is True
    assert metadata["fallback_policy"] == "gov_triggered_frontier_assist"
    assert len(metadata["active_pool"]) == 5
    assert len(metadata["bench_pool"]) == 2


def test_holochat_engine_init_uses_frontier_loader(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_ARCHITECTURE_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_PROVIDER_ROTATION", raising=False)
    monkeypatch.delenv("HOLOCHAT_GOVERNOR_PROVIDER", raising=False)
    frontier_active = [
        FakeAdapter("openai", "gpt-5.4"),
        FakeAdapter("anthropic", "claude-opus-4-8"),
    ]
    frontier_bench = [
        FakeAdapter("xai", "grok-4.3"),
        FakeAdapter("minimax", "MiniMax-Text-01"),
    ]
    monkeypatch.setattr(
        chat_engine,
        "load_adapters",
        lambda: (frontier_active, frontier_bench),
    )
    monkeypatch.setattr(
        chat_engine,
        "GovernorAdapter",
        lambda pool, fixed_governor=None: FakeGovernor(fixed_governor=fixed_governor),
    )
    monkeypatch.setattr(chat_engine, "ProjectBrain", FakeBrain)

    engine = HoloChatEngine()

    assert engine._runtime_profile == DEFAULT_LOCKED_ARCHITECTURE_PROFILE
    assert engine._resolved_architecture_profile.locked_value() == {
        "architecture_profile": "frontier_holo_optimized_opus_gpt55_v1",
        "alignment_profile": "patent_aligned_v4",
        "registry_profile": "full_registry",
        "governor_lane": "HoloGov-B",
    }
    assert [(adapter.provider, adapter.model_id) for adapter in engine._adapters] == [
        ("xai", "grok-4.3"),
        ("openai", "gpt-5.4"),
        ("minimax", "MiniMax-Text-01"),
    ]
    assert [(adapter.provider, adapter.model_id) for adapter in engine._bench] == [
        ("anthropic", "claude-opus-4-8"),
    ]
    assert engine._governor.fixed_governor == "openai"
    assert engine._governor.provider == "openai"


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
        "model": "gpt-4o-mini",
    }
    assert result["runtime"]["selected_provider"] == "openai"
    assert result["runtime"]["selected_model"] == "gpt-4o-mini"
    assert result["runtime"]["governor_present"] is True
    assert result["runtime"]["governor_checked_this_turn"] is True
    assert result["runtime"]["governor_mode"] == "active"
    assert result["runtime"]["governor_provider"] == "governor"
    assert result["runtime"]["governor_model"] == "governor-mini"
    assert result["runtime"]["governor_status"] == "checked_this_turn"
    assert result["runtime"]["governor_role"] == "controller_check_layer"
    assert result["runtime"]["context_delivery_mode"] == "capped_ranked_prompt_slice"
    assert result["runtime"]["durable_memory_store"] == "HoloBrain/capsule"
    assert result["runtime"]["memory_delivery_mode"] == "rolling_summary_selected_context"
    assert result["runtime"]["pinned_artifact_policy"] == "refs_by_default_full_fidelity_when_selected"
    assert result["runtime"]["analyst_receives_full_memory"] is False
    assert result["runtime"]["continuity_ledger_mode"] == "active_prompt_structured_private"
    assert result["runtime"]["continuity_ledger_counts"]["open_issues"] == 3
    assert result["runtime"]["continuity_ledger_counts"]["repaired"] == 1
    assert result["runtime"]["continuity_ledger_counts"]["user_continuity"] == 2
    assert result["runtime"]["structured_state_object_mode"] == "active_prompt"
    assert result["runtime"]["baton_pass_mode"] == "active_prompt"
    assert result["runtime"]["holo4dna_mode"] == "off"
    assert result["runtime"]["reseed_present"] is False
    assert result["runtime"]["reseed_mode"] == "off"
    assert result["runtime"]["autoreseed_enabled"] is True
    assert result["runtime"]["auto_compact_enabled"] is True
    assert result["runtime"]["auto_compact_count"] == 0
    assert result["runtime"]["last_auto_compact_turn"] is None
    assert result["runtime"]["reseed_artifact_count"] == 0
    assert result["runtime"]["last_reseed_turn"] is None
    assert result["runtime"]["visible_handoff_min_turns"] == 40
    assert result["runtime"]["visible_handoff_suggested"] is False
    assert result["runtime"]["failover"]["attempted"] is False
    assert result["runtime"]["failover"]["count"] == 0
    assert result["runtime"]["governor_trace"]["temperature"] == "checked"
    assert result["runtime"]["governor_trace"]["web_decision"] == "off"
    assert result["runtime"]["governor_trace"]["web_search"]["attempted"] is False
    assert result["runtime"]["governor_trace"]["web_search"]["provider"] == "tavily"
    assert result["runtime"]["governor_trace"]["claim_check"] == "checked"
    assert result["runtime"]["governor_trace"]["conversation_paths"] == "generated"
    assert result["runtime"]["gov_arc_state_mode"] == "active_prompt"
    assert result["runtime"]["gov_arc_state"]["current_topic"] == "Stay mini."
    assert result["runtime"]["gov_arc_state"]["next_paths"] == result["conversation_paths"]
    voice = result["runtime"]["holo_voice_diagnostics"]
    assert voice["status"] == "attention"
    assert voice["selected_analyst"] == {"provider": "openai", "model": "gpt-4o-mini"}
    assert voice["capsule_attached"] is False
    assert "capsule_not_attached" in voice["risk_flags"]
    assert "captain_brief_absent" in voice["risk_flags"]
    assert voice["block_presence"]["runtime_identity"] is True
    assert voice["block_presence"]["holo_state_object"] is True
    assert voice["block_presence"]["gov_arc_state"] is True
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
    engine._governor = TenorGovernor()
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


def test_streaming_fresh_thread_handoff_seed_reaches_first_turn_prompt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingStreamAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = TenorGovernor()
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
        FakeAdapter("openai", "gpt-5.4"),
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


def test_browser_chat_prompt_includes_runtime_identity_and_capped_memory(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_LIFE_CONTEXT_CHARS", "1200")
    monkeypatch.setenv("HOLOCHAT_CAPSULE_CONTEXT_CHARS", "900")
    monkeypatch.setattr(chat_engine.random, "randrange", lambda size: 0)
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = TenorGovernor()
    engine._brain = MemoryHeavyBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Stay attached.", capsule_id="raw-capsule-id")
    budget_rows = {row["block_name"]: row for row in result["context_budget"]["rows"]}

    assert "HOLOCHAT RUNTIME IDENTITY" in adapter.last_system_prompt
    assert "capsule_attached: true" in adapter.last_system_prompt
    assert "local memory-attached workspace and chat surface" in adapter.last_system_prompt
    assert "HoloChat itself is not the irreversible-action adjudicator" in adapter.last_system_prompt
    assert "HOLO STATE OBJECT" in adapter.last_system_prompt
    assert "ROLLING_SUMMARY" in adapter.last_system_prompt
    assert "BATON_PASS" in adapter.last_system_prompt
    assert "raw-capsule-id" not in adapter.last_system_prompt
    assert "must-not-leak" not in adapter.last_system_prompt
    assert "life-memory-29" not in adapter.last_system_prompt
    assert "[context_budget] omitted" in adapter.last_system_prompt
    assert budget_rows["runtime_identity"]["included"] is True
    assert budget_rows["holo_state_object"]["included"] is True
    assert budget_rows["life_context"]["token_estimate"] < 500
    assert budget_rows["capsule_context"]["token_estimate"] < 400
    assert result["runtime"]["runtime_profile"] == "mini_only"
    assert result["runtime"]["governor_checked_this_turn"] is True
    assert result["runtime"]["governor_role"] == "controller_check_layer"
    assert result["runtime"]["context_delivery_mode"] == "capped_ranked_prompt_slice"
    assert result["runtime"]["memory_delivery_mode"] == "rolling_summary_selected_context"
    assert result["runtime"]["rolling_summary_mode"] == "active_prompt_sliding_window"
    assert result["runtime"]["continuity_ledger_mode"] == "active_prompt_structured_private"
    assert result["runtime"]["analyst_receives_full_memory"] is False
    voice = result["runtime"]["holo_voice_diagnostics"]
    assert voice["capsule_attached"] is True
    assert voice["capsule_context_count"] == 31
    assert voice["selected_gov_context_count"] == 16
    assert voice["life_context_count"] == 30
    assert voice["captain_brief_present"] is True
    assert voice["block_presence"]["runtime_identity"] is True
    assert voice["block_presence"]["holo_state_object"] is True
    assert voice["block_presence"]["capsule_context"] is True
    assert "captain_brief_absent" not in voice["risk_flags"]


def test_second_turn_prompt_includes_private_continuity_ledger(monkeypatch):
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

    first = engine.send_message(session_id, "Map what Gov carries forward.")
    assert first["runtime"]["continuity_ledger_counts"]["open_issues"] == 3

    engine.send_message(session_id, "Now use that carry-forward.")

    assert "CONTINUITY_LEDGER" in adapter.last_system_prompt
    assert "open_issues" in adapter.last_system_prompt
    assert "user_continuity" in adapter.last_system_prompt
    assert "latest user need: Map what Gov carries forward." in adapter.last_system_prompt


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
    assert session.handoff_artifact_count == 1
    assert session.last_handoff_artifact_turn == 16
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

    session.turn_count = 26
    third = _save_thread_handoff_artifact(
        brain,
        capsule_id="capsule-1",
        session=session,
        consolidation={"session_note": {"what_changed": "Changed again"}, "life_context": []},
    )
    assert third == "artifact-1"
    assert session.handoff_artifact_count == 2
    assert session.last_handoff_artifact_turn == 26
    assert len(brain.saved_artifacts) == 2


def test_handoff_prompt_is_once_per_context_window():
    session = ChatSession(session_id="session-1")
    session.turn_count = 40
    session.continuity_ledger = {
        "regressed": ["goal drift: the live objective no longer matches the latest user decision"],
    }
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
    session.turn_count = 30

    assert session.thread_health_level != "RED"
    assert _handoff_for_context_window(session) is None
    assert session.handoff_suggested is False


def test_thread_health_stays_green_for_long_thread_with_preserved_frame():
    session = ChatSession(session_id="session-long")
    session.turn_count = 80
    session.history = [
        {"role": "user", "content": "technical detail " * 500},
        {"role": "assistant", "content": "bounded answer " * 500},
    ] * 40
    session.gov_arc_state = GovArcState(
        user_goal="keep the dashboard blocked until memory passes",
        current_directive="preserve the latest control gate",
        settled_decisions=["HoloBrain diagnostic comes before HoloVerify"],
        confidence="medium",
    )
    session.continuity_ledger = {
        "user_continuity": ["latest user need: keep the control gate closed"],
        "repaired": ["addressed latest turn: memory diagnostics first"],
    }

    assert session.thread_health_level == "GREEN"
    assert session.thread_status == "HEALTHY"


def test_thread_health_yellow_for_missing_live_frame_evidence():
    session = ChatSession(session_id="session-yellow")
    session.turn_count = 3

    assert session.thread_health_level == "YELLOW"
    assert session.thread_status == "CLEANUP_RECOMMENDED"
    assert "missing_live_goal_evidence" in session.thread_health_reasons


def test_thread_health_red_for_proven_continuity_degradation():
    session = ChatSession(session_id="session-red")
    session.turn_count = 3
    session.continuity_ledger = {
        "regressed": ["capsule boundary violation: incognito memory appeared in live context"],
    }

    assert session.thread_health_level == "RED"
    assert session.thread_status == "ROTATION_RECOMMENDED"
    assert "continuity_degradation_signal" in session.thread_health_reasons


def test_autocompact_is_claimed_on_spaced_intervals():
    session = ChatSession(session_id="session-1")
    session.turn_count = 30
    session.continuity_ledger = {
        "still_missing": ["stale decision carry-over: latest constraint missing from Gov read"],
    }

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
    assert session.autocompact_count == 1
    assert session.last_autocompact_turn == 30

    session.turn_count = 39
    too_soon = _claim_autocompact_for_context_window(
        session,
        capsule_id="capsule-1",
        incognito=False,
    )
    assert too_soon is False
    assert session.autocompact_count == 1

    session.turn_count = 40
    third = _claim_autocompact_for_context_window(
        session,
        capsule_id="capsule-1",
        incognito=False,
    )
    assert third is True
    assert session.autocompact_count == 2
    assert session.last_autocompact_turn == 40

    incognito_session = ChatSession(session_id="session-2")
    incognito_session.turn_count = 30
    incognito_session.continuity_ledger = {
        "still_missing": ["stale decision carry-over: latest constraint missing from Gov read"],
    }
    assert _claim_autocompact_for_context_window(
        incognito_session,
        capsule_id="capsule-1",
        incognito=True,
    ) is False


def test_autocompact_can_run_before_visible_handoff_gate():
    session = ChatSession(session_id="session-1")
    session.turn_count = 30
    session.continuity_ledger = {
        "still_missing": ["stale summary: current user constraint not reflected"],
    }

    assert session.thread_health_level == "RED"
    assert _claim_autocompact_for_context_window(
        session,
        capsule_id="capsule-1",
        incognito=False,
    ) is True
    assert session.autocompact_attempted is True
    assert _handoff_for_context_window(session) is None
    assert session.handoff_suggested is False


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


def test_long_thread_history_is_bounded_before_adapter_call(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "4")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "2000")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "500")
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None
    session_id = str(uuid4())
    session = engine.get_or_create_session(session_id)
    session.history = [
        {
            "role": "user" if idx % 2 == 0 else "assistant",
            "content": f"turn-{idx} " + ("x" * 5000),
        }
        for idx in range(40)
    ]
    original_history_count = len(session.history)

    result = engine.send_message(session_id, "Keep this compact.")
    budget_rows = {row["block_name"]: row for row in result["context_budget"]["rows"]}

    assert len(session.history) == original_history_count + 2
    assert adapter.last_history is not None
    assert len(adapter.last_history) <= 4
    assert all(len(message["content"]) <= 503 for message in adapter.last_history)
    assert result["runtime"]["adapter_history_total_messages"] == original_history_count
    assert result["runtime"]["adapter_history_omitted_messages"] == original_history_count - len(adapter.last_history)
    assert result["runtime"]["adapter_history_chars"] <= 2000
    assert budget_rows["recent_session_history"]["reason"] == "bounded adapter history argument"
    assert budget_rows["recent_session_history"]["token_estimate"] < 700
    assert result["runtime"]["usage"]["input_token_estimate"] < 12000


def test_streaming_long_thread_history_is_bounded_before_adapter_call(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "3")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "1500")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "450")
    adapter = CapturingStreamAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None
    session_id = str(uuid4())
    session = engine.get_or_create_session(session_id)
    session.history = [
        {
            "role": "user" if idx % 2 == 0 else "assistant",
            "content": f"stream-turn-{idx} " + ("y" * 5000),
        }
        for idx in range(25)
    ]

    events = list(engine.stream_message(session_id, "Stream compactly."))
    done = events[-1]

    assert done["done"] is True
    assert adapter.last_history is not None
    assert len(adapter.last_history) <= 3
    assert all(len(message["content"]) <= 453 for message in adapter.last_history)
    assert done["runtime"]["adapter_history_total_messages"] == 25
    assert done["runtime"]["adapter_history_omitted_messages"] == 25 - len(adapter.last_history)
    assert done["runtime"]["adapter_history_chars"] <= 1500
    assert done["runtime"]["usage"]["input_token_estimate"] < 12000


def test_context_hard_limit_blocks_before_provider_call(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_CONTEXT_HARD_LIMIT_TOKENS", "1000")
    adapter = CapturingAdapter("openai", "gpt-4o-mini")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    with pytest.raises(RuntimeError, match="context budget exceeded"):
        engine.send_message(str(uuid4()), "This should block before provider.")

    assert adapter.last_history is None
