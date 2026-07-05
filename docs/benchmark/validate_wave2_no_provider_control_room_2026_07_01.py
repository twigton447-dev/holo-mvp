#!/usr/bin/env python3
"""Validate the Wave 2 domain control room without provider calls."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_ROOT = REPO_ROOT / "docs/benchmark"
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
BATCHES_ROOT = FREEZE_ROOT / "holo_target_batches"
CONTROL_ROOT = BENCHMARK_ROOT / "wave2_domain_control_room_2026_07_01"
OUT_JSON = CONTROL_ROOT / "WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.json"
OUT_MD = CONTROL_ROOT / "WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.md"

PYTHON_PARSE_FILES = [
    "docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
    "docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py",
    "docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py",
    "docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py",
    "docs/benchmark/test_wave2_batch004_provider_approval_gate_2026_07_01.py",
    "docs/benchmark/test_wave2_batch005_full_family_lock_2026_07_01.py",
    "docs/benchmark/test_wave2_domain_completion_audit_2026_07_01.py",
    "docs/benchmark/test_wave2_domain_control_room_2026_07_01.py",
    "docs/benchmark/test_wave2_domain_operator_handoff_2026_07_01.py",
    "docs/benchmark/test_wave2_domain_preservation_manifest_2026_07_01.py",
    "docs/benchmark/test_wave2_domain_selective_staging_plan_2026_07_01.py",
    "docs/benchmark/test_wave2_statistical_claim_guardrail_2026_07_01.py",
    "docs/benchmark/test_wave2_timestamp_insensitive_hashes_2026_07_01.py",
    "docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py",
    "docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
]

JSON_ARTIFACTS = {
    "batch004_approval_packet": (
        "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        "/holo_target_batches/wave2_holo_target_batch_004"
        "/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
    ),
    "batch004_live_preflight": (
        "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        "/holo_target_batches/wave2_holo_target_batch_004"
        "/WAVE2_HOLO_TARGET_BATCH_004_LIVE_PREFLIGHT_2026_07_01.json"
    ),
    "batch005_live_preflight": (
        "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        "/holo_target_batches/wave2_holo_target_batch_005"
        "/WAVE2_HOLO_TARGET_BATCH_005_LIVE_PREFLIGHT_2026_07_01.json"
    ),
    "combined_memo_001_002_003_004": (
        "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
        "/holo_target_batches/WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
    ),
    "control_room": "docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json",
    "domain_ledger": (
        "docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01"
        "/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.json"
    ),
    "ordering": (
        "docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01"
        "/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
    ),
    "operator_handoff": (
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json"
    ),
    "preservation": (
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
    ),
    "selective_staging_plan": (
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json"
    ),
    "statistical_claim_guardrail": (
        "docs/benchmark/wave2_domain_control_room_2026_07_01"
        "/WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json"
    ),
    "readiness": "docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json",
}

LOCAL_COMMANDS = [
    ["python3", "-B", "docs/benchmark/test_wave2_batch004_provider_approval_gate_2026_07_01.py"],
    ["python3", "-B", "docs/benchmark/test_wave2_batch005_full_family_lock_2026_07_01.py"],
    ["python3", "-B", "docs/benchmark/test_wave2_domain_control_room_2026_07_01.py"],
    ["python3", "-B", "docs/benchmark/test_wave2_domain_operator_handoff_2026_07_01.py"],
    ["python3", "-B", "docs/benchmark/test_wave2_domain_preservation_manifest_2026_07_01.py"],
    ["python3", "-B", "docs/benchmark/test_wave2_domain_selective_staging_plan_2026_07_01.py"],
    ["python3", "-B", "docs/benchmark/test_wave2_statistical_claim_guardrail_2026_07_01.py"],
    ["python3", "-B", "docs/benchmark/test_wave2_timestamp_insensitive_hashes_2026_07_01.py"],
    ["git", "diff", "--check"],
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    rendered = json.dumps(body, indent=2, sort_keys=True) + "\n"
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def package_sha256_no_newline(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    rendered = json.dumps(body, indent=2, sort_keys=True)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def package_hash_valid(data: dict[str, Any]) -> bool | None:
    if not data.get("package_sha256"):
        return None
    return data["package_sha256"] in {package_sha256(data), package_sha256_no_newline(data)}


def run_command(argv: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        argv,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "argv": argv,
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def parse_python_files() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relpath in PYTHON_PARSE_FILES:
        path = REPO_ROOT / relpath
        try:
            ast.parse(path.read_text(), filename=relpath)
            rows.append({"path": relpath, "passed": True})
        except SyntaxError as exc:
            rows.append({"error": str(exc), "path": relpath, "passed": False})
    return rows


def read_json_artifacts() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for label, relpath in JSON_ARTIFACTS.items():
        path = REPO_ROOT / relpath
        try:
            raw = path.read_bytes()
            data = json.loads(raw)
            rows[label] = {
                "classification": data.get("classification"),
                "file_sha256": sha256_bytes(raw),
                "package_hash_valid": package_hash_valid(data),
                "package_sha256": data.get("package_sha256"),
                "passed": True,
                "path": relpath,
                "status": data.get("status"),
            }
            if label == "control_room":
                rows[label]["summary"] = data.get("summary")
            if label == "readiness":
                rows[label]["summary"] = data.get("summary")
            if label == "statistical_claim_guardrail":
                rows[label]["claim_boundary"] = data.get("claim_boundary")
                rows[label]["summary"] = data.get("summary")
        except Exception as exc:  # noqa: BLE001 - validation report should preserve the failure text.
            rows[label] = {"error": str(exc), "passed": False, "path": relpath}
    return rows


def control_room_gate_summary(control_room: dict[str, Any]) -> dict[str, Any]:
    batch004 = control_room["gates"]["batch004"]
    batch005 = control_room["gates"]["batch005"]
    current = control_room["current_state"]
    return {
        "approval_packet_sha256": batch004["approval_packet_sha256"],
        "batch004_expected_provider_calls": batch004["expected_counts"]["total_provider_calls"],
        "batch004_live_gate": batch004["live_execution_gate"].get("status"),
        "batch004_provider_calls_made": batch004["providers_called"],
        "batch005_blocked_by": batch005["live_execution_gate"].get("blocked_reason"),
        "batch005_expected_provider_calls": batch005["expected_counts"]["total_provider_calls"],
        "batch005_live_gate": batch005["live_execution_gate"].get("status"),
        "batch005_provider_calls_made": batch005["providers_called"],
        "current_phase": current["current_phase"],
        "current_scored_pairs": current["current_scored_pairs"],
        "next_allowed_live_batch": current["next_allowed_live_batch"],
        "per_class_n_after_clean_batch004": current["per_class_n_after_clean_batch004"],
        "per_class_n_after_clean_batch004_and_batch005": current["per_class_n_after_clean_batch004_and_batch005"],
    }


def build_validation() -> dict[str, Any]:
    python_rows = parse_python_files()
    json_rows = read_json_artifacts()
    command_rows = [run_command(argv) for argv in LOCAL_COMMANDS]
    control_room = json.loads((REPO_ROOT / JSON_ARTIFACTS["control_room"]).read_text())
    operator_handoff = json.loads((REPO_ROOT / JSON_ARTIFACTS["operator_handoff"]).read_text())
    approval = json.loads((REPO_ROOT / JSON_ARTIFACTS["batch004_approval_packet"]).read_text())
    statistical_guardrail = json.loads((REPO_ROOT / JSON_ARTIFACTS["statistical_claim_guardrail"]).read_text())
    batch005_approval = (
        BATCHES_ROOT
        / "wave2_holo_target_batch_005"
        / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
    )
    checks = {
        "approval_packet_preserved": approval.get("status") in {"READY_FOR_EXPLICIT_PROVIDER_APPROVAL", "NOT_READY"},
        "approval_packet_does_not_self_grant": approval.get("approval_granted_by_this_packet") is False,
        "commands_passed": all(row["passed"] for row in command_rows),
        "control_room_pass": control_room.get("status") == "PASS",
        "control_room_no_failed_checks": control_room.get("summary", {}).get("checks_failed") == 0,
        "json_artifacts_parse": all(row["passed"] for row in json_rows.values()),
        "json_declared_package_hashes_valid": all(
            row.get("package_hash_valid") is not False for row in json_rows.values()
        ),
        "no_batch005_approval_packet": not batch005_approval.exists(),
        "operator_handoff_no_provider": operator_handoff.get("summary", {}).get("provider_calls_made_by_handoff")
        == 0,
        "operator_handoff_pass": operator_handoff.get("status") == "PASS",
        "operator_handoff_selected_target_only": operator_handoff.get("current_claim")
        == "SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF",
        "python_ast_parse": all(row["passed"] for row in python_rows),
        "statistical_claim_guardrail_no_provider": statistical_guardrail.get("summary", {}).get(
            "provider_calls_made_by_guardrail"
        )
        == 0,
        "statistical_claim_guardrail_pass": statistical_guardrail.get("status") == "PASS",
        "statistical_claim_guardrail_selected_target_only": statistical_guardrail.get("claim_boundary", {}).get(
            "current_claim"
        )
        == "SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF",
        "validation_generated_without_provider_calls": True,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "checks": checks,
        "classification": "WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01",
        "commands": command_rows,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate_summary": control_room_gate_summary(control_room),
        "generated_without_provider_calls": True,
        "json_artifacts": json_rows,
        "package_sha256": "",
        "python_ast_parse": python_rows,
        "status": status,
        "stop_rules": [
            "This validation does not approve provider calls.",
            "This validation does not run Batch 004 or Batch 005 live execution.",
            "Batch 004 still requires the exact approval statement and current approval packet SHA.",
            "Batch 005 remains locked behind a separate approval packet even though the Batch 004 evidence gate is complete.",
        ],
        "summary": {
            "commands_failed": sum(1 for row in command_rows if not row["passed"]),
            "commands_total": len(command_rows),
            "json_artifacts_failed": sum(1 for row in json_rows.values() if not row["passed"]),
            "json_artifacts_total": len(json_rows),
            "python_parse_failed": sum(1 for row in python_rows if not row["passed"]),
            "python_parse_total": len(python_rows),
            "provider_calls_made_by_validation": 0,
        },
    }


def render_md(report: dict[str, Any]) -> str:
    gate = report["gate_summary"]
    lines = [
        "# Wave 2 No-Provider Control Room Validation",
        "",
        f"Status: `{report['status']}`",
        f"Generated without provider calls: `{report['generated_without_provider_calls']}`",
        "",
        "## Gate Summary",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| Current phase | `{gate['current_phase']}` |",
        f"| Next allowed live batch | `{gate['next_allowed_live_batch']}` |",
        f"| Current scored pairs | `{gate['current_scored_pairs']}` |",
        f"| Per-class n after clean Batch004 | `{gate['per_class_n_after_clean_batch004']}` |",
        f"| Per-class n after clean Batch004+Batch005 | `{gate['per_class_n_after_clean_batch004_and_batch005']}` |",
        f"| Batch004 approval packet SHA-256 | `{gate['approval_packet_sha256']}` |",
        f"| Batch004 live gate | `{gate['batch004_live_gate']}` |",
        f"| Batch004 expected provider calls | `{gate['batch004_expected_provider_calls']}` |",
        f"| Batch004 provider calls made | `{gate['batch004_provider_calls_made']}` |",
        f"| Batch005 live gate | `{gate['batch005_live_gate']}` |",
        f"| Batch005 blocked by | `{gate['batch005_blocked_by']}` |",
        f"| Batch005 expected provider calls after future approval | `{gate['batch005_expected_provider_calls']}` |",
        f"| Batch005 provider calls made | `{gate['batch005_provider_calls_made']}` |",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for check_id, passed in report["checks"].items():
        lines.append(f"| `{check_id}` | `{'PASS' if passed else 'FAIL'}` |")
    lines.extend(["", "## Commands", "", "| Command | Result |", "| --- | --- |"])
    for row in report["commands"]:
        command = " ".join(row["argv"])
        lines.append(f"| `{command}` | `{'PASS' if row['passed'] else 'FAIL'}` |")
    lines.extend(["", "## JSON Artifacts", "", "| Artifact | Result | Package SHA-256 |", "| --- | --- | --- |"])
    for label, row in report["json_artifacts"].items():
        lines.append(
            f"| `{label}` | `{'PASS' if row['passed'] else 'FAIL'}` | "
            f"`{row.get('package_sha256')}` |"
        )
    lines.extend(["", "## Stop Rules", ""])
    lines.extend(f"- {rule}" for rule in report["stop_rules"])
    lines.append("")
    return "\n".join(lines)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main() -> int:
    report = build_validation()
    report["package_sha256"] = package_sha256(report)
    write_json(OUT_JSON, report)
    OUT_MD.write_text(render_md(report))
    print(
        json.dumps(
            {
                "approval_packet_sha256": report["gate_summary"]["approval_packet_sha256"],
                "json": str(OUT_JSON.relative_to(REPO_ROOT)),
                "md": str(OUT_MD.relative_to(REPO_ROOT)),
                "package_sha256": report["package_sha256"],
                "provider_calls_made": 0,
                "status": report["status"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
