#!/usr/bin/env python3
"""Build a no-provider approval packet for Wave 2 Batch 005 live execution."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BATCH_NUMBER = 5
BATCH_ID = f"WAVE2_HOLO_TARGET_BATCH_{BATCH_NUMBER:03d}"
FREEZE_ROOT = Path("docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01")
BATCH_ROOT = FREEZE_ROOT / "holo_target_batches" / f"wave2_holo_target_batch_{BATCH_NUMBER:03d}"
OUT_JSON = BATCH_ROOT / f"{BATCH_ID}_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
OUT_MD = BATCH_ROOT / f"{BATCH_ID}_PROVIDER_APPROVAL_PACKET_2026_07_01.md"
RUNNER_PATH = Path("docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py")

REGISTRATION = BATCH_ROOT / f"{BATCH_ID}_REGISTRATION_2026_07_01.json"
STAGING_PREFLIGHT = BATCH_ROOT / f"{BATCH_ID}_PREFLIGHT_2026_07_01.json"
LIVE_PREFLIGHT = BATCH_ROOT / f"{BATCH_ID}_LIVE_PREFLIGHT_2026_07_01.json"
ORDERING_VERIFICATION = Path(
    "docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/WAVE2_DOMAIN_ORDERING_VERIFICATION_2026_07_01.json"
)
READINESS = Path("docs/benchmark/wave2_domain_completion_readiness_2026_07_01/WAVE2_DOMAIN_COMPLETION_READINESS_2026_07_01.json")
COMBINED_MEMO = (
    FREEZE_ROOT
    / "holo_target_batches"
    / "WAVE2_HOLO_TARGET_BATCH_001_002_003_004_COMBINED_EVIDENCE_MEMO_2026_07_01.json"
)
BATCH004_COMPARISON = (
    FREEZE_ROOT
    / "holo_target_batches"
    / "wave2_holo_target_batch_004"
    / "WAVE2_HOLO_TARGET_BATCH_004_SOLO_VS_HOLO_COMPARISON_2026_07_01.json"
)

APPROVAL_STATEMENT = (
    "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_005 only, exactly as scoped in "
    "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01."
)
RUN_COMMAND = (
    "python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 5 --run-live "
    "--approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET "
    f"--approval-statement {json.dumps(APPROVAL_STATEMENT)}"
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    rendered = json.dumps(body, indent=2, sort_keys=True) + "\n"
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def refresh_live_preflight() -> None:
    spec = importlib.util.spec_from_file_location("wave2_holo_target_batch_runner", RUNNER_PATH.resolve())
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable_to_load_runner:{RUNNER_PATH}")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.configure_batch(BATCH_NUMBER)
    manifest = runner.validate_preflight()
    if manifest.get("status") != "PASS":
        raise RuntimeError(f"batch005_live_preflight_not_pass:{manifest.get('blocked_reason')}")


def pair_rows(selected_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pair: dict[str, dict[str, Any]] = {}
    for row in selected_records:
        pair = by_pair.setdefault(
            row["pair_id"],
            {
                "domain": row["domain"],
                "family_id": row["family_id"],
                "pair_id": row["pair_id"],
                "priority_score": row.get("priority_score"),
                "target_bucket": row.get("target_bucket"),
                "triage_class": row.get("triage_class"),
                "packets": [],
            },
        )
        pair["packets"].append(
            {
                "model_visible_payload_ref": row["model_visible_payload_ref"],
                "model_visible_payload_sha256": row["model_visible_payload_file_sha256"],
                "packet_id": row["packet_id"],
                "packet_ref": row["packet_ref"],
                "packet_sha256": row["packet_sha256"],
                "packet_truth": row["packet_truth"],
                "prompt_ref": row["prompt_ref"],
                "prompt_sha256": row["prompt_sha256"],
                "sibling_id": row["sibling_id"],
            }
        )
    for row in by_pair.values():
        row["packets"] = sorted(row["packets"], key=lambda packet: packet["packet_id"])
    return [by_pair[pair_id] for pair_id in sorted(by_pair)]


def build_packet() -> dict[str, Any]:
    refresh_live_preflight()
    registration = read_json(REGISTRATION)
    staging_preflight = read_json(STAGING_PREFLIGHT)
    live_preflight = read_json(LIVE_PREFLIGHT)
    ordering = read_json(ORDERING_VERIFICATION)
    readiness = read_json(READINESS)
    combined_memo = read_json(COMBINED_MEMO)
    batch004_comparison = read_json(BATCH004_COMPARISON)
    expected_counts = registration["expected_counts"]
    roster = live_preflight["architecture_lock"]["model_roster_declared"]
    live_gate = live_preflight.get("live_execution_gate", {})
    checks = {
        "batch_id_is_005": registration["batch_id"] == BATCH_ID,
        "selection_mode_full_family_remainder": registration.get("selection_mode") == "full-family-remainder",
        "registration_status_preflight_pass": staging_preflight.get("status") == "PASS",
        "live_preflight_pass": live_preflight.get("status") == "PASS",
        "live_execution_gate_pass": live_gate.get("status") == "PASS",
        "live_preflight_requires_approval_statement": live_preflight.get("required_approval_statement")
        == APPROVAL_STATEMENT,
        "live_preflight_approval_statement_hash_matches": live_preflight.get("required_approval_statement_sha256")
        == hashlib.sha256(APPROVAL_STATEMENT.encode("utf-8")).hexdigest(),
        "ordering_verification_pass": ordering.get("status") == "PASS",
        "readiness_pass": readiness.get("status") == "PASS",
        "readiness_all_checks_passed": readiness.get("summary", {}).get("checks_failed") == 0,
        "readiness_batch005_true": readiness.get("summary", {}).get("ready_for_batch005_provider_approval") is True,
        "combined_memo_has_37_valid_pairs": combined_memo.get("combined_metrics", {}).get("holo_valid_pairs") == 37,
        "combined_memo_has_74_correct_packets": combined_memo.get("combined_metrics", {}).get(
            "holo_packets_correct_admissible"
        )
        == 74,
        "batch004_comparison_has_10_valid_pairs": batch004_comparison.get("summary_metrics", {}).get("holo_valid_pairs")
        == 10,
        "expected_provider_calls_230": expected_counts.get("total_provider_calls") == 230,
        "expected_solo_calls_0": expected_counts.get("solo_calls") == 0,
        "expected_judge_calls_0": expected_counts.get("judge_calls") == 0,
        "no_provider_calls_made": live_preflight.get("providers_called") == 0,
        "no_live_started": live_preflight.get("live_holo_started") is False
        and live_preflight.get("solo_started") is False
        and live_preflight.get("judges_started") is False,
        "no_fallback_policy_declared": roster.get("fallback_policy") == "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        "gov_cannot_choose_models": all(not row.get("gov_may_select_models") for row in roster.get("gov_sequence", [])),
        "run_command_batch005_only": "--batch-number 5" in RUN_COMMAND and "--run-live" in RUN_COMMAND,
        "run_command_requires_approval_packet_sha256": "--approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET"
        in RUN_COMMAND,
        "run_command_carries_exact_approval_statement": f"--approval-statement {json.dumps(APPROVAL_STATEMENT)}"
        in RUN_COMMAND,
    }
    status = "READY_FOR_EXPLICIT_PROVIDER_APPROVAL" if all(checks.values()) else "NOT_READY"
    packet = {
        "approval_granted_by_this_packet": False,
        "approval_required": True,
        "approval_statement_required": APPROVAL_STATEMENT,
        "batch_id": BATCH_ID,
        "checks": checks,
        "classification": "WAVE2_BATCH005_PROVIDER_APPROVAL_PACKET_NO_PROVIDER_2026_07_01",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_calls_if_approved": expected_counts,
        "generated_without_provider_calls": True,
        "live_preflight_root_signature": live_preflight.get("root_signature"),
        "model_roster": {
            "fallback_policy": roster.get("fallback_policy"),
            "gov_sequence": roster.get("gov_sequence", []),
            "worker_sequence": roster.get("worker_sequence", []),
        },
        "package_sha256": "",
        "packet_scope": {
            "pair_count": registration["pair_count"],
            "packet_count": registration["packet_count"],
            "selected_pair_ids": registration["selected_pair_ids"],
            "selected_pairs": pair_rows(registration["selected_records"]),
            "selection_mode": registration.get("selection_mode"),
        },
        "pre_run_verifiers": [
            {
                "command": "python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py",
                "package_sha256": ordering.get("package_sha256"),
                "status": ordering.get("status"),
            },
            {
                "command": "python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py",
                "package_sha256": readiness.get("package_sha256"),
                "status": readiness.get("status"),
            },
        ],
        "provider_boundary": {
            "providers": ["xai", "openai", "minimax"],
            "run_command_after_approval": RUN_COMMAND,
            "what_will_be_transmitted": [
                "46 frozen model-visible packet payloads and prompts selected by Batch 005 registration",
                "Holo worker and Gov baton/context messages generated by the fixed runner during live execution",
                "No solo prompts, no judge prompts, and no Batch 001-004 reruns in this live command",
            ],
        },
        "source_paths": {
            "batch004_comparison": str(BATCH004_COMPARISON),
            "combined_batch001_004_memo": str(COMBINED_MEMO),
            "live_preflight": str(LIVE_PREFLIGHT),
            "ordering_verification": str(ORDERING_VERIFICATION),
            "readiness": str(READINESS),
            "registration": str(REGISTRATION),
            "staging_preflight": str(STAGING_PREFLIGHT),
        },
        "status": status,
        "stop_rules": [
            "Do not run this command without the exact explicit approval statement.",
            "Run Batch 005 only; do not rerun Batch 001-004 in the same approval window.",
            "Do not run solo or judge lanes before, during, or after this command unless separately approved.",
            "Abort if either no-provider verifier fails immediately before live execution.",
            "Abort if packet, prompt, model-visible payload, or manifest hashes differ from preflight.",
            "No fallback or model substitution is allowed; provider failure invalidates the run.",
            "Gov may choose control actions only; Gov may not choose or alter models.",
        ],
    }
    packet["package_sha256"] = package_sha256(packet)
    return packet


def render_md(packet: dict[str, Any]) -> str:
    calls = packet["expected_calls_if_approved"]
    approved_command = packet["provider_boundary"]["run_command_after_approval"].replace(
        "APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET",
        packet["package_sha256"],
    )
    lines = [
        "# Wave 2 Batch 005 Provider Approval Packet",
        "",
        f"Classification: `{packet['classification']}`",
        f"Package SHA-256: `{packet['package_sha256']}`",
        f"Status: `{packet['status']}`",
        f"Generated without provider calls: `{packet['generated_without_provider_calls']}`",
        f"Approval granted by this packet: `{packet['approval_granted_by_this_packet']}`",
        "",
        "## Required Approval Statement",
        "",
        f"`{packet['approval_statement_required']}`",
        "",
        "## Scope",
        "",
        "| Item | Value |",
        "| --- | ---: |",
        f"| Selection mode | `{packet['packet_scope']['selection_mode']}` |",
        f"| Pairs | `{packet['packet_scope']['pair_count']}` |",
        f"| Packets | `{packet['packet_scope']['packet_count']}` |",
        f"| Worker calls | `{calls['worker_calls']}` |",
        f"| Gov calls | `{calls['gov_calls']}` |",
        f"| Total provider calls | `{calls['total_provider_calls']}` |",
        f"| Solo calls | `{calls['solo_calls']}` |",
        f"| Judge calls | `{calls['judge_calls']}` |",
        "",
        "## Run Command After Approval",
        "",
        "```bash",
        approved_command,
        "```",
        "",
        "## Model Roster",
        "",
        "| Slot | Provider | Model | Role |",
        "| --- | --- | --- | --- |",
    ]
    for worker in packet["model_roster"]["worker_sequence"]:
        lines.append(f"| `W{worker['worker_index']}` | `{worker['provider']}` | `{worker['model']}` | `{worker['role_name']}` |")
    for gov in packet["model_roster"]["gov_sequence"]:
        lines.append(f"| `{gov['slot']}` | `{gov['provider']}` | `{gov['model']}` | Gov |")
    lines += [
        "",
        "## Selected Pairs",
        "",
        "| Family | Pair | Class | Priority | Packets |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in packet["packet_scope"]["selected_pairs"]:
        packet_ids = ", ".join(packet_row["packet_id"] for packet_row in row["packets"])
        lines.append(
            f"| `{row['family_id']}` | `{row['pair_id']}` | `{row['triage_class']}` | `{row['priority_score']}` | `{packet_ids}` |"
        )
    lines += [
        "",
        "## Pre-Run Verifiers",
        "",
        "| Command | Status | Package SHA-256 |",
        "| --- | --- | --- |",
    ]
    for verifier in packet["pre_run_verifiers"]:
        lines.append(f"| `{verifier['command']}` | `{verifier['status']}` | `{verifier['package_sha256']}` |")
    lines += [
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    for key, value in packet["checks"].items():
        lines.append(f"| `{key}` | `{'PASS' if value else 'FAIL'}` |")
    lines += [
        "",
        "## Stop Rules",
        "",
    ]
    lines += [f"- {rule}" for rule in packet["stop_rules"]]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    packet = build_packet()
    write_json(OUT_JSON, packet)
    OUT_MD.write_text(render_md(packet))
    print(json.dumps({"status": packet["status"], "json": str(OUT_JSON), "md": str(OUT_MD), "package_sha256": packet["package_sha256"]}, indent=2))
    return 0 if packet["status"] == "READY_FOR_EXPLICIT_PROVIDER_APPROVAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
