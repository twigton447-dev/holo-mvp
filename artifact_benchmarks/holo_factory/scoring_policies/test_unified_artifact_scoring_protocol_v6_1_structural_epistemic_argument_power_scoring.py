from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_unified_artifact_scoring_protocol_v6_1_structural_epistemic_argument_power_score import validate_score_payload


def claim(**overrides):
    base = {
        "claim_text": "Supported operational claim",
        "claim_type": "operational",
        "cited_sources": ["S1_EXACT_SOURCE"],
        "exact_source_id_quality": "exact_full_ids",
        "source_support_status": "supported",
        "source_boundary_issue": False,
        "overclaim_issue": False,
        "stale_or_limited_evidence_issue": False,
        "missing_caveat": "",
        "severity": "none",
        "cap_or_ceiling_trigger_if_any": "",
    }
    base.update(overrides)
    return base


def row(label="ARTIFACT_001", **overrides):
    base = {
        "artifact_label": label,
        "verified_word_count": 1100,
        "word_band_pass": True,
        "structural_score_50": 48,
        "epistemic_score_50": 47,
        "structural_epistemic_score_100": 95,
        "argument_power_score_100": 92,
        "argument_power_breakdown": {
            "central_thesis_strength_15": 14,
            "argument_coherence_15": 14,
            "persuasiveness_under_uncertainty_15": 14,
            "insight_density_15": 14,
            "research_integration_15": 14,
            "practical_judgment_10": 8,
            "counterargument_handling_10": 9,
            "clarity_force_memorability_5": 5,
        },
        "raw_composite_score_100": 93.8,
        "word_count_penalty_points": 0,
        "score_after_word_count_adjustment_100": 93.8,
        "score_0_100": 93.8,
        "claim_ledger": [claim(claim_text=f"Claim {i}") for i in range(1, 9)],
        "caps_or_ceilings_applied": [],
        "invented_or_false_source_attributions": [],
        "unsupported_major_claims": [],
        "source_laundering_findings": [],
        "negative_space_misses": [],
        "tempting_but_rejected_claims": [],
        "avoided_failure_modes": ["avoided 1", "avoided 2", "avoided 3"],
        "insight_findings": ["insight 1", "insight 2", "insight 3"],
        "counterargument_analysis": "Explains the strongest alternative and why it is weaker.",
        "major_strengths": ["strength"],
        "major_defects": [],
        "would_survive_expert_review": True,
        "rationale": "fixture rationale",
    }
    base.update(overrides)
    return base


def payload(rows=None):
    return {
        "protocol_id": "unified_artifact_scoring_protocol_v6_1_structural_epistemic_argument_power",
        "artifact_scores": rows or [row()],
        "forced_rank_order_best_to_worst": ["ARTIFACT_001"],
        "pairwise_winners": {},
        "dimension_rankings": {},
        "final_forced_expert_judgment": {
            "winner": "ARTIFACT_001",
            "confidence_0_to_1": 0.8,
            "why_winner_is_stronger": "It has stronger source-grounded decision logic.",
            "why_loser_is_weaker": "The alternative is less coherent.",
            "does_final_judgment_match_numeric_score_order": True,
            "if_not_explain": "",
        },
        "score_spread_explanation": "fixture",
    }


