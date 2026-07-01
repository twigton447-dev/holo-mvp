import json

import pytest

from holo_builder.policy_bridge import (
    POLICY_ACTION_DECISION_MAPPING,
    SMOKE_INPUT_PAYLOAD,
    input_fingerprint,
    run_policy_bridge_smoke,
    validate_policy_bridge_terminal_evidence,
)
from holobrain.policy_agent import (
    ALLOW_ACTION,
    BLOCK_ACTION,
    POLICY_ID,
    POLICY_SET_ID,
    build_policy_envelope,
)


INPUT_FINGERPRINT = "sha256:ab85e28edc2a081d239845e101392804183de1f817bcd416e68d7a384b02bb4e"
POLICY_A_FINGERPRINT = "sha256:8d35366942f5c46c2e4f3e72bf43f5bab30099636062718f3a3a9ee0d8f3746f"
POLICY_B_FINGERPRINT = "sha256:88c73bde15078c52575dc4968c24cd16b145dbaa11e9da6b6be21f5c79252153"


def _read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _read_policy_check(run_dir):
    path = run_dir / "governance" / "policy_checks.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    return json.loads(lines[0])


def test_policy_a_valid_builds_terminal_artifact(tmp_path):
    result = run_policy_bridge_smoke(
        SMOKE_INPUT_PAYLOAD,
        requested_policy_version="A",
        envelope_condition="valid",
        output_dir=tmp_path,
        run_id="policy_a_valid",
    )
    run_dir = result["run_dir"]
    manifest = _read_json(run_dir / "run_manifest.json")
    policy_check = _read_policy_check(run_dir)
    stored_envelope = _read_json(run_dir / "governance" / "holobrain_policy_envelope.json")

    assert input_fingerprint(SMOKE_INPUT_PAYLOAD) == INPUT_FINGERPRINT
    assert stored_envelope == build_policy_envelope("A")
    assert manifest["input_fingerprint"] == INPUT_FINGERPRINT
    assert manifest["policy_set_id"] == POLICY_SET_ID
    assert manifest["policy_version"] == "A"
    assert manifest["policy_fingerprint"] == POLICY_A_FINGERPRINT
    assert manifest["terminal_status"] == "BUILT"
    assert manifest["terminal_decision_policy_action"] == ALLOW_ACTION
    assert manifest["terminal_decision_policy_fingerprint"] == POLICY_A_FINGERPRINT
    assert manifest["terminal_decision_reason"] == f"LOCKED_HOLOBRAIN_POLICY:{POLICY_ID}"
    assert manifest["post_checkpoint_override_invoked"] is False
    assert manifest["secondary_authority_invoked"] is False
    assert manifest["terminal_decision_mutated_after_checkpoint"] is False
    assert manifest["final_artifact_path"] == "final_artifact.json"
    assert (run_dir / manifest["final_artifact_path"]).exists()

    assert policy_check["policy_valid_at_checkpoint"] is True
    assert policy_check["policy_action"] == ALLOW_ACTION
    assert policy_check["expected_terminal_decision_from_policy_action"] == "BUILT"
    assert policy_check["terminal_decision"] == "BUILT"
    assert policy_check["decision_mapping"] == POLICY_ACTION_DECISION_MAPPING
    assert policy_check["decision_invariant_passed"] is True
    assert policy_check["decision_cause"] == "LOCKED_HOLOBRAIN_POLICY"
    assert policy_check["decision_cause_policy_fingerprint"] == POLICY_A_FINGERPRINT
    assert policy_check["fallback_policy_used"] is False
    assert policy_check["local_policy_used"] is False
    assert policy_check["post_checkpoint_override_invoked"] is False
    assert policy_check["final_artifact_emitted"] is True
    assert validate_policy_bridge_terminal_evidence(run_dir) == {
        "valid": True,
        "reason": "VALID_LOCKED_POLICY_TERMINAL_EVIDENCE",
    }


