#!/usr/bin/env python3
"""Stage Wave 2 HoloVerify target batches without provider calls.

This script consumes the committed Wave 2 solo-triage target selection and
creates a no-provider Holo staging package. It validates packet/prompt hashes
against the frozen Wave 2 packet bank and records the exact Holo architecture
expected for a later live run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_3families_wave2_2026-07-01"
TARGET_SELECTION_PATH = FREEZE_ROOT / "solo_triage_3mini" / "WAVE2_HOLO_TARGET_SELECTION_FROM_SOLO_TRIAGE_2026_07_01.json"
BATCH_NUMBER = 1
BATCH_SUFFIX = "001"
BATCH_ID = "WAVE2_HOLO_TARGET_BATCH_001"
OUTPUT_ROOT = FREEZE_ROOT / "holo_target_batches" / "wave2_holo_target_batch_001"
EXPECTED_FREEZE_ROOT_HASH = "80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f"
EXPECTED_TARGET_SELECTION_SHA = "75e6681b163a7c2e2ab70e69ab161ac53b727c0d311774609e2eca1959874c99"

FORBIDDEN_PROMPT_TERMS = (
    "packet_truth",
    "target_bucket",
    "target_sibling",
    "deterministic_answer_key_for_local_audit_only",
    "required_verdict",
    "verdict_basis",
    "local_audit_predicate",
    "answer key",
    "expected verdict",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def current_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def git_diff_names(path: Path) -> list[str]:
    return [
        row
        for row in subprocess.check_output(["git", "diff", "--name-only", "--", str(path)], cwd=REPO_ROOT, text=True).splitlines()
        if row.strip()
    ]


def configure_batch(batch_number: int) -> None:
    global BATCH_NUMBER, BATCH_SUFFIX, BATCH_ID, OUTPUT_ROOT
    if batch_number < 1:
        raise ValueError("batch_number must be >= 1")
    BATCH_NUMBER = batch_number
    BATCH_SUFFIX = f"{batch_number:03d}"
    BATCH_ID = f"WAVE2_HOLO_TARGET_BATCH_{BATCH_SUFFIX}"
    OUTPUT_ROOT = FREEZE_ROOT / "holo_target_batches" / f"wave2_holo_target_batch_{BATCH_SUFFIX}"


def prior_selected_pair_ids(target_selection: dict[str, Any], batch_number: int) -> set[str]:
    excluded: set[str] = set()
    for prior in range(1, batch_number):
        prior_suffix = f"{prior:03d}"
        prior_registration = (
            FREEZE_ROOT
            / "holo_target_batches"
            / f"wave2_holo_target_batch_{prior_suffix}"
            / f"WAVE2_HOLO_TARGET_BATCH_{prior_suffix}_REGISTRATION_2026_07_01.json"
        )
        if prior_registration.exists():
            excluded.update(load_json(prior_registration).get("selected_pair_ids", []))
        elif prior == 1:
            excluded.update(row["pair_id"] for row in target_selection.get("recommended_first_batch", []))
        else:
            raise RuntimeError(f"missing_prior_batch_registration:{prior_registration}")
    return excluded


def select_pairs(target_selection: dict[str, Any], batch_number: int, pair_count: int) -> tuple[list[dict[str, Any]], str]:
    if batch_number == 1:
        selected = list(target_selection.get("recommended_first_batch") or [])
        return selected[:pair_count], "recommended_first_batch from committed Wave 2 solo triage target selection"
    excluded = prior_selected_pair_ids(target_selection, batch_number)
    selected = [row for row in target_selection.get("all_top_targets", []) if row["pair_id"] not in excluded]
    return selected[:pair_count], f"next {pair_count} all_top_targets after excluding prior staged batches"


def collect_batch_records(pair_count: int) -> tuple[dict[str, Any], dict[str, Any]]:
    freeze_manifest = load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    target_selection = load_json(TARGET_SELECTION_PATH)
    packet_manifest = load_json(FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = load_json(FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    packet_index = load_json(FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")

    packet_hash_by_id = {row["packet_id"]: row for row in packet_manifest["records"]}
    prompt_hash_by_id = {row["packet_id"]: row for row in prompt_manifest["records"]}
    index_by_id = {row["packet_id"]: row for row in packet_index}

    selected_pairs, batch_basis = select_pairs(target_selection, BATCH_NUMBER, pair_count)
    records: list[dict[str, Any]] = []
    prompt_leakage_hits: list[dict[str, str]] = []

    for pair in selected_pairs:
        pair_id = pair["pair_id"]
        packet_ids = pair["packets"]
        if len(packet_ids) != 2:
            raise RuntimeError(f"pair {pair_id} does not have exactly two packets")
        for packet_id in packet_ids:
            packet_row = packet_hash_by_id[packet_id]
            prompt_row = prompt_hash_by_id[packet_id]
            index_row = index_by_id[packet_id]
            packet_path = FREEZE_ROOT / packet_row["packet_path"]
            prompt_path = FREEZE_ROOT / prompt_row["prompt_path"]
            model_visible_path = FREEZE_ROOT / packet_row["model_visible_payload_path"]
            packet_hash_ok = sha256_file(packet_path) == packet_row["packet_sha256"]
            prompt_hash_ok = sha256_file(prompt_path) == prompt_row["prompt_sha256"]
            model_visible_hash_ok = sha256_file(model_visible_path) == packet_row["model_visible_payload_file_sha256"]
            prompt_text = prompt_path.read_text()
            lower_prompt = prompt_text.lower()
            for term in FORBIDDEN_PROMPT_TERMS:
                if term.lower() in lower_prompt:
                    prompt_leakage_hits.append({"packet_id": packet_id, "term": term})
            records.append(
                {
                    "pair_id": pair_id,
                    "packet_id": packet_id,
                    "sibling_id": index_row["sibling_id"],
                    "family_id": index_row["family_id"],
                    "domain": index_row["domain"],
                    "packet_truth": index_row["packet_truth"],
                    "target_bucket": index_row["target_bucket"],
                    "target_sibling": index_row["target_sibling"],
                    "triage_class": pair["triage_class"],
                    "priority_score": pair["priority_score"],
                    "not_knew_count": pair["not_knew_count"],
                    "wrong_verdict_count": pair["wrong_verdict_count"],
                    "parse_or_provider_fail_count": pair["parse_or_provider_fail_count"],
                    "packet_ref": str(packet_path.relative_to(REPO_ROOT)),
                    "prompt_ref": str(prompt_path.relative_to(REPO_ROOT)),
                    "model_visible_payload_ref": str(model_visible_path.relative_to(REPO_ROOT)),
                    "packet_sha256": packet_row["packet_sha256"],
                    "prompt_sha256": prompt_row["prompt_sha256"],
                    "model_visible_payload_file_sha256": packet_row["model_visible_payload_file_sha256"],
                    "packet_hash_ok": packet_hash_ok,
                    "prompt_hash_ok": prompt_hash_ok,
                    "model_visible_hash_ok": model_visible_hash_ok,
                }
            )

    registration = {
        "classification": f"{BATCH_ID}_REGISTRATION_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_head": current_head(),
        "freeze_root_hash": freeze_manifest.get("freeze_root_hash"),
        "freeze_root_ref": str(FREEZE_ROOT.relative_to(REPO_ROOT)),
        "source_target_selection_ref": str(TARGET_SELECTION_PATH.relative_to(REPO_ROOT)),
        "source_target_selection_sha256": target_selection.get("package_sha256"),
        "batch_id": BATCH_ID,
        "batch_basis": batch_basis,
        "pair_count": len(selected_pairs),
        "packet_count": len(records),
        "selected_pair_ids": [row["pair_id"] for row in selected_pairs],
        "selected_records": records,
        "holo_architecture": freeze_manifest["architecture_protocol"],
        "expected_counts": {
            "pairs": len(selected_pairs),
            "packets": len(records),
            "worker_calls": len(records) * freeze_manifest["architecture_protocol"]["worker_calls_per_packet"],
            "gov_calls": len(records) * freeze_manifest["architecture_protocol"]["gov_calls_per_packet"],
            "total_provider_calls": len(records) * freeze_manifest["architecture_protocol"]["calls_per_packet"],
            "solo_calls": 0,
            "judge_calls": 0,
        },
        "run_boundaries": {
            "no_provider_calls_in_staging": True,
            "no_holo_live_calls_in_staging": True,
            "no_solo_calls": True,
            "no_judge_calls": True,
            "no_packet_edits": True,
            "no_prompt_edits": True,
            "fallback_or_substitution_allowed": False,
        },
    }

    checks = {
        "freeze_root_matches_expected": freeze_manifest.get("freeze_root_hash") == EXPECTED_FREEZE_ROOT_HASH,
        "target_selection_sha_matches_expected": target_selection.get("package_sha256") == EXPECTED_TARGET_SELECTION_SHA,
        f"pair_count_{pair_count}": len(selected_pairs) == pair_count,
        f"packet_count_{pair_count * 2}": len(records) == pair_count * 2,
        "all_pairs_have_two_siblings": all(
            len([record for record in records if record["pair_id"] == pair["pair_id"]]) == 2 for pair in selected_pairs
        ),
        "packet_hashes_match": all(record["packet_hash_ok"] for record in records),
        "prompt_hashes_match": all(record["prompt_hash_ok"] for record in records),
        "model_visible_hashes_match": all(record["model_visible_hash_ok"] for record in records),
        "no_prompt_leakage_hits": not prompt_leakage_hits,
        "gov_cannot_choose_models": freeze_manifest["architecture_protocol"].get("gov_may_select_models") is False,
        f"expected_provider_calls_{pair_count * 10}": len(records) * freeze_manifest["architecture_protocol"]["calls_per_packet"] == pair_count * 10,
        "expected_solo_calls_0": True,
        "expected_judge_calls_0": True,
        "freeze_root_clean_in_git": not git_diff_names(FREEZE_ROOT),
    }
    preflight = {
        "classification": f"{BATCH_ID}_PREFLIGHT_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "batch_id": registration["batch_id"],
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "prompt_leakage_hits": prompt_leakage_hits,
        "expected_counts": registration["expected_counts"],
        "model_roster": freeze_manifest["architecture_protocol"]["call_sequence"],
        "required_holo_controls": freeze_manifest["architecture_protocol"]["required_holo_controls"],
        "ready_for_live_holo": all(checks.values()),
        "next_valid_step": f"Run live preflight for {BATCH_ID}. Do not run solo or judges first.",
    }
    return registration, preflight


def render_md(registration: dict[str, Any], preflight: dict[str, Any]) -> str:
    lines = [
        f"# Wave 2 Holo Target Batch {BATCH_SUFFIX} Staging",
        "",
        f"Created: `{registration['created_at_utc']}`",
        f"Batch: `{registration['batch_id']}`",
        f"Status: `{preflight['status']}`",
        "",
        "## Scope",
        "",
        f"- Pairs: `{registration['pair_count']}`",
        f"- Packets: `{registration['packet_count']}`",
        f"- Expected provider calls when live: `{registration['expected_counts']['total_provider_calls']}`",
        f"- Worker calls: `{registration['expected_counts']['worker_calls']}`",
        f"- Gov calls: `{registration['expected_counts']['gov_calls']}`",
        "- Solo calls: `0`",
        "- Judge calls: `0`",
        "",
        "## Selected Pairs",
        "",
    ]
    for pair_id in registration["selected_pair_ids"]:
        pair_records = [row for row in registration["selected_records"] if row["pair_id"] == pair_id]
        first = pair_records[0]
        lines.append(
            f"- `{pair_id}` ({first['domain']}): `{first['triage_class']}`, "
            f"not_knew `{first['not_knew_count']}`, priority `{first['priority_score']}`"
        )
    lines.extend(
        [
            "",
            "## Model Order",
            "",
        ]
    )
    for row in registration["holo_architecture"]["call_sequence"]:
        lines.append(f"- `{row['turn']}`: `{row['provider']}/{row['model']}` as `{row['role_name']}`")
    lines.extend(["", "## Preflight Checks", ""])
    for key, value in preflight["checks"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Stop Rules",
            "",
            "- No provider calls were made during staging.",
            "- No solo or judge calls are part of this staged batch.",
            "- Gov may not choose or alter models.",
            "- No fallback or model substitution is allowed.",
            "- Packet and prompt hashes must remain matched to the Wave 2 freeze before live execution.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-number", type=int, default=1)
    parser.add_argument("--pair-count", type=int, default=9)
    args = parser.parse_args()
    configure_batch(args.batch_number)
    registration, preflight = collect_batch_records(args.pair_count)
    registration_path = OUTPUT_ROOT / f"{BATCH_ID}_REGISTRATION_2026_07_01.json"
    preflight_path = OUTPUT_ROOT / f"{BATCH_ID}_PREFLIGHT_2026_07_01.json"
    md_path = OUTPUT_ROOT / f"{BATCH_ID}_PREFLIGHT_2026_07_01.md"
    write_json(registration_path, registration)
    write_json(preflight_path, preflight)
    write_text(md_path, render_md(registration, preflight))
    print(json.dumps({"status": preflight["status"], "registration": str(registration_path), "preflight": str(preflight_path)}, indent=2))
    return 0 if preflight["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
