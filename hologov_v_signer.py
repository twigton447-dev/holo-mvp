"""
Client-side HoloGov-V receipt utilities.

The API process is allowed to verify signer-issued receipts with a public trust
root. It is not allowed to hold the private signing key or mint signatures.
"""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

HOLOGOV_V_RECEIPT_SCHEMA = "hologov_v_receipt_v1"
HOLOGOV_V_RECEIPT_VERSION = "1"

_SIGNED_RECEIPT_FIELDS = (
    "receipt_id",
    "schema",
    "receipt_version",
    "lane",
    "status",
    "enforcement_point",
    "decision",
    "evaluation_id",
    "evidence_hash",
    "signer_id",
    "key_id",
    "issued_at",
    "nonce",
)


class HoloGovVSignerError(RuntimeError):
    """Base error for isolated HoloGov-V signer failures."""


class HoloGovVSignerUnavailableError(HoloGovVSignerError):
    """Raised when the isolated signer cannot be reached or times out."""


class HoloGovVSignerVetoError(HoloGovVSignerError):
    """Raised when the isolated signer refuses to issue a receipt."""


class HoloGovVReceiptVerificationError(HoloGovVSignerError):
    """Raised when a signer response does not verify against the trust root."""


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def receipt_signed_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {field: receipt.get(field) for field in _SIGNED_RECEIPT_FIELDS}


def verify_hologov_v_receipt(
    receipt: dict[str, Any],
    public_key_b64: str,
) -> bool:
    if not isinstance(receipt, dict):
        return False
    if receipt.get("schema") != HOLOGOV_V_RECEIPT_SCHEMA:
        return False
    if receipt.get("receipt_version") != HOLOGOV_V_RECEIPT_VERSION:
        return False
    if receipt.get("lane") != "HoloGov-V":
        return False
    if receipt.get("status") != "accepted":
        return False
    if receipt.get("decision") not in {"ALLOW", "ESCALATE"}:
        return False
    signature_b64 = receipt.get("receipt_signature")
    if not signature_b64:
        return False
    if any(receipt.get(field) in (None, "") for field in _SIGNED_RECEIPT_FIELDS):
        return False

    try:
        public_key = Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64))
        signature = base64.b64decode(signature_b64)
        public_key.verify(
            signature,
            canonical_json(receipt_signed_payload(receipt)).encode("utf-8"),
        )
    except (InvalidSignature, ValueError, TypeError):
        return False
    return True


class HoloGovVSignerClient:
    def __init__(
        self,
        signer_url: str,
        public_key_b64: str,
        timeout_s: float = 1.0,
    ) -> None:
        self.signer_url = signer_url.rstrip("/")
        self.public_key_b64 = public_key_b64
        self.timeout_s = timeout_s

    @classmethod
    def from_env(cls, env: dict[str, str]) -> "HoloGovVSignerClient":
        if env.get("HOLOGOV_V_SIGNER_PRIVATE_KEY_B64", "").strip():
            raise HoloGovVSignerUnavailableError(
                "HOLOGOV_V_SIGNER_PRIVATE_KEY_B64 must not be present in the API process."
            )
        signer_url = env.get("HOLOGOV_V_SIGNER_URL", "").strip()
        public_key_b64 = env.get("HOLOGOV_V_SIGNER_PUBLIC_KEY_B64", "").strip()
        if not signer_url:
            raise HoloGovVSignerUnavailableError("HOLOGOV_V_SIGNER_URL is not configured.")
        if not public_key_b64:
            raise HoloGovVSignerUnavailableError("HOLOGOV_V_SIGNER_PUBLIC_KEY_B64 is not configured.")
        timeout_raw = env.get("HOLOGOV_V_SIGNER_TIMEOUT_MS", "1000").strip()
        try:
            timeout_s = max(0.05, int(timeout_raw) / 1000)
        except ValueError:
            timeout_s = 1.0
        return cls(signer_url=signer_url, public_key_b64=public_key_b64, timeout_s=timeout_s)

    def issue_receipt(
        self,
        *,
        decision: str,
        evaluation_id: str,
        evidence_hash: str,
    ) -> dict[str, Any]:
        url = urllib.parse.urljoin(
            self.signer_url + "/",
            "v1/hologov-v/receipts",
        )
        payload = {
            "decision": decision,
            "evaluation_id": evaluation_id,
            "evidence_hash": evidence_hash,
            "enforcement_point": "/v1/evaluate_action",
        }
        request = urllib.request.Request(
            url,
            data=canonical_json(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code in {403, 409, 422}:
                raise HoloGovVSignerVetoError("HoloGov-V signer vetoed receipt issuance.") from e
            raise HoloGovVSignerUnavailableError("HoloGov-V signer returned an error.") from e
        except (TimeoutError, urllib.error.URLError, OSError) as e:
            raise HoloGovVSignerUnavailableError("HoloGov-V signer unavailable.") from e

        try:
            response_payload = json.loads(raw)
        except json.JSONDecodeError as e:
            raise HoloGovVReceiptVerificationError("HoloGov-V signer returned invalid JSON.") from e

        receipt = response_payload.get("receipt")
        if not isinstance(receipt, dict):
            raise HoloGovVReceiptVerificationError("HoloGov-V signer did not return a receipt.")
        if receipt.get("decision") != decision:
            raise HoloGovVReceiptVerificationError("HoloGov-V signer receipt decision mismatch.")
        if receipt.get("evaluation_id") != evaluation_id:
            raise HoloGovVReceiptVerificationError("HoloGov-V signer receipt evaluation mismatch.")
        if receipt.get("evidence_hash") != evidence_hash:
            raise HoloGovVReceiptVerificationError("HoloGov-V signer receipt evidence mismatch.")
        if not verify_hologov_v_receipt(receipt, self.public_key_b64):
            raise HoloGovVReceiptVerificationError("HoloGov-V signer receipt failed verification.")
        return receipt
