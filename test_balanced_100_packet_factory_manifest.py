from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


MANIFEST = Path("benchmark_factory/balanced_100_packet_manifest_v0_1.json")
APPROVED_STATUSES = {
    "planned",
    "drafted",
    "prefreeze_reviewed",
    "frozen",
    "ledgered",
    "dry_run_passed",
    "live_traced",
    "judged",
    "loss_autopsied",
    "regression_protected",
    "proof_credit_ready",
}


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def test_balanced_manifest_has_required_100_packet_shape() -> None:
    manifest = _manifest()
    families = manifest["pair_families"]
    seams = manifest["seams"]

    assert len(families) == 50
    assert len(families) * 2 == 100
    assert len(seams) == 5
    assert sum(1 for family in families if family["allow_expected_hypothesis"] == "ALLOW") == 50
    assert sum(1 for family in families if family["escalate_expected_hypothesis"] == "ESCALATE") == 50


def test_each_seam_has_exactly_ten_pair_families() -> None:
    manifest = _manifest()
    seam_counts = Counter(family["seam_id"] for family in manifest["pair_families"])

    assert set(seam_counts) == {seam["seam_id"] for seam in manifest["seams"]}
    assert all(count == 10 for count in seam_counts.values())


def test_each_pair_has_one_allow_one_escalate_and_required_delta_controls() -> None:
    for family in _manifest()["pair_families"]:
        assert family["allow_expected_hypothesis"] == "ALLOW"
        assert family["escalate_expected_hypothesis"] == "ESCALATE"
        assert family["allow_packet_id"] != family["escalate_packet_id"]
        assert family["same_structure_required"] is True
        assert family["one_material_delta_required"] is True
        assert family["material_delta"].strip()
        assert family["artifact_template"]


def test_promotion_status_values_are_approved_lifecycle_values() -> None:
    manifest = _manifest()
    approved_from_manifest = set(manifest["approved_lifecycle_statuses"])

    assert approved_from_manifest == APPROVED_STATUSES
    for family in manifest["pair_families"]:
        assert family["promotion_status"] in APPROVED_STATUSES
        assert set(family["evidence_state"]) <= APPROVED_STATUSES


def test_existing_hbb_bec_pairs_are_represented_without_proof_credit() -> None:
    families = {family["family_id"]: family for family in _manifest()["pair_families"]}

    hbb_bec_001 = families["BEC-PAIR-001"]
    assert hbb_bec_001["allow_packet_id"] == "HBB-BEC-001"
    assert hbb_bec_001["escalate_packet_id"] == "HBB-BEC-001-CALLBACK-PROVENANCE-FAIL"
    assert hbb_bec_001["promotion_status"] == "regression_protected"
    assert hbb_bec_001["existing_family"] is True
    assert hbb_bec_001["needs_post_patch_rerun"] is True
    assert hbb_bec_001["proof_credit_ready"] is False
    assert "judged" in hbb_bec_001["evidence_state"]
    assert "loss_autopsied" in hbb_bec_001["evidence_state"]
    assert "regression_protected" in hbb_bec_001["evidence_state"]
    assert "needs post-patch rerun" in hbb_bec_001["notes"].lower()

    hbb_bec_002 = families["BEC-PAIR-002"]
    assert hbb_bec_002["allow_packet_id"] == "HBB-BEC-002-HARD-ALLOW"
    assert hbb_bec_002["escalate_packet_id"] == "HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL"
    assert hbb_bec_002["promotion_status"] == "regression_protected"
    assert hbb_bec_002["existing_family"] is True
    assert hbb_bec_002["needs_post_patch_rerun"] is True
    assert hbb_bec_002["proof_credit_ready"] is False
    assert "judged" in hbb_bec_002["evidence_state"]
    assert "loss_autopsied" in hbb_bec_002["evidence_state"]
    assert "regression_protected" in hbb_bec_002["evidence_state"]
    assert "needs post-patch rerun" in hbb_bec_002["notes"].lower()
