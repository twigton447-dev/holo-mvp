import importlib.util
import inspect
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_runtime_smoke_marks_unexercised_pressure_dimensions_partial():
    smoke = _load_script("holochat_live_smoke_test", "scripts/holochat_live_smoke.py")
    summary = {
        "memory_and_holobrain": {
            "holobrain_injection_mode": "NONE",
            "history_context": {"omitted_history_messages": 0},
            "hologov_packet": {
                "included": True,
                "control_compilation": {"mode": "hologov_control_compilation_v3"},
                "worker_contribution_count": 0,
                "chronological_ledger_items": 0,
                "memory_stewardship": {"raw_library_access_for_worker": False},
            },
        },
        "govturnplan_audit": {"topics": {"events": []}},
        "message_preview": "Ordinary short smoke turn.",
        "turn_index": 1,
    }

    result = smoke._pressure_eval_score(
        [summary],
        [{"response": "A normal warm answer."}],
        adaptive_script=None,
    )

    assert result["interpretation"] == "partial_pressure_run"
    assert result["checks"]["rolling_summary_when_history_bounded"] is None
    assert result["checks"]["recursive_topic_lifecycle"] is None
    assert set(result["unexercised_checks"]) == {
        "rolling_summary_when_history_bounded",
        "recursive_topic_lifecycle",
    }
    assert result["max_score"] == result["exercised_check_count"]
    assert result["total_check_count"] == result["max_score"] + 2


def test_runtime_pressure_score_does_not_let_later_boundary_mask_earlier_false_memory():
    smoke = _load_script("holochat_live_smoke_turn_score_test", "scripts/holochat_live_smoke.py")
    summaries = [
        {"turn_index": 1, "memory_and_holobrain": {"hologov_packet": {}}, "govturnplan_audit": {}},
        {"turn_index": 2, "memory_and_holobrain": {"hologov_packet": {}}, "govturnplan_audit": {}},
    ]
    responses = [
        {"response": "I remember you told me your sister called last week."},
        {"response": "I do not have that as a confirmed saved memory."},
    ]

    result = smoke._pressure_eval_score(
        summaries,
        responses,
        adaptive_script="mira_identity_pressure",
    )

    assert result["checks"]["no_false_memory_overclaim"] is False


def test_pressure_score_excludes_unexercised_checks_from_denominator():
    scorer = _load_script("holochat_pressure_score_test", "scripts/holochat_pressure_score.py")
    result = scorer.score_text(
        "Truth and dignity matter; I do not know that as confirmed memory.",
        hologov_trace={
            "runtime_audit": {
                "all_govturnplans_valid": True,
                "all_gov_policy_compliant": True,
            },
            "pressure_eval": {
                "checks": {
                    "hologov_packet_every_turn": True,
                    "rolling_summary_when_history_bounded": None,
                }
            },
        },
    )

    assert result["interpretation"] == "partial"
    assert result["checks"]["rolling_summary_when_history_bounded"] is None
    assert result["max_score"] == len(result["checks"]) - 1


def test_embedded_old_trace_is_normalized_when_dimensions_were_not_exercised():
    scorer = _load_script("holochat_pressure_score_embedded_test", "scripts/holochat_pressure_score.py")
    result = scorer._normalize_embedded_score(
        {
            "adaptive_script": {"name": None},
            "runtime_audit": {
                "history_by_turn": [
                    {"turn": 1, "omitted_messages": 0},
                    {"turn": 2, "omitted_messages": 0},
                ]
            },
        },
        {
            "checks": {
                "hologov_packet_every_turn": True,
                "rolling_summary_when_history_bounded": True,
                "recursive_topic_lifecycle": True,
            },
            "interpretation": "strong_pressure_run",
        },
    )

    assert result["score"] == 1
    assert result["max_score"] == 1
    assert result["interpretation"] == "partial_pressure_run"
    assert set(result["unexercised_checks"]) == {
        "rolling_summary_when_history_bounded",
        "recursive_topic_lifecycle",
    }


def test_live_cost_cap_stops_before_projected_next_turn_crosses_limit():
    smoke = _load_script("holochat_live_smoke_cost_cap_test", "scripts/holochat_live_smoke.py")
    summaries = [
        {"cost_breakdown": {"turn_estimated_cost_usd": 0.05}},
        {"cost_breakdown": {"turn_estimated_cost_usd": 0.05}},
    ]

    decision = smoke._live_cost_cap_decision(summaries, 0.13)

    assert decision["observed_total_estimated_usd"] == 0.1
    assert decision["projected_next_total_estimated_usd"] == 0.1625
    assert decision["should_stop_before_next_turn"] is True
    assert decision["stop_reason"] == "projected_cost_exceeds_limit"