class StructuralEpistemicV6Tests(unittest.TestCase):
    def assertInvalidContains(self, data, needle):
        errors = validate_score_payload(data)
        self.assertTrue(any(needle in error for error in errors), errors)

    def test_clean_payload_passes(self):
        self.assertEqual(validate_score_payload(payload()), [])

    def test_claim_ledger_required(self):
        self.assertInvalidContains(payload([row(claim_ledger=[])]), "claim_ledger_too_short")

    def test_claim_ledger_max_15(self):
        self.assertInvalidContains(payload([row(claim_ledger=[claim(claim_text=str(i)) for i in range(16)])]), "claim_ledger_too_long")

    def test_raw_score_math(self):
        self.assertInvalidContains(payload([row(structural_epistemic_score_100=99)]), "structural_epistemic_score_math_wrong")

    def test_argument_power_score_math(self):
        self.assertInvalidContains(payload([row(argument_power_score_100=99)]), "argument_power_score_math_wrong")

    def test_raw_composite_score_math(self):
        self.assertInvalidContains(payload([row(raw_composite_score_100=99)]), "raw_composite_score_math_wrong")

    def test_final_cannot_exceed_raw(self):
        self.assertInvalidContains(payload([row(score_0_100=95, raw_composite_score_100=93.8)]), "final_score_exceeds_raw")

    def test_word_overage_penalty_required(self):
        self.assertInvalidContains(
            payload([
                row(
                    verified_word_count=1464,
                    word_band_pass=False,
                    word_count_penalty_points=0,
                    score_after_word_count_adjustment_100=93.8,
                    score_0_100=93.8,
                )
            ]),
            "word_count_overage_penalty_math_wrong",
        )

    def test_word_overage_adjusted_score_required(self):
        self.assertInvalidContains(
            payload([
                row(
                    verified_word_count=1464,
                    word_band_pass=False,
                    word_count_penalty_points=4.92,
                    score_after_word_count_adjustment_100=93.8,
                    score_0_100=93.8,
                )
            ]),
            "score_after_word_count_adjustment_math_wrong",
        )

    def test_word_overage_score_cannot_exceed_adjusted_score(self):
        self.assertInvalidContains(
            payload([
                row(
                    verified_word_count=1464,
                    word_band_pass=False,
                    word_count_penalty_points=4.92,
                    score_after_word_count_adjustment_100=88.88,
                    score_0_100=89.5,
                )
            ]),
            "final_score_exceeds_word_count_adjusted_score",
        )

    def test_abbreviated_source_ids_cap_at_90(self):
        ledger = [claim(claim_text=f"Claim {i}", exact_source_id_quality="abbreviated_ids") for i in range(8)]
        self.assertInvalidContains(payload([row(claim_ledger=ledger, score_0_100=91)]), "abbreviated_source_ids_above_90")

    def test_invented_source_caps_at_60(self):
        self.assertInvalidContains(payload([row(invented_or_false_source_attributions=["bad"], score_0_100=61)]), "invented_or_false_source_above_60")

    def test_material_unsupported_claim_caps_at_82(self):
        ledger = [claim(claim_text=f"Claim {i}") for i in range(7)] + [claim(claim_text="bad", source_support_status="unsupported", severity="material")]
        self.assertInvalidContains(payload([row(claim_ledger=ledger, score_0_100=83)]), "material_unsupported_claim_above_82")

    def test_negative_space_miss_caps_at_83(self):
        self.assertInvalidContains(payload([row(negative_space_misses=["miss"], score_0_100=84)]), "negative_space_misses_above_83")

    def test_source_laundering_caps_at_85(self):
        self.assertInvalidContains(payload([row(source_laundering_findings=["laundered"], score_0_100=86)]), "source_laundering_above_85")

    def test_score_above_90_requires_three_avoided_failures(self):
        self.assertInvalidContains(payload([row(avoided_failure_modes=["one", "two"], score_0_100=91)]), "score_above_90_without_three")

    def test_score_above_95_rejects_major_defects(self):
        self.assertInvalidContains(
            payload([
                row(
                    score_0_100=96,
                    raw_composite_score_100=96,
                    structural_score_50=50,
                    epistemic_score_50=50,
                    structural_epistemic_score_100=100,
                    argument_power_score_100=90,
                    argument_power_breakdown={
                        "central_thesis_strength_15": 14,
                        "argument_coherence_15": 14,
                        "persuasiveness_under_uncertainty_15": 14,
                        "insight_density_15": 14,
                        "research_integration_15": 14,
                        "practical_judgment_10": 8,
                        "counterargument_handling_10": 8,
                        "clarity_force_memorability_5": 4,
                    },
                    major_defects=["defect"],
                )
            ]),
            "score_above_95_with_major_defects",
        )

    def test_pairwise_winner_must_be_exact_label(self):
        data = payload([row("ARTIFACT_001"), row("ARTIFACT_002")])
        data["pairwise_winners"] = {"ARTIFACT_001_vs_ARTIFACT_002": "TIE"}
        self.assertInvalidContains(data, "pairwise_tie_not_allowed")

    def test_argument_power_above_85_requires_insights(self):
        self.assertInvalidContains(payload([row(score_0_100=93.8, insight_findings=[])]), "argument_power_above_85_without_two")

    def test_argument_power_above_90_requires_counterargument(self):
        self.assertInvalidContains(payload([row(score_0_100=93.8, counterargument_analysis="")]), "argument_power_above_90_without_counterargument")

    def test_final_forced_judgment_required(self):
        data = payload()
        data.pop("final_forced_expert_judgment")
        self.assertInvalidContains(data, "final_forced_expert_judgment_missing")

    def test_final_forced_judgment_winner_must_be_exact_label(self):
        data = payload()
        data["final_forced_expert_judgment"]["winner"] = "TIE"
        self.assertInvalidContains(data, "final_forced_expert_judgment_tie")

    def test_old_v6_payload_fails(self):
        data = payload()
        row_data = data["artifact_scores"][0]
        for field in [
            "structural_epistemic_score_100",
            "argument_power_score_100",
            "argument_power_breakdown",
            "raw_composite_score_100",
            "insight_findings",
            "counterargument_analysis",
        ]:
            row_data.pop(field)
        row_data["raw_score_0_100"] = 95
        self.assertInvalidContains(data, "invalid_argument_power_score_100")


if __name__ == "__main__":
    unittest.main()
