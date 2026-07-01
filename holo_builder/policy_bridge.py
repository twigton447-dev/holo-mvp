"""Provider-free HoloBrain -> HoloBuild policy bridge smoke runner."""

from __future__ import annotations

import copy
import json
import uuid
from pathlib import Path
from typing import Any

from holobrain.policy_agent import (
    ALLOW_ACTION,
    BLOCK_ACTION,
    DECISION_POINT,
    POLICY_ID,
    POLICY_SET_ID,
    get_policy_envelope,
    sha256_fingerprint,
)


PRE_EXECUTION_POLICY_LOCK = "PRE_EXECUTION_POLICY_LOCK"
TERMINAL_ARTIFACT_RELEASE = DECISION_POINT
POLICY_ACTION_DECISION_MAPPING = "POLICY_ACTION_DIRECT_TERMINAL_DECISION_V1"

SMOKE_INPUT_PAYLOAD = {
    "input_id": "HB_POLICY_BRIDGE_SMOKE_INPUT_001",
    "builder_mode": "deterministic_local_no_provider",
    "artifact_kind": "claim_summary",
    "artifact": {
        "visibility": "external",
        "body": "BRIDGE_SMOKE_TOKEN: publishable smoke artifact.",
    },
}


def input_fingerprint(input_payload: dict[str, Any]) -> str:
    return sha256_fingerprint(input_payload)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, sort_keys=True) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _read_single_jsonl(path: Path) -> dict[str, Any] | None:
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except Exception:
        return None
    if len(lines) != 1:
        return None
    try:
        payload = json.loads(lines[0])
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _policy_payload_from_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy_set_id": envelope.get("policy_set_id"),
        "policy_version": envelope.get("policy_version"),
        "policy_ids": envelope.get("policy_ids"),
        "policies": envelope.get("policies"),
    }


def _validate_policy_envelope(
    *,
    envelope: dict[str, Any] | None,
    requested_policy_version: str,
) -> dict[str, Any]:
    if envelope is None:
        return {
            "valid": False,
            "result": "ABSENT_POLICY",
            "policy_version": None,
            "policy_fingerprint": None,
            "policy": None,
        }

    policy_payload = _policy_payload_from_envelope(envelope)
    expected_fingerprint = sha256_fingerprint(policy_payload)
    recorded_fingerprint = envelope.get("fingerprint")
    if recorded_fingerprint != expected_fingerprint:
        return {
            "valid": False,
            "result": "FINGERPRINT_MISMATCH",
            "policy_version": envelope.get("policy_version"),
            "policy_fingerprint": recorded_fingerprint,
            "computed_policy_fingerprint": expected_fingerprint,
            "policy": None,
        }

    if envelope.get("policy_set_id") != POLICY_SET_ID:
        return {
            "valid": False,
            "result": "POLICY_SET_MISMATCH",
            "policy_version": envelope.get("policy_version"),
            "policy_fingerprint": recorded_fingerprint,
            "policy": None,
        }

    if envelope.get("policy_version") != requested_policy_version:
        return {
            "valid": False,
            "result": "REQUESTED_POLICY_VERSION_MISMATCH",
            "policy_version": envelope.get("policy_version"),
            "policy_fingerprint": recorded_fingerprint,
            "policy": None,
        }

    policies = envelope.get("policies")
    if not isinstance(policies, list):
        return {
            "valid": False,
            "result": "POLICY_PAYLOAD_INVALID",
            "policy_version": envelope.get("policy_version"),
            "policy_fingerprint": recorded_fingerprint,
            "policy": None,
        }

    matching = [
        policy
        for policy in policies
        if policy.get("policy_id") == POLICY_ID
        and policy.get("decision_point") == TERMINAL_ARTIFACT_RELEASE
    ]
    if len(matching) != 1:
        return {
            "valid": False,
            "result": "TERMINAL_POLICY_NOT_FOUND",
            "policy_version": envelope.get("policy_version"),
            "policy_fingerprint": recorded_fingerprint,
            "policy": None,
        }

    return {
        "valid": True,
        "result": "VALID_LOCKED_POLICY",
        "policy_version": envelope.get("policy_version"),
        "policy_fingerprint": recorded_fingerprint,
        "policy": matching[0],
    }


