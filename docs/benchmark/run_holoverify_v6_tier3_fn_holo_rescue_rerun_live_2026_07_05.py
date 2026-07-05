#!/usr/bin/env python3
"""Run the V6 Tier 3 FN Holo rescue rerun lane.

This wrapper binds live execution to a 14-packet runtime-only manifest.
It does not import or read mixed registration JSON or scoring maps during
live execution. Post-hoc scoring remains separate and may run only after
trace freeze.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(BENCHMARK_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import holoverify_blind_runner_v0 as BLIND  # noqa: E402
import run_holoverify_blind_canary_live_2026_07_02 as CANARY  # noqa: E402


RUNTIME_MANIFEST = BENCHMARK_ROOT / "HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json"
LIVE_ROOT = BENCHMARK_ROOT / "holoverify_v6_tier3_fn_holo_rescue_rerun_2026_07_05" / "live_runs"
POSTHOC_SCORING_SCRIPT = BENCHMARK_ROOT / "score_holoverify_v6_tier3_fn_holo_rescue_rerun_posthoc_2026_07_05.py"

EXPECTED_RUNTIME_MANIFEST_SHA256 = "05ce391eff4f495d91f3cb8187185166a6e218903280b747e1a59ac6991ca0da"
EXPECTED_SCORING_MAP_SHA256 = "90c73ec8b683c074f2ebcdb6ce054bb222e584371420a47e49963f99b8eb5928"
EXPECTED_PACKET_COUNT = 14
EXPECTED_CALL_COUNT = 70
LANE_LABEL = "HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_V0"
EVIDENCE_SCOPE = (
    "MECHANICAL SAME-SET RERUN of the failed V5 Tier 3 FN Holo rescue lane under V6; "
    "internal patch-validation / selected-lane repair evidence only; not public "
    "benchmark evidence, not a global FNR claim, not FP precision evidence, and "
    "not general model superiority."
)
SCORING_MAP_READ_GUARD_TEST = (
    "manual_no_provider_preflight:"
    "v6_tier3_fn_holo_rescue_rerun_live_wrapper_uses_runtime_only_manifest_and_does_not_read_scoring_map"
)
WRAPPER_SCORING_SPLIT_TEST = (
    "manual_no_provider_preflight:"
    "v6_tier3_fn_holo_rescue_rerun_live_wrapper_does_not_keep_mixed_registration_json_path"
)


def _load_payload(opaque_runtime_id: str) -> dict[str, Any]:
    manifest = json.loads(RUNTIME_MANIFEST.read_text())
    packet = next(row for row in manifest["packets"] if row["opaque_runtime_id"] == opaque_runtime_id)
    payload_ref = packet.get("runtime_payload_ref") or packet.get("payload_path")
    if not payload_ref:
        raise KeyError(f"missing runtime payload path for {opaque_runtime_id}")
    return json.loads((REPO_ROOT / payload_ref).read_text())


def _cited(payload: dict[str, Any]) -> str:
    return "|".join(str(doc["doc_id"]) for doc in payload["documents"])


def _worker_output(payload: dict[str, Any], verdict: str = "ALLOW") -> str:
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    blockers = "" if verdict == "ALLOW" else "deterministic scope dependency remains open"
    blocker_type = "" if verdict == "ALLOW" else "SCOPE_MISMATCH"
    final = (
        "ALLOW because the visible source records appear to close the requested action boundary."
        if verdict == "ALLOW"
        else "ESCALATE because the visible source records leave the requested action scope open."
    )
    return "\n".join(
        [
            "worker_role=W1",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=authority scope and requested action dependency",
            f"cited_evidence={_cited(payload)}",
            f"open_blockers={blockers}",
            f"blocker_type={blocker_type}",
            "blocker_resolution=",
            "structured_blocker_resolution=",
            f"final_answer={final}",
        ]
    )


def _gate_from_allow(payload: dict[str, Any]) -> dict[str, Any]:
    parsed = BLIND._parse_key_value(_worker_output(payload, verdict="ALLOW"))
    return BLIND._gate_worker_output(payload, parsed)


def _row_and_gate(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    parsed = BLIND._parse_key_value(_worker_output(payload, verdict="ALLOW"))
    gate = BLIND._gate_worker_output(payload, parsed)
    row = {
        "artifact_id": "PREFLIGHT-ART-001",
        "role": parsed.get("worker_role", "W1"),
        "turn_index": 1,
        "parse_valid": True,
        "parsed": parsed,
        "gate_result": gate,
    }
    deterministic_blockers = BLIND._deterministic_blockers_from_dependency_failures(row, gate)
    gate["deterministic_dependency_blockers"] = deterministic_blockers
    gate["blockers_found"] = deterministic_blockers
    return row, gate


def v6_scope_gate_probe() -> dict[str, Any]:
    add_on_bad = _load_payload("HVSF016HA-4FD06F71B9FBAD305E84")
    protocol_bad = _load_payload("HVSF016HA-BCE20453716AA96B9B48")
    add_on_good = _load_payload("HVSF016HA-B2FBED6E9D535E4F3229")
    protocol_good = _load_payload("HVSF016HA-0705182D345B199BF07B")

    add_on_bad_gate = _gate_from_allow(add_on_bad)
    protocol_bad_gate = _gate_from_allow(protocol_bad)
    add_on_good_gate = _gate_from_allow(add_on_good)
    protocol_good_gate = _gate_from_allow(protocol_good)

    add_on_checks = add_on_bad_gate.get("deterministic_dependency_failures") or []
    protocol_checks = protocol_bad_gate.get("deterministic_dependency_failures") or []
    _, baton_gate = _row_and_gate(protocol_bad)
    baton = BLIND._selected_gov_baton_from_gate(baton_gate)
    selector_row, selector_gate = _row_and_gate(add_on_bad)
    selector_artifact = BLIND._artifact_from_row(selector_row)
    selection = BLIND.select_final([selector_artifact])

    checks = {
        "add_on_bad_rejected": (
            not add_on_bad_gate.get("passed")
            and any(item.get("check_id") == "authority_scope_add_on_activation" for item in add_on_checks)
        ),
        "protocol_bad_rejected": (
            not protocol_bad_gate.get("passed")
            and any(item.get("check_id") == "authority_scope_protocol_start" for item in protocol_checks)
        ),
        "add_on_allow_sibling_passes": add_on_good_gate.get("passed") is True,
        "protocol_allow_sibling_passes": protocol_good_gate.get("passed") is True,
        "gov_baton_carries_dependency_ledger": bool(baton.get("dependency_ledger")),
        "gov_baton_carries_blocker_ledger": bool(baton.get("blocker_ledger")),
        "selector_blocks_unresolved_scope_blocker": selection.get("selected_artifact_id") is None
        and selection.get("selector_blocked_reason") == "no_structurally_valid_artifact"
        and bool(selector_gate.get("deterministic_dependency_blockers")),
    }
    return {
        "classification": "HOLOVERIFY_V6_TIER3_FN_RERUN_SCOPE_GATE_PROMPT_PROBE_V0",
        "checks": checks,
        "passed": all(checks.values()),
        "known_failed_b_side_fixtures": {
            "HVSF-FACTORY16-008-B": {
                "opaque_runtime_id": "HVSF016HA-4FD06F71B9FBAD305E84",
                "deterministic_failure_ids": [item.get("check_id") for item in add_on_checks],
            },
            "HVSF-FACTORY16-019-B": {
                "opaque_runtime_id": "HVSF016HA-BCE20453716AA96B9B48",
                "deterministic_failure_ids": [item.get("check_id") for item in protocol_checks],
            },
        },
        "selector_identity": BLIND.selector_policy_identity(),
        "worker_contract_identity": BLIND.worker_contract_identity(),
    }


def scoped_approval_sentence() -> str:
    selector = CANARY.BLIND.selector_policy_identity()
    worker = CANARY.BLIND.worker_contract_identity()
    return (
        f"I approve live provider execution for {LANE_LABEL} using only runtime-only manifest "
        f"docs/benchmark/{RUNTIME_MANIFEST.name} with SHA-256 {EXPECTED_RUNTIME_MANIFEST_SHA256}, "
        f"selector {selector['selector_policy_version']} hash {selector['selector_policy_sha256']}, "
        f"worker contract {worker['worker_contract_version']} hash {worker['worker_contract_sha256']}, "
        "and exactly 70 provider calls: W1 xai/grok-3-mini x14, "
        "G1 minimax/MiniMax-M2.5-highspeed x14, W2 openai/gpt-5.4-mini x14, "
        "G2 minimax/MiniMax-M2.5-highspeed x14, W3 minimax/MiniMax-M2.5-highspeed x14. "
        f"{EVIDENCE_SCOPE} No solo, no judges, no scoring map before trace freeze, "
        "no mixed registration JSON before trace freeze, no substitutions, no public claims."
    )


def configure_runtime() -> None:
    CANARY.RUNTIME_MANIFEST = RUNTIME_MANIFEST
    CANARY.LIVE_ROOT = LIVE_ROOT
    CANARY.EXPECTED_RUNTIME_MANIFEST_SHA256 = EXPECTED_RUNTIME_MANIFEST_SHA256
    CANARY.EXPECTED_SCORING_MAP_SHA256 = EXPECTED_SCORING_MAP_SHA256
    CANARY.EXPECTED_PACKET_COUNT = EXPECTED_PACKET_COUNT
    CANARY.EXPECTED_CALL_COUNT = EXPECTED_CALL_COUNT
    CANARY.POSTHOC_SCORING_SCRIPT = POSTHOC_SCORING_SCRIPT
    CANARY.SCORING_MAP_READ_GUARD_TEST = SCORING_MAP_READ_GUARD_TEST
    CANARY.WRAPPER_SCORING_SPLIT_TEST = WRAPPER_SCORING_SPLIT_TEST
    CANARY.EXACT_APPROVAL_SENTENCE = scoped_approval_sentence()
    CANARY.scoped_approval_sentence = lambda packet_limit=None, packet_index=1: scoped_approval_sentence()


def preflight(run_dir: Path) -> dict[str, Any]:
    configure_runtime()
    probe = v6_scope_gate_probe()
    if not probe["passed"]:
        raise RuntimeError(f"v6_scope_gate_probe_failed:{probe}")
    report = CANARY.preflight(run_dir, RUNTIME_MANIFEST)
    report["classification"] = "HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_PREFLIGHT_V0"
    report["lane_label"] = LANE_LABEL
    report["patch_validation_only"] = True
    report["evidence_scope"] = EVIDENCE_SCOPE
    report["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    report["mixed_registration_json_loaded_before_trace_freeze"] = False
    report["registration_json_live_input"] = False
    report["expected_provider_calls"] = EXPECTED_CALL_COUNT
    report["expected_call_sequence"] = ["W1", "G1", "W2", "G2", "W3"]
    report["expected_provider_calls_by_slot"] = {
        "W1": {"provider": "xai", "model": "grok-3-mini", "calls": EXPECTED_PACKET_COUNT},
        "G1": {"provider": "minimax", "model": "MiniMax-M2.5-highspeed", "calls": EXPECTED_PACKET_COUNT},
        "W2": {"provider": "openai", "model": "gpt-5.4-mini", "calls": EXPECTED_PACKET_COUNT},
        "G2": {"provider": "minimax", "model": "MiniMax-M2.5-highspeed", "calls": EXPECTED_PACKET_COUNT},
        "W3": {"provider": "minimax", "model": "MiniMax-M2.5-highspeed", "calls": EXPECTED_PACKET_COUNT},
    }
    report["scope_boundary"] = {
        "public_benchmark_evidence": False,
        "global_fnr_claim": False,
        "fp_precision_evidence": False,
        "general_model_superiority": False,
        "internal_patch_validation_selected_lane_repair": True,
    }
    report["v6_scope_gate_probe"] = probe
    report["prompt_probe_expected_provider_calls"] = EXPECTED_CALL_COUNT
    report["prompt_probe_provider_calls_made"] = 0
    report["live_command"] = (
        "python3 docs/benchmark/run_holoverify_v6_tier3_fn_holo_rescue_rerun_live_2026_07_05.py "
        "--run-live --approval-statement \"$APPROVAL\""
    )
    report["approval_sentence"] = scoped_approval_sentence()
    CANARY.write_json(run_dir / "v6_tier3_fn_holo_rescue_rerun_live_preflight.json", report)
    return report


def run_preflight_only() -> dict[str, Any]:
    configure_runtime()
    run_dir = LIVE_ROOT / f"preflight_{CANARY.utc_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return preflight(run_dir)


def run_live(approval_statement: str) -> dict[str, Any]:
    configure_runtime()
    summary = CANARY.run_live(approval_statement)
    summary["classification"] = "HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_LIVE_RUN_SUMMARY_V0"
    summary["lane_label"] = LANE_LABEL
    summary["patch_validation_only"] = True
    summary["evidence_scope"] = EVIDENCE_SCOPE
    summary["runtime_only_manifest"] = str(RUNTIME_MANIFEST.relative_to(REPO_ROOT))
    summary["mixed_registration_json_loaded_before_trace_freeze"] = False
    run_dir = REPO_ROOT / summary["run_dir"]
    CANARY.write_json(run_dir / "v6_tier3_fn_holo_rescue_rerun_live_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--print-approval", action="store_true")
    parser.add_argument("--approval-statement", default="")
    args = parser.parse_args()

    if sum(bool(value) for value in (args.preflight, args.run_live, args.print_approval)) != 1:
        raise SystemExit("choose exactly one of --preflight, --run-live, or --print-approval")
    if args.print_approval:
        configure_runtime()
        print(scoped_approval_sentence())
        return 0
    if args.preflight:
        print(json.dumps(run_preflight_only(), indent=2, sort_keys=True))
        return 0
    print(json.dumps(run_live(args.approval_statement), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
