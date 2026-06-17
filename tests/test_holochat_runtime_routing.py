from dataclasses import dataclass
from uuid import uuid4

import pytest

import chat_engine
from chat_engine import (
    HoloChatEngine,
    _runtime_metadata,
    _select_runtime_pools,
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


class FakeBrain:
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


def _mini_pool():
    return [
        FakeAdapter("openai", "gpt-4o-mini"),
        FakeAdapter("anthropic", "claude-haiku-4-5-20251001"),
        FakeAdapter("google", "gemini-2.0-flash"),
        FakeAdapter("xai", "grok-3-mini"),
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
        "gemini-2.0-flash",
        "grok-3-mini",
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
        "gemini-2.0-flash",
        "grok-3-mini",
    ]
    assert engine._bench == []


def test_browser_chat_path_remains_serial_and_reports_runtime(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setattr(chat_engine.random, "randrange", lambda size: 0)
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
    assert result["runtime"]["runtime_profile"] == "mini_only"
    assert result["runtime"]["serial_call"] is True
    assert result["runtime"]["parallel_fanout"] is False
    assert result["runtime"]["frontier_enabled"] is False


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
    assert "capsule_attached_via_token: true" in adapter.last_system_prompt
    assert "raw-capsule-id" not in adapter.last_system_prompt
    assert "must-not-leak" not in adapter.last_system_prompt
    assert "life-memory-29" not in adapter.last_system_prompt
    assert "[context_budget] omitted" in adapter.last_system_prompt
    assert budget_rows["runtime_identity"]["included"] is True
    assert budget_rows["life_context"]["token_estimate"] < 500
    assert budget_rows["capsule_context"]["token_estimate"] < 400
    assert result["runtime"]["runtime_profile"] == "mini_only"
