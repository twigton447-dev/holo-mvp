from __future__ import annotations

import json
from pathlib import Path


STATIC_GATE_PATH = Path("reports/BAL100_BATCH_003_targeted_post_repair_static_gate.json")
SCORECARD_PATH = Path("reports/BAL100_scorecard.json")

REPAIRED_FAMILIES = [
    "BAL100-BEC-SUBTLE-CLOSEOUT-019",
    "BAL100-BEC-SUBTLE-CLOSEOUT-020",
]
RETIRED_FAMILIES = [
    "BAL100-BEC-SUBTLE-CLOSEOUT-021",
    "BAL100-BEC-SUBTLE-CLOSEOUT-022",
]
FORBIDDEN_MODEL_VISIBLE_TERMS = (
    "provenance fail",
    "hidden blocker",
    "unsafe",
    "escalate",
    "fraud",
    "sanctions",
    "missing po",
    "missing approval",
    "bank mismatch",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _packet_path(family_suffix: str, sibling_slot: str) -> Path:
    return Path(f"holo_builder/outputs/builder/BAL100_BATCH_003_SUBTLE_CLOSEOUT_{family_suffix}_{sibling_slot}_draft_v0_1.json")


def test_targeted_post_repair_static_gate_scope_and_classes() -> None:
    gate = _load(STATIC_GATE_PATH)

    assert gate["batch_id"] == "BAL100-BATCH-003"
    assert gate["scope"]["repaired_family_ids"] == REPAIRED_FAMILIES
    assert gate["scope"]["retired_not_touched_family_ids"] == RETIRED_FAMILIES
    assert gate["scope"]["live_scout_run"] is False
    assert gate["scope"]["judge_run"] is False
    assert gate["scope"]["freeze_run"] is False
    assert gate["scope"]["proof_credit_mutated"] is False
    assert gate["classification_counts"] == {
        "targeted_rescout_ready": 2,
        "repair_failed_kill": 0,
        "needs_human_review": 0,
    }

    assert [item["family_id"] for item in gate["family_static_gate"]] == REPAIRED_FAMILIES
    for item in gate["family_static_gate"]:
        assert item["post_repair_static_gate_class"] == "targeted_rescout_ready"
        checks = item["post_repair_checks"]
        assert checks["allow_sibling_closes_exact_action_boundary"] is True
        assert checks["escalate_sibling_has_one_narrow_unresolved_defect"] is True
        assert checks["defect_subtle_not_neon"] is True
        assert checks["exactly_one_material_delta"] is True
        assert checks["new_secondary_blockers_introduced"] is False
        assert checks["sibling_artifact_structure_mirrors"] is True
        assert checks["model_visible_answer_key_leak"] is False
        assert checks["benchmark_credit_mutation"] is False


def test_repaired_batch003_pairs_preserve_symmetry_and_one_material_delta() -> None:
    for family_suffix in ("019", "020"):
        allow = _load(_packet_path(family_suffix, "A"))
        sibling = _load(_packet_path(family_suffix, "B"))

        assert allow["expected_verdict"] == "ALLOW"
        assert sibling["expected_verdict"] == "ESCALATE"
        assert allow["draft_status"] == "batch003_candidate_draft"
        assert sibling["draft_status"] == "batch003_candidate_draft"
        assert allow["_builder"]["family_id"] == sibling["_builder"]["family_id"]
        assert allow["payload"]["context"]["action_boundary"] == sibling["payload"]["context"]["action_boundary"]
        assert allow["payload"]["context"]["explanation_summary"] == sibling["payload"]["context"]["explanation_summary"]

        allow_docs = allow["payload"]["context"]["internal_documents"]
        sibling_docs = sibling["payload"]["context"]["internal_documents"]
        assert [doc["doc_id"] for doc in allow_docs] == [doc["doc_id"] for doc in sibling_docs]
        assert [doc["type"] for doc in allow_docs] == [doc["type"] for doc in sibling_docs]

        changed_doc_ids = [
            allow_doc["doc_id"]
            for allow_doc, sibling_doc in zip(allow_docs, sibling_docs)
            if allow_doc["content"] != sibling_doc["content"]
        ]
        assert changed_doc_ids == [allow["_builder"]["material_delta_doc_id"]]

        for packet in (allow, sibling):
            visible = json.dumps(packet["payload"], sort_keys=True).lower()
            for forbidden in FORBIDDEN_MODEL_VISIBLE_TERMS:
                assert forbidden not in visible, (packet["scenario_id"], forbidden)
            assert "expected_verdict" not in visible
            assert "spec_target_verdict" not in visible
            assert "proof_credit" not in visible


def test_batch003_targeted_repair_does_not_change_proof_credit() -> None:
    scorecard = _load(SCORECARD_PATH)
    proof_credit = scorecard["proof_credit_ready"]

    assert proof_credit["pair_families"] == 2
    assert proof_credit["packets"] == 4
    assert proof_credit["families"] == ["BEC-PAIR-009", "BEC-PAIR-010"]
