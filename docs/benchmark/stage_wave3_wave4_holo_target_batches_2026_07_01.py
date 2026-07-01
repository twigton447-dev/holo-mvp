#!/usr/bin/env python3
"""Stage Wave 3 / Wave 4 HoloVerify target batches without provider calls."""

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
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_wave3_wave4_2026-07-01"
EXPECTED_FREEZE_ROOT_HASH = "ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5"
DATE_STAMP = "2026_07_01"

WAVE_CONFIG = {
    "wave3": {
        "batch_id": "WAVE3_HOLO_TARGET_BATCH_001",
        "output_dir": "wave3_holo_target_batch_001",
        "solo_dir": "wave3_solo_triage",
        "title": "Wave 3 Holo Target Batch 001",
    },
    "wave4": {
        "batch_id": "WAVE4_HOLO_TARGET_BATCH_001",
        "output_dir": "wave4_holo_target_batch_001",
        "solo_dir": "wave4_solo_triage",
        "title": "Wave 4 Holo Target Batch 001",
    },
}

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


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


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


def frozen_assets_clean_in_git() -> bool:
    return not git_diff_names(FREEZE_ROOT / "families") and not git_diff_names(FREEZE_ROOT / "manifests")


def latest_solo_results(wave: str) -> Path:
    solo_root = FREEZE_ROOT / "solo_triage_3mini" / WAVE_CONFIG[wave]["solo_dir"]
    candidates = sorted(solo_root.glob("run_*/solo_triage_results.json"))
    if not candidates:
        raise RuntimeError(f"missing_solo_triage_results:{solo_root}")
    return candidates[-1]


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def approval_statement(batch_id: str) -> str:
    return (
        f"I explicitly approve provider calls for {batch_id} only, exactly as scoped in "
        f"{batch_id}_PROVIDER_APPROVAL_PACKET_{DATE_STAMP}."
    )


