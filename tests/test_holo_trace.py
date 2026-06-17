import json

from holo_trace import (
    HoloSearchTraceRecord,
    HoloTraceRecord,
    redact_secrets,
    save_search_trace,
    stable_context_hash,
)


def _trace() -> HoloTraceRecord:
    return HoloTraceRecord(
        session_id="session-1",
        turn_number=1,
        holo_state_id="state-1",
        holo_state_schema_version="holochat_state_v0.1",
        dna_profile="verify_4mini",
        selected_council_provider="openai",
        selected_council_model="gpt-4o-mini",
        selected_hologov_provider="google",
        selected_hologov_model="gemini-2.5-flash-lite",
        assigned_role="DIRECT_SYNTHESIS",
        route_reason="test",
        thread_health={"score": 100, "level": "GREEN", "status": "HEALTHY"},
        context_packet_hash=stable_context_hash("system", "user"),
        extra_metadata={"api_key": "secret", "nested": {"token": "abc"}},
    )


def test_trace_object_redacts_secrets():
    safe = _trace().safe_dict()

    assert safe["extra_metadata"]["api_key"] == "[REDACTED]"
    assert safe["extra_metadata"]["nested"]["token"] == "[REDACTED]"


def test_trace_object_serializes_cleanly():
    raw = _trace().to_json()
    parsed = json.loads(raw)

    assert parsed["session_id"] == "session-1"
    assert parsed["selected_council_model"] == "gpt-4o-mini"
    assert parsed["extra_metadata"]["api_key"] == "[REDACTED]"


def test_context_hash_stable_for_same_input():
    first = stable_context_hash("system", "user")
    second = stable_context_hash("system", "user")
    different = stable_context_hash("system", "different")

    assert first == second
    assert first != different
    assert len(first) == 64


def test_redact_secrets_handles_nested_values():
    redacted = redact_secrets({"Authorization": "Bearer secret", "safe": ["ok"]})

    assert redacted["Authorization"] == "[REDACTED]"
    assert redacted["safe"] == ["ok"]


def test_search_trace_save_noops_when_persistence_unavailable():
    record = HoloSearchTraceRecord(
        session_id="session-1",
        turn_number=1,
        query="current news",
        result_count=2,
    )

    assert save_search_trace(None, record) is False
