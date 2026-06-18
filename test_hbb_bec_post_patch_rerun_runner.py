from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmark_factory.batches import run_HBB_BEC_post_patch_4dna_rerun as runner


EXPECTED_PACKET_IDS = [
    "HBB-BEC-001",
    "HBB-BEC-001-CALLBACK-PROVENANCE-FAIL",
    "HBB-BEC-002-HARD-ALLOW",
    "HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL",
]


def _set_dummy_provider_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = set()
    for family in runner.EXPECTED_FAMILIES:
        roster = runner.build_roster(family["session_id"])
        for model in [*runner.active_roster_models(roster), roster["holo_gov"]]:
            env = runner._transport_model(model)["api_key_env"]
            if env not in seen:
                monkeypatch.setenv(env, "test-key")
                seen.add(env)


def _set_local_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    for marker in runner.CO_ENV_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    _set_dummy_provider_keys(monkeypatch)
    monkeypatch.setenv(runner.APPROVAL_ENV, runner.APPROVAL_VALUE)


def test_expected_packet_hash_mapping_matches_preflight_records() -> None:
    mapping = runner.expected_packet_hash_mapping()

    assert list(mapping) == EXPECTED_PACKET_IDS
    assert mapping["HBB-BEC-001"]["payload_hash"] == "8181d83ceb7f36f97160f078a4d4d35bdced5555fba5478c55bd3d954f40c4f1"
    assert mapping["HBB-BEC-001-CALLBACK-PROVENANCE-FAIL"]["hash8"] == "807468fc"
    assert mapping["HBB-BEC-002-HARD-ALLOW"]["path"].endswith("HBB-BEC-002-HARD-ALLOW_f7986fa2.json")
    assert mapping["HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL"]["role"] == "ESCALATE"


def test_approved_frozen_packets_load_with_exact_scope_and_hashes() -> None:
    packets = runner.load_approved_frozen_packets()

    assert [packet["scenario_id"] for packet in packets] == EXPECTED_PACKET_IDS
    assert [packet["family_id"] for packet in packets] == [
        "HBB-BEC-001",
        "HBB-BEC-001",
        "HBB-BEC-002-HARD",
        "HBB-BEC-002-HARD",
    ]
    assert all(packet["model_visible_keys"] == ["action", "context"] for packet in packets)
    assert all(packet["frozen_approved_by"] == "Taylor" for packet in packets)


def test_scope_validator_rejects_changed_hash() -> None:
    records = runner._all_expected_packet_records()
    records[0] = dict(records[0])
    records[0]["hash"] = "0" * 64

    with pytest.raises(SystemExit, match="scope mismatch"):
        runner.validate_approved_scope(records)


def test_seed447_roster_matches_original_hbb_shape() -> None:
    roster = runner.build_roster("HBB-BEC-001_pair_4dna_seed447_post_patch")

    assert roster["holo_gov"]["provider"] == "openai"
    assert [model["provider"] for model in roster["active_non_gov"]] == ["xai", "google", "minimax"]
    assert [model["provider"] for model in roster["excluded"]] == ["anthropic"]
    assert runner.expected_call_count() == 16


def test_google_roster_provider_routes_to_gemini_transport() -> None:
    roster = runner.build_roster("HBB-BEC-001_pair_4dna_seed447_post_patch")
    google_model = [model for model in roster["active_non_gov"] if model["provider"] == "google"][0]
    transport = runner._transport_model(google_model)

    assert transport["provider"] == "gemini"
    assert transport["api_key_env"] == "GOOGLE_API_KEY"


def test_no_live_plan_writes_prompt_cards_without_answer_key(tmp_path: Path) -> None:
    plan = runner.build_prompt_cards(tmp_path)
    prompt_files = sorted((tmp_path / "prompt_cards").glob("*.json"))

    assert plan["execution_mode"] == "plan_only_no_live"
    assert plan["provider_calls_performed_by_script"] is False
    assert plan["post_patch_rerun"] is True
    assert plan["original_trace"] is False
    assert plan["official_trace"] is False
    assert plan["expected_row_count"] == 16
    assert plan["prompt_cards"] == 16
    assert plan["proof_credit_remains_unchanged"] is True
    assert len(prompt_files) == 16

    active_card = json.loads([path for path in prompt_files if "__xai__" in path.name][0].read_text())
    visible = json.loads(active_card["user"])
    assert set(visible) == {"action", "context"}
    assert "expected_verdict" not in active_card["user"]
    assert "_frozen" not in active_card["user"]

    gov_card = json.loads([path for path in prompt_files if "__hologov__" in path.name][0].read_text())
    gov_visible = json.loads(gov_card["user"])
    assert set(gov_visible) == {"action", "context", "active_non_gov_responses"}
    assert gov_visible["active_non_gov_responses"] == []


def test_execute_mode_requires_taylor_local_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    for marker in runner.CO_ENV_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    monkeypatch.delenv(runner.APPROVAL_ENV, raising=False)
    _set_dummy_provider_keys(monkeypatch)

    with pytest.raises(SystemExit, match=runner.APPROVAL_ENV):
        runner.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--i-am-taylor-local",
                "--yes-send-frozen-payloads-to-providers",
            ]
        )


