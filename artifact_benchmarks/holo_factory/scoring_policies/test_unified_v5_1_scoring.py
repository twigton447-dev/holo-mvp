from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_unified_v5_1_score import validate_score_payload


def cap(cap_id: str, max_score: float, evidence: str = "fixture") -> dict:
    return {"cap_id": cap_id, "max_score_100": max_score, "evidence": evidence}


def base_row(label: str = "ARTIFACT_001", score: float = 84.0) -> dict:
    return {
        "artifact_label": label,
        "admission_status": "pass",
        "raw_evidence_score_100": score,
        "applicable_hard_caps": [],
        "applicable_expert_ceilings": [],
        "final_score_100": score,
        "final_score_10": round(score / 10, 2),
        "ceiling_band": "84_89_decision_useful",
        "passes_source_fidelity_gate": True,
        "passes_source_to_claim_traceability_gate": True,
        "passes_decision_logic_gate": True,
        "passes_operational_specificity_gate": True,
        "passes_uncertainty_gate": True,
        "passes_contradiction_negative_space_gate": True,
        "passes_risk_suppression_gate": True,
        "passes_expert_review_gate": True,
        "source_fidelity_score_15": 12,
        "source_to_claim_traceability_score_10": 8,
        "contradiction_handling_score_10": 8,
        "uncertainty_limitations_score_10": 8,
        "data_stat_chart_score_8": 6,
        "decision_usefulness_score_12": 10,
        "operational_actionability_score_10": 8,
        "risk_suppression_blindspot_score_15": 14,
        "expert_review_survivability_score_10": 10,
        "hallucination_resistance_findings": ["uses frozen source IDs only"],
        "source_boundary_findings": ["does not treat draft as final"],
        "blindspots_caught": ["capacity benefit not proven"],
        "blindspots_missed": [],
        "tempting_but_rejected_claims": ["capacity solved"],
        "overclaim_risks_suppressed": ["no admission reduction claim"],
        "unsupported_or_weak_claims": [],
        "avoided_failure_modes": ["false reassurance", "FDA overclaim"],
        "expert_review_survivability_rationale": "Would survive expert review with minor edits.",
        "why_not_100": "Needs stronger operational measurement plan and more explicit subgroup monitoring.",
        "weakest_source_to_claim_link": "Pilot benefit remains inferred rather than proven.",
        "missing_or_underdeveloped_caveat": "Local staffing constraints are not fully specified.",
        "unresolved_uncertainty": "Does monitoring improve outcomes versus check-ins?",
        "biggest_overclaim_risk": "Readers may treat pilot as capacity solution.",
        "risk_if_leader_relied_on_it": "Could overdeploy before equity safeguards are working.",
        "expert_reviewer_challenge": "Show local device performance and escalation staffing.",
        "needed_to_move_above_83": "Keep source boundaries and stop rules explicit.",
        "needed_to_move_above_90": "Add stronger expert-review rationale and avoided failure modes.",
        "needed_to_move_above_95": "Add validation data and implementation metrics.",
        "material_repairs_required": ["Add local pilot measurement protocol"],
        "most_dangerous_failure_if_relied_on": "False reassurance in deteriorating patients.",
        "required_repairs_to_clear_next_band": "Add explicit subgroup monitoring and escalation staffing.",
    }


def base_payload(score: float = 84.0) -> dict:
    return {
        "protocol_id": "unified_artifact_scoring_protocol_v5_1",
        "judge_id": "fixture_judge",
        "source_packet_present": True,
        "artifact_scores": [base_row("ARTIFACT_001", score), base_row("ARTIFACT_003", score)],
        "pairwise_comparative_consistency": {
            "more_source_faithful": "ARTIFACT_001",
            "more_decision_useful": "ARTIFACT_001",
            "safer_to_rely_on": "ARTIFACT_001",
            "better_uncertainty_handling": "ARTIFACT_001",
            "better_contradiction_handling": "ARTIFACT_001",
            "better_blindspot_detection": "ARTIFACT_001",
            "better_hallucination_resistance": "ARTIFACT_001",
            "better_overclaim_suppression": "ARTIFACT_001",
            "more_operationally_actionable": "ARTIFACT_001",
            "more_expert_survivable": "ARTIFACT_001",
            "overall_winner": "ARTIFACT_001",
            "numeric_pairwise_consistency_rationale": "Numeric scores align with pairwise winners.",
        },
        "ranking_score_consistency_check": "Consistent.",
        "overall_rationale": "Fixture.",
    }


class V51ValidatorTests(unittest.TestCase):
    def assertInvalidContains(self, payload: dict, needle: str) -> None:
        errors = validate_score_payload(payload)
        self.assertTrue(any(needle in err for err in errors), errors)

    def test_valid_fixture_passes(self):
        self.assertEqual(validate_score_payload(base_payload()), [])

    def test_invented_source_above_70_fails(self):
        payload = base_payload(84)
        payload["artifact_scores"][0]["applicable_hard_caps"] = [cap("invented_source_or_citation", 70)]
        self.assertInvalidContains(payload, "invented_source_above_70")

    def test_false_attribution_above_75_fails(self):
        payload = base_payload(84)
        payload["artifact_scores"][0]["applicable_hard_caps"] = [cap("false_source_attribution", 75)]
        self.assertInvalidContains(payload, "false_source_attribution_above_75")

    def test_failed_gate_above_83_fails(self):
        payload = base_payload(84)
        payload["artifact_scores"][0]["passes_uncertainty_gate"] = False
        self.assertInvalidContains(payload, "score_above_83_with_failed_gate")

    def test_risk_suppression_gate_false_above_83_fails(self):
        payload = base_payload(84)
        payload["artifact_scores"][0]["passes_risk_suppression_gate"] = False
        self.assertInvalidContains(payload, "risk_suppression_gate_false_above_83")

    def test_score_above_90_without_avoided_failure_modes_fails(self):
        payload = base_payload(91)
        payload["artifact_scores"][0]["avoided_failure_modes"] = ["one"]
        self.assertInvalidContains(payload, "score_above_90_needs_two_avoided_failure_modes")

    def test_score_above_85_without_defect_audit_fails(self):
        payload = base_payload(86)
        payload["artifact_scores"][0]["why_not_100"] = ""
        self.assertInvalidContains(payload, "score_above_85_missing_defect_audit")

    def test_pairwise_prose_label_fails(self):
        payload = base_payload()
        payload["pairwise_comparative_consistency"]["overall_winner"] = "Artifact 1 is better"
        self.assertInvalidContains(payload, "pairwise_label_not_exact")

    def test_source_packet_missing_but_source_fidelity_accepted_fails(self):
        payload = base_payload()
        payload["source_packet_present"] = False
        self.assertInvalidContains(payload, "source_packet_missing_but_source_fidelity_accepted")

    def test_raw_text_cap_trigger_with_empty_caps_fails(self):
        payload = base_payload()
        payload["raw_judge_text"] = "This artifact contains an invented source and should be capped."
        self.assertInvalidContains(payload, "raw_text_indicates_cap_trigger_but_parsed_caps_empty")


if __name__ == "__main__":
    unittest.main()
