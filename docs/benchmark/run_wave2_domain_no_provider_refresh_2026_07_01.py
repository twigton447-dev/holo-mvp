#!/usr/bin/env python3
"""Run the Wave 2 no-provider domain consolidation refresh chain."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_ROOT = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01"
OUT_JSON = OUT_ROOT / "WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.json"
OUT_MD = OUT_ROOT / "WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01.md"
PYCACHE_PREFIX = Path("/private/tmp/wave2_domain_no_provider_refresh_pycache")

CONTROL_ROOM = REPO_ROOT / "docs/benchmark/wave2_domain_control_room_2026_07_01/WAVE2_DOMAIN_CONTROL_ROOM_2026_07_01.json"
COMPLETION_AUDIT = OUT_ROOT / "WAVE2_DOMAIN_COMPLETION_AUDIT_2026_07_01.json"
CONTROL_ROOM_VALIDATION = (
    REPO_ROOT
    / "docs/benchmark/wave2_domain_control_room_2026_07_01"
    / "WAVE2_NO_PROVIDER_CONTROL_ROOM_VALIDATION_2026_07_01.json"
)
READINESS = REPO_ROOT / "docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json"
ORDERING = REPO_ROOT / "docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
APPROVAL = (
    REPO_ROOT
    / "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    / "holo_target_batches/wave2_holo_target_batch_004"
    / "WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)
METRICS_PACKAGE = REPO_ROOT / "docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/compiled_metrics_package.json"
WORKBOOK = REPO_ROOT / "outputs/holoverify_holobuild_metrics_2026_07_01/HoloVerify_HoloBuild_HashLocked_Metrics_2026_07_01.xlsx"
PRESERVATION = OUT_ROOT / "WAVE2_DOMAIN_PRESERVATION_MANIFEST_2026_07_01.json"
SELECTIVE_STAGING_PLAN = OUT_ROOT / "WAVE2_DOMAIN_SELECTIVE_STAGING_PLAN_2026_07_01.json"
STATISTICAL_CLAIM_GUARDRAIL = OUT_ROOT / "WAVE2_STATISTICAL_CLAIM_GUARDRAIL_2026_07_01.json"
OPERATOR_HANDOFF = OUT_ROOT / "WAVE2_DOMAIN_OPERATOR_HANDOFF_2026_07_01.json"

PYTHON_SCRIPTS = [
    "docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py",
    "docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py",
    "docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py",
    "docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py",
    "docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py",
    "docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py",
    "docs/benchmark/build_wave2_batch004_provider_approval_packet_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_control_room_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py",
    "docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py",
    "docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py",
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
]

STEPS = [
    {
        "name": "compile_python_refresh_scripts",
        "argv": ["python3", "-m", "py_compile", *PYTHON_SCRIPTS],
    },
    {
        "name": "combined_evidence_batches_001_004",
        "argv": [
            "python3",
            "-B",
            "docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py",
            "--batches",
            "1",
            "2",
            "3",
            "4",
        ],
    },
    {
        "name": "compile_metrics_package",
        "argv": ["python3", "-B", "docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py"],
    },
    {
        "name": "build_metrics_workbook",
        "argv": ["node", "docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs"],
    },
    {
        "name": "build_domain_consolidation_ledger",
        "argv": ["python3", "-B", "docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py"],
    },
    {
        "name": "verify_domain_ordering",
        "argv": ["python3", "-B", "docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py"],
    },
    {
        "name": "build_completion_readiness",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py"],
    },
    {
        "name": "build_control_room_pre_lock_test",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_domain_control_room_2026_07_01.py"],
    },
    {
        "name": "test_batch004_provider_approval_gate",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_batch004_provider_approval_gate_2026_07_01.py"],
    },
    {
        "name": "test_batch005_full_family_approval_lock_fail_closed",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_batch005_full_family_lock_2026_07_01.py"],
    },
    {
        "name": "rebuild_control_room_after_batch005_lock_test",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_domain_control_room_2026_07_01.py"],
    },
    {
        "name": "build_statistical_claim_guardrail",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py"],
    },
    {
        "name": "build_preservation_manifest",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_domain_preservation_manifest_2026_07_01.py"],
    },
    {
        "name": "build_selective_staging_plan",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_domain_selective_staging_plan_2026_07_01.py"],
    },
    {
        "name": "build_operator_handoff",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_domain_operator_handoff_2026_07_01.py"],
    },
    {
        "name": "test_domain_control_room",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_domain_control_room_2026_07_01.py"],
    },
    {
        "name": "test_preservation_manifest",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_domain_preservation_manifest_2026_07_01.py"],
    },
    {
        "name": "test_selective_staging_plan",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_domain_selective_staging_plan_2026_07_01.py"],
    },
    {
        "name": "test_statistical_claim_guardrail",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_statistical_claim_guardrail_2026_07_01.py"],
    },
    {
        "name": "test_operator_handoff",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_domain_operator_handoff_2026_07_01.py"],
    },
    {
        "name": "test_timestamp_insensitive_hashes",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_timestamp_insensitive_hashes_2026_07_01.py"],
    },
    {
        "name": "validate_no_provider_control_room",
        "argv": ["python3", "-B", "docs/benchmark/validate_wave2_no_provider_control_room_2026_07_01.py"],
    },
    {
        "name": "build_completion_audit",
        "argv": ["python3", "-B", "docs/benchmark/build_wave2_domain_completion_audit_2026_07_01.py"],
    },
    {
        "name": "test_completion_audit",
        "argv": ["python3", "-B", "docs/benchmark/test_wave2_domain_completion_audit_2026_07_01.py"],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_text(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def package_body(value: Any, *, top_level: bool = False) -> Any:
    if isinstance(value, dict):
        return {
            key: package_body(item)
            for key, item in value.items()
            if key
            not in {
                "created_at_utc",
                "duration_seconds",
                "ended_at_utc",
                "started_at_utc",
            }
            and not (top_level and key == "package_sha256")
        }
    if isinstance(value, list):
        return [package_body(item) for item in value]
    return value


def package_sha256(data: dict[str, Any]) -> str:
    body = package_body(data, top_level=True)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True) + "\n")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def tail(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[-limit:]


def run_step(step: dict[str, Any]) -> dict[str, Any]:
    started = datetime.now(timezone.utc)
    monotonic_start = time.monotonic()
    env = os.environ.copy()
    env["PYTHONPYCACHEPREFIX"] = str(PYCACHE_PREFIX)
    result = subprocess.run(
        step["argv"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    ended = datetime.now(timezone.utc)
    return {
        "argv": step["argv"],
        "duration_seconds": round(time.monotonic() - monotonic_start, 3),
        "ended_at_utc": ended.isoformat(),
        "name": step["name"],
        "returncode": result.returncode,
        "started_at_utc": started.isoformat(),
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "stderr_tail": tail(result.stderr),
        "stdout_tail": tail(result.stdout),
    }


def final_artifacts() -> dict[str, Any]:
    control_room = read_json(CONTROL_ROOM)
    completion_audit = read_json(COMPLETION_AUDIT)
    control_validation = read_json(CONTROL_ROOM_VALIDATION)
    readiness = read_json(READINESS)
    ordering = read_json(ORDERING)
    approval = read_json(APPROVAL)
    metrics = read_json(METRICS_PACKAGE)
    preservation = read_json(PRESERVATION)
    selective_staging_plan = read_json(SELECTIVE_STAGING_PLAN)
    statistical_guardrail = read_json(STATISTICAL_CLAIM_GUARDRAIL)
    operator_handoff = read_json(OPERATOR_HANDOFF)
    return {
        "batch004_approval_packet": {
            "approval_granted_by_packet": approval.get("approval_granted_by_this_packet"),
            "package_sha256": approval.get("package_sha256"),
            "status": approval.get("status"),
        },
        "completion_audit": {
            "completion_claim": completion_audit.get("completion_claim"),
            "package_hash_valid": package_sha256(completion_audit) == completion_audit.get("package_sha256"),
            "package_sha256": completion_audit.get("package_sha256"),
            "provider_calls_made": completion_audit.get("summary", {}).get("provider_calls_made_by_audit"),
            "status": completion_audit.get("status"),
        },
        "control_room": {
            "checks_failed": control_room.get("summary", {}).get("checks_failed"),
            "next_allowed_live_batch": control_room.get("current_state", {}).get("next_allowed_live_batch"),
            "package_hash_valid": package_sha256(control_room) == control_room.get("package_sha256"),
            "package_sha256": control_room.get("package_sha256"),
            "status": control_room.get("status"),
        },
        "control_room_validation": {
            "package_hash_valid": package_sha256(control_validation) == control_validation.get("package_sha256"),
            "package_sha256": control_validation.get("package_sha256"),
            "provider_calls_made": control_validation.get("summary", {}).get("provider_calls_made_by_validation"),
            "status": control_validation.get("status"),
        },
        "metrics_package": {
            "generated_without_provider_calls": metrics.get("generated_without_provider_calls"),
            "metric_summary_count": metrics.get("metric_summary_count"),
            "source_audit_count": metrics.get("source_audit_count"),
        },
        "preservation_manifest": {
            "other_dirty_path_count": preservation.get("summary", {}).get("other_dirty_path_count"),
            "package_hash_valid": package_sha256(preservation) == preservation.get("package_sha256"),
            "package_sha256": preservation.get("package_sha256"),
            "status": preservation.get("status"),
            "tracked_or_untracked_path_count": preservation.get("summary", {}).get("tracked_or_untracked_path_count"),
        },
        "selective_staging_plan": {
            "package_hash_valid": package_sha256(selective_staging_plan) == selective_staging_plan.get("package_sha256"),
            "package_sha256": selective_staging_plan.get("package_sha256"),
            "path_count": selective_staging_plan.get("summary", {}).get("path_count"),
            "provider_calls_made": selective_staging_plan.get("summary", {}).get("provider_calls_made_by_plan"),
            "status": selective_staging_plan.get("status"),
        },
        "statistical_claim_guardrail": {
            "current_claim": statistical_guardrail.get("claim_boundary", {}).get("current_claim"),
            "package_hash_valid": package_sha256(statistical_guardrail) == statistical_guardrail.get("package_sha256"),
            "package_sha256": statistical_guardrail.get("package_sha256"),
            "provider_calls_made": statistical_guardrail.get("summary", {}).get("provider_calls_made_by_guardrail"),
            "status": statistical_guardrail.get("status"),
        },
        "ordering": {
            "package_sha256": ordering.get("package_sha256"),
            "status": ordering.get("status"),
        },
        "operator_handoff": {
            "package_hash_valid": package_sha256(operator_handoff) == operator_handoff.get("package_sha256"),
            "package_sha256": operator_handoff.get("package_sha256"),
            "provider_calls_made": operator_handoff.get("summary", {}).get("provider_calls_made_by_handoff"),
            "status": operator_handoff.get("status"),
        },
        "readiness": {
            "checks_failed": readiness.get("summary", {}).get("checks_failed"),
            "package_sha256": readiness.get("package_sha256"),
            "status": readiness.get("status"),
        },
        "workbook": {
            "exists": WORKBOOK.exists(),
            "path": str(WORKBOOK.relative_to(REPO_ROOT)),
        },
    }


def build_receipt(steps: list[dict[str, Any]]) -> dict[str, Any]:
    passed = all(step["status"] == "PASS" for step in steps)
    artifacts = final_artifacts() if passed else {}
    artifact_checks = {
        "batch004_approval_packet_preserved": artifacts.get("batch004_approval_packet", {}).get("status")
        in {"READY_FOR_EXPLICIT_PROVIDER_APPROVAL", "NOT_READY"},
        "completion_audit_hash_valid": artifacts.get("completion_audit", {}).get("package_hash_valid") is True,
        "completion_audit_not_complete_claim": artifacts.get("completion_audit", {}).get("completion_claim")
        == "NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED",
        "completion_audit_pass": artifacts.get("completion_audit", {}).get("status") == "PASS",
        "control_room_hash_valid": artifacts.get("control_room", {}).get("package_hash_valid") is True,
        "control_room_pass": artifacts.get("control_room", {}).get("status") == "PASS",
        "control_room_validation_hash_valid": artifacts.get("control_room_validation", {}).get("package_hash_valid") is True,
        "control_room_validation_pass": artifacts.get("control_room_validation", {}).get("status") == "PASS",
        "metrics_no_provider": artifacts.get("metrics_package", {}).get("generated_without_provider_calls") is True,
        "ordering_pass": artifacts.get("ordering", {}).get("status") == "PASS",
        "operator_handoff_hash_valid": artifacts.get("operator_handoff", {}).get("package_hash_valid") is True,
        "operator_handoff_pass": artifacts.get("operator_handoff", {}).get("status") == "PASS",
        "operator_handoff_no_provider": artifacts.get("operator_handoff", {}).get("provider_calls_made") == 0,
        "preservation_manifest_hash_valid": artifacts.get("preservation_manifest", {}).get("package_hash_valid") is True,
        "preservation_manifest_pass": artifacts.get("preservation_manifest", {}).get("status") == "PASS",
        "preservation_manifest_other_dirty_paths_reported": artifacts.get("preservation_manifest", {}).get("other_dirty_path_count")
        is not None,
        "readiness_pass": artifacts.get("readiness", {}).get("status") == "PASS",
        "selective_staging_plan_hash_valid": artifacts.get("selective_staging_plan", {}).get("package_hash_valid") is True,
        "selective_staging_plan_pass": artifacts.get("selective_staging_plan", {}).get("status") == "PASS",
        "selective_staging_plan_path_count_matches_preservation": artifacts.get("selective_staging_plan", {}).get(
            "path_count"
        )
        == artifacts.get("preservation_manifest", {}).get("tracked_or_untracked_path_count"),
        "statistical_claim_guardrail_hash_valid": artifacts.get("statistical_claim_guardrail", {}).get(
            "package_hash_valid"
        )
        is True,
        "statistical_claim_guardrail_pass": artifacts.get("statistical_claim_guardrail", {}).get("status") == "PASS",
        "statistical_claim_guardrail_selected_target_only": artifacts.get("statistical_claim_guardrail", {}).get(
            "current_claim"
        )
        == "SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF",
        "workbook_exists": artifacts.get("workbook", {}).get("exists") is True,
    }
    status = "PASS" if passed and all(artifact_checks.values()) else "FAIL"
    receipt = {
        "artifact_checks": artifact_checks,
        "classification": "WAVE2_DOMAIN_NO_PROVIDER_REFRESH_RECEIPT_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "final_artifacts": artifacts,
        "generated_without_provider_calls": True,
        "package_sha256": "",
        "provider_calls_made_by_refresh": 0,
        "status": status,
        "steps": steps,
        "stop_rules": [
            "This refresh never runs Batch 004 live provider calls.",
            "This refresh never approves provider calls.",
            "The Batch 005 run-live path is exercised only as a fail-closed approval-lock test and must create zero live run directories.",
            "The control room is rebuilt after the Batch 005 lock test so final artifacts reflect the latest preflight roots.",
            "The operator handoff is a no-provider runbook and does not grant live execution approval.",
            "The selective staging plan only emits path-limited git add commands and does not stage files.",
            "The statistical guardrail preserves selected-target evidence separately from full-family statistical proof.",
        ],
        "summary": {
            "failed_steps": [step["name"] for step in steps if step["status"] != "PASS"],
            "provider_calls_made": 0,
            "steps_passed": sum(1 for step in steps if step["status"] == "PASS"),
            "steps_total": len(steps),
        },
    }
    receipt["package_sha256"] = package_sha256(receipt)
    return receipt


def render_md(receipt: dict[str, Any]) -> str:
    control = receipt.get("final_artifacts", {}).get("control_room", {})
    completion_audit = receipt.get("final_artifacts", {}).get("completion_audit", {})
    validation = receipt.get("final_artifacts", {}).get("control_room_validation", {})
    approval = receipt.get("final_artifacts", {}).get("batch004_approval_packet", {})
    preservation = receipt.get("final_artifacts", {}).get("preservation_manifest", {})
    selective = receipt.get("final_artifacts", {}).get("selective_staging_plan", {})
    statistical = receipt.get("final_artifacts", {}).get("statistical_claim_guardrail", {})
    operator_handoff = receipt.get("final_artifacts", {}).get("operator_handoff", {})
    lines = [
        "# Wave 2 Domain No-Provider Refresh Receipt",
        "",
        f"Status: `{receipt['status']}`",
        f"Package SHA-256: `{receipt['package_sha256']}`",
        f"Generated without provider calls: `{receipt['generated_without_provider_calls']}`",
        f"Provider calls made by refresh: `{receipt['provider_calls_made_by_refresh']}`",
        "",
        "## Final Artifacts",
        "",
        "| Artifact | Status | Package SHA-256 |",
        "| --- | --- | --- |",
        f"| Control room | `{control.get('status')}` | `{control.get('package_sha256')}` |",
        f"| Completion audit | `{completion_audit.get('status')}` | `{completion_audit.get('package_sha256')}` |",
        f"| Control room validation | `{validation.get('status')}` | `{validation.get('package_sha256')}` |",
        f"| Operator handoff | `{operator_handoff.get('status')}` | `{operator_handoff.get('package_sha256')}` |",
        f"| Preservation manifest | `{preservation.get('status')}` | `{preservation.get('package_sha256')}` |",
        f"| Selective staging plan | `{selective.get('status')}` | `{selective.get('package_sha256')}` |",
        f"| Statistical claim guardrail | `{statistical.get('status')}` | `{statistical.get('package_sha256')}` |",
        f"| Batch004 approval packet | `{approval.get('status')}` | `{approval.get('package_sha256')}` |",
        f"| Ordering verifier | `{receipt.get('final_artifacts', {}).get('ordering', {}).get('status')}` | `{receipt.get('final_artifacts', {}).get('ordering', {}).get('package_sha256')}` |",
        f"| Readiness | `{receipt.get('final_artifacts', {}).get('readiness', {}).get('status')}` | `{receipt.get('final_artifacts', {}).get('readiness', {}).get('package_sha256')}` |",
        "",
        "## Steps",
        "",
        "| Step | Status | Seconds |",
        "| --- | --- | ---: |",
    ]
    for step in receipt["steps"]:
        lines.append(f"| `{step['name']}` | `{step['status']}` | `{step['duration_seconds']}` |")
    lines.extend(["", "## Stop Rules", ""])
    lines.extend(f"- {rule}" for rule in receipt["stop_rules"])
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    steps: list[dict[str, Any]] = []
    for step in STEPS:
        result = run_step(step)
        steps.append(result)
        if result["status"] != "PASS":
            break
    receipt = build_receipt(steps)
    write_json(OUT_JSON, receipt)
    OUT_MD.write_text(render_md(receipt))
    print(
        json.dumps(
            {
                "json": str(OUT_JSON.relative_to(REPO_ROOT)),
                "md": str(OUT_MD.relative_to(REPO_ROOT)),
                "package_sha256": receipt["package_sha256"],
                "status": receipt["status"],
                "steps_passed": receipt["summary"]["steps_passed"],
                "steps_total": receipt["summary"]["steps_total"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
