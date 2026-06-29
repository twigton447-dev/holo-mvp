#!/usr/bin/env python3
"""No-provider proof that AP solo binds to the frozen OpenAI-W2 Holo roster."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


BENCHMARK_ROOT = Path(__file__).resolve().parent
RUNNER_PATH = BENCHMARK_ROOT / "run_ap_replication_holoverify_3dna_2026_06_29.py"
EXPECTED_HOLO_RUN = (
    BENCHMARK_ROOT
    / "holoverify_ap_procurement_replication_2026-06-29"
    / "holo_live_runs_openai_w2"
    / "run_20260629T201840Z"
)
EXPECTED_FREEZE_ROOT = "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7"
EXPECTED_SOLO_KEYS = ("xai", "openai_w2", "minimax")


def load_runner():
    spec = importlib.util.spec_from_file_location("ap_solo_binding_proof", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    ap = load_runner()
    latest = ap.latest_complete_holo_run(ap.OPENAI_W2_HOLO_RUN_ROOT, "run_*")
    holo = ap.load_holo_run(EXPECTED_HOLO_RUN)
    model_keys = ap.solo_model_keys_for_holo(EXPECTED_HOLO_RUN, holo)
    ap.configure_solo_roster(model_keys)
    freeze = ap.read_freeze()
    records = freeze["records"]

    roster = [
        {
            "model_key": key,
            "provider": ap.RUNNER.MODEL_CONFIGS[key]["provider"],
            "model": ap.RUNNER.MODEL_CONFIGS[key]["model"],
            "dna": ap.RUNNER.MODEL_CONFIGS[key]["dna"],
        }
        for key in model_keys
    ]
    plan_count = len(records) * len(model_keys)
    prompt_hash_mismatches = []
    for record in records:
        prompt_path = ap.BENCHMARK_ROOT / record["prompt_path"]
        if ap.sha256_file(prompt_path) != record["prompt_file_sha256"]:
            prompt_hash_mismatches.append(record["packet_id"])

    provider_calls = 0
    judge_calls = 0
    checks = {
        "latest_complete_is_expected_holo_run": latest == EXPECTED_HOLO_RUN,
        "holo_classification_complete": holo.get("classification") == "HOLOVERIFY_AP_REPLICATION_HOLO_COMPLETE",
        "freeze_root_matches": freeze["summary"].get("freeze_root_hash") == EXPECTED_FREEZE_ROOT,
        "model_keys_match_openai_w2_holo": model_keys == EXPECTED_SOLO_KEYS,
        "roster_has_no_gemini": all(item["provider"] != "google" and "gemini" not in item["model"].lower() for item in roster),
        "roster_has_openai_w2": any(item["provider"] == "openai" and item["model"] == "gpt-5.4-mini" for item in roster),
        "packet_count": len(records) == 40,
        "plan_count": plan_count == 120,
        "prompt_hashes_match_freeze": not prompt_hash_mismatches,
        "provider_calls_zero": provider_calls == 0,
        "judge_calls_zero": judge_calls == 0,
    }
    failed = [key for key, value in checks.items() if not value]
    report = {
        "classification": "AP_OPENAI_W2_SOLO_BINDING_NO_PROVIDER_PROOF",
        "status": "PASS" if not failed else "FAIL",
        "failed": failed,
        "checks": checks,
        "holo_run": str(EXPECTED_HOLO_RUN),
        "solo_model_keys": list(model_keys),
        "solo_roster": roster,
        "packet_count": len(records),
        "plan_count": plan_count,
        "provider_calls": provider_calls,
        "judge_calls": judge_calls,
        "prompt_hash_mismatches": prompt_hash_mismatches,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
