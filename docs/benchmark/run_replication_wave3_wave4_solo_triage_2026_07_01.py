#!/usr/bin/env python3
"""Run or preflight solo one-shot triage over frozen Wave 3 / Wave 4 packets.

This is a lane-locked adapter around the June 29 solo triage runner. It points
the runner at the combined Wave 3 / Wave 4 freeze root and keeps the solo lane
separate from Holo:
- no Gov
- no state brief
- no baton
- no artifact registry
- no final selector
- no judges
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

LEGACY_RUNNER_PATH = BENCHMARK_ROOT / "run_replication_3family_solo_triage_2026_06_29.py"
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
RUN_ROOT = FREEZE_ROOT / "solo_triage_3mini"
EXPECTED_FREEZE_ROOT_HASH = "ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5"
OPENAI_MODEL_ID = "gpt-5.4-mini"

WAVE_FAMILIES = {
    "wave3": {
        "HV-GOVP-REP-2026-07-01": "Government procurement / grants controls",
        "HV-BENC-REP-2026-07-01": "Benefits / public casework controls",
        "HV-BKYC-REP-2026-07-01": "Banking / KYC / AML controls",
    },
    "wave4": {
        "HV-DEFA-REP-2026-07-01": "Defense administration / logistics controls",
        "HV-INSR-REP-2026-07-01": "Insurance claims / coverage controls",
        "HV-UTIL-REP-2026-07-01": "Energy / utilities / infrastructure controls",
    },
}
EXPECTED_FAMILIES = {family_id: domain for wave in WAVE_FAMILIES.values() for family_id, domain in wave.items()}


def load_legacy_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wave3_wave4_legacy_solo_triage", LEGACY_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


LEGACY = load_legacy_runner()

# Mutate only this imported module instance. Historical runner files and older
# freeze roots remain untouched.
LEGACY.FREEZE_ROOT = FREEZE_ROOT
LEGACY.RUN_ROOT = RUN_ROOT
LEGACY.EXPECTED_FREEZE_ROOT_HASH = EXPECTED_FREEZE_ROOT_HASH
LEGACY.OPENAI_WEAK_MODEL_ID = OPENAI_MODEL_ID
LEGACY.EXPECTED_FAMILIES = EXPECTED_FAMILIES
LEGACY.AP.RUNNER.MODEL_CONFIGS[LEGACY.OPENAI_WEAK_MODEL_KEY] = {
    "provider": "openai",
    "model": OPENAI_MODEL_ID,
    "dna": "openai",
    "api_key_env": "OPENAI_API_KEY",
    "kind": "openai_responses",
}


def read_wave3_wave4_freeze_records() -> list[dict[str, Any]]:
    freeze = LEGACY.load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    if freeze.get("freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError(f"freeze_root_hash_mismatch:{freeze.get('freeze_root_hash')}")

    index = LEGACY.load_json(FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")
    packet_manifest = LEGACY.load_json(FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = LEGACY.load_json(FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    packet_by_id = {row["packet_id"]: row for row in packet_manifest["records"]}
    prompt_by_id = {row["packet_id"]: row for row in prompt_manifest["records"]}

    records = []
    for row in sorted(index, key=lambda item: (item["wave"], item["family_id"], item["pair_id"], item["sibling_id"])):
        packet_hash = packet_by_id[row["packet_id"]]
        prompt_hash = prompt_by_id[row["packet_id"]]
        packet_path = FREEZE_ROOT / packet_hash["packet_path"]
        prompt_path = FREEZE_ROOT / prompt_hash["prompt_path"]
        payload_path = FREEZE_ROOT / packet_hash["model_visible_payload_path"]
        if LEGACY.sha256_file(packet_path) != packet_hash["packet_sha256"]:
            raise RuntimeError(f"packet_hash_mismatch:{row['packet_id']}")
        if LEGACY.sha256_file(prompt_path) != prompt_hash["prompt_sha256"]:
            raise RuntimeError(f"prompt_hash_mismatch:{row['packet_id']}")
        if LEGACY.sha256_file(payload_path) != packet_hash["model_visible_payload_file_sha256"]:
            raise RuntimeError(f"model_visible_payload_hash_mismatch:{row['packet_id']}")
        packet = LEGACY.load_json(packet_path)
        answer_key = packet["deterministic_answer_key_for_local_audit_only"]
        records.append(
            {
                **row,
                "packet_path": str(packet_path.relative_to(BENCHMARK_ROOT)),
                "prompt_path": str(prompt_path.relative_to(BENCHMARK_ROOT)),
                "model_visible_payload_path": str(payload_path.relative_to(BENCHMARK_ROOT)),
                "packet_file_sha256": packet_hash["packet_sha256"],
                "prompt_file_sha256": prompt_hash["prompt_sha256"],
                "model_visible_payload_file_sha256": packet_hash["model_visible_payload_file_sha256"],
                "packet": packet,
                "required_verdict_for_local_audit_only": answer_key["required_verdict"],
                "required_source_ids_for_local_audit_only": answer_key["required_source_ids"],
                "allowed_source_ids_for_local_audit_only": answer_key["allowed_source_ids"],
            }
        )
    validate_wave3_wave4_records(records)
    return records


def validate_wave3_wave4_records(records: list[dict[str, Any]]) -> None:
    if len(records) != 240:
        raise RuntimeError(f"expected_240_records_got:{len(records)}")
    family_counts = Counter(row["family_id"] for row in records)
    if set(family_counts) != set(EXPECTED_FAMILIES):
        raise RuntimeError(f"family_set_mismatch:{sorted(family_counts)}")
    wave_counts = Counter(row["wave"] for row in records)
    if wave_counts != {"wave3": 120, "wave4": 120}:
        raise RuntimeError(f"wave_packet_count_mismatch:{dict(wave_counts)}")
    for family_id in EXPECTED_FAMILIES:
        family_rows = [row for row in records if row["family_id"] == family_id]
        if len(family_rows) != 40:
            raise RuntimeError(f"family_packet_count_mismatch:{family_id}:{len(family_rows)}")
        if len({row["pair_id"] for row in family_rows}) != 20:
            raise RuntimeError(f"family_pair_count_mismatch:{family_id}")
        truths = Counter(row["packet_truth"] for row in family_rows)
        if truths != {"ALLOW": 20, "ESCALATE": 20}:
            raise RuntimeError(f"family_truth_balance_mismatch:{family_id}:{truths}")
        buckets = Counter(row["target_bucket"] for row in family_rows if row["target_sibling"])
        if buckets != {"hard_allow": 10, "hard_escalate": 10}:
            raise RuntimeError(f"family_target_balance_mismatch:{family_id}:{buckets}")


LEGACY.read_freeze_records = read_wave3_wave4_freeze_records

_legacy_preflight_report = LEGACY.preflight_report
_legacy_summarize = LEGACY.summarize
_legacy_run_live = LEGACY.run_live


def wave3_wave4_preflight_report(*args: Any, **kwargs: Any) -> dict[str, Any]:
    report = _legacy_preflight_report(*args, **kwargs)
    checks = dict(report.get("checks") or {})
    checks.pop("openai_weak_is_gpt_4o_mini", None)
    active_models = [row["model"] for row in report.get("model_roster", [])]
    checks["openai_w2_is_gpt_5_4_mini"] = (
        LEGACY.RUNNER.MODEL_CONFIGS[LEGACY.OPENAI_WEAK_MODEL_KEY]["model"] == OPENAI_MODEL_ID
    )
    checks["no_gpt_4o_mini_in_triage_roster"] = "gpt-4o-mini" not in active_models
    checks["wave3_wave4_freeze_root_matches"] = report.get("freeze_root") == EXPECTED_FREEZE_ROOT_HASH
    selected_family_ids = set(report.get("selection", {}).get("family_ids", []))
    checks["selected_family_set_valid"] = selected_family_ids <= set(EXPECTED_FAMILIES)
    report["classification"] = "HOLOVERIFY_REPLICATION_WAVE3_WAVE4_SOLO_TRIAGE_PREFLIGHT"
    report["checks"] = checks
    report["status"] = "PASS" if all(checks.values()) else "FAIL"
    report["wave3_wave4_lane_lock"] = {
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "families": EXPECTED_FAMILIES,
        "openai_model": OPENAI_MODEL_ID,
        "no_gov": True,
        "no_holo_state": True,
        "no_judges": True,
    }
    return report


def wave3_wave4_summarize(*args: Any, **kwargs: Any) -> dict[str, Any]:
    summary = _legacy_summarize(*args, **kwargs)
    summary["classification"] = summary["classification"].replace(
        "HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE",
        "HOLOVERIFY_REPLICATION_WAVE3_WAVE4_SOLO_TRIAGE",
    )
    summary["wave3_wave4_lane_lock"] = {
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "families": EXPECTED_FAMILIES,
        "openai_model": OPENAI_MODEL_ID,
        "no_gov": True,
        "no_holo_state": True,
        "no_judges": True,
    }
    return summary


def wave3_wave4_run_live(*args: Any, **kwargs: Any) -> int:
    result = _legacy_run_live(*args, **kwargs)
    if result:
        summaries = sorted(RUN_ROOT.glob("*/run_*/solo_triage_results.json"))
        if summaries:
            latest = max(summaries, key=lambda path: path.stat().st_mtime)
            try:
                summary = json.loads(latest.read_text())
            except Exception:
                return result
            if summary.get("classification") == "HOLOVERIFY_REPLICATION_WAVE3_WAVE4_SOLO_TRIAGE_COMPLETE":
                return 0
    return result


LEGACY.preflight_report = wave3_wave4_preflight_report
LEGACY.summarize = wave3_wave4_summarize
LEGACY.run_live = wave3_wave4_run_live


def selected_families(wave: str | None, families: list[str] | None) -> list[str] | None:
    selected: list[str] = []
    if wave:
        selected.extend(WAVE_FAMILIES[wave])
    if families:
        selected.extend(families)
    if not selected:
        return None
    unknown = sorted(set(selected) - set(EXPECTED_FAMILIES))
    if unknown:
        raise RuntimeError(f"unknown_family_ids:{unknown}")
    return sorted(set(selected))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true", help="Local no-provider preflight only.")
    parser.add_argument("--run-live", action="store_true", help="Run solo triage in an authorized shell.")
    parser.add_argument("--wave", choices=sorted(WAVE_FAMILIES), help="Run or preflight all families in one wave.")
    parser.add_argument("--family", action="append", choices=sorted(EXPECTED_FAMILIES), help="Limit to a frozen family. May be repeated.")
    parser.add_argument("--pair-limit", type=int, help="Limit to the first N sibling pairs after family filtering.")
    parser.add_argument("--packet-limit", type=int, help="Limit to the first N packets after family/pair filtering.")
    parser.add_argument("--batch-label", default="wave3_wave4_solo_triage", help="Label used in output run path and reports.")
    args = parser.parse_args()
    family_ids = selected_families(args.wave, args.family)
    if args.preflight:
        report = LEGACY.preflight_report(
            family_ids=family_ids,
            pair_limit=args.pair_limit,
            packet_limit=args.packet_limit,
            batch_label=args.batch_label,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if args.run_live:
        return LEGACY.run_live(
            family_ids=family_ids,
            pair_limit=args.pair_limit,
            packet_limit=args.packet_limit,
            batch_label=args.batch_label,
        )
    parser.error("Use --preflight or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
