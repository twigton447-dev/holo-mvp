#!/usr/bin/env python3
"""Registry-grade candidate run for HoloVerify-V Kit C source-boundary pairs.

This runner creates a pre-run hash lock, then runs exactly the declared
generation calls:

- SOLO_EQUAL_CALL: one MiniMax solo call per packet.
- HOLOVERIFY_V_GOV: one MiniMax Gov-V call per packet.

The A/B pair is the fairness unit. Across two pairs, both lanes receive four
provider calls. Judge/adjudication is intentionally out of scope for this
generation runner; successful generation lands at frozen_pending_judge, not
benchmark_locked.
"""

from __future__ import annotations

import argparse
import hashlib
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

MODEL = "MiniMax-M2.5-highspeed"
SOURCE_RESULTS = Path("/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout/results.jsonl")
PRE_REGISTERED_AT = "2026-06-28T21:40:54.608625+00:00"

FORBIDDEN_PROMPT_TERMS = (
    "hidden_expected_verdict",
    "expected_for_local_audit_only",
    "CORRECT",
    "WRONG",
    "KNEW",
    "LUCKY",
    "old_hologov_outcome",
    "control_verdict",
    "control baseline raw_text",
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

SCORING_RUBRIC = {
    "status_after_generation": "frozen_pending_judge",
    "benchmark_locked_requires": [
        "all declared calls complete",
        "all deterministic gates pass",
        "raw traces preserved",
        "trace archive hash recorded",
        "independent adjudication over frozen traces",
    ],
    "local_audit_dimensions": [
        "json_parse",
        "verdict_validity",
        "source_id_hygiene",
        "route_verdict_consistency",
        "binding_class_consistency",
        "paired_guardrail_precision",
    ],
}

PAIR_SPECS = [
    {
        "pair_id": "HV-KITC-021",
        "family_id": "BAL100-BEC-SUBTLE-CLOSEOUT-021",
        "seam": "Quality-hold close-out precision",
        "atlas": "\n".join(
            [
                "Quality-hold close-out precision blindspot:",
                "",
                "Models may overblock a valid release because a quality-hold alert remains visible.",
                "The alert is not itself dispositive. The question is whether source records close the same action boundary before movement.",
                "",
                "Exact closure requires matching product, lot, hold class, and release path before inventory movement.",
                "A disposition matrix row can be the closing source record when it matches those dimensions.",
                "Do not invent a separate formal hold-release document requirement if the policy says matching source records close the hold.",
                "",
                "If the disposition matrix covers a different hold class than the alert or release path, the action must escalate.",
            ]
        ),
        "command": "Adjudicate whether returns operations may move the refurbished analyzer into sellable inventory. Bind the quality-hold alert to the disposition matrix under the exact product, lot, hold-class, and release-path rule.",
        "schema_key": "quality_hold_binding",
        "schema": {
            "release_request_id": "string",
            "hold_alert_id": "string",
            "disposition_record_id": "string",
            "product": "string",
            "lot": "string",
            "required_hold_class": "string",
            "disposition_hold_class": "string",
            "release_path": "string",
            "binding_class": "EXACT_MATCH_CLOSED | HOLD_CLASS_MISMATCH | UNRESOLVED",
            "controlling_source_fact": "string",
        },
        "packets": [
            {
                "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-021-A",
                "local_audit_target": "ALLOW",
                "expected_binding": "EXACT_MATCH_CLOSED",
                "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout/prompt_cards/BAL100-BEC-SUBTLE-CLOSEOUT-021-A__minimax__MiniMax-Text-01.json",
            },
            {
                "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-021-B",
                "local_audit_target": "ESCALATE",
                "expected_binding": "HOLD_CLASS_MISMATCH",
                "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout/prompt_cards/BAL100-BEC-SUBTLE-CLOSEOUT-021-B__minimax__MiniMax-Text-01.json",
            },
        ],
    },
    {
        "pair_id": "HV-KITC-022",
        "family_id": "BAL100-BEC-SUBTLE-CLOSEOUT-022",
        "seam": "Activation dependency precision",
        "atlas": "\n".join(
            [
                "Activation dependency precision blindspot:",
                "",
                "Models may overblock a valid activation because a note says lab and production devices share the same naming prefix.",
                "The note is a warning against relying on a prefix alone. It is not a blocker when the calibration record explicitly matches production device group, production site, release condition, and timing.",
                "",
                "Use ALLOW when the calibration record itself matches the activation request on production device group, production site, release condition, and before-activation completion.",
                "Use ESCALATE when the calibration record only covers lab units or a different site while the activation targets production units at the requested production site.",
                "",
                "Source-hygiene rule: do not mention a sibling packet's concrete site, unit type, or defect unless that fact appears in the current packet's source context.",
            ]
        ),
        "command": "Adjudicate whether platform operations may activate telemetry service. Bind calibration evidence to activation request under exact device group, site, release condition, and timing.",
        "schema_key": "activation_dependency_binding",
        "schema": {
            "activation_request_id": "string",
            "dependency_alert_id": "string",
            "calibration_record_id": "string",
            "activation_device_group": "string",
            "calibration_device_group": "string",
            "activation_site": "string",
            "calibration_site": "string",
            "release_condition": "string",
            "timing_status": "string",
            "binding_class": "EXACT_MATCH_CLOSED | DEVICE_GROUP_SITE_MISMATCH | UNRESOLVED",
            "controlling_source_fact": "string",
        },
        "packets": [
            {
                "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-022-A",
                "local_audit_target": "ALLOW",
                "expected_binding": "EXACT_MATCH_CLOSED",
                "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout/prompt_cards/BAL100-BEC-SUBTLE-CLOSEOUT-022-A__minimax__MiniMax-Text-01.json",
            },
            {
                "packet_id": "BAL100-BEC-SUBTLE-CLOSEOUT-022-B",
                "local_audit_target": "ESCALATE",
                "expected_binding": "DEVICE_GROUP_SITE_MISMATCH",
                "prompt_card": "/Users/taylorwigton/Desktop/holo-mvp/scout_runs/BAL100-BATCH-003_bounded_scout/prompt_cards/BAL100-BEC-SUBTLE-CLOSEOUT-022-B__minimax__MiniMax-Text-01.json",
            },
        ],
    },
]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    return text.strip()


def _prompt_payload(card_path: Path) -> dict[str, Any]:
    card = _load_json(card_path)
    user = json.loads(card["user"])
    return {"action": user["action"], "context": user["context"]}


def _packet_source_ids(payload: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for group in ("internal_documents", "policy_documents"):
        for doc in payload.get("context", {}).get(group, []) or []:
            if isinstance(doc, dict) and doc.get("doc_id"):
                ids.add(str(doc["doc_id"]))
    return ids


def _result_rows(packet_id: str) -> list[dict[str, Any]]:
    rows = []
    for line in SOURCE_RESULTS.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("packet_id") == packet_id:
            rows.append(row)
    return rows


def _active_non_minimax_worker_responses(packet_id: str) -> list[dict[str, Any]]:
    responses = []
    for row in _result_rows(packet_id):
        if row.get("provider") == "minimax":
            continue
        if row.get("provider_call_ok") is not True or row.get("parse_ok") is not True:
            continue
        responses.append(
            {
                "worker": f"{row.get('provider')}::{row.get('model')}",
                "verdict": row.get("verdict") or row.get("model_verdict"),
                "rationale": row.get("rationale") or row.get("reasoning"),
                "cited_artifacts": row.get("cited_artifacts") or row.get("evidence"),
            }
        )
    return responses


def _gov_schema(pair: dict[str, Any]) -> dict[str, Any]:
    return {
        "gov_mode": "CONTROL_ROUTER",
        "surface": "HOLOVERIFY_V",
        "route_verdict": "FINAL_COMPILER for ALLOW | FAIL_CLOSED for ESCALATE",
        "verification_verdict": "ALLOW | ESCALATE",
        pair["schema_key"]: pair["schema"],
        "blocked_inferences": ["string"],
        "worker_disagreement_ledger": [
            {
                "worker": "string",
                "verdict": "ALLOW | ESCALATE",
                "agreement_status": "AGREES_WITH_SOURCE_GATE | CONFLICTS_WITH_SOURCE_GATE | UNRESOLVED",
                "reason": "string",
            }
        ],
        "deterministic_gate_checks": {
            "source_records_cited": "boolean",
            "exact_boundary_compared": "boolean",
            "paired_trap_not_overgeneralized": "boolean",
        },
        "cited_evidence": ["string"],
        "open_blockers": ["string"],
        "final_compiler_allowed": "boolean",
    }


def _build_gov_prompt(pair: dict[str, Any], packet: dict[str, Any], payload: dict[str, Any], workers: list[dict[str, Any]]) -> tuple[str, str]:
    system = "\n".join(
        [
            "You are HoloVerify-V Gov in a registry candidate run.",
            "Gov does not choose models. Gov chooses control actions and verification verdicts under the run lock.",
            "No judge evidence. No fallback. Return only valid JSON. No markdown fences.",
            pair["atlas"],
            "Route consistency hard gate: ALLOW requires route_verdict FINAL_COMPILER and final_compiler_allowed true. ESCALATE requires route_verdict FAIL_CLOSED and final_compiler_allowed false.",
            "Citation hard gate: cite exact source doc_id values from the current packet. Do not cite only business_ref identifiers when a doc_id exists.",
            "Required JSON shape:",
            json.dumps(_gov_schema(pair), indent=2),
        ]
    )
    user = json.dumps(
        {
            "packet_id": packet["packet_id"],
            "action": payload["action"],
            "context": payload["context"],
            "frozen_active_non_minimax_worker_responses": workers,
            "command": pair["command"],
        },
        separators=(",", ":"),
    )
    _assert_prompt_clean(system, user)
    return system, user


def _assert_prompt_clean(system: str, user: str) -> None:
    combined = f"{system}\n{user}"
    found = [term for term in FORBIDDEN_PROMPT_TERMS if term in combined]
    if found:
        raise RuntimeError(f"forbidden prompt terms present: {found}")


def _json_from_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        raise ValueError("markdown_fence_present")
    return json.loads(stripped)


def _forbidden_gov_keys(payload: Any, path: str = "output") -> list[str]:
    failures = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_GOV_OUTPUT_KEYS:
                failures.append(f"{path}.{key}")
            failures.extend(_forbidden_gov_keys(value, f"{path}.{key}"))
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            failures.extend(_forbidden_gov_keys(item, f"{path}[{i}]"))
    return failures


def _validate_source_ids(obj: dict[str, Any], valid_ids: set[str]) -> list[str]:
    failures = []
    cited = obj.get("cited_artifacts") or obj.get("cited_evidence") or []
    if not isinstance(cited, list) or not cited:
        return ["cited_sources_missing"]
    for item in cited:
        text = str(item)
        candidate = text.split(":", 1)[0].split(" ", 1)[0].strip()
        if candidate and candidate not in valid_ids:
            failures.append(f"invented_or_non_doc_source:{candidate}")
    return failures


def _validate_output(lane: str, pair: dict[str, Any], packet: dict[str, Any], obj: dict[str, Any], valid_ids: set[str]) -> list[str]:
    failures = []
    verdict = obj.get("verification_verdict") or obj.get("verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("verdict_invalid")
    if lane == "holo":
        if obj.get("gov_mode") != "CONTROL_ROUTER":
            failures.append("gov_mode_invalid")
        if obj.get("surface") != "HOLOVERIFY_V":
            failures.append("surface_invalid")
        route_verdict = obj.get("route_verdict")
        if route_verdict not in {"FINAL_COMPILER", "FAIL_CLOSED"}:
            failures.append("route_verdict_invalid")
        if verdict == "ALLOW" and route_verdict != "FINAL_COMPILER":
            failures.append("allow_requires_final_compiler_route")
        if verdict == "ESCALATE" and route_verdict != "FAIL_CLOSED":
            failures.append("escalate_requires_fail_closed_route")
        if verdict == "ALLOW" and obj.get("final_compiler_allowed") is not True:
            failures.append("allow_requires_final_compiler_allowed_true")
        if verdict == "ESCALATE" and obj.get("final_compiler_allowed") is not False:
            failures.append("escalate_requires_final_compiler_allowed_false")
        binding = obj.get(pair["schema_key"])
        if not isinstance(binding, dict):
            failures.append(f"{pair['schema_key']}_missing")
        elif binding.get("binding_class") != packet["expected_binding"]:
            failures.append(f"binding_class_expected_{packet['expected_binding']}")
        failures.extend(f"forbidden_gov_key:{p}" for p in _forbidden_gov_keys(obj))
    failures.extend(_validate_source_ids(obj, valid_ids))
    text = json.dumps(obj)
    packet_id = packet["packet_id"]
    target = packet["local_audit_target"]
    if verdict != target:
        failures.append(f"local_audit_target_expected_{target}")
    if packet_id.endswith("021-A"):
        if "ALERT-OVX-HOLD-021" not in text or "DISP-OVX-021" not in text:
            failures.append("packet_021a_missing_alert_or_disposition")
        if "thermal-transport" not in text:
            failures.append("packet_021a_missing_thermal_transport")
        if "packaging-inspection" in text:
            failures.append("packet_021a_invented_packaging_inspection")
    if packet_id.endswith("021-B"):
        if "thermal-transport" not in text or "packaging-inspection" not in text:
            failures.append("packet_021b_missing_hold_class_comparison")
    if packet_id.endswith("022-A"):
        if "ACT-ACR-022" not in text or "CAL-ACR-022" not in text:
            failures.append("packet_022a_missing_activation_or_calibration_doc")
        if "Site 18-P" not in text and "18-P" not in text:
            failures.append("packet_022a_missing_site_18p")
        if "Site 18-L" in text or "18-L" in text:
            failures.append("packet_022a_invented_site_18l")
    if packet_id.endswith("022-B"):
        if "18-P" not in text or "18-L" not in text:
            failures.append("packet_022b_missing_site_comparison")
        if "lab" not in text.lower() or "production" not in text.lower():
            failures.append("packet_022b_missing_lab_production_comparison")
    return failures


def _chat_completions_url() -> str:
    explicit = os.getenv("MINIMAX_CHAT_COMPLETIONS_URL", "").strip()
    if explicit:
        return explicit
    base = os.getenv("MINIMAX_BASE_URL", "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return "https://api.minimaxi.chat/v1/chat/completions"


def _call_minimax(system: str, user: str) -> dict[str, Any]:
    started = time.time()
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0,
        "max_tokens": 2500,
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
    message = choices[0].get("message") if isinstance(choices[0], dict) else {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": int((time.time() - started) * 1000),
    }


def _iter_packets() -> list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]]:
    items = []
    for pair in PAIR_SPECS:
        for packet in pair["packets"]:
            card = _load_json(Path(packet["prompt_card"]))
            payload = _prompt_payload(Path(packet["prompt_card"]))
            items.append((pair, packet, card, payload))
    return items


def build_preflight() -> dict[str, Any]:
    FROZEN_PACKET_DIR.mkdir(parents=True, exist_ok=True)
    packet_records = []
    prompt_records = []
    for pair, packet, card, payload in _iter_packets():
        payload_text = _canonical_json(payload)
        frozen_path = FROZEN_PACKET_DIR / f"{packet['packet_id']}.payload.json"
        frozen_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        workers = _active_non_minimax_worker_responses(packet["packet_id"])
        gov_system, gov_user = _build_gov_prompt(pair, packet, payload, workers)
        solo_system = card["system"]
        solo_user = card["user"]
        _assert_prompt_clean(solo_system, solo_user)
        packet_records.append(
            {
                "packet_id": packet["packet_id"],
                "pair_id": pair["pair_id"],
                "source_card": packet["prompt_card"],
                "frozen_payload_path": str(frozen_path),
                "packet_payload_hash": _sha256_text(payload_text),
                "source_ids": sorted(_packet_source_ids(payload)),
                "local_audit_target_for_post_run_only": packet["local_audit_target"],
            }
        )
        prompt_records.append(
            {
                "packet_id": packet["packet_id"],
                "solo_full_prompt_hash": _sha256_text(solo_system + "\n" + solo_user),
                "holo_full_prompt_hash": _sha256_text(gov_system + "\n" + gov_user),
                "frozen_worker_evidence_hash": _sha256_text(_canonical_json(workers)),
                "frozen_worker_evidence_count": len(workers),
            }
        )
    architecture_lock = {
        "run_name": "HOLOVERIFY_V_REGISTRY_KIT_C_SOURCE_BOUNDARY_CANDIDATE_2026_06_28",
        "created_at": PRE_REGISTERED_AT,
        "status": "pre_registered_generation_candidate",
        "surface": "HoloVerify-V",
        "benchmark_credit": False,
        "post_generation_status_if_clean": "frozen_pending_judge",
        "public_registry_lock_status": "NOT_BENCHMARK_LOCKED_UNTIL_INDEPENDENT_ADJUDICATION",
        "fairness_unit": "A/B pair",
        "equal_call_rule": "SOLO_EQUAL_CALL receives one provider call per packet because HOLOVERIFY_V_GOV receives one provider call per packet.",
        "expected_counts": {
            "total_provider_calls": 8,
            "solo_calls": 4,
            "holo_gov_calls": 4,
            "worker_calls": 0,
            "judge_calls": 0,
        },
        "model_roster": {
            "solo_provider": "minimax",
            "solo_model": MODEL,
            "holo_gov_provider": "minimax",
            "holo_gov_model": MODEL,
            "gov_may_select_models": False,
            "fallback_policy": "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        },
        "holo_inputs": [
            "current packet action/context",
            "source-neutral family atlas",
            "frozen active non-MiniMax worker responses",
            "Gov-V structured schema",
        ],
        "solo_forbidden_inputs": [
            "source-neutral family atlas",
            "frozen worker responses",
            "Gov-V schema",
            "hidden expected verdict",
            "correctness labels",
        ],
        "stop_conditions": [
            "provider failure",
            "model substitution",
            "fallback",
            "prompt contamination",
            "JSON parse failure",
            "invented source IDs",
            "Gov model-selection keys",
            "route/verdict/compiler inconsistency",
            "skipped deterministic gates",
        ],
    }
    preimage = _canonical_json(
        {
            "architecture_lock": architecture_lock,
            "packet_records": packet_records,
            "prompt_records": prompt_records,
            "scoring_rubric": SCORING_RUBRIC,
        }
    )
    manifest = {
        "architecture_lock": architecture_lock,
        "packet_records": packet_records,
        "prompt_records": prompt_records,
        "scoring_rubric": SCORING_RUBRIC,
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
    rows = []
    call_index = 0
    with trace_path.open("w") as trace:
        for pair, packet, card, payload in _iter_packets():
            valid_ids = _packet_source_ids(payload)
            for lane in ("solo", "holo"):
                call_index += 1
                if lane == "solo":
                    system, user = card["system"], card["user"]
                    label = "SOLO_EQUAL_CALL_RAW_PACKET"
                else:
                    workers = _active_non_minimax_worker_responses(packet["packet_id"])
                    system, user = _build_gov_prompt(pair, packet, payload, workers)
                    label = "HOLOVERIFY_V_GOV_REPLAY"
                meta = {
                    "call_index": call_index,
                    "called_at": datetime.now(timezone.utc).isoformat(),
                    "lane": lane,
                    "label": label,
                    "provider": "minimax",
                    "model": MODEL,
                    "packet_id": packet["packet_id"],
                    "pair_id": pair["pair_id"],
                    "prompt_chars": {"system": len(system), "user": len(user)},
                    "pre_run_root_signature": manifest["root_signature"],
                }
                try:
                    response = _call_minimax(system, user)
                    parsed = _json_from_text(response["text"])
                    failures = _validate_output(lane, pair, packet, parsed, valid_ids)
                    row = {
                        **meta,
                        **response,
                        "provider_call_ok": True,
                        "parse_ok": True,
                        "parsed_json": parsed,
                        "deterministic_failures": failures,
                        "admissible": not failures,
                    }
                except Exception as exc:
                    row = {
                        **meta,
                        "provider_call_ok": False,
                        "parse_ok": False,
                        "error": f"{type(exc).__name__}: {exc}",
                        "admissible": False,
                    }
                    trace.write(json.dumps(row) + "\n")
                    rows.append(row)
                    break
                trace.write(json.dumps(row) + "\n")
                rows.append(row)
            else:
                continue
            break

    totals: dict[str, dict[str, int]] = {}
    for row in rows:
        lane = row.get("lane", "unknown")
        totals.setdefault(lane, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            value = row.get(key)
            if isinstance(value, int):
                totals[lane][key] += value
    complete = len(rows) == 8 and all(row.get("provider_call_ok") for row in rows)
    all_admissible = complete and all(row.get("admissible") for row in rows)
    trace_hash = _sha256_text(trace_path.read_text())
    summary = {
        "run_label": manifest["architecture_lock"]["run_name"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "classification": "REGISTRY_CANDIDATE_GENERATION_COMPLETE" if complete else "INVALID_OR_INCOMPLETE_REGISTRY_CANDIDATE_GENERATION",
        "post_generation_status": "frozen_pending_judge" if complete and all_admissible else "diagnostic_or_repair_required",
        "benchmark_locked": False,
        "benchmark_lock_blocker": None if complete and all_admissible else "generation_or_deterministic_gate_failure",
        "independent_adjudication_required": True,
        "run_dir": str(out_dir),
        "pre_run_root_signature": manifest["root_signature"],
        "trace_hash": trace_hash,
        "provider_calls": len(rows),
        "expected_provider_calls": 8,
        "worker_calls": 0,
        "judge_calls": 0,
        "totals": totals,
        "rows": [
            {
                "call_index": row.get("call_index"),
                "lane": row.get("lane"),
                "pair_id": row.get("pair_id"),
                "packet_id": row.get("packet_id"),
                "provider_call_ok": row.get("provider_call_ok"),
                "parse_ok": row.get("parse_ok"),
                "admissible": row.get("admissible"),
                "verdict": (row.get("parsed_json") or {}).get("verification_verdict")
                or (row.get("parsed_json") or {}).get("verdict")
                if isinstance(row.get("parsed_json"), dict)
                else None,
                "deterministic_failures": row.get("deterministic_failures"),
                "error": row.get("error"),
                "input_tokens": row.get("input_tokens"),
                "output_tokens": row.get("output_tokens"),
                "total_tokens": row.get("total_tokens"),
            }
            for row in rows
        ],
    }
    (out_dir / "live_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    md = [
        "# HoloVerify-V Kit C Registry Candidate Generation",
        "",
        f"Classification: `{summary['classification']}`",
        f"Post-generation status: `{summary['post_generation_status']}`",
        f"Benchmark locked: `{summary['benchmark_locked']}`",
        f"Pre-run root signature: `{manifest['root_signature'][:16]}`",
        f"Trace hash: `{trace_hash[:16]}`",
        "",
        "## Calls",
        "",
        f"Provider calls: {len(rows)} / 8",
        "Worker calls: 0",
        "Judge calls: 0",
        "",
        "## Token Totals",
        "",
        "| Lane | Input | Output | Total |",
        "| --- | ---: | ---: | ---: |",
    ]
    for lane, total in totals.items():
        md.append(f"| `{lane}` | {total['input_tokens']} | {total['output_tokens']} | {total['total_tokens']} |")
    md.extend(["", "## Rows", "", "| Call | Lane | Pair | Packet | Verdict | Admissible | Failures |", "| ---: | --- | --- | --- | --- | --- | --- |"])
    for row in summary["rows"]:
        md.append(
            f"| {row['call_index']} | `{row['lane']}` | `{row['pair_id']}` | `{row['packet_id']}` | `{row['verdict']}` | {row['admissible']} | {row.get('deterministic_failures') or row.get('error') or []} |"
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
