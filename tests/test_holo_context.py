from dataclasses import dataclass

from holo_context import HoloContextBuilder, build_context_budget_ledger
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

    assert "HOLOSTATE holochat_state_v0.1" in packet.system_prompt
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


def test_runtime_identity_block_is_present_and_safe():
    state = HoloState(session_id="s", capsule_id="raw-capsule-id")

    packet = HoloContextBuilder().build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
        runtime_info={
            "runtime_profile": "mini_only",
            "active_pool": [{"provider": "openai", "model": "gpt-4o-mini"}],
            "email": "taylor@example.com",
            "capsule_id": "raw-capsule-id",
        },
        capsule_attached=True,
    )

    identity_block = packet.system_prompt.split("HOLOCHAT RUNTIME IDENTITY:", 1)[1].split("\n\n", 1)[0]
    assert "HoloChat" in identity_block
    assert "local memory-attached workspace and chat surface" in identity_block
    assert "capsule_attached: true" in identity_block
    assert "signed-in capsule" in identity_block
    assert "conversation, memory, context, drafts, planning, project continuity" in identity_block
    assert "runtime_profile: mini_only" in identity_block
    assert "openai:gpt-4o-mini" in identity_block
    assert "HoloBrain" in identity_block
    assert "HoloVerify" in identity_block
    assert "HoloEvidence" in identity_block
    assert "HoloVerify/Holo Engine" in identity_block
    assert "ALLOW/ESCALATE" in identity_block
    assert "HoloChat itself is not the irreversible-action adjudicator" in identity_block
    assert "evaluates agent actions before execution" not in identity_block
    assert "raw-capsule-id" not in identity_block
    assert "taylor@example.com" not in identity_block
    for unsafe_word in ("token", "cookie", "auth", "Supabase", "secret", "password"):
        assert unsafe_word.lower() not in identity_block.lower()
    assert "runtime_identity" in packet.metadata["included_blocks"]


def test_context_memory_blocks_are_capped_and_do_not_include_sensitive_keys(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_LIFE_CONTEXT_CHARS", "900")
    monkeypatch.setenv("HOLOCHAT_CAPSULE_CONTEXT_CHARS", "700")
    state = HoloState(session_id="s")
    life_context = [
        {
            "category": "work",
            "key": f"project_{idx}",
            "value": f"life-value-{idx} " + ("x" * 120),
            "confidence": 0.95 - (idx * 0.01),
            "reinforcement_count": idx,
        }
        for idx in range(20)
    ]
    capsule_context = {
        "project_holochat": "high signal " + ("y" * 180),
        **{f"noise_{idx}": "noisy " + ("z" * 160) for idx in range(20)},
        "_password_hash": "must-not-appear",
        "api_token_note": "must-not-appear-either",
    }

    packet = HoloContextBuilder().build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
        capsule_context=capsule_context,
        life_context=life_context,
    )

    rows = {row["block_name"]: row for row in packet.metadata["context_budget"]["rows"]}
    assert "project_holochat" in packet.system_prompt
    assert "[context_budget] omitted" in packet.system_prompt
    assert "must-not-appear" not in packet.system_prompt
    assert "must-not-appear-either" not in packet.system_prompt
    assert "life-value-19" not in packet.system_prompt
    assert rows["life_context"]["token_estimate"] < 350
    assert rows["capsule_context"]["token_estimate"] < 300
    assert packet.metadata["context_budget"]["largest_blocks"]


def test_context_budget_rows_do_not_expose_raw_memory_or_search_text():
    state = HoloState(session_id="s")

    packet = HoloContextBuilder().build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
        capsule_context={"project": "secret memory value"},
        web_results="raw search result body",
    )

    budget_text = str(packet.metadata["context_budget"])
    assert "secret memory value" not in budget_text
    assert "raw search result body" not in budget_text
    assert "capsule_context" in budget_text
    assert "web_results" in budget_text


def test_context_budget_estimates_are_stable_and_find_largest_blocks():
    ledger = build_context_budget_ledger(
        [
            {"block_name": "small", "content": "abcd", "source_type": "system"},
            {"block_name": "large", "content": "x" * 41, "source_type": "memory"},
            {"block_name": "omitted", "content": "ignored", "included": False, "source_type": "search"},
        ]
    )

    rows = {row.block_name: row for row in ledger.rows}
    assert rows["small"].char_count == 4
    assert rows["small"].token_estimate == 1
    assert rows["large"].token_estimate == 11
    assert rows["omitted"].char_count == 0
    assert ledger.largest_blocks[0]["block_name"] == "large"


def test_context_budget_status_uses_env_limit(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_CONTEXT_BUDGET_TOKENS", "2")

    ledger = build_context_budget_ledger(
        [{"block_name": "large", "content": "x" * 40, "source_type": "memory"}]
    )

    assert ledger.budget_limit_tokens == 2
    assert ledger.budget_status == "over_budget"


def test_context_budget_does_not_trim_prompt_content():
    state = HoloState(session_id="s")

    packet = HoloContextBuilder().build(
        base_system_prompt="base",
        holo_state=state,
        user_message="hello",
        capsule_context={"project": "keep this memory"},
        web_results="keep this search result",
    )

    assert "keep this memory" in packet.system_prompt
    assert "keep this search result" in packet.user_message
    assert packet.metadata["context_budget"]["budget_status"] == "within_budget"
