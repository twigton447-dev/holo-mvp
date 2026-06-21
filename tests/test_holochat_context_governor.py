from holochat_context_governor import (
    HOLOCHAT_STATE_CONTEXT_KEY,
    audit_canonical_state_object,
    build_baton_pass,
    build_holochat_state,
    generate_auto_reseed_payload,
    load_state_from_capsule_context,
    merge_artifact_registry,
    should_auto_compact,
    state_context_value,
    update_rolling_summary,
)
from holo_state import HoloState, RequiredTools


def test_state_object_schema_creation():
    state = build_holochat_state(
        session_id="session-1",
        capsule_id="capsule-1",
        turn_number=1,
        user_message="New goal: maintain continuity. Do not call providers.",
        response_text="Created the local state path.",
    )

    canonical = state.canonical_object()

    assert canonical["USER_GOAL"].startswith("New goal")
    assert canonical["LATEST_INPUT_SUMMARY"].startswith("New goal")
    assert canonical["CRITICAL_CONSTRAINTS"] == ["Do not call providers."]
    assert canonical["REQUIRED_TOOLS"] == ["NONE"]
    assert canonical["BATON_PASS"]["current_task"].startswith("New goal")
    assert state.state_audit.trusted is True
    assert state.state_audit.state_hash


def test_rolling_summary_update_keeps_compact_state():
    summary = update_rolling_summary(
        "Prior decision: use HoloBrain.",
        latest_input_summary="Add auto-reseed.",
        response_summary="Implemented state hooks.",
        limit=120,
    )

    assert "Add auto-reseed" in summary
    assert "Implemented state hooks" in summary
    assert len(summary) <= 120


def test_auto_compact_trigger_uses_budget_pressure():
    assert should_auto_compact(
        context_budget={
            "budget_status": "within_budget",
            "budget_limit_tokens": 1000,
            "total_token_estimate": 850,
        },
        thread_health_level="GREEN",
        thread_health_score=80,
    ) is True


def test_auto_reseed_payload_generation_is_bounded_and_structured():
    state = build_holochat_state(
        session_id="session-1",
        turn_number=2,
        user_message="Continue the current mission.",
        response_text="Next action is ready.",
    )

    payload = generate_auto_reseed_payload(state, max_chars=1400)

    assert payload.startswith("HOLOCHAT AUTO-RESEED")
    assert "rolling_summary:" in payload
    assert "baton_pass:" in payload
    assert "Retrieve scoped artifacts by ID only when needed" in payload
    assert len(payload) <= 1400


def test_artifact_registry_reference_preservation():
    merged = merge_artifact_registry(
        [{"artifact_id": "artifact-1", "title": "Old", "status": "available_by_id"}],
        [{"artifact_id": "artifact-2", "title": "New", "content_hash": "abc123", "type": "html"}],
    )

    assert [item["artifact_id"] for item in merged] == ["artifact-1", "artifact-2"]
    assert merged[1]["hash"] == "abc123"
    assert merged[1]["status"] == "available_by_id"


def test_baton_pass_generation():
    baton = build_baton_pass(
        current_task="Patch continuity",
        next_action="Run tests",
        unresolved_tensions=["Branch is recovered but stale folder remains"],
        artifact_registry=[{"artifact_id": "artifact-1"}],
        constraints=["No push"],
        required_tools=[RequiredTools.NONE],
    )

    assert baton.current_task == "Patch continuity"
    assert baton.next_action == "Run tests"
    assert baton.relevant_artifact_ids == ["artifact-1"]
    assert baton.constraints_for_next_assistant == ["No push"]


def test_audit_failure_on_missing_required_fields():
    state = HoloState(session_id="session-1")
    broken = state.canonical_object()
    broken.pop("USER_GOAL")

    audit = audit_canonical_state_object(broken)

    assert audit.trusted is False
    assert audit.missing_required_fields == ["USER_GOAL"]


def test_no_secret_env_leakage_in_reseed_output():
    state = build_holochat_state(
        session_id="session-1",
        turn_number=1,
        user_message="Use OPENAI_API_KEY=sk-testsecret123456789 but do not leak it.",
        response_text="Stored no secret values.",
    )

    payload = generate_auto_reseed_payload(state)

    assert "sk-testsecret" not in payload
    assert "OPENAI_API_KEY=[REDACTED]" in payload


def test_state_context_round_trips_through_capsule_context():
    state = build_holochat_state(
        session_id="session-1",
        capsule_id="capsule-1",
        turn_number=1,
        user_message="Remember this state.",
    )
    context = {HOLOCHAT_STATE_CONTEXT_KEY: state_context_value(state)}

    restored = load_state_from_capsule_context(context)

    assert restored is not None
    assert restored.state_id == state.state_id
