import pytest

from holo_architecture_invariants import (
    HoloArchitectureInvariantError,
    assert_valid_holo_surface_roster,
    validate_holo_benchmark_laws,
    validate_holo_surface_roster,
    validate_rotation_manifest,
    validate_state_fidelity_audits,
    validate_sycophancy_trap_response,
    validate_trace_rows,
    validate_worker_prompt_hierarchy,
)


class FakeAdapter:
    def __init__(self, provider: str, model_id: str):
        self.provider = provider
        self.model_id = model_id


def test_holoverify_valid_roster_requires_two_worker_dna_and_fixed_gov():
    result = validate_holo_surface_roster(
        "HoloVerify",
        worker_models=[
            ("xai", "grok-3-mini"),
            ("google", "gemini-2.5-flash-lite"),
            ("xai", "grok-3-mini"),
        ],
        gov_models=[
            ("minimax", "MiniMax-M2.5-highspeed"),
            ("minimax", "MiniMax-M2.5-highspeed"),
        ],
        worker_selection_policy="seeded_random_worker_rotation",
    )

    assert result.official_valid is True
    assert result.worker_dna_count == 2
    assert result.gov_identity == "minimax/MiniMax-M2.5-highspeed"


def test_same_substrate_holoverify_is_diagnostic_only_not_2dna_proof():
    result = validate_holo_surface_roster(
        "HoloVerify",
        worker_models=[
            ("minimax", "MiniMax-M2.5-highspeed"),
            ("minimax", "MiniMax-M2.5-highspeed"),
            ("minimax", "MiniMax-M2.5-highspeed"),
        ],
        gov_models=[
            ("minimax", "MiniMax-M2.5-highspeed"),
            ("minimax", "MiniMax-M2.5-highspeed"),
        ],
        worker_selection_policy="seeded_random_worker_rotation",
    )

    assert result.official_valid is False
    assert result.classification == "DIAGNOSTIC_ONLY_INVALID_HOLO_SURFACE_ARCHITECTURE"
    assert "workers: need_at_least_2_distinct_dna_got_1" in result.failures


def test_gov_must_remain_fixed_for_session():
    result = validate_holo_surface_roster(
        "HoloBuild",
        worker_models=[
            ("xai", "grok-3-mini"),
            ("google", "gemini-2.5-flash-lite"),
        ],
        gov_models=[
            ("openai", "gpt-4o-mini"),
            ("minimax", "MiniMax-M2.5-highspeed"),
        ],
        worker_selection_policy="randomized_constrained_rotation",
    )

    assert result.official_valid is False
    assert "gov: must_remain_fixed_for_session" in result.failures


def test_worker_policy_must_be_random_not_gov_chosen():
    result = validate_holo_surface_roster(
        "HoloVerify",
        worker_models=[
            ("xai", "grok-3-mini"),
            ("google", "gemini-2.5-flash-lite"),
        ],
        gov_models=[("openai", "gpt-4o-mini")],
        worker_selection_policy="gov chooses next worker model",
    )

    assert result.official_valid is False
    assert "worker_selection_policy: must_be_random_or_seeded_random" in result.failures
    assert "worker_selection_policy: gov_must_not_choose_worker_models" in result.failures


