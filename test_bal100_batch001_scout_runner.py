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
    assert anthropic_payload["messages"][0]["role"] == "user"
    assert gemini_payload["contents"][0]["parts"][0]["text"]


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

    summary = scout._summarize_results(records, "synthetic-failed-run")
    packet_summary = summary["packet_summaries"][0]

    assert summary["run_status"] == "operational_failure"
    assert summary["repair_candidates"] == []
    assert summary["discard_candidates"] == []
    assert summary["incomplete_packets"] == [card["packet_id"]]
    assert packet_summary["error_result_refs"] == [record["result_id"] for record in records]
    assert packet_summary["incomplete"] is True
    assert all(record["model_verdict"] == "ERROR" for record in records)


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
