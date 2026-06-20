from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROTOCOL_ID = "unified_artifact_scoring_protocol_v5_2_structural_epistemic"

STRUCTURAL_FIELDS = [
    "bluf",
    "data_isolation",
    "option_distinctness",
    "evidence_constraints",
    "risk_symmetry",
    "scannability",
]

EPISTEMIC_FIELDS = [
    "claim_evidence_distance",
    "conflicting_data_handling",
    "insight_vs_summary",
    "operational_reality_gap",
    "source_weighting_validity",
]

HARD_CAPS: dict[str, float] = {
    "invented_source_or_citation": 70,
    "false_source_attribution": 75,
    "material_source_misrepresentation": 75,
    "source_boundary_violation": 75,
    "central_data_stat_chart_error": 75,
    "missed_contradiction_changing_recommendation": 80,
    "unsupported_major_recommendation": 82,
    "unsafe_or_overconfident_operational_advice": 82,
    "generic_crisis_memo_low_operational_usefulness": 78,
    "failure_to_handle_uncertainty": 85,
    "severe_required_section_failure": 88,
    "reliance_critical_missing_caveat": 85,
    "stale_evidence_treated_as_current_decisive": 82,
    "draft_provisional_limited_source_treated_as_final_authority": 80,
    "material_negative_space_miss": 83,
    "no_clear_decision_recommendation": 83,
    "no_operational_stop_go_logic": 83,
}

BANDS = [
    (95.0, "Executive-ready / highly rigorous"),
    (90.0, "Strong / expert-survivable with minor edits"),
    (83.0, "Functional / needs revision"),
    (70.0, "Draft quality / research summary"),
    (0.0, "Rejected / not decision-grade"),
]


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


def band_for(score: float) -> str:
    for threshold, band in BANDS:
        if score >= threshold:
            return band
    return "Rejected / not decision-grade"


def cap_id(item: Any) -> str | None:
    if isinstance(item, str):
        return item
    if isinstance(item, dict) and isinstance(item.get("cap_id"), str):
        return item["cap_id"]
    return None


def lowest_cap(row: dict[str, Any]) -> float:
    values: list[float] = []
    for item in row.get("applicable_hard_caps") or []:
        if isinstance(item, dict) and isinstance(item.get("max_score_100"), (int, float)):
            values.append(float(item["max_score_100"]))
            continue
        cid = cap_id(item)
        if cid in HARD_CAPS:
            values.append(HARD_CAPS[cid])
    return min(values) if values else 100.0


def validate_dimension_block(row: dict[str, Any], block_name: str, fields: list[str], label: str, errors: list[str]) -> list[int]:
    block = row.get(block_name)
    values: list[int] = []
    if not isinstance(block, dict):
        errors.append(f"{label}:{block_name}_missing_or_not_object")
        return values
    for field in fields:
        value = block.get(field)
        if not isinstance(value, int) or value not in {0, 1, 2, 3}:
            errors.append(f"{label}:invalid_dimension_score:{block_name}.{field}")
        else:
            values.append(value)
    return values


