from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmark_factory.batches import run_BAL100_BATCH_001_five_mini_scout as scout


def test_default_scout_prepares_prompt_cards_without_provider_calls(tmp_path: Path) -> None:
    plan = scout.build_prompt_cards(out_dir=tmp_path)

    assert plan["batch_id"] == "BAL100-BATCH-001"
    assert plan["benchmark_credit"] is False
    assert plan["official_trace"] is False
    assert plan["judge"] is False
    assert plan["freeze"] is False
    assert plan["provider_calls_performed_by_script"] is False
    assert plan["packets"] == 16
    assert plan["prompt_cards"] == 80
    assert len(list((tmp_path / "prompt_cards").glob("*.json"))) == 80


def test_prompt_cards_are_payload_only_and_non_benchmark(tmp_path: Path) -> None:
    scout.build_prompt_cards(out_dir=tmp_path)
    card_path = next((tmp_path / "prompt_cards").glob("*.json"))
    card = json.loads(card_path.read_text())
    user_payload = json.loads(card["user"])

    assert set(user_payload) == {"action", "context"}
    assert card["benchmark_credit"] is False
    assert card["official_trace"] is False
    assert card["judge_truth"] is False
    assert card["freeze"] is False
    assert "expected_verdict" not in card["user"]


def test_execute_mode_requires_taylor_local_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    for marker in scout.CO_ENV_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    monkeypatch.delenv(scout.APPROVAL_ENV, raising=False)

    with pytest.raises(SystemExit, match=scout.APPROVAL_ENV):
        scout.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--i-am-taylor-local",
                "--yes-send-draft-payloads-to-providers",
            ]
        )


def test_execute_mode_refuses_codex_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_SANDBOX", "1")
    monkeypatch.setenv(scout.APPROVAL_ENV, scout.APPROVAL_VALUE)

    with pytest.raises(SystemExit, match="Codex/Co"):
        scout.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--i-am-taylor-local",
                "--yes-send-draft-payloads-to-providers",
            ]
        )
