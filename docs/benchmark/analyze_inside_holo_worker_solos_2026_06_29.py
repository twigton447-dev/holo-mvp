#!/usr/bin/env python3
"""Score frozen Holo worker turns as standalone solo artifacts.

This answers a narrow question: if the same MiniMax worker calls inside Holo
were treated as standalone final answers, do any fail the 10 locked packets?

No provider calls are made. This is a derived analysis over frozen traces.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_hard_allow_fp_5pair_solo_and_knew_judges_2026_06_28 import (
    canonical_json,
    iter_packets,
    local_knew_label,
    sha256_file,
    validate_freeze,
)


BENCHMARK_ROOT = Path(__file__).resolve().parent
OUT_ROOT = BENCHMARK_ROOT / "inside_holo_worker_solo_autopsy_2026-06-29"
EXCLUDED_LOCK_FILES = {"LOCK_MANIFEST.json", "LOCK_VALIDATION.json"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_first_key(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for item in value.values():
            found = find_first_key(item, key)
            if found is not None:
                return found
    if isinstance(value, list):
        for item in value:
            found = find_first_key(item, key)
            if found is not None:
                return found
    return None


def worker_record(packet: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    parsed = row.get("parsed_json")
    if row.get("parse_ok"):
        local = local_knew_label(parsed, packet)
    else:
        local = {"label": "CONFUSED", "passes": False, "failures": [row.get("parse_error") or "parse_failed"]}
    gate_result = row.get("gate_result") if isinstance(row.get("gate_result"), dict) else {}
    gate_passed = gate_result.get("passed") if "passed" in gate_result else row.get("admissible")
    deterministic_failures = gate_result.get("failures") or row.get("deterministic_failures") or []
    failure_reasons: list[str] = []
    if not row.get("provider_call_ok"):
        failure_reasons.append("provider_call_failed")
    if not row.get("parse_ok"):
        failure_reasons.append("parse_failed")
    if gate_passed is not True:
        failure_reasons.append("deterministic_gate_failed")
    if not local["passes"]:
        failure_reasons.append(f"standalone_knew_failed:{local['label']}")
    selected_artifact = packet["holo_packet_result"].get("final_selector", {}).get("selected_artifact_id")
    artifact_id = row.get("artifact_id")
    if not failure_reasons:
        correction_path = "none_needed"
    elif row.get("worker_index", 0) < 3:
        correction_path = "next_hologov_baton_then_later_worker_or_final_selector"
    elif selected_artifact and selected_artifact != artifact_id:
        correction_path = "final_selector_rejected_regressed_worker_and_selected_best_prior"
    elif packet["holo_packet_result"].get("final_admissible") is True:
        correction_path = "final_selected_artifact_passed_holo_local_gate"
    else:
        correction_path = "not_corrected_in_final_holo_result"
    return {
        "packet_id": packet["packet_id"],
        "pair_id": packet["pair_id"],
        "packet_kind": packet["kind"],
        "worker_index": row.get("worker_index"),
        "role_name": row.get("role_name"),
        "provider": row.get("provider"),
        "model": row.get("model"),
        "artifact_id": row.get("artifact_id"),
        "provider_call_ok": row.get("provider_call_ok"),
        "parse_ok": row.get("parse_ok"),
        "admissible": row.get("admissible"),
        "gate_passed": gate_passed,
        "deterministic_gate_failures": deterministic_failures,
        "verification_verdict": parsed.get("verification_verdict") if isinstance(parsed, dict) else find_first_key(parsed, "verification_verdict"),
        "binding_class": find_first_key(parsed, "binding_class"),
        "local_knew_label_as_standalone_solo": local["label"],
        "local_knew_pass_as_standalone_solo": local["passes"],
        "local_knew_failures_as_standalone_solo": local["failures"],
        "internal_failure_before_holo_correction": bool(failure_reasons),
        "internal_failure_reasons": failure_reasons,
        "correction_path": correction_path,
        "final_selected_artifact_id": selected_artifact,
    }


def build_analysis() -> dict[str, Any]:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    freeze = validate_freeze()
    packets = iter_packets(freeze)
    worker_rows: list[dict[str, Any]] = []
    for packet in packets:
        for row in packet["holo_trace_rows"]:
            if row.get("call_kind") == "worker":
                worker_rows.append(worker_record(packet, row))

    by_role: dict[str, dict[str, Any]] = {}
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in worker_rows:
        grouped[(row["worker_index"], row["role_name"])].append(row)
    for (worker_index, role_name), rows in sorted(grouped.items()):
        passes = sum(1 for row in rows if row["local_knew_pass_as_standalone_solo"])
        by_role[f"worker_{worker_index}_{role_name}"] = {
            "worker_index": worker_index,
            "role_name": role_name,
            "worker_count": len(rows),
            "local_knew_passes": passes,
            "local_knew_failures": len(rows) - passes,
            "internal_failures_before_holo_correction": sum(1 for row in rows if row["internal_failure_before_holo_correction"]),
            "failed_packets": [
                {
                    "packet_id": row["packet_id"],
                    "packet_kind": row["packet_kind"],
                    "label": row["local_knew_label_as_standalone_solo"],
                    "gate_passed": row["gate_passed"],
                    "failures": row["local_knew_failures_as_standalone_solo"],
                    "internal_failure_reasons": row["internal_failure_reasons"],
                    "correction_path": row["correction_path"],
                    "verdict": row["verification_verdict"],
                    "binding_class": row["binding_class"],
                }
                for row in rows
                if row["internal_failure_before_holo_correction"]
            ],
        }

    by_packet: dict[str, dict[str, Any]] = {}
    packet_grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in worker_rows:
        packet_grouped[row["packet_id"]].append(row)
    for packet_id, rows in sorted(packet_grouped.items()):
        passes = sum(1 for row in rows if row["local_knew_pass_as_standalone_solo"])
        by_packet[packet_id] = {
            "packet_id": packet_id,
            "packet_kind": rows[0]["packet_kind"],
            "standalone_worker_knew_passes": passes,
            "standalone_worker_knew_failures": len(rows) - passes,
            "internal_failures_before_holo_correction": sum(1 for row in rows if row["internal_failure_before_holo_correction"]),
            "all_worker_turns_knew": passes == len(rows),
            "worker_labels": [
                {
                    "worker_index": row["worker_index"],
                    "role_name": row["role_name"],
                    "label": row["local_knew_label_as_standalone_solo"],
                    "passes": row["local_knew_pass_as_standalone_solo"],
                    "gate_passed": row["gate_passed"],
                    "failures": row["local_knew_failures_as_standalone_solo"],
                    "internal_failure_reasons": row["internal_failure_reasons"],
                    "correction_path": row["correction_path"],
                }
                for row in sorted(rows, key=lambda item: item["worker_index"])
            ],
        }

    total_passes = sum(1 for row in worker_rows if row["local_knew_pass_as_standalone_solo"])
    internal_failures = sum(1 for row in worker_rows if row["internal_failure_before_holo_correction"])
    analysis = {
        "classification": "INSIDE_HOLO_WORKER_SOLO_AUTOPSY",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider_calls_made_now": 0,
        "source": "derived_from_frozen_holo_full_trace_worker_rows",
        "freeze_root_signature": freeze["root_signature"],
        "packet_count": len(packets),
        "worker_turn_count": len(worker_rows),
        "provider_model_substrate": sorted({f"{row['provider']}::{row['model']}" for row in worker_rows}),
        "scoring_rule": "Each Holo worker turn is scored as if it were a standalone solo final artifact. Only KNEW passes.",
        "internal_failure_definition": [
            "provider_call_ok is not true",
            "parse_ok is not true",
            "deterministic gate did not pass",
            "standalone KNEW label is not KNEW",
        ],
        "overall": {
            "standalone_worker_knew_passes": total_passes,
            "standalone_worker_knew_failures": len(worker_rows) - total_passes,
            "standalone_worker_knew_rate": total_passes / len(worker_rows) if worker_rows else None,
            "internal_failures_before_holo_correction": internal_failures,
            "packets_with_at_least_one_worker_failure": sum(1 for row in by_packet.values() if row["standalone_worker_knew_failures"] > 0),
            "packets_with_at_least_one_internal_failure_before_holo_correction": sum(
                1 for row in by_packet.values() if row["internal_failures_before_holo_correction"] > 0
            ),
            "packets_where_all_worker_turns_knew": sum(1 for row in by_packet.values() if row["all_worker_turns_knew"]),
        },
        "by_role": by_role,
        "by_packet": by_packet,
        "worker_turns": worker_rows,
        "interpretation": (
            "The same MiniMax substrate inside Holo can fail before HoloGov/full architecture correction when individual worker turns are treated as standalone solos or gate-checked in isolation. "
            "Holo's 10/10 final KNEW result depends on governance, gates, state, artifact selection, and repair across turns, not on every single worker call being independently perfect."
        ),
    }
    (OUT_ROOT / "INSIDE_HOLO_WORKER_SOLO_AUTOPSY.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    write_markdown(analysis)
    return analysis


def write_markdown(analysis: dict[str, Any]) -> None:
    lines = [
        "# Inside-Holo Worker Solo Autopsy",
        "",
        "Classification: `INSIDE_HOLO_WORKER_SOLO_AUTOPSY`",
        "",
        f"Freeze root signature: `{analysis['freeze_root_signature']}`",
        "",
        "Provider calls made now: `0`",
        "",
        "## Question",
        "",
        "If the same MiniMax worker calls inside Holo are treated as standalone solo final answers, do any fail the 10 locked packets?",
        "",
        "## Answer",
        "",
        f"Yes. Standalone inside-Holo worker turns passed KNEW on `{analysis['overall']['standalone_worker_knew_passes']}/{analysis['worker_turn_count']}` worker turns.",
        "",
        f"Packets with at least one standalone worker failure: `{analysis['overall']['packets_with_at_least_one_worker_failure']}/{analysis['packet_count']}`.",
        "",
        f"Internal failures before Holo correction, including deterministic gate failures and standalone KNEW failures: `{analysis['overall']['internal_failures_before_holo_correction']}/{analysis['worker_turn_count']}` worker turns.",
        "",
        f"Packets with at least one internal failure before Holo correction: `{analysis['overall']['packets_with_at_least_one_internal_failure_before_holo_correction']}/{analysis['packet_count']}`.",
        "",
        "This means Holo's 10/10 final KNEW result is not explained by every MiniMax worker being individually perfect. It is explained by the full architecture: Gov, deterministic gates, state, artifact registry, pinned best, and final selection.",
        "",
        "## By Worker Role",
        "",
        "| Worker | Role | KNEW | Standalone KNEW failures | Internal failures before correction |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    for role in analysis["by_role"].values():
        lines.append(
            f"| {role['worker_index']} | `{role['role_name']}` | {role['local_knew_passes']}/{role['worker_count']} | {role['local_knew_failures']} | {role['internal_failures_before_holo_correction']} |"
        )
    lines.extend(
        [
            "",
            "## By Packet",
            "",
            "| Packet | Kind | Worker KNEW | Standalone KNEW failures | Internal failures before correction | Labels |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in analysis["by_packet"].values():
        labels = ", ".join(
            f"W{item['worker_index']}={item['label']}/gate={'PASS' if item['gate_passed'] else 'FAIL'}"
            for item in row["worker_labels"]
        )
        lines.append(
            f"| `{row['packet_id']}` | `{row['packet_kind']}` | {row['standalone_worker_knew_passes']}/3 | {row['standalone_worker_knew_failures']} | {row['internal_failures_before_holo_correction']} | {labels} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            analysis["interpretation"],
        ]
    )
    (OUT_ROOT / "INSIDE_HOLO_WORKER_SOLO_AUTOPSY.md").write_text("\n".join(lines) + "\n")


def locked_files() -> list[dict[str, Any]]:
    files = []
    for path in sorted(item for item in OUT_ROOT.rglob("*") if item.is_file()):
        if path.name in EXCLUDED_LOCK_FILES:
            continue
        files.append(
            {
                "relative_path": str(path.relative_to(OUT_ROOT)),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    return files


def build_lock(analysis: dict[str, Any]) -> dict[str, Any]:
    manifest_no_root = {
        "classification": "INSIDE_HOLO_WORKER_SOLO_AUTOPSY_LOCK",
        "status": "FROZEN_HASH_LOCKED",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "freeze_root_signature": analysis["freeze_root_signature"],
        "provider_calls_made_now": 0,
        "packet_count": analysis["packet_count"],
        "worker_turn_count": analysis["worker_turn_count"],
        "overall": analysis["overall"],
        "locked_files": locked_files(),
    }
    root_signature = sha256_bytes(canonical_json(manifest_no_root).encode("utf-8"))
    manifest = {**manifest_no_root, "root_signature": root_signature}
    (OUT_ROOT / "LOCK_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def validate_lock() -> dict[str, Any]:
    manifest = json.loads((OUT_ROOT / "LOCK_MANIFEST.json").read_text())
    for item in manifest["locked_files"]:
        path = OUT_ROOT / item["relative_path"]
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"hash mismatch: {item['relative_path']}")
    copy = dict(manifest)
    root = copy.pop("root_signature")
    recomputed = sha256_bytes(canonical_json(copy).encode("utf-8"))
    if recomputed != root:
        raise RuntimeError(f"root mismatch: {recomputed} != {root}")
    validation = {
        "validation_status": "PASS",
        "root_signature": root,
        "locked_file_count": len(manifest["locked_files"]),
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_ROOT / "LOCK_VALIDATION.json").write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    return validation


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if not args.validate_only:
        analysis = build_analysis()
        manifest = build_lock(analysis)
        print(json.dumps({"build": "ok", "root_signature": manifest["root_signature"], "out_root": str(OUT_ROOT)}, indent=2, sort_keys=True))
    validation = validate_lock()
    print(json.dumps(validation, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
