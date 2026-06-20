from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_unified_v5_2_claim_ledger_score import validate_score_payload

SOURCE_IDS = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"]


def claim(i: int, **overrides):
    row = {
        "claim_id": f"C{i}",
        "claim_text": f"Claim {i}",
        "claim_type": "factual",
        "cited_sources": ["S1"],
        "source_support_status": "supported",
        "source_boundary_issue": False,
        "overclaim_issue": False,
        "stale_or_limited_evidence_issue": False,
        "missing_caveat": "",
        "severity": "none",
        "cap_trigger_if_any": None,
    }
    row.update(overrides)
    return row


def ledger(**overrides):
    base = {
        "major_claims": [claim(i) for i in range(1, 9)],
        "invented_or_false_source_attributions": [],
        "unsupported_major_claims": [],
        "source_laundering_findings": [],
        "negative_space_misses": [],
        "tempting_but_rejected_claims": ["capacity solved"],
        "avoided_failure_modes": ["FDA draft treated as non-final", "capacity benefit not overclaimed"],
    }
    base.update(overrides)
    return base


def artifact(label="ARTIFACT_001", score=84, **overrides):
    row = {
        "artifact_label": label,
        "raw_evidence_score_100": score,
        "final_score_100": score,
        "claim_ledger": ledger(),
    }
    row.update(overrides)
    return row


def payload(**overrides):
    base = {
        "protocol_id": "unified_artifact_scoring_protocol_v5_2_claim_ledger_candidate",
        "source_packet_source_ids": SOURCE_IDS,
        "artifact_scores": [artifact("ARTIFACT_001"), artifact("ARTIFACT_003")],
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
        },
    }
    base.update(overrides)
    return base


class V52ClaimLedgerTests(unittest.TestCase):
    def assertInvalidContains(self, doc, needle):
        errors = validate_score_payload(doc)
        self.assertTrue(any(needle in err for err in errors), errors)

    def test_valid_fixture_passes(self):
        self.assertEqual(validate_score_payload(payload()), [])

    def test_judge_cannot_score_without_claim_ledger(self):
        doc = payload()
        del doc["artifact_scores"][0]["claim_ledger"]
        self.assertInvalidContains(doc, "missing_claim_ledger")

    def test_false_source_attribution_triggers_cap(self):
        doc = payload()
        led = ledger(invented_or_false_source_attributions=["S9 falsely attributed to FDA"])
        doc["artifact_scores"][0] = artifact("ARTIFACT_001", 80, claim_ledger=led)
        self.assertInvalidContains(doc, "final_score_exceeds_claim_ledger_cap:75")

    def test_unsupported_major_claim_triggers_cap(self):
        doc = payload()
        claims = [claim(i) for i in range(1, 9)]
        claims[0] = claim(1, source_support_status="unsupported", severity="material", cap_trigger_if_any="unsupported_major_claim")
        led = ledger(major_claims=claims, unsupported_major_claims=["C1 unsupported recommendation"])
        doc["artifact_scores"][0] = artifact("ARTIFACT_001", 84, claim_ledger=led)
        self.assertInvalidContains(doc, "final_score_exceeds_claim_ledger_cap:82")

    def test_score_above_83_fails_with_material_negative_space_miss(self):
        doc = payload()
        led = ledger(negative_space_misses=[{"claim_id": "C4", "severity": "material", "issue": "capacity benefit negative space missing"}])
        doc["artifact_scores"][0] = artifact("ARTIFACT_001", 84, claim_ledger=led)
        self.assertInvalidContains(doc, "material_negative_space_above_83")

    def test_all_tie_pairwise_fails_without_evidence(self):
        tie = {field: "TIE" for field in [
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
        ]}
        self.assertInvalidContains(payload(pairwise_comparative_consistency=tie), "all_tie_pairwise_without_claim_ledger_evidence")

    def test_score_above_90_fails_without_three_avoided_failure_modes(self):
        doc = payload()
        doc["artifact_scores"][0] = artifact("ARTIFACT_001", 91, claim_ledger=ledger(avoided_failure_modes=["one", "two"]))
        self.assertInvalidContains(doc, "score_above_90_needs_three_avoided_failure_modes")


if __name__ == "__main__":
    unittest.main()
