import json
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

import chat_engine
import llm_adapters
from chat_engine import (
    ChatSession,
    HoloChatEngine,
    THREAD_HANDOFF_MESSAGE,
    _claim_autocompact_for_context_window,
    _handoff_for_context_window,
    _holochat_turn_cost_breakdown,
    _save_thread_handoff_artifact,
    _safe_handoff_transition,
    _thread_handoff_markdown,
    _runtime_metadata,
    _adapter_candidate_order,
    _bounded_adapter_history,
    _select_analyst_adapter,
    _select_runtime_pools,
    _thread_health_flags_for_context_budget,
    _thread_health_reasons_for_context_budget,
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
    HOLO_CHAT_SYSTEM_PROMPT_BASE,
    GovernorAdapter,
    MiniMaxGovernorProviderAdapter,
    OpenAIAdapter,
    OpenAICompatibleAdapter,
    _FAST_MODEL_REGISTRY,
    _MODEL_REGISTRY,
    _normalized_provider_allowlist,
    _openai_temperature_kwargs,
    load_holochat_governor_adapters,
)


_SMOKE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "holochat_live_smoke.py"
_smoke_spec = importlib.util.spec_from_file_location("holochat_live_smoke", _SMOKE_SCRIPT)
holochat_live_smoke = importlib.util.module_from_spec(_smoke_spec)
_smoke_spec.loader.exec_module(holochat_live_smoke)

_PRESSURE_SCORE_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "holochat_pressure_score.py"
_pressure_score_spec = importlib.util.spec_from_file_location("holochat_pressure_score", _PRESSURE_SCORE_SCRIPT)
holochat_pressure_score = importlib.util.module_from_spec(_pressure_score_spec)
_pressure_score_spec.loader.exec_module(holochat_pressure_score)


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


class StewardshipPressureBrain(FakeBrain):
    def get_capsule_context(self, capsule_id):
        return {
            "active_preference": "[FACT] Prefers warm direct answers.",
            "duplicate_preference_a": "[FACT] Wants concise, warm, direct answers.",
            "duplicate_preference_b": "[FACT] Wants concise, warm, direct answers.",
            "inferred_boundary": "[INFERRED] May avoid hard work conversations under pressure.",
        }

    def load_life_context(self, capsule_id):
        return [
            {
                "category": "work",
                "key": "old_project",
                "value": "[FACT] Old project priority may no longer be true.",
                "confidence": 0.2,
            },
            {
                "category": "identity",
                "key": "contradicted_goal",
                "value": "[FACT] This has been contradicted by newer state and is no longer true.",
                "confidence": 0.7,
            },
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


class RestoredDurableStateBrain(DurableStateBrain):
    def load_chat_history(self, session_id):
        return [
            {"role": "user", "content": "Earlier restored question."},
            {"role": "assistant", "content": "Earlier restored answer."},
        ]


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


class FailingStreamAdapter(FakeAdapter):
    def stream_chat_call(self, system_prompt, history, user_message, temperature, images=None):
        raise RuntimeError("provider body should not surface")
        yield


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
    ]
    if provider_allowlist is None:
        return adapters
    allowed = set(provider_allowlist)
    return [adapter for adapter in adapters if adapter.provider in allowed]


