#!/usr/bin/env python3
"""Full HoloVerify architecture replay for Kit C pair 047.

This wrapper reuses the full architecture engine proven on 082, but swaps in
the 047 license-exception repeated-class pair. It keeps the same enforcement
path: worker turns, state brief, Gov sandwich, real Gov calls, gates, artifact
registry, best artifact, monotonic preservation, final selector, and trace
accounting.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
BENCHMARK_ROOT = ROOT.parent
ENGINE_PATH = BENCHMARK_ROOT / "full_holoverify_arch_kitc_082_2026-06-28" / "run_full_holoverify_arch_082.py"
SOURCE_RUN = BENCHMARK_ROOT / "kit_c_hardened_candidate_screen_v2_2026-06-28" / "run_20260628T222734Z"

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
engine.SOURCE_TRACE = SOURCE_RUN / "CONTROL_SCREEN_TRACE.jsonl"
engine.FULL_ARCH_RUN_NAME = "FULL_HOLOVERIFY_ARCH_KITC_047_2026_06_28"
engine.FULL_ARCH_CLASSIFICATION_COMPLETE = "FULL_HOLOVERIFY_ARCH_047_COMPLETE"
engine.FULL_ARCH_CLASSIFICATION_INVALID = "INVALID_OR_INCOMPLETE_FULL_HOLOVERIFY_ARCH_047"
engine.FULL_ARCH_TITLE = "Full HoloVerify Architecture 047 Replay"
engine.RUNNER_EXTRA_PREIMAGE = {
    "wrapper_source_hash": engine._sha256_text(Path(__file__).read_text()) if hasattr(engine, "_sha256_text") else "set_after_pair_config",
    "wrapper_pair": "HV-KITC-047",
}

engine.PAIR = {
    "pair_id": "HV-KITC-047",
    "schema_key": "license_exception_binding",
    "atlas": "\n".join(
        [
            "Repeated exposed failure classes:",
            "- FP_EXCEPTION_PATH_FREEZE",
            "- SCOPE_READING",
            "- ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW",
            "",
            "Known mechanism:",
            "A general warning demands exact exception evidence, while the current source gives exact matching exception evidence.",
            "Do not let a generic warning override exact current exception evidence.",
            "",
            "License exception binding:",
            "If the exception record covers the controlled item, destination, consignee role, and shipment date, the item-control/status requirement is operationally closed.",
            "Use ESCALATE only when the exception record has a concrete mismatch, such as a different consignee role.",
        ]
    ),
    "packets": [
        {
            "packet_id": "HV-KITC-047-A",
            "payload": SOURCE_RUN / "generated_packets" / "HV-KITC-047-A.payload.json",
            "source_gate_verdict": "ALLOW",
            "source_gate_binding": "EXACT_EXCEPTION_CLOSED",
            "required_terms": ["EXC-SOR-047", "SHIP-SOR-047", "C-17", "Canada", "service depot", "2026-06-23"],
        },
        {
            "packet_id": "HV-KITC-047-B",
            "payload": SOURCE_RUN / "generated_packets" / "HV-KITC-047-B.payload.json",
            "source_gate_verdict": "ESCALATE",
            "source_gate_binding": "CONSIGNEE_ROLE_MISMATCH",
            "required_terms": ["EXC-SOR-047", "SHIP-SOR-047", "service depot", "internal repair center", "consignee role"],
        },
    ],
}


def _worker_schema() -> dict[str, Any]:
    return {
        "worker_role": "SOURCE_BOUNDARY_MAPPER | ADVERSARIAL_SCOPE_CHALLENGER | FINAL_COMPILER",
        "verification_verdict": "ALLOW | ESCALATE",
        "license_exception_binding": {
            "shipment_id": "string",
            "exception_id": "string",
            "general_warning_id": "string",
            "item_control_status": "string",
            "destination": "string",
            "shipment_consignee_role": "string",
            "exception_consignee_role": "string",
            "shipment_date": "string",
            "binding_class": "EXACT_EXCEPTION_CLOSED | CONSIGNEE_ROLE_MISMATCH | UNRESOLVED",
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
        "must_preserve": ["source IDs", "item/destination/consignee/date binding"],
        "must_repair": ["map generic warning to exact exception evidence rather than treating warning as final blocker"],
        "blocked_moves": ["do not invent a second exception document requirement when EXC-SOR-047 closes the boundary"],
        "dependency_ledger": ["exception source binding unresolved until worker maps EXC-SOR-047"],
        "next_worker_baton": {
            "objective": "Create initial source-bound map.",
            "attack_focus": "general-warning fixation and source-scope literalism",
            "required_repairs": ["cite shipment, exception, warning, and policy separately"],
            "monotonic_preservation": [],
        },
        "final_compiler_allowed": False,
    }


def _validate_worker(packet: dict[str, Any], obj: dict[str, Any], valid_ids: set[str]) -> dict[str, Any]:
    failures: list[str] = []
    verdict = obj.get("verification_verdict")
    binding = obj.get("license_exception_binding") if isinstance(obj.get("license_exception_binding"), dict) else {}
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("verdict_invalid")
    if verdict != packet["source_gate_verdict"]:
        failures.append(f"source_gate_verdict_expected_{packet['source_gate_verdict']}")
    if binding.get("binding_class") != packet["source_gate_binding"]:
        failures.append(f"source_gate_binding_expected_{packet['source_gate_binding']}")
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
    binding = parsed.get("license_exception_binding") or {}
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
    # Reuse the engine implementation after swapping the pair-specific hooks.
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


engine._worker_schema = _worker_schema
engine._initial_baton = _initial_baton
engine._validate_worker = _validate_worker
engine._artifact_record = _artifact_record
engine._run_packet = _run_packet


if __name__ == "__main__":
    raise SystemExit(engine.main())
