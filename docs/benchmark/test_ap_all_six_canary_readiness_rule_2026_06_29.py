#!/usr/bin/env python3
"""No-provider fixtures for the AP all-six-collapse canary readiness rule."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
CANARY_PATH = BENCHMARK_ROOT / "run_ap_openai_w2_holo_all_six_collapse_canary_2026_06_29.py"
LOCKED_RUN = (
    BENCHMARK_ROOT
    / "holoverify_ap_procurement_replication_2026-06-29"
    / "holo_canary_openai_w2_all_six_collapse"
    / "run_20260629T193200Z"
)


def load_canary():
    spec = importlib.util.spec_from_file_location("ap_all_six_canary_readiness_fixture", CANARY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_pair_level_solo_collapse_evidence() -> None:
    canary = load_canary()
    evidence = canary.solo_triage_pair_evidence()
    if set(evidence) != set(canary.TARGET_PAIR_IDS):
        raise AssertionError(sorted(evidence))
    for pair_id in canary.TARGET_PAIR_IDS:
        if not canary.has_pair_level_all_six_solo_collapse(evidence[pair_id]):
            raise AssertionError({pair_id: evidence[pair_id]})


def test_non_all_six_evidence_rejected() -> None:
    canary = load_canary()
    bad_cases = [
        {"triage_class": "STRONG_SOLO_COLLAPSE", "not_knew_count": 6, "calls_present": 6},
        {"triage_class": "ALL_SIX_SOLO_COLLAPSE", "not_knew_count": 5, "calls_present": 6},
        {"triage_class": "ALL_SIX_SOLO_COLLAPSE", "not_knew_count": 6, "calls_present": 5},
        {},
    ]
    for case in bad_cases:
        if canary.has_pair_level_all_six_solo_collapse(case):
            raise AssertionError(case)


def test_locked_run_corrects_under_pair_level_rule() -> None:
    canary = load_canary()
    summary = json.loads((LOCKED_RUN / "canary_results.json").read_text())
    evidence = canary.solo_triage_pair_evidence()
    corrected_valid_pairs = 0
    for item in summary["benchmark_inventory"]:
        pair_id = item["pair_id"]
        pair_level = canary.has_pair_level_all_six_solo_collapse(evidence[pair_id])
        corrected_valid_pairs += int(item["target_final_correct"] and item["guardrail_final_correct"] and pair_level)
    if summary["packet_correct"] != canary.EXPECTED_COUNTS["packets"]:
        raise AssertionError(summary["packet_correct"])
    if corrected_valid_pairs != canary.EXPECTED_COUNTS["pairs"]:
        raise AssertionError(corrected_valid_pairs)


def main() -> None:
    tests = [
        test_pair_level_solo_collapse_evidence,
        test_non_all_six_evidence_rejected,
        test_locked_run_corrects_under_pair_level_rule,
    ]
    for test in tests:
        test()
        print(f"{test.__name__}=PASS")
    print("AP_ALL_SIX_CANARY_READINESS_RULE_FIXTURES=PASS")


if __name__ == "__main__":
    main()
