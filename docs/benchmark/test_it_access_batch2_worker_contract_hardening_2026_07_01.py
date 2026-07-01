#!/usr/bin/env python3
"""No-provider fixtures for IT Access batch 2 worker contract hardening."""

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
IT_RUNNER_PATH = BENCHMARK_ROOT / "run_it_access_replication_holoverify_3dna_2026_06_30.py"
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_2026-06-29"
IT_ROOT = BENCHMARK_ROOT / "holoverify_it_access_replication_2026-06-30"
INVALID_BATCH2_RUN = (
    IT_ROOT
    / "holo_live_runs_openai_w2_batched"
    / "batch_2"
    / "run_20260701T004011Z"
)
EXPECTED_FREEZE_ROOT_HASH = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


RUNNER = load_module("it_access_batch2_base_runner_fixture", BASE_RUNNER_PATH)
IT = load_module("it_access_batch2_wrapper_fixture", IT_RUNNER_PATH)


def assert_raises_contains(fn, needle: str) -> None:
    try:
        fn()
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        if needle not in message:
            raise AssertionError(f"expected {needle!r} in {message!r}") from exc
        return
    raise AssertionError(f"expected exception containing {needle!r}")


def freeze_fingerprint() -> dict[str, Any]:
    manifest = json.loads((FREEZE_ROOT / "FREEZE_MANIFEST.json").read_text())
    packet_manifest = json.loads((FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json").read_text())
    prompt_manifest = json.loads((FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json").read_text())
    return {
        "freeze_root_hash": manifest.get("freeze_root_hash"),
        "packet_manifest_records": len(packet_manifest.get("records") or []),
        "prompt_manifest_records": len(prompt_manifest.get("records") or []),
        "packet_manifest_text": (FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json").read_text(),
        "prompt_manifest_text": (FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json").read_text(),
    }


def invalid_xai_missing_action_boundary_fixture() -> str:
    return "\n".join(
        [
            "worker_role=SOURCE_BOUNDARY_MAPPER",
            "verification_verdict=ESCALATE",
            "binding_class=SOURCE_BOUNDARY_OPEN",
            "allow_rule_assessment=Source records fail to close boundary",
            "escalate_rule_assessment=Change window dependency remains open",
            "dependency_check=change window expiration unresolved",
            "controlling_source_fact=SRC-18487DF3B66F-CTL",
            "cited_evidence=SRC-18487DF3B66F-CTL|SRC-18487DF3B66F-BND",
            "open_blockers=change window expiration",
            "critical_features_preserved=source IDs|action boundary|policy exact-match rule",
            (
                "final_answer=Action may not proceed. SRC-18487DF3B66F-CTL shows missing change "
                "window expiration for role escalation. Exact source boundary remains open. "
                "Escalate to close dependency before any execution."
            ),
        ]
    )


def valid_xai_action_boundary_fixture() -> str:
    return "\n".join(
        [
            "worker_role=SOURCE_BOUNDARY_MAPPER",
            "verification_verdict=ESCALATE",
            "binding_class=SOURCE_BOUNDARY_OPEN",
            "action_boundary=May IT grant or change the requested access, role, permission, or privileged action? Focus: role escalation outside change window.",
            "allow_rule_assessment=source records do not close boundary",
            "escalate_rule_assessment=change window dependency remains open",
            "dependency_check=change window expiration unresolved",
            "controlling_source_fact=SRC-18487DF3B66F-CTL",
            "cited_evidence=SRC-18487DF3B66F-CTL|SRC-18487DF3B66F-BND",
            "open_blockers=change window expiration",
            "critical_features_preserved=change window expiration|SRC-18487DF3B66F-CTL|SRC-18487DF3B66F-BND",
            (
                "final_answer=ESCALATE: the role escalation remains outside the current change window. "
                "SRC-18487DF3B66F-CTL leaves change window expiration unresolved, and "
                "SRC-18487DF3B66F-BND says expired windows cannot authorize escalation before execution."
            ),
        ]
    )


def it_spec_fixture() -> dict[str, Any]:
    return {
        "boundary": "May IT grant or change the requested access, role, permission, or privileged action? Focus: role escalation outside change window.",
        "failure_class_notes": "change window expiration",
        "knew_terms": {
            "A": [],
            "B": [
                "change window expiration",
                "SRC-18487DF3B66F-CTL",
                "SRC-18487DF3B66F-BND",
            ],
        },
    }


def test_missing_action_boundary_remains_invalid() -> None:
    assert_raises_contains(
        lambda: RUNNER._worker_from_response(
            {"text": invalid_xai_missing_action_boundary_fixture(), "finish_reason": "stop"}
        ),
        "worker_compact_missing_keys:action_boundary",
    )


def test_corrected_compact_worker_parses_and_gates() -> None:
    parsed = RUNNER._worker_from_response(
        {"text": valid_xai_action_boundary_fixture(), "finish_reason": "stop"}
    )
    gate = RUNNER._validate_worker(
        parsed,
        it_spec_fixture(),
        "B",
        {"SRC-18487DF3B66F-CTL", "SRC-18487DF3B66F-BND"},
    )
    if gate["passed"] is not True:
        raise AssertionError(gate)


def test_worker_prompt_contains_literal_action_boundary_line() -> None:
    boundary = it_spec_fixture()["boundary"]
    payload = {
        "action": {"description": boundary},
        "context": {
            "action_boundary": boundary,
            "internal_documents": [{"doc_id": "SRC-18487DF3B66F-CTL", "content": "fixture"}],
            "policy_documents": [{"doc_id": "SRC-18487DF3B66F-BND", "content": "fixture"}],
        },
    }
    pair = {"pair_id": "HV-ITAC-REP-012", "spec": it_spec_fixture()}
    packet = {"packet_id": "HV-ITAC-REP-012-B"}
    worker = {
        "worker_index": 1,
        "role_name": "SOURCE_BOUNDARY_MAPPER",
        "config": {"provider": "xai", "model": "grok-3-mini"},
    }
    messages, prompt_obj = RUNNER._build_worker_messages(
        "fixture-run",
        pair,
        packet,
        payload,
        worker,
        {
            "run_id": "fixture-run",
            "pair_id": pair["pair_id"],
            "packet_id": packet["packet_id"],
            "unresolved_dependencies": ["change window expiration"],
        },
        RUNNER._initial_baton(it_spec_fixture()),
        [],
    )
    required_line = f"action_boundary={boundary}"
    prompt_text = json.dumps({"messages": messages, "prompt_object": prompt_obj}, sort_keys=True)
    contract = prompt_obj["structured_canonical_state"]["task_and_answer_contract"]
    if contract.get("required_literal_boundary_line") != required_line:
        raise AssertionError(contract)
    if required_line not in contract.get("output_key_skeleton", []):
        raise AssertionError(contract.get("output_key_skeleton"))
    if required_line not in prompt_obj["structured_canonical_state"]["current_turn_command"]:
        raise AssertionError(prompt_obj["structured_canonical_state"]["current_turn_command"])
    if "Never omit action_boundary=" not in messages[0]["content"]:
        raise AssertionError(messages[0]["content"])
    if "packet_truth" in prompt_text or "expected verdict" in prompt_text.lower():
        raise AssertionError("prompt leaked answer-key language")


def test_invalid_batch2_run_preserved() -> None:
    summary_path = INVALID_BATCH2_RUN / "batch_results.json"
    trace_path = INVALID_BATCH2_RUN / "TRACE_CALLS.jsonl"
    if not summary_path.exists() or not trace_path.exists():
        raise AssertionError("invalid batch 2 run is missing")
    summary = json.loads(summary_path.read_text())
    root = summary.get("root_failure") or {}
    if summary.get("classification") != "IT_ACCESS_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE":
        raise AssertionError(summary.get("classification"))
    if summary.get("provider_calls") != 46:
        raise AssertionError(summary.get("provider_calls"))
    if root.get("turn_id") != "HV-ITAC-REP-012-B_W1":
        raise AssertionError(root)
    if root.get("provider") != "xai" or root.get("model") != "grok-3-mini":
        raise AssertionError(root)
    if root.get("error") != "ValueError: worker_compact_missing_keys:action_boundary":
        raise AssertionError(root.get("error"))
    if trace_path.read_text().count("\n") != 46:
        raise AssertionError("invalid trace call count changed")


def test_no_packet_or_prompt_hash_mutation() -> None:
    before = freeze_fingerprint()
    if before["freeze_root_hash"] != EXPECTED_FREEZE_ROOT_HASH:
        raise AssertionError(before["freeze_root_hash"])
    test_missing_action_boundary_remains_invalid()
    test_corrected_compact_worker_parses_and_gates()
    test_worker_prompt_contains_literal_action_boundary_line()
    test_invalid_batch2_run_preserved()
    after = freeze_fingerprint()
    if before != after:
        raise AssertionError("frozen packet or prompt manifests changed")


def main() -> None:
    tests = [
        test_missing_action_boundary_remains_invalid,
        test_corrected_compact_worker_parses_and_gates,
        test_worker_prompt_contains_literal_action_boundary_line,
        test_invalid_batch2_run_preserved,
        test_no_packet_or_prompt_hash_mutation,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}=PASS")
    print("NO_PROVIDER_FIXTURES=PASS")


if __name__ == "__main__":
    main()
