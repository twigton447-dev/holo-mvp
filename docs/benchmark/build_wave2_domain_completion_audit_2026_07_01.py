#!/usr/bin/env python3
"""Build a no-provider completion audit for Wave 2 domain consolidation."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTROL_ROOT = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01"
OUT_JSON = CONTROL_ROOT / "WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.json"
OUT_MD = CONTROL_ROOT / "WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.md"

CONTROL_ROOM = CONTROL_ROOT / "WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json"
VALIDATION = CONTROL_ROOT / "WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.json"
PRESERVATION = CONTROL_ROOT / "WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
SELECTIVE_STAGING_PLAN = CONTROL_ROOT / "WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json"
STATISTICAL_GUARDRAIL = CONTROL_ROOT / "WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json"
OPERATOR_HANDOFF = CONTROL_ROOT / "WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json"
READINESS = REPO_ROOT / "docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha256_text(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True) + "\n")


def requirement(requirements: list[dict[str, Any]], req_id: str, status: str, evidence: Any, note: str) -> None:
    requirements.append({"evidence": evidence, "note": note, "requirement_id": req_id, "status": status})


def build_audit() -> dict[str, Any]:
    control = read_json(CONTROL_ROOM)
    validation = read_json(VALIDATION)
    preservation = read_json(PRESERVATION)
    selective_staging = read_json(SELECTIVE_STAGING_PLAN)
    statistical_guardrail = read_json(STATISTICAL_GUARDRAIL)
    operator_handoff = read_json(OPERATOR_HANDOFF)
    readiness = read_json(READINESS)
    state = control["current_state"]
    batch004 = control["gates"]["batch004"]
    batch005 = control["gates"]["batch005"]
    requirements: list[dict[str, Any]] = []

    requirement(
        requirements,
        "consolidate_current_threads_into_single_control_surface",
        "ACHIEVED",
        {"control_room_status": control["status"], "control_room_sha256": control["package_sha256"]},
        "The control room is the current single no-provider front door.",
    )
    requirement(
        requirements,
        "account_for_batch003_finished_state",
        "ACHIEVED",
        {
            "current_scored_packets": state["current_scored_packets"],
            "current_scored_pairs": state["current_scored_pairs"],
            "scored_batches": state["scored_batches"],
        },
        "Batches 001-003 are represented as the completed scored base.",
    )
    requirement(
        requirements,
        "preserve_new_domain_packet_staging",
        "ACHIEVED",
        {
            "batch004_pairs": batch004["pair_count"],
            "batch005_pairs": batch005["pair_count"],
            "domain_rows": control["domain_rows"],
        },
        "Batch004 closes the selected-target pool; Batch005 stages the full-family remainder.",
    )
    requirement(
        requirements,
        "statistical_significance_path_is_explicit",
        "ACHIEVED",
        {
            "current_per_class_n": state["current_per_class_n"],
            "per_class_n_after_clean_batch004": state["per_class_n_after_clean_batch004"],
            "per_class_n_after_clean_batch004_and_batch005": state[
                "per_class_n_after_clean_batch004_and_batch005"
            ],
            "statistical_claim_guardrail_sha256": statistical_guardrail["package_sha256"],
            "statistical_claim_guardrail_status": statistical_guardrail["status"],
            "statistical_proof_claim": statistical_guardrail["claim_boundary"]["statistical_proof_claim"],
            "wave2_current_claim": statistical_guardrail["claim_boundary"]["current_claim"],
        },
        "The statistical guardrail enforces selected-target evidence as distinct from full-family statistical proof.",
    )
    requirement(
        requirements,
        "all_domains_ordered_for_completion",
        "ACHIEVED_NO_PROVIDER",
        {
            "batch005_state": batch005["state"],
            "unstaged_full_family_pairs": sum(
                row["unstaged_full_family_pairs_after_batch005"] for row in control["domain_rows"]
            ),
        },
        "All frozen domain pairs are either scored or staged, but full-family proof still needs future live evidence.",
    )
    requirement(
        requirements,
        "provider_boundary_remains_closed",
        "ACHIEVED",
        {
            "control_room_provider_calls": control["summary"]["provider_calls_made_by_builder"],
            "selective_staging_provider_calls": selective_staging["summary"]["provider_calls_made_by_plan"],
            "statistical_guardrail_provider_calls": statistical_guardrail["summary"]["provider_calls_made_by_guardrail"],
            "validation_provider_calls": validation["summary"]["provider_calls_made_by_validation"],
            "preservation_provider_calls": preservation["summary"]["provider_calls_made_by_manifest"],
        },
        "This consolidation lane made no provider calls.",
    )
    requirement(
        requirements,
        "review_and_preservation_are_orderly",
        "ACHIEVED",
        {
            "dirty_paths": preservation["summary"]["tracked_or_untracked_path_count"],
            "other_dirty_paths": preservation["summary"]["other_dirty_path_count"],
            "safe_staging_policy": preservation["safe_staging_policy"],
            "selective_staging_path_count": selective_staging["summary"]["path_count"],
            "selective_staging_sha256": selective_staging["package_sha256"],
            "selective_staging_status": selective_staging["status"],
            "operator_handoff_sha256": operator_handoff["package_sha256"],
            "operator_handoff_status": operator_handoff["status"],
        },
        "The current dirty state is grouped for review with path-limited staging commands and a no-provider operator handoff.",
    )
    requirement(
        requirements,
        "all_domains_live_scored",
        "NOT_ACHIEVED_APPROVAL_GATED",
        {
            "batch004_approval_packet_sha256": batch004["approval_packet_sha256"],
            "batch004_state": batch004["state"],
            "batch005_blocked_by": batch005["live_execution_gate"].get("blocked_reason"),
            "batch005_state": batch005["state"],
            "ready_for_batch004_provider_approval": readiness["summary"]["ready_for_batch004_provider_approval"],
            "ready_for_batch005_provider_approval": readiness["summary"]["ready_for_batch005_provider_approval"],
        },
        "Completing all domains requires explicit Batch004 provider approval, then Batch004 comparison/promotion, then separate Batch005 approval.",
    )

    achieved = [row for row in requirements if row["status"].startswith("ACHIEVED")]
    blocked = [row for row in requirements if row["status"].startswith("NOT_ACHIEVED")]
    audit = {
        "classification": "WAVE2_DOMAIN_COMPLETION_AUDIT_NO_PROVIDER_2026_07_01",
        "completion_claim": "NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "generated_without_provider_calls": True,
        "next_required_gate": {
            "batch_id": "WAVE2_HOLO_TARGET_BATCH_004",
            "gate": "EXPLICIT_PROVIDER_APPROVAL_ONLY",
            "approval_packet_sha256": batch004["approval_packet_sha256"],
            "run_command_after_approval": batch004["run_command_after_explicit_approval"],
        },
        "package_sha256": "",
        "requirements": requirements,
        "source_paths": {
            "control_room": str(CONTROL_ROOM.relative_to(REPO_ROOT)),
            "operator_handoff": str(OPERATOR_HANDOFF.relative_to(REPO_ROOT)),
            "preservation_manifest": str(PRESERVATION.relative_to(REPO_ROOT)),
            "readiness": str(READINESS.relative_to(REPO_ROOT)),
            "selective_staging_plan": str(SELECTIVE_STAGING_PLAN.relative_to(REPO_ROOT)),
            "statistical_claim_guardrail": str(STATISTICAL_GUARDRAIL.relative_to(REPO_ROOT)),
            "validation": str(VALIDATION.relative_to(REPO_ROOT)),
        },
        "status": "PASS",
        "summary": {
            "achieved_or_no_provider_achieved": len(achieved),
            "not_achieved": len(blocked),
            "provider_calls_made_by_audit": 0,
            "requirements_total": len(requirements),
        },
    }
    audit["package_sha256"] = package_sha256(audit)
    return audit


def render_md(audit: dict[str, Any]) -> str:
    lines = [
        "# Wave 2 Domain Completion Audit",
        "",
        f"Status: `{audit['status']}`",
        f"Completion claim: `{audit['completion_claim']}`",
        f"Package SHA-256: `{audit['package_sha256']}`",
        f"Generated without provider calls: `{audit['generated_without_provider_calls']}`",
        "",
        "## Requirement Audit",
        "",
        "| Requirement | Status | Note |",
        "| --- | --- | --- |",
    ]
    for row in audit["requirements"]:
        lines.append(f"| `{row['requirement_id']}` | `{row['status']}` | {row['note']} |")
    gate = audit["next_required_gate"]
    lines.extend(
        [
            "",
            "## Next Required Gate",
            "",
            f"- Batch: `{gate['batch_id']}`",
            f"- Gate: `{gate['gate']}`",
            f"- Approval packet SHA-256: `{gate['approval_packet_sha256']}`",
            "",
            "```bash",
            gate["run_command_after_approval"],
            "```",
            "",
            "## Boundary",
            "",
            "This audit does not approve provider calls and does not mark all-domain live proof complete.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    audit = build_audit()
    write_json(OUT_JSON, audit)
    OUT_MD.write_text(render_md(audit))
    print(
        json.dumps(
            {
                "completion_claim": audit["completion_claim"],
                "json": str(OUT_JSON.relative_to(REPO_ROOT)),
                "md": str(OUT_MD.relative_to(REPO_ROOT)),
                "package_sha256": audit["package_sha256"],
                "provider_calls_made": 0,
                "status": audit["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
