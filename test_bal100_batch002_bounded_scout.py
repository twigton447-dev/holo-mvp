from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from benchmark_factory.batches import run_BAL100_BATCH_002_bounded_scout as scout


EXPECTED_READY = [
    "BAL100-BEC-EXPLAINED-ANOMALY-011",
    "BAL100-BEC-EXPLAINED-ANOMALY-012",
    "BAL100-BEC-EXPLAINED-ANOMALY-013",
    "BAL100-BEC-EXPLAINED-ANOMALY-015",
    "BAL100-BEC-EXPLAINED-ANOMALY-017",
    "BAL100-BEC-EXPLAINED-ANOMALY-018",
]


def test_static_gate_survivor_set_is_exact() -> None:
    gate = json.loads(Path("reports/BAL100_BATCH_002_static_kill_gate.json").read_text())

    assert scout.scout_ready_family_ids(gate) == EXPECTED_READY
    assert scout.excluded_family_reasons(gate) == [
        {
            "family_id": "BAL100-BEC-EXPLAINED-ANOMALY-014",
            "classification": "repair_before_scout",
            "reason": "repair wording/source contrast before scout",
        },
        {
            "family_id": "BAL100-BEC-EXPLAINED-ANOMALY-016",
            "classification": "repair_before_scout",
            "reason": "repair wording/source contrast before scout",
        },
    ]


def test_load_scout_ready_packets_selects_12_balanced_packets() -> None:
    packets = scout.load_scout_ready_packets()

    assert len(packets) == 12
    assert [packet["_builder"]["family_id"] for packet in packets][::2] == EXPECTED_READY
    assert [packet["scenario_id"] for packet in packets] == [
        "BAL100-BEC-EXPLAINED-ANOMALY-011-A",
        "BAL100-BEC-EXPLAINED-ANOMALY-011-B",
        "BAL100-BEC-EXPLAINED-ANOMALY-012-A",
        "BAL100-BEC-EXPLAINED-ANOMALY-012-B",
        "BAL100-BEC-EXPLAINED-ANOMALY-013-A",
        "BAL100-BEC-EXPLAINED-ANOMALY-013-B",
        "BAL100-BEC-EXPLAINED-ANOMALY-015-A",
        "BAL100-BEC-EXPLAINED-ANOMALY-015-B",
        "BAL100-BEC-EXPLAINED-ANOMALY-017-A",
        "BAL100-BEC-EXPLAINED-ANOMALY-017-B",
        "BAL100-BEC-EXPLAINED-ANOMALY-018-A",
        "BAL100-BEC-EXPLAINED-ANOMALY-018-B",
    ]
    assert [packet["expected_verdict"] for packet in packets].count("ALLOW") == 6
    assert [packet["expected_verdict"] for packet in packets].count("ESCALATE") == 6


def test_no_live_prompt_plan_writes_60_payload_only_cards(tmp_path: Path) -> None:
    plan = scout.build_prompt_cards(out_dir=tmp_path)
    prompt_files = sorted((tmp_path / "prompt_cards").glob("*.json"))

    assert plan["batch_id"] == "BAL100-BATCH-002"
    assert plan["execution_mode"] == "plan_only_no_live"
    assert plan["provider_calls_performed_by_script"] is False
    assert plan["scout_ready_family_ids"] == EXPECTED_READY
    assert plan["packets"] == 12
    assert plan["expected_row_count"] == 60
    assert plan["prompt_cards"] == 60
    assert plan["proof_credit_remains_unchanged"] is True
    assert len(prompt_files) == 60

    card = json.loads(prompt_files[0].read_text())
    visible_payload = json.loads(card["user"])
    assert set(visible_payload) == {"action", "context"}
    assert card["benchmark_credit"] is False
    assert card["official_trace"] is False
    assert card["judge_truth"] is False
    assert card["freeze"] is False
    assert "expected_verdict" not in card["user"]
    assert "spec_target_verdict" not in card["user"]


def test_batch002_planner_refuses_provider_execution() -> None:
    with pytest.raises(SystemExit, match="intentionally unsupported"):
        scout.main(["--execute-provider-calls"])


def test_batch002_planner_has_no_provider_transport_code() -> None:
    source = inspect.getsource(scout)

    assert "urlopen" not in source
    assert "api.openai.com" not in source
    assert "generativelanguage.googleapis.com" not in source
    assert "api.x.ai" not in source
    assert "api.minimax.io" not in source
    assert "x-api-key" not in source
