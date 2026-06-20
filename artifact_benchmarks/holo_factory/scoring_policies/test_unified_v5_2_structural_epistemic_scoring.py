from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_unified_v5_2_structural_epistemic_score import validate_score_payload


def cap(cap_id: str, max_score: float) -> dict:
    return {"cap_id": cap_id, "max_score_100": max_score, "evidence": "fixture"}


def row(label: str = "ARTIFACT_001", structural: dict | None = None, epistemic: dict | None = None, caps: list | None = None) -> dict:
    structural = structural or {
        "bluf": 3,
        "data_isolation": 3,
        "option_distinctness": 3,
        "evidence_constraints": 3,
        "risk_symmetry": 3,
        "scannability": 3,
    }
    epistemic = epistemic or {
        "claim_evidence_distance": 3,
        "conflicting_data_handling": 3,
        "insight_vs_summary": 3,
        "operational_reality_gap": 3,
        "source_weighting_validity": 3,
    }
    structural_total = sum(structural.values())
    epistemic_total = sum(epistemic.values())
    raw_total = structural_total + epistemic_total
    normalized = round((raw_total / 33) * 100, 1)
    caps = caps or []
    final = min([normalized] + [float(item.get("max_score_100", 100)) for item in caps if isinstance(item, dict)])
    if final >= 95:
        band = "Executive-ready / highly rigorous"
    elif final >= 90:
        band = "Strong / expert-survivable with minor edits"
    elif final >= 83:
        band = "Functional / needs revision"
    elif final >= 70:
        band = "Draft quality / research summary"
    else:
        band = "Rejected / not decision-grade"
    return {
        "artifact_id": label,
        "structural_scores": structural,
        "structural_raw_18": structural_total,
        "epistemic_scores": epistemic,
        "epistemic_raw_15": epistemic_total,
        "raw_total_33": raw_total,
        "normalized_total_100": normalized,
        "applicable_hard_caps": caps,
        "final_score_100": final,
        "band": band,
        "dimension_justifications": {"fixture": "all scored dimensions have fixture evidence"},
        "strongest_dimensions": ["BLUF"],
        "weakest_dimensions": ["none"],
        "required_repairs_to_next_band": ["fixture repair note"],
        "expert_reviewer_challenge": "fixture expert challenge",
        "decision_reliance_risk": "fixture reliance risk",
    }


def payload(rows: list[dict] | None = None) -> dict:
    return {
        "protocol_id": "unified_artifact_scoring_protocol_v5_2_structural_epistemic",
        "artifact_scores": rows or [row()],
    }


class StructuralEpistemicV52Tests(unittest.TestCase):
    def assertInvalidContains(self, data: dict, needle: str) -> None:
        errors = validate_score_payload(data)
        self.assertTrue(any(needle in err for err in errors), errors)

    def test_full_score_fixture_passes(self):
        self.assertEqual(validate_score_payload(payload([row()])), [])

    def test_manual_d5_regression_fixture_passes(self):
        fixture_path = Path(__file__).with_name("unified_artifact_scoring_protocol_v5_2_structural_epistemic_d5_manual_regression_fixture.json")
        self.assertEqual(validate_score_payload(__import__("json").loads(fixture_path.read_text(encoding="utf-8"))), [])

    def test_artifact_003_manual_math_band_is_84_8(self):
        fixture_path = Path(__file__).with_name("unified_artifact_scoring_protocol_v5_2_structural_epistemic_d5_manual_regression_fixture.json")
        data = __import__("json").loads(fixture_path.read_text(encoding="utf-8"))
        artifact = [item for item in data["artifact_scores"] if item["artifact_id"] == "ARTIFACT_003"][0]
        self.assertEqual(artifact["raw_total_33"], 28)
        self.assertEqual(artifact["normalized_total_100"], 84.8)
        self.assertEqual(artifact["band"], "Functional / needs revision")

    def test_invalid_dimension_score_fails(self):
        data = payload([row()])
        data["artifact_scores"][0]["structural_scores"]["bluf"] = 4
        self.assertInvalidContains(data, "invalid_dimension_score")

    def test_structural_math_error_fails(self):
        data = payload([row()])
        data["artifact_scores"][0]["structural_raw_18"] = 17
        self.assertInvalidContains(data, "structural_subtotal_math_wrong")

    def test_normalized_math_error_fails(self):
        data = payload([row()])
        data["artifact_scores"][0]["normalized_total_100"] = 99.0
        self.assertInvalidContains(data, "normalized_score_math_wrong")

    def test_final_score_cannot_exceed_hard_cap(self):
        capped = row(caps=[cap("invented_source_or_citation", 70)])
        capped["final_score_100"] = 90
        capped["band"] = "Strong / expert-survivable with minor edits"
        self.assertInvalidContains(payload([capped]), "final_score_exceeds_hard_cap")

    def test_95_plus_requires_all_dimensions_at_3(self):
        structural = {
            "bluf": 2,
            "data_isolation": 3,
            "option_distinctness": 3,
            "evidence_constraints": 3,
            "risk_symmetry": 3,
            "scannability": 3,
        }
        data = row(structural=structural)
        data["structural_raw_18"] = 17
        data["raw_total_33"] = 32
        data["normalized_total_100"] = 97.0
        data["final_score_100"] = 97.0
        data["band"] = "Executive-ready / highly rigorous"
        self.assertInvalidContains(payload([data]), "score_95_plus_with_structural_dimension_below_3")

    def test_90_plus_requires_key_epistemic_dimensions_at_3(self):
        epistemic = {
            "claim_evidence_distance": 2,
            "conflicting_data_handling": 3,
            "insight_vs_summary": 3,
            "operational_reality_gap": 3,
            "source_weighting_validity": 3,
        }
        data = row(epistemic=epistemic)
        data["epistemic_raw_15"] = 14
        data["raw_total_33"] = 32
        data["normalized_total_100"] = 97.0
        data["final_score_100"] = 97.0
        data["band"] = "Executive-ready / highly rigorous"
        self.assertInvalidContains(payload([data]), "score_90_plus_claim_evidence_distance_below_3")

    def test_no_clear_decision_cap_above_83_fails(self):
        capped = row(caps=[cap("no_clear_decision_recommendation", 83)])
        capped["final_score_100"] = 84
        capped["band"] = "Functional / needs revision"
        self.assertInvalidContains(payload([capped]), "no_clear_decision_recommendation_above_83")

    def test_no_operational_stop_logic_cap_above_83_fails(self):
        capped = row(caps=[cap("no_operational_stop_go_logic", 83)])
        capped["final_score_100"] = 84
        capped["band"] = "Functional / needs revision"
        self.assertInvalidContains(payload([capped]), "no_operational_stop_go_logic_above_83")


if __name__ == "__main__":
    unittest.main()
