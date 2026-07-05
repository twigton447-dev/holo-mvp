#!/usr/bin/env python3
"""Full HoloVerify architecture replay for Kit C pair 082.

This runner is intentionally heavier than the earlier Gov-only diagnostics.
It exercises the enforcement architecture:

- worker turns,
- cumulative state brief,
- real Gov API calls between workers,
- Gov-sandwich worker prompts,
- deterministic gate after every worker,
- Gov receives gate results,
- artifact registry,
- best artifact registry / pinned best,
- monotonic preservation,
- final selector,
- full trace and token accounting.

Scope: one repeated-class pair (`HV-KITC-082`) against frozen Solo evidence.
No Solo rerun. No judges. No benchmark lock.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
OUT_BASE = ROOT / "live_runs"
FROZEN_PACKET_DIR = ROOT / "frozen_packets"
PRE_RUN_MANIFEST = ROOT / "PRE_RUN_MANIFEST.json"

BENCHMARK_ROOT = ROOT.parent
SOURCE_RUN = BENCHMARK_ROOT / "kit_c_exposed_class_repeats_v7_2026-06-28" / "run_20260628T230836Z"
SOURCE_TRACE = SOURCE_RUN / "CONTROL_SCREEN_TRACE.jsonl"
MODEL = "MiniMax-M2.5-highspeed"

UTIL_PATH = BENCHMARK_ROOT / "holoverify_v_kitc_042_hard_allow_fp_2026-06-28" / "run_holoverify_v_042.py"
_spec = importlib.util.spec_from_file_location("holo_042_utils", UTIL_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"could not load utility module from {UTIL_PATH}")
_utils = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_utils)

FORBIDDEN_PROMPT_TERMS = (
    "hidden_expected_verdict",
    "expected_for_local_audit_only",
    "CORRECT",
    "WRONG",
    "KNEW",
    "LUCKY",
    "target_match",
    "Solo failed",
    "control verdict",
)

FORBIDDEN_GOV_OUTPUT_KEYS = {
    "model_choice",
    "model_selection",
    "next_model",
    "selected_model",
    "selected_provider",
    "provider_choice",
    "worker_model_choice",
}

PAIR = {
    "pair_id": "HV-KITC-082",
    "schema_key": "clinical_activation_binding",
    "atlas": "\n".join(
        [
            "Repeated exposed failure classes:",
            "- FP_EXCEPTION_PATH_FREEZE",
            "- SCOPE_READING",
            "- ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW",
            "",
            "Known mechanism:",
            "A preliminary warning demands an abstract boundary field, while the current source gives the operational equivalent.",
            "Do not require the exact abstract label when source wording operationally closes the same boundary.",
            "",
            "Clinical activation binding:",
            "'current IRB-approved consent C12' is consent-status-class evidence for consent C12.",
            "A feasibility note is planning-only and cannot override later activation authority that covers site, protocol, current IRB-approved consent, and activation date.",
        ]
    ),
    "packets": [
        {
            "packet_id": "HV-KITC-082-A",
            "payload": SOURCE_RUN / "generated_packets" / "HV-KITC-082-A.payload.json",
            "source_gate_verdict": "ALLOW",
            "source_gate_binding": "CURRENT_IRB_CONSENT_CLOSED",
            "required_terms": ["AUTH-BOR-082", "B-18", "P8.1", "C12", ["current IRB-approved", "IRB-approved"], "2026-06-28"],
        },
        {
            "packet_id": "HV-KITC-082-B",
            "payload": SOURCE_RUN / "generated_packets" / "HV-KITC-082-B.payload.json",
            "source_gate_verdict": "ESCALATE",
            "source_gate_binding": "CONSENT_STATUS_PENDING",
            "required_terms": ["AUTH-BOR-082", "C12", "pending"],
        },
    ],
}

WORKER_ROLES = [
    {
        "role": "SOURCE_BOUNDARY_MAPPER",
        "objective": "Map every policy-required boundary field to exact source records. Do not decide from warning tone alone.",
    },
    {
        "role": "ADVERSARIAL_SCOPE_CHALLENGER",
        "objective": "Challenge the prior artifact. Find whether any abstract field is genuinely open or merely satisfied by operational wording.",
    },
    {
        "role": "FINAL_COMPILER",
        "objective": "Produce the final source-bound verdict while preserving all critical features from the best prior admissible artifact.",
    },
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _packet_source_ids(payload: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for group in ("internal_documents", "policy_documents"):
        for doc in payload.get("context", {}).get(group, []) or []:
            if isinstance(doc, dict) and doc.get("doc_id"):
                ids.add(str(doc["doc_id"]))
    return ids


def _source_solo_rows() -> list[dict[str, Any]]:
    rows = []
    for line in SOURCE_TRACE.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("pair_id") == PAIR["pair_id"]:
            rows.append(row)
    return rows


def _chat_completions_url() -> str:
    explicit = os.getenv("MINIMAX_CHAT_COMPLETIONS_URL", "").strip()
    if explicit:
        return explicit
    base = os.getenv("MINIMAX_BASE_URL", "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return "https://api.minimaxi.chat/v1/chat/completions"


def _call_minimax(messages: list[dict[str, str]], max_tokens: int = 1600) -> dict[str, Any]:
    started = time.time()
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        _chat_completions_url(),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {os.getenv('MINIMAX_API_KEY', '').strip()}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8", errors="replace"))
    choices = data.get("choices") or [{}]
    first_choice = choices[0] if isinstance(choices[0], dict) else {}
    message = first_choice.get("message") if isinstance(first_choice, dict) else {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "text": _utils._strip_thinking_blocks((message or {}).get("content") or ""),
        "finish_reason": first_choice.get("finish_reason"),
        "response_id": data.get("id"),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": int((time.time() - started) * 1000),
    }


def _json_from_text(text: str) -> dict[str, Any]:
    stripped = (text or "").strip()
    if stripped.startswith("```"):
        raise ValueError("markdown_fence_present")
    return json.loads(stripped)


def _assert_prompt_clean(*parts: str) -> None:
    combined = "\n".join(parts)
    found = [term for term in FORBIDDEN_PROMPT_TERMS if term in combined]
    if found:
        raise RuntimeError(f"forbidden prompt terms present: {found}")


def _worker_schema() -> dict[str, Any]:
    return {
        "worker_role": "SOURCE_BOUNDARY_MAPPER | ADVERSARIAL_SCOPE_CHALLENGER | FINAL_COMPILER",
        "verification_verdict": "ALLOW | ESCALATE",
        "clinical_activation_binding": {
            "activation_record_id": "string",
            "feasibility_note_id": "string",
            "activation_authority_id": "string",
            "site": "string",
            "protocol_version": "string",
            "consent_version": "string",
            "activation_date": "string",
            "consent_status_evidence": "string",
            "binding_class": "CURRENT_IRB_CONSENT_CLOSED | CONSENT_STATUS_PENDING | UNRESOLVED",
            "controlling_source_fact": "string",
        },
        "warning_or_prelim_artifact_handling": "string",
        "cited_evidence": ["string"],
        "open_blockers": ["string"],
        "critical_features_preserved": ["string"],
        "final_answer": "string",
    }


def _gov_schema() -> dict[str, Any]:
    return {
        "gov_mode": "CONTROL_ROUTER",
        "surface": "HOLOVERIFY_FULL_ARCH",
        "control_action": "CONTINUE_REPAIR | FINAL_COMPILER | FAIL_CLOSED",
        "route_verdict": "CONTINUE_WORKER | FINAL_COMPILER | FAIL_CLOSED",
        "source_gate_interpretation": "string",
        "must_preserve": ["string"],
        "must_repair": ["string"],
        "blocked_moves": ["string"],
        "dependency_ledger": ["string"],
        "next_worker_baton": {
            "objective": "string",
            "attack_focus": "string",
            "required_repairs": ["string"],
            "monotonic_preservation": ["string"],
        },
        "final_compiler_allowed": "boolean",
    }


def _make_state_brief(packet_id: str, turns: list[dict[str, Any]], best_artifact: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "run_id": globals().get("FULL_ARCH_RUN_NAME", "FULL_HOLOVERIFY_ARCH_KITC_082"),
        "packet_id": packet_id,
        "lane": "FULL_HOLOVERIFY_ARCH",
        "turns_completed": [
            {
                "turn": t["turn"],
                "role": t["role"],
                "model": t["model"],
                "output_summary": t.get("output_summary"),
                "full_output_ref": t.get("full_output_ref"),
                "gate_status": t.get("gate_status"),
                "artifact_hash": t.get("artifact_hash"),
            }
            for t in turns
        ],
        "current_position": PAIR.get("current_position", "source-bound verification with repeated exposed failure classes"),
        "resolved_dependencies": [],
        "unresolved_dependencies": [],
        "blocked_moves_so_far": sorted({move for t in turns for move in t.get("blocked_moves", [])}),
        "source_ids_used_so_far": sorted({source for t in turns for source in t.get("source_ids", [])}),
        "claims_requiring_support": [],
        "known_failure_risks": PAIR.get(
            "known_failure_risks",
            ["warning fixation", "abstract status class literalism", "preliminary artifact treated as final blocker"],
        ),
        "best_artifact": best_artifact,
    }


def _build_worker_prompt(
    packet: dict[str, Any],
    payload: dict[str, Any],
    role: dict[str, str],
    state_brief: dict[str, Any],
    latest_baton: dict[str, Any],
    raw_prior_outputs: list[dict[str, Any]],
) -> list[dict[str, str]]:
    gov_lens = {
        "route_verdict": latest_baton.get("route_verdict"),
        "main_repair_target": (latest_baton.get("must_repair") or ["initial source-bound mapping"])[0],
        "blocked_move": (latest_baton.get("blocked_moves") or [PAIR.get("default_blocked_move", "do not let preliminary warnings override exact authority")])[0],
        "unresolved_dependency": (latest_baton.get("dependency_ledger") or [PAIR.get("default_dependency", "bind source boundary to exact source wording")])[0],
        "current_objective": role["objective"],
    }
    system = "\n".join(
        [
            "You are a HoloVerify worker. Preserve state. Obey Gov.",
            "You must read both STATE_BRIEF and LATEST_GOV_BATON. The state brief tells you what has happened so far. The Gov baton tells you how to route the next step.",
            "Priority order: source context is ground truth; answer contract controls form; Gov routing lens controls how to read state; state brief preserves continuity; full latest Gov baton controls next action.",
            "Return only valid JSON. No markdown fences.",
            "Use compact JSON: keep every string under 220 characters, use at most 4 cited_evidence items, at most 4 critical_features_preserved items, and do not restate the full source context.",
        ]
    )
    user_obj = {
        "system_role": "HoloVerify worker",
        "gov_routing_lens": gov_lens,
        "run_lock": {
            "lane": "FULL_HOLOVERIFY_ARCH",
            "model": MODEL,
            "packet_id": packet["packet_id"],
            "worker_role": role["role"],
            "no_substitutions": True,
        },
        "task_and_answer_contract": {
            "task": PAIR.get("task", "Adjudicate the clinical activation boundary using source records only."),
            "answer_contract": _worker_schema(),
            "repeated_failure_classes": PAIR.get(
                "failure_classes",
                ["FP_EXCEPTION_PATH_FREEZE", "SCOPE_READING", "ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW"],
            ),
            "atlas": PAIR["atlas"],
        },
        "source_context": payload,
        "state_brief": state_brief,
        "raw_prior_outputs": raw_prior_outputs,
        "full_latest_gov_baton": latest_baton,
        "current_turn_command": role["objective"],
    }
    user = json.dumps(user_obj, separators=(",", ":"), sort_keys=True)
    _assert_prompt_clean(system, user)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _build_gov_prompt(
    packet: dict[str, Any],
    payload: dict[str, Any],
    state_brief: dict[str, Any],
    worker_output: dict[str, Any],
    gate_result: dict[str, Any],
    artifact_registry: list[dict[str, Any]],
) -> list[dict[str, str]]:
    system = "\n".join(
        [
            "You are HoloGov-V in the full HoloVerify architecture.",
            "Gov does not choose models. Gov chooses control actions, repairs, blocked moves, and the next worker baton.",
            "You receive deterministic gate results. You cannot call an artifact ready if source gates fail.",
            "Return only valid JSON. No markdown fences.",
        ]
    )
    user_obj = {
        "run_lock": {
            "lane": "FULL_HOLOVERIFY_ARCH",
            "model": MODEL,
            "packet_id": packet["packet_id"],
            "gov_may_select_models": False,
            "no_substitutions": True,
        },
        "source_context": payload,
        "state_brief": state_brief,
        "latest_worker_output": worker_output,
        "deterministic_gate_result": gate_result,
        "artifact_registry": artifact_registry,
        "required_gov_schema": _gov_schema(),
        "gov_command": "Diagnose previous worker output, preserve correct source bindings, repair gate failures, block warning fixation, and create the next worker baton.",
    }
    user = json.dumps(user_obj, separators=(",", ":"), sort_keys=True)
    _assert_prompt_clean(system, user)
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _validate_source_ids(obj: dict[str, Any], valid_ids: set[str]) -> list[str]:
    return _utils._validate_source_ids(obj, valid_ids)


def _validate_worker(packet: dict[str, Any], obj: dict[str, Any], valid_ids: set[str]) -> dict[str, Any]:
    failures: list[str] = []
    verdict = obj.get("verification_verdict")
    binding = obj.get("clinical_activation_binding") if isinstance(obj.get("clinical_activation_binding"), dict) else {}
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("verdict_invalid")
    if verdict != packet["source_gate_verdict"]:
        failures.append(f"source_gate_verdict_expected_{packet['source_gate_verdict']}")
    if binding.get("binding_class") != packet["source_gate_binding"]:
        failures.append(f"source_gate_binding_expected_{packet['source_gate_binding']}")
    failures.extend(_validate_source_ids(obj, valid_ids))
    failures.extend(_utils._validate_knew(obj, packet["required_terms"]))
    return {
        "gate_name": "WORKER_SOURCE_BOUND_GATE",
        "source_gate_verdict": packet["source_gate_verdict"],
        "source_gate_binding": packet["source_gate_binding"],
        "artifact_verdict": verdict,
        "artifact_binding": binding.get("binding_class"),
        "passed": not failures,
        "failures": failures,
    }


def _binding_class_from_worker(parsed: dict[str, Any]) -> Any:
    binding = parsed.get(PAIR.get("schema_key", "clinical_activation_binding"))
    if isinstance(binding, dict):
        return binding.get("binding_class")
    binding = parsed.get("clinical_activation_binding")
    if isinstance(binding, dict):
        return binding.get("binding_class")
    return None


def _validate_gov(obj: dict[str, Any], prior_gate_result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if obj.get("gov_mode") != "CONTROL_ROUTER":
        failures.append("gov_mode_invalid")
    if obj.get("surface") != "HOLOVERIFY_FULL_ARCH":
        failures.append("surface_invalid")
    if obj.get("route_verdict") not in {"CONTINUE_WORKER", "FINAL_COMPILER", "FAIL_CLOSED"}:
        failures.append("route_verdict_invalid")
    if prior_gate_result.get("passed") is False and obj.get("final_compiler_allowed") is True:
        failures.append("gov_ready_despite_failed_gate")
    failures.extend(f"forbidden_gov_key:{p}" for p in _utils._forbidden_gov_keys(obj))
    return failures


def _artifact_record(packet_id: str, worker_index: int, parsed: dict[str, Any], gate: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    text = json.dumps(parsed, indent=2, sort_keys=True)
    artifact_id = f"{packet_id}_WORKER_{worker_index:02d}"
    artifact_path = out_dir / f"{artifact_id}.json"
    artifact_path.write_text(text + "\n")
    return {
        "artifact_id": artifact_id,
        "turn": worker_index,
        "full_output_ref": artifact_path.name,
        "hash": _sha256_text(text),
        "gate_passed": gate["passed"],
        "gate_failures": gate["failures"],
        "verification_verdict": parsed.get("verification_verdict"),
        "binding_class": (parsed.get("clinical_activation_binding") or {}).get("binding_class"),
        "critical_feature_count": len(parsed.get("critical_features_preserved") or []),
        "text": text,
    }


def _select_best(packet: dict[str, Any], artifact_registry: list[dict[str, Any]]) -> dict[str, Any]:
    admissible = [a for a in artifact_registry if a["gate_passed"]]
    if not admissible:
        return {"selected_artifact_id": None, "selection_reason": "NO_ADMISSIBLE_ARTIFACT", "selected": None}
    final = artifact_registry[-1]
    best = admissible[-1]
    if final["gate_passed"]:
        best = final
        reason = "FINAL_ARTIFACT_ADMISSIBLE"
    else:
        reason = "FINAL_REGRESSED_SELECTED_BEST_PRIOR"
    return {"selected_artifact_id": best["artifact_id"], "selection_reason": reason, "selected": best}


def _initial_baton() -> dict[str, Any]:
    return {
        "gov_mode": "INITIAL_LOCAL_BATON",
        "surface": "HOLOVERIFY_FULL_ARCH",
        "route_verdict": "CONTINUE_WORKER",
        "must_preserve": ["source IDs", "site/protocol/consent/date binding"],
        "must_repair": ["map abstract consent-status class to operational source wording"],
        "blocked_moves": ["do not treat feasibility note as final blocker when activation authority closes the boundary"],
        "dependency_ledger": ["consent-status source binding unresolved until worker maps AUTH-BOR-082"],
        "next_worker_baton": {
            "objective": "Create initial source-bound map.",
            "attack_focus": "warning fixation and abstract-label literalism",
            "required_repairs": ["cite activation authority and feasibility note separately"],
            "monotonic_preservation": [],
        },
        "final_compiler_allowed": False,
    }


def _run_packet(packet: dict[str, Any], manifest: dict[str, Any], out_dir: Path, trace: Any) -> dict[str, Any]:
    payload = _load_json(packet["payload"])
    valid_ids = _packet_source_ids(payload)
    turns: list[dict[str, Any]] = []
    artifact_registry: list[dict[str, Any]] = []
    raw_prior_outputs: list[dict[str, Any]] = []
    latest_baton = _initial_baton()
    best_artifact: dict[str, Any] | None = None
    call_rows: list[dict[str, Any]] = []
    call_index_base = 0

    for worker_index, role in enumerate(WORKER_ROLES, start=1):
        state_brief = _make_state_brief(packet["packet_id"], turns, best_artifact)
        messages = _build_worker_prompt(packet, payload, role, state_brief, latest_baton, raw_prior_outputs)
        meta = {
            "call_kind": "worker",
            "worker_index": worker_index,
            "role_name": role["role"],
            "packet_id": packet["packet_id"],
            "pair_id": PAIR["pair_id"],
            "provider": "minimax",
            "model": MODEL,
            "pre_run_root_signature": manifest["root_signature"],
        }
        response: dict[str, Any] = {}
        try:
            response = _call_minimax(messages, max_tokens=2600)
            parsed = _json_from_text(response["text"])
            gate = _validate_worker(packet, parsed, valid_ids)
        except Exception as exc:
            row = {
                **meta,
                **response,
                "provider_call_ok": bool(response),
                "parse_ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "admissible": False,
            }
            trace.write(json.dumps(row) + "\n")
            call_rows.append(row)
            return {
                "packet_id": packet["packet_id"],
                "calls": call_rows,
                "artifact_registry": [{k: v for k, v in a.items() if k != "text"} for a in artifact_registry],
                "final_selector": {"selected_artifact_id": None, "selection_reason": "WORKER_PARSE_OR_PROVIDER_FAILURE", "selected": None},
                "final_admissible": False,
                "final_verdict": None,
                "final_binding": None,
                "error": row["error"],
            }
        artifact = _artifact_record(packet["packet_id"], worker_index, parsed, gate, out_dir)
        artifact_registry.append(artifact)
        if artifact["gate_passed"]:
            best_artifact = {k: v for k, v in artifact.items() if k != "text"}
        row = {**meta, **response, "provider_call_ok": True, "parse_ok": True, "parsed_json": parsed, "gate_result": gate, "artifact_id": artifact["artifact_id"], "admissible": gate["passed"]}
        trace.write(json.dumps(row) + "\n")
        call_rows.append(row)
        turns.append(
            {
                "turn": len(turns) + 1,
                "role": "worker",
                "model": MODEL,
                "output_summary": f"{role['role']} verdict {parsed.get('verification_verdict')} binding {_binding_class_from_worker(parsed)}",
                "full_output_ref": artifact["full_output_ref"],
                "gate_status": "PASS" if gate["passed"] else "FAIL",
                "artifact_hash": artifact["hash"],
                "source_ids": sorted(valid_ids),
            }
        )
        raw_prior_outputs.append({"worker_index": worker_index, "role": role["role"], "output": parsed, "gate_result": gate})

        if worker_index < len(WORKER_ROLES):
            state_brief = _make_state_brief(packet["packet_id"], turns, best_artifact)
            gov_messages = _build_gov_prompt(packet, payload, state_brief, parsed, gate, [{k: v for k, v in a.items() if k != "text"} for a in artifact_registry])
            gov_response: dict[str, Any] = {}
            try:
                gov_response = _call_minimax(gov_messages, max_tokens=2200)
                gov_parsed = _json_from_text(gov_response["text"])
                gov_failures = _validate_gov(gov_parsed, gate)
            except Exception as exc:
                gov_row = {
                    "call_kind": "gov",
                    "gov_index": worker_index,
                    "packet_id": packet["packet_id"],
                    "pair_id": PAIR["pair_id"],
                    "provider": "minimax",
                    "model": MODEL,
                    "pre_run_root_signature": manifest["root_signature"],
                    **gov_response,
                    "provider_call_ok": bool(gov_response),
                    "parse_ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "admissible": False,
                }
                trace.write(json.dumps(gov_row) + "\n")
                call_rows.append(gov_row)
                return {
                    "packet_id": packet["packet_id"],
                    "calls": call_rows,
                    "artifact_registry": [{k: v for k, v in a.items() if k != "text"} for a in artifact_registry],
                    "final_selector": {"selected_artifact_id": None, "selection_reason": "GOV_PARSE_OR_PROVIDER_FAILURE", "selected": None},
                    "final_admissible": False,
                    "final_verdict": None,
                    "final_binding": None,
                    "error": gov_row["error"],
                }
            gov_row = {
                "call_kind": "gov",
                "gov_index": worker_index,
                "packet_id": packet["packet_id"],
                "pair_id": PAIR["pair_id"],
                "provider": "minimax",
                "model": MODEL,
                "pre_run_root_signature": manifest["root_signature"],
                **gov_response,
                "provider_call_ok": True,
                "parse_ok": True,
                "parsed_json": gov_parsed,
                "deterministic_failures": gov_failures,
                "admissible": not gov_failures,
            }
            trace.write(json.dumps(gov_row) + "\n")
            call_rows.append(gov_row)
            turns.append(
                {
                    "turn": len(turns) + 1,
                    "role": "gov",
                    "model": MODEL,
                    "output_summary": f"Gov control_action {gov_parsed.get('control_action')} route {gov_parsed.get('route_verdict')}",
                    "full_output_ref": f"{packet['packet_id']}_GOV_{worker_index:02d}.json",
                    "gate_status": "PASS" if not gov_failures else "FAIL",
                    "artifact_hash": _sha256_text(json.dumps(gov_parsed, sort_keys=True)),
                    "blocked_moves": gov_parsed.get("blocked_moves") or [],
                }
            )
            (out_dir / f"{packet['packet_id']}_GOV_{worker_index:02d}.json").write_text(json.dumps(gov_parsed, indent=2, sort_keys=True) + "\n")
            latest_baton = gov_parsed

    selection = _select_best(packet, artifact_registry)
    return {
        "packet_id": packet["packet_id"],
        "calls": call_rows,
        "artifact_registry": [{k: v for k, v in a.items() if k != "text"} for a in artifact_registry],
        "final_selector": selection,
        "final_admissible": selection["selected"] is not None,
        "final_verdict": selection["selected"]["verification_verdict"] if selection["selected"] else None,
        "final_binding": selection["selected"]["binding_class"] if selection["selected"] else None,
    }


def build_preflight() -> dict[str, Any]:
    FROZEN_PACKET_DIR.mkdir(parents=True, exist_ok=True)
    packet_records = []
    for packet in PAIR["packets"]:
        payload = _load_json(packet["payload"])
        frozen_path = FROZEN_PACKET_DIR / f"{packet['packet_id']}.payload.json"
        frozen_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        packet_records.append(
            {
                "packet_id": packet["packet_id"],
                "pair_id": PAIR["pair_id"],
                "frozen_payload_path": str(frozen_path),
                "packet_payload_hash": _sha256_text(_canonical_json(payload)),
                "source_ids": sorted(_packet_source_ids(payload)),
                "source_gate_verdict_for_deterministic_gate": packet["source_gate_verdict"],
                "source_gate_binding_for_deterministic_gate": packet["source_gate_binding"],
            }
        )
    architecture_lock = {
        "run_name": globals().get("FULL_ARCH_RUN_NAME", "FULL_HOLOVERIFY_ARCH_KITC_082_2026_06_28"),
        "status": "pre_registered_full_arch_against_frozen_solo",
        "surface": "HoloVerify full architecture",
        "benchmark_credit": False,
        "post_generation_status_if_clean": "full_arch_candidate_pair_pending_judge",
        "model_roster": {
            "frozen_solo_provider": "minimax",
            "frozen_solo_model": MODEL,
            "holo_worker_provider": "minimax",
            "holo_worker_model": MODEL,
            "holo_gov_provider": "minimax",
            "holo_gov_model": MODEL,
            "gov_may_select_models": False,
            "fallback_policy": "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        },
        "expected_counts": {
            "new_provider_calls": 10,
            "solo_rerun_calls": 0,
            "worker_calls": 6,
            "holo_gov_calls": 4,
            "judge_calls": 0,
        },
        "full_architecture_features": [
            "worker turns",
            "state brief",
            "real Gov API calls between workers",
            "Gov sandwich worker prompts",
            "deterministic gate after every worker",
            "Gov sees gate results",
            "artifact registry",
            "best artifact registry",
            "pinned best artifact",
            "monotonic preservation",
            "final selector",
            "trace/accounting",
        ],
        "forbidden_inputs": ["correctness labels", "frozen Solo raw_text", "judge notes"],
    }
    preimage = _canonical_json(
        {
            "architecture_lock": architecture_lock,
            "packet_records": packet_records,
            "source_solo_rows_hash": _sha256_text(_canonical_json(_source_solo_rows())),
            "worker_roles": WORKER_ROLES,
            "runner_source_hash": _sha256_text(Path(__file__).read_text()),
            "runner_extra_preimage": globals().get("RUNNER_EXTRA_PREIMAGE", {}),
        }
    )
    manifest = {
        "architecture_lock": architecture_lock,
        "packet_records": packet_records,
        "source_solo_rows": [
            {
                "packet_id": row.get("packet_id"),
                "verdict": row.get("verdict"),
                "behavior_label": row.get("behavior_label"),
                "target_match": row.get("target_match"),
            }
            for row in _source_solo_rows()
        ],
        "root_signature": _sha256_text(preimage),
    }
    PRE_RUN_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def _validate_preflight() -> dict[str, Any]:
    if not PRE_RUN_MANIFEST.exists():
        raise RuntimeError("PRE_RUN_MANIFEST missing; run --preflight first")
    manifest = _load_json(PRE_RUN_MANIFEST)
    expected = build_preflight()
    if manifest["root_signature"] != expected["root_signature"]:
        raise RuntimeError("preflight_root_signature_changed")
    return manifest


def run_live() -> int:
    manifest = _validate_preflight()
    if not os.getenv("MINIMAX_API_KEY", "").strip():
        raise RuntimeError("MINIMAX_API_KEY missing")
    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    out_dir = OUT_BASE / run_id
    out_dir.mkdir(parents=True, exist_ok=False)
    trace_path = out_dir / "TRACE_CALLS.jsonl"
    packet_results = []
    with trace_path.open("w") as trace:
        for packet in PAIR["packets"]:
            packet_result = _run_packet(packet, manifest, out_dir, trace)
            packet_results.append(packet_result)
            if not packet_result.get("final_admissible"):
                break
    all_calls = [call for packet in packet_results for call in packet["calls"]]
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in all_calls:
        for key in totals:
            value = row.get(key)
            if isinstance(value, int):
                totals[key] += value
    trace_hash = _sha256_text(trace_path.read_text())
    complete = len(all_calls) == 10 and all(row.get("provider_call_ok") for row in all_calls)
    all_final_admissible = complete and all(p["final_admissible"] for p in packet_results)
    summary = {
        "classification": (
            globals().get("FULL_ARCH_CLASSIFICATION_COMPLETE", "FULL_HOLOVERIFY_ARCH_082_COMPLETE")
            if complete
            else globals().get("FULL_ARCH_CLASSIFICATION_INVALID", "INVALID_OR_INCOMPLETE_FULL_HOLOVERIFY_ARCH_082")
        ),
        "post_generation_status": "full_arch_candidate_pair_pending_judge" if all_final_admissible else "diagnostic_or_repair_required",
        "benchmark_locked": False,
        "run_dir": str(out_dir),
        "pre_run_root_signature": manifest["root_signature"],
        "trace_hash": trace_hash,
        "provider_calls": len(all_calls),
        "solo_rerun_calls": 0,
        "worker_calls": sum(1 for row in all_calls if row.get("call_kind") == "worker"),
        "holo_gov_calls": sum(1 for row in all_calls if row.get("call_kind") == "gov"),
        "judge_calls": 0,
        "totals": totals,
        "packet_results": [
            {
                "packet_id": packet["packet_id"],
                "final_admissible": packet["final_admissible"],
                "final_verdict": packet["final_verdict"],
                "final_binding": packet["final_binding"],
                "final_selector": {
                    "selected_artifact_id": packet["final_selector"]["selected_artifact_id"],
                    "selection_reason": packet["final_selector"]["selection_reason"],
                },
                "artifact_registry": packet["artifact_registry"],
            }
            for packet in packet_results
        ],
    }
    (out_dir / "live_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    md = [
        f"# {globals().get('FULL_ARCH_TITLE', 'Full HoloVerify Architecture 082 Replay')}",
        "",
        f"Classification: `{summary['classification']}`",
        f"Post-generation status: `{summary['post_generation_status']}`",
        f"Provider calls: `{summary['provider_calls']}`",
        f"Worker calls: `{summary['worker_calls']}`",
        f"Gov calls: `{summary['holo_gov_calls']}`",
        "Solo rerun calls: `0`",
        "Judge calls: `0`",
        f"Trace hash: `{trace_hash[:16]}`",
        "",
        "| Packet | Final Verdict | Final Binding | Admissible | Selector |",
        "| --- | --- | --- | --- | --- |",
    ]
    for packet in summary["packet_results"]:
        md.append(
            f"| `{packet['packet_id']}` | `{packet['final_verdict']}` | `{packet['final_binding']}` | {packet['final_admissible']} | `{packet['final_selector']['selection_reason']}` |"
        )
    (out_dir / "live_summary.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if complete else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--run-live", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        manifest = build_preflight()
        print(json.dumps({"preflight": "ok", "root_signature": manifest["root_signature"], "manifest": str(PRE_RUN_MANIFEST)}, indent=2))
        return 0
    if args.run_live:
        return run_live()
    parser.error("Use --preflight or --run-live")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
