import json
from pathlib import Path

import pytest

import holo_builder.freeze as freeze_mod
from holo_builder.freeze import freeze_packet
from holo_builder.freeze_manifest import build_freeze_manifest, compute_payload_hash


def _nested_builder_packet() -> dict:
    return {
        "scenario_id": "TEST-HBB-001",
        "domain": "AP / BEC",
        "expected_verdict": "ALLOW",
        "payload_revision": 1,
        "_internal": {
            "expected_reason": "Builder hypothesis only.",
            "suspicious_surface": "Vendor master payment change.",
            "clearing_evidence": ["portal", "callback", "vendor audit"],
        },
        "_builder": {
            "source_spec": "test-spec.json",
            "spec_target_verdict": "ALLOW",
            "spec_packet_format": "payment_email",
        },
        "payload": {
            "action": {
                "type": "invoice_payment",
                "vendor": "Sable Data Services",
                "amount": 84250,
                "currency": "USD",
                "payment_method": "ACH",
                "payment_hold": False,
            },
            "context": {
                "email_thread": [
                    {
                        "from": "billing@sable.example",
                        "to": "ap@example.com",
                        "date": "2024-04-12",
                        "subject": "Invoice SDS-1044",
                        "body": "Please process invoice SDS-1044.",
                    }
                ],
                "internal_documents": [
                    {"type": "portal_submission", "content": {"ref": "PORTAL-1"}},
                    {"type": "callback_record", "content": {"ref": "CALL-1"}},
                    {"type": "vendor_master_audit", "content": {"ref": "VMA-1"}},
                ],
                "policy_documents": [
                    {"type": "vendor_master_policy", "content": {"section": "4.2"}}
                ],
            },
        },
    }


def _approved_manifest(packet: dict, packet_path: Path) -> dict:
    manifest = build_freeze_manifest(packet, packet_path)
    manifest["taylor_approved_for_freeze"] = True
    manifest["approved_by"] = "Taylor"
    return manifest


def _redirect_freeze_outputs(monkeypatch, tmp_path):
    monkeypatch.setattr(freeze_mod, "FROZEN_DIR", tmp_path / "frozen")
    monkeypatch.setattr(freeze_mod, "LEDGER_PATH", tmp_path / "ledger.jsonl")


def test_valid_manifest_freezes_nested_builder_packet(tmp_path, monkeypatch):
    packet = _nested_builder_packet()
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, indent=2))
    manifest = _approved_manifest(packet, packet_path)
    _redirect_freeze_outputs(monkeypatch, tmp_path)

    frozen_path, pkg_hash = freeze_packet(packet, manifest, packet_path)

    assert pkg_hash == compute_payload_hash(packet)
    assert frozen_path.exists()
    frozen_packet = json.loads(frozen_path.read_text())
    assert frozen_packet["_frozen"]["freeze_gate"] == "build_freeze_manifest"
    assert frozen_packet["_frozen"]["builder_hypothesis_verdict"] == "ALLOW"
    assert frozen_packet["_frozen"]["static_lint_result"] == "PASS"
    assert "qa_classification" not in frozen_packet["_frozen"]


def test_mismatched_payload_hash_blocks_freeze(tmp_path, monkeypatch):
    packet = _nested_builder_packet()
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, indent=2))
    manifest = _approved_manifest(packet, packet_path)
    manifest["payload_hash"] = "0" * 64
    _redirect_freeze_outputs(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="payload_hash"):
        freeze_packet(packet, manifest, packet_path)


def test_missing_taylor_approval_blocks_freeze(tmp_path, monkeypatch):
    packet = _nested_builder_packet()
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, indent=2))
    manifest = build_freeze_manifest(packet, packet_path)
    _redirect_freeze_outputs(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="taylor_approved_for_freeze"):
        freeze_packet(packet, manifest, packet_path)


def test_expected_verdict_inside_model_visible_payload_blocks_freeze(tmp_path, monkeypatch):
    packet = _nested_builder_packet()
    packet["payload"]["context"]["expected_verdict"] = "ALLOW"
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet, indent=2))
    manifest = _approved_manifest(packet, packet_path)
    _redirect_freeze_outputs(monkeypatch, tmp_path)

    assert manifest["payload_visibility_result"] == "FAIL"
    with pytest.raises(ValueError, match="payload_visibility"):
        freeze_packet(packet, manifest, packet_path)
