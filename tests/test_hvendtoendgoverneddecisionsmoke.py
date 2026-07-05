"""
hvendtoendgoverneddecisionsmoke

Architectural answer before implementation:
With an isolated signer, HoloGov-V receipt issuance is no longer a
formatting-time API helper inside main.py. Partner-valid output depends on a
fresh Ed25519 receipt issued by a separate signer process for the exact
action/context evidence hash. The API process may verify that receipt with a
public trust root, but it must not possess the private signing key.

The contract under test is still artifact-bound: raw ContextGovernor.evaluate
can compute a non-partner-valid decision object before enforcement, but no
reachable response path may produce a partner-valid artifact when the signer
vetoes, dies, or is unreachable.
"""

from __future__ import annotations

import base64
import contextlib
import copy
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from hologov_v_signer import verify_hologov_v_receipt
from llm_adapters import BEC_CATEGORIES
from tests.conftest import MINIMAL_PAYLOAD, VALID_HEADERS

ROOT = Path(__file__).resolve().parents[1]


def _canonical_packet(body: dict) -> dict:
    return {
        "action": body.get("action", {}),
        "context": body.get("context", {}),
    }


def _canonical_hash(body: dict) -> str:
    encoded = json.dumps(
        _canonical_packet(body),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _raw_governor_result(body: dict, evaluation_id: str = "holo_smoke_internal") -> dict:
    severity_flags = {cat: "LOW" for cat in BEC_CATEGORIES}
    coverage_matrix = {
        cat: {"addressed": True, "max_severity": "LOW"}
        for cat in BEC_CATEGORIES
    }
    turn = {
        "provider": "offline",
        "model_id": "offline-smoke",
        "role": "Initial Assessment",
        "turn_number": 1,
        "verdict": "ALLOW",
        "reasoning": "Offline smoke result.",
        "severity_flags": severity_flags,
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
        "decision_reason": "Offline governed path produced an ALLOW decision.",
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
                "brief": "Offline smoke governor brief.",
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


class OfflineGovernor:
    def __init__(self):
        self.calls: list[dict] = []

    def evaluate(self, body: dict) -> dict:
        self.calls.append(copy.deepcopy(body))
        return _raw_governor_result(body)


@pytest.fixture
def signer_keypair():
    private_key = Ed25519PrivateKey.generate()
    private_b64 = base64.b64encode(
        private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
    ).decode("ascii")
    public_b64 = base64.b64encode(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    ).decode("ascii")
    return private_b64, public_b64


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_signer(url: str, proc: subprocess.Popen, timeout_s: float = 5.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        if proc.poll() is not None:
            stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
            raise AssertionError(f"signer exited early with {proc.returncode}: {stderr}")
        try:
            with urllib.request.urlopen(f"{url}/health", timeout=0.2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, OSError):
            time.sleep(0.05)
    raise AssertionError("signer did not become healthy")


@contextlib.contextmanager
def _signer_process(private_key_b64: str, *, mode: str = "accept"):
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["HOLOGOV_V_SIGNER_PRIVATE_KEY_B64"] = private_key_b64
    env["HOLOGOV_V_SIGNER_PORT"] = str(port)
    env["HOLOGOV_V_SIGNER_MODE"] = mode
    proc = subprocess.Popen(
        [sys.executable, "-m", "hologov_v_signer_service"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        _wait_for_signer(url, proc)
        yield url, proc
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)


@contextlib.contextmanager
def _action_client(monkeypatch, signer_url: str, public_key_b64: str, governor=None):
    import main

    governor = governor or OfflineGovernor()
    monkeypatch.setattr(main, "ContextGovernor", lambda: governor)
    monkeypatch.setattr(main, "HoloChatEngine", lambda: object())
    monkeypatch.setattr(main, "_db", None)
    monkeypatch.setattr(main, "_hologov_v_signer_client", None)
    monkeypatch.setenv("HOLOGOV_V_SIGNER_URL", signer_url)
    monkeypatch.setenv("HOLOGOV_V_SIGNER_PUBLIC_KEY_B64", public_key_b64)
    monkeypatch.setenv("HOLOGOV_V_SIGNER_TIMEOUT_MS", "300")
    monkeypatch.delenv("HOLOGOV_V_SIGNER_PRIVATE_KEY_B64", raising=False)
    main._rate_limiter._requests.clear()

    with TestClient(main.app, raise_server_exceptions=False) as client:
        yield client, governor, main


def _partner_request_with_forged_fields() -> dict:
    body = copy.deepcopy(MINIMAL_PAYLOAD)
    body.update({
        "audit_id": "caller_supplied_audit",
        "evaluation_id": "caller_supplied_evaluation",
        "provenance": {"source": "caller", "provenance_id": "forged"},
        "evidence_hash": "caller_supplied_hash",
    })
    return body


def _walk_dicts(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def _has_verifiable_receipt(artifact: dict, public_key_b64: str) -> bool:
    return any(
        verify_hologov_v_receipt(candidate, public_key_b64)
        for candidate in _walk_dicts(artifact)
    )


def _has_positive_finality_marker(artifact: dict) -> bool:
    finality_keys = {"partner_valid", "verified", "governed", "authorized", "approved"}
    finality_values = {"true", "yes", "accepted", "approved", "authorized", "governed", "verified"}
    for candidate in _walk_dicts(artifact):
        for key, value in candidate.items():
            if key not in finality_keys:
                continue
            if value is True:
                return True
            if isinstance(value, str) and value.strip().lower() in finality_values:
                return True
    return False


def _is_partner_valid(artifact: dict, body: dict, public_key_b64: str) -> bool:
    if artifact.get("decision") not in {"ALLOW", "ESCALATE"}:
        return False

    receipt = artifact.get("hologov_v_enforcement_receipt")
    provenance = artifact.get("provenance")
    audit = artifact.get("audit")
    if not isinstance(receipt, dict) or not isinstance(provenance, dict) or not isinstance(audit, dict):
        return False

    expected_hash = _canonical_hash(body)
    if receipt.get("enforcement_point") != "/v1/evaluate_action":
        return False
    if receipt.get("evidence_hash") != expected_hash:
        return False
    if not verify_hologov_v_receipt(receipt, public_key_b64):
        return False

    if provenance.get("source") != "holo_internal":
        return False
    if provenance.get("evidence_hash") != expected_hash:
        return False
    if provenance.get("receipt_id") != receipt.get("receipt_id"):
        return False
    if provenance.get("receipt_signature") != receipt.get("receipt_signature"):
        return False

    if audit.get("evidence_hash") != expected_hash:
        return False
    if audit.get("canonical_packet") != _canonical_packet(body):
        return False
    if not audit.get("decision_basis"):
        return False
    if not audit.get("turn_history"):
        return False
    if not audit.get("coverage_matrix"):
        return False
    if not audit.get("governor_briefs"):
        return False
    artifacts = audit.get("artifacts") or {}
    action_v1 = artifacts.get("action_v1") or {}
    context_v1 = artifacts.get("context_v1") or {}
    if action_v1.get("status") != "PINNED" or context_v1.get("status") != "PINNED":
        return False
    if action_v1.get("content") != body["action"]:
        return False
    if context_v1.get("content") != body["context"]:
        return False

    return True


def _assert_non_partner_valid(artifact: dict, body: dict, public_key_b64: str) -> None:
    assert not _is_partner_valid(artifact, body, public_key_b64)
    assert not _has_verifiable_receipt(artifact, public_key_b64)
    assert not _has_positive_finality_marker(artifact)


def _shortcut_artifacts(client, main, body: dict) -> dict[str, dict]:
    raw_result = _raw_governor_result(body)

    preloaded_result = copy.deepcopy(raw_result)
    preloaded_result.update({
        "hologov_v_enforcement_receipt": {
            "receipt_id": "hgovv_preloaded",
            "schema": "hologov_v_receipt_v1",
            "receipt_version": "1",
            "lane": "HoloGov-V",
            "status": "accepted",
            "enforcement_point": "/v1/evaluate_action",
            "decision": "ALLOW",
            "evaluation_id": raw_result["evaluation_id"],
            "evidence_hash": _canonical_hash(body),
            "signer_id": "caller",
            "key_id": "caller",
            "issued_at": "2026-06-26T00:00:00Z",
            "nonce": "caller",
            "receipt_signature": "caller-forged-signature",
        },
        "provenance": {"source": "holo_internal", "evidence_hash": _canonical_hash(body)},
        "partner_audit": {"evidence_hash": _canonical_hash(body)},
    })

    compat_resp = client.post(
        "/v1/evaluate",
        json={
            "client_id": "partner-smoke",
            "domain": "invoice_payment",
            "action_payload": {
                **body["action"],
                "email_chain": body["context"]["email_chain"],
            },
        },
        headers={"Authorization": f"Bearer {VALID_HEADERS['x-api-key']}"},
    )
    legacy_resp = client.post("/evaluate", json=body, headers=VALID_HEADERS)

    return {
        "raw_governor_result": raw_result,
        "build_response": main._build_response(copy.deepcopy(raw_result)),
        "build_response_preloaded_partner_fields": main._build_response(preloaded_result),
        "persisted_project_brain_shape": {
            "evaluation_id": raw_result["evaluation_id"],
            "decision": raw_result["decision"],
            "decision_reason": raw_result["decision_reason"],
            "coverage_matrix": raw_result["coverage_matrix"],
        },
        "cache_replay_shape": {**copy.deepcopy(raw_result), "source": "cache"},
        "fallback_wrapper": {
            "evaluation_id": raw_result["evaluation_id"],
            "verdict": raw_result["decision"],
            "confidence": "LOW",
            "primary_signal": raw_result["decision_reason"],
        },
        "legacy_v1_evaluate": compat_resp.json(),
        "legacy_evaluate": legacy_resp.json(),
        "hand_built_bad_signature": {
            "audit_id": raw_result["evaluation_id"],
            "decision": "ALLOW",
            "decision_reason": raw_result["decision_reason"],
            "hologov_v_enforcement_receipt": preloaded_result["hologov_v_enforcement_receipt"],
            "provenance": {
                "source": "holo_internal",
                "provenance_id": "caller-forged",
                "evaluation_id": raw_result["evaluation_id"],
                "evidence_hash": _canonical_hash(body),
                "receipt_id": "hgovv_preloaded",
                "receipt_signature": "caller-forged-signature",
            },
            "audit": {
                "evidence_hash": _canonical_hash(body),
                "canonical_packet": _canonical_packet(body),
                "decision_basis": raw_result["decision_reason"],
                "turn_history": raw_result["turn_history"],
                "artifacts": {
                    "action_v1": raw_result["artifacts"]["action_v1"],
                    "context_v1": raw_result["artifacts"]["context_v1"],
                },
                "coverage_matrix": raw_result["coverage_matrix"],
                "governor_briefs": raw_result["governor_briefs"],
            },
        },
    }


def _assert_all_shortcuts_rejected(client, main, body: dict, public_key_b64: str) -> None:
    assert not hasattr(main, "_enforce_hologov_v_receipt")
    assert not hasattr(main, "_attach_partner_boundary_audit")
    assert not hasattr(main, "_hologov_v_receipt_signature")
    for artifact in _shortcut_artifacts(client, main, body).values():
        _assert_non_partner_valid(artifact, body, public_key_b64)


def test_normal_governed_path_returns_partner_valid_internal_artifact(monkeypatch, signer_keypair):
    private_key_b64, public_key_b64 = signer_keypair
    body = _partner_request_with_forged_fields()

    with _signer_process(private_key_b64, mode="accept") as (signer_url, _proc):
        with _action_client(monkeypatch, signer_url, public_key_b64) as (client, governor, main):
            assert "HOLOGOV_V_SIGNER_PRIVATE_KEY_B64" not in os.environ

            resp = client.post("/v1/evaluate_action", json=body, headers=VALID_HEADERS)

            assert resp.status_code == 200
            data = resp.json()
            assert _is_partner_valid(data, body, public_key_b64)
            assert governor.calls and governor.calls[0]["action"] == body["action"]

            assert data["audit_id"] != body["audit_id"]
            assert data["audit_id"] != body["evaluation_id"]
            assert data["provenance"] != body["provenance"]
            assert data["provenance"]["source"] == "holo_internal"
            assert data["provenance"]["evidence_hash"] != body["evidence_hash"]
            assert data["audit"]["evidence_hash"] == _canonical_hash(body)
            assert data["audit"]["canonical_packet"] == _canonical_packet(body)
            _assert_all_shortcuts_rejected(client, main, body, public_key_b64)


def test_signer_veto_fails_closed_across_all_paths(monkeypatch, signer_keypair):
    private_key_b64, public_key_b64 = signer_keypair
    body = _partner_request_with_forged_fields()

    with _signer_process(private_key_b64, mode="veto") as (signer_url, _proc):
        with _action_client(monkeypatch, signer_url, public_key_b64) as (client, _governor, main):
            resp = client.post("/v1/evaluate_action", json=body, headers=VALID_HEADERS)

            assert resp.status_code == 503
            data = resp.json()
            assert "decision" not in data
            assert "audit" not in data
            _assert_non_partner_valid(data, body, public_key_b64)
            _assert_all_shortcuts_rejected(client, main, body, public_key_b64)


def test_signer_process_death_fails_closed_across_all_paths(monkeypatch, signer_keypair):
    private_key_b64, public_key_b64 = signer_keypair
    body = _partner_request_with_forged_fields()

    with _signer_process(private_key_b64, mode="accept") as (signer_url, proc):
        proc.kill()
        proc.wait(timeout=2)
        with _action_client(monkeypatch, signer_url, public_key_b64) as (client, _governor, main):
            resp = client.post("/v1/evaluate_action", json=body, headers=VALID_HEADERS)

            assert resp.status_code == 503
            data = resp.json()
            assert "decision" not in data
            assert "audit" not in data
            _assert_non_partner_valid(data, body, public_key_b64)
            _assert_all_shortcuts_rejected(client, main, body, public_key_b64)


def test_signer_unreachable_fails_closed_across_all_paths(monkeypatch, signer_keypair):
    _private_key_b64, public_key_b64 = signer_keypair
    body = _partner_request_with_forged_fields()
    signer_url = f"http://127.0.0.1:{_free_port()}"

    with _action_client(monkeypatch, signer_url, public_key_b64) as (client, _governor, main):
        resp = client.post("/v1/evaluate_action", json=body, headers=VALID_HEADERS)

        assert resp.status_code == 503
        data = resp.json()
        assert "decision" not in data
        assert "audit" not in data
        _assert_non_partner_valid(data, body, public_key_b64)
        _assert_all_shortcuts_rejected(client, main, body, public_key_b64)
