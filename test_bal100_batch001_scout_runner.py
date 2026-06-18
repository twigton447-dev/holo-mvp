from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from benchmark_factory.batches import run_BAL100_BATCH_001_five_mini_scout as scout


def _sample_card() -> dict:
    packet = scout._load_packets()[0]
    model = scout.MODELS[0]
    return scout._prompt_card(packet, model["provider"], model["model"])


def _assert_non_benchmark_record(record: dict) -> None:
    assert record["benchmark_credit"] is False
    assert record["official_trace"] is False
    assert record["judge"] is False
    assert record["freeze"] is False


def _set_dummy_provider_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    for model in scout.MODELS:
        monkeypatch.setenv(model["api_key_env"], "test-key")


def _fake_execution(monkeypatch: pytest.MonkeyPatch) -> dict:
    captured: dict = {}

    def fake_execute_local_scout(
        timeout: int,
        out_dir: Path = scout.OUT_DIR,
        *,
        execution_mode: str,
        operator: str,
        family_id: str | None = None,
    ) -> dict:
        captured.update(
            {
                "timeout": timeout,
                "out_dir": out_dir,
                "execution_mode": execution_mode,
                "operator": operator,
                "family_id": family_id,
            }
        )
        return {
            "run_id": "synthetic-run",
            "batch_id": scout.BATCH_ID,
            "benchmark_credit": False,
            "official_trace": False,
            "judge": False,
            "freeze": False,
            "execution_mode": execution_mode,
            "operator": operator,
        }

    monkeypatch.setattr(scout, "execute_local_scout", fake_execute_local_scout)
    return captured


def test_default_scout_prepares_prompt_cards_without_provider_calls(tmp_path: Path) -> None:
    plan = scout.build_prompt_cards(out_dir=tmp_path)

    assert plan["batch_id"] == "BAL100-BATCH-001"
    assert plan["benchmark_credit"] is False
    assert plan["official_trace"] is False
    assert plan["judge"] is False
    assert plan["freeze"] is False
    assert plan["execution_mode"] == "plan_only"
    assert plan["provider_calls_performed_by_script"] is False
    assert plan["packets"] == 16
    assert plan["prompt_cards"] == 80
    assert len(list((tmp_path / "prompt_cards").glob("*.json"))) == 80


def test_bec005_family_filter_selects_exact_pair() -> None:
    packets = scout._load_packets(family_id=scout.BEC_PAIR_005_FAMILY_ID)

    assert [packet["scenario_id"] for packet in packets] == [
        "BAL100-BEC-PAIR-005-ALLOW",
        "BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL",
    ]
    assert [packet["expected_verdict"] for packet in packets] == ["ALLOW", "ESCALATE"]


def test_bec005_filtered_prompt_cards_are_pair_only(tmp_path: Path) -> None:
    plan = scout.build_prompt_cards(out_dir=tmp_path, family_id=scout.BEC_PAIR_005_FAMILY_ID)
    prompt_files = sorted((tmp_path / "prompt_cards").glob("*.json"))

    assert plan["family_id"] == "BEC-PAIR-005"
    assert plan["packets"] == 2
    assert plan["prompt_cards"] == 10
    assert len(prompt_files) == 10
    assert all(path.name.startswith("BAL100-BEC-PAIR-005-") for path in prompt_files)


def test_unknown_family_filter_fails_closed() -> None:
    with pytest.raises(SystemExit, match="Unsupported family filter"):
        scout._load_packets(family_id="BEC-PAIR-999")


def test_incomplete_family_filter_fails_closed() -> None:
    packets = [
        packet
        for packet in scout._load_packets()
        if packet["scenario_id"] != "BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL"
    ]

    with pytest.raises(SystemExit, match="exact expected sibling pair"):
        scout._filter_packets_by_family(packets, scout.BEC_PAIR_005_FAMILY_ID)


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


def test_prompt_requires_compact_json_to_reduce_truncation_risk() -> None:
    card = _sample_card()
    system_prompt = card["system"]

    assert "Return only a compact JSON object" in system_prompt
    assert "rationale must be 1-3 concise sentences" in system_prompt
    assert "no numbered lists" in system_prompt
    assert "at most 5 artifact IDs" in system_prompt
    assert "Do not include prose, code fences, or text outside the JSON object." in system_prompt


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


