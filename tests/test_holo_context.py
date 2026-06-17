from dataclasses import dataclass

from holo_context import HoloContextBuilder
from holo_router import RouteDecision
from holo_state import HoloState, RequiredTools


@dataclass(frozen=True)
class _RouteFactory:
    @staticmethod
    def make() -> RouteDecision:
        return RouteDecision(
            council_provider="openai",
            council_model="gpt-4o-mini",
            hologov_provider="google",
            hologov_model="gemini-2.5-flash-lite",
            assigned_role="DIRECT_SYNTHESIS",
            route_reason="test_route",
            fallback_used=False,
            fallback_reason=None,
            dna_profile="verify_4mini",
            dna_degraded=False,
            eligible_provider_count=4,
        )


def test_context_packet_includes_required_holostate_fields():
    state = HoloState.from_chat_turn(
        session_id="session-1",
        turn_number=1,
        user_message="What should I do?",
        required_tools=[RequiredTools.NONE],
    )

    packet = HoloContextBuilder().build(
        base_system_prompt="You are Holo.",
        holo_state=state,
        user_message="What should I do?",
        route_decision=_RouteFactory.make(),
    )

    assert "HOLOSTATE v0.1" in packet.system_prompt
    assert state.state_id in packet.system_prompt
    assert '"session_id":"session-1"' in packet.system_prompt
    assert "HOLOCOUNCIL ROUTE" in packet.system_prompt
    assert "holo_state" in packet.metadata["included_blocks"]


def test_context_packet_includes_web_results_only_when_provided():
    state = HoloState(session_id="s")
    builder = HoloContextBuilder()

    without_web = builder.build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
    )
    with_web = builder.build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
        web_results="Source: example\nResult",
    )

    assert "Source: example" not in without_web.user_message
    assert "web_results" in without_web.metadata["omitted_blocks"]
    assert "Source: example" in with_web.user_message
    assert "web_results" in with_web.metadata["included_blocks"]


def test_context_packet_omits_memory_in_incognito():
    state = HoloState(session_id="s")

    packet = HoloContextBuilder().build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
        capsule_context={"about_me": "private"},
        life_context=[{"category": "work", "key": "project", "value": "secret"}],
        latest_consolidation={"captain_note": "secret"},
        incognito=True,
    )

    assert "private" not in packet.system_prompt
    assert "secret" not in packet.system_prompt
    assert "capsule_context" in packet.metadata["omitted_blocks"]
    assert "life_context" in packet.metadata["omitted_blocks"]


def test_context_metadata_lists_included_blocks_and_size():
    state = HoloState(session_id="s")

    packet = HoloContextBuilder().build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
        capsule_context={"name": "Randall"},
    )

    assert "base_system_prompt" in packet.metadata["included_blocks"]
    assert "capsule_context" in packet.metadata["included_blocks"]
    assert packet.char_count == len(packet.system_prompt) + len(packet.user_message)
    assert packet.token_estimate >= 1
    assert len(packet.context_hash) == 64
