from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmark_factory.batches import run_BAL100_BATCH_003_bounded_scout as scout


EXPECTED_FAMILIES = [
    "BAL100-BEC-SUBTLE-CLOSEOUT-019",
    "BAL100-BEC-SUBTLE-CLOSEOUT-020",
    "BAL100-BEC-SUBTLE-CLOSEOUT-021",
    "BAL100-BEC-SUBTLE-CLOSEOUT-022",
]
EXPECTED_PACKET_IDS = [
    "BAL100-BEC-SUBTLE-CLOSEOUT-019-A",
    "BAL100-BEC-SUBTLE-CLOSEOUT-019-B",
    "BAL100-BEC-SUBTLE-CLOSEOUT-020-A",
    "BAL100-BEC-SUBTLE-CLOSEOUT-020-B",
    "BAL100-BEC-SUBTLE-CLOSEOUT-021-A",
    "BAL100-BEC-SUBTLE-CLOSEOUT-021-B",
    "BAL100-BEC-SUBTLE-CLOSEOUT-022-A",
    "BAL100-BEC-SUBTLE-CLOSEOUT-022-B",
]


def test_static_gate_survivor_set_is_exact() -> None:
    gate = json.loads(Path("reports/BAL100_BATCH_003_static_kill_gate.json").read_text())

    assert scout.scout_ready_family_ids(gate) == EXPECTED_FAMILIES


def test_load_bounded_packets_selects_8_balanced_packets() -> None:
    packets = scout.load_bounded_packets()

    assert len(packets) == 8
    assert [packet["_builder"]["family_id"] for packet in packets][::2] == EXPECTED_FAMILIES
    assert [packet["scenario_id"] for packet in packets] == EXPECTED_PACKET_IDS
    assert [packet["expected_verdict"] for packet in packets].count("ALLOW") == 4
    assert [packet["expected_verdict"] for packet in packets].count("ESCALATE") == 4


def test_scope_validator_rejects_missing_or_extra_packet() -> None:
    packets = scout.load_bounded_packets()

    with pytest.raises(SystemExit, match="packet scope mismatch"):
        scout.validate_bounded_scope(packets[:-1])


def test_no_live_prompt_plan_writes_40_payload_only_cards(tmp_path: Path) -> None:
    plan = scout.build_prompt_cards(out_dir=tmp_path)
    prompt_files = sorted((tmp_path / "prompt_cards").glob("*.json"))

    assert plan["batch_id"] == "BAL100-BATCH-003"
    assert plan["execution_mode"] == "plan_only_no_live"
    assert plan["provider_calls_performed_by_script"] is False
    assert plan["scout_ready_family_ids"] == EXPECTED_FAMILIES
    assert plan["packets"] == 8
    assert plan["packet_ids_to_scout"] == EXPECTED_PACKET_IDS
    assert plan["expected_row_count"] == 40
    assert plan["prompt_cards"] == 40
    assert plan["proof_credit_remains_unchanged"] is True
    assert len(prompt_files) == 40

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
    out_dir = tmp_path / "batch003-live"

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
    assert len(list((out_dir / "prompt_cards").glob("*.json"))) == 40
    result_lines = (out_dir / "results.jsonl").read_text().splitlines()
    summary = json.loads((out_dir / "summary.json").read_text())
    assert len(result_lines) == 40
    assert summary["results"] == 40
    assert summary["expected_row_count"] == 40
    assert summary["scout_ready_family_ids"] == EXPECTED_FAMILIES
    assert summary["packet_ids_to_scout"] == EXPECTED_PACKET_IDS
    assert summary["benchmark_credit"] is False
    assert summary["official_trace"] is False
    assert summary["scout_only"] is True
    assert summary["diagnostic_only"] is True
    assert summary["proof_credit_remains_unchanged"] is True
    assert not list(out_dir.glob("*trace*"))


def test_transport_is_reused_from_batch001_core() -> None:
    assert scout.MODELS == scout.scout_core.MODELS
    assert scout.APPROVAL_ENV == "BAL100_BATCH003_SCOUT_APPROVED"
    assert scout.CODEX_APPROVAL_ENV == "BAL100_BATCH003_CODEX_SCOUT_APPROVED"
