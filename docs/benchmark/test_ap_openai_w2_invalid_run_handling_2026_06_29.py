#!/usr/bin/env python3
"""No-provider fixtures for AP OpenAI-W2 invalid-run handling."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
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


def test_valid_compact_gov_baton_parses() -> None:
    parsed = RUNNER._gov_from_response(
        {
            "text": (
                "verdict=ALLOW route=FINAL_COMPILER final=true "
                "preserve=SOURCE_BOUNDARY_CLOSED repair= block= dep= "
                "objective=final focus=source"
            ),
            "finish_reason": "stop",
        }
    )
    assert parsed["verdict"] == "ALLOW"
    assert parsed["route"] == "FINAL_COMPILER"
    assert parsed["final"] is True
    assert parsed["preserve"] == "SOURCE_BOUNDARY_CLOSED"
    assert parsed["repair"] == ""
    assert parsed["block"] == ""
    assert parsed["dep"] == ""
    assert parsed["objective"] == "final"
    assert parsed["focus"] == "source"


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


def test_no_packet_or_prompt_hash_mutation() -> None:
    before = freeze_fingerprint()
    test_gov_empty_text_invalid()
    test_gov_length_incomplete_invalid()
    test_valid_compact_gov_baton_parses()
    after = freeze_fingerprint()
    if before != after:
        raise AssertionError("AP packet or prompt hashes changed during no-provider fixtures")


def main() -> None:
    tests = [
        test_gov_empty_text_invalid,
        test_gov_length_incomplete_invalid,
        test_valid_compact_gov_baton_parses,
        test_invalid_summary_without_architecture_lock_passes,
        test_no_packet_or_prompt_hash_mutation,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}=PASS")
    print("NO_PROVIDER_FIXTURES=PASS")


if __name__ == "__main__":
    main()