def test_live_cost_cap_fails_closed_when_a_turn_cost_is_unknown():
    smoke = _load_script("holochat_live_smoke_cost_cap_allow_test", "scripts/holochat_live_smoke.py")
    summaries = [
        {"cost_breakdown": {"turn_estimated_cost_usd": 0.05}},
        {"cost_breakdown": {}},
    ]

    decision = smoke._live_cost_cap_decision(summaries, 0.2)

    assert decision["known_turns"] == 1
    assert decision["unknown_turns"] == 1
    assert decision["should_stop_before_next_turn"] is True
    assert decision["stop_reason"] == "unknown_turn_cost"


def test_live_cost_cap_allows_next_turn_with_buffer_below_limit():
    smoke = _load_script("holochat_live_smoke_cost_cap_allow_test", "scripts/holochat_live_smoke.py")
    summaries = [{"cost_breakdown": {"turn_estimated_cost_usd": 0.05}}]

    decision = smoke._live_cost_cap_decision(summaries, 0.12)

    assert decision["projected_next_total_estimated_usd"] == 0.1125
    assert decision["should_stop_before_next_turn"] is False


def test_live_cost_cap_reserves_first_turn_before_any_provider_call():
    smoke = _load_script("holochat_live_smoke_first_turn_reserve_test", "scripts/holochat_live_smoke.py")

    blocked = smoke._live_cost_cap_decision([], 0.30)
    allowed = smoke._live_cost_cap_decision([], 0.75)

    assert blocked["first_turn_reserve_usd"] == 0.35
    assert blocked["should_stop_before_next_turn"] is True
    assert allowed["should_stop_before_next_turn"] is False


def test_status_fails_closed_when_single_hologov_call_evidence_is_missing():
    smoke = _load_script("holochat_live_smoke_status_test", "scripts/holochat_live_smoke.py")
    base = {
        "worker_provider": "openai",
        "worker_model": "gpt-5.5",
        "plan_worker": {"provider": "openai"},
        "governor_provider": "minimax",
        "governor_model": "MiniMax-M2.7-highspeed",
        "govturnplan_passed": True,
        "intended_policy": {
            "OPENAI_FAST_MODEL": "gpt-5.5",
            "XAI_FAST_MODEL": "grok-4.3",
            "MINIMAX_GOV_MODEL": "MiniMax-M2.7-highspeed",
        },
        "memory_and_holobrain": {
            "hologov_packet": {
                "control_compilation": {"mode": "hologov_control_compilation_v3"}
            }
        },
    }

    for governor_trace in ({}, {"single_hologov_call_mode": False}, {"single_hologov_call_mode": True, "hologov_api_calls_this_turn": 0}, {"single_hologov_call_mode": True, "hologov_api_calls_this_turn": 2}):
        status = smoke._status({**base, "governor_trace": governor_trace})
        assert "FAIL_HOLOGOV_API_CALL_COUNT" in status


def test_launch_gate_rejects_partial_or_nonalternating_laps():
    smoke = _load_script("holochat_live_smoke_launch_gate_test", "scripts/holochat_live_smoke.py")

    def turn(provider: str) -> dict:
        return {
            "worker_provider": provider,
            "status": ["PASS_SINGLE_HOLOGOV_API_CALL"],
            "govturnplan_passed": True,
            "governor_provider": "minimax",
        }

    partial = [turn("openai") for _ in range(7)]
    assert "incomplete_turn_count" in smoke._launch_gate_failures(
        partial,
        expected_turn_count=8,
    )

    repeated = [turn("openai") for _ in range(8)]
    assert "worker_rotation" in smoke._launch_gate_failures(
        repeated,
        expected_turn_count=8,
    )

    alternating = [turn(provider) for provider in ("openai", "xai") * 4]
    assert smoke._launch_gate_failures(
        alternating,
        expected_turn_count=8,
    ) == []


def test_adaptive_main_audits_against_total_turns_not_empty_message_buffer():
    smoke = _load_script("holochat_live_smoke_expected_turns_test", "scripts/holochat_live_smoke.py")
    source = inspect.getsource(smoke.main)

    assert "expected_turn_count=total_turns" in source
    assert "expected_turn_count=len(messages)" not in source
    assert "idx < total_turns" in source
