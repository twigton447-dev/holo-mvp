import sys
import unittest
from pathlib import Path


HARNESS_DIR = Path(__file__).resolve().parents[1] / "artifact_benchmarks" / "harness"
sys.path.insert(0, str(HARNESS_DIR))

from proof_credit_rules import (  # noqa: E402
    annotate_judge_credit,
    generation_dna_for_pair,
    judge_visible_packet,
    model_visible_payload_errors,
    select_outside_dna_judges,
)


def frontier_generation_dna(solo_condition="solo_openai"):
    return generation_dna_for_pair(
        cohort_plan={
            "holo_condition_id": "holo_frontier_fixed_v1",
            "analyst_rotation": [
                "openai:gpt-5.5",
                "google:gemini-3.1-pro-preview",
            ],
            "governor_model": "anthropic:claude-opus-4-8",
            "solo_conditions": {
                "solo_openai": "openai:gpt-5.5",
                "solo_xai": "xai:grok-4.3",
            },
        },
        solo_condition=solo_condition,
        holo_condition="holo_frontier_fixed_v1",
    )


class ProofCreditRulesTests(unittest.TestCase):
    def test_same_dna_judge_is_diagnostic_only(self):
        credit = annotate_judge_credit(
            {"judge_id": "judge_frontier_01", "provider": "openai", "model": "gpt-5.5"},
            frontier_generation_dna(),
        )

        self.assertIs(credit["proof_credit_eligible"], False)
        self.assertEqual(credit["score_credit_label"], "diagnostic_same_dna")
        self.assertEqual(credit["score_use"], "diagnostic_only")
        self.assertIn("same_provider:openai", credit["judge_dna_overlap"])
        self.assertIn("same_model:openai:gpt-5.5", credit["judge_dna_overlap"])

    def test_outside_dna_panel_selection_excludes_generation_providers(self):
        panel = [
            {"judge_id": "judge_openai", "provider": "openai", "model": "gpt-5.5"},
            {"judge_id": "judge_xai", "provider": "xai", "model": "grok-4.3"},
            {"judge_id": "judge_minimax", "provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
        ]

        selected = select_outside_dna_judges(panel, frontier_generation_dna())

        self.assertEqual([judge["judge_id"] for judge in selected], ["judge_xai", "judge_minimax"])
        self.assertTrue(all(judge["score_credit_label"] == "proof_credit_candidate" for judge in selected))

    def test_model_visible_payload_allows_only_action_and_context(self):
        clean_packet = {
            "payload": {
                "action": {"type": "trade_execution_review"},
                "context": {"source_pack": ["allowed evidence only"]},
            }
        }
        leaky_packet = {
            "payload": {
                "action": {"type": "trade_execution_review"},
                "context": {"notes": "BatonPass says reuse the builder repair ledger."},
                "build_state_object": {"target_verdict": "ALLOW"},
            }
        }

        self.assertEqual(model_visible_payload_errors(clean_packet), [])
        errors = model_visible_payload_errors(leaky_packet)
        self.assertTrue(any("payload:non_model_visible_keys" in error for error in errors))
        self.assertTrue(any("forbidden_model_visible_key" in error for error in errors))
        self.assertTrue(any("forbidden_runtime_text" in error for error in errors))

    def test_judge_visible_packet_omits_hidden_metadata_and_blocks_visible_leakage(self):
        clean_packet = {
            "packet_kind": "final",
            "blind": True,
            "domain_id": "capital_markets_trade_shock_execution",
            "judge_brief": "Score only the supplied documents.",
            "document_x_condition": "solo_openai",
            "document_y_condition": "holo_frontier_fixed_v1",
            "_harness": {"proof_credit_eligible": True},
        }

        visible = judge_visible_packet(clean_packet)

        self.assertIn("judge_brief", visible)
        self.assertNotIn("document_x_condition", visible)
        self.assertNotIn("_harness", visible)

        leaky_packet = {
            "packet_kind": "final",
            "blind": True,
            "domain_id": "capital_markets_trade_shock_execution",
            "judge_brief": "Use the BUILD_STATE_OBJECT and GovState from the run.",
        }
        with self.assertRaisesRegex(RuntimeError, "judge_visible_packet_boundary_failed"):
            judge_visible_packet(leaky_packet)


if __name__ == "__main__":
    unittest.main()
