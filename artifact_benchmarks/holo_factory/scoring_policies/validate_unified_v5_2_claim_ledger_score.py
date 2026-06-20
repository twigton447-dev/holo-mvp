from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROTOCOL_ID = "unified_artifact_scoring_protocol_v5_2_claim_ledger_candidate"
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
ALLOWED_NON_SOURCE_CONTEXT_IDS = {"TASK_BRIEF", "DOMAIN_CARD"}
MATERIAL_SEVERITIES = {"material", "fatal"}
BAD_SUPPORT = {"unsupported", "contradicted", "not_in_packet"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and any(str(item).strip() for item in value)


def claim_cap(claim: dict[str, Any]) -> float:
    cap_id = str(claim.get("cap_trigger_if_any") or "")
    support = claim.get("source_support_status")
    severity = claim.get("severity")
    ctype = claim.get("claim_type")
    if cap_id in {"false_source_attribution", "material_source_misrepresentation"}:
        return 75.0
    if cap_id == "invented_source_or_citation":
        return 70.0
    if cap_id == "unsupported_major_claim":
        return 82.0
    if ctype == "source_status" and support in BAD_SUPPORT:
        return 75.0 if severity in MATERIAL_SEVERITIES else 80.0
    if support in {"not_in_packet", "contradicted"} and severity == "fatal":
        return 70.0
    if support == "unsupported" and severity in MATERIAL_SEVERITIES:
        return 82.0
    return 100.0


def validate_score_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("protocol_id") != PROTOCOL_ID:
        errors.append("protocol_id_mismatch")

    source_ids = set(payload.get("source_packet_source_ids") or [])
    if not source_ids:
        errors.append("missing_source_packet_source_ids")

    rows = payload.get("artifact_scores")
    if not isinstance(rows, list) or not rows:
        errors.append("artifact_scores_missing")
        rows = []

    for row in rows:
        if not isinstance(row, dict):
            errors.append("artifact_score_row_not_object")
            continue
        label = row.get("artifact_label", "UNKNOWN")
        final = row.get("final_score_100")
        raw = row.get("raw_evidence_score_100")
        if not isinstance(final, (int, float)) or final < 0 or final > 100:
            errors.append(f"{label}:invalid_final_score_100")
            continue
        if not isinstance(raw, (int, float)) or raw < 0 or raw > 100:
            errors.append(f"{label}:invalid_raw_evidence_score_100")
        elif final > raw + 0.01:
            errors.append(f"{label}:final_score_exceeds_raw_score")

        ledger = row.get("claim_ledger")
        if not isinstance(ledger, dict):
            errors.append(f"{label}:missing_claim_ledger")
            continue

        claims = ledger.get("major_claims")
        if not isinstance(claims, list):
            errors.append(f"{label}:major_claims_missing")
            claims = []
        if len(claims) < 8:
            errors.append(f"{label}:fewer_than_8_major_claims")
        if len(claims) > 15:
            errors.append(f"{label}:more_than_15_major_claims")

        derived_caps = []
        material_source_defects = []
        for idx, claim in enumerate(claims):
            if not isinstance(claim, dict):
                errors.append(f"{label}:claim_not_object:{idx}")
                continue
            claim_id = claim.get("claim_id") or f"claim_{idx}"
            cited = claim.get("cited_sources") or []
            if not isinstance(cited, list):
                errors.append(f"{label}:{claim_id}:cited_sources_not_list")
                cited = []
            for src in cited:
                if src not in source_ids and src not in ALLOWED_NON_SOURCE_CONTEXT_IDS:
                    errors.append(f"{label}:{claim_id}:unknown_cited_source_id:{src}")
                    derived_caps.append(70.0)
            for field in [
                "claim_text",
                "claim_type",
                "source_support_status",
                "severity",
                "cap_trigger_if_any",
            ]:
                if field not in claim:
                    errors.append(f"{label}:{claim_id}:missing_claim_field:{field}")
            cap = claim_cap(claim)
            if cap < 100:
                derived_caps.append(cap)
            if claim.get("severity") in MATERIAL_SEVERITIES and claim.get("source_support_status") in BAD_SUPPORT:
                material_source_defects.append(claim_id)

        if nonempty_list(ledger.get("invented_or_false_source_attributions")):
            derived_caps.append(75.0)
        if nonempty_list(ledger.get("unsupported_major_claims")):
            derived_caps.append(82.0)
        if nonempty_list(ledger.get("negative_space_misses")):
            # Materiality can be encoded as dict severity or plain string. Plain entries are treated as material.
            for miss in ledger.get("negative_space_misses") or []:
                severity = miss.get("severity") if isinstance(miss, dict) else "material"
                if severity in MATERIAL_SEVERITIES:
                    derived_caps.append(83.0)
                    if final > 83:
                        errors.append(f"{label}:material_negative_space_above_83")
                    break

        if final > 85 and len([x for x in ledger.get("avoided_failure_modes") or [] if str(x).strip()]) < 2:
            errors.append(f"{label}:score_above_85_needs_two_avoided_failure_modes")
        if final > 90:
            if len([x for x in ledger.get("avoided_failure_modes") or [] if str(x).strip()]) < 3:
                errors.append(f"{label}:score_above_90_needs_three_avoided_failure_modes")
            if material_source_defects:
                errors.append(f"{label}:score_above_90_with_material_source_support_defects:{','.join(material_source_defects)}")

        if derived_caps:
            cap = min(derived_caps)
            if final > cap + 0.01:
                errors.append(f"{label}:final_score_exceeds_claim_ledger_cap:{cap}")

    pairwise = payload.get("pairwise_comparative_consistency") or {}
    if not isinstance(pairwise, dict):
        errors.append("pairwise_comparative_consistency_not_object")
    else:
        values = [pairwise.get(field) for field in PAIRWISE_FIELDS]
        if values and all(value == "TIE" for value in values):
            evidence = pairwise.get("all_tie_claim_ledger_evidence")
            if not isinstance(evidence, list) or len([x for x in evidence if str(x).strip()]) < 2:
                errors.append("all_tie_pairwise_without_claim_ledger_evidence")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a v5.2 claim-ledger candidate score JSON.")
    parser.add_argument("--score-json", required=True)
    args = parser.parse_args()
    payload = load_json(Path(args.score_json))
    errors = validate_score_payload(payload)
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors, "provider_calls": 0}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
