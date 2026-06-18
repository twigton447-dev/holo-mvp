import pytest
from pydantic import ValidationError

from holo_state import BatonPass, CouncilRole, GovArcState, HoloState, RequiredTools, ThreadHealth


def test_holo_state_serializes_and_deserializes_cleanly():
    state = HoloState.from_chat_turn(
        session_id="session-1",
        capsule_id="capsule-1",
        turn_number=3,
        user_message="Decide what to do next.",
        thread_health_score=74,
    )

    restored = HoloState.model_validate_json(state.model_dump_json())

    assert restored.schema_version == "holochat_state_v0.1"
    assert restored.session_id == "session-1"
    assert restored.capsule_id == "capsule-1"
    assert restored.turn_number == 3
    assert restored.thread_health.level == "GREEN"
    assert restored.gov_arc_state.current_topic == "Decide what to do next."


def test_gov_arc_state_is_owned_structured_state():
    state = HoloState(
        session_id="s",
        gov_arc_state=GovArcState(
            current_topic="web search repair",
            current_directive="show the exact decision trace",
            next_paths=["Inspect the web trace", "Separate Gov from Python", "Test the UI"],
            web_decision="checked via deterministic",
            confidence="medium",
        ),
    )

    restored = HoloState.model_validate_json(state.model_dump_json())

    assert restored.gov_arc_state.current_topic == "web search repair"
    assert restored.gov_arc_state.next_paths == [
        "Inspect the web trace",
        "Separate Gov from Python",
        "Test the UI",
    ]
    assert restored.gov_arc_state.web_decision == "checked via deterministic"


def test_required_tools_validation_rejects_unknown_tool():
    with pytest.raises(ValidationError):
        HoloState(session_id="s", required_tools=["NOT_A_TOOL"])


def test_baton_pass_defaults_are_safe():
    baton = BatonPass()

    assert baton.next_model_policy == "serial_one_model_at_a_time"
    assert baton.assigned_role == CouncilRole.DIRECT_SYNTHESIS
    assert baton.required_tools == [RequiredTools.NONE]
    assert baton.mode == "serial"


def test_thread_health_from_existing_score_status():
    health = ThreadHealth.from_score(18, status="ROTATION_RECOMMENDED", reasons=["long_thread"])

    assert health.score == 18
    assert health.level == "RED"
    assert health.status == "ROTATION_RECOMMENDED"
    assert health.reasons == ["long_thread"]