def test_policy_b_valid_blocks_terminal_artifact(tmp_path):
    result = run_policy_bridge_smoke(
        SMOKE_INPUT_PAYLOAD,
        requested_policy_version="B",
        envelope_condition="valid",
        output_dir=tmp_path,
        run_id="policy_b_valid",
    )
    run_dir = result["run_dir"]
    manifest = _read_json(run_dir / "run_manifest.json")
    policy_check = _read_policy_check(run_dir)
    stored_envelope = _read_json(run_dir / "governance" / "holobrain_policy_envelope.json")

    assert stored_envelope == build_policy_envelope("B")
    assert manifest["input_fingerprint"] == INPUT_FINGERPRINT
    assert manifest["policy_set_id"] == POLICY_SET_ID
    assert manifest["policy_version"] == "B"
    assert manifest["policy_fingerprint"] == POLICY_B_FINGERPRINT
    assert manifest["terminal_status"] == "BLOCKED"
    assert manifest["terminal_decision_policy_action"] == BLOCK_ACTION
    assert manifest["terminal_decision_policy_fingerprint"] == POLICY_B_FINGERPRINT
    assert manifest["terminal_decision_reason"] == f"LOCKED_HOLOBRAIN_POLICY:{POLICY_ID}"
    assert manifest["post_checkpoint_override_invoked"] is False
    assert manifest["secondary_authority_invoked"] is False
    assert manifest["terminal_decision_mutated_after_checkpoint"] is False
    assert manifest["final_artifact_path"] is None
    assert not (run_dir / "final_artifact.json").exists()

    assert policy_check["policy_valid_at_checkpoint"] is True
    assert policy_check["policy_action"] == BLOCK_ACTION
    assert policy_check["expected_terminal_decision_from_policy_action"] == "BLOCKED"
    assert policy_check["terminal_decision"] == "BLOCKED"
    assert policy_check["decision_mapping"] == POLICY_ACTION_DECISION_MAPPING
    assert policy_check["decision_invariant_passed"] is True
    assert policy_check["decision_cause"] == "LOCKED_HOLOBRAIN_POLICY"
    assert policy_check["decision_cause_policy_fingerprint"] == POLICY_B_FINGERPRINT
    assert policy_check["fallback_policy_used"] is False
    assert policy_check["local_policy_used"] is False
    assert policy_check["post_checkpoint_override_invoked"] is False
    assert policy_check["final_artifact_emitted"] is False
    assert validate_policy_bridge_terminal_evidence(run_dir) == {
        "valid": True,
        "reason": "VALID_LOCKED_POLICY_TERMINAL_EVIDENCE",
    }


@pytest.mark.parametrize(
    ("condition", "expected_result", "envelope_exists"),
    (
        ("absent", "ABSENT_POLICY", False),
        ("tampered", "FINGERPRINT_MISMATCH", True),
        ("mismatched", "REQUESTED_POLICY_VERSION_MISMATCH", True),
    ),
)
def test_invalid_policy_fails_closed_without_terminal_artifact(
    tmp_path,
    condition,
    expected_result,
    envelope_exists,
):
    result = run_policy_bridge_smoke(
        SMOKE_INPUT_PAYLOAD,
        requested_policy_version="A",
        envelope_condition=condition,
        output_dir=tmp_path,
        run_id=f"policy_a_{condition}",
    )
    run_dir = result["run_dir"]
    manifest = _read_json(run_dir / "run_manifest.json")
    policy_check = _read_policy_check(run_dir)
    envelope_path = run_dir / "governance" / "holobrain_policy_envelope.json"

    assert envelope_path.exists() is envelope_exists
    assert manifest["requested_policy_version"] == "A"
    assert manifest["received_envelope_condition"] == condition
    assert manifest["policy_validation_result"] == expected_result
    assert manifest["policy_version"] is None
    assert manifest["policy_fingerprint"] is None
    assert manifest["terminal_status"] == "POLICY_NOT_VERIFIED"
    assert manifest["terminal_decision_reason"] == "NO_VALID_LOCKED_HOLOBRAIN_POLICY"
    assert manifest["terminal_decision_policy_fingerprint"] is None
    assert manifest["final_artifact_path"] is None
    assert manifest["final_artifact_behavior_consistent_with_terminal_decision"] is True
    assert manifest["post_checkpoint_override_invoked"] is False
    assert manifest["secondary_authority_invoked"] is False
    assert manifest["terminal_decision_mutated_after_checkpoint"] is False
    assert not (run_dir / "final_artifact.json").exists()

    assert policy_check["policy_valid_at_checkpoint"] is False
    assert policy_check["policy_validation_result"] == expected_result
    assert policy_check["terminal_decision"] == "POLICY_NOT_VERIFIED"
    assert policy_check["decision_cause"] == "NO_VALID_LOCKED_HOLOBRAIN_POLICY"
    assert policy_check["decision_cause_policy_fingerprint"] is None
    assert policy_check["locked_policy_fingerprint"] is None
    assert policy_check["policy_action"] is None
    assert policy_check["final_artifact_emitted"] is False
    assert policy_check["fallback_policy_used"] is False
    assert policy_check["local_policy_used"] is False
    assert policy_check["post_checkpoint_override_invoked"] is False
    assert validate_policy_bridge_terminal_evidence(run_dir) == {
        "valid": True,
        "reason": "VALID_FAIL_CLOSED_POLICY_NOT_VERIFIED_EVIDENCE",
    }


