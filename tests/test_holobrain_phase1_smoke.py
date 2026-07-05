import json
from pathlib import Path

import pytest

from holobrain.memory.contracts import (
    CaseExperience,
    MaintenanceCandidate,
    PolicyClause,
    PolicyObject,
    assert_no_raw_trace_default_payload,
    build_retrieval_slice,
    highest_authority,
    lane_fidelity_contract,
    promote_maintenance_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
PROFILE_MANIFEST = ROOT / "holo_profiles" / "locked_architecture_profiles.json"
DOCTRINE = ROOT / "holobrain" / "memory" / "HoloGov_Memory_Doctrine_v0.1.md"
ROSTER = ROOT / "holobrain" / "memory" / "HoloBrainMaintenanceRoster_v0.1.md"


def _policy(status="active", superseded_by=None):
    return PolicyObject(
        policy_id="policy.payment.change.v1",
        lane_scope=("HoloGov-B", "HoloGov-V"),
        domain="partner_action_review",
        title="Payment change review",
        clauses=(
            PolicyClause(
                clause_id="verify-authority",
                operative_text="Verify authority before approving the action.",
                source_ref="policy.payment.change.v1#verify-authority",
            ),
        ),
        full_text_ref="object://policies/payment-change-v1.md#sha256:policyhash",
        status=status,
        superseded_by=superseded_by,
    )


def _case(status="active", superseded_by=None):
    return CaseExperience(
        case_id="case.payment-change.near-miss.v1",
        lane_scope=("HoloGov-B", "HoloGov-V"),
        domain="partner_action_review",
        case_type="diagnostic",
        confidence="locked_artifact_backed",
        summary="A proposed vendor payment change lacked independent authority evidence.",
        trigger_pattern=("payment instruction change",),
        failed_approaches=("treating callback text as authority",),
        successful_resolution="Escalated until authority was independently verified.",
        decision_lessons=("Do not allow action from callback text alone.",),
        scope_limits=("Only applies to partner action review with payment-change risk.",),
        non_generalization_conditions=("Does not apply when formal policy grants auto-allow.",),
        related_policy_refs=("policy.payment.change.v1#verify-authority",),
        evidence_refs=("object://cases/payment-change-near-miss.json#sha256:casehash",),
        status=status,
        superseded_by=superseded_by,
    )


def test_locked_profile_manifest_loads():
    manifest = json.loads(PROFILE_MANIFEST.read_text())

    assert manifest["schema_version"] == "holo.architecture_profiles.v1"
    assert manifest["manifest_version"] == "2026-06-25.1"
    profile = manifest["profiles"]["frontier_holo_optimized_opus_gpt55_v1"]
    assert profile == {
        "profile_id": "frontier_holo_optimized_opus_gpt55_v1",
        "profile_version": "v1",
        "status": "locked",
        "runtime_class": "frontier_holo_optimized",
        "builder_alignment": "patent_aligned_v4",
        "registry_mode": "full_registry",
        "governor_lane": "HoloGov-B",
        "runtime_behavior": "manifest_controls_runtime_selection",
        "pool_strategy": "frontier_ordered_full_registry",
        "active_provider_order": ["xai", "openai", "minimax"],
        "governor_provider": "openai",
    }


def test_hologov_memory_doctrine_locked():
    text = DOCTRINE.read_text()

    assert "Version: `0.1`" in text
    assert "Status: `locked`" in text
    assert "Effective date: `2026-06-25`" in text
    assert "Supersedes: `none`" in text
    assert "Superseded by: `none`" in text
    assert "HoloBrain is the overarching memory and intelligence infrastructure" in text
    assert "near-lossless at the reference and audit layer" in text
    assert "not at the prompt-injection layer" in text
    assert "Future modifications to this doctrine must create a new version" in text


def test_holobrain_roster_locked():
    text = ROSTER.read_text()

    assert "Version: `0.1`" in text
    assert "Status: `locked`" in text
    assert "Effective date: `2026-06-25`" in text
    assert "Governing doctrine: `holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md`" in text
    for agent in (
        "HoloScribe",
        "HoloPrune",
        "HoloThread",
        "HoloSentinel",
        "HoloScope",
        "HoloLedger",
    ):
        assert f"### {agent}" in text
    assert "HoloWeaver" not in text
    assert "may not silently rewrite truth" in text
    assert "No HoloBrain maintenance agent may auto-modify" in text


def test_no_raw_trace_default_payload_rule():
    doctrine_text = DOCTRINE.read_text()

    assert "HoloBrain should not store raw trace dumps as default memory payload" in doctrine_text
    assert "Raw traces should remain referenced substrate" in doctrine_text
    assert_no_raw_trace_default_payload({"summary": "compact", "artifact_ref": "sha256:abc"})
    with pytest.raises(ValueError, match="referenced substrate only"):
        assert_no_raw_trace_default_payload(
            {"summary": "compact", "raw_trace_dump": "provider transcript"}
        )


def test_policy_object_retrieval_slice():
    slice_ = build_retrieval_slice(
        lane="HoloGov-V",
        domain="partner_action_review",
        policies=(_policy(), _policy(status="superseded", superseded_by="policy.v2")),
        cases=(),
    )

    assert slice_.live_injection["policy_clauses"] == (
        {
            "policy_id": "policy.payment.change.v1",
            "clause_id": "verify-authority",
            "operative_text": "Verify authority before approving the action.",
            "source_ref": "policy.payment.change.v1#verify-authority",
        },
    )
    assert slice_.referenced_substrate["policy_refs"] == (
        "object://policies/payment-change-v1.md#sha256:policyhash",
    )
    assert slice_.audit.retrieved_policy_ids == ("policy.payment.change.v1",)
    assert slice_.audit.suppressed_policy_ids == ("policy.payment.change.v1",)


def test_case_experience_scope_limits():
    case = _case()

    assert case.scope_limits == (
        "Only applies to partner action review with payment-change risk.",
    )
    assert case.non_generalization_conditions == (
        "Does not apply when formal policy grants auto-allow.",
    )
    with pytest.raises(ValueError, match="scope_limits"):
        CaseExperience(
            case_id="case.unscoped",
            lane_scope=("HoloGov-B",),
            domain="partner_action_review",
            case_type="diagnostic",
            confidence="low",
            summary="Too broad.",
            trigger_pattern=("broad pattern",),
            failed_approaches=("none",),
            successful_resolution="none",
            decision_lessons=("none",),
            scope_limits=(),
            non_generalization_conditions=("none",),
            related_policy_refs=(),
            evidence_refs=(),
        )


def test_retrieval_injection_audit_record():
    slice_ = build_retrieval_slice(
        lane="HoloGov-B",
        domain="partner_action_review",
        policies=(_policy(),),
        cases=(_case(),),
    )

    assert slice_.audit.lane == "HoloGov-B"
    assert slice_.audit.domain == "partner_action_review"
    assert slice_.audit.injected_policy_clause_ids == (
        "policy.payment.change.v1#verify-authority",
    )
    assert slice_.audit.injected_case_ids == ("case.payment-change.near-miss.v1",)
    assert slice_.audit.referenced_substrate_refs == (
        "object://policies/payment-change-v1.md#sha256:policyhash",
        "object://cases/payment-change-near-miss.json#sha256:casehash",
    )


def test_maintenance_candidate_queue_no_promotion():
    candidate = MaintenanceCandidate(
        agent_name="HoloThread",
        proposal_type="supersession_candidate",
        target_ref="case.payment-change.near-miss.v1",
        proposed_change={"superseded_by": "case.payment-change.near-miss.v2"},
    )

    assert candidate.approval_status == "queued"
    assert candidate.can_silently_promote_truth is False
    with pytest.raises(PermissionError, match="explicit approval"):
        promote_maintenance_candidate(candidate)


def test_policy_case_authority_ladder():
    policy = _policy()
    case = _case()

    assert highest_authority((case, policy)) is policy


def test_bv_near_lossless_reference_audit_not_prompt():
    for lane in ("HoloGov-B", "HoloGov-V"):
        contract = lane_fidelity_contract(lane)
        assert contract.reference_audit_fidelity == "near_lossless"
        assert contract.prompt_injection == "compact_operational_slice"
        assert contract.full_corpus_injected is False
        assert contract.lossless_by_default_fields

    compact_contract = lane_fidelity_contract("HoloGov-C")
    assert compact_contract.reference_audit_fidelity == "compact"
    assert compact_contract.prompt_injection == "rolling_summary"