def test_execute_mode_requires_frozen_payload_acknowledgement(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_local_approval(monkeypatch)

    with pytest.raises(SystemExit, match="--yes-send-frozen-payloads-to-providers"):
        runner.main(["--execute-provider-calls", "--operator", "Taylor", "--i-am-taylor-local"])


def test_codex_execute_mode_requires_codex_flag_and_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_SANDBOX", "1")
    _set_dummy_provider_keys(monkeypatch)
    monkeypatch.setenv(runner.APPROVAL_ENV, runner.APPROVAL_VALUE)
    monkeypatch.delenv(runner.CODEX_APPROVAL_ENV, raising=False)

    with pytest.raises(SystemExit, match="--allow-codex-provider-calls"):
        runner.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--yes-send-frozen-payloads-to-providers",
            ]
        )

    with pytest.raises(SystemExit, match=runner.CODEX_APPROVAL_ENV):
        runner.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--allow-codex-provider-calls",
                "--yes-send-frozen-payloads-to-providers",
            ]
        )


def test_live_execution_refuses_existing_output_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _set_local_approval(monkeypatch)

    with pytest.raises(SystemExit, match="already exists"):
        runner.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--i-am-taylor-local",
                "--yes-send-frozen-payloads-to-providers",
                "--out-dir",
                str(tmp_path),
            ]
        )


def test_approved_live_execution_writes_post_patch_outputs_without_original_traces(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _set_local_approval(monkeypatch)
    out_dir = tmp_path / "hbb-post-patch-live"

    def fake_attempt_provider_call(
        card: dict,
        roster_model: dict,
        timeout: int,
        *,
        execution_mode: str,
        operator: str,
    ) -> dict:
        verdict_key = "final_verdict" if card["role"] == "holo_gov" else "verdict"
        parsed = {verdict_key: "ALLOW", "evidence": [], "reasoning": "synthetic test record"}
        return {
            "result_id": f"{card['packet_id']}::{card['role']}::{roster_model['provider']}::{roster_model['model']}",
            "run_id": runner.RUN_ID,
            "run_type": runner.RUN_TYPE,
            "post_patch_rerun": True,
            "original_trace": False,
            "official_trace": False,
            "judge": False,
            "qa_or_ablation": False,
            "freeze": False,
            "benchmark_credit": False,
            "execution_mode": execution_mode,
            "operator": operator,
            "packet_id": card["packet_id"],
            "packet_hash": card["packet_hash"],
            "hash8": card["hash8"],
            "family_id": card["family_id"],
            "packet_role": card["packet_role"],
            "role": card["role"],
            "provider": roster_model["provider"],
            "transport_provider": runner._transport_provider(roster_model["provider"]),
            "model": roster_model["model"],
            "latency_ms": 1,
            "called_at": "2026-06-18T00:00:00Z",
            "provider_call_ok": True,
            "parse_ok": True,
            "verdict": "ALLOW",
            "raw_text_excerpt": json.dumps(parsed),
            "http_status": 200,
            "input_tokens": 10,
            "output_tokens": 20,
            "parsed_json": parsed,
        }

    monkeypatch.setattr(runner, "attempt_provider_call", fake_attempt_provider_call)

    exit_code = runner.main(
        [
            "--execute-provider-calls",
            "--operator",
            "Taylor",
            "--i-am-taylor-local",
            "--yes-send-frozen-payloads-to-providers",
            "--out-dir",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert len((out_dir / "results.jsonl").read_text().splitlines()) == 16
    assert len(list((out_dir / "prompt_cards").glob("*.json"))) == 16
    packet_records = sorted((out_dir / "post_patch_rerun_records").glob("*.json"))
    assert len(packet_records) == 4

    summary = json.loads((out_dir / "summary.json").read_text())
    assert summary["results"] == 16
    assert summary["expected_row_count"] == 16
    assert summary["post_patch_rerun"] is True
    assert summary["original_trace"] is False
    assert summary["official_trace"] is False
    assert summary["proof_credit_remains_unchanged"] is True

    packet_record = json.loads(packet_records[0].read_text())
    assert packet_record["trace_type"] == "holo_4dna_mini_frozen_pair_post_patch_rerun"
    assert packet_record["post_patch_rerun"] is True
    assert packet_record["original_trace"] is False
    assert packet_record["official_trace"] is False
    assert len(packet_record["calls"]["active_non_gov"]) == 3
    assert packet_record["calls"]["holo_gov"]["role"] == "holo_gov"


def test_prompt_patch_rules_are_sourced_from_llm_adapters_text() -> None:
    analyst = runner.analyst_system_prompt().lower()
    gov = runner.gov_system_prompt().lower()

    assert "elevated scrutiny triggers" in analyst
    assert "not payment blockers after" in analyst
    assert "number_source" in gov
    assert "portal_change_record" in gov
    assert "completed ap signoff" in gov
    assert "cannot override" in gov
