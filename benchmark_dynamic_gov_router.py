#!/usr/bin/env python3
"""
Provider-free validator for the D11-lock Dynamic Gov Router contract.

The contract is intentionally narrow:

    Gov does not choose models. Gov chooses control actions.

Model order/randomization is owned by the run lock. Gov may route the next
control move: repair, preserve, targeted hunter, early exit, final compiler,
or fail closed. This validator decides whether a saved Gov control object is
allowed to count as compliant with the dynamic-router architecture.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


ALLOWED_ROUTE_VERDICTS = {
    "CONTINUE",
    "REPAIR",
    "TARGETED_HUNTER",
    "PRESERVE_LOCKED",
    "EARLY_EXIT_TO_FINAL_COMPILER",
    "FINAL_COMPILER",
    "FAIL_CLOSED",
}

ALLOWED_BURN_VALUES = {"LOW", "MEDIUM", "HIGH"}
ALLOWED_DRIFT_SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

FORBIDDEN_MODEL_SELECTION_KEYS = {
    "model",
    "model_id",
    "model_choice",
    "model_selection",
    "next_model",
    "selected_model",
    "selected_provider",
    "provider",
    "provider_choice",
    "worker_model",
}

REQUIRED_TOP_LEVEL_FIELDS = (
    "gov_mode",
    "route_verdict",
    "burn_decision",
    "targeted_hunter",
    "delta_ledger",
    "deterministic_form_actuation",
    "open_blockers",
    "final_compiler_allowed",
)


@dataclass(frozen=True)
class DynamicGovRouterValidation:
    official_valid: bool
    classification: str
    failures: list[str]
    route_verdict: str | None
    final_compiler_allowed: bool | None
    high_severity_drift_count: int


def _is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def _forbidden_model_keys(payload: Any, path: str = "control") -> list[str]:
    failures: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if key_text in FORBIDDEN_MODEL_SELECTION_KEYS:
                failures.append(f"{child_path}: gov_must_not_choose_models")
            failures.extend(_forbidden_model_keys(value, child_path))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            failures.extend(_forbidden_model_keys(item, f"{path}[{index}]"))
    return failures


def _validate_burn_decision(payload: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    burn = payload.get("burn_decision")
    if not _is_mapping(burn):
        return ["burn_decision: missing_or_not_object"]

    if not isinstance(burn.get("continue_turns"), bool):
        failures.append("burn_decision.continue_turns: missing_or_not_bool")
    if burn.get("estimated_value_of_next_turn") not in ALLOWED_BURN_VALUES:
        failures.append("burn_decision.estimated_value_of_next_turn: invalid")
    if not str(burn.get("reason", "")).strip():
        failures.append("burn_decision.reason: missing_or_empty")
    return failures


def _validate_targeted_hunter(payload: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    route = payload.get("route_verdict")
    hunter = payload.get("targeted_hunter")
    if not _is_mapping(hunter):
        return ["targeted_hunter: missing_or_not_object"]

    if route != "TARGETED_HUNTER":
        return failures

    for field in ("hunter_target", "attack_question", "success_condition"):
        if not str(hunter.get(field, "")).strip():
            failures.append(f"targeted_hunter.{field}: required_for_targeted_hunter")

    must_not_discuss = hunter.get("must_not_discuss")
    if not isinstance(must_not_discuss, list):
        failures.append("targeted_hunter.must_not_discuss: missing_or_not_list")
    return failures


def _validate_delta_ledger(payload: Mapping[str, Any]) -> tuple[list[str], int]:
    failures: list[str] = []
    ledger = payload.get("delta_ledger")
    if not isinstance(ledger, list):
        return ["delta_ledger: missing_or_not_list"], 0

    high_count = 0
    required = (
        "claim_or_action",
        "prior_position",
        "current_position",
        "drift_class",
        "severity",
        "required_repair",
    )
    for index, entry in enumerate(ledger):
        if not _is_mapping(entry):
            failures.append(f"delta_ledger[{index}]: not_object")
            continue
        for field in required:
            if not str(entry.get(field, "")).strip():
                failures.append(f"delta_ledger[{index}].{field}: missing_or_empty")
        severity = entry.get("severity")
        if severity not in ALLOWED_DRIFT_SEVERITIES:
            failures.append(f"delta_ledger[{index}].severity: invalid")
        if severity in {"HIGH", "CRITICAL"}:
            high_count += 1
    return failures, high_count


def _validate_early_exit(payload: Mapping[str, Any], high_drift_count: int) -> list[str]:
    failures: list[str] = []
    route = payload.get("route_verdict")
    final_allowed = payload.get("final_compiler_allowed")
    open_blockers = payload.get("open_blockers")
    evidence = payload.get("early_exit_evidence")

    if final_allowed is not None and not isinstance(final_allowed, bool):
        failures.append("final_compiler_allowed: missing_or_not_bool")
    if not isinstance(open_blockers, list):
        failures.append("open_blockers: missing_or_not_list")

    if route not in {"EARLY_EXIT_TO_FINAL_COMPILER", "FINAL_COMPILER"}:
        if high_drift_count and final_allowed is True:
            failures.append("final_compiler_allowed: high_or_critical_drift_requires_repair_or_fail_closed")
        return failures

    if final_allowed is not True:
        failures.append("final_compiler_allowed: required_true_for_final_compiler_route")
    if open_blockers:
        failures.append("open_blockers: must_be_empty_for_final_compiler_route")
    if high_drift_count:
        failures.append("delta_ledger: high_or_critical_drift_blocks_final_compiler_route")
    if not _is_mapping(evidence):
        return failures + ["early_exit_evidence: missing_or_not_object"]

    required_true = (
        "deterministic_gate_passed",
        "required_sections_present",
        "source_ids_valid",
        "semantic_trap_gates_passed",
        "no_material_drift",
    )
    for field in required_true:
        if evidence.get(field) is not True:
            failures.append(f"early_exit_evidence.{field}: required_true_for_final_compiler_route")
    return failures


def validate_dynamic_gov_router_control(control: Mapping[str, Any]) -> DynamicGovRouterValidation:
    failures: list[str] = []

    if not _is_mapping(control):
        return DynamicGovRouterValidation(
            official_valid=False,
            classification="DIAGNOSTIC_ONLY_INVALID_DYNAMIC_GOV_ROUTER",
            failures=["control: missing_or_not_object"],
            route_verdict=None,
            final_compiler_allowed=None,
            high_severity_drift_count=0,
        )

    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in control:
            failures.append(f"{field}: missing")

    if control.get("gov_mode") != "CONTROL_ROUTER":
        failures.append("gov_mode: must_be_CONTROL_ROUTER")

    route = control.get("route_verdict")
    if route not in ALLOWED_ROUTE_VERDICTS:
        failures.append("route_verdict: invalid_or_model_selection")

    failures.extend(_forbidden_model_keys(control))
    failures.extend(_validate_burn_decision(control))
    failures.extend(_validate_targeted_hunter(control))

    delta_failures, high_drift_count = _validate_delta_ledger(control)
    failures.extend(delta_failures)
    failures.extend(_validate_early_exit(control, high_drift_count))

    if not isinstance(control.get("deterministic_form_actuation"), Mapping):
        failures.append("deterministic_form_actuation: missing_or_not_object")

    official_valid = not failures
    return DynamicGovRouterValidation(
        official_valid=official_valid,
        classification=(
            "OFFICIAL_DYNAMIC_GOV_ROUTER_VALID"
            if official_valid
            else "DIAGNOSTIC_ONLY_INVALID_DYNAMIC_GOV_ROUTER"
        ),
        failures=failures,
        route_verdict=route if route in ALLOWED_ROUTE_VERDICTS else None,
        final_compiler_allowed=(
            control.get("final_compiler_allowed")
            if isinstance(control.get("final_compiler_allowed"), bool)
            else None
        ),
        high_severity_drift_count=high_drift_count,
    )


def validate_dynamic_gov_router_control_file(path: str | Path) -> DynamicGovRouterValidation:
    with Path(path).open("r", encoding="utf-8") as fh:
        control = json.load(fh)
    return validate_dynamic_gov_router_control(control)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a D11-lock Dynamic Gov Router control object."
    )
    parser.add_argument("control_json", help="Path to Gov control object JSON")
    args = parser.parse_args()

    result = validate_dynamic_gov_router_control_file(args.control_json)
    print(json.dumps(asdict(result), indent=2, sort_keys=True))
    return 0 if result.official_valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
