"""Local HoloBrain policy source for the HoloBuild bridge smoke test."""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


POLICY_SET_ID = "HB_POLICY_BRIDGE_SMOKE"
POLICY_ID = "HB-SMOKE-TERMINAL-001"
DECISION_POINT = "TERMINAL_ARTIFACT_RELEASE"
AGENT_NAME = "HoloBrainPolicyAgent"

ALLOW_ACTION = "ALLOW_FINAL_ARTIFACT"
BLOCK_ACTION = "BLOCK_FINAL_ARTIFACT"

VALID_POLICY_VERSIONS = frozenset({"A", "B"})
VALID_ENVELOPE_CONDITIONS = frozenset({"valid", "absent", "tampered", "mismatched"})


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_fingerprint(data: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def build_policy_payload(policy_version: str) -> dict[str, Any]:
    if policy_version not in VALID_POLICY_VERSIONS:
        raise ValueError(f"unknown smoke policy version: {policy_version}")

    action = ALLOW_ACTION if policy_version == "A" else BLOCK_ACTION
    return {
        "policy_set_id": POLICY_SET_ID,
        "policy_version": policy_version,
        "policy_ids": [POLICY_ID],
        "policies": [
            {
                "policy_id": POLICY_ID,
                "decision_point": DECISION_POINT,
                "match": {
                    "artifact.visibility": "external",
                    "artifact.contains": "BRIDGE_SMOKE_TOKEN",
                },
                "action": action,
            }
        ],
    }


def build_policy_envelope(
    policy_version: str,
    *,
    issued_at: str = "2026-06-26T00:00:00Z",
) -> dict[str, Any]:
    payload = build_policy_payload(policy_version)
    return {
        **payload,
        "issued_by_agent": AGENT_NAME,
        "issued_at": issued_at,
        "fingerprint": sha256_fingerprint(payload),
    }


def get_policy_envelope(
    requested_policy_version: str,
    *,
    envelope_condition: str = "valid",
    issued_at: str = "2026-06-26T00:00:00Z",
) -> dict[str, Any] | None:
    """Return a local policy envelope or a controlled corrupted variant."""
    if requested_policy_version not in VALID_POLICY_VERSIONS:
        raise ValueError(f"unknown smoke policy version: {requested_policy_version}")
    if envelope_condition not in VALID_ENVELOPE_CONDITIONS:
        raise ValueError(f"unknown envelope condition: {envelope_condition}")
    if envelope_condition == "absent":
        return None

    version = requested_policy_version
    if envelope_condition == "mismatched":
        version = "B" if requested_policy_version == "A" else "A"

    envelope = build_policy_envelope(version, issued_at=issued_at)
    if envelope_condition == "tampered":
        tampered = copy.deepcopy(envelope)
        policy = tampered["policies"][0]
        policy["action"] = (
            BLOCK_ACTION if policy["action"] == ALLOW_ACTION else ALLOW_ACTION
        )
        return tampered

    return envelope
