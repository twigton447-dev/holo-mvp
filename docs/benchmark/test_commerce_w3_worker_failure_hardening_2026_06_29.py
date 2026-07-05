#!/usr/bin/env python3
"""No-provider fixtures for Commerce W3 worker truncation hardening."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

BASE_RUNNER_PATH = BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py"
AP_RUNNER_PATH = BENCHMARK_ROOT / "run_ap_replication_holoverify_3dna_2026_06_29.py"
COMMERCE_RUNNER_PATH = BENCHMARK_ROOT / "run_commerce_replication_holoverify_3dna_2026_06_29.py"
COMMERCE_ROOT = BENCHMARK_ROOT / "holoverify_agentic_commerce_replication_2026-06-29"
AUTOPSY_JSON = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_W3_WORKER_TRUNCATION_AUTOPSY_2026_06_29.json"
PREFLIGHT_JSON = COMMERCE_ROOT / "COMMERCE_OPENAI_W2_LIVE_HOLO_PREFLIGHT_2026_06_29.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("commerce_w3_base_runner_fixture", BASE_RUNNER_PATH)
AP = load_module("commerce_w3_ap_runner_fixture", AP_RUNNER_PATH)
COMMERCE = load_module("commerce_w3_wrapper_fixture", COMMERCE_RUNNER_PATH)


def assert_raises_contains(fn, needle: str) -> None:
    try:
        fn()
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        if needle not in message:
            raise AssertionError(f"expected {needle!r} in {message!r}") from exc
        return
    raise AssertionError(f"expected exception containing {needle!r}")


def compact_worker_fixture() -> str:
    return "\n".join(
        [
            "worker_role=FINAL_COMPILER",
            "verification_verdict=ALLOW",
            "binding_class=SOURCE_BOUNDARY_CLOSED",
            "action_boundary=fixture action boundary",
            "allow_rule_assessment=current source closes the boundary",
            "escalate_rule_assessment=no open escalation defect remains",
            "dependency_check=timing scope authority and dependency closed",
            "controlling_source_fact=SRC-FIXTURE-CTL",
            "cited_evidence=SRC-FIXTURE-CTL|SRC-FIXTURE-BND",
            "open_blockers=",
            "critical_features_preserved=source IDs|action boundary|critical terms",
            "final_answer=Action may proceed because the fixture source control closes the exact execution boundary and no dependency remains open.",
        ]
    )


def test_openai_compatible_preserves_raw_text_when_filter_strips_visible_text() -> None:
    original_http_json = RUNNER._http_json

    def fake_http_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int = 150) -> dict[str, Any]:
        return {
            "id": "cmpl-fixture",
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "<think>hidden analysis consumed the budget</think>"},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 3600, "total_tokens": 3610},
        }

    try:
        RUNNER._http_json = fake_http_json
        response = RUNNER._call_openai_compatible(
            {
                "provider": "minimax",
                "model": "MiniMax-M2.5-highspeed",
                "api_key_env": "MINIMAX_API_KEY",
                "default_url": "https://api.minimax.io/v1/text/chatcompletion_v2",
            },
            [{"role": "user", "content": "fixture"}],
            max_tokens=6000,
        )
    finally:
        RUNNER._http_json = original_http_json

    assert response["raw_text"] == "<think>hidden analysis consumed the budget</think>"
    assert response["text"] == ""
    assert response["text_stripped_by_thinking_filter"] is True
    assert response["finish_reason"] == "length"
    assert response["output_tokens"] == 3600


def test_openai_responses_w2_preserves_raw_text_when_filter_strips_visible_text() -> None:
    class FakeHTTPResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return json.dumps(
                {
                    "id": "resp-fixture",
                    "status": "completed",
                    "output": [
                        {
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": "<think>hidden analysis</think>" + compact_worker_fixture(),
                                }
                            ]
                        }
                    ],
                    "usage": {"input_tokens": 11, "output_tokens": 222, "total_tokens": 233},
                }
            ).encode("utf-8")

    original_urlopen = AP.urllib.request.urlopen
    try:
        AP.urllib.request.urlopen = lambda _req, timeout=240: FakeHTTPResponse()
        response = AP._call_openai_responses_once(
            {
                "provider": "openai",
                "model": "gpt-5.4-mini",
                "api_key_env": "OPENAI_API_KEY",
            },
            [{"role": "user", "content": "fixture"}],
            max_tokens=3600,
        )
    finally:
        AP.urllib.request.urlopen = original_urlopen

    assert response["raw_text"].startswith("<think>hidden analysis</think>")
    assert response["text"].startswith("worker_role=FINAL_COMPILER")
    assert response["text_stripped_by_thinking_filter"] is True
    assert response["output_tokens"] == 222


def test_length_empty_worker_response_remains_invalid_and_non_retryable() -> None:
    response = {
        "text": "",
        "raw_text": "<think>hidden analysis consumed the budget</think>",
        "finish_reason": "length",
        "output_tokens": 3600,
    }
    assert RUNNER._is_retryable_empty_worker_response(response) is False
    assert_raises_contains(lambda: RUNNER._worker_from_response(response), "worker_finish_reason_length_empty_text")


def test_valid_compact_worker_output_still_parses() -> None:
    parsed = RUNNER._worker_from_response({"text": compact_worker_fixture(), "finish_reason": "stop"})
    assert parsed["verification_verdict"] == "ALLOW"
    assert parsed["boundary_binding"]["binding_class"] == "SOURCE_BOUNDARY_CLOSED"
    assert parsed["_worker_output_format"] == "compact_key_value_v1"


def test_minimax_final_compiler_gets_larger_budget_only_for_w3() -> None:
    minimax_config = {"provider": "minimax", "model": "MiniMax-M2.5-highspeed"}
    xai_config = {"provider": "xai", "model": "grok-3-mini"}
    final_worker = {"worker_index": 3, "role_name": "FINAL_COMPILER"}
    mapper_worker = {"worker_index": 1, "role_name": "SOURCE_BOUNDARY_MAPPER"}

    assert RUNNER._worker_max_tokens(final_worker, minimax_config) == 6000
    assert RUNNER._worker_max_tokens(mapper_worker, minimax_config) == RUNNER.WORKER_MAX_TOKENS
    assert RUNNER._worker_max_tokens(final_worker, xai_config) == RUNNER.WORKER_MAX_TOKENS


def test_worker_contract_and_prompt_forbid_hidden_reasoning_before_contract() -> None:
    rules = " ".join(RUNNER._worker_contract()["rules"])
    assert "Do not emit hidden reasoning" in rules
    assert "first output characters must be worker_role=" in rules

    pair = {"pair_id": "HV-ACOM-REP-FIXTURE", "spec": {"boundary": "fixture boundary"}}
    packet = {"packet_id": "HV-ACOM-REP-FIXTURE-A"}
    worker = {
        "worker_index": 3,
        "role_name": "FINAL_COMPILER",
        "config": {"provider": "minimax", "model": "MiniMax-M2.5-highspeed"},
    }
    messages, _prompt_obj = RUNNER._build_worker_messages(
        "fixture-run",
        pair,
        packet,
        {"action": {"description": "fixture"}, "context": {"internal_documents": [], "policy_documents": []}},
        worker,
        {"unresolved_dependencies": []},
        {"route_verdict": "CONTINUE_WORKER", "must_repair": ["repair fixture gate"], "blocked_moves": [], "dependency_ledger": []},
        [],
    )
    system = messages[0]["content"]
    assert "Do not emit hidden reasoning" in system
    assert "Start immediately with worker_role=" in system


def test_commerce_invalid_run_autopsy_preserves_original_w3_failure() -> None:
    assert AUTOPSY_JSON.exists(), AUTOPSY_JSON
    autopsy = json.loads(AUTOPSY_JSON.read_text())
    root = autopsy["root_failure"]
    assert autopsy["invalid_run_preserved"] is True
    assert root["turn_id"] == "HV-ACOM-REP-005-A_W3"
    assert root["provider"] == "minimax"
    assert root["model"] == "MiniMax-M2.5-highspeed"
    assert root["role_name"] == "FINAL_COMPILER"
    assert root["finish_reason"] == "length"
    assert root["output_tokens"] == 3600
    assert root["visible_text"] == ""
    assert root["raw_text_preserved_in_invalid_run"] is False
    assert root["error"] == "ValueError: worker_finish_reason_length_empty_text"


def test_commerce_preflight_artifact_declares_no_providers_and_openai_w2() -> None:
    assert PREFLIGHT_JSON.exists(), PREFLIGHT_JSON
    preflight = json.loads(PREFLIGHT_JSON.read_text())
    assert preflight["status"] == "PASS"
    assert preflight["providers_called"] == 0
    assert preflight["judges_started"] is False
    assert preflight["solo_started"] is False
    assert preflight["runner_binding"]["actual_w2_model"] == "gpt-5.4-mini"
    assert preflight["expected_counts"]["holo_calls"] == 200
    assert preflight["checks"]["generic_worker_max_tokens"] is True
    assert preflight["checks"]["minimax_final_compiler_worker_max_tokens"] is True
    assert preflight["checks"]["minimax_final_compiler_budget_active"] is True
    assert preflight["runtime_contracts"]["generic_worker_max_tokens"] == 3600
    assert preflight["runtime_contracts"]["minimax_final_compiler_worker_max_tokens"] == 6000


def main() -> int:
    tests = [
        test_openai_compatible_preserves_raw_text_when_filter_strips_visible_text,
        test_openai_responses_w2_preserves_raw_text_when_filter_strips_visible_text,
        test_length_empty_worker_response_remains_invalid_and_non_retryable,
        test_valid_compact_worker_output_still_parses,
        test_minimax_final_compiler_gets_larger_budget_only_for_w3,
        test_worker_contract_and_prompt_forbid_hidden_reasoning_before_contract,
        test_commerce_invalid_run_autopsy_preserves_original_w3_failure,
        test_commerce_preflight_artifact_declares_no_providers_and_openai_w2,
    ]
    for test in tests:
        test()
    print(
        json.dumps(
            {
                "classification": "COMMERCE_W3_WORKER_FAILURE_HARDENING_NO_PROVIDER_TEST",
                "status": "PASS",
                "tests": [test.__name__ for test in tests],
                "provider_calls": 0,
                "judge_calls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
