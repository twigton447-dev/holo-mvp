from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PROTOCOL_ID = "unified_artifact_scoring_protocol_v6_1_structural_epistemic_argument_power"

CLAIM_TYPES = {"factual", "causal", "regulatory", "operational", "statistical", "recommendation", "source-status"}
SOURCE_ID_QUALITY = {"exact_full_ids", "abbreviated_ids", "vague_reference", "no_source_reference"}
SUPPORT_STATUS = {"supported", "partially_supported", "unsupported", "contradicted", "not_in_packet"}
SEVERITY = {"none", "minor", "material", "fatal"}
ARGUMENT_BREAKDOWN_WEIGHTS: dict[str, float] = {
    "central_thesis_strength_15": 15,
    "argument_coherence_15": 15,
    "persuasiveness_under_uncertainty_15": 15,
    "insight_density_15": 15,
    "research_integration_15": 15,
    "practical_judgment_10": 10,
    "counterargument_handling_10": 10,
    "clarity_force_memorability_5": 5,
}

CAPS: dict[str, float] = {
    "invented_source_or_fabricated_external_fact": 60,
    "material_source_misattribution": 75,
    "source_status_error": 80,
    "unsupported_major_recommendation_claim": 82,
    "material_negative_space_miss": 83,
    "generic_operational_advice_without_executable_gates": 84,
    "material_risk_of_acting_or_waiting_omission": 86,
    "word_count_under_minimum_missing_substance": 88,
    "abbreviated_source_ids_when_exact_ids_expected": 90,
}

