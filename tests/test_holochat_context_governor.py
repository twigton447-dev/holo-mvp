from holochat_context_governor import (
    HOLOCHAT_STATE_CONTEXT_KEY,
    HoloBrainInjectionMode,
    audit_canonical_state_object,
    build_baton_pass,
    build_holobrain_injection_plan,
    build_holobrain_injection_payload,
    build_holochat_state,
    generate_auto_reseed_payload,
    has_meaningful_holobrain_delta,
    load_state_from_capsule_context,
    merge_artifact_registry,
    retrieve_holobrain_artifact_body,
    select_holobrain_injection_mode,
    should_auto_compact,
    state_context_value,
    update_rolling_summary,
)
from holo_state import HoloState, RequiredTools, StateAudit


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


def test_holobrain_baton_only_on_normal_turn():
    state = build_holochat_state(
        session_id="session-1",
        turn_number=3,
        user_message="New goal: keep the HoloGov-C patch narrow.",
    )

    mode = select_holobrain_injection_mode(
        state,
        thread_status="HEALTHY",
        context_budget={"budget_status": "within_budget"},
        fresh_thread=False,
        recovery_needed=False,
        topic_shift=False,
        artifact_needed=False,
    )

    assert mode == HoloBrainInjectionMode.BATON_ONLY


def test_holobrain_full_reseed_on_recovery():
    state = build_holochat_state(
        session_id="session-1",
        turn_number=3,
        user_message="New goal: preserve continuity.",
    )

    mode = select_holobrain_injection_mode(
        state,
        thread_status="HEALTHY",
        context_budget={"budget_status": "within_budget"},
        fresh_thread=False,
        recovery_needed=True,
        topic_shift=False,
        artifact_needed=False,
    )

    assert mode == HoloBrainInjectionMode.FULL_RESEED


def test_unrelated_topic_shift_does_not_inject_full_reseed():
    state = build_holochat_state(
        session_id="session-1",
        turn_number=3,
        user_message="New goal: preserve continuity.",
    )

    mode = select_holobrain_injection_mode(
        state,
        thread_status="unrelated topic shift",
        context_budget={"budget_status": "within_budget"},
        fresh_thread=False,
        recovery_needed=False,
        topic_shift=True,
        artifact_needed=False,
    )

    assert mode == HoloBrainInjectionMode.HASHES_ONLY


def test_untrusted_state_audit_uses_hashes_only():
    state = build_holochat_state(
        session_id="session-1",
        turn_number=3,
        user_message="New goal: preserve continuity.",
    )
    state.state_audit = StateAudit(trusted=False, state_hash="hash-1")

    mode = select_holobrain_injection_mode(
        state,
        thread_status="HEALTHY",
        context_budget={"budget_status": "within_budget"},
        fresh_thread=True,
        recovery_needed=True,
        topic_shift=False,
        artifact_needed=False,
    )

    assert mode == HoloBrainInjectionMode.HASHES_ONLY


def test_holobrain_injected_chars_stay_under_configured_budget(monkeypatch):
    monkeypatch.setenv("HOLOCHAT_HOLOBRAIN_INJECTION_MAX_CHARS", "420")
    state = build_holochat_state(
        session_id="session-1",
        turn_number=3,
        user_message="New goal: preserve a very long continuity packet. Do not call providers.",
        response_text="x" * 2000,
    )

    plan = build_holobrain_injection_plan(
        state,
        thread_status="HEALTHY",
        context_budget={"budget_status": "within_budget"},
        fresh_thread=True,
        recovery_needed=False,
        topic_shift=False,
        artifact_needed=False,
    )

    assert plan.mode == HoloBrainInjectionMode.FULL_RESEED
    assert plan.char_count <= 420
    assert plan.token_estimate == (plan.char_count + 3) // 4


def test_holobrain_artifacts_are_refs_by_default():
    ref = merge_artifact_registry(
        [],
        [{
            "artifact_id": "artifact-1",
            "title": "Continuity Doc",
            "type": "html",
            "content": "<html><body>FULL BODY SHOULD NOT ENTER PROMPT</body></html>",
            "summary": "Short artifact summary.",
            "status": "available_by_id",
        }],
    )[0]

    payload = build_holobrain_injection_payload(
        HoloState(
            session_id="session-1",
            artifact_registry=[ref],
            state_audit=StateAudit(
                trusted=True,
                state_hash="state-hash",
                artifact_registry_hash="registry-hash",
            ),
        ),
        HoloBrainInjectionMode.ARTIFACT_REFS,
    )

    assert "artifact-1" in payload
    assert "Short artifact summary." in payload
    assert "FULL BODY SHOULD NOT ENTER PROMPT" not in payload


def test_full_artifact_body_is_retrieved_only_when_needed():
    class ArtifactBrain:
        def __init__(self):
            self.calls = 0

        def get_artifact(self, capsule_id, artifact_id):
            self.calls += 1
            return {"content": "full artifact body"}

    brain = ArtifactBrain()

    assert retrieve_holobrain_artifact_body(
        brain,
        "capsule-1",
        "artifact-1",
        full_body_needed=False,
    ) is None
    assert brain.calls == 0
    assert retrieve_holobrain_artifact_body(
        brain,
        "capsule-1",
        "artifact-1",
        full_body_needed=True,
    ) == "full artifact body"
    assert brain.calls == 1


def test_meaningful_delta_ignores_routine_turn_without_durable_change():
    previous = build_holochat_state(
        session_id="session-1",
        turn_number=1,
        user_message="New goal: keep the state gate narrow.",
        response_text="ok",
    )
    candidate = build_holochat_state(
        session_id="session-1",
        turn_number=2,
        user_message="Continue.",
        response_text="ok",
        previous_state=previous,
    )

    assert has_meaningful_holobrain_delta(previous, candidate) is False
    assert candidate.rolling_summary == previous.rolling_summary
