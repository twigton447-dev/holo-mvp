#!/usr/bin/env python3
"""No-provider regression test for the Wave 2 Batch 005 full-family lock."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


RUNNER_PATH = Path("docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py")
BATCH005_ROOT = Path(
    "docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
    "/holo_target_batches/wave2_holo_target_batch_005"
)


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wave2_runner_batch005_under_test", RUNNER_PATH.resolve())
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def live_run_dirs(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {row.name for row in path.iterdir() if row.is_dir()}


def main() -> int:
    runner = load_runner()
    runner.configure_batch(5)
    before_live_dirs = live_run_dirs(runner.LIVE_RUN_ROOT)

    manifest = runner.validate_preflight()
    gate = manifest["live_execution_gate"]
    assert manifest["status"] == "PASS", manifest
    assert manifest["selection_mode"] == "full-family-remainder", manifest
    assert gate["status"] == "LOCKED", gate
    assert set(gate["blocked_reason"]) == {
        "batch_004_comparison_exists",
        "batch_004_combined_memo_exists",
    }, gate
    assert manifest["providers_called"] == 0, manifest
    assert manifest["live_holo_started"] is False, manifest
    assert manifest["solo_started"] is False, manifest
    assert manifest["judges_started"] is False, manifest

    try:
        runner.run_live(None, None)
    except RuntimeError as exc:
        error = str(exc)
    else:
        raise AssertionError("Batch 005 run_live unexpectedly passed")

    assert error.startswith("wave2_holo_live_execution_gate_locked:"), error
    assert "OPENAI_API_KEY" not in error
    assert "MINIMAX" not in error.upper()
    assert "XAI" not in error.upper()
    assert live_run_dirs(runner.LIVE_RUN_ROOT) == before_live_dirs
    assert not (BATCH005_ROOT / "WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.json").exists()

    print(
        json.dumps(
            {
                "status": "PASS",
                "batch_id": "WAVE2_HOLO_TARGET_BATCH_005",
                "checked_lock": gate["blocked_reason"],
                "run_live_error": error,
                "provider_calls_made": 0,
                "live_run_dirs_created": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