def _policy_matches_artifact(policy: dict[str, Any], artifact: dict[str, Any]) -> bool:
    match = policy.get("match") or {}
    visibility_ok = artifact.get("visibility") == match.get("artifact.visibility")
    required_text = match.get("artifact.contains")
    body_ok = isinstance(required_text, str) and required_text in artifact.get("body", "")
    return visibility_ok and body_ok


def _terminal_decision_from_action(policy_action: str | None) -> str:
    if policy_action == ALLOW_ACTION:
        return "BUILT"
    if policy_action == BLOCK_ACTION:
        return "BLOCKED"
    return "POLICY_NOT_VERIFIED"


def _build_candidate_artifact(input_payload: dict[str, Any]) -> dict[str, Any]:
    artifact = copy.deepcopy(input_payload.get("artifact") or {})
    return {
        "artifact_kind": input_payload.get("artifact_kind"),
        "visibility": artifact.get("visibility"),
        "body": artifact.get("body"),
    }


def run_policy_bridge_smoke(
    input_payload: dict[str, Any] | None = None,
    *,
    requested_policy_version: str,
    envelope_condition: str = "valid",
    output_dir: str | Path,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Run the isolated policy bridge slice and write falsifiable evidence."""
    payload = copy.deepcopy(input_payload or SMOKE_INPUT_PAYLOAD)
    run_id = run_id or f"hb_policy_bridge_{uuid.uuid4().hex[:12]}"
    run_root = Path(output_dir) / "runs" / run_id
    governance_dir = run_root / "governance"
    governance_dir.mkdir(parents=True, exist_ok=True)

    in_fingerprint = input_fingerprint(payload)
    policy_request = {
        "run_id": run_id,
        "domain": "policy_bridge_smoke",
        "requested_policy_set": POLICY_SET_ID,
        "requested_policy_version": requested_policy_version,
        "received_envelope_condition": envelope_condition,
        "hologov_profile": "offline_policy_bridge_smoke_v1",
        "input_fingerprint": in_fingerprint,
    }
    policy_request_path = governance_dir / "policy_request.json"
    _write_json(policy_request_path, policy_request)

    envelope = get_policy_envelope(
        requested_policy_version,
        envelope_condition=envelope_condition,
    )
    envelope_path = governance_dir / "holobrain_policy_envelope.json"
    if envelope is not None:
        _write_json(envelope_path, envelope)

    validation = _validate_policy_envelope(
        envelope=envelope,
        requested_policy_version=requested_policy_version,
    )
    ingest_record = {
        "checkpoint": PRE_EXECUTION_POLICY_LOCK,
        "policy_source": "HoloBrain",
        "policy_set_id": POLICY_SET_ID,
        "requested_policy_version": requested_policy_version,
        "received_policy_version": validation.get("policy_version"),
        "received_envelope_condition": envelope_condition,
        "policy_validation_result": validation["result"],
        "policy_valid": validation["valid"],
        "locked_policy_fingerprint": (
            validation["policy_fingerprint"] if validation["valid"] else None
        ),
        "policy_envelope_path": (
            str(envelope_path.relative_to(run_root)) if envelope is not None else None
        ),
    }
    _write_json(governance_dir / "policy_ingest_record.json", ingest_record)

    candidate_artifact = _build_candidate_artifact(payload)
    policy = validation.get("policy")
    policy_action = policy.get("action") if isinstance(policy, dict) else None
    policy_match = (
        _policy_matches_artifact(policy, candidate_artifact)
        if validation["valid"] and isinstance(policy, dict)
        else False
    )

    if validation["valid"] and policy_match:
        terminal_status = _terminal_decision_from_action(policy_action)
        decision_cause = "LOCKED_HOLOBRAIN_POLICY"
        decision_reason = f"LOCKED_HOLOBRAIN_POLICY:{POLICY_ID}"
        decision_policy_fingerprint = validation["policy_fingerprint"]
        expected_terminal = terminal_status
        invariant_passed = terminal_status in {"BUILT", "BLOCKED"}
    else:
        terminal_status = "POLICY_NOT_VERIFIED"
        decision_cause = "NO_VALID_LOCKED_HOLOBRAIN_POLICY"
        decision_reason = "NO_VALID_LOCKED_HOLOBRAIN_POLICY"
        decision_policy_fingerprint = None
        expected_terminal = "POLICY_NOT_VERIFIED"
        invariant_passed = validation["valid"] is False

    final_artifact_path: Path | None = None
    final_artifact_emitted = False
    if terminal_status == "BUILT":
        final_artifact_path = run_root / "final_artifact.json"
        _write_json(final_artifact_path, candidate_artifact)
        final_artifact_emitted = True

    policy_check = {
        "checkpoint": TERMINAL_ARTIFACT_RELEASE,
        "input_fingerprint": in_fingerprint,
        "policy_source": "HoloBrain",
        "policy_set_id": POLICY_SET_ID,
        "requested_policy_version": requested_policy_version,
        "received_policy_version": validation.get("policy_version"),
        "received_envelope_condition": envelope_condition,
        "locked_policy_fingerprint": (
            validation["policy_fingerprint"] if validation["valid"] else None
        ),
        "policy_valid_at_checkpoint": validation["valid"],
        "policy_validation_result": validation["result"],
        "evaluated_policy_id": POLICY_ID if validation["valid"] else None,
        "policy_match": policy_match,
        "policy_action": policy_action,
        "expected_terminal_decision_from_policy_action": expected_terminal,
        "terminal_decision": terminal_status,
        "decision_mapping": POLICY_ACTION_DECISION_MAPPING,
        "decision_invariant_passed": invariant_passed,
        "terminal_decision_finalized_at_checkpoint": True,
        "post_checkpoint_override_allowed": False,
        "post_checkpoint_override_invoked": False,
        "post_checkpoint_override_sources_checked": [
            "downstream_stage",
            "fallback_guard",
            "local_policy",
            "release_layer",
            "secondary_authority",
        ],
        "post_checkpoint_override_source": None,
        "terminal_decision_mutated_after_checkpoint": False,
        "fallback_policy_used": False,
        "local_policy_used": False,
        "secondary_authority_invoked": False,
        "decision_cause": decision_cause,
        "decision_cause_policy_fingerprint": decision_policy_fingerprint,
        "final_artifact_emitted": final_artifact_emitted,
    }
    _write_jsonl(governance_dir / "policy_checks.jsonl", [policy_check])

    manifest = {
        "run_id": run_id,
        "input_fingerprint": in_fingerprint,
        "policy_source": "HoloBrain",
        "policy_set_id": POLICY_SET_ID,
        "requested_policy_version": requested_policy_version,
        "received_policy_version": validation.get("policy_version"),
        "received_envelope_condition": envelope_condition,
        "policy_version": validation.get("policy_version") if validation["valid"] else None,
        "policy_fingerprint": (
            validation["policy_fingerprint"] if validation["valid"] else None
        ),
        "policy_validation_result": validation["result"],
        "policy_ingest_checkpoint": PRE_EXECUTION_POLICY_LOCK,
        "enforcement_checkpoint": TERMINAL_ARTIFACT_RELEASE,
        "terminal_status": terminal_status,
        "terminal_decision_policy_action": policy_action,
        "terminal_decision_expected_from_policy_action": expected_terminal,
        "terminal_decision_mapping": POLICY_ACTION_DECISION_MAPPING,
        "terminal_decision_invariant_passed": invariant_passed,
        "terminal_decision_source_checkpoint": TERMINAL_ARTIFACT_RELEASE,
        "terminal_decision_reason": decision_reason,
        "terminal_decision_policy_fingerprint": decision_policy_fingerprint,
        "post_checkpoint_override_allowed": False,
        "post_checkpoint_override_invoked": False,
        "post_checkpoint_override_source": None,
        "secondary_authority_invoked": False,
        "terminal_decision_mutated_after_checkpoint": False,
        "final_artifact_behavior_consistent_with_terminal_decision": (
            (terminal_status == "BUILT" and final_artifact_emitted)
            or (terminal_status in {"BLOCKED", "POLICY_NOT_VERIFIED"} and not final_artifact_emitted)
        ),
        "final_artifact_path": (
            str(final_artifact_path.relative_to(run_root)) if final_artifact_path else None
        ),
    }
    _write_json(run_root / "run_manifest.json", manifest)

    return {
        "run_id": run_id,
        "run_dir": run_root,
        "governance_dir": governance_dir,
        "policy_request": policy_request,
        "policy_envelope": envelope,
        "policy_ingest_record": ingest_record,
        "policy_check": policy_check,
        "run_manifest": manifest,
    }


def validate_policy_bridge_terminal_evidence(run_dir: str | Path) -> dict[str, Any]:
    """Return whether a run has enough evidence to be policy-bridge-valid."""
    root = Path(run_dir)
    governance_dir = root / "governance"
    manifest = _read_json(root / "run_manifest.json")
    if manifest is None:
        return {"valid": False, "reason": "MISSING_RUN_MANIFEST"}

    policy_request = _read_json(governance_dir / "policy_request.json")
    if policy_request is None:
        return {"valid": False, "reason": "MISSING_POLICY_REQUEST"}

    ingest_record = _read_json(governance_dir / "policy_ingest_record.json")
    if ingest_record is None:
        return {"valid": False, "reason": "MISSING_POLICY_INGEST_RECORD"}

    policy_check = _read_single_jsonl(governance_dir / "policy_checks.jsonl")
    if policy_check is None:
        return {"valid": False, "reason": "MISSING_OR_INVALID_POLICY_CHECKS"}

    if manifest.get("policy_ingest_checkpoint") != PRE_EXECUTION_POLICY_LOCK:
        return {"valid": False, "reason": "MISSING_POLICY_LOCK_CHECKPOINT"}
    if manifest.get("enforcement_checkpoint") != TERMINAL_ARTIFACT_RELEASE:
        return {"valid": False, "reason": "MISSING_TERMINAL_RELEASE_CHECKPOINT"}
    if policy_check.get("checkpoint") != TERMINAL_ARTIFACT_RELEASE:
        return {"valid": False, "reason": "POLICY_CHECK_NOT_TERMINAL_RELEASE"}
    if manifest.get("input_fingerprint") != policy_request.get("input_fingerprint"):
        return {"valid": False, "reason": "INPUT_FINGERPRINT_MISMATCH"}
    if manifest.get("terminal_status") != policy_check.get("terminal_decision"):
        return {"valid": False, "reason": "TERMINAL_DECISION_MISMATCH"}

    override_fields = (
        "post_checkpoint_override_invoked",
        "secondary_authority_invoked",
        "terminal_decision_mutated_after_checkpoint",
    )
    for field in override_fields:
        if manifest.get(field) is not False or policy_check.get(field) is not False:
            return {"valid": False, "reason": f"OVERRIDE_FIELD_NOT_FALSE:{field}"}

    terminal_status = manifest.get("terminal_status")
    final_artifact_path = manifest.get("final_artifact_path")
    final_artifact_exists = bool(final_artifact_path and (root / final_artifact_path).exists())

    if terminal_status in {"BUILT", "BLOCKED"}:
        envelope = _read_json(governance_dir / "holobrain_policy_envelope.json")
        if envelope is None:
            return {"valid": False, "reason": "MISSING_POLICY_ENVELOPE"}
        envelope_fingerprint = sha256_fingerprint(_policy_payload_from_envelope(envelope))
        recorded_fingerprint = envelope.get("fingerprint")
        if recorded_fingerprint != envelope_fingerprint:
            return {"valid": False, "reason": "POLICY_ENVELOPE_FINGERPRINT_INVALID"}

        manifest_fingerprint = manifest.get("policy_fingerprint")
        check_locked_fingerprint = policy_check.get("locked_policy_fingerprint")
        check_cause_fingerprint = policy_check.get("decision_cause_policy_fingerprint")
        fingerprints = {
            recorded_fingerprint,
            manifest_fingerprint,
            manifest.get("terminal_decision_policy_fingerprint"),
            check_locked_fingerprint,
            check_cause_fingerprint,
            ingest_record.get("locked_policy_fingerprint"),
        }
        if None in fingerprints or len(fingerprints) != 1:
            return {"valid": False, "reason": "LOCKED_POLICY_FINGERPRINT_CHAIN_INVALID"}

        if manifest.get("policy_version") != policy_check.get("received_policy_version"):
            return {"valid": False, "reason": "POLICY_VERSION_MISMATCH"}
        if ingest_record.get("policy_valid") is not True:
            return {"valid": False, "reason": "POLICY_NOT_VALID_AT_LOCK"}
        if policy_check.get("policy_valid_at_checkpoint") is not True:
            return {"valid": False, "reason": "POLICY_NOT_VALID_AT_TERMINAL_CHECKPOINT"}
        if policy_check.get("decision_cause") != "LOCKED_HOLOBRAIN_POLICY":
            return {"valid": False, "reason": "TERMINAL_DECISION_NOT_CAUSED_BY_LOCKED_POLICY"}
        if not str(manifest.get("terminal_decision_reason", "")).startswith(
            f"LOCKED_HOLOBRAIN_POLICY:{POLICY_ID}"
        ):
            return {"valid": False, "reason": "TERMINAL_DECISION_REASON_INVALID"}
        if policy_check.get("decision_mapping") != POLICY_ACTION_DECISION_MAPPING:
            return {"valid": False, "reason": "TERMINAL_DECISION_MAPPING_INVALID"}
        if manifest.get("terminal_decision_invariant_passed") is not True:
            return {"valid": False, "reason": "MANIFEST_DECISION_INVARIANT_NOT_PASSED"}
        if policy_check.get("decision_invariant_passed") is not True:
            return {"valid": False, "reason": "POLICY_CHECK_DECISION_INVARIANT_NOT_PASSED"}

        policy_action = policy_check.get("policy_action")
        if policy_action == ALLOW_ACTION and terminal_status != "BUILT":
            return {"valid": False, "reason": "ALLOW_ACTION_DID_NOT_BUILD"}
        if policy_action == BLOCK_ACTION and terminal_status != "BLOCKED":
            return {"valid": False, "reason": "BLOCK_ACTION_DID_NOT_BLOCK"}
        if policy_action not in {ALLOW_ACTION, BLOCK_ACTION}:
            return {"valid": False, "reason": "UNKNOWN_POLICY_ACTION"}

        if terminal_status == "BUILT":
            if not final_artifact_exists or policy_check.get("final_artifact_emitted") is not True:
                return {"valid": False, "reason": "BUILT_ARTIFACT_MISSING"}
        if terminal_status == "BLOCKED":
            if final_artifact_exists or policy_check.get("final_artifact_emitted") is not False:
                return {"valid": False, "reason": "BLOCKED_ARTIFACT_EMITTED"}
        return {"valid": True, "reason": "VALID_LOCKED_POLICY_TERMINAL_EVIDENCE"}

    if terminal_status == "POLICY_NOT_VERIFIED":
        if final_artifact_exists or policy_check.get("final_artifact_emitted") is not False:
            return {"valid": False, "reason": "UNVERIFIED_POLICY_EMITTED_ARTIFACT"}
        if manifest.get("policy_fingerprint") is not None:
            return {"valid": False, "reason": "UNVERIFIED_POLICY_HAS_MANIFEST_FINGERPRINT"}
        if manifest.get("terminal_decision_policy_fingerprint") is not None:
            return {"valid": False, "reason": "UNVERIFIED_POLICY_HAS_DECISION_FINGERPRINT"}
        if policy_check.get("policy_valid_at_checkpoint") is not False:
            return {"valid": False, "reason": "UNVERIFIED_POLICY_MARKED_VALID_AT_CHECKPOINT"}
        if policy_check.get("decision_cause") != "NO_VALID_LOCKED_HOLOBRAIN_POLICY":
            return {"valid": False, "reason": "UNVERIFIED_POLICY_DECISION_CAUSE_INVALID"}
        return {"valid": True, "reason": "VALID_FAIL_CLOSED_POLICY_NOT_VERIFIED_EVIDENCE"}

    return {"valid": False, "reason": "UNKNOWN_TERMINAL_STATUS"}
