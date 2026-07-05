from copy import deepcopy

from benchmark_dynamic_gov_router import validate_dynamic_gov_router_control


def _base_control():
    return {
        "gov_mode": "CONTROL_ROUTER",
        "route_verdict": "REPAIR",
        "burn_decision": {
            "continue_turns": True,
            "reason": "One blocker remains; next turn has high repair value.",
            "estimated_value_of_next_turn": "HIGH",
        },
        "targeted_hunter": {},
        "delta_ledger": [],
        "deterministic_form_actuation": {},
        "open_blockers": [
            {
                "blocker": "word_band_over",
                "required_repair": "compress to target band",
            }
        ],
        "final_compiler_allowed": False,
    }


def test_basic_repair_control_is_valid():
    result = validate_dynamic_gov_router_control(_base_control())

    assert result.official_valid is True
    assert result.classification == "OFFICIAL_DYNAMIC_GOV_ROUTER_VALID"
    assert result.route_verdict == "REPAIR"


def test_gov_must_not_choose_models_at_top_level():
    payload = _base_control()
    payload["selected_model"] = "claude-haiku-4-5-20251001"

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is False
    assert "control.selected_model: gov_must_not_choose_models" in result.failures


def test_gov_must_not_choose_models_inside_nested_baton():
    payload = _base_control()
    payload["targeted_hunter"] = {
        "hunter_target": "Section 4",
        "attack_question": "Find the authority laundering defect.",
        "success_condition": "Return defect or certification.",
        "must_not_discuss": ["style"],
        "worker_model": "grok-3-mini",
    }
    payload["route_verdict"] = "TARGETED_HUNTER"

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is False
    assert "control.targeted_hunter.worker_model: gov_must_not_choose_models" in result.failures


def test_targeted_hunter_requires_specific_attack_contract():
    payload = _base_control()
    payload["route_verdict"] = "TARGETED_HUNTER"
    payload["targeted_hunter"] = {
        "hunter_target": "Section 4 vendor-master exception",
        "attack_question": "Does the section convert a narrow exception into broad authority?",
        "must_not_discuss": ["general summary", "style"],
        "success_condition": "Identify source-grounded defect or certify none found.",
    }

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is True
    assert result.route_verdict == "TARGETED_HUNTER"


def test_targeted_hunter_missing_attack_question_is_invalid():
    payload = _base_control()
    payload["route_verdict"] = "TARGETED_HUNTER"
    payload["targeted_hunter"] = {
        "hunter_target": "Section 4",
        "must_not_discuss": [],
        "success_condition": "Return defect or certification.",
    }

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is False
    assert "targeted_hunter.attack_question: required_for_targeted_hunter" in result.failures


def test_early_exit_requires_clean_evidence_and_no_open_blockers():
    payload = _base_control()
    payload["route_verdict"] = "EARLY_EXIT_TO_FINAL_COMPILER"
    payload["burn_decision"] = {
        "continue_turns": False,
        "reason": "Artifact is admissible and next turn has low marginal value.",
        "estimated_value_of_next_turn": "LOW",
    }
    payload["open_blockers"] = []
    payload["final_compiler_allowed"] = True
    payload["early_exit_evidence"] = {
        "deterministic_gate_passed": True,
        "required_sections_present": True,
        "source_ids_valid": True,
        "semantic_trap_gates_passed": True,
        "no_material_drift": True,
    }

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is True
    assert result.final_compiler_allowed is True


def test_early_exit_with_open_blocker_is_invalid():
    payload = _base_control()
    payload["route_verdict"] = "EARLY_EXIT_TO_FINAL_COMPILER"
    payload["burn_decision"] = {
        "continue_turns": False,
        "reason": "Premature exit.",
        "estimated_value_of_next_turn": "LOW",
    }
    payload["final_compiler_allowed"] = True
    payload["early_exit_evidence"] = {
        "deterministic_gate_passed": True,
        "required_sections_present": True,
        "source_ids_valid": True,
        "semantic_trap_gates_passed": True,
        "no_material_drift": True,
    }

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is False
    assert "open_blockers: must_be_empty_for_final_compiler_route" in result.failures


def test_high_severity_drift_blocks_final_compiler():
    payload = _base_control()
    payload["route_verdict"] = "EARLY_EXIT_TO_FINAL_COMPILER"
    payload["burn_decision"] = {
        "continue_turns": False,
        "reason": "Premature exit.",
        "estimated_value_of_next_turn": "LOW",
    }
    payload["open_blockers"] = []
    payload["final_compiler_allowed"] = True
    payload["early_exit_evidence"] = {
        "deterministic_gate_passed": True,
        "required_sections_present": True,
        "source_ids_valid": True,
        "semantic_trap_gates_passed": True,
        "no_material_drift": True,
    }
    payload["delta_ledger"] = [
        {
            "claim_or_action": "limited holding notice",
            "prior_position": "non-admission status update only",
            "current_position": "customer-facing exposure language",
            "drift_class": "ACTION_BOUNDARY_DRIFT",
            "severity": "HIGH",
            "required_repair": "restore non-admission boundary",
        }
    ]

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is False
    assert result.high_severity_drift_count == 1
    assert "delta_ledger: high_or_critical_drift_blocks_final_compiler_route" in result.failures


def test_high_severity_drift_requires_repair_if_not_final_route():
    payload = deepcopy(_base_control())
    payload["final_compiler_allowed"] = True
    payload["delta_ledger"] = [
        {
            "claim_or_action": "holding notice",
            "prior_position": "non-admission",
            "current_position": "admission",
            "drift_class": "ACTION_BOUNDARY_DRIFT",
            "severity": "CRITICAL",
            "required_repair": "restore boundary",
        }
    ]

    result = validate_dynamic_gov_router_control(payload)

    assert result.official_valid is False
    assert "final_compiler_allowed: high_or_critical_drift_requires_repair_or_fail_closed" in result.failures