def build_records(selected_pairs: list[dict[str, Any]], wave: str) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    packet_manifest = load_json(FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = load_json(FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    packet_index = load_json(FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")

    packet_hash_by_id = {row["packet_id"]: row for row in packet_manifest["records"]}
    prompt_hash_by_id = {row["packet_id"]: row for row in prompt_manifest["records"]}
    index_by_id = {row["packet_id"]: row for row in packet_index}

    records: list[dict[str, Any]] = []
    prompt_leakage_hits: list[dict[str, str]] = []
    for pair in selected_pairs:
        if len(pair["packets"]) != 2:
            raise RuntimeError(f"pair_without_two_siblings:{pair['pair_id']}")
        for packet_id in pair["packets"]:
            packet_row = packet_hash_by_id[packet_id]
            prompt_row = prompt_hash_by_id[packet_id]
            index_row = index_by_id[packet_id]
            packet_path = FREEZE_ROOT / packet_row["packet_path"]
            prompt_path = FREEZE_ROOT / prompt_row["prompt_path"]
            model_visible_path = FREEZE_ROOT / packet_row["model_visible_payload_path"]
            prompt_text = prompt_path.read_text()
            lower_prompt = prompt_text.lower()
            for term in FORBIDDEN_PROMPT_TERMS:
                if term.lower() in lower_prompt:
                    prompt_leakage_hits.append({"packet_id": packet_id, "term": term})
            records.append(
                {
                    "domain": index_row["domain"],
                    "family_id": index_row["family_id"],
                    "model_visible_hash_ok": sha256_file(model_visible_path) == packet_row["model_visible_payload_file_sha256"],
                    "model_visible_payload_file_sha256": packet_row["model_visible_payload_file_sha256"],
                    "model_visible_payload_ref": str(model_visible_path.relative_to(REPO_ROOT)),
                    "not_knew_count": pair.get("not_knew_count"),
                    "packet_hash_ok": sha256_file(packet_path) == packet_row["packet_sha256"],
                    "packet_id": packet_id,
                    "packet_ref": str(packet_path.relative_to(REPO_ROOT)),
                    "packet_sha256": packet_row["packet_sha256"],
                    "packet_truth": index_row["packet_truth"],
                    "pair_id": pair["pair_id"],
                    "parse_or_provider_fail_count": pair.get("parse_or_provider_fail_count"),
                    "priority_score": pair.get("priority_score"),
                    "prompt_hash_ok": sha256_file(prompt_path) == prompt_row["prompt_sha256"],
                    "prompt_ref": str(prompt_path.relative_to(REPO_ROOT)),
                    "prompt_sha256": prompt_row["prompt_sha256"],
                    "sibling_id": index_row["sibling_id"],
                    "target_bucket": index_row["target_bucket"],
                    "target_sibling": index_row["target_sibling"],
                    "triage_class": pair.get("triage_class", "UNKNOWN"),
                    "wave": wave,
                    "wrong_verdict_count": pair.get("wrong_verdict_count"),
                }
            )
    return records, prompt_leakage_hits


def build_package(wave: str, pair_limit: int | None) -> dict[str, Any]:
    cfg = WAVE_CONFIG[wave]
    freeze_manifest = load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    solo_path = latest_solo_results(wave)
    solo_results = load_json(solo_path)
    selected_pairs = list(solo_results.get("top_holo_targets") or [])
    if pair_limit is not None:
        selected_pairs = selected_pairs[:pair_limit]
    records, prompt_leakage_hits = build_records(selected_pairs, wave)
    batch_id = cfg["batch_id"]
    output_root = FREEZE_ROOT / "holo_target_batches" / cfg["output_dir"]
    registration_path = output_root / f"{batch_id}_REGISTRATION_{DATE_STAMP}.json"
    preflight_path = output_root / f"{batch_id}_PREFLIGHT_{DATE_STAMP}.json"
    preflight_md_path = output_root / f"{batch_id}_PREFLIGHT_{DATE_STAMP}.md"
    approval_json_path = output_root / f"{batch_id}_PROVIDER_APPROVAL_PACKET_{DATE_STAMP}.json"
    approval_md_path = output_root / f"{batch_id}_PROVIDER_APPROVAL_PACKET_{DATE_STAMP}.md"

    architecture = freeze_manifest["architecture_protocol"]
    expected_counts = {
        "gov_calls": len(records) * architecture["gov_calls_per_packet"],
        "judge_calls": 0,
        "packets": len(records),
        "pairs": len(selected_pairs),
        "solo_calls": 0,
        "total_provider_calls": len(records) * architecture["calls_per_packet"],
        "worker_calls": len(records) * architecture["worker_calls_per_packet"],
    }
    registration = {
        "batch_id": batch_id,
        "classification": f"{batch_id}_REGISTRATION_NO_PROVIDER",
        "claim_boundary": "Selected-target staging only; not scored until a clean live Holo run exists.",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_counts": expected_counts,
        "freeze_root_hash": freeze_manifest.get("freeze_root_hash"),
        "freeze_root_ref": str(FREEZE_ROOT.relative_to(REPO_ROOT)),
        "holo_architecture": architecture,
        "repo_head": current_head(),
        "run_boundaries": {
            "fallback_or_substitution_allowed": False,
            "no_holo_live_calls_in_staging": True,
            "no_judge_calls": True,
            "no_packet_edits": True,
            "no_prompt_edits": True,
            "no_provider_calls_in_staging": True,
            "no_solo_calls": True,
        },
        "selected_pair_ids": [row["pair_id"] for row in selected_pairs],
        "selected_records": records,
        "source_solo_results_ref": str(solo_path.relative_to(REPO_ROOT)),
        "source_solo_results_sha256": sha256_file(solo_path),
        "source_target_selection_sha256": sha256_file(solo_path),
        "wave": wave,
    }
    pair_record_counts = {
        pair["pair_id"]: sum(1 for record in records if record["pair_id"] == pair["pair_id"]) for pair in selected_pairs
    }
    checks = {
        "all_pairs_have_two_siblings": all(count == 2 for count in pair_record_counts.values()),
        "expected_judge_calls_0": expected_counts["judge_calls"] == 0,
        "expected_solo_calls_0": expected_counts["solo_calls"] == 0,
        "expected_total_provider_calls": expected_counts["total_provider_calls"] == len(selected_pairs) * 10,
        "freeze_root_matches_expected": freeze_manifest.get("freeze_root_hash") == EXPECTED_FREEZE_ROOT_HASH,
        "frozen_assets_clean_in_git": frozen_assets_clean_in_git(),
        "gov_cannot_choose_models": architecture.get("gov_may_select_models") is False,
        "model_visible_hashes_match": all(record["model_visible_hash_ok"] for record in records),
        "no_prompt_leakage_hits": not prompt_leakage_hits,
        "packet_hashes_match": all(record["packet_hash_ok"] for record in records),
        "pair_count_matches_selected_targets": len(selected_pairs) == len(solo_results.get("top_holo_targets") or []) if pair_limit is None else len(selected_pairs) == pair_limit,
        "prompt_hashes_match": all(record["prompt_hash_ok"] for record in records),
        "solo_triage_complete": solo_results.get("classification") == "HOLOVERIFY_REPLICATION_WAVE3_WAVE4_SOLO_TRIAGE_COMPLETE",
        "solo_triage_expected_provider_calls": solo_results.get("provider_calls") == solo_results.get("expected_provider_calls") == 360,
        "solo_triage_no_gov_holo_judges": solo_results.get("gov_calls") == 0 and solo_results.get("holo_calls") == 0 and solo_results.get("judge_calls") == 0,
        "solo_triage_no_provider_failures": not solo_results.get("provider_failures"),
    }
    preflight = {
        "batch_id": batch_id,
        "checks": checks,
        "classification": f"{batch_id}_PREFLIGHT_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_counts": expected_counts,
        "model_roster": architecture["call_sequence"],
        "prompt_leakage_hits": prompt_leakage_hits,
        "ready_for_provider_approval_packet": all(checks.values()),
        "required_holo_controls": architecture["required_holo_controls"],
        "status": "PASS" if all(checks.values()) else "FAIL",
        "wave": wave,
    }
    approval = {
        "approval_granted_by_this_packet": False,
        "approval_required": True,
        "approval_statement_required": approval_statement(batch_id),
        "batch_id": batch_id,
        "classification": f"{batch_id}_PROVIDER_APPROVAL_PACKET_NO_PROVIDER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_calls_if_approved": expected_counts,
        "generated_without_provider_calls": True,
        "model_roster": architecture["call_sequence"],
        "packet_scope": {
            "packet_count": expected_counts["packets"],
            "pair_count": expected_counts["pairs"],
            "selected_pair_ids": registration["selected_pair_ids"],
            "wave": wave,
        },
        "provider_boundary": {
            "live_runner_status": "PENDING_OR_SEPARATE",
            "run_command_after_approval": (
                "python3 -B docs/benchmark/run_wave3_wave4_holo_target_batch_2026_07_01.py "
                f"--wave {wave} --batch-number 1 --run-live "
                "--approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET "
                f"--approval-statement {json.dumps(approval_statement(batch_id))}"
            ),
        },
        "source_paths": {
            "registration": str(registration_path.relative_to(REPO_ROOT)),
            "preflight": str(preflight_path.relative_to(REPO_ROOT)),
            "solo_triage_results": str(solo_path.relative_to(REPO_ROOT)),
        },
        "status": "READY_FOR_EXPLICIT_PROVIDER_APPROVAL" if preflight["status"] == "PASS" else "NOT_READY",
        "stop_rules": [
            "Do not run providers without explicit approval.",
            "Do not run solo or judges.",
            "Do not edit frozen packets or prompts.",
            "No fallback or model substitution.",
        ],
    }
    approval["package_sha256"] = package_sha256(approval)

    write_json(registration_path, registration)
    write_json(preflight_path, preflight)
    write_text(preflight_md_path, render_preflight_md(cfg["title"], registration, preflight))
    write_json(approval_json_path, approval)
    write_text(approval_md_path, render_approval_md(cfg["title"], approval))
    return {
        "approval_packet": str(approval_json_path),
        "batch_id": batch_id,
        "expected_counts": expected_counts,
        "preflight": str(preflight_path),
        "registration": str(registration_path),
        "status": preflight["status"],
        "wave": wave,
    }


def render_preflight_md(title: str, registration: dict[str, Any], preflight: dict[str, Any]) -> str:
    lines = [
        f"# {title} Staging",
        "",
        f"Batch: `{registration['batch_id']}`",
        f"Status: `{preflight['status']}`",
        f"Claim boundary: {registration['claim_boundary']}",
        "",
        "## Scope",
        "",
    ]
    for key in ("pairs", "packets", "worker_calls", "gov_calls", "total_provider_calls", "solo_calls", "judge_calls"):
        lines.append(f"- `{key}`: `{registration['expected_counts'][key]}`")
    lines.extend(["", "## Selected Pairs", ""])
    for pair_id in registration["selected_pair_ids"]:
        row = next(record for record in registration["selected_records"] if record["pair_id"] == pair_id)
        lines.append(
            f"- `{pair_id}` ({row['domain']}): `{row['target_bucket']}`, `{row['triage_class']}`, "
            f"not-KNEW `{row['not_knew_count']}`, wrong-verdict `{row['wrong_verdict_count']}`"
        )
    lines.extend(["", "## Model Order", ""])
    for item in registration["holo_architecture"]["call_sequence"]:
        lines.append(f"- `{item}`")
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
            "- Packet and prompt hashes must remain matched to the Wave3/Wave4 freeze before live execution.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_approval_md(title: str, approval: dict[str, Any]) -> str:
    command = approval["provider_boundary"]["run_command_after_approval"].replace(
        "APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET", approval["package_sha256"]
    )
    lines = [
        f"# {title} Provider Approval Packet",
        "",
        f"Status: `{approval['status']}`",
        f"Approval granted by this packet: `{approval['approval_granted_by_this_packet']}`",
        f"Approval packet SHA-256: `{approval['package_sha256']}`",
        "",
        "## Required Statement",
        "",
        f"`{approval['approval_statement_required']}`",
        "",
        "## Expected Calls If Approved",
        "",
    ]
    for key, value in approval["expected_calls_if_approved"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Command After Explicit Approval", "", "```bash", command, "```", ""])
    lines.extend(["## Stop Rules", ""])
    lines.extend(f"- {rule}" for rule in approval["stop_rules"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave", choices=tuple(WAVE_CONFIG) + ("both",), default="both")
    parser.add_argument("--pair-limit", type=int)
    args = parser.parse_args()
    waves = ["wave3", "wave4"] if args.wave == "both" else [args.wave]
    results = [build_package(wave, args.pair_limit) for wave in waves]
    print(json.dumps({"provider_calls": 0, "judge_calls": 0, "results": results}, indent=2, sort_keys=True))
    return 0 if all(row["status"] == "PASS" for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
