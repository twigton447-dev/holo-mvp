from __future__ import annotations

import copy

from fastapi.testclient import TestClient

from llm_adapters import BEC_CATEGORIES
from tests.conftest import MINIMAL_PAYLOAD, VALID_HEADERS


def _raw_holoverify_result(body: dict, evaluation_id: str = "holo_hv_smoke") -> dict:
    coverage_matrix = {
        category: {"addressed": True, "max_severity": "LOW"}
        for category in BEC_CATEGORIES
    }
    turn = {
        "provider": "offline",
        "model_id": "offline-smoke",
        "role": "Initial Assessment",
        "turn_number": 1,
        "verdict": "ALLOW",
        "reasoning": "Offline governed decision smoke.",
        "severity_flags": {category: "LOW" for category in BEC_CATEGORIES},
        "findings": [],
        "raw_response": "{}",
        "input_tokens": 10,
        "output_tokens": 5,
        "temperature": 0.2,
        "delta": 1,
        "coverage_delta": 1,
        "flip_delta": 0,
    }
    return {
        "evaluation_id": evaluation_id,
        "scenario": "invoice_payment",
        "tier": "fast",
        "decision": "ALLOW",
        "decision_reason": "Offline HoloVerify smoke decision.",
        "exit_reason": "clean_exit",
        "routing_audit": None,
        "turns_completed": 1,
        "converged": True,
        "oscillation": False,
        "decay": False,
        "partial": False,
        "deltas": [1],
        "turn_history": [turn],
        "artifacts": {
            "action_v1": {
                "artifact_id": "action_v1",
                "type": "action_payload",
                "status": "PINNED",
                "version": 1,
                "content": copy.deepcopy(body["action"]),
            },
            "context_v1": {
                "artifact_id": "context_v1",
                "type": "context_bundle",
                "status": "PINNED",
                "version": 1,
                "content": copy.deepcopy(body["context"]),
            },
        },
        "governor_briefs": [
            {
                "for_turn": 2,
                "brief": "Offline HoloGov-V smoke brief.",
                "convergence_level": "EARLY",
            }
        ],
        "verified_facts": {},
        "coverage_matrix": coverage_matrix,
        "elapsed_ms": 1,
        "run_health": {},
        "total_tokens": {
            "driver": {"input": 10, "output": 5},
            "governor": {"input": 0, "output": 0},
            "total": {"input": 10, "output": 5},
        },
    }


class _OfflineGovernor:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.fail = False

    def evaluate(self, body: dict) -> dict:
        self.calls.append(copy.deepcopy(body))
        if self.fail:
            raise RuntimeError("sentinel HoloGov-V enforcement poison")
        return _raw_holoverify_result(body)


class _OfflineSigner:
    def __init__(self) -> None:
        self.veto = False
        self.calls: list[dict] = []

    def issue_receipt(self, *, decision: str, evaluation_id: str, evidence_hash: str) -> dict:
        self.calls.append(
            {
                "decision": decision,
                "evaluation_id": evaluation_id,
                "evidence_hash": evidence_hash,
            }
        )
        if self.veto:
            from hologov_v_signer import HoloGovVSignerVetoError

            raise HoloGovVSignerVetoError("sentinel signer veto")
        return {
            "receipt_id": "hgovv_smoke_receipt",
            "schema": "hologov_v_receipt_v1",
            "receipt_version": "1",
            "lane": "HoloGov-V",
            "status": "accepted",
            "enforcement_point": "/v1/evaluate_action",
            "decision": decision,
            "evaluation_id": evaluation_id,
            "evidence_hash": evidence_hash,
            "signer_id": "offline-smoke-signer",
            "key_id": "offline-smoke-key",
            "issued_at": "2026-06-30T00:00:00Z",
            "nonce": "offline-smoke-nonce",
            "receipt_signature": "offline-smoke-signature",
        }


def _request_with_forged_fields() -> dict:
    body = copy.deepcopy(MINIMAL_PAYLOAD)
    body.update(
        {
            "audit_id": "caller_supplied_audit",
            "evaluation_id": "caller_supplied_evaluation",
            "provenance": {"source": "caller", "evidence_hash": "caller_hash"},
            "evidence_hash": "caller_hash",
        }
    )
    return body


def _assert_no_partner_valid_decision(data: dict) -> None:
    assert "audit_id" not in data
    assert "decision" not in data
    assert "hologov_v_enforcement_receipt" not in data
    assert "provenance" not in data
    assert "audit" not in data


def test_hv_end_to_end_governed_decision_smoke(monkeypatch):
    import main

    body = _request_with_forged_fields()
    governor = _OfflineGovernor()
    signer = _OfflineSigner()

    monkeypatch.setattr(main, "ContextGovernor", lambda: governor)
    monkeypatch.setattr(main, "HoloChatEngine", lambda: object())
    monkeypatch.setattr(main, "_db", None)
    monkeypatch.setattr(main, "_hologov_v_signer_client", signer)
    main._rate_limiter._requests.clear()

    with TestClient(main.app, raise_server_exceptions=False) as client:
        raw_shortcut = main._build_response(_raw_holoverify_result(body))
        assert "decision" in raw_shortcut
        assert "hologov_v_enforcement_receipt" not in raw_shortcut
        assert "provenance" not in raw_shortcut
        assert "audit" not in raw_shortcut

        response = client.post("/v1/evaluate_action", json=body, headers=VALID_HEADERS)
        assert response.status_code == 200
        data = response.json()

        assert governor.calls and governor.calls[0]["action"] == body["action"]
        assert signer.calls
        expected_hash = main._evidence_packet_hash(body)
        assert signer.calls[0]["evidence_hash"] == expected_hash

        assert data["decision"] == "ALLOW"
        assert data["audit_id"] != body["audit_id"]
        assert data["audit_id"] != body["evaluation_id"]
        assert data["hologov_v_enforcement_receipt"]["lane"] == "HoloGov-V"
        assert data["hologov_v_enforcement_receipt"]["evidence_hash"] == expected_hash
        assert data["provenance"]["source"] == "holo_internal"
        assert data["provenance"] != body["provenance"]
        assert data["provenance"]["evidence_hash"] == expected_hash
        assert data["audit"]["evidence_hash"] == expected_hash
        assert data["audit"]["canonical_packet"] == main._canonical_action_context_packet(body)

        signer.veto = True
        veto_response = client.post("/v1/evaluate_action", json=body, headers=VALID_HEADERS)
        assert veto_response.status_code == 503
        _assert_no_partner_valid_decision(veto_response.json())

        signer.veto = False
        governor.fail = True
        poisoned_response = client.post("/v1/evaluate_action", json=body, headers=VALID_HEADERS)
        assert poisoned_response.status_code == 500
        _assert_no_partner_valid_decision(poisoned_response.json())