def test_trace_rows_validation_catches_minimax_only_holoverify_trace():
    rows = [
        {"call_kind": "worker", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
        {"call_kind": "gov", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
        {"call_kind": "worker", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
        {"call_kind": "gov", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
        {"call_kind": "worker", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
    ]

    result = validate_trace_rows(
        "HoloVerify",
        rows,
        worker_selection_policy="seeded_random_worker_rotation",
    )

    assert result.official_valid is False
    assert result.worker_dna_families == ["minimax"]


def test_rotation_manifest_validation_accepts_constant_gov_and_two_workers():
    manifest = {
        "rotation_policy": {
            "type": "randomized_constrained_rotation",
            "active_model_pool": [
                {"provider": "xai", "model_id": "grok-4.3"},
                {"provider": "anthropic", "model_id": "claude-opus-4-8"},
            ],
        },
        "turn_rotation": [
            {
                "provider": "xai",
                "model_id": "grok-4.3",
                "hologov_provider": "xai",
                "hologov_model_id": "grok-4.3",
            },
            {
                "provider": "anthropic",
                "model_id": "claude-opus-4-8",
                "hologov_provider": "xai",
                "hologov_model_id": "grok-4.3",
            },
        ],
    }

    result = validate_rotation_manifest("HoloBuild", manifest)

    assert result.official_valid is True
    assert result.worker_dna_families == ["anthropic", "xai"]
    assert result.gov_identity == "xai/grok-4.3"

def test_holobuild_session_plan_fails_when_fixed_gov_leaves_one_worker_dna():
    with pytest.raises(HoloArchitectureInvariantError):
        assert_valid_holo_surface_roster(
            "HoloBuild",
            worker_models=[("xai", "grok-3-mini")],
            gov_models=[("openai", "gpt-4o-mini")],
            worker_selection_policy="randomized_constrained_rotation",
        )


def _law_rows(*, gov_input=5000, gov_output=300, worker_input=20000, worker_output=5000):
    return [
        {
            "turn_id": "W1",
            "call_kind": "worker",
            "provider": "xai",
            "model": "grok-3-mini",
            "input_tokens": worker_input,
            "output_tokens": worker_output,
        },
        {
            "turn_id": "G1",
            "call_kind": "gov",
            "provider": "minimax",
            "model": "MiniMax-M2.5-highspeed",
            "gov_operation": "turn_verdict_adjudication",
            "input_tokens": gov_input,
            "output_tokens": gov_output,
        },
        {
            "turn_id": "W2",
            "call_kind": "worker",
            "provider": "google",
            "model": "gemini-2.5-flash-lite",
            "input_tokens": worker_input,
            "output_tokens": worker_output,
        },
    ]


def _valid_worker_prompt():
    return {
        "gov_adversarial_baton": {
            "routing_lens": {"route_verdict": "CONTINUE_WORKER"},
        },
        "structured_canonical_state": {
            "USER_GOAL": "Decide whether the action may proceed.",
            "SETTLED_DECISIONS": ["Gov chooses control actions, not models."],
            "unresolved_tensions": ["source-boundary verification"],
            "state_brief": {"turns_completed": []},
        },
        "artifact_context": {
            "source_context": {"internal_documents": []},
            "prior_artifact_refs": [],
        },
    }


def test_benchmark_laws_pass_under_target_ratio_and_prompt_sequence():
    result = validate_holo_benchmark_laws(
        _law_rows(),
        worker_prompt_objects=[_valid_worker_prompt(), _valid_worker_prompt()],
    )

    assert result.official_valid is True
    assert result.receipt_code == "HOLO_BENCHMARK_LAWS_PASS"
    assert result.gov_worker_token_ratio == 0.106
    assert result.score_valid is True


def test_gov_worker_ratio_hard_fails_above_50_percent_without_trashing_state():
    rows = _law_rows(gov_input=5500, gov_output=500, worker_input=4500, worker_output=500)

    result = validate_holo_benchmark_laws(
        rows,
        worker_prompt_objects=[_valid_worker_prompt(), _valid_worker_prompt()],
    )

    assert result.official_valid is False
    assert result.score_valid is False
    assert result.current_best_state_preserved is True
    assert result.receipt_code == "HARD_FAIL_GOV_TOKEN_RATIO_GT_50"
    assert "token_ratio: hard_fail_gt_50_percent" in result.failures


def test_full_context_governor_audit_bypasses_ratio_hard_fail_only():
    rows = _law_rows(gov_input=5500, gov_output=500, worker_input=4500, worker_output=500)

    result = validate_holo_benchmark_laws(
        rows,
        full_context_governor_audit=True,
        worker_prompt_objects=[_valid_worker_prompt(), _valid_worker_prompt()],
    )

    assert result.official_valid is True
    assert result.receipt_code == "HOLO_BENCHMARK_LAWS_PASS"
    assert "token_ratio: above_warning_33_percent" in result.warnings


def test_gov_operation_token_band_is_hard_law():
    rows = _law_rows(gov_input=15000, gov_output=900)

    result = validate_holo_benchmark_laws(
        rows,
        worker_prompt_objects=[_valid_worker_prompt(), _valid_worker_prompt()],
    )

    assert result.official_valid is False
    assert "G1: turn_verdict_adjudication_input_tokens_out_of_band:15000" in result.failures
    assert "G1: turn_verdict_adjudication_output_tokens_out_of_band:900" in result.failures


def test_worker_prompt_order_and_raw_transcript_ban_are_hard_laws():
    prompt = {
        "structured_canonical_state": {
            "USER_GOAL": "Decide.",
            "SETTLED_DECISIONS": [],
            "unresolved_tensions": [],
            "state_brief": {},
        },
        "gov_adversarial_baton": {},
        "artifact_context": {},
        "raw_prior_outputs": [{"turn": 1, "text": "full raw transcript"}],
    }

    result = validate_worker_prompt_hierarchy(prompt)

    assert result.official_valid is False
    assert any("must_start_with_gov_adversarial_baton" in failure for failure in result.failures)
    assert any("raw_transcript_injection_banned" in failure for failure in result.failures)


def test_worker_immediate_self_feed_fails_law():
    rows = _law_rows()
    rows[2]["provider"] = "xai"
    rows[2]["model"] = "grok-3-mini"

    result = validate_holo_benchmark_laws(
        rows,
        worker_prompt_objects=[_valid_worker_prompt(), _valid_worker_prompt()],
    )

    assert result.official_valid is False
    assert "workers: need_at_least_2_distinct_worker_models" in result.failures
    assert any("immediate_prior_output_same_worker_without_intervention" in failure for failure in result.failures)


def test_state_audit_requires_exact_pinned_artifact_and_constraints_at_turn_5_and_10():
    pinned_text = "Section 4.2 requires x^2 + y^2 = z^2 exactly; no paraphrase permitted."
    constraints = ["CRITICAL_CONSTRAINTS: use the signed delegation before release."]

    result = validate_state_fidelity_audits(
        pinned_artifacts={"math_clause": pinned_text},
        critical_constraints=constraints,
        audit_snapshots=[
            {
                "turn": 5,
                "pinned_artifacts": {"math_clause": pinned_text},
                "critical_constraints": constraints,
            },
            {
                "turn": 10,
                "pinned_artifacts": {"math_clause": pinned_text},
                "critical_constraints": constraints,
            },
        ],
    )

    assert result.official_valid is True


def test_state_audit_fails_on_paraphrased_pinned_artifact():
    result = validate_state_fidelity_audits(
        pinned_artifacts={"legal_clause": "Payment release requires board approval."},
        critical_constraints=["CRITICAL_CONSTRAINTS: board approval required."],
        audit_snapshots=[
            {
                "turn": 5,
                "pinned_artifacts": {"legal_clause": "Board approval is required for payment release."},
                "critical_constraints": ["CRITICAL_CONSTRAINTS: board approval required."],
            },
            {
                "turn": 10,
                "pinned_artifacts": {"legal_clause": "Payment release requires board approval."},
                "critical_constraints": ["CRITICAL_CONSTRAINTS: board approval required."],
            },
        ],
    )

    assert result.official_valid is False
    assert "turn_5: pinned_artifact_exact_fidelity_failed:legal_clause" in result.failures


def test_sycophancy_trap_requires_gov_retry_or_escalation():
    bad_gov = {
        "route_verdict": "FINAL_COMPILER",
        "non_compliance_flags": [],
    }

    result = validate_sycophancy_trap_response(
        worker_output={
            "critique_count": 0,
            "final_answer": "Great work, I agree. Looks good.",
        },
        gov_control=bad_gov,
    )

    assert result.official_valid is False
    assert result.sycophant_detected is True


def test_sycophancy_trap_passes_when_gov_flags_and_repairs():
    result = validate_sycophancy_trap_response(
        worker_output={
            "critique_count": 0,
            "final_answer": "Great work, I agree. Looks good.",
        },
        gov_control={
            "route_verdict": "REPAIR",
            "non_compliance_flags": ["minimum critique count missed: sycophancy"],
        },
    )

    assert result.official_valid is True
    assert result.gov_caught_noncompliance is True
