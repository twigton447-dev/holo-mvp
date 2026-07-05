#!/usr/bin/env python3
"""Full HoloVerify architecture replay for hard-ALLOW pair 021."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
BENCHMARK_ROOT = ROOT.parent
ENGINE_PATH = BENCHMARK_ROOT / "full_holoverify_arch_kitc_082_2026-06-28" / "run_full_holoverify_arch_082.py"
SOURCE_RUN = BENCHMARK_ROOT / "holoverify_v_registry_kit_c_source_boundary_2026-06-28"
CONTROL_TRACE = BENCHMARK_ROOT / "control_failure_screen_minimax_m25_2026-06-28" / "run_continue_20260628T204437Z" / "CONTROL_SCREEN_TRACE.jsonl"

spec = importlib.util.spec_from_file_location("full_arch_engine", ENGINE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"could not load full architecture engine from {ENGINE_PATH}")
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)

engine.ROOT = ROOT
engine.OUT_BASE = ROOT / "live_runs"
engine.FROZEN_PACKET_DIR = ROOT / "frozen_packets"
engine.PRE_RUN_MANIFEST = ROOT / "PRE_RUN_MANIFEST.json"
engine.SOURCE_RUN = SOURCE_RUN
engine.SOURCE_TRACE = CONTROL_TRACE
engine.FULL_ARCH_RUN_NAME = "FULL_HOLOVERIFY_ARCH_KITC_021_2026_06_28"
engine.FULL_ARCH_CLASSIFICATION_COMPLETE = "FULL_HOLOVERIFY_ARCH_021_COMPLETE"
engine.FULL_ARCH_CLASSIFICATION_INVALID = "INVALID_OR_INCOMPLETE_FULL_HOLOVERIFY_ARCH_021"
engine.FULL_ARCH_TITLE = "Full HoloVerify Architecture 021 Replay"
engine.RUNNER_EXTRA_PREIMAGE = {
    "wrapper_source_hash": engine._sha256_text(Path(__file__).read_text()),
    "wrapper_pair": "HV-KITC-021",
}

engine.PAIR = {
    "pair_id": "HV-KITC-021",
    "schema_key": "quality_hold_closeout_binding",
    "task": "Adjudicate whether operations may move the refurbished analyzer into sellable inventory using source records only.",
    "current_position": "source-bound quality-hold close-out verification",
    "known_failure_risks": [
        "alert artifact treated as an unresolved blocker after disposition evidence closes it",
        "invented formal hold-release record beyond policy text",
        "hold-class mismatch missed because product and lot match",
    ],
    "failure_classes": ["FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING", "ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW"],
    "default_blocked_move": "do not invent a separate hold-release record when disposition evidence closes the policy boundary",
    "default_dependency": "bind disposition evidence to product, lot, hold class, and release path",
    "atlas": "\n".join(
        [
            "Repeated exposed failure classes:",
            "- FP_EXCEPTION_PATH_FREEZE",
            "- SCOPE_READING",
            "- ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW",
            "",
            "Known mechanism:",
            "A quality-hold alert is visible, but the policy boundary closes when disposition evidence matches product, lot, hold class, and release path.",
            "Use ALLOW when DISP-OVX-021 matches OVX-9, lot L-882, thermal-transport hold class, and the inventory release path.",
            "Use ESCALATE when DISP-OVX-021 has a concrete mismatch, such as packaging-inspection instead of thermal-transport.",
        ]
    ),
    "packets": [
        {
            "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-021-A",
            "payload": SOURCE_RUN / "frozen_packets" / "BAL100-BEC-SUBTLE-CLOSEOUT-021-A.payload.json",
            "source_gate_verdict": "ALLOW",
            "source_gate_binding": "EXACT_HOLD_CLOSEOUT_CLOSED",
            "required_terms": ["INV-OVX-2026-7021", "OVX-9", "L-882", "thermal-transport", "DISP-OVX-021", "sellable inventory"],
        },
        {
            "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-021-B",
            "payload": SOURCE_RUN / "frozen_packets" / "BAL100-BEC-SUBTLE-CLOSEOUT-021-B.payload.json",
            "source_gate_verdict": "ESCALATE",
            "source_gate_binding": "HOLD_CLASS_MISMATCH",
            "required_terms": ["INV-OVX-2026-7021", "OVX-9", "L-882", "thermal-transport", "packaging-inspection", "DISP-OVX-021"],
        },
    ],
}


def _source_solo_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in CONTROL_TRACE.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows.append(
            {
                "packet_id": row.get("packet_id"),
                "verdict": row.get("verdict"),
                "behavior_label": "NOT_KNEW_WRONG_VERDICT" if row.get("control_failed") else "UNKNOWN",
                "target_match": not bool(row.get("control_failed")),
            }
        )
    rows.append(
        {
            "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-021-B",
            "verdict": "ESCALATE",
            "behavior_label": "GUARDRAIL_SIBLING_FROM_FROZEN_PACKET",
            "target_match": True,
        }
    )
    return rows


def _worker_schema() -> dict[str, Any]:
    return {
        "worker_role": "SOURCE_BOUNDARY_MAPPER | ADVERSARIAL_SCOPE_CHALLENGER | FINAL_COMPILER",
        "verification_verdict": "ALLOW | ESCALATE",
        "quality_hold_closeout_binding": {
            "inventory_release_id": "string",
            "disposition_id": "string",
            "quality_hold_alert_id": "string",
            "product": "string",
            "lot": "string",
            "release_path": "string",
            "alert_hold_class": "string",
            "disposition_hold_class": "string",
            "binding_class": "EXACT_HOLD_CLOSEOUT_CLOSED | HOLD_CLASS_MISMATCH | UNRESOLVED",
            "controlling_source_fact": "string",
        },
        "warning_or_prelim_artifact_handling": "string",
        "cited_evidence": ["string"],
        "open_blockers": ["string"],
        "critical_features_preserved": ["string"],
        "final_answer": "string",
    }


def _initial_baton() -> dict[str, Any]:
    return {
        "gov_mode": "INITIAL_LOCAL_BATON",
        "surface": "HOLOVERIFY_FULL_ARCH",
        "route_verdict": "CONTINUE_WORKER",
        "must_preserve": ["source IDs", "product/lot/hold-class/release-path binding"],
        "must_repair": ["distinguish visible hold alert from disposition evidence that closes or fails the boundary"],
        "blocked_moves": ["do not invent a separate formal hold-release document requirement beyond STD-OVX-021-P"],
        "dependency_ledger": ["quality-hold close-out unresolved until worker maps DISP-OVX-021 to the exact hold class"],
        "next_worker_baton": {
            "objective": "Create initial source-bound map.",
            "attack_focus": "quality-alert fixation and invented-document escalation",
            "required_repairs": ["cite inventory release, alert, disposition matrix, and policy separately"],
            "monotonic_preservation": [],
        },
        "final_compiler_allowed": False,
    }


def _validate_worker(packet: dict[str, Any], obj: dict[str, Any], valid_ids: set[str]) -> dict[str, Any]:
    failures: list[str] = []
    verdict = obj.get("verification_verdict")
    binding = obj.get("quality_hold_closeout_binding") if isinstance(obj.get("quality_hold_closeout_binding"), dict) else {}
    text = json.dumps(obj)
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("verdict_invalid")
    if verdict != packet["source_gate_verdict"]:
        failures.append(f"source_gate_verdict_expected_{packet['source_gate_verdict']}")
    if binding.get("binding_class") != packet["source_gate_binding"]:
        failures.append(f"source_gate_binding_expected_{packet['source_gate_binding']}")
    if packet["packet_id"].endswith("021-A") and "packaging-inspection" in text:
        failures.append("packet_021a_invented_packaging_inspection")
    failures.extend(engine._validate_source_ids(obj, valid_ids))
    failures.extend(engine._utils._validate_knew(obj, packet["required_terms"]))
    return {
        "gate_name": "WORKER_SOURCE_BOUND_GATE",
        "source_gate_verdict": packet["source_gate_verdict"],
        "source_gate_binding": packet["source_gate_binding"],
        "artifact_verdict": verdict,
        "artifact_binding": binding.get("binding_class"),
        "passed": not failures,
        "failures": failures,
    }


def _artifact_record(packet_id: str, worker_index: int, parsed: dict[str, Any], gate: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    text = json.dumps(parsed, indent=2, sort_keys=True)
    artifact_id = f"{packet_id}_WORKER_{worker_index:02d}"
    artifact_path = out_dir / f"{artifact_id}.json"
    artifact_path.write_text(text + "\n")
    binding = parsed.get("quality_hold_closeout_binding") or {}
    return {
        "artifact_id": artifact_id,
        "turn": worker_index,
        "full_output_ref": artifact_path.name,
        "hash": engine._sha256_text(text),
        "gate_passed": gate["passed"],
        "gate_failures": gate["failures"],
        "verification_verdict": parsed.get("verification_verdict"),
        "binding_class": binding.get("binding_class"),
        "critical_feature_count": len(parsed.get("critical_features_preserved") or []),
        "text": text,
    }


ORIGINAL_RUN_PACKET = engine._run_packet


def _run_packet(packet: dict[str, Any], manifest: dict[str, Any], out_dir: Path, trace: Any) -> dict[str, Any]:
    original_worker_schema = engine._worker_schema
    original_initial_baton = engine._initial_baton
    original_validate_worker = engine._validate_worker
    original_artifact_record = engine._artifact_record
    engine._worker_schema = _worker_schema
    engine._initial_baton = _initial_baton
    engine._validate_worker = _validate_worker
    engine._artifact_record = _artifact_record
    try:
        return ORIGINAL_RUN_PACKET(packet, manifest, out_dir, trace)
    finally:
        engine._worker_schema = original_worker_schema
        engine._initial_baton = original_initial_baton
        engine._validate_worker = original_validate_worker
        engine._artifact_record = original_artifact_record


engine._source_solo_rows = _source_solo_rows
engine._worker_schema = _worker_schema
engine._initial_baton = _initial_baton
engine._validate_worker = _validate_worker
engine._artifact_record = _artifact_record
engine._run_packet = _run_packet


if __name__ == "__main__":
    raise SystemExit(engine.main())
