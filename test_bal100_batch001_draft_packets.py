from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from holo_builder.freeze_manifest import payload_visibility_errors


DRAFT_GLOB = "holo_builder/outputs/builder/BAL100_BEC_PAIR_*_draft_v0_1.json"
EXPECTED_FAMILIES = {f"BEC-PAIR-{idx:03d}" for idx in range(3, 11)}
PAYLOAD_KEYS = {"action", "context"}
LEAKY_PAYLOAD_KEYS = {
    "_builder",
    "_internal",
    "_frozen",
    "expected_verdict",
    "hidden_ground_truth",
    "gold_answer",
    "scoring_targets",
    "verdict",
    "allow_reason",
    "is_clean",
    "is_approved",
    "is_cleared",
    "cleared",
    "approved",
    "pre_approved",
}
ESCALATE_SOURCE_MARKERS = (
    "portal_change_record",
    "change_request",
    "invoice",
    "submitted_contact",
    "submitted_billing_contact",
    "post_change",
    "newly supplied",
    "ap_queue_note",
    "vendor_contact_record",
)
ALLOW_CALLBACK_SOURCE_NOISE = (
    "portal_change_record",
    "submitted_contact_phone",
    "invoice supplied phone",
    "newly supplied contact record",
    "post-change contact source",
    "change_request_contact_update",
    "remittance_contact_phone",
    "regional_billing_phone",
)
NEON_ESCALATE_LABELS = (
    "noncompliant_callback_source",
    "source_defect_note",
    "single_material_blocker_note",
    "noncompliant",
    "material blocker",
    "violation",
    "unsafe",
    "do not pay",
    "bad source",
)
CALLBACK_DELTA_FIELDS = {
    "number_source",
    "dialed_number",
    "provenance_basis",
    "source_exclusion_note",
    "control_closure_note",
    "downstream_controls_boundary_note",
    "callback_phone_lineage",
    "pre_change_vendor_master_source",
    "unused_pre_change_vendor_master_source",
    "source_defect_note",
    "single_material_blocker_note",
}
INDEPENDENT_BLOCKER_MARKERS = (
    "missing po",
    "po missing",
    "missing purchase order",
    "missing approval",
    "approval missing",
    "sanctions",
    "expired delegation",
    "domain spoof",
    "spoofed domain",
    "phishing",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _drafts() -> list[dict[str, Any]]:
    return [_load(path) for path in sorted(Path(".").glob(DRAFT_GLOB))]


def _by_family() -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for draft in _drafts():
        grouped[draft["_builder"]["family_id"]].append(draft)
    return grouped


def _internal_docs(packet: dict[str, Any]) -> list[dict[str, Any]]:
    return packet["payload"]["context"]["internal_documents"]


def _callback(packet: dict[str, Any]) -> dict[str, Any]:
    callbacks = [doc for doc in _internal_docs(packet) if doc.get("type") == "ap_callback_record"]
    assert len(callbacks) == 1
    return callbacks[0]


def _snapshot(packet: dict[str, Any]) -> dict[str, Any]:
    snapshots = [doc for doc in _internal_docs(packet) if doc.get("type") == "vendor_master_snapshot"]
    assert len(snapshots) == 1
    return snapshots[0]


def _doc(packet: dict[str, Any], doc_type: str) -> dict[str, Any]:
    docs = [doc for doc in _internal_docs(packet) if doc.get("type") == doc_type]
    assert len(docs) == 1
    return docs[0]


def _payload_text(packet: dict[str, Any]) -> str:
    return json.dumps(packet["payload"], sort_keys=True).lower()


def _walk_keys(obj: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            keys.append(key)
            keys.extend(_walk_keys(value))
    elif isinstance(obj, list):
        for value in obj:
            keys.extend(_walk_keys(value))
    return keys


def _normalized_payload_for_pair_compare(packet: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(packet["payload"])
    for doc in payload["context"]["internal_documents"]:
        if doc.get("type") == "ap_callback_record":
            for field in CALLBACK_DELTA_FIELDS:
                doc[field] = "<CALLBACK_PROVENANCE_DELTA>"
    return payload


def test_batch001_draft_file_count_and_verdict_balance() -> None:
    drafts = _drafts()
    verdict_counts = Counter(draft["expected_verdict"] for draft in drafts)

    assert len(drafts) == 16
    assert verdict_counts == {"ALLOW": 8, "ESCALATE": 8}


def test_batch001_expected_families_are_present() -> None:
    grouped = _by_family()

    assert set(grouped) == EXPECTED_FAMILIES
    assert all(len(siblings) == 2 for siblings in grouped.values())


def test_payload_visibility_contract_has_no_model_visible_metadata() -> None:
    for draft in _drafts():
        payload = draft["payload"]
        assert set(payload) == PAYLOAD_KEYS
        assert payload_visibility_errors(draft) == []
        assert not (set(_walk_keys(payload)) & LEAKY_PAYLOAD_KEYS)


def test_each_pair_preserves_action_boundary_and_aligned_artifact_structure() -> None:
    for family_id, siblings in _by_family().items():
        allow = next(packet for packet in siblings if packet["expected_verdict"] == "ALLOW")
        escalate = next(packet for packet in siblings if packet["expected_verdict"] == "ESCALATE")

        assert allow["_builder"]["action_boundary"] == escalate["_builder"]["action_boundary"], family_id
        assert allow["payload"]["action"] == escalate["payload"]["action"], family_id
        assert [doc["type"] for doc in _internal_docs(allow)] == [doc["type"] for doc in _internal_docs(escalate)]
        assert [doc["doc_id"] for doc in _internal_docs(allow)] == [doc["doc_id"] for doc in _internal_docs(escalate)]
        assert _normalized_payload_for_pair_compare(allow) == _normalized_payload_for_pair_compare(escalate), family_id


def test_each_pair_has_one_callback_provenance_delta() -> None:
    for family_id, siblings in _by_family().items():
        allow = next(packet for packet in siblings if packet["expected_verdict"] == "ALLOW")
        escalate = next(packet for packet in siblings if packet["expected_verdict"] == "ESCALATE")
        allow_callback = _callback(allow)
        escalate_callback = _callback(escalate)

        assert allow["_builder"]["material_delta"] == "callback source provenance only"
        assert escalate["_builder"]["material_delta"] == "callback source provenance only"
        assert allow_callback["number_source"] != escalate_callback["number_source"], family_id
        assert allow_callback["dialed_number"] != escalate_callback["dialed_number"], family_id


def test_allow_uses_prechange_vendor_master_callback_source() -> None:
    for draft in _drafts():
        if draft["expected_verdict"] != "ALLOW":
            continue
        callback = _callback(draft)
        snapshot = _snapshot(draft)

        source = callback["number_source"].lower()
        assert "vendor_master" in source
        assert "snapshot" in source or "pre-change" in source
        assert callback["dialed_number"] == snapshot["phone_on_file"]
        assert callback["provenance_basis"] == "pre_change_vendor_master_record"
        assert callback["callback_phone_lineage"]["selected_record_type"] == "vendor_master_snapshot"
        assert callback["callback_phone_lineage"]["selected_record_id"] == snapshot["doc_id"]
        assert callback["callback_phone_lineage"]["contact_phone_source"] == "phone_on_file"
        assert callback["pre_change_vendor_master_source"]["snapshot_id"] == snapshot["doc_id"]
        assert callback["pre_change_vendor_master_source"]["selected_for_callback"] is True
        assert "no unresolved discrepancy remains" in callback["control_closure_note"].lower()
        assert "release_checklist_complete=true" in callback["control_closure_note"]
        assert "pre-change vendor-master record" in callback["downstream_controls_boundary_note"].lower()


def test_allow_callback_record_is_not_overloaded_with_forbidden_source_vocabulary() -> None:
    for draft in _drafts():
        if draft["expected_verdict"] != "ALLOW":
            continue
        callback_text = json.dumps(_callback(draft), sort_keys=True).lower()

        for marker in ALLOW_CALLBACK_SOURCE_NOISE:
            assert marker not in callback_text


def test_escalate_uses_submitted_or_new_callback_source_without_neon_labels() -> None:
    for draft in _drafts():
        if draft["expected_verdict"] != "ESCALATE":
            continue
        callback = _callback(draft)
        source = callback["number_source"].lower()
        snapshot = _snapshot(draft)
        callback_text = json.dumps(callback, sort_keys=True).lower()
        callback_keys = set(_walk_keys(callback))

        assert "vendor_master_snapshot" not in source
        assert "pre-change" not in source
        assert any(marker in source for marker in ESCALATE_SOURCE_MARKERS)
        assert callback["provenance_basis"] == "selected_callback_source_record"
        assert callback["callback_phone_lineage"]["selected_record_type"] != "vendor_master_snapshot"
        assert callback["callback_phone_lineage"]["selected_phone"] == callback["dialed_number"]
        assert callback["pre_change_vendor_master_source"]["snapshot_id"] == snapshot["doc_id"]
        assert callback["pre_change_vendor_master_source"]["phone_on_file"] == snapshot["phone_on_file"]
        assert callback["pre_change_vendor_master_source"]["comparison_to_callback_log"] == "different_phone_than_selected_record"
        assert "do not substitute for pre-change callback-source lineage" in callback["downstream_controls_boundary_note"]
        assert not (callback_keys & {"source_defect_note", "single_material_blocker_note", "unused_pre_change_vendor_master_source"})
        for label in NEON_ESCALATE_LABELS:
            assert label not in callback_text


def test_repaired_control_closure_is_visible_without_second_blockers() -> None:
    for draft in _drafts():
        signoff = _doc(draft, "ap_change_signoff_record")
        scrutiny = _doc(draft, "elevated_scrutiny_record")
        xref = _doc(draft, "invoice_cross_reference_record")
        hold = _doc(draft, "temporary_payment_hold_record")

        assert "two-person ap signoff complete" in signoff["control_completion_note"].lower()
        assert "scrutiny_completed=true" in scrutiny["control_completion_note"]
        assert "review_closed=" in scrutiny["control_completion_note"]
        assert "hold_released=true" in hold["release_decision_note"]
        assert "no active hold remained" in hold["release_decision_note"].lower()
        assert "xref_complete=true" in xref["control_completion_note"]
        assert "no unresolved discrepancy" in xref["control_completion_note"].lower()


def test_too_easy_escalate_variants_were_strengthened_without_second_blockers() -> None:
    strengthened = {
        "BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL",
        "BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL",
    }

    for draft in _drafts():
        if draft["scenario_id"] not in strengthened:
            continue
        source = _callback(draft)["number_source"].lower()

        assert "vendor_contact_record" in source
        assert "created_from=portal-chg" in source
        assert "contact_phone_source=change_request_contact_update" in source
        assert "newly supplied" not in source
        assert "invoice:" not in source
        assert "ap_queue_note" not in source


def test_no_second_independent_blocker_is_visible_in_payload() -> None:
    for draft in _drafts():
        text = _payload_text(draft)
        action = draft["payload"]["action"]
        invoice = next(doc for doc in _internal_docs(draft) if doc.get("type") == "invoice")
        signoff = next(doc for doc in _internal_docs(draft) if doc.get("type") == "ap_change_signoff_record")
        hold = next(doc for doc in _internal_docs(draft) if doc.get("type") == "temporary_payment_hold_record")

        assert action["payment_hold"] is False
        assert invoice["purchase_order_ref"]
        assert len(signoff["approver_signatures"]) == 2
        assert hold["hold_released_at"]
        for marker in INDEPENDENT_BLOCKER_MARKERS:
            assert marker not in text
