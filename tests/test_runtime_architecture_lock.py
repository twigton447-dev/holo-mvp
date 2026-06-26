from dataclasses import FrozenInstanceError

import pytest

import chat_engine
from chat_engine import (
    DEFAULT_LOCKED_ARCHITECTURE_PROFILE,
    LOCKED_ARCHITECTURE_MANIFEST,
    ResolvedArchitectureProfile,
    _holochat_runtime_profile,
    _select_runtime_pools,
)


class FakeAdapter:
    def __init__(self, provider: str, model_id: str):
        self.provider = provider
        self.model_id = model_id


EXPECTED_LOCKED_VALUE = {
    "architecture_profile": "frontier_holo_optimized_opus_gpt55_v1",
    "alignment_profile": "patent_aligned_v4",
    "registry_profile": "full_registry",
    "governor_lane": "HoloGov-B",
}


def _frontier_loader():
    return (
        [
            FakeAdapter("openai", "env-may-change-model-not-profile"),
            FakeAdapter("anthropic", "env-may-change-model-not-profile"),
            FakeAdapter("google", "env-may-change-model-not-profile"),
        ],
        [
            FakeAdapter("xai", "env-may-change-model-not-profile"),
            FakeAdapter("minimax", "env-may-change-model-not-profile"),
        ],
    )


def _assert_locked_manifest_profile(profile: ResolvedArchitectureProfile):
    assert profile.locked_value() == EXPECTED_LOCKED_VALUE
    assert profile.source == "locked_manifest"
    assert profile.status == "locked"
    assert profile.runtime_behavior == "manifest_controls_runtime_selection"
    assert profile.pool_strategy == "frontier_ordered_full_registry"
    assert profile.manifest_path == str(LOCKED_ARCHITECTURE_MANIFEST)
    assert profile.manifest_version == "2026-06-25.1"


def test_locked_manifest_profile_cannot_be_overridden_by_runtime_precedence_layers(monkeypatch, tmp_path):
    # Baseline: no env/default runtime label may define behavior.
    monkeypatch.delenv("HOLOCHAT_ARCHITECTURE_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    profile, active, bench = _select_runtime_pools(frontier_loader=_frontier_loader)
    _assert_locked_manifest_profile(profile)
    assert [adapter.provider for adapter in active] == ["xai", "openai", "minimax"]
    assert [adapter.provider for adapter in bench] == ["anthropic", "google"]

    # Env vars are ignored for profile selection, even when they contain the
    # locked profile id.
    monkeypatch.setenv("HOLOCHAT_ARCHITECTURE_PROFILE", DEFAULT_LOCKED_ARCHITECTURE_PROFILE)
    monkeypatch.setenv("HOLOCHAT_RUNTIME_PROFILE", DEFAULT_LOCKED_ARCHITECTURE_PROFILE)
    profile, active, bench = _select_runtime_pools(frontier_loader=_frontier_loader)
    _assert_locked_manifest_profile(profile)
    assert profile.selector_source == "locked_constant"

    # Env, config, provider routing, model routing, demo flags, and cache-like
    # state may not mutate the final architecture or manifest provenance.
    override_env = {
        "HOLOCHAT_PROVIDER_ROTATION": "google,anthropic,openai",
        "HOLOCHAT_GOVERNOR_PROVIDER": "google",
        "OPENAI_MODEL": "not-the-architecture",
        "ANTHROPIC_MODEL": "not-the-architecture",
        "GOOGLE_MODEL": "not-the-architecture",
        "XAI_MODEL": "not-the-architecture",
        "MINIMAX_MODEL": "not-the-architecture",
        "HOLOCHAT_4DNA_SHADOW": "1",
        "HOLOCHAT_4DNA_ENABLED": "1",
        "HOLOCHAT_CONTEXT_BUDGET_TOKENS": "999999",
    }
    for name, value in override_env.items():
        monkeypatch.setenv(name, value)
    profile, active, bench = _select_runtime_pools(frontier_loader=_frontier_loader)
    _assert_locked_manifest_profile(profile)
    assert profile.governor_provider == "openai"
    assert [adapter.provider for adapter in active] == ["xai", "openai", "minimax"]
    assert [adapter.provider for adapter in bench] == ["anthropic", "google"]

    # CLI/test-shim style direct values cannot use legacy aliases.
    for legacy_alias in ("frontier_active", "legacy_frontier", "balanced", "mini_only"):
        with pytest.raises(RuntimeError, match="override is disabled"):
            _select_runtime_pools(legacy_alias, frontier_loader=_frontier_loader)

    # Env aliases are ignored. They cannot select or reject the active profile.
    for legacy_alias in ("frontier_active", "legacy_frontier", "balanced", "mini_only"):
        monkeypatch.setenv("HOLOCHAT_RUNTIME_PROFILE", legacy_alias)
        profile, active, bench = _select_runtime_pools(frontier_loader=_frontier_loader)
        _assert_locked_manifest_profile(profile)
        assert profile.selector_source == "locked_constant"

    # Missing-manifest fallback is forbidden.
    monkeypatch.delenv("HOLOCHAT_ARCHITECTURE_PROFILE", raising=False)
    monkeypatch.delenv("HOLOCHAT_RUNTIME_PROFILE", raising=False)
    monkeypatch.setattr(chat_engine, "LOCKED_ARCHITECTURE_MANIFEST", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="manifest not found"):
        _holochat_runtime_profile()

    # The resolved object is frozen after manifest validation.
    monkeypatch.setattr(chat_engine, "LOCKED_ARCHITECTURE_MANIFEST", LOCKED_ARCHITECTURE_MANIFEST)
    profile = _holochat_runtime_profile()
    with pytest.raises(FrozenInstanceError):
        profile.runtime_class = "mini_only"


def test_hostile_runtime_env_cannot_reach_legacy_pool_construction(monkeypatch):
    hostile_env = {
        "HOLOCHAT_ARCHITECTURE_PROFILE": "malicious_manifest_profile",
        "HOLOCHAT_PROVIDER_ROTATION": "google,anthropic,openai",
        "HOLOCHAT_GOVERNOR_PROVIDER": "google",
        "OPENAI_MODEL": "hostile-openai",
        "ANTHROPIC_MODEL": "hostile-anthropic",
        "GOOGLE_MODEL": "hostile-google",
        "XAI_MODEL": "hostile-xai",
        "MINIMAX_MODEL": "hostile-minimax",
        "HOLOCHAT_4DNA_SHADOW": "1",
        "HOLOCHAT_4DNA_ENABLED": "1",
    }
    for name, value in hostile_env.items():
        monkeypatch.setenv(name, value)

    for legacy_profile in ("mini_only", "balanced", "frontier_active", "legacy_frontier"):
        monkeypatch.setenv("HOLOCHAT_RUNTIME_PROFILE", legacy_profile)

        profile, active, bench = _select_runtime_pools(frontier_loader=_frontier_loader)
        _assert_locked_manifest_profile(profile)
        assert profile.selector_source == "locked_constant"
        assert [adapter.provider for adapter in active] == ["xai", "openai", "minimax"]