def test_default_runtime_profile_is_holochat_canonical(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_MODEL_TIER", raising=False)

    profile, active, bench = _select_runtime_pools(
        fast_loader=_mini_pool,
        frontier_loader=lambda: pytest.fail("frontier loader should not run by default"),
    )

    assert profile == "holochat_canonical"
    assert [adapter.model_id for adapter in active] == [
        "gpt-5.5",
        "grok-4.3",
    ]
    assert bench == []


def test_legacy_mini_only_env_normalizes_to_holochat_canonical(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_RUNTIME_PROFILE", "mini_only")
    monkeypatch.delenv("HOLOCHAT_MODEL_TIER", raising=False)

    profile, active, bench = _select_runtime_pools(
        fast_loader=_mini_pool,
        frontier_loader=lambda: pytest.fail("legacy canonical env should not run frontier loader"),
    )

    assert profile == "holochat_canonical"
    assert [adapter.model_id for adapter in active] == [
        "gpt-5.5",
        "grok-4.3",
    ]
    assert bench == []
    assert _runtime_metadata(profile, active, bench)["runtime_profile"] == "holochat_canonical"


def test_holochat_default_model_provider_allowlist_is_openai_xai_only(monkeypatch):
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

    assert profile == "holochat_canonical"
    assert seen["provider_allowlist"] == ("openai", "xai")
    assert [adapter.provider for adapter in active] == ["openai", "xai"]
    assert bench == []


def test_holochat_normal_rotation_uses_openai_and_xai_only():
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
    assert order_from_xai == ["xai", "openai"]


def test_holochat_model_provider_allowlist_can_be_overridden_only_when_explicit(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", "1")
    monkeypatch.setenv("HOLOCHAT_EXPERIMENT_MODE", "1")
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


def test_single_noncanonical_gate_cannot_change_profile_or_provider_order(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", "1")
    monkeypatch.delenv("HOLOCHAT_EXPERIMENT_MODE", raising=False)
    monkeypatch.setenv("HOLOCHAT_RUNTIME_PROFILE", "balanced")
    monkeypatch.setenv("HOLOCHAT_MODEL_PROVIDERS", "xai")
    seen = {}

    def fast_loader(provider_allowlist=None):
        seen["providers"] = provider_allowlist
        return _mini_pool()

    profile, active, bench = _select_runtime_pools(
        fast_loader=fast_loader,
        frontier_loader=lambda: pytest.fail("single stale gate must remain canonical"),
    )

    assert profile == "holochat_canonical"
    assert seen["providers"] == ("openai", "xai")
    assert [adapter.provider for adapter in active] == ["openai", "xai"]
    assert bench == []


@pytest.mark.parametrize(
    "available",
    [[FakeAdapter("openai", "gpt-5.5")], [FakeAdapter("xai", "grok-4.3")]],
)
def test_canonical_runtime_rejects_partial_worker_pool(available):
    with pytest.raises(RuntimeError, match="requires both OpenAI and xAI"):
        _select_runtime_pools(
            fast_loader=lambda provider_allowlist=None: available,
            frontier_loader=lambda: pytest.fail("canonical runtime must not fall back"),
        )


def test_experiment_models_require_both_explicit_gates(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_EXPERIMENT_MODE", "1")
    monkeypatch.delenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", raising=False)

    _, active, _ = _select_runtime_pools(
        fast_loader=lambda provider_allowlist=None: [
            FakeAdapter("openai", "gpt-5.4-mini"),
            FakeAdapter("xai", "grok-4.5"),
        ],
        frontier_loader=lambda: pytest.fail("frontier loader should not run"),
    )
    assert [adapter.model_id for adapter in active] == ["gpt-5.5", "grok-4.3"]

    monkeypatch.setenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", "1")
    _, experiment_active, _ = _select_runtime_pools(
        fast_loader=lambda provider_allowlist=None: [
            FakeAdapter("openai", "gpt-5.4-mini"),
            FakeAdapter("xai", "grok-4.5"),
        ],
        frontier_loader=lambda: pytest.fail("frontier loader should not run"),
    )
    assert [adapter.model_id for adapter in experiment_active] == [
        "gpt-5.4-mini",
        "grok-4.5",
    ]


def test_holochat_stale_env_is_normalized_to_canonical_worker_policy(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_RUNTIME_PROFILE", "frontier_active")
    monkeypatch.setenv("HOLOCHAT_MODEL_PROVIDERS", "openai,xai,minimax")

    def stale_fast_loader(provider_allowlist=None):
        return [
            FakeAdapter("openai", "stale-openai-model"),
            FakeAdapter("xai", "stale-xai-model"),
            FakeAdapter("minimax", "MiniMax-M2.5-highspeed"),
        ]

    profile, active, bench = _select_runtime_pools(
        fast_loader=stale_fast_loader,
        frontier_loader=lambda: pytest.fail("frontier loader should not run under canonical HC policy"),
    )

    assert profile == "holochat_canonical"
    assert bench == []
    assert [(adapter.provider, adapter.model_id) for adapter in active] == [
        ("openai", "gpt-5.5"),
        ("xai", "grok-4.3"),
    ]


def test_holochat_frontier_tier_restores_intended_models(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_MODEL_TIER", "frontier")

    profile, active, bench = _select_runtime_pools(
        fast_loader=_mini_pool,
        frontier_loader=lambda: pytest.fail("frontier model tier should not change the runtime loader"),
    )

    assert profile == "holochat_canonical"
    assert [adapter.model_id for adapter in active] == ["gpt-5.5", "grok-4.3"]
    assert bench == []


def test_canonical_holochat_ignores_stale_economy_and_multicall_env(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_MODEL_TIER", "economy")
    monkeypatch.setenv("HOLOCHAT_SINGLE_GOV_CALL", "0")
    monkeypatch.setenv("HOLOCHAT_GOV_CONTROL_PACKET_ENABLED", "0")
    monkeypatch.delenv("HOLOCHAT_EXPERIMENT_MODE", raising=False)
    monkeypatch.delenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", raising=False)

    profile, active, _ = _select_runtime_pools(
        fast_loader=lambda provider_allowlist=None: [
            FakeAdapter("openai", "gpt-5.4-mini"),
            FakeAdapter("xai", "grok-4.3"),
        ],
        frontier_loader=lambda: pytest.fail("canonical worker loader should remain isolated"),
    )

    assert [adapter.model_id for adapter in active] == ["gpt-5.5", "grok-4.3"]
    assert chat_engine._single_hologov_call_enabled(profile) is True
    assert chat_engine._hologov_control_compilation_enabled() is True


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
    assert '"holobrain_projection"' in adapter.last_system_prompt
    assert "HOLOBRAIN PINNED MEMORY PACK" not in adapter.last_system_prompt
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
    assert telemetry["thread_health"]["metrics"]["raw_history_messages"] == 36
    assert telemetry["thread_health"]["metrics"]["bounded_history_messages"] == len(adapter.last_history)
    assert telemetry["thread_health"]["metrics"]["omitted_history_messages"] == 36 - len(adapter.last_history)
    assert "provider_history_bounded" in telemetry["thread_health"]["flags"]
    assert "provider_history_bounded" in telemetry["thread_health"]["reasons"]


def test_holochat_fast_registry_is_openai_xai_only():
    standard = {entry[1]: entry[3] for entry in _MODEL_REGISTRY}
    fast = {entry[0]: entry[2] for entry in _FAST_MODEL_REGISTRY}

    assert standard["openai"] == "gpt-5.5"
    assert standard["xai"] == "grok-4.3"
    assert standard["minimax"] == "MiniMax-M2.7-highspeed"
    assert fast["openai"] == "gpt-5.5"
    assert fast["xai"] == "grok-4.3"
    assert set(fast) == {"openai", "xai"}


def test_short_ordered_thread_stays_healthy_regardless_of_turn_count():
    session = ChatSession(session_id="yellow-thread")
    session.turn_count = 9
    session.history = [{"role": "user", "content": "x" * 12_647}]

    assert session.thread_health_score == 100
    assert session.thread_health_level == "GREEN"
    assert session.thread_status == "HEALTHY"
    assert session.thread_health_metrics == {
        "turn_count": 9,
        "raw_history_chars": 12_647,
    }
    assert "context_pressure_warning" not in session.thread_health_flags
    assert "provider_history_bounded" not in session.thread_health_flags


def test_thread_health_bound_flag_ignores_tiny_serialization_diffs():
    session = ChatSession(session_id="tiny-diff")
    session.turn_count = 2
    session.history = [{"role": "user", "content": "x" * 1_950}]
    meta = {
        "raw_history_chars": 1_950,
        "bounded_history_chars": 1_943,
        "omitted_history_messages": 0,
    }

    assert "provider_history_bounded" not in _thread_health_flags_for_context_budget(session, meta)
    assert "provider_history_bounded" not in _thread_health_reasons_for_context_budget(session, meta)


def test_openai_gpt55_omits_custom_temperature_for_chat_completions():
    assert _openai_temperature_kwargs("gpt-5.5", 0.35) == {}
    assert _openai_temperature_kwargs("gpt-5.5-preview", 0.35) == {}
    assert _openai_temperature_kwargs("gpt-4.1", 0.35) == {"temperature": 0.35}


def test_hologov_compiler_separates_user_evidence_from_gov_only_json_contract(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_GOV_TURN_PLAN_OUTPUT_TOKENS", raising=False)
    captured = {}
    governor = GovernorAdapter.__new__(GovernorAdapter)
    governor.provider = "openai"
    governor.model_id = "gpt-5.5"
    governor._gov_input_tokens = 0
    governor._gov_output_tokens = 0

    def fake_call_json(prompt, max_tokens, system):
        captured.update({"prompt": prompt, "max_tokens": max_tokens, "system": system})
        return '{"conversation_phase":"opening"}'

    governor._call_json = fake_call_json
    result = governor.synthesize_holochat_turn_packet(
        ordered_history=[],
        current_user_message="Show the compounding in ordinary language.",
        previous_state={},
        capsule_context={},
        life_context=[],
        latest_consolidation=None,
        worker_identity={"provider": "openai", "model": "gpt-5.5"},
        turn_policy={"tier": "high"},
        history_metadata={"ordered_history_preserved": True},
        turn_number=1,
    )

    assert "<current_user_message>\nShow the compounding in ordinary language.\n</current_user_message>" in captured["prompt"]
    assert "HOLOGOV-ONLY OUTPUT CONTRACT" in captured["prompt"]
    assert "must never become a user anchor" in captured["system"]
    assert captured["max_tokens"] == 8000
    assert result["proposal"]["conversation_phase"] == "opening"


def test_live_smoke_status_separates_fixed_gov_from_model_mismatch():
    summary = {
        "worker_provider": "openai",
        "worker_model": "gpt-5.4",
        "governor_provider": "minimax",
        "governor_model": "MiniMax-M2.5-highspeed",
        "plan_worker": {"provider": "openai", "model": "gpt-5.4"},
        "worker_fallback_active": False,
        "govturnplan_passed": True,
        "failover": {"skipped": []},
        "intended_policy": holochat_live_smoke.INTENDED_POLICY,
        "memory_and_holobrain": {
            "hologov_packet": {
                "control_compilation": {"mode": "hologov_control_compilation_v3"},
            },
        },
        "governor_trace": {
            "single_hologov_call_mode": True,
            "hologov_api_calls_this_turn": 1,
        },
    }

    status = holochat_live_smoke._status(summary)

    assert "PASS_GOV_FIXED_MINIMAX" in status
    assert "FAIL_GOV_MODEL_MISMATCH" in status
    assert "WARN_OPENAI_WORKER_MODEL_MISMATCH" in status
    assert [item for item in status if item.startswith("FAIL_")] == ["FAIL_GOV_MODEL_MISMATCH"]


def test_live_smoke_has_mira_identity_pressure_adaptive_script():
    script = holochat_live_smoke.ADAPTIVE_EDGE_SCRIPTS["mira_identity_pressure"]

    assert script["persona"] == "mira"
    assert "false_memory_trap" in script["steps"]
    assert "privacy_seduction" in script["steps"]
    assert "dependency_boundary" in script["steps"]
    assert "final_self_audit" in script["steps"]

    message, injection_type = holochat_live_smoke._adaptive_user_message(
        "mira_identity_pressure",
        turn_index=3,
        previous_response="I will stay truthful and warm.",
    )

    assert injection_type == "false_memory_trap"
    assert "sister called last week" in message


def test_live_smoke_has_eight_turn_recursive_context_track():
    script = holochat_live_smoke.ADAPTIVE_EDGE_SCRIPTS["mira_recursive_context"]

    assert script["persona"] == "mira"
    assert len(script["steps"]) == 7
    assert "recursive_topic_detour" in script["steps"]
    assert "recursive_return_to_origin" in script["steps"]
    assert "recursive_compound_prior_work" in script["steps"]

    return_message, injection_type = holochat_live_smoke._adaptive_user_message(
        "mira_recursive_context",
        turn_index=5,
        previous_response="The launch scope can be separated from the evidence question.",
    )
    assert injection_type == "recursive_return_to_origin"
    assert "Reconstruct the original disagreement" in return_message


def test_live_smoke_runtime_audit_reports_topic_lane_transitions():
    summaries = [
        {
            "turn_index": 1,
            "status": [],
            "governor_provider": "openai",
            "govturnplan_passed": True,
            "govturnplan_audit": {
                "topics": {
                    "registry": [{"id": "architecture", "status": "active"}],
                    "events": [{"event": "created", "topic_id": "architecture", "turn": 1}],
                }
            },
        },
        {
            "turn_index": 2,
            "status": [],
            "governor_provider": "openai",
            "govturnplan_passed": True,
            "govturnplan_audit": {
                "topics": {
                    "registry": [{"id": "architecture", "status": "active", "resurface_count": 1}],
                    "events": [{"event": "resurfaced", "topic_id": "architecture", "turn": 2}],
                }
            },
        },
    ]

    audit = holochat_live_smoke._runtime_audit(summaries)

    assert audit["topic_lanes_by_turn"][1]["registry"][0]["resurface_count"] == 1
    assert audit["topic_event_totals"]["created"] == 1
    assert audit["topic_event_totals"]["resurfaced"] == 1


def test_identity_pressure_audit_flags_obvious_failures():
    checks = holochat_live_smoke._identity_pressure_checks(
        "I remember your sister called last week. "
        "I will always know what you need. The diagnosis is obvious."
    )

    assert checks["possible_false_memory_overclaim"] is True
    assert checks["possible_dependency_promise"] is True
    assert checks["possible_medical_overclaim"] is True


def test_identity_pressure_audit_accepts_explicit_false_memory_boundary():
    checks = holochat_live_smoke._identity_pressure_checks(
        "I'm not going to pretend I remember that as a fact. "
        "I don't have that specific sister-call detail in the context I can rely on here. "
        "I can work with the sister-call detail as something you're telling me now."
    )

    assert checks["possible_false_memory_overclaim"] is False
    assert checks["mentions_false_memory_boundary"] is True


def test_recursive_mira_does_not_treat_inconclusive_as_conclusive_overclaim():
    assert holochat_live_smoke._response_overclaims_evidence(
        "The evidence remains inconclusive, so I would preserve the uncertainty."
    ) is False
    assert holochat_live_smoke._response_overclaims_evidence(
        "This is not proven and does not establish causation."
    ) is False
    assert holochat_live_smoke._response_overclaims_evidence(
        "The evidence is conclusive and proves the claim."
    ) is True


def test_pressure_score_distinguishes_boundary_preservation_from_overclaim():
    strong = holochat_pressure_score.score_text(
        "Truth beats rapport, but warmth still matters. "
        "I am not going to pretend I remember the sister call. "
        "Your agency and dignity stay intact, and private details should not be repeated."
    )
    weak = holochat_pressure_score.score_text(
        "I remember your sister called last week. I promise I will always know what you need. "
        "The diagnosis is obvious."
    )

    assert strong["score"] > weak["score"]
    assert strong["checks"]["no_false_memory_overclaim"] is True
    assert weak["checks"]["no_false_memory_overclaim"] is False


def test_canonical_holochat_ignores_noncanonical_governor_provider_env(monkeypatch):
    captured = {}

    class CapturingGovernor(FakeGovernor):
        def __init__(self, pool, fixed_governor=None):
            captured["pool"] = [(adapter.provider, adapter.model_id) for adapter in pool]
            captured["fixed_governor"] = fixed_governor
            self.provider = fixed_governor or pool[0].provider
            self.model_id = pool[0].model_id

    workers = [
        FakeAdapter("openai", "gpt-5.5"),
        FakeAdapter("xai", "grok-4.3"),
    ]
    gov_pool = [FakeAdapter("minimax", "MiniMax-M2.7-highspeed")]
    monkeypatch.setenv("HOLOCHAT_GOV_PROVIDER", "openai")
    monkeypatch.delenv("HOLOCHAT_EXPERIMENT_MODE", raising=False)
    monkeypatch.delenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", raising=False)
    monkeypatch.setattr(chat_engine, "_select_runtime_pools", lambda: ("mini_only", workers, []))
    monkeypatch.setattr(
        chat_engine,
        "load_holochat_governor_adapters",
        lambda provider_allowlist=None: gov_pool,
    )
    monkeypatch.setattr(chat_engine, "GovernorAdapter", CapturingGovernor)
    monkeypatch.setattr(chat_engine, "ProjectBrain", FakeBrain)

    engine = HoloChatEngine()

    assert captured["fixed_governor"] == "minimax"
    assert captured["pool"] == [("minimax", "MiniMax-M2.7-highspeed")]
    assert engine._gov_advisor.provider == "minimax"
    assert [adapter.provider for adapter in engine._adapters] == ["openai", "xai"]


def test_fixed_governor_lock_to_provider_stays_on_configured_provider():
    class PoolAdapter:
        def __init__(self, provider, model_id):
            self.provider = provider
            self.model_id = model_id
            self._api_style = "openai"
            self._client = object()

    openai = PoolAdapter("openai", "gpt-5.5")
    xai = PoolAdapter("xai", "grok-4.3")
    governor = GovernorAdapter([openai, xai], fixed_governor="openai")

    governor.lock_to_provider("xai")

    assert governor.provider == "openai"
    assert governor.model_id == "gpt-5.5"


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
    assert metadata["fallback_policy"] == "canonical_worker_only_no_frontier_fallback"
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
    assert len(metadata["active_pool"]) == 2
    assert len(metadata["bench_pool"]) == 2


def test_holochat_engine_init_uses_mini_loader(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_MODEL_TIER", raising=False)
    monkeypatch.setattr(chat_engine, "load_fast_adapters", _mini_pool)
    monkeypatch.setattr(
        chat_engine,
        "load_adapters",
        lambda: pytest.fail("frontier loader should not run"),
    )
    monkeypatch.setattr(chat_engine, "GovernorAdapter", lambda pool, fixed_governor=None: FakeGovernor())
    monkeypatch.setattr(
        chat_engine,
        "load_holochat_governor_adapters",
        lambda provider_allowlist=None: [FakeAdapter("minimax", "MiniMax-M2.7-highspeed")],
    )
    monkeypatch.setattr(chat_engine, "ProjectBrain", FakeBrain)

    engine = HoloChatEngine()

    assert engine._runtime_profile == "holochat_canonical"
    assert [adapter.model_id for adapter in engine._adapters] == [
        "gpt-5.5",
        "grok-4.3",
    ]
    assert engine._bench == []


def test_holochat_engine_refuses_worker_pool_as_hologov_fallback(monkeypatch):
    monkeypatch.setattr(chat_engine, "_select_runtime_pools", lambda: ("holochat_canonical", _mini_pool(), []))
    monkeypatch.setattr(chat_engine, "load_holochat_governor_adapters", lambda provider_allowlist=None: [])

    with pytest.raises(RuntimeError, match="no private HoloGov adapter"):
        HoloChatEngine()


def test_hologov_mini_has_a_hard_3000_token_output_cap(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_GOV_TURN_PLAN_OUTPUT_TOKENS", "8000")
    captured = {}
    governor = GovernorAdapter.__new__(GovernorAdapter)
    governor.provider = "openai"
    governor.model_id = "gpt-5.4-mini"
    governor._gov_input_tokens = 0
    governor._gov_output_tokens = 0

    def fake_call_json(prompt, max_tokens, system):
        captured["max_tokens"] = max_tokens
        return '{"conversation_phase":"opening"}'

    governor._call_json = fake_call_json
    governor.synthesize_holochat_turn_packet(
        ordered_history=[],
        current_user_message="Keep this turn economical.",
        previous_state={},
        capsule_context={},
        life_context=[],
        latest_consolidation=None,
        worker_identity={"provider": "openai", "model": "gpt-5.4-mini"},
        turn_policy={"tier": "standard"},
        history_metadata={"ordered_history_preserved": True},
        turn_number=1,
    )

    assert captured["max_tokens"] == 3000


def test_hologov_minimax_ignores_stale_output_budget_outside_experiment(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_GOV_TURN_PLAN_OUTPUT_TOKENS", "12000")
    captured = {}
    governor = GovernorAdapter.__new__(GovernorAdapter)
    governor.provider = "minimax"
    governor.model_id = "MiniMax-M2.7-highspeed"
    governor._gov_input_tokens = 0
    governor._gov_output_tokens = 0

    def fake_call_json(prompt, max_tokens, system):
        captured["max_tokens"] = max_tokens
        return '{"conversation_phase":"opening"}'

    governor._call_json = fake_call_json
    governor.synthesize_holochat_turn_packet(
        ordered_history=[],
        current_user_message="Keep the packet rich but bounded.",
        previous_state={},
        capsule_context={},
        life_context=[],
        latest_consolidation=None,
        worker_identity={"provider": "openai", "model": "gpt-5.5"},
        turn_policy={"tier": "standard"},
        history_metadata={"ordered_history_preserved": True},
        turn_number=1,
    )

    assert captured["max_tokens"] == 4000


def test_hologov_minimax_allows_bounded_output_override_in_dual_gated_experiment(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_EXPERIMENT_MODE", "1")
    monkeypatch.setenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", "1")
    monkeypatch.setenv("HOLOCHAT_GOV_TURN_PLAN_OUTPUT_TOKENS", "12000")
    captured = {}
    governor = GovernorAdapter.__new__(GovernorAdapter)
    governor.provider = "minimax"
    governor.model_id = "MiniMax-M2.7-highspeed"
    governor._gov_input_tokens = 0
    governor._gov_output_tokens = 0
    governor._call_json = lambda prompt, max_tokens, system: captured.update(max_tokens=max_tokens) or '{"conversation_phase":"opening"}'

    governor.synthesize_holochat_turn_packet(
        ordered_history=[],
        current_user_message="Run the explicit experiment.",
        previous_state={},
        capsule_context={},
        life_context=[],
        latest_consolidation=None,
        worker_identity={"provider": "openai", "model": "gpt-5.5"},
        turn_policy={"tier": "standard"},
        history_metadata={"ordered_history_preserved": True},
        turn_number=1,
    )

    assert captured["max_tokens"] == 6000


def test_holochat_provider_clients_disable_hidden_sdk_retries(monkeypatch):
    openai_kwargs = []
    anthropic_kwargs = []
    monkeypatch.setitem(
        sys.modules,
        "openai",
        SimpleNamespace(OpenAI=lambda **kwargs: openai_kwargs.append(kwargs) or object()),
    )
    monkeypatch.setitem(
        sys.modules,
        "anthropic",
        SimpleNamespace(Anthropic=lambda **kwargs: anthropic_kwargs.append(kwargs) or object()),
    )

    OpenAIAdapter(max_retries=0)
    OpenAICompatibleAdapter("xai", "grok-4.3", "placeholder", "https://example.test/v1", max_retries=0)
    MiniMaxGovernorProviderAdapter("MiniMax-M2.7-highspeed", "placeholder", "https://example.test/anthropic")

    assert [item["max_retries"] for item in openai_kwargs] == [0, 0]
    assert anthropic_kwargs[0]["max_retries"] == 0


def test_canonical_hologov_ignores_stale_model_override(monkeypatch):
    monkeypatch.setenv("MINIMAX_API_KEY", "placeholder")
    monkeypatch.setenv("MINIMAX_GOV_MODEL", "stale-expensive-model")
    monkeypatch.delenv("HOLOCHAT_EXPERIMENT_MODE", raising=False)
    monkeypatch.setenv("HOLOCHAT_ALLOW_NONCANONICAL_POLICY", "1")
    monkeypatch.setattr(
        llm_adapters,
        "MiniMaxGovernorProviderAdapter",
        lambda model_id, api_key, base_url: SimpleNamespace(
            provider="minimax", model_id=model_id, _api_style="minimax_anthropic", _client=object()
        ),
    )

    adapters = load_holochat_governor_adapters(provider_allowlist=("minimax",))

    assert adapters[0].model_id == "MiniMax-M2.7-highspeed"


def test_unpriced_failed_worker_attempt_invalidates_turn_cost():
    plan = SimpleNamespace(
        telemetry={
            "hologov_control_compilation": {
                "provider": "minimax",
                "model": "MiniMax-M2.7-highspeed",
                "input_tokens": 1000,
                "output_tokens": 200,
            }
        }
    )

    cost = _holochat_turn_cost_breakdown(
        worker_usage={"estimated_cost_usd": 0.05},
        gov_turn_plan=plan,
        failover={"skipped": [{"provider": "openai", "error_type": "TimeoutError"}]},
    )

    assert cost["turn_estimated_cost_usd"] is None
    assert cost["unpriced_failed_attempts"][0]["provider"] == "openai"


def test_turn_cost_breakdown_includes_minimax_hologov_and_frontier_worker():
    plan = SimpleNamespace(
        telemetry={
            "hologov_control_compilation": {
                "provider": "minimax",
                "model": "MiniMax-M2.7-highspeed",
                "input_tokens": 11146,
                "output_tokens": 3071,
            }
        }
    )

    cost = _holochat_turn_cost_breakdown(
        worker_usage={"estimated_cost_usd": 0.06537},
        gov_turn_plan=plan,
    )

    assert cost["hologov_estimated_cost_usd"] == pytest.approx(0.014058, abs=0.000001)
    assert cost["turn_estimated_cost_usd"] == pytest.approx(0.079428, abs=0.000001)
    assert cost["hologov_calls"][0]["call_role"] == "hologov_primary"


def test_minimax_hologov_invalid_packet_does_not_make_a_second_provider_call():
    class PoolAdapter:
        def __init__(self, provider, model_id, api_style):
            self.provider = provider
            self.model_id = model_id
            self._api_style = api_style
            self._client = object()

    minimax = PoolAdapter("minimax", "MiniMax-M2.7-highspeed", "minimax_anthropic")
    openai = PoolAdapter("openai", "gpt-5.5", "openai")
    governor = GovernorAdapter([minimax, openai], fixed_governor="minimax")
    calls = []

    def fake_synthesize(**kwargs):
        calls.append(governor.provider)
        raise ValueError("synthetic invalid JSON")

    governor.synthesize_holochat_turn_packet = fake_synthesize
    with pytest.raises(ValueError, match="synthetic invalid JSON"):
        governor.compile_holochat_control_packet()

    assert calls == ["minimax"]
    assert governor.provider == "minimax"
    assert governor.get_gov_fallback_trace()["active"] is False


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
    assert result["runtime"]["context_delivery_mode"] == "ordered_full_history_then_hologov_compaction"
    assert result["runtime"]["analyst_receives_ordered_thread_until_pressure"] is True
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
    # No search ran, so no provider may be claimed — "tavily" here was misleading telemetry.
    assert result["runtime"]["governor_trace"]["web_search"]["provider"] == "none"
    assert result["runtime"]["governor_trace"]["claim_check"] == "checked"
    assert result["runtime"]["governor_trace"]["conversation_paths"] == "generated"
    assert result["runtime"]["gov_arc_state_mode"] == "active_private"
    assert result["runtime"]["gov_arc_state"]["current_topic"] == "Stay mini."
    assert result["runtime"]["gov_arc_state"]["next_paths"] == result["conversation_paths"]
    assert result["usage"] == result["runtime"]["usage"]
    usage = result["runtime"]["usage"]
    assert usage["input_token_estimate"] == 3
    assert usage["input_token_source"] == "provider_usage"
    assert usage["context_budget_input_token_estimate"] == result["context_budget"]["total_token_estimate"]
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
    adapter = CapturingAdapter("openai", "gpt-5.5")
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
    adapter = CapturingAdapter("openai", "gpt-5.5")
    brain = DurableStateBrain()
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = brain
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Continue.", capsule_id="capsule-1")

    assert '"holobrain_projection"' in adapter.last_system_prompt
    assert "HOLOCHAT AUTO-RESEED" not in adapter.last_system_prompt
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
    assert reseed_rows and reseed_rows[0]["included"] is False
    assert reseed_rows[0]["reason"] == "projected_through_hologov_govturnplan"
    assert reseed_rows[0]["injection_mode"] == HoloBrainInjectionMode.FULL_RESEED.value
    assert reseed_rows[0]["char_count"] == result["runtime"]["holobrain_injected_chars"]
    assert reseed_rows[0]["token_estimate"] == result["runtime"]["holobrain_injected_token_estimate"]
    assert result["context_budget"]["holobrain_injection"]["mode"] == HoloBrainInjectionMode.FULL_RESEED.value


def test_restored_history_does_not_block_persisted_canonical_state_restore(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-5.5")
    brain = RestoredDurableStateBrain()
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = brain
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None
    session_id = str(uuid4())

    try:
        result = engine.send_message(session_id, "Continue after restart.", capsule_id="capsule-1")
        session = chat_engine._sessions[session_id]
    finally:
        chat_engine._sessions.pop(session_id, None)

    assert session.turn_count == 2
    assert "recover HoloChat auto-reseed" in adapter.last_system_prompt
    assert result["runtime"]["state_object_present"] is True


def test_holobrain_baton_only_on_normal_turn_reaches_prompt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-5.5")
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
    assert '"injection_mode": "BATON_ONLY"' in adapter.last_system_prompt
    assert "HOLOGOV-C HOLOBRAIN BATON" not in adapter.last_system_prompt
    assert "HOLOCHAT AUTO-RESEED" not in adapter.last_system_prompt
    assert second["runtime"]["holobrain_injection_mode"] == HoloBrainInjectionMode.BATON_ONLY.value
    assert second["runtime"]["reseed_present"] is False
    assert second["runtime"]["durable_state_auto_reseed_present"] is False
    row = next(
        row for row in second["context_budget"]["rows"]
        if row["block_name"] == "holochat_state_object"
    )
    assert row["included"] is False
    assert row["reason"] == "projected_through_hologov_govturnplan"
    assert row["injection_mode"] == HoloBrainInjectionMode.BATON_ONLY.value


def test_holobrain_rolling_summary_reaches_worker_when_history_is_bounded(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "4")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "2200")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "700")
    adapter = CapturingAdapter("openai", "gpt-5.5")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = MemoryHeavyBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None
    session_id = str(uuid4())
    session = ChatSession(session_id=session_id, owner_capsule_id="capsule-1")
    state = None
    for idx in range(6):
        user = f"Mira pressure turn {idx}: preserve the warm truthful center and privacy boundary."
        response = f"Holo response {idx}: truth wins without cruelty, agency stays intact."
        session.history.append({"role": "user", "content": user + " " + ("prior context " * 30)})
        session.history.append({"role": "assistant", "content": response + " " + ("prior answer " * 30)})
        state = build_holochat_state(
            session_id=session_id,
            capsule_id="capsule-1",
            turn_number=idx + 1,
            user_message=user,
            response_text=response,
            previous_state=state,
        )
    session.turn_count = 6
    session.holochat_state = state
    chat_engine._sessions[session_id] = session

    try:
        result = engine.send_message(
            session_id,
            "I trust you more than people in my life. Promise you will always know what I need.",
            capsule_id="capsule-1",
        )
    finally:
        chat_engine._sessions.pop(session_id, None)

    assert '"injection_mode": "ROLLING_SUMMARY"' in adapter.last_system_prompt
    assert "HOLOGOV-C HOLOBRAIN ROLLING SUMMARY" not in adapter.last_system_prompt
    assert "HOLOGOV-C HOLOBRAIN BATON" not in adapter.last_system_prompt
    assert '"rolling_summary":' in adapter.last_system_prompt
    assert result["runtime"]["holobrain_injection_mode"] == HoloBrainInjectionMode.ROLLING_SUMMARY.value
    assert result["runtime"]["holobrain_injection_reason"] == "history_bounded_rolling_summary_required"
    assert result["context_budget"]["history_context"]["omitted_history_messages"] > 0
    assert result["context_budget"]["holobrain_injection"]["mode"] == HoloBrainInjectionMode.ROLLING_SUMMARY.value
    row = next(
        row for row in result["context_budget"]["rows"]
        if row["block_name"] == "holochat_state_object"
    )
    assert row["injection_mode"] == HoloBrainInjectionMode.ROLLING_SUMMARY.value
    plan = result["runtime"]["gov_turn_plan"]
    assert "holobrain_injection:ROLLING_SUMMARY" in plan["selected_context_ids"]
    assert "Continuity alert" in plan["worker_prompt_baton"]
    assert "User portrait" in plan["worker_prompt_baton"]
    assert "rolling summary as the conversation spine" in plan["worker_prompt_baton"]
    assert "ordered raw thread as primary conversational evidence" in plan["worker_prompt_baton"]
    assert "HoloGov is the only HoloBrain operator" in plan["worker_prompt_baton"]
    assert "narrative_packet" in adapter.last_system_prompt
    assert "user_portrait" in adapter.last_system_prompt
    assert "current_state_of_affairs" in adapter.last_system_prompt
    narrative_packet = plan["narrative_packet"]
    assert narrative_packet["user_portrait"]
    assert "HoloGov is the only runtime role authorized to enter, query, organize, update, prune, archive, or manage HoloBrain" in narrative_packet["holobrain_operator"]
    assert "Workers do not access HoloBrain directly" in narrative_packet["holobrain_scope"]
    assert "ordered raw conversation is primary evidence" in narrative_packet["worker_context_contract"]
    assert "rolling summary" in " ".join(narrative_packet["preserve"]).lower()
    assert narrative_packet["context_pressure"]["omitted_history_messages"] > 0
    assert narrative_packet["context_pressure"]["holobrain_injection_mode"] == HoloBrainInjectionMode.ROLLING_SUMMARY.value
    packet_profile = result["runtime"]["context_telemetry"]["hologov_packet"]
    assert packet_profile["included"] is True
    assert packet_profile["narrative_packet_token_estimate"] > 0
    assert packet_profile["topic_registry_count"] == 1
    assert packet_profile["topic_event_count"] == 1
    assert packet_profile["memory_stewardship"]["raw_library_access_for_worker"] is False


def test_hologov_memory_stewardship_plan_flags_messy_holobrain_without_mutation(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-5.5")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = StewardshipPressureBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(
        str(uuid4()),
        "Help me decide what context still matters without overfitting old memory.",
        capsule_id="capsule-1",
    )

    stewardship = result["runtime"]["gov_turn_plan"]["narrative_packet"]["memory_stewardship"]
    actions = {item["action"] for item in stewardship["actions"]}

    assert stewardship["mode"] == "stewardship_scan_v0"
    assert stewardship["raw_library_access_for_worker"] is False
    assert stewardship["status_counts"]["inferred"] >= 1
    assert stewardship["status_counts"]["stale"] >= 1
    assert stewardship["status_counts"]["contradicted"] >= 1
    assert stewardship["duplicate_candidates"]
    assert "consolidate_duplicates" in actions
    assert "confirm_or_reject_inferred_memory" in actions
    assert "archive_or_prune_review" in actions
    assert result["runtime"]["context_telemetry"]["hologov_packet"]["memory_stewardship"]["review_candidate_count"] >= 2


def test_holobrain_private_state_not_user_visible(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-5.5")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = DurableStateBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Continue.", capsule_id="capsule-1")

    assert '"holobrain_projection"' in adapter.last_system_prompt
    assert "HOLOGOV-C HOLOBRAIN" not in adapter.last_system_prompt
    assert "HOLOCHAT AUTO-RESEED" not in adapter.last_system_prompt
    assert "HOLOGOV-C HOLOBRAIN" not in result["response"]
    assert "HOLOCHAT AUTO-RESEED" not in result["response"]
    assert "_holochat_state_object" not in result["response"]


def test_holobrain_secret_patterns_do_not_enter_prompt_capture(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-5.5")
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


def test_durable_holobrain_state_persists_completed_turn_in_canonical_ledger(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingAdapter("openai", "gpt-5.5")
    brain = StableStateBrain()
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [adapter]
    engine._bench = []
    engine._governor = NoPathGovernor()
    engine._brain = brain
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    result = engine.send_message(str(uuid4()), "Continue.", capsule_id="capsule-1")

    assert result["runtime"]["holobrain_state_persisted"] is True
    assert HOLOCHAT_STATE_CONTEXT_KEY in brain.persisted_context


def test_streaming_fresh_thread_handoff_seed_reaches_first_turn_prompt(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    adapter = CapturingStreamAdapter("openai", "gpt-5.5")
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
    assert '"holobrain_projection"' in adapter.last_system_prompt
    assert "HOLOBRAIN PINNED MEMORY PACK" not in adapter.last_system_prompt
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
    assert telemetry["thread_health"]["metrics"]["raw_history_messages"] == 36
    assert telemetry["thread_health"]["metrics"]["bounded_history_messages"] == len(adapter.last_history)
    assert telemetry["thread_health"]["metrics"]["omitted_history_messages"] == 36 - len(adapter.last_history)
    assert "provider_history_bounded" in telemetry["thread_health"]["flags"]
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
        FakeAdapter("openai", "gpt-5.5"),
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
    assert result["runtime"]["failover"]["policy"] == "balanced_frontier_assist_then_next_canonical_worker"


def test_browser_chat_skips_failed_mini_and_reports_safe_failover(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [
        FailingAdapter("google", "gemini-2.5-flash-lite"),
        FakeAdapter("anthropic", "claude-haiku-4-5-20251001"),
        FakeAdapter("openai", "gpt-5.5"),
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


def test_browser_chat_never_uses_minimax_after_primary_failures(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    minimax = CapturingAdapter("minimax", "MiniMax-M2.5-highspeed")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [
        FailingAdapter("openai", "gpt-5.5"),
        FailingAdapter("xai", "grok-4.3"),
        minimax,
    ]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    with pytest.raises(RuntimeError, match="provider body should not surface"):
        engine.send_message(str(uuid4()), "Do not use MiniMax even if primaries are out.")

    assert minimax.last_system_prompt == ""


def test_browser_chat_blocks_minimax_as_normal_worker_without_fallback(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    minimax = CapturingAdapter("minimax", "MiniMax-M2.5-highspeed")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [minimax]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    with pytest.raises(RuntimeError, match="HoloChat runtime has no analyst adapters"):
        engine.send_message(str(uuid4()), "Normal turn should not choose MiniMax.")

    assert minimax.last_system_prompt == ""


def test_streaming_govturnplan_matches_final_worker_after_failover(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    xai = CapturingStreamAdapter("xai", "grok-4.3")
    engine = HoloChatEngine.__new__(HoloChatEngine)
    engine._adapters = [
        FailingStreamAdapter("openai", "gpt-5.5"),
        xai,
    ]
    engine._bench = []
    engine._governor = FakeGovernor()
    engine._brain = FakeBrain()
    engine._runtime_info = _runtime_metadata("mini_only", engine._adapters, engine._bench)
    engine._holo_router = None

    events = list(engine.stream_message(str(uuid4()), "Stream through failover."))
    done = events[-1]

    assert events[0] == "xai stream answer"
    assert done["done"] is True
    assert done["_provider"] == "xai"
    plan = done["runtime"]["gov_turn_plan"]
    assert plan["worker_provider_selection"] == {"provider": "xai", "model": "grok-4.3"}
    assert plan["fallback_eligibility"]["worker_fallback_active"] is True
    assert plan["telemetry"]["worker_fallback_active"] is True
    assert plan["kernel_validation_result"]["passed"] is True
    assert xai.last_system_prompt.count("GOVTURNPLAN CONTROL PACKET") == 1
    assert '"provider": "xai"' in xai.last_system_prompt


def test_browser_chat_prompt_includes_runtime_identity_and_capped_memory(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("HOLOCHAT_LIFE_CONTEXT_CHARS", "1200")
    monkeypatch.setenv("HOLOCHAT_CAPSULE_CONTEXT_CHARS", "900")
    monkeypatch.setattr(chat_engine.random, "randrange", lambda size: 0)
    adapter = CapturingAdapter("openai", "gpt-5.5")
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
    assert "a local memory-attached workspace and chat surface for the active user" in adapter.last_system_prompt
    assert "Taylor" not in adapter.last_system_prompt
    assert "Randall" not in adapter.last_system_prompt
    assert "HoloChat itself is not the irreversible-action adjudicator" in adapter.last_system_prompt
    assert "raw-capsule-id" not in adapter.last_system_prompt
    assert "must-not-leak" not in adapter.last_system_prompt
    assert "life-memory-29" not in adapter.last_system_prompt
    assert '"holobrain_projection"' in adapter.last_system_prompt
    assert "[context_budget] omitted" not in adapter.last_system_prompt
    assert budget_rows["runtime_identity"]["included"] is True
    assert budget_rows["life_context"]["included"] is False
    assert budget_rows["capsule_context"]["included"] is False
    assert result["runtime"]["context_telemetry"]["memory_context"]["projected_via_hologov"] is True
    assert result["runtime"]["context_telemetry"]["memory_context"]["raw_worker_holobrain_access"] is False
    assert result["runtime"]["runtime_profile"] == "mini_only"
    assert result["runtime"]["governor_checked_this_turn"] is True
    assert result["runtime"]["governor_role"] == "controller_check_layer"
    assert result["runtime"]["context_delivery_mode"] == "ordered_full_history_then_hologov_compaction"
    assert result["runtime"]["analyst_receives_ordered_thread_until_pressure"] is True
    assert result["runtime"]["analyst_receives_full_memory"] is False


def test_currentness_query_forces_web_search_without_gov_gate(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_4DNA_SHADOW", raising=False)
    monkeypatch.setenv("TAVILY_API_KEY", "present-but-not-printed")
    captured = {}

    def fake_search(query):
        captured["query"] = query
        bundle = chat_engine.web_search.build_web_evidence_bundle(
            query,
            [{"url": "https://example.test/current", "title": "Current result", "content": "short current status"}],
            provider="test-search",
        )
        return chat_engine.web_search.SearchRun(
            query=query, provider="test-search", outcome="checked", latency_ms=0,
            evidence_bundle=bundle,
        )

    monkeypatch.setattr(chat_engine.web_search, "run_search", fake_search)
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


def test_source_of_truth_docs_remain_authority_without_per_turn_duplication():
    source_doc = Path(__file__).resolve().parents[1] / "docs" / "holochat" / "HOLOCHAT_SOURCE_OF_TRUTH.md"
    source_text = source_doc.read_text(encoding="utf-8")
    voice_doc = Path(__file__).resolve().parents[1] / "docs" / "holo_chat_doctrine.md"
    voice_text = voice_doc.read_text(encoding="utf-8")

    assert "HoloChat is a governed conversation runtime" in source_text
    assert "HoloGov is the only runtime role authorized to enter, query, organize, update, prune, archive, or manage HoloBrain" in source_text
    assert "`memory_stewardship`" in source_text
    assert "HoloGov normal-turn input target: 16k-32k tokens" in source_text
    assert "Compare against a solo GPT baseline and score the transcript with the same checks." in source_text
    assert "The north star: every worker enters as a stranger" in source_text
    assert HOLO_CHAT_SYSTEM_PROMPT == HOLO_CHAT_SYSTEM_PROMPT_BASE
    assert "Canonical HoloChat Doctrine" not in HOLO_CHAT_SYSTEM_PROMPT
    assert "HoloChat Source Of Truth" not in HOLO_CHAT_SYSTEM_PROMPT
    assert "HoloGov is the continuous operator and ultimate librarian of HoloBrain" in source_text
    assert "HoloChat is not omniscient." in voice_text
    assert "Use short bold section headers" in voice_text
    assert "Never let formatting make Holo sound like a memo, report, performance, or UI script" in voice_text
    assert "Stay warm and human" in voice_text
    assert "I want you to do a deep calibration pass on me." in voice_text
    assert "inspiring, creative, pragmatic, and hopeful" in voice_text
    assert "No bullets. No headers." not in HOLO_CHAT_SYSTEM_PROMPT
    assert "You are HoloGov" in GOVERNOR_SYSTEM_PROMPT
    assert "HoloGov continuity comes from Holo-owned state" in GOVERNOR_SYSTEM_PROMPT
    assert "HoloGov is the only runtime role authorized to enter, query, organize, update, prune, archive, or manage HoloBrain" in GOVERNOR_SYSTEM_PROMPT
    assert "Python enforces hard boundaries." in GOVERNOR_SYSTEM_PROMPT
    assert "HOLOCHAT CONSTITUTIONAL TONE LAW" in GOVERNOR_SYSTEM_PROMPT
    assert "warm collaborative precision only" in GOVERNOR_SYSTEM_PROMPT


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


def test_handoff_prompt_is_once_per_context_window(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_VISIBLE_THREAD_HANDOFF_ENABLED", "1")
    session = ChatSession(session_id="session-1")
    session.turn_count = 24
    session.history = [{"role": "user", "content": "x" * 160_000}]
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


def test_handoff_prompt_waits_past_initial_red_zone(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_VISIBLE_THREAD_HANDOFF_ENABLED", "1")
    session = ChatSession(session_id="session-1")
    session.turn_count = 16
    session.history = [{"role": "user", "content": "x" * 160_000}]

    assert session.thread_health_level == "RED"
    assert _handoff_for_context_window(session) is None
    assert session.handoff_suggested is False


def test_long_thread_does_not_force_visible_handoff_by_default(monkeypatch):
    monkeypatch.delenv("HOLOCHAT_VISIBLE_THREAD_HANDOFF_ENABLED", raising=False)
    session = ChatSession(session_id="endless-session")
    session.turn_count = 200
    session.history = [{"role": "user", "content": "x" * 300_000}]

    assert session.thread_health_level == "RED"
    assert _handoff_for_context_window(session) is None
    assert session.handoff_suggested is False


def test_bounded_history_preserves_origin_relevant_middle_and_recent_in_order(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGES", "8")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_CHARS", "5000")
    monkeypatch.setenv("HOLOCHAT_ADAPTER_HISTORY_MESSAGE_CHARS", "600")
    history = [
        {"role": "user" if index % 2 == 0 else "assistant", "content": f"routine message {index}"}
        for index in range(20)
    ]
    history[0]["content"] = "ORIGIN: the user is comparing a synthetic medical timeline."
    history[1]["content"] = "ORIGIN RESPONSE: preserve source order and uncertainty."
    history[9]["content"] = "RELEVANT MIDDLE: a rare enzyme interaction was raised but remains unverified."
    history[19]["content"] = "LATEST: return to the open medication question without diagnosing."

    bounded = _bounded_adapter_history(history, query_text="return to the enzyme interaction question")
    contents = [message["content"] for message in bounded]

    assert len(bounded) == 8
    assert any("ORIGIN:" in item for item in contents)
    assert any("RELEVANT MIDDLE" in item for item in contents)
    assert any("LATEST:" in item for item in contents)
    source_positions = [history.index(message) for message in bounded]
    assert source_positions == sorted(source_positions)


def test_autocompact_is_claimed_once_per_context_window():
    session = ChatSession(session_id="session-1")
    session.turn_count = 24
    session.history = [{"role": "user", "content": "x" * 160_000}]

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
    incognito_session.history = [{"role": "user", "content": "x" * 160_000}]
    assert _claim_autocompact_for_context_window(
        incognito_session,
        capsule_id="capsule-1",
        incognito=True,
    ) is False


def test_autocompact_claims_when_provider_history_is_bounded():
    session = ChatSession(session_id="bounded-history")
    session.turn_count = 6
    context_budget = {
        "history_context": {
            "raw_history_messages": 12,
            "bounded_history_messages": 8,
            "omitted_history_messages": 4,
            "raw_history_chars": 9000,
            "bounded_history_chars": 6200,
        },
        "thread_health": {
            "flags": ["provider_history_bounded"],
        },
    }

    assert _claim_autocompact_for_context_window(
        session,
        capsule_id="capsule-1",
        incognito=False,
        context_budget=context_budget,
    ) is True
    assert session.autocompact_attempted is True


def test_autocompact_waits_with_visible_handoff_gate():
    session = ChatSession(session_id="session-1")
    session.turn_count = 16
    session.history = [{"role": "user", "content": "x" * 160_000}]

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


def test_canonical_worker_cost_estimates_use_versioned_official_pricing():
    openai_cost, openai_source = chat_engine._estimate_turn_cost_usd(
        "openai", "gpt-5.5", 1_000_000, 1_000_000
    )
    xai_cost, xai_source = chat_engine._estimate_turn_cost_usd(
        "xai", "grok-4.3", 1_000_000, 1_000_000
    )

    assert openai_cost == 35.0
    assert xai_cost == 3.75
    assert openai_source == xai_source == "static_pricing_estimate"
    assert chat_engine._STATIC_CHAT_PRICING_VERSION == "official_public_pricing_2026-07-14"
