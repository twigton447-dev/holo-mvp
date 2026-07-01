#!/usr/bin/env python3
"""No-provider regression test for the Wave 2 Batch 004 approval gate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


RUNNER_PATH = Path("docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py")
APPROVAL_PACKET = Path(
    "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    "/holo_target_batches/wave2_holo_target_batch_004"
    "/WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.json"
)
APPROVAL_PACKET_MD = APPROVAL_PACKET.with_suffix(".md")


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wave2_runner_under_test", RUNNER_PATH.resolve())
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def assert_locked(result: dict[str, Any], expected_blocked: set[str]) -> None:
    assert result["status"] == "LOCKED", result
    blocked = set(result["blocked_reason"] or [])
    missing = expected_blocked - blocked
    assert not missing, {"missing_blocked_checks": sorted(missing), "result": result}


def main() -> int:
    runner = load_runner()
    runner.configure_batch(4)
    manifest = runner.load_json(runner.LIVE_PREFLIGHT_JSON)
    approval = json.loads(APPROVAL_PACKET.read_text())
    statement = approval["approval_statement_required"]
    packet_sha = approval["package_sha256"]

    assert approval["status"] == "READY_FOR_EXPLICIT_PROVIDER_APPROVAL"
    assert approval["approval_granted_by_this_packet"] is False
    assert approval["expected_calls_if_approved"]["total_provider_calls"] == 100
    assert approval["expected_calls_if_approved"]["solo_calls"] == 0
    assert approval["expected_calls_if_approved"]["judge_calls"] == 0
    assert runner.package_sha256(approval) == packet_sha

    no_approval = runner.provider_approval_gate(None, None, manifest)
    assert_locked(
        no_approval,
        {
            "approval_statement_provided",
            "approval_statement_exact_match",
            "approval_packet_sha256_provided",
            "approval_packet_sha256_exact_match",
        },
    )

    wrong_statement = runner.provider_approval_gate("I approve all provider calls.", packet_sha, manifest)
    assert_locked(wrong_statement, {"approval_statement_exact_match"})

    wrong_hash = runner.provider_approval_gate(statement, "0" * 64, manifest)
    assert_locked(wrong_hash, {"approval_packet_sha256_exact_match"})

    exact = runner.provider_approval_gate(statement, packet_sha, manifest)
    assert exact["status"] == "PASS", exact
    assert exact["blocked_reason"] is None, exact
    assert all(exact["checks"].values()), exact

    md = APPROVAL_PACKET_MD.read_text()
    assert f"--approval-packet-sha256 {packet_sha}" in md
    assert "--batch-number 4 --run-live" in md
    assert "--batch-number 5" not in md

    print(
        json.dumps(
            {
                "status": "PASS",
                "approval_packet_sha256": packet_sha,
                "checked_locked_paths": [
                    "missing_statement_and_hash",
                    "wrong_statement",
                    "wrong_hash",
                ],
                "checked_pass_path": "exact_statement_and_exact_packet_hash",
                "provider_calls_made": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
