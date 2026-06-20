from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path(
    "benchmark_factory/batches/BAL100_LEADERBOARD_20_allow_balance_govstate_batonpass_config.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_status(source_evidence: dict[str, str]) -> list[dict[str, Any]]:
    rows = []
    for key, raw_path in source_evidence.items():
        path = Path(raw_path)
        rows.append(
            {
                "source": key,
                "path": raw_path,
                "exists": path.exists(),
                "sha256": _sha256(path),
            }
        )
    return rows


def _safe_boundaries_pass(gov_state: dict[str, Any], status: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    blocked = (
        "provider_calls",
        "freeze",
        "judge",
        "official_trace",
        "qa",
        "ablation",
        "scorecard_movement",
        "leaderboard_update",
        "push",
    )
    for key in blocked:
        if status.get(key) is not False:
            failures.append(f"status.{key} is not false")
        if gov_state.get("safe_boundaries", {}).get(key) is not False:
            failures.append(f"gov_state.safe_boundaries.{key} is not false")
    return not failures, failures


def _visibility_contract_pass(baton_pass: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    contract = baton_pass.get("payload_visibility_contract", {})
    visible = contract.get("model_visible_future_packet_keys", [])
    builder_only = set(contract.get("builder_only_keys", []))
    required_builder_only = {
        "BUILD_STATE_OBJECT",
        "builder_baton_pass",
        "expected_verdict",
        "expected_reason",
        "hidden_ground_truth",
        "scoring_targets",
        "gov_state",
        "baton_pass",
        "hologov_decision",
        "hologov_build_decision",
        "proof_credit_status",
        "ticket_id",
        "_builder",
        "_internal",
        "_frozen",
    }
    if visible != ["action", "context"]:
        failures.append("model_visible_future_packet_keys must be exactly ['action', 'context']")
    missing = sorted(required_builder_only - builder_only)
    if missing:
        failures.append(f"builder_only_keys missing {missing}")
    return not failures, failures


def _state_architecture_pass(config: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    architecture = config.get("state_object_architecture", {})
    build_state = architecture.get("build_state_object", {})
    verify_state = architecture.get("verify_state_object", {})
    baton_pass = config.get("baton_pass", {})
    gov_state = config.get("gov_state", {})

    if build_state.get("name") != "BUILD_STATE_OBJECT":
        failures.append("build_state_object.name must be BUILD_STATE_OBJECT")
    if verify_state.get("name") != "VERIFY_STATE_OBJECT":
        failures.append("verify_state_object.name must be VERIFY_STATE_OBJECT")
    derivation = verify_state.get("derivation_rule", "")
    if "payload.action" not in derivation or "payload.context" not in derivation:
        failures.append("verify_state_object.derivation_rule must cite payload.action and payload.context")
    if "BUILD_STATE_OBJECT" not in architecture.get("isolation_rule", ""):
        failures.append("isolation_rule must explicitly name BUILD_STATE_OBJECT")
    if not baton_pass.get("adversarial_role"):
        failures.append("baton_pass.adversarial_role is required")
    if not baton_pass.get("focus_areas"):
        failures.append("baton_pass.focus_areas is required")
    if not baton_pass.get("unresolved_tensions"):
        failures.append("baton_pass.unresolved_tensions is required")
    if not gov_state.get("repair_ledger"):
        failures.append("gov_state.repair_ledger is required")
    if not gov_state.get("artifact_registry_policy"):
        failures.append("gov_state.artifact_registry_policy is required")
    if not gov_state.get("state_audit_policy"):
        failures.append("gov_state.state_audit_policy is required")
    if "Judge owns adjudication truth" not in gov_state.get("authority", ""):
        failures.append("gov_state.authority must clarify Judge owns adjudication truth")
    return not failures, failures


def build_report(config_path: Path) -> dict[str, Any]:
    config = _load_json(config_path)
    source_rows = _source_status(config.get("source_evidence", {}))
    missing_sources = [row["path"] for row in source_rows if not row["exists"]]
    safe_ok, safe_failures = _safe_boundaries_pass(config["gov_state"], config["status"])
    visibility_ok, visibility_failures = _visibility_contract_pass(config["baton_pass"])
    state_arch_ok, state_arch_failures = _state_architecture_pass(config)
    seed_queue = config["baton_pass"].get("candidate_seed_queue", [])
    role_contract = config["baton_pass"].get("role_contract", [])

    validation_failures = []
    validation_failures.extend(safe_failures)
    validation_failures.extend(visibility_failures)
    validation_failures.extend(state_arch_failures)
    if missing_sources:
        validation_failures.append(f"missing source artifacts: {missing_sources}")
    if len(seed_queue) < config["gov_state"]["leaderboard_state"]["additional_allow_packets_needed"]:
        validation_failures.append("candidate seed queue has fewer entries than additional ALLOW packets needed")
    if len(role_contract) < 5:
        validation_failures.append("baton pass role contract must cover at least five harness roles")

    return {
        "artifact_type": "BAL100_leaderboard_20_allow_balance_govstate_batonpass",
        "created_at": _utc_now(),
        "config_path": str(config_path),
        "ticket_id": config["ticket_id"],
        "status": "PASS" if not validation_failures else "FAIL",
        "validation": {
            "planning_only": config["status"].get("planning_only") is True,
            "source_artifacts": source_rows,
            "missing_source_artifacts": missing_sources,
            "safe_boundaries_pass": safe_ok,
            "payload_visibility_contract_pass": visibility_ok,
            "state_object_architecture_pass": state_arch_ok,
            "candidate_seed_queue_count": len(seed_queue),
            "role_contract_count": len(role_contract),
            "failures": validation_failures,
        },
        "state_object_architecture": config["state_object_architecture"],
        "gov_state": config["gov_state"],
        "baton_pass": config["baton_pass"],
        "harness_readiness": config["harness_readiness"],
        "safe_boundaries": config["gov_state"]["safe_boundaries"],
        "next_no_live_outputs": config["baton_pass"]["next_no_live_outputs"],
    }


def _md_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = ["| Source | Path | Exists | SHA256 |", "|---|---|---:|---|"]
    for row in rows:
        sha = row.get("sha256") or ""
        lines.append(f"| {row['source']} | `{row['path']}` | {row['exists']} | `{sha[:16]}` |")
    return lines


def build_markdown(report: dict[str, Any]) -> str:
    gov_state = report["gov_state"]
    baton_pass = report["baton_pass"]
    architecture = report["state_object_architecture"]
    leaderboard = gov_state["leaderboard_state"]
    validation = report["validation"]
    lines = [
        "# BAL100 Leaderboard 20 ALLOW Balance - GovState/BatonPass",
        "",
        f"Status: {report['status']}  ",
        f"Ticket: `{report['ticket_id']}`  ",
        f"Created: {report['created_at']}  ",
        "Mode: no-live planning only",
        "",
        "## Objective",
        "",
        gov_state["objective"],
        "",
        "## Patent-Aligned State Object Architecture",
        "",
        architecture["single_source_of_truth_rule"],
        "",
        f"- Build lane: `{architecture['build_state_object']['name']}` for {architecture['build_state_object']['lane']}.",
        f"- Verify lane: `{architecture['verify_state_object']['name']}` for {architecture['verify_state_object']['lane']}.",
        f"- Runtime HV derivation rule: {architecture['verify_state_object']['derivation_rule']}",
        f"- Isolation rule: {architecture['isolation_rule']}",
        "",
        "## Leaderboard State",
        "",
        "| Metric | Current | Target |",
        "|---|---:|---:|",
        f"| Total packets | {leaderboard['current_total_packets']} | {leaderboard['target_total_packets']} |",
        f"| ALLOW packets | {leaderboard['current_allow_packets']} | {leaderboard['target_allow_packets']} |",
        f"| ESCALATE packets | {leaderboard['current_escalate_packets']} | {leaderboard['target_escalate_packets']} |",
        f"| HoloGov FPR | {leaderboard['current_hologov_fpr']} | {leaderboard['target_hologov_fpr']} |",
        f"| HoloGov FNR | {leaderboard['current_hologov_fnr']} | {leaderboard['target_hologov_fnr']} |",
        "",
        "## GovState Decision",
        "",
        f"- Authority: {gov_state['authority']}",
        f"- Primary path: {gov_state['selected_strategy']['primary_path']}",
        f"- Secondary path: {gov_state['selected_strategy']['secondary_path']}",
        f"- Deferred path: {gov_state['selected_strategy']['deferred_path']}",
        f"- Stage readiness: {gov_state['stage_readiness_policy']['hologov_role']}; {gov_state['stage_readiness_policy']['judge_role']}; {gov_state['stage_readiness_policy']['proof_credit_rule']}",
        "",
        "## BatonPass Contract",
        "",
        baton_pass["handoff_summary"],
        "",
        "### BatonPass Focus",
        "",
        f"- Next agent: `{baton_pass['next_agent']}`",
        f"- Adversarial role: `{baton_pass['adversarial_role']}`",
        "",
        "Focus areas:",
        "",
    ]
    for focus in baton_pass["focus_areas"]:
        lines.append(f"- {focus}")
    lines.extend(
        [
            "",
            "Unresolved tensions:",
            "",
        ]
    )
    for tension in baton_pass["unresolved_tensions"]:
        lines.append(f"- {tension}")
    lines.extend(
        [
            "",
            "### Role Contract",
            "",
        ]
    )
    for role in baton_pass["role_contract"]:
        lines.append(f"- `{role['role']}`: {role['instruction']}")
    lines.extend(
        [
            "",
            "### Payload Visibility Contract",
            "",
            "- Future solo-model packet keys: `action`, `context` only.",
            "- BUILD_STATE_OBJECT, builder BatonPass, expected verdicts, HoloGov build decisions, ticket IDs, proof-credit status, and candidate-lane labels are builder-only.",
            "- HoloBuilder may use build-state data for generation and validation, but must not place it in prompt cards, frozen model-visible payloads, runtime HV/HoloGov VERIFY_STATE_OBJECT, or official trace model-visible state.",
            "",
            "## Candidate Seed Queue",
            "",
            "| Candidate | EVAL | Domain | Status | Reason To Consider |",
            "|---|---|---|---|---|",
        ]
    )
    for candidate in baton_pass["candidate_seed_queue"]:
        lines.append(
            "| {candidate_id} | {eval_id} | {domain} | {status} | {reason_to_consider} |".format(
                **candidate
            )
        )
    lines.extend(
        [
            "",
            "## Evidence-Binding Requirements",
            "",
        ]
    )
    for requirement in baton_pass["evidence_binding_requirements"]:
        lines.append(f"- {requirement}")
    lines.extend(
        [
            "",
            "## Repair Ledger",
            "",
            "| Issue | Status | Desired Repair |",
            "|---|---|---|",
        ]
    )
    for issue in gov_state["repair_ledger"]:
        lines.append(f"| {issue['issue_id']} | {issue['status']} | {issue['desired_repair']} |")
    lines.extend(
        [
            "",
            "## Artifact Registry And State Audit",
            "",
            f"- Artifact registry rule: {gov_state['artifact_registry_policy']['rule']}",
            f"- State audit required before stage transition: {gov_state['state_audit_policy']['required_before_stage_transition']}",
            "",
            "State audit checks:",
            "",
        ]
    )
    for check in gov_state["state_audit_policy"]["checks"]:
        lines.append(f"- {check}")
    lines.extend(
        [
            "",
            "## Contamination Cues To Avoid",
            "",
        ]
    )
    for cue in baton_pass["contamination_cues_to_avoid"]:
        lines.append(f"- {cue}")
    lines.extend(
        [
            "",
            "## Stop Rules",
            "",
        ]
    )
    for rule in gov_state["stop_rules"]:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Source Artifact Check",
            "",
            *_md_table(validation["source_artifacts"]),
            "",
            "## Validation",
            "",
            f"- Safe boundaries pass: {validation['safe_boundaries_pass']}",
            f"- Payload visibility contract pass: {validation['payload_visibility_contract_pass']}",
            f"- State object architecture pass: {validation['state_object_architecture_pass']}",
            f"- Candidate seed queue count: {validation['candidate_seed_queue_count']}",
            f"- Role contract count: {validation['role_contract_count']}",
        ]
    )
    if validation["failures"]:
        lines.append("- Failures:")
        for failure in validation["failures"]:
            lines.append(f"  - {failure}")
    else:
        lines.append("- Failures: none")
    lines.extend(
        [
            "",
            "## Safe Boundaries",
            "",
            "This artifact does not authorize provider calls, freeze, Judge, official trace, QA, ablation, scorecard movement, leaderboard update, packet promotion, proof-credit status change, push, or any live transmission.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build no-live GovState/BatonPass artifacts for the BAL100 leaderboard-to-20 ALLOW balance ticket."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()

    config = _load_json(args.config)
    report = build_report(args.config)
    outputs = config["report_outputs"]
    json_out = Path(outputs["json"])
    md_out = Path(outputs["markdown"])
    _write_json(json_out, report)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(build_markdown(report))
    print(f"wrote {json_out}")
    print(f"wrote {md_out}")
    print(f"status {report['status']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
