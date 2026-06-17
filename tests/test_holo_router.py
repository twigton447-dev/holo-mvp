from dataclasses import dataclass

from holo_router import (
    HoloRouter,
    PreviousRoute,
    resolve_holochat_dna_profile,
)
from holo_state import HoloState


@dataclass(frozen=True)
class FakeAdapter:
    provider: str
    model_id: str


VERIFY_4MINI_ADAPTERS = [
    FakeAdapter("minimax", "MiniMax-M2.5-highspeed"),
    FakeAdapter("xai", "grok-3-mini"),
    FakeAdapter("openai", "gpt-4o-mini"),
    FakeAdapter("google", "gemini-2.5-flash-lite"),
]


ALL_KEYS = {
    "MINIMAX_API_KEY": "1",
    "XAI_API_KEY": "1",
    "OPENAI_API_KEY": "1",
    "GOOGLE_API_KEY": "1",
}


def test_profile_resolves_four_model_entries_when_config_present():
    result = resolve_holochat_dna_profile(VERIFY_4MINI_ADAPTERS, env=ALL_KEYS)

    assert result.resolved_profile == "verify_4mini"
    assert result.fallback_used is False
    assert len(result.eligible_adapters) == 4
    assert result.eligible_provider_count == 4
    assert result.dna_degraded is False


def test_missing_provider_key_skips_cleanly():
    env = dict(ALL_KEYS)
    env.pop("XAI_API_KEY")

    result = resolve_holochat_dna_profile(VERIFY_4MINI_ADAPTERS, env=env)

    assert len(result.eligible_adapters) == 3
    assert "xai/grok-3-mini:missing_env:XAI_API_KEY" in result.skipped
    assert result.dna_degraded is True
    assert result.fallback_used is False


def test_profile_fallback_is_explicit_not_silent():
    adapters = [FakeAdapter("anthropic", "claude-haiku-test")]

    result = resolve_holochat_dna_profile(adapters, env=ALL_KEYS)

    assert result.fallback_used is True
    assert result.resolved_profile == "active_adapter_pool"
    assert result.fallback_reason == "profile verify_4mini resolved zero eligible adapters"


def test_no_immediate_council_repeat_when_alternative_exists():
    router = HoloRouter(VERIFY_4MINI_ADAPTERS, env=ALL_KEYS, seed=7)
    state = HoloState(session_id="s")

    first = router.select_route(state)
    second = router.select_route(state, previous_route=first)

    assert (second.council_provider, second.council_model) != (
        first.council_provider,
        first.council_model,
    )


def test_hologov_and_council_differ_when_possible():
    router = HoloRouter(VERIFY_4MINI_ADAPTERS, env=ALL_KEYS, seed=1)
    state = HoloState(session_id="s")

    route = router.select_route(state)

    assert route.council_provider != route.hologov_provider
    assert route.dna_degraded is False


def test_single_provider_degraded_mode_works():
    adapters = [FakeAdapter("openai", "gpt-4o-mini")]
    env = {"OPENAI_API_KEY": "1"}
    router = HoloRouter(adapters, env=env, seed=2)

    route = router.select_route(HoloState(session_id="s"))

    assert route.council_provider == "openai"
    assert route.hologov_provider == "openai"
    assert route.dna_degraded is True
    assert route.eligible_provider_count == 1


def test_hologov_tenure_lock_is_preserved():
    router = HoloRouter(VERIFY_4MINI_ADAPTERS, env=ALL_KEYS, seed=3)
    state = HoloState(session_id="s")
    previous = PreviousRoute(
        council_provider="openai",
        council_model="gpt-4o-mini",
        hologov_provider="google",
        hologov_model="gemini-2.5-flash-lite",
        hologov_tenure_remaining=5,
    )

    route = router.select_route(state, previous_route=previous)

    assert route.hologov_provider == "google"
    assert route.hologov_model == "gemini-2.5-flash-lite"
    assert route.hologov_tenure_remaining == 4


def test_seeded_routing_is_deterministic():
    state = HoloState(session_id="s")
    router_a = HoloRouter(VERIFY_4MINI_ADAPTERS, env=ALL_KEYS, seed=42)
    router_b = HoloRouter(VERIFY_4MINI_ADAPTERS, env=ALL_KEYS, seed=42)

    route_a = router_a.select_route(state)
    route_b = router_b.select_route(state)

    assert route_a == route_b
