from copy import deepcopy

from benchmark_full_gated_judge import validate_full_gated_judgment


def _artifact(total=94, admissible=True, eligible=True):
    return {
        "deterministic_score_25": 25 if admissible else 15,
        "epistemic_score_25": 23 if admissible else 18,
        "structural_score_25": 23 if admissible else 18,
        "argument_score_25": 23 if admissible else 18,
        "total_score_100": total,
        "admissible_under_local_deterministic_gate": admissible,
        "officially_eligible_for_win": eligible,
        "score_caps": [] if admissible else ["inadmissible deterministic cap"],
        "critical_failures": [] if admissible else ["semantic_gate_failure"],
        "deterministic_findings": ["deterministic compliance finding"],
        "epistemic_findings": ["epistemic source reasoning finding"],
        "structural_findings": ["structural usability finding"],
        "argument_findings": ["argument quality finding"],
    }


def _canonical_result():
    return {
        "classification": "FULL_GATED_100_POINT_JUDGE_RESULT",
        "local_deterministic_audit_by_blind": {
            "A": {"admissible": True, "failures": [], "gate_score": 39},
            "B": {
                "admissible": False,
                "failures": ["word_band", "semantic_gate_failure"],
                "gate_score": 28,
            },
        },
        "parsed_json": {
            "artifact_a": _artifact(total=94, admissible=True, eligible=True),
            "artifact_b": _artifact(total=69, admissible=False, eligible=False),
            "official_winner": "artifact_a",
            "argument_quality_winner": "artifact_a",
            "winner_reason": "Artifact A is eligible and higher scoring.",
            "confidence": "High",
            "official_judgment_valid": True,
            "rubric_compliance_note": "All four ledgers and local audit were applied.",
        },
    }


def test_canonical_full_gated_result_is_official():
    result = validate_full_gated_judgment(_canonical_result())

    assert result.official_valid is True
    assert result.classification == "OFFICIAL_FULL_GATED_100PT_VALID"
    assert result.official_winner_key == "artifact_a"
    assert result.artifact_scores["artifact_a"]["computed_total_score_100"] == 94


def test_missing_local_deterministic_audit_is_diagnostic_only():
    payload = _canonical_result()
    payload.pop("local_deterministic_audit_by_blind")

    result = validate_full_gated_judgment(payload)

    assert result.official_valid is False
    assert "local_deterministic_audit_by_blind: missing_or_not_object" in result.failures


def test_narrow_judge_without_all_four_ledgers_is_diagnostic_only():
    payload = _canonical_result()
    payload["parsed_json"]["artifact_a"].pop("argument_score_25")

    result = validate_full_gated_judgment(payload)

    assert result.official_valid is False
    assert "artifact_a.argument_score_25: missing_or_not_numeric" in result.failures
    assert "artifact_a.total_score_100: does_not_equal_four_ledgers" in result.failures


def test_noncanonical_artifacts_a_b_shape_is_diagnostic_only():
    payload = _canonical_result()
    parsed = payload["parsed_json"]
    parsed.pop("artifact_a")
    parsed.pop("artifact_b")
    parsed["artifacts"] = {
        "A": {
            "deterministic_compliance_score_25": 25,
            "epistemic_source_reasoning_score_25": 23,
            "structural_executive_usability_score_25": 24,
            "argument_quality_score_25": 23,
            "total_score_100": 95,
        },
        "B": {
            "deterministic_compliance_score_25": 15,
            "epistemic_source_reasoning_score_25": 20,
            "structural_executive_usability_score_25": 22,
            "argument_quality_score_25": 21,
            "total_score_100": 78,
        },
    }
    parsed["official_winner"] = "A"
    parsed["argument_quality_winner"] = "A"

    result = validate_full_gated_judgment(payload)

    assert result.official_valid is False
    assert "parsed_json.artifact_a: missing_or_not_object" in result.failures
    assert "parsed_json.official_winner: must_be_artifact_a_or_artifact_b" in result.failures


def test_inadmissible_artifact_cannot_be_official_winner():
    payload = _canonical_result()
    payload["parsed_json"]["official_winner"] = "artifact_b"

    result = validate_full_gated_judgment(payload)

    assert result.official_valid is False
    assert "parsed_json.official_winner: selected_artifact_not_officially_eligible" in result.failures


def test_total_must_equal_sum_of_four_ledgers():
    payload = _canonical_result()
    payload["parsed_json"]["artifact_a"] = deepcopy(payload["parsed_json"]["artifact_a"])
    payload["parsed_json"]["artifact_a"]["total_score_100"] = 99

    result = validate_full_gated_judgment(payload)

    assert result.official_valid is False
    assert "artifact_a.total_score_100: does_not_equal_four_ledgers" in result.failures
