from __future__ import annotations

import json
from pathlib import Path


DESIGN = Path("benchmark_factory/batches/BAL100-BATCH-001_bec_callback_provenance_design.json")
BLOCKER_SOURCES = (
    "portal",
    "change_request",
    "invoice",
    "submitted_contact",
    "newly supplied",
)


def _design() -> dict:
    return json.loads(DESIGN.read_text())


def test_batch001_has_required_balanced_design_shape() -> None:
    design = _design()
    families = design["families"]

    assert design["batch_id"] == "BAL100-BATCH-001"
    assert len(families) == 8
    assert len(families) * 2 == 16
    assert sum(1 for family in families if family["allow_hypothesis"] == "ALLOW") == 8
    assert sum(1 for family in families if family["escalate_hypothesis"] == "ESCALATE") == 8


def test_batch001_is_only_bec_callback_provenance_planned_work() -> None:
    for family in _design()["families"]:
        assert family["seam_id"] == "BEC_CALLBACK_PROVENANCE"
        assert family["batch_id"] == "BAL100-BATCH-001"
        assert family["domain"] == "BEC"
        assert family["promotion_status"] == "planned"


def test_batch001_pairs_require_same_structure_and_one_delta() -> None:
    for family in _design()["families"]:
        assert family["same_structure_required"] is True
        assert family["one_material_delta_required"] is True
        assert family["allow_packet_id"] != family["escalate_packet_id"]
        assert family["artifact_template"]
        delta = family["material_delta"].lower()
        assert "callback" in delta
        assert "source" in delta
        assert "provenance" in delta


def test_allow_closures_preserve_completed_controls_and_prechange_source() -> None:
    for family in _design()["families"]:
        closure = family["allow_control_closure"].lower()
        assert "completed controls" in closure
        assert "pre-change" in closure
        assert "vendor-master" in closure


def test_escalate_blockers_preserve_bad_callback_source_boundary() -> None:
    for family in _design()["families"]:
        blocker = family["escalate_blocker"].lower()
        assert "callback" in blocker
        assert "noncompliant" in blocker
        assert any(source in blocker for source in BLOCKER_SOURCES)


def test_batch001_contains_no_generated_or_evidence_credit_state() -> None:
    forbidden_truthy = ("generated", "frozen", "traced", "judged", "proof_credit_ready")

    for family in _design()["families"]:
        assert family["promotion_status"] == "planned"
        for key in forbidden_truthy:
            assert family[key] is False
