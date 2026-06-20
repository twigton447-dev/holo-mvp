from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from holo_builder.freeze_manifest import compute_payload_hash, payload_visibility_errors
from holo_builder.lint import check as lint_check


INVENTORY_PATH = Path("reports/BAL100_LEADERBOARD_20_ALLOW_CANDIDATE_INVENTORY_001.json")
DEFAULT_OUT_DIR = Path("holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance")
DEFAULT_JSON_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_MIGRATED_DRAFTS_001.json")
DEFAULT_MD_OUT = Path("reports/BAL100_LEADERBOARD_20_ALLOW_MIGRATED_DRAFTS_001.md")


STRICT_MODEL_VISIBLE_FORBIDDEN_TERMS = (
    "BUILD_STATE_OBJECT",
    "VERIFY_STATE_OBJECT",
    "builder BatonPass",
    "GovState",
    "HoloGov",
    "expected_verdict",
    "hidden_ground_truth",
    "scoring_targets",
    "proof-credit",
    "BAL100-LEADERBOARD",
    "correct verdict",
)

LOUD_LABEL_TERMS = (
    "approved_to_release",
    "no_blocker",
    "expected ALLOW",
    "expected ESCALATE",
    "known good",
    "answer key",
)


SCENARIO_ID_MAP = {
    "HAB-001_v5": "BAL100-HARD-ALLOW-HAB-001-ALLOW",
    "HAB-003_v2": "BAL100-HARD-ALLOW-HAB-003-ALLOW",
    "HAB-004_v1": "BAL100-HARD-ALLOW-HAB-004-ALLOW",
    "HAB-005_v1": "BAL100-HARD-ALLOW-HAB-005-ALLOW",
    "HAB-006_v1": "BAL100-HARD-ALLOW-HAB-006-ALLOW",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _payload_text(packet: dict[str, Any]) -> str:
    return json.dumps(packet.get("payload", {}), sort_keys=True, ensure_ascii=True)


def _contamination_audit(packet: dict[str, Any]) -> dict[str, Any]:
    text = _payload_text(packet)
    strict_hits = [term for term in STRICT_MODEL_VISIBLE_FORBIDDEN_TERMS if term.lower() in text.lower()]
    loud_hits = [term for term in LOUD_LABEL_TERMS if term.lower() in text.lower()]
    return {
        "status": "PASS" if not strict_hits and not loud_hits else "FAIL",
        "strict_forbidden_hits": strict_hits,
        "loud_label_hits": loud_hits,
        "note": "Risk/advisory language is allowed when it is domain evidence rather than answer-key labeling.",
    }


def _doc_from_email(email: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "doc_id": f"EMAIL-{index:02d}",
        "type": "email_record",
        "from": email.get("from"),
        "to": email.get("to"),
        "date": email.get("date"),
        "subject": email.get("subject"),
        "body": email.get("body"),
        **({"sender_title": email["sender_title"]} if email.get("sender_title") else {}),
    }


def _doc_from_policy(policy: dict[str, Any], index: int) -> dict[str, Any]:
    doc = deepcopy(policy)
    doc.setdefault("doc_id", f"POLICY-{index:02d}")
    doc.setdefault("type", "policy_document")
    return doc


def _doc_from_attachment(attachment: dict[str, Any], index: int) -> dict[str, Any]:
    doc = deepcopy(attachment)
    doc.setdefault("doc_id", attachment.get("filename", f"ATTACHMENT-{index:02d}"))
    doc.setdefault("type", attachment.get("type", "attachment_record"))
    return doc


def _doc_from_telemetry(telemetry: dict[str, Any], index: int) -> dict[str, Any]:
    data = telemetry.get("data", {})
    return {
        "doc_id": data.get("ticket_id") or data.get("doc_id") or f"TELEMETRY-{index:02d}",
        "type": telemetry.get("data_type", "telemetry_record"),
        "system": telemetry.get("system"),
        "retrieved_at": telemetry.get("retrieved_at"),
        "data": deepcopy(data),
    }


def _ensure_payment_email_action(packet: dict[str, Any]) -> None:
    action = packet["payload"]["action"]
    if packet.get("domain") == "IAM":
        action.setdefault("vendor", "Apex Corp Identity and Access Management")
        action.setdefault("amount", "not_applicable_access_request")
        action.setdefault("currency", "N/A")
        action.setdefault("payment_method", "access_control_request")
    action.setdefault("payment_hold", False)


def _build_internal_documents(source: dict[str, Any], candidate: dict[str, Any]) -> list[dict[str, Any]]:
    context = source["payload"]["context"]
    docs: list[dict[str, Any]] = []

    for doc in context.get("internal_documents", []):
        docs.append(deepcopy(doc))
    for index, attachment in enumerate(context.get("attachments", []), start=1):
        docs.append(_doc_from_attachment(attachment, index))
    for index, telemetry in enumerate(context.get("parallel_telemetry", []), start=1):
        docs.append(_doc_from_telemetry(telemetry, index))
    for index, email in enumerate(context.get("email_thread", []), start=1):
        docs.append(_doc_from_email(email, index))
    for index, policy in enumerate(context.get("policy_documents", []), start=1):
        docs.append(_doc_from_policy(policy, index))

    # Deduplicate by doc_id while preserving order.
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for doc in docs:
        doc_id = str(doc.get("doc_id") or f"DOC-{len(deduped)+1:02d}")
        if doc_id in seen:
            doc = {**doc, "doc_id": f"{doc_id}-COPY-{len(deduped)+1:02d}"}
            doc_id = doc["doc_id"]
        seen.add(doc_id)
        deduped.append(doc)

    min_docs = 3 if source.get("domain") == "IAM" else 5
    if len(deduped) < min_docs:
        deduped.append(
            {
                "doc_id": f"MIGRATION-EVIDENCE-{candidate['candidate_id']}",
                "type": "migration_document_index",
                "content": "Builder-only migration converted existing source records into BAL100 internal_documents without changing payload truth.",
                "source_packet": candidate["source_packet"],
            }
        )
    return deduped


def _migrate_candidate(candidate: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    source_path = Path(candidate["source_packet"])
    source = _load_json(source_path)
    migrated = deepcopy(source)
    scenario_id = SCENARIO_ID_MAP[candidate["candidate_id"]]
    migrated["scenario_id"] = scenario_id
    migrated["scenario_set_version"] = "bal100-leaderboard-20-hard-allow-balance-v0.1"
    migrated["payload_revision"] = 1
    migrated["draft_status"] = "bal100_hard_allow_migration_draft_no_live"
    migrated["_builder"] = {
        "spec_target_verdict": "ALLOW",
        "spec_packet_format": "payment_email",
        "spec_minimum_internal_documents": 3 if source.get("domain") == "IAM" else 5,
        "source_packet": candidate["source_packet"],
        "source_audit_packet": candidate["audit_packet"],
        "source_candidate_id": candidate["candidate_id"],
        "source_eval_id": candidate["eval_id"],
        "source_suite_status": candidate["suite_status"],
        "ticket_id": "BAL100-LEADERBOARD-20-ALLOW-BALANCE-001",
        "state_object_used": "BUILD_STATE_OBJECT",
        "verify_state_object_isolation": "Do not pass BUILD_STATE_OBJECT or builder BatonPass into runtime HV/HoloGov.",
        "diagnostic_seam": candidate["seam"],
        "false_positive_trap": candidate["false_positive_trap"],
        "draft_note": "No-live migrated draft only. Not frozen. Not proof credit. HV/Judge owns adjudication truth after approved intake.",
    }
    _ensure_payment_email_action(migrated)
    migrated["payload"]["context"]["internal_documents"] = _build_internal_documents(source, candidate)

    out_path = out_dir / f"{scenario_id}_draft_v0_1.json"
    _write_json(out_path, migrated)
    lint_result = lint_check(migrated)
    visibility_errors = payload_visibility_errors(migrated)
    contamination = _contamination_audit(migrated)
    payload_hash = compute_payload_hash(migrated)
    return {
        "candidate_id": candidate["candidate_id"],
        "scenario_id": scenario_id,
        "domain": migrated.get("domain"),
        "source_packet": candidate["source_packet"],
        "draft_packet": str(out_path),
        "payload_hash": payload_hash,
        "hash8": payload_hash[:8],
        "hb_lint": {
            "status": "PASS" if lint_result.passed else "FAIL",
            "errors": lint_result.errors,
            "warnings": lint_result.warnings,
        },
        "payload_visibility_result": "PASS" if not visibility_errors else "FAIL",
        "payload_visibility_errors": visibility_errors,
        "contamination_audit": contamination,
        "ready_for_freeze_manifest_preflight": lint_result.passed and not visibility_errors and contamination["status"] == "PASS",
    }


def build_migrated_drafts(inventory_path: Path, out_dir: Path) -> dict[str, Any]:
    inventory = _load_json(inventory_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    selected = [row for row in inventory["inventory"] if row["selection"] == "selected"]
    rows = [_migrate_candidate(row, out_dir) for row in selected]
    validation_failures = []
    if len(rows) != 5:
        validation_failures.append("expected exactly five migrated drafts")
    if any(row["hb_lint"]["status"] != "PASS" for row in rows):
        validation_failures.append("one or more migrated drafts failed HB lint")
    if any(row["payload_visibility_result"] != "PASS" for row in rows):
        validation_failures.append("one or more migrated drafts failed payload visibility")
    if any(row["contamination_audit"]["status"] != "PASS" for row in rows):
        validation_failures.append("one or more migrated drafts failed contamination audit")

    return {
        "artifact_type": "BAL100_leaderboard_20_allow_migrated_drafts",
        "created_at": _utc_now(),
        "status": "PASS" if not validation_failures else "FAIL",
        "mode": "no_live_migrated_draft_generation_and_static_lint",
        "ticket_id": inventory["ticket_id"],
        "source_inventory": str(inventory_path),
        "out_dir": str(out_dir),
        "draft_count": len(rows),
        "drafts": rows,
        "validation": {
            "failures": validation_failures,
            "all_hb_lint_pass": all(row["hb_lint"]["status"] == "PASS" for row in rows),
            "all_payload_visibility_pass": all(row["payload_visibility_result"] == "PASS" for row in rows),
            "all_contamination_audit_pass": all(row["contamination_audit"]["status"] == "PASS" for row in rows),
            "all_ready_for_freeze_manifest_preflight": all(row["ready_for_freeze_manifest_preflight"] for row in rows),
        },
        "safe_boundaries": {
            "provider_calls": False,
            "freeze": False,
            "judge": False,
            "official_trace": False,
            "qa": False,
            "ablation": False,
            "scorecard_movement": False,
            "leaderboard_update": False,
            "push": False,
            "packet_promotion": False,
            "proof_credit_status_change": False,
        },
        "next_step": "If Taylor approves static preflight only, run freeze-manifest on these exact five draft paths and stop before freeze.",
    }


def build_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# BAL100 Leaderboard 20 ALLOW Migrated Drafts",
        "",
        f"Status: {report['status']}  ",
        f"Created: {report['created_at']}  ",
        f"Ticket: `{report['ticket_id']}`  ",
        "Mode: no-live migrated draft generation and static lint",
        "",
        "## Drafts",
        "",
        "| Candidate | Scenario ID | Domain | Lint | Visibility | Contamination | Hash8 | Draft Path |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in report["drafts"]:
        lines.append(
            f"| `{row['candidate_id']}` | `{row['scenario_id']}` | {row['domain']} | {row['hb_lint']['status']} | {row['payload_visibility_result']} | {row['contamination_audit']['status']} | `{row['hash8']}` | `{row['draft_packet']}` |"
        )
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- Draft count: {report['draft_count']}",
            f"- All HB lint pass: {report['validation']['all_hb_lint_pass']}",
            f"- All payload visibility pass: {report['validation']['all_payload_visibility_pass']}",
            f"- All contamination audit pass: {report['validation']['all_contamination_audit_pass']}",
            f"- All ready for freeze-manifest preflight: {report['validation']['all_ready_for_freeze_manifest_preflight']}",
            f"- Failures: {report['validation']['failures'] or 'none'}",
            "",
            "## Next Step",
            "",
            report["next_step"],
            "",
            "## Safe Boundaries",
            "",
            "No provider calls, freeze, Judge, official trace, QA, ablation, scorecard movement, leaderboard update, packet promotion, proof-credit status change, or push were authorized or performed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create no-live BAL100/HB migrated drafts from selected hard-ALLOW source candidates.")
    parser.add_argument("--inventory", type=Path, default=INVENTORY_PATH)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD_OUT)
    args = parser.parse_args()

    report = build_migrated_drafts(args.inventory, args.out_dir)
    _write_json(args.json_out, report)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.write_text(build_markdown(report))
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    print(f"status {report['status']}")
    print(f"drafts {report['draft_count']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