def validate_score_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("protocol_id") != PROTOCOL_ID:
        errors.append("protocol_id_mismatch")

    rows = payload.get("artifact_scores")
    if not isinstance(rows, list) or not rows:
        errors.append("artifact_scores_missing_or_empty")
        return errors

    for row in rows:
        if not isinstance(row, dict):
            errors.append("artifact_score_row_not_object")
            continue
        label = str(row.get("artifact_id") or "UNKNOWN")
        structural_values = validate_dimension_block(row, "structural_scores", STRUCTURAL_FIELDS, label, errors)
        epistemic_values = validate_dimension_block(row, "epistemic_scores", EPISTEMIC_FIELDS, label, errors)

        structural_sum = sum(structural_values)
        epistemic_sum = sum(epistemic_values)
        raw_total = structural_sum + epistemic_sum
        normalized = round((raw_total / 33) * 100, 1)

        if row.get("structural_raw_18") != structural_sum:
            errors.append(f"{label}:structural_subtotal_math_wrong")
        if row.get("epistemic_raw_15") != epistemic_sum:
            errors.append(f"{label}:epistemic_subtotal_math_wrong")
        if row.get("raw_total_33") != raw_total:
            errors.append(f"{label}:raw_total_math_wrong")
        if not isinstance(row.get("normalized_total_100"), (int, float)) or abs(float(row["normalized_total_100"]) - normalized) > 0.05:
            errors.append(f"{label}:normalized_score_math_wrong")

        final = row.get("final_score_100")
        if not isinstance(final, (int, float)) or final < 0 or final > 100:
            errors.append(f"{label}:invalid_final_score_100")
            continue
        if final > normalized + 0.05:
            errors.append(f"{label}:final_score_exceeds_normalized_score")
        cap = lowest_cap(row)
        if final > cap + 0.05:
            errors.append(f"{label}:final_score_exceeds_hard_cap:{cap}")

        expected_band = band_for(float(final))
        if row.get("band") != expected_band:
            errors.append(f"{label}:band_mismatch:{expected_band}")

        if final >= 95:
            low_struct = [field for field in STRUCTURAL_FIELDS if isinstance(row.get("structural_scores"), dict) and row["structural_scores"].get(field) != 3]
            low_epi = [field for field in EPISTEMIC_FIELDS if isinstance(row.get("epistemic_scores"), dict) and row["epistemic_scores"].get(field) != 3]
            if low_struct:
                errors.append(f"{label}:score_95_plus_with_structural_dimension_below_3:{','.join(low_struct)}")
            if low_epi:
                errors.append(f"{label}:score_95_plus_with_epistemic_dimension_below_3:{','.join(low_epi)}")
        if final >= 90 and isinstance(row.get("epistemic_scores"), dict):
            epi = row["epistemic_scores"]
            if epi.get("claim_evidence_distance") != 3:
                errors.append(f"{label}:score_90_plus_claim_evidence_distance_below_3")
            if epi.get("source_weighting_validity") != 3:
                errors.append(f"{label}:score_90_plus_source_weighting_below_3")
            if epi.get("operational_reality_gap") != 3:
                errors.append(f"{label}:score_90_plus_operational_reality_gap_below_3")

        cap_ids = {cid for cid in (cap_id(item) for item in row.get("applicable_hard_caps") or []) if cid}
        if "no_clear_decision_recommendation" in cap_ids and final > 83:
            errors.append(f"{label}:no_clear_decision_recommendation_above_83")
        if "no_operational_stop_go_logic" in cap_ids and final > 83:
            errors.append(f"{label}:no_operational_stop_go_logic_above_83")
        if "invented_source_or_citation" in cap_ids and final > 70:
            errors.append(f"{label}:invented_source_above_70")
        if "false_source_attribution" in cap_ids and final > 75:
            errors.append(f"{label}:false_source_attribution_above_75")
        if "material_source_misrepresentation" in cap_ids and final > 75:
            errors.append(f"{label}:material_source_misrepresentation_above_75")

        for field in [
            "dimension_justifications",
            "strongest_dimensions",
            "weakest_dimensions",
            "expert_reviewer_challenge",
            "decision_reliance_risk",
        ]:
            if not nonempty(row.get(field)):
                errors.append(f"{label}:missing_required_explanation:{field}")
        if final < 95 and not nonempty(row.get("required_repairs_to_next_band")):
            errors.append(f"{label}:missing_required_explanation:required_repairs_to_next_band")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate v5.2 Structural + Epistemic score JSON.")
    parser.add_argument("--score-json", required=True, type=Path)
    args = parser.parse_args()
    payload = load_json(args.score_json)
    errors = validate_score_payload(payload)
    result = {"valid": not errors, "errors": errors}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
