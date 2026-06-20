from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PROTOCOL_ID = "unified_artifact_scoring_protocol_v5_1"
VALID_LABELS = {"ARTIFACT_001", "ARTIFACT_003"}
PAIRWISE_VALUES = VALID_LABELS | {"TIE"}

HARD_CAPS: dict[str, float] = {
    "invented_source_or_citation": 70,
    "false_source_attribution": 75,
    "material_source_misrepresentation": 75,
    "source_boundary_violation": 75,
    "central_data_stat_chart_error": 75,
    "missed_contradiction_changes_recommendation": 80,
    "unsupported_major_recommendation": 82,
    "unsafe_or_overconfident_operational_advice": 82,
    "generic_crisis_memo_low_operational_usefulness": 78,
    "failure_to_handle_uncertainty": 85,
    "severe_required_section_failure": 88,
    "reliance_critical_missing_caveat": 85,
    "stale_evidence_treated_as_current_or_decisive": 82,
    "draft_provisional_limited_source_treated_as_final_authority": 80,
    "material_negative_space_miss": 83,
    "no_clear_decision_recommendation": 83,
    "no_operational_stop_go_logic": 83,
}

GATE_FIELDS = [
    "passes_source_fidelity_gate",
    "passes_source_to_claim_traceability_gate",
    "passes_decision_logic_gate",
    "passes_operational_specificity_gate",
    "passes_uncertainty_gate",
    "passes_contradiction_negative_space_gate",
    "passes_risk_suppression_gate",
    "passes_expert_review_gate",
]

SCORE_FIELDS = {
    "source_fidelity_score_15": 15,
    "source_to_claim_traceability_score_10": 10,
    "contradiction_handling_score_10": 10,
    "uncertainty_limitations_score_10": 10,
    "data_stat_chart_score_8": 8,
    "decision_usefulness_score_12": 12,
    "operational_actionability_score_10": 10,
    "risk_suppression_blindspot_score_15": 15,
    "expert_review_survivability_score_10": 10,
}

DEFECT_AUDIT_FIELDS = [
    "why_not_100",
    "weakest_source_to_claim_link",
    "missing_or_underdeveloped_caveat",
    "unresolved_uncertainty",
    "biggest_overclaim_risk",
    "risk_if_leader_relied_on_it",
    "expert_reviewer_challenge",
    "needed_to_move_above_83",
    "needed_to_move_above_90",
    "needed_to_move_above_95",
    "material_repairs_required",
]

PAIRWISE_FIELDS = [
    "more_source_faithful",
    "more_decision_useful",
    "safer_to_rely_on",
    "better_uncertainty_handling",
    "better_contradiction_handling",
    "better_blindspot_detection",
    "better_hallucination_resistance",
    "better_overclaim_suppression",
    "more_operationally_actionable",
    "more_expert_survivable",
    "overall_winner",
]

