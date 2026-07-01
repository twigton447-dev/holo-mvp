#!/usr/bin/env python3
"""Regression checks for the Wave 2 no-provider completion audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_ROOT = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01"
AUDIT = CONTROL_ROOT / "WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.json"
AUDIT_MD = AUDIT.with_suffix(".md")
CONTROL_ROOM = CONTROL_ROOT / "WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json"
STATISTICAL_GUARDRAIL = CONTROL_ROOT / "WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json"
BATCH005_APPROVAL = (
    REPO_ROOT
    / "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    / "holo_target_batches/wave2_holo_target_batch_005"
    / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)


def package_sha256(data: dict) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return hashlib.sha256((json.dumps(body, indent=2, sort_keys=True) + "\n").encode("utf-8")).hexdigest()


def main() -> int:
    audit = json.loads(AUDIT.read_text())
    control = json.loads(CONTROL_ROOM.read_text())
    statistical_guardrail = json.loads(STATISTICAL_GUARDRAIL.read_text())
    md = AUDIT_MD.read_text()

    assert audit["status"] == "PASS", audit
    assert audit["completion_claim"] == "NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED", audit
    assert audit["generated_without_provider_calls"] is True, audit
    assert package_sha256(audit) == audit["package_sha256"], audit["package_sha256"]
    assert audit["summary"]["provider_calls_made_by_audit"] == 0, audit["summary"]
    assert audit["summary"]["requirements_total"] == 8, audit["summary"]
    assert audit["summary"]["not_achieved"] == 1, audit["summary"]

    by_id = {row["requirement_id"]: row for row in audit["requirements"]}
    assert by_id["all_domains_live_scored"]["status"] == "NOT_ACHIEVED_APPROVAL_GATED", by_id
    assert by_id["all_domains_ordered_for_completion"]["status"] == "ACHIEVED_NO_PROVIDER", by_id
    assert by_id["provider_boundary_remains_closed"]["status"] == "ACHIEVED", by_id
    review = by_id["review_and_preservation_are_orderly"]["evidence"]
    assert review["operator_handoff_status"] == "PASS", review
    assert review["selective_staging_status"] == "PASS", review
    statistical = by_id["statistical_significance_path_is_explicit"]["evidence"]
    assert statistical["statistical_claim_guardrail_status"] == "PASS", statistical
    assert (
        statistical["wave2_current_claim"] == "SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF"
    ), statistical
    assert statistical["statistical_proof_claim"] == "NOT_ACHIEVED_BATCH005_NOT_RUN", statistical
    statistical_evidence = by_id["statistical_significance_path_is_explicit"]["evidence"]
    assert statistical_evidence["statistical_claim_guardrail_sha256"] == statistical_guardrail["package_sha256"], statistical_evidence
    assert statistical_evidence["statistical_claim_guardrail_status"] == "PASS", statistical_evidence
    assert (
        statistical_evidence["wave2_current_claim"]
        == "SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF"
    ), statistical_evidence
    assert statistical_evidence["statistical_proof_claim"] == "NOT_ACHIEVED_BATCH005_NOT_RUN", statistical_evidence
    provider_evidence = by_id["provider_boundary_remains_closed"]["evidence"]
    assert provider_evidence["statistical_guardrail_provider_calls"] == 0, provider_evidence
    assert audit["source_paths"]["statistical_claim_guardrail"] == str(STATISTICAL_GUARDRAIL.relative_to(REPO_ROOT)), audit

    gate = audit["next_required_gate"]
    batch004 = control["gates"]["batch004"]
    assert gate["batch_id"] == "WAVE2_HOLO_TARGET_BATCH_005", gate
    assert gate["gate"] == "CREATE_BATCH005_APPROVAL_PACKET_THEN_EXPLICIT_PROVIDER_APPROVAL", gate
    assert gate["approval_packet_sha256"] is None, gate
    assert gate["run_command_after_approval"] is None, gate
    assert batch004["approval_granted_by_packet"] is False, batch004
    assert control["gates"]["batch005"]["live_execution_gate"]["status"] == "PASS", control
    assert not BATCH005_APPROVAL.exists(), BATCH005_APPROVAL

    assert "Completion claim: `NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED`" in md, md
    assert "WAVE2_HOLO_TARGET_BATCH_005" in md, md
    assert "This audit does not approve provider calls" in md, md

    print(
        json.dumps(
            {
                "approval_packet_sha256": gate["approval_packet_sha256"],
                "completion_claim": audit["completion_claim"],
                "provider_calls_made": 0,
                "status": "PASS",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
