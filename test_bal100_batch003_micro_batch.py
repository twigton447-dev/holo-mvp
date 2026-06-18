from __future__ import annotations

import json
from pathlib import Path


DESIGN_PATH = Path("benchmark_factory/batches/BAL100_BATCH_003_subtle_escalate_design.json")
SUMMARY_PATH = Path("reports/BAL100_BATCH_003_draft_generation_summary.json")
STATIC_GATE_PATH = Path("reports/BAL100_BATCH_003_static_kill_gate.json")
SCORECARD_PATH = Path("reports/BAL100_scorecard.json")

EXPECTED_FAMILIES = [
    "BAL100-BEC-SUBTLE-CLOSEOUT-019",
    "BAL100-BEC-SUBTLE-CLOSEOUT-020",
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


def _draft_packets() -> list[dict]:
    summary = _load(SUMMARY_PATH)
    return [_load(Path(item["path"])) for item in summary["draft_files"]]


def test_batch003_design_counts_and_boundaries() -> None:
    design = _load(DESIGN_PATH)

    assert design["batch_id"] == "BAL100-BATCH-003"
    assert design["target_counts"] == {
        "allow_hypotheses": 4,
        "escalate_hypotheses": 4,
        "pair_families": 4,
        "planned_packets": 8,
    }
    assert design["planned_family_ids"] == EXPECTED_FAMILIES
    assert design["design_constraints"]["benchmark_credit"] is False
    assert design["non_actions"]["scout"] is False
    assert design["non_actions"]["live_calls"] is False
    assert design["non_actions"]["proof_credit_changed"] is False


def test_batch003_draft_summary_and_packets_are_balanced() -> None:
    summary = _load(SUMMARY_PATH)
    packets = _draft_packets()

    assert summary["batch_id"] == "BAL100-BATCH-003"
    assert summary["counts"]["families"] == 4
    assert summary["counts"]["packets"] == 8
    assert summary["counts"]["allow_hypotheses"] == 4
    assert summary["counts"]["escalate_hypotheses"] == 4
    assert summary["counts"]["benchmark_credit"] is False
    assert summary["counts"]["scout"] is False
    assert summary["counts"]["live_calls"] is False
    assert len(packets) == 8
    assert [packet["expected_verdict"] for packet in packets].count("ALLOW") == 4
    assert [packet["expected_verdict"] for packet in packets].count("ESCALATE") == 4
    assert all(packet["draft_status"] == "batch003_candidate_draft" for packet in packets)
    assert all(packet["_builder"]["batch_id"] == "BAL100-BATCH-003" for packet in packets)
    assert all(packet["_builder"]["diagnostic_seam"] == "subtle action-boundary defect" for packet in packets)


def test_batch003_pairs_preserve_structure_and_one_material_delta() -> None:
    packets_by_family: dict[str, list[dict]] = {}
    for packet in _draft_packets():
        packets_by_family.setdefault(packet["_builder"]["family_id"], []).append(packet)

    assert sorted(packets_by_family) == EXPECTED_FAMILIES
    for family_id, pair in packets_by_family.items():
        pair = sorted(pair, key=lambda packet: packet["_builder"]["sibling_slot"])
        allow, sibling = pair
        assert allow["expected_verdict"] == "ALLOW"
        assert sibling["expected_verdict"] == "ESCALATE"
        assert allow["payload"]["context"]["action_boundary"] == sibling["payload"]["context"]["action_boundary"]
        assert allow["payload"]["context"]["explanation_summary"] == sibling["payload"]["context"]["explanation_summary"]

        allow_docs = allow["payload"]["context"]["internal_documents"]
        sibling_docs = sibling["payload"]["context"]["internal_documents"]
        assert [doc["doc_id"] for doc in allow_docs] == [doc["doc_id"] for doc in sibling_docs]
        assert [doc["type"] for doc in allow_docs] == [doc["type"] for doc in sibling_docs]

        changed_doc_ids = [
            a["doc_id"]
            for a, b in zip(allow_docs, sibling_docs)
            if a["content"] != b["content"]
        ]
        assert changed_doc_ids == [allow["_builder"]["material_delta_doc_id"]], family_id


def test_batch003_model_visible_payload_has_no_answer_key_language() -> None:
    for packet in _draft_packets():
        visible = json.dumps(packet["payload"], sort_keys=True).lower()
        for forbidden in FORBIDDEN_MODEL_VISIBLE_TERMS:
            assert forbidden not in visible, (packet["scenario_id"], forbidden)
        assert "expected_verdict" not in visible
        assert "spec_target_verdict" not in visible
        assert "proof_credit" not in visible


def test_batch003_static_gate_passes_quality_target() -> None:
    gate = _load(STATIC_GATE_PATH)

    assert gate["batch_id"] == "BAL100-BATCH-003"
    assert gate["classification_counts"] == {
        "kill_before_scout": 0,
        "repair_before_scout": 0,
        "scout_ready": 4,
    }
    assert gate["aggressive_target_met"] is True
    assert gate["scout_ready_threshold"] == 3
    for item in gate["family_classifications"]:
        assert item["classification"] == "scout_ready"
        assert item["escalate_screams_answer"] is False
        assert item["model_visible_answer_key_leak"] is False
        assert item["more_than_one_material_delta"] is False
        assert item["generic_blocker"] is False
        assert item["second_blocker"] is False


def test_batch003_does_not_change_proof_credit() -> None:
    scorecard = _load(SCORECARD_PATH)
    proof_credit = scorecard["proof_credit_ready"]

    assert proof_credit["pair_families"] == 2
    assert proof_credit["packets"] == 4
    assert proof_credit["families"] == ["BEC-PAIR-009", "BEC-PAIR-010"]