def test_taylor_local_mode_still_executes_with_local_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    for marker in scout.CO_ENV_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    _set_dummy_provider_keys(monkeypatch)
    monkeypatch.setenv(scout.APPROVAL_ENV, scout.APPROVAL_VALUE)
    captured = _fake_execution(monkeypatch)

    exit_code = scout.main(
        [
            "--execute-provider-calls",
            "--operator",
            "Taylor",
            "--i-am-taylor-local",
            "--yes-send-draft-payloads-to-providers",
        ]
    )

    assert exit_code == 0
    assert captured["execution_mode"] == "taylor_local"
    assert captured["operator"] == "Taylor"


def test_taylor_local_execute_mode_forwards_family_filter_and_out_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    for marker in scout.CO_ENV_MARKERS:
        monkeypatch.delenv(marker, raising=False)
    _set_dummy_provider_keys(monkeypatch)
    monkeypatch.setenv(scout.APPROVAL_ENV, scout.APPROVAL_VALUE)
    captured = _fake_execution(monkeypatch)

    exit_code = scout.main(
        [
            "--execute-provider-calls",
            "--operator",
            "Taylor",
            "--i-am-taylor-local",
            "--yes-send-draft-payloads-to-providers",
            "--family-id",
            "BEC-PAIR-005",
            "--out-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert captured["family_id"] == "BEC-PAIR-005"
    assert captured["out_dir"] == tmp_path
    assert captured["execution_mode"] == "taylor_local"


def test_codex_execute_mode_refused_without_new_flag_or_env(monkeypatch: pytest.MonkeyPatch) -> None:
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

    monkeypatch.delenv(scout.CODEX_APPROVAL_ENV, raising=False)
    with pytest.raises(SystemExit, match=scout.CODEX_APPROVAL_ENV):
        scout.main(
            [
                "--execute-provider-calls",
                "--operator",
                "Taylor",
                "--allow-codex-provider-calls",
                "--yes-send-draft-payloads-to-providers",
            ]
        )


def test_codex_execute_mode_allowed_with_flag_and_exact_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CODEX_SANDBOX", "1")
    monkeypatch.setenv(scout.CODEX_APPROVAL_ENV, scout.CODEX_APPROVAL_VALUE)
    _set_dummy_provider_keys(monkeypatch)
    captured = _fake_execution(monkeypatch)

    exit_code = scout.main(
        [
            "--execute-provider-calls",
            "--operator",
            "Taylor",
            "--allow-codex-provider-calls",
            "--yes-send-draft-payloads-to-providers",
        ]
    )

    assert exit_code == 0
    assert captured["execution_mode"] == "codex_approved"
    assert captured["operator"] == "Taylor"


def test_http_payload_construction_does_not_require_provider_sdks() -> None:
    source = inspect.getsource(scout)

    assert "from openai import" not in source
    assert "import anthropic" not in source
    assert "from google import" not in source
    assert "google.genai" not in source

    card = _sample_card()
    openai_payload = scout._openai_compatible_payload(card, scout.MODELS[0])
    anthropic_payload = scout._anthropic_payload(card, scout.MODELS[1])
    gemini_payload = scout._gemini_payload(card)

    assert openai_payload["messages"][0]["role"] == "system"
    assert openai_payload["messages"][1]["role"] == "user"
    assert openai_payload["max_tokens"] == scout.DEFAULT_MAX_OUTPUT_TOKENS
    assert anthropic_payload["messages"][0]["role"] == "user"
    assert anthropic_payload["max_tokens"] == scout.ANTHROPIC_MAX_OUTPUT_TOKENS
    assert anthropic_payload["max_tokens"] > scout.DEFAULT_MAX_OUTPUT_TOKENS
    assert gemini_payload["contents"][0]["parts"][0]["text"]
    assert gemini_payload["generationConfig"]["maxOutputTokens"] == scout.DEFAULT_MAX_OUTPUT_TOKENS


def test_complete_fenced_json_parses_successfully() -> None:
    parsed = scout._parse_model_verdict(
        """```json
{"verdict":"ALLOW","rationale":"Callback source is compliant.","cited_artifacts":["CALLSYS-883306"]}
```"""
    )

    assert parsed["parse_ok"] is True
    assert parsed["model_verdict"] == "ALLOW"
    assert parsed["cited_artifacts"] == ["CALLSYS-883306"]


def test_unterminated_fenced_json_with_verdict_prefix_fails_closed() -> None:
    parsed = scout._parse_model_verdict(
        """```json
{"verdict":"ALLOW","rationale":"This starts as JSON but never closes."""
    )

    assert parsed["parse_ok"] is False
    assert parsed["model_verdict"] == "ERROR"
    assert "No JSON object with verdict" in parsed["parse_error"]


def test_provider_failure_preserves_error_cause(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_http(*_args, **_kwargs):
        raise scout.ProviderCallError(
            "HTTPError",
            "unauthorized scout request",
            http_status=401,
            raw_text='{"error":"unauthorized"}',
        )

    monkeypatch.setattr(scout, "_http_post_json", fail_http)
    record = scout.attempt_provider_call(_sample_card(), scout.MODELS[0], timeout=1)

    _assert_non_benchmark_record(record)
    assert record["provider_call_ok"] is False
    assert record["parse_ok"] is False
    assert record["verdict"] == "ERROR"
    assert record["error_type"] == "HTTPError"
    assert record["error_message_excerpt"] == "unauthorized scout request"
    assert record["http_status"] == 401
    assert record["raw_text_excerpt"] == '{"error":"unauthorized"}'
    assert record["result_id"]


def test_parse_failure_is_separate_from_provider_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def ok_http(*_args, **_kwargs):
        return {
            "http_status": 200,
            "raw_text": "{}",
            "json": {
                "choices": [
                    {"message": {"content": "I cannot provide a JSON verdict."}}
                ],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7},
            },
        }

    monkeypatch.setattr(scout, "_http_post_json", ok_http)
    record = scout.attempt_provider_call(_sample_card(), scout.MODELS[0], timeout=1)

    _assert_non_benchmark_record(record)
    assert record["provider_call_ok"] is True
    assert record["parse_ok"] is False
    assert record["verdict"] == "ERROR"
    assert record["parse_error"]
    assert record["raw_text_excerpt"] == "I cannot provide a JSON verdict."
    assert record["http_status"] == 200
    assert "error_type" not in record


def test_successful_provider_response_records_parsed_verdict(monkeypatch: pytest.MonkeyPatch) -> None:
    def ok_http(*_args, **_kwargs):
        return {
            "http_status": 200,
            "raw_text": "{}",
            "json": {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "verdict": "ALLOW",
                                    "rationale": "Callback source is pre-change vendor master.",
                                    "cited_artifacts": ["CALLSYS-883104"],
                                }
                            )
                        }
                    }
                ],
                "usage": {"prompt_tokens": 11, "completion_tokens": 7},
            },
        }

    monkeypatch.setattr(scout, "_http_post_json", ok_http)
    record = scout.attempt_provider_call(_sample_card(), scout.MODELS[0], timeout=1)

    _assert_non_benchmark_record(record)
    assert record["provider_call_ok"] is True
    assert record["parse_ok"] is True
    assert record["verdict"] == "ALLOW"
    assert record["input_tokens"] == 11
    assert record["output_tokens"] == 7


def test_summary_error_verdicts_link_to_detailed_rows_without_repair_signal() -> None:
    card = _sample_card()
    records = [
        scout._error_record(card, scout.MODELS[0], RuntimeError("network unavailable"), 12, "provider_call"),
        scout._error_record(card, scout.MODELS[1], RuntimeError("network unavailable"), 13, "provider_call"),
    ]

    summary = scout._summarize_results(records, "synthetic-failed-run", execution_mode="codex_approved", operator="Taylor")
    packet_summary = summary["packet_summaries"][0]

    assert summary["benchmark_credit"] is False
    assert summary["official_trace"] is False
    assert summary["judge"] is False
    assert summary["freeze"] is False
    assert summary["execution_mode"] == "codex_approved"
    assert summary["operator"] == "Taylor"
    assert summary["run_status"] == "operational_failure"
    assert summary["repair_candidates"] == []
    assert summary["discard_candidates"] == []
    assert summary["incomplete_packets"] == [card["packet_id"]]
    assert packet_summary["error_result_refs"] == [record["result_id"] for record in records]
    assert packet_summary["incomplete"] is True
    assert all(record["model_verdict"] == "ERROR" for record in records)
