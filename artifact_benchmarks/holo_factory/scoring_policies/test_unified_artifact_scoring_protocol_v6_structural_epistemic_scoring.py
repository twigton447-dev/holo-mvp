from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_unified_artifact_scoring_protocol_v6_structural_epistemic_score import validate_score_payload


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
        "raw_score_0_100": 95,
        "score_0_100": 95,
        "claim_ledger": [claim(claim_text=f"Claim {i}") for i in range(1, 9)],
        "caps_or_ceilings_applied": [],
        "invented_or_false_source_attributions": [],
        "unsupported_major_claims": [],
        "source_laundering_findings": [],
        "negative_space_misses": [],
        "tempting_but_rejected_claims": [],
        "avoided_failure_modes": ["avoided 1", "avoided 2", "avoided 3"],
        "major_strengths": ["strength"],
        "major_defects": [],
        "would_survive_expert_review": True,
        "rationale": "fixture rationale",
    }
    base.update(overrides)
    return base


def payload(rows=None):
    return {
        "protocol_id": "unified_artifact_scoring_protocol_v6_structural_epistemic",
        "artifact_scores": rows or [row()],
        "forced_rank_order_best_to_worst": ["ARTIFACT_001"],
        "pairwise_winners": {},
        "dimension_rankings": {},
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
        self.assertInvalidContains(payload([row(raw_score_0_100=99)]), "raw_score_math_wrong")

    def test_final_cannot_exceed_raw(self):
        self.assertInvalidContains(payload([row(score_0_100=96, raw_score_0_100=95)]), "final_score_exceeds_raw")

    def test_word_band_fail_caps_at_88(self):
        self.assertInvalidContains(payload([row(word_band_pass=False, score_0_100=90)]), "word_band_fail_above_88")

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
        self.assertInvalidContains(payload([row(score_0_100=96, raw_score_0_100=96, structural_score_50=48, epistemic_score_50=48, major_defects=["defect"])]), "score_above_95_with_major_defects")

    def test_pairwise_winner_must_be_exact_label(self):
        data = payload([row("ARTIFACT_001"), row("ARTIFACT_002")])
        data["pairwise_winners"] = {"ARTIFACT_001_vs_ARTIFACT_002": "TIE"}
        self.assertInvalidContains(data, "pairwise_tie_not_allowed")


if __name__ == "__main__":
    unittest.main()