def test_forged_terminal_artifact_without_bridge_is_not_partner_valid(tmp_path):
    run_dir = tmp_path / "runs" / "forged_no_bridge"
    governance_dir = run_dir / "governance"
    governance_dir.mkdir(parents=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "final_artifact.json").write_text(
        json.dumps(SMOKE_INPUT_PAYLOAD["artifact"], indent=2),
        encoding="utf-8",
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "forged_no_bridge",
                "input_fingerprint": INPUT_FINGERPRINT,
                "policy_source": "HoloBrain",
                "policy_set_id": POLICY_SET_ID,
                "policy_version": "A",
                "policy_fingerprint": POLICY_A_FINGERPRINT,
                "policy_ingest_checkpoint": "PRE_EXECUTION_POLICY_LOCK",
                "enforcement_checkpoint": "TERMINAL_ARTIFACT_RELEASE",
                "terminal_status": "BUILT",
                "terminal_decision_policy_action": ALLOW_ACTION,
                "terminal_decision_reason": f"LOCKED_HOLOBRAIN_POLICY:{POLICY_ID}",
                "terminal_decision_policy_fingerprint": POLICY_A_FINGERPRINT,
                "post_checkpoint_override_invoked": False,
                "secondary_authority_invoked": False,
                "terminal_decision_mutated_after_checkpoint": False,
                "final_artifact_path": "final_artifact.json",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert validate_policy_bridge_terminal_evidence(run_dir) == {
        "valid": False,
        "reason": "MISSING_POLICY_REQUEST",
    }


def test_forged_locked_policy_claim_without_envelope_is_not_partner_valid(tmp_path):
    run_dir = tmp_path / "runs" / "forged_claimed_lock"
    governance_dir = run_dir / "governance"
    governance_dir.mkdir(parents=True)

    (governance_dir / "policy_request.json").write_text(
        json.dumps(
            {
                "run_id": "forged_claimed_lock",
                "domain": "policy_bridge_smoke",
                "requested_policy_set": POLICY_SET_ID,
                "requested_policy_version": "A",
                "received_envelope_condition": "valid",
                "hologov_profile": "offline_policy_bridge_smoke_v1",
                "input_fingerprint": INPUT_FINGERPRINT,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (governance_dir / "policy_ingest_record.json").write_text(
        json.dumps(
            {
                "checkpoint": "PRE_EXECUTION_POLICY_LOCK",
                "policy_source": "HoloBrain",
                "policy_set_id": POLICY_SET_ID,
                "requested_policy_version": "A",
                "received_policy_version": "A",
                "received_envelope_condition": "valid",
                "policy_validation_result": "VALID_LOCKED_POLICY",
                "policy_valid": True,
                "locked_policy_fingerprint": POLICY_A_FINGERPRINT,
                "policy_envelope_path": "governance/holobrain_policy_envelope.json",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (governance_dir / "policy_checks.jsonl").write_text(
        json.dumps(
            {
                "checkpoint": "TERMINAL_ARTIFACT_RELEASE",
                "input_fingerprint": INPUT_FINGERPRINT,
                "policy_source": "HoloBrain",
                "policy_set_id": POLICY_SET_ID,
                "requested_policy_version": "A",
                "received_policy_version": "A",
                "locked_policy_fingerprint": POLICY_A_FINGERPRINT,
                "policy_valid_at_checkpoint": True,
                "policy_validation_result": "VALID_LOCKED_POLICY",
                "evaluated_policy_id": POLICY_ID,
                "policy_match": True,
                "policy_action": ALLOW_ACTION,
                "expected_terminal_decision_from_policy_action": "BUILT",
                "terminal_decision": "BUILT",
                "decision_mapping": POLICY_ACTION_DECISION_MAPPING,
                "decision_invariant_passed": True,
                "post_checkpoint_override_invoked": False,
                "secondary_authority_invoked": False,
                "terminal_decision_mutated_after_checkpoint": False,
                "decision_cause": "LOCKED_HOLOBRAIN_POLICY",
                "decision_cause_policy_fingerprint": POLICY_A_FINGERPRINT,
                "final_artifact_emitted": True,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "run_id": "forged_claimed_lock",
                "input_fingerprint": INPUT_FINGERPRINT,
                "policy_source": "HoloBrain",
                "policy_set_id": POLICY_SET_ID,
                "policy_version": "A",
                "policy_fingerprint": POLICY_A_FINGERPRINT,
                "policy_ingest_checkpoint": "PRE_EXECUTION_POLICY_LOCK",
                "enforcement_checkpoint": "TERMINAL_ARTIFACT_RELEASE",
                "terminal_status": "BUILT",
                "terminal_decision_policy_action": ALLOW_ACTION,
                "terminal_decision_expected_from_policy_action": "BUILT",
                "terminal_decision_mapping": POLICY_ACTION_DECISION_MAPPING,
                "terminal_decision_invariant_passed": True,
                "terminal_decision_reason": f"LOCKED_HOLOBRAIN_POLICY:{POLICY_ID}",
                "terminal_decision_policy_fingerprint": POLICY_A_FINGERPRINT,
                "post_checkpoint_override_invoked": False,
                "secondary_authority_invoked": False,
                "terminal_decision_mutated_after_checkpoint": False,
                "final_artifact_path": "final_artifact.json",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "final_artifact.json").write_text(
        json.dumps(SMOKE_INPUT_PAYLOAD["artifact"], indent=2),
        encoding="utf-8",
    )

    assert validate_policy_bridge_terminal_evidence(run_dir) == {
        "valid": False,
        "reason": "MISSING_POLICY_ENVELOPE",
    }
