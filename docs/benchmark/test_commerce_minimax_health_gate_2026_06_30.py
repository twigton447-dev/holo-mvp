#!/usr/bin/env python3
"""No-provider fixtures for the Commerce MiniMax health gate."""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BATCH_RUNNER_PATH = BENCHMARK_ROOT / "run_commerce_openai_w2_holo_batched_family_2026_06_30.py"


def load_batch_runner():
    spec = importlib.util.spec_from_file_location("commerce_minimax_health_gate_fixture", BATCH_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


BATCH = load_batch_runner()


def write_health_report(
    root: Path,
    name: str,
    *,
    created_at: datetime,
    status: str = "PASS",
    provider_clean: bool = True,
    attempts: int = 1,
    recovered: bool = False,
    response_exact: bool = True,
) -> Path:
    path = root / name / "COMMERCE_MINIMAX_HEALTH_CHECK_2026_06_30.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "classification": "COMMERCE_MINIMAX_HEALTH_CHECK_NON_BENCHMARK",
                "status": status,
                "created_at": created_at.isoformat(),
                "provider_clean": provider_clean,
                "transport_attempt_count": attempts,
                "transport_recovered": recovered,
                "response_exact": response_exact,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    return path


def test_health_gate_missing_report_blocks_when_required(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(BATCH, "MINIMAX_HEALTH_ROOT", tmp_path)

    status = BATCH.latest_minimax_health_report(now=datetime(2026, 6, 30, tzinfo=timezone.utc))

    assert status["status"] == "MISSING"
    assert status["recent_pass"] is False
    assert status["reason"] == "no_minimax_health_check_report_found"


def test_recent_clean_minimax_health_report_passes(tmp_path, monkeypatch) -> None:
    now = datetime(2026, 6, 30, 22, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(BATCH, "MINIMAX_HEALTH_ROOT", tmp_path)
    write_health_report(tmp_path, "health_20260630T215900Z", created_at=now - timedelta(seconds=60))

    status = BATCH.latest_minimax_health_report(now=now)

    assert status["status"] == "PASS"
    assert status["recent_pass"] is True
    assert status["provider_clean"] is True
    assert status["transport_attempt_count"] == 1


def test_stale_minimax_health_report_blocks(tmp_path, monkeypatch) -> None:
    now = datetime(2026, 6, 30, 22, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(BATCH, "MINIMAX_HEALTH_ROOT", tmp_path)
    write_health_report(
        tmp_path,
        "health_20260630T210000Z",
        created_at=now - timedelta(seconds=BATCH.MINIMAX_HEALTH_MAX_AGE_SECONDS + 1),
    )

    status = BATCH.latest_minimax_health_report(now=now)

    assert status["status"] == "FAIL"
    assert status["recent_pass"] is False
    assert status["reason"] == "latest_health_check_missing_stale_failed_or_degraded"


def test_recovered_transport_health_report_blocks_even_with_expected_text(tmp_path, monkeypatch) -> None:
    now = datetime(2026, 6, 30, 22, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(BATCH, "MINIMAX_HEALTH_ROOT", tmp_path)
    write_health_report(
        tmp_path,
        "health_20260630T215900Z",
        created_at=now - timedelta(seconds=60),
        provider_clean=False,
        attempts=2,
        recovered=True,
        response_exact=True,
    )

    status = BATCH.latest_minimax_health_report(now=now)

    assert status["status"] == "FAIL"
    assert status["recent_pass"] is False
    assert status["transport_attempt_count"] == 2
    assert status["transport_recovered"] is True


def test_health_check_prompt_contains_no_benchmark_content() -> None:
    prompt = BATCH.MINIMAX_HEALTH_PROMPT

    assert prompt == "Return exactly MINIMAX_READY"
    assert BATCH.MINIMAX_HEALTH_MAX_TOKENS == 128
    assert "HV-" not in prompt
    assert "ALLOW" not in prompt
    assert "ESCALATE" not in prompt
    assert "SRC-" not in prompt
