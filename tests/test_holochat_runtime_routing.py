import json
from dataclasses import dataclass
from uuid import uuid4

import pytest

import chat_engine
from chat_engine import (
    ChatSession,
    HoloChatEngine,
    _save_thread_handoff_artifact,
    _thread_handoff_markdown,
    _runtime_metadata,
    _select_runtime_pools,
)
from holo_state import GovArcState
from llm_adapters import GOVERNOR_SYSTEM_PROMPT, HOLO_CHAT_SYSTEM_PROMPT


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

    def chat_call(self, system_prompt, history, user_message, temperature, images=None):
        self.last_system_prompt = system_prompt
        return super().chat_call(system_prompt, history, user_message, temperature, images=images)


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


def test_default_runtime_profile_is_mini_only(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)

    profile, active, bench = _select_runtime_pools(
        fast_loader=_mini_pool,
        frontier_loader=lambda: pytest.fail("frontier loader should not run by default"),
    )

    assert profile == "mini_only"
    assert [adapter.model_id for adapter in active] == [
        "gpt-4o-mini",
        "claude-haiku-4-5-20251001",
        "gemini-2.5-flash-lite",
        "grok-3-mini",
        "mistral-small-latest",
    ]
    assert bench == []


def test_mini_only_does_not_fall_back_to_frontier_when_empty():
    with pytest.raises(RuntimeError, match="frontier fallback is disabled"):
        _select_runtime_pools(
            "mini_only",
            fast_loader=lambda: [],
            frontier_loader=lambda: pytest.fail("frontier loader should not run"),
        )


def test_explicit_frontier_profile_uses_legacy_loader():
    frontier_active = [FakeAdapter("openai", "gpt-5.4")]
    frontier_bench = [FakeAdapter("xai", "grok-3")]

    profile, active, bench = _select_runtime_pools(
        "frontier_active",
        fast_loader=lambda: pytest.fail("fast loader should not run"),
        frontier_loader=lambda: (frontier_active, frontier_bench),
    )

    assert profile == "frontier_active"
    assert active == frontier_active
    assert bench == frontier_bench


def test_runtime_metadata_reports_mini_only_without_frontier_fallback():
    metadata = _runtime_metadata("mini_only", _mini_pool(), [])

    assert metadata["runtime_profile"] == "mini_only"
    assert metadata["frontier_enabled"] is False
    assert metadata["fallback_policy"] == "no_frontier_fallback"
    assert metadata["serial_call"] is True
    assert metadata["parallel_fanout"] is False
    assert metadata["bench_pool"] == []


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
        "gpt-4o-mini",
        "claude-haiku-4-5-20251001",
        "gemini-2.5-flash-lite",
        "grok-3-mini",
        "mistral-small-latest",
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
    assert result["runtime"]["lossless_memory_store"] == "HoloBrain/capsule"
    assert result["runtime"]["analyst_receives_full_memory"] is False
    assert result["runtime"]["structured_state_object_mode"] == "shadow"
    assert result["runtime"]["baton_pass_mode"] == "shadow"
    assert result["runtime"]["holo4dna_mode"] == "off"
    assert result["runtime"]["reseed_present"] is False
    assert result["runtime"]["reseed_mode"] == "off"
    assert result["runtime"]["autoreseed_enabled"] is False
    assert result["runtime"]["failover"]["attempted"] is False
    assert result["runtime"]["failover"]["count"] == 0
    assert result["runtime"]["governor_trace"]["temperature"] == "checked"
    assert result["runtime"]["governor_trace"]["web_decision"] == "off"
    assert result["runtime"]["governor_trace"]["web_search"]["attempted"] is False
    assert result["runtime"]["governor_trace"]["web_search"]["provider"] == "tavily"
    assert result["runtime"]["governor_trace"]["claim_check"] == "checked"
    assert result["runtime"]["governor_trace"]["conversation_paths"] == "generated"
    assert result["runtime"]["gov_arc_state_mode"] == "explicit_shadow"
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
    assert "Gov continuity comes from Holo-owned state" in GOVERNOR_SYSTEM_PROMPT
    assert "Python enforces." in GOVERNOR_SYSTEM_PROMPT


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
