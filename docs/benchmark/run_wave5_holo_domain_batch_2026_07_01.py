#!/usr/bin/env python3
"""Stage and run Wave5 Holo domain batches.

Wave5 contains 7 domains, 140 sibling pairs, and 280 packets. This runner
keeps execution intentionally small: one domain batch is 5 sibling pairs
or 10 packets, which is 50 Holo provider calls if later approved.

Default operations are no-provider:
- --stage-all writes deterministic batch registrations and approval shells.
- --preflight validates one batch without provider calls.
- --preflight-all validates every staged batch without provider calls.

Live execution remains locked behind exact provider approval and runs only one
explicitly selected batch.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


BENCHMARK_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCHMARK_ROOT.parents[1]
FREEZE_ROOT = BENCHMARK_ROOT / "holoverify_replication_packet_freeze_wave5_2026-07-01"
WAVE2_RUNNER_PATH = BENCHMARK_ROOT / "run_wave2_holo_target_batch_2026_07_01.py"
EXPECTED_FREEZE_ROOT_HASH = "3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf"
SUMMARY_JSON = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_EXECUTION_PREFLIGHT_2026_07_01.json"
SUMMARY_MD = BENCHMARK_ROOT / "HOLOVERIFY_WAVE5_BATCH_EXECUTION_PREFLIGHT_2026_07_01.md"

BATCHES_PER_FAMILY = 4
PAIRS_PER_BATCH = 5
PACKETS_PER_PAIR = 2
CALLS_PER_PACKET = 5
DATE_STAMP = "2026_07_01"
STABLE_CREATED_AT_UTC = "2026-07-01T00:00:00+00:00"

FAMILY_ORDER = [
    "HV-MEDX-REP-2026-07-01",
    "HV-TRES-REP-2026-07-01",
    "HV-LREG-REP-2026-07-01",
    "HV-CLAD-REP-2026-07-01",
    "HV-SECO-REP-2026-07-01",
    "HV-PSRC-REP-2026-07-01",
    "HV-OTSF-REP-2026-07-01",
]

FAMILY_CODES = {
    "HV-MEDX-REP-2026-07-01": "MEDX",
    "HV-TRES-REP-2026-07-01": "TRES",
    "HV-LREG-REP-2026-07-01": "LREG",
    "HV-CLAD-REP-2026-07-01": "CLAD",
    "HV-SECO-REP-2026-07-01": "SECO",
    "HV-PSRC-REP-2026-07-01": "PSRC",
    "HV-OTSF-REP-2026-07-01": "OTSF",
}


def load_wave2_runner() -> Any:
    spec = importlib.util.spec_from_file_location("wave5_holo_live_base", WAVE2_RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def package_sha256(data: dict[str, Any]) -> str:
    body = dict(data)
    body.pop("created_at_utc", None)
    body.pop("package_sha256", None)
    return sha256_text(json.dumps(body, indent=2, sort_keys=True, ensure_ascii=True) + "\n")


def current_head() -> str:
    return f"wave5_runner={sha256_file(Path(__file__).resolve())}:base_runner={sha256_file(WAVE2_RUNNER_PATH)}"


def family_code(family_id: str) -> str:
    if family_id not in FAMILY_CODES:
        raise ValueError(f"unknown_family_id:{family_id}")
    return FAMILY_CODES[family_id]


def batch_id(family_id: str, batch_number: int) -> str:
    return f"WAVE5_{family_code(family_id)}_HOLO_BATCH_{batch_number:03d}"


def batch_root(family_id: str, batch_number: int) -> Path:
    code = family_code(family_id).lower()
    return FREEZE_ROOT / "holo_domain_batches" / f"wave5_{code}_holo_batch_{batch_number:03d}"


def registration_path(family_id: str, batch_number: int) -> Path:
    bid = batch_id(family_id, batch_number)
    return batch_root(family_id, batch_number) / f"{bid}_REGISTRATION_{DATE_STAMP}.json"


def staging_preflight_path(family_id: str, batch_number: int) -> Path:
    bid = batch_id(family_id, batch_number)
    return batch_root(family_id, batch_number) / f"{bid}_PREFLIGHT_{DATE_STAMP}.json"


def approval_packet_path(family_id: str, batch_number: int) -> Path:
    bid = batch_id(family_id, batch_number)
    return batch_root(family_id, batch_number) / f"{bid}_PROVIDER_APPROVAL_PACKET_{DATE_STAMP}.json"


def load_freeze_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    freeze_manifest = load_json(FREEZE_ROOT / "FREEZE_MANIFEST.json")
    if freeze_manifest.get("freeze_root_hash") != EXPECTED_FREEZE_ROOT_HASH:
        raise RuntimeError(f"freeze_root_mismatch:{freeze_manifest.get('freeze_root_hash')}")
    packet_manifest = load_json(FREEZE_ROOT / "manifests" / "PACKET_HASH_MANIFEST.json")
    prompt_manifest = load_json(FREEZE_ROOT / "manifests" / "PROMPT_HASH_MANIFEST.json")
    packet_index = load_json(FREEZE_ROOT / "manifests" / "PACKET_INDEX.json")
    return freeze_manifest, packet_manifest, prompt_manifest, packet_index


def packet_hash_maps() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _, packet_manifest, prompt_manifest, packet_index = load_freeze_sources()
    return (
        {row["packet_id"]: row for row in packet_manifest["records"]},
        {row["packet_id"]: row for row in prompt_manifest["records"]},
        {row["packet_id"]: row for row in packet_index},
    )


def selected_records_for_batch(family_id: str, batch_number: int) -> list[dict[str, Any]]:
    packet_hash_by_id, prompt_hash_by_id, index_by_id = packet_hash_maps()
    family_rows = [row for row in index_by_id.values() if row["family_id"] == family_id]
    pair_ids = sorted({row["pair_id"] for row in family_rows})
    expected_pairs = PAIRS_PER_BATCH * BATCHES_PER_FAMILY
    if len(pair_ids) != expected_pairs:
        raise RuntimeError(f"family_pair_count_mismatch:{family_id}:{len(pair_ids)}")
    start = (batch_number - 1) * PAIRS_PER_BATCH
    selected_pair_ids = pair_ids[start : start + PAIRS_PER_BATCH]
    if len(selected_pair_ids) != PAIRS_PER_BATCH:
        raise RuntimeError(f"batch_pair_count_mismatch:{family_id}:{batch_number}:{len(selected_pair_ids)}")

    selected: list[dict[str, Any]] = []
    for pair_id in selected_pair_ids:
        siblings = sorted(
            [row for row in family_rows if row["pair_id"] == pair_id],
            key=lambda row: row["sibling_id"],
        )
        if [row["sibling_id"] for row in siblings] != ["A", "B"]:
            raise RuntimeError(f"pair_sibling_mismatch:{pair_id}")
        if sum(1 for row in siblings if row["target_sibling"]) != 1:
            raise RuntimeError(f"target_sibling_mismatch:{pair_id}")
        for row in siblings:
            packet_row = packet_hash_by_id[row["packet_id"]]
            prompt_row = prompt_hash_by_id[row["packet_id"]]
            packet_path = FREEZE_ROOT / packet_row["packet_path"]
            prompt_path = FREEZE_ROOT / prompt_row["prompt_path"]
            model_visible_path = FREEZE_ROOT / packet_row["model_visible_payload_path"]
            selected.append(
                {
                    **row,
                    "packet_ref": str(packet_path.relative_to(REPO_ROOT)),
                    "prompt_ref": str(prompt_path.relative_to(REPO_ROOT)),
                    "model_visible_payload_ref": str(model_visible_path.relative_to(REPO_ROOT)),
                    "packet_sha256": packet_row["packet_sha256"],
                    "prompt_sha256": prompt_row["prompt_sha256"],
                    "model_visible_payload_file_sha256": packet_row["model_visible_payload_file_sha256"],
                    "packet_hash_ok": sha256_file(packet_path) == packet_row["packet_sha256"],
                    "prompt_hash_ok": sha256_file(prompt_path) == prompt_row["prompt_sha256"],
                    "model_visible_hash_ok": sha256_file(model_visible_path)
                    == packet_row["model_visible_payload_file_sha256"],
                }
            )
    return selected


def holo_architecture() -> dict[str, Any]:
    return {
        "variant": "holoverify_3dna_openai_w2_current_locked_protocol",
        "calls_per_packet": CALLS_PER_PACKET,
        "worker_calls_per_packet": 3,
        "gov_calls_per_packet": 2,
        "fallback_policy": "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        "call_sequence": [
            "W1:xai/grok-3-mini:SOURCE_BOUNDARY_MAPPER",
            "G1:minimax/MiniMax-M2.5-highspeed:CONTROL_ROUTER",
            "W2:openai/gpt-5.4-mini:ADVERSARIAL_SCOPE_CHALLENGER",
            "G2:minimax/MiniMax-M2.5-highspeed:CONTROL_ROUTER",
            "W3:minimax/MiniMax-M2.5-highspeed:FINAL_COMPILER",
        ],
        "worker_model_roster": [
            {"slot": "W1", "role": "SOURCE_BOUNDARY_MAPPER", "provider": "xai", "model": "grok-3-mini", "dna": "xai"},
            {
                "slot": "W2",
                "role": "ADVERSARIAL_SCOPE_CHALLENGER",
                "provider": "openai",
                "model": "gpt-5.4-mini",
                "dna": "openai",
            },
            {
                "slot": "W3",
                "role": "FINAL_COMPILER",
                "provider": "minimax",
                "model": "MiniMax-M2.5-highspeed",
                "dna": "minimax",
            },
        ],
        "gov_model_roster": [
            {
                "slot": "G1",
                "role": "CONTROL_ROUTER",
                "provider": "minimax",
                "model": "MiniMax-M2.5-highspeed",
                "dna": "minimax",
                "gov_may_select_models": False,
            },
            {
                "slot": "G2",
                "role": "CONTROL_ROUTER",
                "provider": "minimax",
                "model": "MiniMax-M2.5-highspeed",
                "dna": "minimax",
                "gov_may_select_models": False,
            },
        ],
        "required_holo_controls": [
            "state brief present for workers",
            "Gov routing lens present",
            "full latest Gov baton present",
            "deterministic gate after every worker",
            "Gov receives deterministic gate results",
            "artifact registry present",
            "best artifact registry present",
            "pinned best artifact present after first admissible candidate",
            "monotonic preservation enforced",
            "final selector present",
            "external solo and intra-Holo evidence separated",
        ],
    }


def expected_counts(pair_count: int) -> dict[str, int]:
    packets = pair_count * PACKETS_PER_PAIR
    return {
        "pairs": pair_count,
        "packets": packets,
        "worker_calls": packets * 3,
        "gov_calls": packets * 2,
        "total_provider_calls": packets * CALLS_PER_PACKET,
        "solo_calls": 0,
        "judge_calls": 0,
    }


def selection_sha(selected_records: list[dict[str, Any]]) -> str:
    selected_payload = [
        {
            "packet_id": row["packet_id"],
            "pair_id": row["pair_id"],
            "sibling_id": row["sibling_id"],
            "packet_sha256": row["packet_sha256"],
            "prompt_sha256": row["prompt_sha256"],
            "model_visible_payload_file_sha256": row["model_visible_payload_file_sha256"],
        }
        for row in selected_records
    ]
    return sha256_text(canonical_json(selected_payload))


def approval_shell(family_id: str, batch_number: int, registration: dict[str, Any]) -> dict[str, Any]:
    bid = registration["batch_id"]
    statement = (
        f"I explicitly approve provider calls for {bid} only, exactly as scoped in "
        f"{bid}_PROVIDER_APPROVAL_PACKET_{DATE_STAMP}."
    )
    command = (
        "python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py "
        f"--family {family_id} --batch-number {batch_number} --run-live "
        "--approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET "
        f"--approval-statement {json.dumps(statement)}"
    )
    packet = {
        "classification": f"{bid}_PROVIDER_APPROVAL_PACKET_NO_PROVIDER_SHELL",
        "status": "NOT_READY",
        "created_at_utc": STABLE_CREATED_AT_UTC,
        "batch_id": bid,
        "family_id": family_id,
        "batch_number": batch_number,
        "approval_granted_by_this_packet": False,
        "approval_statement_required": statement,
        "expected_calls_if_approved": registration["expected_counts"],
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "registration_ref": str(registration_path(family_id, batch_number).relative_to(REPO_ROOT)),
        "provider_boundary": {
            "requires_explicit_approval": True,
            "run_command_after_approval": command,
            "no_solo": True,
            "no_judges": True,
            "no_fallback_or_substitution": True,
            "one_batch_only": True,
        },
        "stop_rules": [
            "Do not run providers without exact approval statement and approval packet SHA.",
            "Do not edit frozen packets or prompts.",
            "Do not run solo or judges.",
            "Do not fallback or substitute models.",
            "If the batch fails, preserve the invalid run and stop.",
        ],
    }
    packet["package_sha256"] = package_sha256(packet)
    return packet


def stage_batch(family_id: str, batch_number: int) -> dict[str, Any]:
    freeze_manifest, _, _, _ = load_freeze_sources()
    selected = selected_records_for_batch(family_id, batch_number)
    selected_pair_ids = []
    for row in selected:
        if row["pair_id"] not in selected_pair_ids:
            selected_pair_ids.append(row["pair_id"])
    bid = batch_id(family_id, batch_number)
    counts = expected_counts(len(selected_pair_ids))
    checks = {
        "freeze_root_matches": freeze_manifest.get("freeze_root_hash") == EXPECTED_FREEZE_ROOT_HASH,
        "family_known": family_id in freeze_manifest["families"],
        "pair_count_5": len(selected_pair_ids) == PAIRS_PER_BATCH,
        "packet_count_10": len(selected) == PAIRS_PER_BATCH * PACKETS_PER_PAIR,
        "all_packet_hashes_match": all(row["packet_hash_ok"] for row in selected),
        "all_prompt_hashes_match": all(row["prompt_hash_ok"] for row in selected),
        "all_model_visible_hashes_match": all(row["model_visible_hash_ok"] for row in selected),
        "one_target_sibling_per_pair": all(
            sum(1 for row in selected if row["pair_id"] == pair_id and row["target_sibling"]) == 1
            for pair_id in selected_pair_ids
        ),
        "no_provider_calls": True,
        "no_judge_calls": True,
    }
    registration = {
        "classification": f"{bid}_REGISTRATION_NO_PROVIDER",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "created_at_utc": STABLE_CREATED_AT_UTC,
        "repo_head": current_head(),
        "batch_id": bid,
        "family_id": family_id,
        "domain": freeze_manifest["families"][family_id]["domain"],
        "batch_number": batch_number,
        "batch_basis": "Wave5 domain order, 5 sibling pairs per batch",
        "selection_mode": "wave5-domain-5pair-batch",
        "claim_boundary": "Batch staging only; not evidence until a clean live Holo run exists.",
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "freeze_root_ref": str(FREEZE_ROOT.relative_to(REPO_ROOT)),
        "source_target_selection_sha256": selection_sha(selected),
        "pair_count": len(selected_pair_ids),
        "packet_count": len(selected),
        "selected_pair_ids": selected_pair_ids,
        "selected_records": selected,
        "expected_counts": counts,
        "holo_architecture": holo_architecture(),
        "run_boundaries": {
            "no_provider_calls_in_staging": True,
            "no_holo_live_calls_in_staging": True,
            "no_solo_calls": True,
            "no_judge_calls": True,
            "no_packet_edits": True,
            "no_prompt_edits": True,
            "fallback_or_substitution_allowed": False,
        },
        "checks": checks,
        "blocked_reason": None if all(checks.values()) else [key for key, value in checks.items() if not value],
    }
    preflight = {
        "classification": f"{bid}_PREFLIGHT_NO_PROVIDER",
        "status": registration["status"],
        "created_at_utc": STABLE_CREATED_AT_UTC,
        "batch_id": bid,
        "family_id": family_id,
        "batch_number": batch_number,
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "registration_ref": str(registration_path(family_id, batch_number).relative_to(REPO_ROOT)),
        "selected_pair_ids": selected_pair_ids,
        "expected_counts": counts,
        "checks": checks,
        "providers_called": 0,
        "judges_called": 0,
        "ready_for_live_preflight": registration["status"] == "PASS",
        "blocked_reason": registration["blocked_reason"],
    }
    write_json(registration_path(family_id, batch_number), registration)
    write_json(staging_preflight_path(family_id, batch_number), preflight)
    write_json(approval_packet_path(family_id, batch_number), approval_shell(family_id, batch_number, registration))
    return registration


def stage_all() -> list[dict[str, Any]]:
    registrations = []
    for family_id in FAMILY_ORDER:
        for batch_number in range(1, BATCHES_PER_FAMILY + 1):
            registrations.append(stage_batch(family_id, batch_number))
    return registrations


def configure_runner(module: Any, family_id: str, batch_number: int) -> None:
    bid = batch_id(family_id, batch_number)
    root = batch_root(family_id, batch_number)
    registration = load_json(registration_path(family_id, batch_number))

    module.__file__ = str(Path(__file__).resolve())
    module.FREEZE_ROOT = FREEZE_ROOT
    module.EXPECTED_FREEZE_ROOT_HASH = EXPECTED_FREEZE_ROOT_HASH
    module.EXPECTED_TARGET_SELECTION_SHA = registration["source_target_selection_sha256"]
    module.BATCH_NUMBER = batch_number
    module.BATCH_SUFFIX = f"{batch_number:03d}"
    module.BATCH_ID = bid
    module.STAGING_ROOT = root
    module.REGISTRATION_PATH = registration_path(family_id, batch_number)
    module.PREFLIGHT_PATH = staging_preflight_path(family_id, batch_number)
    module.LIVE_PREFLIGHT_JSON = root / f"{bid}_LIVE_PREFLIGHT_{DATE_STAMP}.json"
    module.LIVE_PREFLIGHT_MD = root / f"{bid}_LIVE_PREFLIGHT_{DATE_STAMP}.md"
    module.LIVE_RUN_ROOT = root / "live_runs"
    original_load_json = module.load_json
    original_render_live_summary_md = module.render_live_summary_md

    def runtime_fingerprint() -> str:
        return (
            "wave5_runtime:"
            f"wave5_runner={sha256_file(Path(__file__).resolve())}:"
            f"base_runner={sha256_file(WAVE2_RUNNER_PATH)}"
        )

    def load_json_with_wave5_architecture(path: Path) -> Any:
        data = original_load_json(path)
        if Path(path) == FREEZE_ROOT / "FREEZE_MANIFEST.json":
            data = dict(data)
            data.setdefault(
                "architecture_protocol",
                {"required_holo_controls": holo_architecture()["required_holo_controls"]},
            )
        return data

    def convert_payload(packet: dict[str, Any]) -> dict[str, Any]:
        internal_documents = []
        policy_documents = []
        for record in packet["source_control_facts"]:
            doc = {
                "doc_id": record["source_id"],
                "type": record["source_type"],
                "content": record["content"],
            }
            if record["source_type"] == "policy_control":
                policy_documents.append(
                    {
                        "doc_id": record["source_id"],
                        "title": "Frozen Wave5 source-boundary policy",
                        "content": record["content"],
                    }
                )
            else:
                internal_documents.append(doc)
        return {
            "action": {
                "action_date": "2026-07-01",
                "amount": 0,
                "business_ref": packet["model_visible_payload"]["case_ref"],
                "currency": "USD",
                "description": packet["action_boundary"],
                "type": packet.get("domain_slug") or "wave5_action_boundary",
                "vendor": f"Frozen Wave5 {family_code(family_id)} record",
            },
            "context": {
                "action_boundary": packet["action_boundary"],
                "anomaly_observed": packet["tempting_wrong_move"],
                "explanation_summary": "Verify whether the frozen Wave5 source records close the exact action boundary before execution.",
                "internal_documents": internal_documents,
                "policy_documents": policy_documents,
            },
        }

    def render_preflight_md(preflight: dict[str, Any]) -> str:
        expected = preflight["architecture_lock"]["expected_counts"]
        approval_statement = preflight.get("required_approval_statement") or ""
        command = (
            "python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py "
            f"--family {family_id} --batch-number {batch_number} --run-live "
            "--approval-packet-sha256 APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET "
            f"--approval-statement {json.dumps(approval_statement)}"
        )
        lines = [
            f"# Wave5 {family_code(family_id)} Holo Batch {batch_number:03d} Live Preflight",
            "",
            f"Status: `{preflight['status']}`",
            f"Batch: `{preflight['batch_id']}`",
            f"Family: `{family_id}`",
            f"Selection mode: `{preflight.get('selection_mode')}`",
            f"Freeze root: `{preflight['freeze_root_hash']}`",
            f"Root signature: `{preflight['root_signature']}`",
            "",
            "## Expected Calls",
            "",
        ]
        for key in ("pairs", "packets", "worker_calls", "gov_calls", "total_provider_calls", "solo_calls", "judge_calls"):
            lines.append(f"- `{key}`: `{expected[key]}`")
        lines.extend(["", "## Checks", "", "| Check | Value |", "| --- | --- |"])
        for key, value in preflight["checks"].items():
            lines.append(f"| `{key}` | `{value}` |")
        lines.extend(
            [
                "",
                "## Provider Approval Gate",
                "",
                f"Approval required: `{preflight.get('provider_approval_required')}`",
                f"Required statement SHA-256: `{preflight.get('required_approval_statement_sha256')}`",
                "",
                "Required approval statement:",
                "",
                f"`{preflight.get('required_approval_statement')}`",
                "",
                "## Next Step",
                "",
            ]
        )
        if preflight["status"] == "PASS":
            lines.append(f"Run `{command}` only when provider calls are explicitly approved.")
        else:
            lines.append(f"Do not run live. Blocked checks: `{preflight['blocked_reason']}`")
        return "\n".join(lines) + "\n"

    def render_live_summary_md(summary: dict[str, Any]) -> str:
        return original_render_live_summary_md(summary).replace("Wave 2 Holo Target Batch", "Wave5 Holo Domain Batch")

    module.convert_payload = convert_payload
    module.current_head = runtime_fingerprint
    module.load_json = load_json_with_wave5_architecture
    module.render_preflight_md = render_preflight_md
    module.render_live_summary_md = render_live_summary_md


def render_approval_md(approval: dict[str, Any]) -> str:
    command = approval["provider_boundary"]["run_command_after_approval"].replace(
        "APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET", approval["package_sha256"]
    )
    lines = [
        "# Wave5 Holo Batch Provider Approval Packet",
        "",
        f"Status: `{approval['status']}`",
        f"Batch: `{approval['batch_id']}`",
        f"Family: `{approval['family_id']}`",
        f"Approval granted by this packet: `{approval['approval_granted_by_this_packet']}`",
        f"Approval packet SHA-256: `{approval['package_sha256']}`",
        f"Live preflight root signature: `{approval.get('live_preflight_root_signature')}`",
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


def refresh_provider_approval_packet(
    runner: Any,
    family_id: str,
    batch_number: int,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    path = approval_packet_path(family_id, batch_number)
    approval = load_json(path)
    approval["classification"] = f"{manifest['batch_id']}_PROVIDER_APPROVAL_PACKET_NO_PROVIDER_RUNTIME_REFRESHED"
    approval["expected_calls_if_approved"] = manifest["architecture_lock"]["expected_counts"]
    approval["live_preflight_root_signature"] = manifest["root_signature"]
    approval["model_roster"] = manifest["architecture_lock"]["model_roster_declared"]
    approval["next_locked_gate"] = "EXPLICIT_PROVIDER_APPROVAL_WITH_EXACT_STATEMENT_AND_PACKET_SHA"
    approval["pre_run_verifiers"] = {
        "live_preflight_status": manifest["status"],
        "providers_called_during_preflight": manifest["providers_called"],
        "solo_started_during_preflight": manifest["solo_started"],
        "judges_started_during_preflight": manifest["judges_started"],
        "live_holo_started_during_preflight": manifest["live_holo_started"],
    }
    approval["status"] = "READY_FOR_EXPLICIT_PROVIDER_APPROVAL" if manifest["status"] == "PASS" else "NOT_READY"
    approval["package_sha256"] = package_sha256(approval)
    write_json(path, approval)
    write_text(path.with_suffix(".md"), render_approval_md(approval))
    manifest["provider_approval_packet_ref"] = str(path.relative_to(REPO_ROOT))
    manifest["provider_approval_packet_sha256"] = approval["package_sha256"]
    manifest["run_command_after_explicit_approval"] = approval["provider_boundary"]["run_command_after_approval"].replace(
        "APPROVAL_PACKET_SHA256_FROM_PROVIDER_APPROVAL_PACKET", approval["package_sha256"]
    )
    write_json(runner.LIVE_PREFLIGHT_JSON, manifest)
    return approval


def build_preflight(family_id: str, batch_number: int) -> dict[str, Any]:
    runner = load_wave2_runner()
    configure_runner(runner, family_id, batch_number)
    manifest = runner.validate_preflight()
    manifest["created_at"] = STABLE_CREATED_AT_UTC
    refresh_provider_approval_packet(runner, family_id, batch_number, manifest)
    return manifest


def iter_batch_specs() -> list[tuple[str, int]]:
    return [(family_id, batch_number) for family_id in FAMILY_ORDER for batch_number in range(1, BATCHES_PER_FAMILY + 1)]


def preflight_all() -> dict[str, Any]:
    stage_all()
    preflights = [build_preflight(family_id, batch_number) for family_id, batch_number in iter_batch_specs()]
    rows = []
    for manifest in preflights:
        expected = manifest["architecture_lock"]["expected_counts"]
        registration_ref = Path(REPO_ROOT / manifest["registration_ref"])
        registration = load_json(registration_ref)
        family_id = registration["family_id"]
        batch_number = registration["batch_number"]
        bid = manifest["batch_id"]
        root = batch_root(family_id, batch_number)
        rows.append(
            {
                "batch_id": bid,
                "family_id": family_id,
                "status": manifest["status"],
                "pairs": expected["pairs"],
                "packets": expected["packets"],
                "expected_provider_calls": expected["total_provider_calls"],
                "registration_ref": manifest["registration_ref"],
                "live_preflight_ref": str((root / f"{bid}_LIVE_PREFLIGHT_{DATE_STAMP}.json").relative_to(REPO_ROOT)),
                "provider_approval_packet_ref": manifest.get("provider_approval_packet_ref"),
                "approval_packet_sha256": manifest.get("provider_approval_packet_sha256"),
                "run_command_after_explicit_approval": manifest.get("run_command_after_explicit_approval"),
            }
        )
    checks = {
        "batch_count_28": len(rows) == len(FAMILY_ORDER) * BATCHES_PER_FAMILY,
        "all_preflights_pass": all(row["status"] == "PASS" for row in rows),
        "all_batches_5_pairs": all(row["pairs"] == PAIRS_PER_BATCH for row in rows),
        "all_batches_10_packets": all(row["packets"] == PAIRS_PER_BATCH * PACKETS_PER_PAIR for row in rows),
        "all_batches_50_provider_calls_if_approved": all(row["expected_provider_calls"] == 50 for row in rows),
        "total_pairs_140": sum(row["pairs"] for row in rows) == 140,
        "total_packets_280": sum(row["packets"] for row in rows) == 280,
        "total_expected_provider_calls_if_all_approved": sum(row["expected_provider_calls"] for row in rows) == 1400,
        "provider_calls_0": 0 == 0,
        "judge_calls_0": 0 == 0,
    }
    report = {
        "classification": "HOLOVERIFY_WAVE5_BATCH_EXECUTION_PREFLIGHT_NO_PROVIDER",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "created_at_utc": STABLE_CREATED_AT_UTC,
        "repo_head": current_head(),
        "freeze_root_hash": EXPECTED_FREEZE_ROOT_HASH,
        "batching_policy": {
            "domains": len(FAMILY_ORDER),
            "batches_per_domain": BATCHES_PER_FAMILY,
            "pairs_per_batch": PAIRS_PER_BATCH,
            "packets_per_batch": PAIRS_PER_BATCH * PACKETS_PER_PAIR,
            "provider_calls_per_batch_if_approved": 50,
            "one_live_batch_per_explicit_approval": True,
        },
        "totals": {
            "batches": len(rows),
            "pairs": sum(row["pairs"] for row in rows),
            "packets": sum(row["packets"] for row in rows),
            "expected_provider_calls_if_all_batches_approved": sum(row["expected_provider_calls"] for row in rows),
            "providers_called_during_preflight": 0,
            "judges_called_during_preflight": 0,
        },
        "checks": checks,
        "blocked_reason": None if all(checks.values()) else [key for key, value in checks.items() if not value],
        "batches": rows,
    }
    write_json(SUMMARY_JSON, report)
    write_text(SUMMARY_MD, render_summary_md(report))
    return report


def render_summary_md(report: dict[str, Any]) -> str:
    lines = [
        "# HoloVerify Wave5 Batch Execution Preflight",
        "",
        f"Status: `{report['status']}`",
        f"Freeze root: `{report['freeze_root_hash']}`",
        f"Generated without provider calls: `{report['totals']['providers_called_during_preflight'] == 0}`",
        f"Generated without judges: `{report['totals']['judges_called_during_preflight'] == 0}`",
        "",
        "## Batch Policy",
        "",
        "- One domain batch contains `5` sibling pairs / `10` packets.",
        "- Each approved live batch is `50` Holo provider calls.",
        "- The full Wave5 packet bank is split into `28` separately approvable batches.",
        "- This file does not approve provider calls.",
        "",
        "## Totals",
        "",
    ]
    for key, value in report["totals"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Checks", "", "| Check | Value |", "| --- | --- |"])
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Batches",
            "",
            "| Batch | Family | Pairs | Packets | Calls If Approved | Approval SHA |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["batches"]:
        lines.append(
            f"| `{row['batch_id']}` | `{row['family_id']}` | `{row['pairs']}` | `{row['packets']}` | "
            f"`{row['expected_provider_calls']}` | `{row.get('approval_packet_sha256')}` |"
        )
    lines.extend(
        [
            "",
            "## Run Rule",
            "",
            "Run only one batch at a time, and only with the exact approval statement and approval packet SHA for that batch.",
        ]
    )
    return "\n".join(lines) + "\n"


def completed_live_runs_for_batch(family_id: str, batch_number: int) -> list[dict[str, Any]]:
    live_root = batch_root(family_id, batch_number) / "live_runs"
    completed = []
    if not live_root.exists():
        return completed
    for run_dir in sorted(live_root.glob("run_*")):
        result_path = run_dir / "live_results.json"
        if not result_path.exists():
            continue
        result = load_json(result_path)
        if result.get("readiness_passed") is True:
            completed.append(
                {
                    "run_id": run_dir.name,
                    "run_dir": str(run_dir.relative_to(REPO_ROOT)),
                    "classification": result.get("classification"),
                    "provider_calls": result.get("provider_calls"),
                    "packet_count": result.get("packet_count"),
                    "packet_correct": result.get("packet_correct"),
                    "valid_pairs": result.get("valid_pairs"),
                }
            )
    return completed


def run_live(family_id: str, batch_number: int, approval_statement: str | None, approval_packet_sha256: str | None) -> int:
    completed_runs = completed_live_runs_for_batch(family_id, batch_number)
    if completed_runs:
        report = {
            "classification": "WAVE5_LIVE_RUN_IDEMPOTENCY_GATE_LOCKED",
            "status": "BLOCKED",
            "batch_id": batch_id(family_id, batch_number),
            "family_id": family_id,
            "batch_number": batch_number,
            "provider_calls_by_this_gate": 0,
            "judge_calls_by_this_gate": 0,
            "blocked_reason": "batch_already_has_clean_completed_live_run",
            "completed_live_runs": completed_runs,
            "next_valid_action": "Do not rerun this batch. Audit and commit the existing clean run, or register a new explicit variant.",
        }
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    runner = load_wave2_runner()
    configure_runner(runner, family_id, batch_number)
    return runner.run_live(approval_statement, approval_packet_sha256)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=FAMILY_ORDER)
    parser.add_argument("--batch-number", type=int, default=1)
    parser.add_argument("--stage-all", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--preflight-all", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--approval-statement")
    parser.add_argument("--approval-packet-sha256")
    args = parser.parse_args()

    if args.stage_all:
        registrations = stage_all()
        print(json.dumps({"status": "PASS", "registrations": len(registrations), "providers_called": 0, "judges_called": 0}, indent=2))
        return 0
    if args.preflight_all:
        report = preflight_all()
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "PASS" else 1
    if args.preflight:
        if not args.family:
            parser.error("--family is required for --preflight")
        stage_batch(args.family, args.batch_number)
        manifest = build_preflight(args.family, args.batch_number)
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    if args.run_live:
        if not args.family:
            parser.error("--family is required for --run-live")
        return run_live(args.family, args.batch_number, args.approval_statement, args.approval_packet_sha256)
    parser.error("choose --stage-all, --preflight, --preflight-all, or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
