#!/usr/bin/env python3
"""Full HoloVerify architecture replay for hard-ALLOW pair 022."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
BENCHMARK_ROOT = ROOT.parent
ENGINE_PATH = BENCHMARK_ROOT / "full_holoverify_arch_kitc_082_2026-06-28" / "run_full_holoverify_arch_082.py"
SOURCE_RUN = BENCHMARK_ROOT / "holoverify_v_registry_kit_c_source_boundary_2026-06-28"
CONTROL_TRACE = BENCHMARK_ROOT / "control_failure_screen_minimax_m25_2026-06-28" / "run_continue_20260628T211143Z" / "CONTROL_SCREEN_TRACE.jsonl"

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
engine.FULL_ARCH_RUN_NAME = "FULL_HOLOVERIFY_ARCH_KITC_022_2026_06_28"
engine.FULL_ARCH_CLASSIFICATION_COMPLETE = "FULL_HOLOVERIFY_ARCH_022_COMPLETE"
engine.FULL_ARCH_CLASSIFICATION_INVALID = "INVALID_OR_INCOMPLETE_FULL_HOLOVERIFY_ARCH_022"
engine.FULL_ARCH_TITLE = "Full HoloVerify Architecture 022 Replay"
engine.RUNNER_EXTRA_PREIMAGE = {
    "wrapper_source_hash": engine._sha256_text(Path(__file__).read_text()),
    "wrapper_pair": "HV-KITC-022",
}

engine.PAIR = {
    "pair_id": "HV-KITC-022",
    "schema_key": "activation_dependency_binding",
    "task": "Adjudicate whether platform operations may activate telemetry service using source records only.",
    "current_position": "source-bound activation dependency verification",
    "known_failure_risks": [
        "shared prefix warning treated as contradiction even when current calibration record is exact",
        "lab-vs-production distinction missed because DG-41B prefix matches",
        "dependency attachment treated as enough without site and release-condition match",
    ],
    "failure_classes": ["FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING", "ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW"],
    "default_blocked_move": "do not escalate from a shared-prefix note when CAL-ACR-022 exactly covers production Site 18-P",
    "default_dependency": "bind calibration packet to device group, site, release condition, and timing",
    "atlas": "\n".join(
        [
            "Repeated exposed failure classes:",
            "- FP_EXCEPTION_PATH_FREEZE",
            "- SCOPE_READING",
            "- ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW",
            "",
            "Known mechanism:",
            "A warning says lab and production devices share a naming prefix, but the policy boundary is exact device group, site, release condition, and timing.",
            "Use ALLOW when CAL-ACR-022 matches DG-41B production telemetry units at Site 18-P for RC-7 before ACT-ACR-2026-8022.",
            "Use ESCALATE when calibration covers lab units at Site 18-L while activation is for production units at Site 18-P.",
        ]
    ),
    "packets": [
        {
            "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-022-A",
            "payload": SOURCE_RUN / "frozen_packets" / "BAL100-BEC-SUBTLE-CLOSEOUT-022-A.payload.json",
            "source_gate_verdict": "ALLOW",
            "source_gate_binding": "EXACT_ACTIVATION_DEPENDENCY_CLOSED",
            "required_terms": ["ACT-ACR-2026-8022", "ACT-ACR-022", "CAL-ACR-022", "DG-41B", "Site 18-P", "production", "RC-7"],
        },
        {
            "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-022-B",
            "payload": SOURCE_RUN / "frozen_packets" / "BAL100-BEC-SUBTLE-CLOSEOUT-022-B.payload.json",
            "source_gate_verdict": "ESCALATE",
            "source_gate_binding": "SITE_AND_USE_CLASS_MISMATCH",
            "required_terms": ["ACT-ACR-2026-8022", "CAL-ACR-022", "18-P", "18-L", "production", "lab", "RC-7"],
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
            "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-022-B",
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
        "activation_dependency_binding": {
            "activation_id": "string",
            "calibration_id": "string",
            "dependency_alert_id": "string",
            "activation_device_group": "string",
            "calibration_device_group": "string",
            "activation_site": "string",
            "calibration_site": "string",
            "release_condition": "string",
            "timing_match": "string",
            "binding_class": "EXACT_ACTIVATION_DEPENDENCY_CLOSED | SITE_AND_USE_CLASS_MISMATCH | UNRESOLVED",
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
        "must_preserve": ["source IDs", "device-group/site/release-condition/timing binding"],
        "must_repair": ["distinguish shared-prefix warning from exact calibration source match"],
        "blocked_moves": ["do not turn NOTE-ACR-022 into a blocker when CAL-ACR-022 exactly covers production Site 18-P"],
        "dependency_ledger": ["activation dependency unresolved until worker maps CAL-ACR-022 to activation scope"],
        "next_worker_baton": {
            "objective": "Create initial source-bound map.",
            "attack_focus": "shared-prefix warning fixation and lab/production mismatch detection",
            "required_repairs": ["cite activation request, calibration packet, release condition, site roster, and policy separately"],
            "monotonic_preservation": [],
        },
        "final_compiler_allowed": False,
    }


def _validate_worker(packet: dict[str, Any], obj: dict[str, Any], valid_ids: set[str]) -> dict[str, Any]:
    failures: list[str] = []
    verdict = obj.get("verification_verdict")
    binding = obj.get("activation_dependency_binding") if isinstance(obj.get("activation_dependency_binding"), dict) else {}
    text = json.dumps(obj)
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("verdict_invalid")
    if verdict != packet["source_gate_verdict"]:
        failures.append(f"source_gate_verdict_expected_{packet['source_gate_verdict']}")
    if binding.get("binding_class") != packet["source_gate_binding"]:
        failures.append(f"source_gate_binding_expected_{packet['source_gate_binding']}")
    if packet["packet_id"].endswith("022-A"):
        binding_text = json.dumps(
            {
                "activation_site": binding.get("activation_site"),
                "calibration_site": binding.get("calibration_site"),
                "controlling_source_fact": binding.get("controlling_source_fact"),
                "cited_evidence": obj.get("cited_evidence"),
                "open_blockers": obj.get("open_blockers"),
            }
        )
        if "18-L" in binding_text:
            failures.append("packet_022a_site_18l_contaminated_binding_or_citation")
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
    binding = parsed.get("activation_dependency_binding") or {}
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