CAP_TEXT_PATTERNS: list[tuple[re.Pattern[str], float]] = [
    (re.compile(r"max\s+(\d+(?:\.\d+)?)", re.I), -1),
    (re.compile(r"word[- ]count.*under.*substance|under.*word[- ]count.*substance", re.I), 88),
    (re.compile(r"abbreviated source", re.I), 90),
    (re.compile(r"invented source|fabricated", re.I), 60),
    (re.compile(r"false source|misattribution", re.I), 75),
    (re.compile(r"unsupported major", re.I), 82),
    (re.compile(r"negative[- ]space", re.I), 83),
    (re.compile(r"generic operational", re.I), 84),
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


def item_cap_value(item: Any) -> float | None:
    if isinstance(item, dict):
        if isinstance(item.get("max_score_100"), (int, float)):
            return float(item["max_score_100"])
        cid = item.get("cap_id") or item.get("ceiling_id")
        if isinstance(cid, str) and cid in CAPS:
            return CAPS[cid]
        text = json.dumps(item, sort_keys=True)
    else:
        text = str(item)
    if text in CAPS:
        return CAPS[text]
    for pattern, value in CAP_TEXT_PATTERNS:
        match = pattern.search(text)
        if match:
            if value == -1:
                return float(match.group(1))
            return value
    return None


def lowest_cap(row: dict[str, Any]) -> float:
    caps: list[float] = []
    for item in row.get("caps_or_ceilings_applied") or []:
        value = item_cap_value(item)
        if value is not None:
            caps.append(value)
    return min(caps) if caps else 100.0


def validate_claim(claim: Any, label: str, idx: int, errors: list[str]) -> None:
    if not isinstance(claim, dict):
        errors.append(f"{label}:claim_{idx}_not_object")
        return
    required = [
        "claim_text", "claim_type", "cited_sources", "exact_source_id_quality", "source_support_status",
        "source_boundary_issue", "overclaim_issue", "stale_or_limited_evidence_issue", "missing_caveat",
        "severity", "cap_or_ceiling_trigger_if_any",
    ]
    for field in required:
        if field not in claim:
            errors.append(f"{label}:claim_{idx}_missing_{field}")
    if claim.get("claim_type") not in CLAIM_TYPES:
        errors.append(f"{label}:claim_{idx}_invalid_claim_type")
    if claim.get("exact_source_id_quality") not in SOURCE_ID_QUALITY:
        errors.append(f"{label}:claim_{idx}_invalid_source_id_quality")
    if claim.get("source_support_status") not in SUPPORT_STATUS:
        errors.append(f"{label}:claim_{idx}_invalid_source_support_status")
    if claim.get("severity") not in SEVERITY:
        errors.append(f"{label}:claim_{idx}_invalid_severity")
    if not isinstance(claim.get("cited_sources"), list):
        errors.append(f"{label}:claim_{idx}_cited_sources_not_list")
    for field in ["source_boundary_issue", "overclaim_issue", "stale_or_limited_evidence_issue"]:
        if not isinstance(claim.get(field), bool):
            errors.append(f"{label}:claim_{idx}_{field}_not_boolean")


def validate_score_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("protocol_id") != PROTOCOL_ID:
        errors.append("protocol_id_mismatch")
    rows = payload.get("artifact_scores")
    if not isinstance(rows, list) or not rows:
        errors.append("artifact_scores_missing_or_empty")
        return errors
    labels = [row.get("artifact_label") for row in rows if isinstance(row, dict)]
    for row in rows:
        if not isinstance(row, dict):
            errors.append("artifact_score_row_not_object")
            continue
        label = str(row.get("artifact_label") or "UNKNOWN")
        ledger = row.get("claim_ledger")
        if not isinstance(ledger, list):
            errors.append(f"{label}:claim_ledger_missing_or_not_list")
            ledger = []
        if len(ledger) < 8:
            errors.append(f"{label}:claim_ledger_too_short")
        if len(ledger) > 15:
            errors.append(f"{label}:claim_ledger_too_long")
        for idx, claim in enumerate(ledger, 1):
            validate_claim(claim, label, idx, errors)

        structural = row.get("structural_score_50")
        epistemic = row.get("epistemic_score_50")
        structural_epistemic = row.get("structural_epistemic_score_100")
        argument_power = row.get("argument_power_score_100")
        raw = row.get("raw_composite_score_100")
        penalty = row.get("word_count_penalty_points")
        adjusted = row.get("score_after_word_count_adjustment_100")
        final = row.get("score_0_100")
        for field, value, maxv in [
            ("structural_score_50", structural, 50),
            ("epistemic_score_50", epistemic, 50),
            ("structural_epistemic_score_100", structural_epistemic, 100),
            ("argument_power_score_100", argument_power, 100),
            ("raw_composite_score_100", raw, 100),
            ("word_count_penalty_points", penalty, 100),
            ("score_after_word_count_adjustment_100", adjusted, 100),
            ("score_0_100", final, 100),
        ]:
            if not isinstance(value, (int, float)) or value < 0 or value > maxv:
                errors.append(f"{label}:invalid_{field}")
        if isinstance(structural, (int, float)) and isinstance(epistemic, (int, float)):
            expected_structural_epistemic = round(float(structural) + float(epistemic), 4)
            if not isinstance(structural_epistemic, (int, float)) or abs(float(structural_epistemic) - expected_structural_epistemic) > 0.05:
                errors.append(f"{label}:structural_epistemic_score_math_wrong")
        breakdown = row.get("argument_power_breakdown")
        if not isinstance(breakdown, dict):
            errors.append(f"{label}:argument_power_breakdown_missing_or_not_object")
            breakdown = {}
        argument_sum = 0.0
        for field, maxv in ARGUMENT_BREAKDOWN_WEIGHTS.items():
            value = breakdown.get(field)
            if not isinstance(value, (int, float)) or value < 0 or value > maxv:
                errors.append(f"{label}:invalid_argument_power_breakdown:{field}")
            else:
                argument_sum += float(value)
        if isinstance(argument_power, (int, float)) and abs(float(argument_power) - round(argument_sum, 4)) > 0.05:
            errors.append(f"{label}:argument_power_score_math_wrong")
        if isinstance(structural_epistemic, (int, float)) and isinstance(argument_power, (int, float)):
            expected_raw = round((0.60 * float(structural_epistemic)) + (0.40 * float(argument_power)), 4)
            if not isinstance(raw, (int, float)) or abs(float(raw) - expected_raw) > 0.05:
                errors.append(f"{label}:raw_composite_score_math_wrong")
        verified_word_count = row.get("verified_word_count")
        if isinstance(raw, (int, float)) and isinstance(penalty, (int, float)) and isinstance(adjusted, (int, float)):
            expected_penalty = 0.0
            if isinstance(verified_word_count, int) and verified_word_count > 1300:
                expected_penalty = round((verified_word_count - 1300) * 0.03, 4)
            if isinstance(verified_word_count, int) and verified_word_count <= 1300 and penalty > 0.05:
                errors.append(f"{label}:word_count_penalty_without_overage")
            if isinstance(verified_word_count, int) and verified_word_count > 1300 and abs(float(penalty) - expected_penalty) > 0.06:
                errors.append(f"{label}:word_count_overage_penalty_math_wrong")
            expected_adjusted = round(max(0.0, float(raw) - float(penalty)), 4)
            if abs(float(adjusted) - expected_adjusted) > 0.06:
                errors.append(f"{label}:score_after_word_count_adjustment_math_wrong")
        if isinstance(final, (int, float)) and isinstance(raw, (int, float)) and final > raw + 0.05:
            errors.append(f"{label}:final_score_exceeds_raw_composite_score")
        if isinstance(final, (int, float)) and isinstance(adjusted, (int, float)) and final > adjusted + 0.05:
            errors.append(f"{label}:final_score_exceeds_word_count_adjusted_score")
        cap = lowest_cap(row)
        if isinstance(final, (int, float)) and final > cap + 0.05:
            errors.append(f"{label}:final_score_exceeds_cap_or_ceiling:{cap}")

        word_band_pass = row.get("word_band_pass")
        if not isinstance(word_band_pass, bool):
            errors.append(f"{label}:word_band_pass_not_boolean")

        qualities = {claim.get("exact_source_id_quality") for claim in ledger if isinstance(claim, dict)}
        if "abbreviated_ids" in qualities and isinstance(final, (int, float)) and final > 90.05:
            errors.append(f"{label}:abbreviated_source_ids_above_90")
        support_defects = [claim for claim in ledger if isinstance(claim, dict) and claim.get("source_support_status") in {"unsupported", "contradicted", "not_in_packet"}]
        material_support_defects = [claim for claim in support_defects if claim.get("severity") in {"material", "fatal"}]
        if material_support_defects and isinstance(final, (int, float)) and final > 82.05:
            errors.append(f"{label}:material_unsupported_claim_above_82")
        material_boundary_or_overclaim = [claim for claim in ledger if isinstance(claim, dict) and claim.get("severity") in {"material", "fatal"} and (claim.get("source_boundary_issue") or claim.get("overclaim_issue"))]
        if material_boundary_or_overclaim and isinstance(final, (int, float)) and final > 82.05:
            errors.append(f"{label}:material_boundary_or_overclaim_above_82")
        if row.get("invented_or_false_source_attributions") and isinstance(final, (int, float)) and final > 60.05:
            errors.append(f"{label}:invented_or_false_source_above_60")
        if row.get("unsupported_major_claims") and isinstance(final, (int, float)) and final > 82.05:
            errors.append(f"{label}:unsupported_major_claims_above_82")
        if row.get("negative_space_misses") and isinstance(final, (int, float)) and final > 83.05:
            errors.append(f"{label}:negative_space_misses_above_83")
        if row.get("source_laundering_findings") and isinstance(final, (int, float)) and final > 85.05:
            errors.append(f"{label}:source_laundering_above_85")

        avoided = row.get("avoided_failure_modes")
        if not isinstance(avoided, list):
            errors.append(f"{label}:avoided_failure_modes_not_list")
            avoided = []
        if isinstance(final, (int, float)) and final > 85 and len(avoided) < 2:
            errors.append(f"{label}:score_above_85_without_two_avoided_failure_modes")
        if isinstance(final, (int, float)) and final > 90 and len(avoided) < 3:
            errors.append(f"{label}:score_above_90_without_three_avoided_failure_modes")
        if isinstance(final, (int, float)) and final > 90 and material_support_defects:
            errors.append(f"{label}:score_above_90_with_material_source_support_defect")
        if isinstance(final, (int, float)) and final > 95:
            if row.get("caps_or_ceilings_applied"):
                errors.append(f"{label}:score_above_95_with_caps_or_ceilings")
            if row.get("major_defects"):
                errors.append(f"{label}:score_above_95_with_major_defects")
            if row.get("source_laundering_findings") or row.get("unsupported_major_claims") or row.get("negative_space_misses"):
                errors.append(f"{label}:score_above_95_with_defect_findings")
        insight_findings = row.get("insight_findings")
        if not isinstance(insight_findings, list):
            errors.append(f"{label}:insight_findings_not_list")
            insight_findings = []
        if isinstance(argument_power, (int, float)) and argument_power > 85 and len(insight_findings) < 2:
            errors.append(f"{label}:argument_power_above_85_without_two_insight_findings")
        if isinstance(argument_power, (int, float)) and argument_power > 90 and len(insight_findings) < 3:
            errors.append(f"{label}:argument_power_above_90_without_three_insight_findings")
        if isinstance(argument_power, (int, float)) and argument_power > 90 and not nonempty(row.get("counterargument_analysis")):
            errors.append(f"{label}:argument_power_above_90_without_counterargument_analysis")
        if isinstance(argument_power, (int, float)) and argument_power > 95:
            defect_text = json.dumps(row.get("major_defects") or [], sort_keys=True).lower()
            if re.search(r"clarity|coherence|research|integration|synthesis|argument", defect_text):
                errors.append(f"{label}:argument_power_above_95_with_argument_quality_defect")
        for field in ["major_strengths", "rationale"]:
            if not nonempty(row.get(field)):
                errors.append(f"{label}:missing_required_explanation:{field}")

    pairwise = payload.get("pairwise_winners") or {}
    if isinstance(pairwise, dict):
        for key, value in pairwise.items():
            if isinstance(value, str) and value not in labels:
                if "tie" in value.lower() or "equal" in value.lower():
                    errors.append(f"pairwise_tie_not_allowed_without_ledger_evidence:{key}")
                else:
                    errors.append(f"pairwise_winner_not_exact_artifact_label:{key}")
    final_judgment = payload.get("final_forced_expert_judgment")
    if not isinstance(final_judgment, dict):
        errors.append("final_forced_expert_judgment_missing_or_not_object")
    else:
        winner = final_judgment.get("winner")
        if winner not in labels:
            if isinstance(winner, str) and "tie" in winner.lower():
                errors.append("final_forced_expert_judgment_tie_not_allowed_without_ledger_evidence")
            else:
                errors.append("final_forced_expert_judgment_winner_not_exact_artifact_label")
        confidence = final_judgment.get("confidence_0_to_1")
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            errors.append("final_forced_expert_judgment_invalid_confidence")
        for field in ["why_winner_is_stronger", "why_loser_is_weaker"]:
            if not nonempty(final_judgment.get(field)):
                errors.append(f"final_forced_expert_judgment_missing_{field}")
        if not isinstance(final_judgment.get("does_final_judgment_match_numeric_score_order"), bool):
            errors.append("final_forced_expert_judgment_match_flag_not_boolean")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate v6.1 Structural/Epistemic + Argument Power score JSON.")
    parser.add_argument("--score-json", required=True, type=Path)
    args = parser.parse_args()
    payload = load_json(args.score_json)
    errors = validate_score_payload(payload)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
