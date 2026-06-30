#!/usr/bin/env python3
"""No-provider fixtures for AP OpenAI-W2 invalid-run handling."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import urllib.error
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("holo_3dna_runner_invalid_fixture", BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py")
AP = load_module("ap_runner_invalid_fixture", BENCHMARK_ROOT / "run_ap_replication_holoverify_3dna_2026_06_29.py")


def assert_raises_contains(fn, needle: str) -> None:
    try:
        fn()
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        if needle not in message:
            raise AssertionError(f"expected {needle!r} in {message!r}") from exc
        return
    raise AssertionError(f"expected exception containing {needle!r}")


def freeze_fingerprint() -> tuple[list[str], list[str]]:
    freeze = AP.read_freeze()
    packets = sorted(row["packet_file_sha256"] for row in freeze["records"])
    prompts = sorted(row["prompt_file_sha256"] for row in freeze["records"])
    if len(packets) != 40 or len(prompts) != 40:
        raise AssertionError("AP freeze should contain 40 packet hashes and 40 prompt hashes")
    return packets, prompts


def test_gov_empty_text_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response({"text": "", "finish_reason": "stop"}),
        "gov_empty_text",
    )


def test_gov_length_incomplete_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response({"text": "verdict=ALLOW route=FINAL_COMPILER", "finish_reason": "length"}),
        "gov_finish_reason_length_incomplete_baton",
    )


def valid_gov_v2_baton() -> str:
    return "\n".join(
        [
            "verdict=CONTINUE",
            "dep=GATE",
            "focus=GATE_REPAIR",
            "objective=REPAIR_GATE",
            "preserve=CLOSED",
            "repair=GATE_FIELDS",
            "block=FINAL_ON_FAIL",
        ]
    )


def test_valid_gov_v2_baton_parses() -> None:
    parsed = RUNNER._gov_from_response(
        {
            "text": valid_gov_v2_baton(),
            "finish_reason": "stop",
        }
    )
    assert parsed["gov_baton_version"] == "gov_micro_baton_v2"
    assert parsed["verdict"] == "CONTINUE"
    assert parsed["dep"] == "GATE"
    assert parsed["focus"] == "GATE_REPAIR"
    assert parsed["objective"] == "REPAIR_GATE"
    assert parsed["preserve"] == "CLOSED"
    assert parsed["repair"] == "GATE_FIELDS"
    assert parsed["block"] == "FINAL_ON_FAIL"


def test_gov_v2_placeholder_token_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response(
            {
                "text": valid_gov_v2_baton().replace("preserve=CLOSED", "preserve=wb_code"),
                "finish_reason": "stop",
            }
        ),
        "gov_micro_v2_placeholder_token:preserve:wb_code",
    )


def test_gov_v2_long_prose_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response(
            {
                "text": "\n".join(
                    [
                        "verdict=CONTINUE",
                        "dep=GATE",
                        "focus=GATE_REPAIR",
                        "objective=REPAIR_GATE",
                        "preserve=CLOSED",
                        "repair=Repair deterministic gate failures while preserving source boundary",
                        "block=FINAL_ON_FAIL",
                    ]
                ),
                "finish_reason": "stop",
            }
        ),
        "gov_micro_v2_field_too_long:repair",
    )


def test_gov_v2_truncated_missing_fields_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response(
            {
                "text": "\n".join(
                    [
                        "verdict=CONTINUE",
                        "dep=GATE",
                        "focus=GATE_REPAIR",
                        "objective=REPAIR_GATE",
                    ]
                ),
                "finish_reason": "stop",
            }
        ),
        "gov_micro_v2_missing_keys:preserve,repair,block",
    )


def test_gov_v2_missing_dep_focus_objective_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response(
            {
                "text": "\n".join(
                    [
                        "verdict=CONTINUE",
                        "preserve=CLOSED",
                        "repair=GATE_FIELDS",
                        "block=FINAL_ON_FAIL",
                    ]
                ),
                "finish_reason": "stop",
            }
        ),
        "gov_micro_v2_missing_keys:dep,focus,objective",
    )


def test_gov_v2_unknown_enum_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response(
            {"text": valid_gov_v2_baton().replace("focus=GATE_REPAIR", "focus=WRITE_LONG_MEMO"), "finish_reason": "stop"}
        ),
        "gov_micro_v2_unknown_enum:focus:WRITE_LONG_MEMO",
    )


def test_gov_v2_finish_reason_length_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response({"text": valid_gov_v2_baton(), "finish_reason": "length"}),
        "gov_finish_reason_length_incomplete_baton",
    )


def test_gov_v2_json_or_quotes_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response({"text": '{"verdict":"CONTINUE"}', "finish_reason": "stop"}),
        "gov_micro_v2_forbidden_punctuation",
    )


def test_gov_v2_markdown_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._gov_from_response({"text": f"```text\n{valid_gov_v2_baton()}\n```", "finish_reason": "stop"}),
        "gov_micro_v2_markdown_present",
    )


def test_invalid_summary_without_architecture_lock_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        trace_path = run_dir / "TRACE_CALLS.jsonl"
        row = {
            "turn_id": "HV-AP-REP-017-B_G1",
            "packet_id": "HV-AP-REP-017-B",
            "pair_id": "HV-AP-REP-017",
            "call_kind": "gov",
            "provider": "minimax",
            "model": "MiniMax-M2.5-highspeed",
            "dna": "minimax",
            "gov_index": 1,
            "provider_call_ok": True,
            "parse_ok": False,
            "admissible": False,
            "finish_reason": "length",
            "error": "ValueError: gov_finish_reason_length_empty_text",
            "input_tokens": 168,
            "output_tokens": 384,
            "total_tokens": 552,
            "received_gate_result": True,
        }
        trace_path.write_text(json.dumps(row, sort_keys=True) + "\n")
        manifest = {
            "root_signature": "fixture-root",
            "model_roster_declared": {
                "worker_sequence": [
                    {"worker_index": 1, "provider": "xai", "model": "grok-3-mini", "dna": "xai"},
                    {"worker_index": 2, "provider": "openai", "model": "gpt-5.4-mini", "dna": "openai"},
                    {"worker_index": 3, "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
                ],
                "gov_sequence": [
                    {"slot": "G1", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
                    {"slot": "G2", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
                ],
            },
            "expected_counts": {"holo_calls": 200, "packets": 40, "judge_calls": 0},
        }
        summary = AP.holo_summary(run_dir, manifest, [], trace_path)
        if summary["readiness_passed"] is not False:
            raise AssertionError("invalid fixture summary should not pass readiness")
        if summary["invalidation_reason"] != "GOV_CONTRACT_OR_TRUNCATION_FAILURE":
            raise AssertionError(summary["invalidation_reason"])
        if summary["root_failure"]["turn_id"] != "HV-AP-REP-017-B_G1":
            raise AssertionError(summary["root_failure"])
        if not (run_dir / "live_results.json").exists():
            raise AssertionError("summary JSON was not written")
        if not (run_dir / "live_summary.md").exists():
            raise AssertionError("summary Markdown was not written")


def test_gov_provider_failure_summary_precedes_gov_contract_failure() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp)
        trace_path = run_dir / "TRACE_CALLS.jsonl"
        row = {
            "turn_id": "HV-ACOM-REP-013-A_G1",
            "packet_id": "HV-ACOM-REP-013-A",
            "pair_id": "HV-ACOM-REP-013",
            "call_kind": "gov",
            "provider": "minimax",
            "model": "MiniMax-M2.5-highspeed",
            "dna": "minimax",
            "gov_index": 1,
            "provider_call_ok": False,
            "parse_ok": False,
            "admissible": False,
            "finish_reason": None,
            "error": "URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>",
            "received_gate_result": True,
        }
        trace_path.write_text(json.dumps(row, sort_keys=True) + "\n")
        manifest = {
            "root_signature": "fixture-root",
            "model_roster_declared": {
                "worker_sequence": [
                    {"worker_index": 1, "provider": "xai", "model": "grok-3-mini", "dna": "xai"},
                    {"worker_index": 2, "provider": "openai", "model": "gpt-5.4-mini", "dna": "openai"},
                    {"worker_index": 3, "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
                ],
                "gov_sequence": [
                    {"slot": "G1", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
                    {"slot": "G2", "provider": "minimax", "model": "MiniMax-M2.5-highspeed", "dna": "minimax"},
                ],
            },
            "expected_counts": {"holo_calls": 200, "packets": 40, "judge_calls": 0},
        }
        original_family = AP.AP_FAMILY_ID
        try:
            AP.AP_FAMILY_ID = "HV-ACOM-REP-2026-06-29"
            summary = AP.holo_summary(run_dir, manifest, [], trace_path)
        finally:
            AP.AP_FAMILY_ID = original_family
        if summary["readiness_passed"] is not False:
            raise AssertionError("invalid fixture summary should not pass readiness")
        if summary["invalidation_reason"] != "PROVIDER_FAILURE":
            raise AssertionError(summary["invalidation_reason"])
        if summary["classification"] != "HOLOVERIFY_COMMERCE_REPLICATION_HOLO_INVALID_OR_INCOMPLETE":
            raise AssertionError(summary["classification"])
        if summary["root_failure"]["turn_id"] != "HV-ACOM-REP-013-A_G1":
            raise AssertionError(summary["root_failure"])


def test_retry_classifies_transport_only() -> None:
    retryable_http = urllib.error.HTTPError(
        "https://example.invalid",
        503,
        "Service Unavailable",
        hdrs=None,
        fp=io.BytesIO(b"temporary outage"),
    )
    retryable = RUNNER._classify_transport_exception(retryable_http)
    assert retryable and retryable["retryable"] is True
    assert retryable["class"] == "HTTP_503"

    non_retryable_http = urllib.error.HTTPError(
        "https://example.invalid",
        400,
        "Bad Request",
        hdrs=None,
        fp=io.BytesIO(b"bad request"),
    )
    non_retryable = RUNNER._classify_transport_exception(non_retryable_http)
    assert non_retryable and non_retryable["retryable"] is False
    assert non_retryable["class"] == "HTTP_400"

    timeout = RUNNER._classify_transport_exception(TimeoutError("The read operation timed out"))
    assert timeout and timeout["retryable"] is True
    assert timeout["class"] == "READ_TIMEOUT"

    dns_failure = RUNNER._classify_transport_exception(
        urllib.error.URLError(OSError(8, "nodename nor servname provided, or not known"))
    )
    assert dns_failure and dns_failure["retryable"] is True
    assert dns_failure["class"] == "DNS_RESOLUTION_ERROR"

    content_failure = RUNNER._classify_transport_exception(ValueError("gov_empty_text"))
    if content_failure is not None:
        raise AssertionError("content/model failures must not classify as transport")


def test_transport_retry_success_marks_recovered() -> None:
    calls = {"count": 0}
    original_sleep = RUNNER._transport_sleep
    RUNNER._transport_sleep = lambda _seconds: None
    try:
        def call_once() -> dict[str, object]:
            calls["count"] += 1
            if calls["count"] == 1:
                raise TimeoutError("The read operation timed out")
            return {"text": "OK", "finish_reason": "stop"}

        response = RUNNER._call_with_transport_retry(
            call_once,
            provider="openai",
            model="gpt-5.4-mini",
            timeout_seconds=240,
        )
    finally:
        RUNNER._transport_sleep = original_sleep
    if response["transport_attempt_count"] != 2:
        raise AssertionError(response)
    if response["transport_recovered"] is not True:
        raise AssertionError(response)
    if response["transport_retry_failures"][0]["class"] != "READ_TIMEOUT":
        raise AssertionError(response)


def test_transport_retry_dns_success_marks_recovered() -> None:
    calls = {"count": 0}
    original_sleep = RUNNER._transport_sleep
    RUNNER._transport_sleep = lambda _seconds: None
    try:
        def call_once() -> dict[str, object]:
            calls["count"] += 1
            if calls["count"] == 1:
                raise urllib.error.URLError(OSError(8, "nodename nor servname provided, or not known"))
            return {"text": "OK", "finish_reason": "stop"}

        response = RUNNER._call_with_transport_retry(
            call_once,
            provider="minimax",
            model="MiniMax-M2.5-highspeed",
            timeout_seconds=150,
        )
    finally:
        RUNNER._transport_sleep = original_sleep
    if response["transport_attempt_count"] != 2:
        raise AssertionError(response)
    if response["transport_recovered"] is not True:
        raise AssertionError(response)
    if response["transport_retry_failures"][0]["class"] != "DNS_RESOLUTION_ERROR":
        raise AssertionError(response)


def test_transport_retry_exhaustion_fails_closed() -> None:
    original_sleep = RUNNER._transport_sleep
    RUNNER._transport_sleep = lambda _seconds: None
    try:
        try:
            RUNNER._call_with_transport_retry(
                lambda: (_ for _ in ()).throw(TimeoutError("The read operation timed out")),
                provider="openai",
                model="gpt-5.4-mini",
                timeout_seconds=240,
            )
        except RUNNER.TransportFailureAfterRetries as exc:
            metadata = exc.metadata
            if metadata["transport_attempt_count"] != 3:
                raise AssertionError(metadata)
            if metadata["transport_final_failure_class"] != "READ_TIMEOUT":
                raise AssertionError(metadata)
            if len(metadata["transport_retry_failures"]) != 3:
                raise AssertionError(metadata)
            return
        raise AssertionError("transport retry exhaustion should fail closed")
    finally:
        RUNNER._transport_sleep = original_sleep


def test_empty_worker_response_classifier_is_narrow() -> None:
    exact_empty = {"text": "", "finish_reason": "", "output_tokens": 0}
    if RUNNER._is_retryable_empty_worker_response(exact_empty) is not True:
        raise AssertionError(exact_empty)

    markdown_failure = {"text": "```json\n{}\n```", "finish_reason": "stop", "output_tokens": 5}
    if RUNNER._is_retryable_empty_worker_response(markdown_failure) is not False:
        raise AssertionError(markdown_failure)

    length_failure = {"text": "", "finish_reason": "length", "output_tokens": 0}
    if RUNNER._is_retryable_empty_worker_response(length_failure) is not False:
        raise AssertionError(length_failure)

    hidden_or_unreported_output = {"text": "", "finish_reason": "stop", "output_tokens": None}
    if RUNNER._is_retryable_empty_worker_response(hidden_or_unreported_output) is not False:
        raise AssertionError(hidden_or_unreported_output)


def test_empty_worker_output_retry_success_marks_recovered() -> None:
    calls = {"count": 0}
    original_call_model = RUNNER._call_model
    original_sleep = RUNNER._empty_worker_output_sleep
    RUNNER._empty_worker_output_sleep = lambda _seconds: None
    try:
        def fake_call_model(config, messages, max_tokens):
            calls["count"] += 1
            if calls["count"] == 1:
                return {
                    "text": "",
                    "finish_reason": "",
                    "response_id": "empty-fixture-1",
                    "input_tokens": 10,
                    "output_tokens": 0,
                    "total_tokens": 10,
                    "transport_attempt_count": 1,
                    "transport_recovered": False,
                    "transport_retry_failures": [],
                }
            return {
                "text": compact_worker_fixture(),
                "finish_reason": "stop",
                "response_id": "ok-fixture-2",
                "input_tokens": 11,
                "output_tokens": 150,
                "total_tokens": 161,
                "transport_attempt_count": 1,
                "transport_recovered": False,
                "transport_retry_failures": [],
            }

        RUNNER._call_model = fake_call_model
        response = RUNNER._call_worker_model_with_empty_output_retry(
            {"provider": "xai", "model": "grok-3-mini"},
            [{"role": "user", "content": "fixture"}],
            max_tokens=800,
            turn_id="HV-AP-REP-FIXTURE-A_W1",
        )
    finally:
        RUNNER._call_model = original_call_model
        RUNNER._empty_worker_output_sleep = original_sleep
    if response["empty_worker_output_attempt_count"] != 2:
        raise AssertionError(response)
    if response["empty_worker_output_recovered"] is not True:
        raise AssertionError(response)
    if response["empty_worker_output_retry_failures"][0]["class"] != "EMPTY_WORKER_TEXT_ZERO_OUTPUT_TOKENS":
        raise AssertionError(response)
    parsed = RUNNER._worker_from_response(response)
    if parsed["verification_verdict"] != "ALLOW":
        raise AssertionError(parsed)


def test_empty_worker_output_retry_exhaustion_stays_invalid() -> None:
    original_call_model = RUNNER._call_model
    original_sleep = RUNNER._empty_worker_output_sleep
    RUNNER._empty_worker_output_sleep = lambda _seconds: None
    try:
        def fake_call_model(config, messages, max_tokens):
            return {
                "text": "",
                "finish_reason": "",
                "response_id": "empty-fixture",
                "input_tokens": 10,
                "output_tokens": 0,
                "total_tokens": 10,
                "transport_attempt_count": 1,
                "transport_recovered": False,
                "transport_retry_failures": [],
            }

        RUNNER._call_model = fake_call_model
        response = RUNNER._call_worker_model_with_empty_output_retry(
            {"provider": "xai", "model": "grok-3-mini"},
            [{"role": "user", "content": "fixture"}],
            max_tokens=800,
            turn_id="HV-AP-REP-FIXTURE-A_W1",
        )
    finally:
        RUNNER._call_model = original_call_model
        RUNNER._empty_worker_output_sleep = original_sleep
    if response["empty_worker_output_attempt_count"] != 3:
        raise AssertionError(response)
    if response["empty_worker_output_recovered"] is not False:
        raise AssertionError(response)
    if len(response["empty_worker_output_retry_failures"]) != 3:
        raise AssertionError(response)
    assert_raises_contains(lambda: RUNNER._worker_from_response(response), "worker_empty_text")


def test_malformed_worker_content_is_not_empty_retry() -> None:
    calls = {"count": 0}
    original_call_model = RUNNER._call_model
    try:
        def fake_call_model(config, messages, max_tokens):
            calls["count"] += 1
            return {
                "text": "```json\n{}\n```",
                "finish_reason": "stop",
                "response_id": "malformed-fixture",
                "input_tokens": 10,
                "output_tokens": 4,
                "total_tokens": 14,
                "transport_attempt_count": 1,
                "transport_recovered": False,
                "transport_retry_failures": [],
            }

        RUNNER._call_model = fake_call_model
        response = RUNNER._call_worker_model_with_empty_output_retry(
            {"provider": "xai", "model": "grok-3-mini"},
            [{"role": "user", "content": "fixture"}],
            max_tokens=800,
            turn_id="HV-AP-REP-FIXTURE-A_W1",
        )
    finally:
        RUNNER._call_model = original_call_model
    if calls["count"] != 1:
        raise AssertionError(calls)
    if response["empty_worker_output_attempt_count"] != 1:
        raise AssertionError(response)
    if response["empty_worker_output_recovered"] is not False:
        raise AssertionError(response)
    assert_raises_contains(lambda: RUNNER._worker_from_response(response), "worker_markdown_fence_present")


def compact_worker_fixture(*, verdict: str = "ALLOW", source_id: str = "SRC-TEST-CTL") -> str:
    return "\n".join(
        [
            "worker_role=ADVERSARIAL_SCOPE_CHALLENGER",
            f"verification_verdict={verdict}",
            "binding_class=SOURCE_BOUNDARY_CLOSED",
            "action_boundary=invoice release with complete PO/invoice/receipt match",
            "allow_rule_assessment=exact current source closes the boundary",
            "escalate_rule_assessment=escalate only if source defect remains open",
            "dependency_check=current exact match and approver limit are present",
            f"controlling_source_fact={source_id}",
            f"cited_evidence={source_id}|SRC-TEST-POL",
            "open_blockers=",
            "critical_features_preserved=exact match|approver limit|source boundary closed",
            (
                "final_answer=ALLOW: the source boundary is closed for the invoice release. "
                "The cited control record and policy show exact current source support, approver limit, "
                "and matching source evidence before execution, so no blocker remains open."
            ),
        ]
    )


def worker_spec_fixture() -> dict[str, object]:
    return {
        "boundary": "invoice release with complete PO/invoice/receipt match",
        "knew_terms": {"A": ["exact match", "approver limit"], "B": []},
    }


def test_gov_prompt_contains_no_placeholder_examples() -> None:
    worker_output = RUNNER._worker_from_response(
        {"text": compact_worker_fixture(), "finish_reason": "completed"}
    )
    gate = RUNNER._validate_worker(worker_output, worker_spec_fixture(), "A", {"SRC-TEST-CTL", "SRC-TEST-POL"})
    messages, prompt_obj = RUNNER._build_gov_messages(
        "fixture-run",
        {"pair_id": "HV-AP-REP-FIXTURE", "spec": worker_spec_fixture(), "benchmark_bucket": "hard_allow"},
        {"packet_id": "HV-AP-REP-FIXTURE-A"},
        {"context": {"internal_documents": [], "policy_documents": []}},
        {"turns_completed": []},
        worker_output,
        gate,
        [],
    )
    prompt_text = json.dumps({"messages": messages, "prompt_object": prompt_obj}, sort_keys=True)
    forbidden_fragments = [
        "wb_code",
        "fail_code",
        "repair_hint",
        "blocked_hint",
        "focus_hint",
        "field_name",
        "TODO",
        "placeholder",
        "preserve=wb",
        "repair=fail",
    ]
    found = [fragment for fragment in forbidden_fragments if fragment in prompt_text]
    if found:
        raise AssertionError(f"Gov prompt contains placeholder-like fragments: {found}")
    selected = prompt_obj["selected_baton_lines"]
    if selected != [
        "verdict=FINAL",
        "dep=NONE",
        "focus=FINAL_CHECK",
        "objective=FINALIZE",
        "preserve=CLOSED",
        "repair=NONE",
        "block=NONE",
    ]:
        raise AssertionError(selected)
    reparsed = RUNNER._gov_from_response({"text": "\n".join(selected), "finish_reason": "stop"})
    if reparsed["gov_baton_version"] != "gov_micro_baton_v2":
        raise AssertionError(reparsed)


def test_worker_malformed_unterminated_json_invalid() -> None:
    malformed = (
        '{"worker_role":"ADVERSARIAL_SCOPE_CHALLENGER","verification_verdict":"ALLOW",'
        '"final_answer":"The source boundary is closed.","}'
    )
    assert_raises_contains(
        lambda: RUNNER._worker_from_response({"text": malformed, "finish_reason": "completed"}),
        "Unterminated string",
    )


def test_worker_markdown_wrapped_json_invalid() -> None:
    wrapped = '```json\n{"verification_verdict":"ALLOW"}\n```'
    assert_raises_contains(
        lambda: RUNNER._worker_from_response({"text": wrapped, "finish_reason": "completed"}),
        "worker_markdown_fence_present",
    )


def test_valid_compact_worker_output_parses_and_gates() -> None:
    parsed = RUNNER._worker_from_response(
        {"text": compact_worker_fixture(), "finish_reason": "completed"}
    )
    if parsed["_worker_output_format"] != "compact_key_value_v1":
        raise AssertionError(parsed)
    gate = RUNNER._validate_worker(parsed, worker_spec_fixture(), "A", {"SRC-TEST-CTL", "SRC-TEST-POL"})
    if gate["passed"] is not True:
        raise AssertionError(gate)


def test_worker_output_missing_verdict_invalid() -> None:
    missing_verdict = "\n".join(
        line for line in compact_worker_fixture().splitlines() if not line.startswith("verification_verdict=")
    )
    assert_raises_contains(
        lambda: RUNNER._worker_from_response({"text": missing_verdict, "finish_reason": "completed"}),
        "worker_compact_missing_keys:verification_verdict",
    )


def test_worker_output_with_invented_source_id_invalid() -> None:
    parsed = RUNNER._worker_from_response(
        {"text": compact_worker_fixture(source_id="SRC-INVENTED"), "finish_reason": "completed"}
    )
    gate = RUNNER._validate_worker(parsed, worker_spec_fixture(), "A", {"SRC-TEST-CTL", "SRC-TEST-POL"})
    failures = gate["failures"]
    if "invented_source_id:SRC-INVENTED" not in failures:
        raise AssertionError(failures)
    if gate["passed"] is not False:
        raise AssertionError(gate)


def test_no_packet_or_prompt_hash_mutation() -> None:
    before = freeze_fingerprint()
    test_gov_empty_text_invalid()
    test_gov_length_incomplete_invalid()
    test_valid_gov_v2_baton_parses()
    test_gov_v2_placeholder_token_invalid()
    test_gov_v2_long_prose_invalid()
    test_gov_v2_truncated_missing_fields_invalid()
    test_gov_v2_missing_dep_focus_objective_invalid()
    test_gov_v2_unknown_enum_invalid()
    test_gov_v2_finish_reason_length_invalid()
    test_gov_v2_json_or_quotes_invalid()
    test_gov_v2_markdown_invalid()
    test_gov_provider_failure_summary_precedes_gov_contract_failure()
    test_retry_classifies_transport_only()
    test_transport_retry_success_marks_recovered()
    test_transport_retry_dns_success_marks_recovered()
    test_transport_retry_exhaustion_fails_closed()
    test_empty_worker_response_classifier_is_narrow()
    test_empty_worker_output_retry_success_marks_recovered()
    test_empty_worker_output_retry_exhaustion_stays_invalid()
    test_malformed_worker_content_is_not_empty_retry()
    test_worker_malformed_unterminated_json_invalid()
    test_worker_markdown_wrapped_json_invalid()
    test_gov_prompt_contains_no_placeholder_examples()
    test_valid_compact_worker_output_parses_and_gates()
    test_worker_output_missing_verdict_invalid()
    test_worker_output_with_invented_source_id_invalid()
    after = freeze_fingerprint()
    if before != after:
        raise AssertionError("AP packet or prompt hashes changed during no-provider fixtures")


def main() -> None:
    tests = [
        test_gov_empty_text_invalid,
        test_gov_length_incomplete_invalid,
        test_valid_gov_v2_baton_parses,
        test_gov_v2_placeholder_token_invalid,
        test_gov_v2_long_prose_invalid,
        test_gov_v2_truncated_missing_fields_invalid,
        test_gov_v2_missing_dep_focus_objective_invalid,
        test_gov_v2_unknown_enum_invalid,
        test_gov_v2_finish_reason_length_invalid,
        test_gov_v2_json_or_quotes_invalid,
        test_gov_v2_markdown_invalid,
        test_invalid_summary_without_architecture_lock_passes,
        test_gov_provider_failure_summary_precedes_gov_contract_failure,
        test_retry_classifies_transport_only,
        test_transport_retry_success_marks_recovered,
        test_transport_retry_dns_success_marks_recovered,
        test_transport_retry_exhaustion_fails_closed,
        test_empty_worker_response_classifier_is_narrow,
        test_empty_worker_output_retry_success_marks_recovered,
        test_empty_worker_output_retry_exhaustion_stays_invalid,
        test_malformed_worker_content_is_not_empty_retry,
        test_worker_malformed_unterminated_json_invalid,
        test_worker_markdown_wrapped_json_invalid,
        test_gov_prompt_contains_no_placeholder_examples,
        test_valid_compact_worker_output_parses_and_gates,
        test_worker_output_missing_verdict_invalid,
        test_worker_output_with_invented_source_id_invalid,
        test_no_packet_or_prompt_hash_mutation,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}=PASS")
    print("NO_PROVIDER_FIXTURES=PASS")


if __name__ == "__main__":
    main()
