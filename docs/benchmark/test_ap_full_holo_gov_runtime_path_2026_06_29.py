#!/usr/bin/env python3
"""No-provider proof for the AP OpenAI-W2 full-family Gov runtime path."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
AP_RUNNER_PATH = BENCHMARK_ROOT / "run_ap_replication_holoverify_3dna_2026_06_29.py"
BASE_RUNNER_PATH = BENCHMARK_ROOT / "run_20pair_holoverify_3dna_2026_06_29.py"
CANARY_WRAPPER_PATH = Path("/private/tmp/run_ap_openai_w2_one_pair_canary.py")
FULL_WRAPPER_PATH = Path("/private/tmp/run_ap_openai_w2_holo_policy_v1.py")
EXPECTED_FREEZE_ROOT = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"
EXPECTED_GOV_MAX_TOKENS = 1024


def load_ap_runner():
    spec = importlib.util.spec_from_file_location("ap_openai_w2_runtime_path_test", AP_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    ap = load_ap_runner()
    runner = ap.RUNNER
    ap.configure_openai_w2_runner()

    freeze = ap.read_freeze()
    pairs = ap.build_pairs(freeze["records"])
    pair = pairs[0]
    packet_id = pair["freeze_records"]["A"]["packet_id"]
    payload = pair["payloads"]["A"]

    active_models = [
        runner.MODEL_CONFIGS[worker["model_key"]]["model"]
        for worker in runner.WORKER_SEQUENCE
    ] + [runner.MODEL_CONFIGS[runner.GOV_MODEL_KEY]["model"]]

    state_brief = runner._make_state_brief(
        "no_provider_runtime_proof",
        pair["pair_id"],
        packet_id,
        [],
        [pair["spec"].get("failure_class_notes") or pair["spec"]["boundary"]],
        [],
        None,
        None,
    )
    worker_output = {
        "verification_verdict": "ALLOW",
        "boundary_binding": {
            "binding_class": "SOURCE_BOUNDARY_CLOSED",
            "controlling_source_fact": "SRC-PROOF",
        },
        "cited_evidence": ["SRC-PROOF"],
        "open_blockers": [],
        "critical_features_preserved": [],
        "final_answer": "ALLOW: proof fixture only; no provider call is made.",
    }
    gate_result = {
        "passed": False,
        "failures": ["missing_boundary_binding:escalate_rule_assessment"],
        "artifact_verdict": "ALLOW",
        "artifact_binding": "SOURCE_BOUNDARY_CLOSED",
        "critical_term_count": 0,
    }

    gov_messages, gov_prompt_obj = runner._build_gov_messages(
        "no_provider_runtime_proof",
        pair,
        {"packet_id": packet_id},
        payload,
        state_brief,
        worker_output,
        gate_result,
        [],
    )
    gov_prompt_text = json.dumps(
        {"messages": gov_messages, "prompt_object": gov_prompt_obj},
        sort_keys=True,
        separators=(",", ":"),
    )
    selected_lines = gov_prompt_obj["selected_baton_lines"]
    selected_parse = runner._gov_from_response({"text": "\n".join(selected_lines), "finish_reason": "stop"})

    stale_fragments = [
        "Return one compact key=value baton only",
        "wb_code",
        "fail_code",
        "repair_hint",
        "blocked_hint",
        "focus_hint",
        "field_name",
        "preserve=wb",
        "repair=fail",
    ]
    stale_hits = [fragment for fragment in stale_fragments if fragment in gov_prompt_text]

    base_source = BASE_RUNNER_PATH.read_text()
    ap_source = AP_RUNNER_PATH.read_text()
    canary_source = CANARY_WRAPPER_PATH.read_text() if CANARY_WRAPPER_PATH.exists() else ""
    full_source = FULL_WRAPPER_PATH.read_text() if FULL_WRAPPER_PATH.exists() else ""

    assert_true(freeze["summary"].get("freeze_root_hash") == EXPECTED_FREEZE_ROOT, "freeze_root_mismatch")
    assert_true(len(freeze["records"]) == 40, "ap_packet_count_not_40")
    assert_true(len(pairs) == 20, "ap_pair_count_not_20")
    assert_true(runner.MODEL_CONFIGS[runner.WORKER_SEQUENCE[1]["model_key"]]["model"] == "gpt-5.4-mini", "w2_model_mismatch")
    assert_true(not any("gemini" in model.lower() for model in active_models), "gemini_active")
    assert_true(runner._worker_contract().get("format") == "compact_key_value_v1", "worker_contract_mismatch")
    assert_true(runner._gov_contract().get("format") == "gov_micro_baton_v2", "gov_contract_mismatch")
    assert_true(getattr(runner, "GOV_MAX_TOKENS", None) == EXPECTED_GOV_MAX_TOKENS, "gov_max_tokens_not_1024")
    assert_true("HoloGov-V micro-router v2" in gov_messages[0]["content"], "gov_prompt_missing_micro_router_v2")
    assert_true("Return gov_micro_baton_v2 only" in gov_messages[0]["content"], "gov_prompt_missing_contract")
    assert_true(len(selected_lines) == 7, "selected_baton_line_count_not_7")
    assert_true(selected_parse.get("gov_baton_version") == "gov_micro_baton_v2", "selected_baton_parse_failed")
    assert_true(not stale_hits, f"stale_or_placeholder_gov_prompt_hits:{stale_hits}")
    assert_true("_call_model(gov_config, gov_messages, max_tokens=GOV_MAX_TOKENS)" in base_source, "base_gov_call_budget_path_missing")
    assert_true("RUNNER.GOV_MAX_TOKENS = AP_OPENAI_W2_GOV_MAX_TOKENS" in ap_source, "ap_gov_budget_override_missing")
    assert_true("RUNNER._run_packet" in canary_source or "AP.RUNNER._run_packet" in canary_source, "canary_wrapper_not_using_run_packet")
    assert_true("RUNNER._run_packet" in full_source or "AP.RUNNER._run_packet" in full_source, "full_wrapper_not_using_run_packet")

    report = {
        "classification": "AP_FULL_HOLO_GOV_RUNTIME_PATH_NO_PROVIDER_PROOF",
        "status": "PASS",
        "freeze_root": EXPECTED_FREEZE_ROOT,
        "packet_count": len(freeze["records"]),
        "pair_count": len(pairs),
        "w2_model": runner.MODEL_CONFIGS[runner.WORKER_SEQUENCE[1]["model_key"]]["model"],
        "worker_contract_format": runner._worker_contract().get("format"),
        "gov_contract_format": runner._gov_contract().get("format"),
        "gov_max_tokens": getattr(runner, "GOV_MAX_TOKENS", None),
        "gov_prompt_selected_baton_lines": selected_lines,
        "stale_or_placeholder_hits": stale_hits,
        "canary_wrapper_uses_run_packet": bool("RUNNER._run_packet" in canary_source or "AP.RUNNER._run_packet" in canary_source),
        "full_wrapper_uses_run_packet": bool("RUNNER._run_packet" in full_source or "AP.RUNNER._run_packet" in full_source),
        "provider_calls": 0,
        "judge_calls": 0,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
