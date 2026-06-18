from __future__ import annotations

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


def test_scope_validator_rejects_excluded_family() -> None:
    packets = scout.load_scout_ready_packets()
    excluded = json.loads(
        Path("holo_builder/outputs/builder/BAL100_BATCH_002_EXPLAINED_ANOMALY_014_A_draft_v0_1.json").read_text()
    )

    with pytest.raises(SystemExit, match="packet scope mismatch"):
        scout.validate_bounded_scope([*packets, excluded])


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


def _set_dummy_provider_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for model in scout.MODELS:
        monkeypatch.setenv(model["api_key_env"], "test-key")


def _set_local_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    for marker in scout.CO_ENV_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    _set_dummy_provider_keys(monkeypatch)
    monkeypatch.setenv(scout.APPROVAL_ENV, scout.APPROVAL_VALUE)


def test_execute_mode_requires_taylor_local_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    for marker in scout.CO_ENV_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    monkeypatch.delenv(scout.APPROVAL_ENV, raising=False)
    _set_dummy_provider_keys(monkeypatch)

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


def test_execute_mode_requires_payload_acknowledgement(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_local_approval(monkeypatch)

    with pytest.raises(SystemExit, match="--yes-send-draft-payloads-to-providers"):
        scout.main(["--execute-provider-calls", "--operator", "Taylor", "--i-am-taylor-local"])


def test_codex_execute_mode_requires_codex_flag_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_SANDBOX", "1")
    _set_dummy_provider_keys(monkeypatch)

    with pytest.raises(SystemExit, match="--allow-codex-provider-calls"):
        scout.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--yes-send-draft-payloads-to-providers",
            ]
        )

    with pytest.raises(SystemExit, match=scout.CODEX_APPROVAL_ENV):
        monkeypatch.setenv(scout.APPROVAL_ENV, scout.APPROVAL_VALUE)
        scout.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--allow-codex-provider-calls",
                "--yes-send-draft-payloads-to-providers",
            ]
        )


def test_live_execution_refuses_existing_output_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _set_local_approval(monkeypatch)

    with pytest.raises(SystemExit, match="already exists"):
        scout.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--i-am-taylor-local",
                "--yes-send-draft-payloads-to-providers",
                "--out-dir",
                str(tmp_path),
            ]
        )


def test_approved_live_execution_writes_results_and_summary_without_traces(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _set_local_approval(monkeypatch)
    out_dir = tmp_path / "batch002-live"

    def fake_attempt_provider_call(
        card: dict,
        model: dict,
        timeout: int,
        *,
        execution_mode: str,
        operator: str,
    ) -> dict:
        return {
            "result_id": f"{card['packet_id']}::{model['provider']}::{model['model']}",
            "batch_id": scout.BATCH_ID,
            "seam_name": scout.SEAM_NAME,
            "benchmark_credit": False,
            "official_trace": False,
            "judge": False,
            "freeze": False,
            "scout_only": True,
            "diagnostic_only": True,
            "execution_mode": execution_mode,
            "operator": operator,
            "packet_id": card["packet_id"],
            "family_id": card["family_id"],
            "builder_hypothesis": card["builder_hypothesis"],
            "provider": model["provider"],
            "model": model["model"],
            "latency_ms": 1,
            "called_at": "2026-06-18T00:00:00Z",
            "provider_call_ok": True,
            "parse_ok": True,
            "verdict": card["builder_hypothesis"],
            "model_verdict": card["builder_hypothesis"],
            "raw_text_excerpt": "{\"verdict\":\"%s\"}" % card["builder_hypothesis"],
            "http_status": 200,
            "input_tokens": 10,
            "output_tokens": 20,
            "rationale": "synthetic test record",
            "cited_artifacts": [],
            "parsed_json": {"verdict": card["builder_hypothesis"]},
        }

    monkeypatch.setattr(scout, "attempt_provider_call", fake_attempt_provider_call)

    exit_code = scout.main(
        [
            "--execute-provider-calls",
            "--operator",
            "Taylor",
            "--i-am-taylor-local",
            "--yes-send-draft-payloads-to-providers",
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert len(list((out_dir / "prompt_cards").glob("*.json"))) == 60
    result_lines = (out_dir / "results.jsonl").read_text().splitlines()
    summary = json.loads((out_dir / "summary.json").read_text())
    assert len(result_lines) == 60
    assert summary["results"] == 60
    assert summary["expected_row_count"] == 60
    assert summary["benchmark_credit"] is False
    assert summary["official_trace"] is False
    assert summary["scout_only"] is True
    assert summary["diagnostic_only"] is True
    assert summary["proof_credit_remains_unchanged"] is True
    assert not list(out_dir.glob("*trace*"))


def test_transport_is_reused_from_batch001_core() -> None:
    assert scout.MODELS == scout.scout_core.MODELS
    assert scout.APPROVAL_ENV == "BAL100_BATCH002_SCOUT_APPROVED"
    assert scout.CODEX_APPROVAL_ENV == "BAL100_BATCH002_CODEX_SCOUT_APPROVED"
