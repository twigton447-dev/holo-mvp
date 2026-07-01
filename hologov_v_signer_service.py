"""
Process-isolated HoloGov-V signer service.

Run with:
  HOLOGOV_V_SIGNER_PRIVATE_KEY_B64=<raw Ed25519 private key, base64>
  python -m hologov_v_signer_service

The API process talks to this service over HTTP and verifies receipts with the
corresponding public key. The private signing key must not be present in the API
process environment.
"""

from __future__ import annotations

import base64
import json
import os
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from hologov_v_signer import (
    HOLOGOV_V_RECEIPT_SCHEMA,
    HOLOGOV_V_RECEIPT_VERSION,
    canonical_json,
    receipt_signed_payload,
)


def _load_private_key() -> Ed25519PrivateKey:
    raw = os.environ.get("HOLOGOV_V_SIGNER_PRIVATE_KEY_B64", "").strip()
    if not raw:
        raise RuntimeError("HOLOGOV_V_SIGNER_PRIVATE_KEY_B64 is required.")
    return Ed25519PrivateKey.from_private_bytes(base64.b64decode(raw))


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _issue_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    if os.environ.get("HOLOGOV_V_SIGNER_MODE", "accept") == "veto":
        raise PermissionError("signer veto")

    decision = payload.get("decision")
    if decision not in {"ALLOW", "ESCALATE"}:
        raise ValueError("decision must be ALLOW or ESCALATE")
    evidence_hash = payload.get("evidence_hash")
    if not isinstance(evidence_hash, str) or len(evidence_hash) != 64:
        raise ValueError("evidence_hash must be a sha256 hex digest")
    evaluation_id = payload.get("evaluation_id")
    if not isinstance(evaluation_id, str) or not evaluation_id:
        raise ValueError("evaluation_id is required")

    receipt = {
        "receipt_id": f"hgovv_{uuid.uuid4().hex[:16]}",
        "schema": HOLOGOV_V_RECEIPT_SCHEMA,
        "receipt_version": HOLOGOV_V_RECEIPT_VERSION,
        "lane": "HoloGov-V",
        "status": "accepted",
        "enforcement_point": "/v1/evaluate_action",
        "decision": decision,
        "evaluation_id": evaluation_id,
        "evidence_hash": evidence_hash,
        "signer_id": os.environ.get("HOLOGOV_V_SIGNER_ID", "hologov-v-isolated-signer"),
        "key_id": os.environ.get("HOLOGOV_V_SIGNER_KEY_ID", "hologov-v-test-key"),
        "issued_at": _utc_now(),
        "nonce": uuid.uuid4().hex,
    }
    private_key = _load_private_key()
    signature = private_key.sign(
        canonical_json(receipt_signed_payload(receipt)).encode("utf-8")
    )
    receipt["receipt_signature"] = base64.b64encode(signature).decode("ascii")
    return receipt


class _SignerHandler(BaseHTTPRequestHandler):
    server_version = "HoloGovVSigner/1"

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = canonical_json(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json(404, {"error": "not_found"})
            return
        self._send_json(200, {
            "status": "ok",
            "signer_id": os.environ.get("HOLOGOV_V_SIGNER_ID", "hologov-v-isolated-signer"),
            "key_id": os.environ.get("HOLOGOV_V_SIGNER_KEY_ID", "hologov-v-test-key"),
        })

    def do_POST(self) -> None:
        if os.environ.get("HOLOGOV_V_SIGNER_MODE") == "crash":
            os._exit(70)
        if self.path != "/v1/hologov-v/receipts":
            self._send_json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            receipt = _issue_receipt(payload)
        except PermissionError:
            self._send_json(403, {"status": "veto", "error": "signer_veto"})
            return
        except Exception as e:
            self._send_json(422, {"status": "rejected", "error": type(e).__name__})
            return
        self._send_json(200, {"status": "accepted", "receipt": receipt})

    def log_message(self, _format: str, *_args: Any) -> None:
        return


def main() -> None:
    host = os.environ.get("HOLOGOV_V_SIGNER_HOST", "127.0.0.1")
    port = int(os.environ.get("HOLOGOV_V_SIGNER_PORT", "8765"))
    _load_private_key()
    httpd = ThreadingHTTPServer((host, port), _SignerHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