CAP_TRIGGER_PATTERNS = {
    "invented_source_or_citation": re.compile(r"invented (source|citation)|fabricated (source|citation)", re.I),
    "false_source_attribution": re.compile(r"false attribution|misattributed", re.I),
    "material_source_misrepresentation": re.compile(r"source misrepresentation|misrepresents? source", re.I),
    "unsupported_major_recommendation": re.compile(r"unsupported major recommendation|unsupported recommendation", re.I),
    "no_clear_decision_recommendation": re.compile(r"no clear decision recommendation|lacks clear recommendation", re.I),
    "no_operational_stop_go_logic": re.compile(r"no operational stop|lacks stop/go|missing stop/go", re.I),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(nonempty(item) for item in value)
    if isinstance(value, dict):
        return any(nonempty(item) for item in value.values())
    return value is not None


def cap_ids(row: dict[str, Any]) -> set[str]:
    ids = set()
    for item in row.get("applicable_hard_caps") or []:
        if isinstance(item, dict) and item.get("cap_id"):
            ids.add(str(item["cap_id"]))
        elif isinstance(item, str):
            ids.add(item)
    return ids


def lowest_cap(row: dict[str, Any]) -> float:
    values = []
    for item in row.get("applicable_hard_caps") or []:
        if isinstance(item, dict):
            if item.get("cap_id") in HARD_CAPS:
                values.append(HARD_CAPS[item["cap_id"]])
            elif isinstance(item.get("max_score_100"), (int, float)):
                values.append(float(item["max_score_100"]))
    return min(values) if values else 100.0


def lowest_ceiling(row: dict[str, Any]) -> float:
    values = []
    for item in row.get("applicable_expert_ceilings") or []:
        if isinstance(item, dict) and isinstance(item.get("max_score_100"), (int, float)):
            values.append(float(item["max_score_100"]))
    if any(row.get(field) is False for field in GATE_FIELDS):
        values.append(83.0)
    return min(values) if values else 100.0


def validate_score_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("protocol_id") != PROTOCOL_ID:
        errors.append("protocol_id_mismatch")
    source_packet_present = payload.get("source_packet_present") is True
    rows = payload.get("artifact_scores")
    if not isinstance(rows, list) or len(rows) != 2:
        errors.append("artifact_scores_must_have_exactly_two_rows")
        rows = []
    labels = {row.get("artifact_label") for row in rows if isinstance(row, dict)}
    if labels != VALID_LABELS:
        errors.append(f"artifact_labels_mismatch:{sorted(labels)}")

    for row in rows:
        if not isinstance(row, dict):
            errors.append("artifact_score_row_not_object")
            continue
        label = row.get("artifact_label")
        final = row.get("final_score_100")
        raw = row.get("raw_evidence_score_100")
        if not isinstance(final, (int, float)) or final < 0 or final > 100:
            errors.append(f"{label}:invalid_final_score_100")
            continue
        if not isinstance(raw, (int, float)) or raw < 0 or raw > 100:
            errors.append(f"{label}:invalid_raw_evidence_score_100")
        else:
            category_sum = sum(float(row.get(field, -9999)) for field in SCORE_FIELDS)
            if abs(category_sum - float(raw)) > 0.01:
                errors.append(f"{label}:raw_score_not_equal_category_sum")
        if isinstance(raw, (int, float)) and final > raw + 0.01:
            errors.append(f"{label}:final_score_exceeds_raw_score")
        cap = lowest_cap(row)
        if final > cap + 0.01:
            errors.append(f"{label}:final_score_exceeds_hard_cap:{cap}")
        ceiling = lowest_ceiling(row)
        if final > ceiling + 0.01:
            errors.append(f"{label}:final_score_exceeds_expert_ceiling:{ceiling}")
        if row.get("admission_status") == "fail" and final > 69:
            errors.append(f"{label}:admission_fail_above_diagnostic_band")
        failed_gates = [field for field in GATE_FIELDS if row.get(field) is False]
        if failed_gates and final > 83:
            errors.append(f"{label}:score_above_83_with_failed_gate:{','.join(failed_gates)}")
        if row.get("passes_risk_suppression_gate") is False and final > 83:
            errors.append(f"{label}:risk_suppression_gate_false_above_83")
        ids = cap_ids(row)
        if "invented_source_or_citation" in ids and final > 70:
            errors.append(f"{label}:invented_source_above_70")
        if "false_source_attribution" in ids and final > 75:
            errors.append(f"{label}:false_source_attribution_above_75")
        if "material_source_misrepresentation" in ids and final > 75:
            errors.append(f"{label}:material_source_misrepresentation_above_75")
        if "no_clear_decision_recommendation" in ids and final > 83:
            errors.append(f"{label}:no_clear_decision_recommendation_above_83")
        if "no_operational_stop_go_logic" in ids and final > 83:
            errors.append(f"{label}:no_operational_stop_go_logic_above_83")
        if final > 85:
            missing = [field for field in DEFECT_AUDIT_FIELDS if not nonempty(row.get(field))]
            if missing:
                errors.append(f"{label}:score_above_85_missing_defect_audit:{','.join(missing)}")
        if final > 90:
            if not nonempty(row.get("expert_review_survivability_rationale")):
                errors.append(f"{label}:score_above_90_missing_expert_review_rationale")
            if len([item for item in row.get("avoided_failure_modes") or [] if str(item).strip()]) < 2:
                errors.append(f"{label}:score_above_90_needs_two_avoided_failure_modes")
        if final > 95 and len(str(row.get("why_not_100") or "").strip()) < 20:
            errors.append(f"{label}:score_above_95_missing_concrete_why_not_100")
        if not source_packet_present and float(row.get("source_fidelity_score_15") or 0) > 0:
            errors.append(f"{label}:source_packet_missing_but_source_fidelity_accepted")
        for field, max_value in SCORE_FIELDS.items():
            value = row.get(field)
            if not isinstance(value, (int, float)) or value < 0 or value > max_value:
                errors.append(f"{label}:invalid_category_score:{field}")

    pairwise = payload.get("pairwise_comparative_consistency") or {}
    if not isinstance(pairwise, dict):
        errors.append("pairwise_comparative_consistency_not_object")
    else:
        for field in PAIRWISE_FIELDS:
            value = pairwise.get(field)
            if value not in PAIRWISE_VALUES:
                errors.append(f"pairwise_label_not_exact:{field}:{value}")
    raw_text = payload.get("raw_judge_text") or ""
    if raw_text:
        detected = [cap_id for cap_id, pattern in CAP_TRIGGER_PATTERNS.items() if pattern.search(raw_text)]
        all_caps = set().union(*(cap_ids(row) for row in rows if isinstance(row, dict))) if rows else set()
        missing_caps = [cap_id for cap_id in detected if cap_id not in all_caps]
        if detected and not all_caps:
            errors.append("raw_text_indicates_cap_trigger_but_parsed_caps_empty")
        elif missing_caps:
            errors.append("raw_text_indicates_unparsed_cap_trigger:" + ",".join(missing_caps))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Unified Artifact Scoring Protocol v5.1 judge JSON output.")
    parser.add_argument("--score-json", required=True, help="Path to pasted or provider-returned judge JSON.")
    parser.add_argument("--strict", action="store_true", help="Fail on any validation error. Default behavior also fails on errors; flag is informational.")
    args = parser.parse_args()
    path = Path(args.score_json)
    payload = load_json(path)
    errors = validate_score_payload(payload)
    result = {
        "status": "UNIFIED_V5_1_SCORE_VALID" if not errors else "UNIFIED_V5_1_SCORE_INVALID",
        "score_json": str(path),
        "errors": errors,
        "provider_calls": 0,
    }
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
