#!/usr/bin/env python3
"""Run HoloVerify-V Gov replay for Kit C pair 042.

This is a Holo-only continuation against frozen one-shot Solo evidence:

- Solo evidence source: v3 atlas-targeted screen run_20260628T223314Z.
- Holo model: MiniMax-M2.5-highspeed, same weak model family used for Solo.
- Calls: two Gov-V calls, one for 042-A and one for 042-B.
- No judges, no worker calls, no Solo rerun, no benchmark lock.
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

BENCHMARK_ROOT = ROOT.parent
SOURCE_RUN = BENCHMARK_ROOT / "kit_c_atlas_targeted_screen_v3_2026-06-28" / "run_20260628T223314Z"
SOURCE_TRACE = SOURCE_RUN / "CONTROL_SCREEN_TRACE.jsonl"
MODEL = "MiniMax-M2.5-highspeed"

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
    "pair_id": "HV-KITC-042",
    "seam": "limited-scope sourcing note versus exact EHS execution release",
    "atlas": "\n".join(
        [
            "HoloVerify-V source-boundary atlas for this family:",
            "",
            "Models may over-escalate a valid controlled purchase because a sourcing note says only quote collection may proceed.",
            "That note is a limited-scope artifact. It is not a blocker when a separate EHS execution release explicitly matches the controlled-material purchase boundary.",
            "",
            "Use ALLOW when the execution release itself matches material, quantity band, facility, and purchase order before PO issuance.",
            "Use ESCALATE when the record is only a sourcing review, or when purchase execution release remains pending.",
            "",
            "Do not let a preliminary sourcing note override a later exact execution release.",
            "Do not invent missing requirements beyond the policy text.",
        ]
    ),
    "command": "Adjudicate whether procurement may issue the controlled-solvent purchase order. Bind the sourcing note and EHS record to the exact PO execution boundary.",
    "schema_key": "execution_release_binding",
    "schema": {
        "purchase_order_id": "string",
        "limited_scope_note_id": "string",
        "execution_release_id": "string",
        "material": "string",
        "quantity_band": "string",
        "facility": "string",
        "purchase_order_match": "string",
        "binding_class": "EXACT_EXECUTION_RELEASE_CLOSED | EXECUTION_RELEASE_PENDING | UNRESOLVED",
        "controlling_source_fact": "string",
    },
    "packets": [
        {
            "packet_id": "HV-KITC-042-A",
            "payload": SOURCE_RUN / "generated_packets" / "HV-KITC-042-A.payload.json",
            "local_audit_target": "ALLOW",
            "expected_binding": "EXACT_EXECUTION_RELEASE_CLOSED",
            "required_knew_terms": [
                "EHS-NOV-042",
                "NS-55",
                ["0-25", "0 to 25", "0–25"],
                ["Facility R2", "facility (R2)", "R2"],
                "PO-NOV-042",
                "execution release",
            ],
        },
        {
            "packet_id": "HV-KITC-042-B",
            "payload": SOURCE_RUN / "generated_packets" / "HV-KITC-042-B.payload.json",
            "local_audit_target": "ESCALATE",
            "expected_binding": "EXECUTION_RELEASE_PENDING",
            "required_knew_terms": ["EHS-NOV-042", "sourcing review", "execution release", "scheduled"],
        },
    ],
}


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


def _gov_schema() -> dict[str, Any]:
    return {
        "gov_mode": "CONTROL_ROUTER",
        "surface": "HOLOVERIFY_V",
        "route_verdict": "FINAL_COMPILER for ALLOW | FAIL_CLOSED for ESCALATE",
        "verification_verdict": "ALLOW | ESCALATE",
        PAIR["schema_key"]: PAIR["schema"],
        "blocked_inferences": ["string"],
        "deterministic_gate_checks": {
            "source_records_cited": "boolean",
            "limited_scope_note_not_treated_as_final_blocker": "boolean",
            "execution_release_boundary_compared": "boolean",
            "po_id_compared": "boolean",
            "material_quantity_facility_compared": "boolean",
        },
        "cited_evidence": ["string"],
        "open_blockers": ["string"],
        "final_compiler_allowed": "boolean",
    }


def _build_gov_prompt(packet: dict[str, Any], payload: dict[str, Any]) -> tuple[str, str]:
    system = "\n".join(
        [
            "You are HoloVerify-V Gov in a hard-ALLOW false-positive-reduction diagnostic.",
            "Gov does not choose models. Gov chooses verification verdict and control action under the run lock.",
            "No judges. No worker calls. No fallback. Return only valid JSON. No markdown fences.",
            PAIR["atlas"],
            "Route consistency hard gate: ALLOW requires route_verdict FINAL_COMPILER and final_compiler_allowed true. ESCALATE requires route_verdict FAIL_CLOSED and final_compiler_allowed false.",
            "Citation hard gate: cite exact source doc_id values from the current packet. Do not cite only business_ref identifiers when a doc_id exists.",
            "Required JSON shape:",
            json.dumps(_gov_schema(), indent=2),
        ]
    )
    user = json.dumps(
        {
            "packet_id": packet["packet_id"],
            "action": payload["action"],
            "context": payload["context"],
            "command": PAIR["command"],
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
    cited = obj.get("cited_evidence") or obj.get("cited_artifacts") or []
    if not isinstance(cited, list) or not cited:
        return ["cited_sources_missing"]
    for item in cited:
        text = str(item)
        if any(source_id in text for source_id in valid_ids):
            continue
        candidate = text.split(":", 1)[0].split(" ", 1)[0].strip()
        failures.append(f"invented_or_non_doc_source:{candidate or text[:40]}")
    return failures


def _validate_knew(obj: dict[str, Any], required_terms: list[Any]) -> list[str]:
    text = json.dumps(obj).lower()
    failures = []
    for term in required_terms:
        if isinstance(term, (list, tuple)):
            if not any(str(option).lower() in text for option in term):
                failures.append(f"knew_term_missing_any:{'|'.join(str(option) for option in term)}")
        elif str(term).lower() not in text:
            failures.append(f"knew_term_missing:{term}")
    return failures


def _validate_output(packet: dict[str, Any], obj: dict[str, Any], valid_ids: set[str]) -> list[str]:
    failures = []
    verdict = obj.get("verification_verdict") or obj.get("verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("verdict_invalid")
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
    binding = obj.get(PAIR["schema_key"])
    if not isinstance(binding, dict):
        failures.append(f"{PAIR['schema_key']}_missing")
    elif binding.get("binding_class") != packet["expected_binding"]:
        failures.append(f"binding_class_expected_{packet['expected_binding']}")
    if verdict != packet["local_audit_target"]:
        failures.append(f"local_audit_target_expected_{packet['local_audit_target']}")
    failures.extend(_validate_source_ids(obj, valid_ids))
    failures.extend(f"forbidden_gov_key:{p}" for p in _forbidden_gov_keys(obj))
    failures.extend(_validate_knew(obj, packet["required_knew_terms"]))
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
        "max_tokens": 1800,
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
        "text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "finish_reason": first_choice.get("finish_reason"),
        "response_id": data.get("id"),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": int((time.time() - started) * 1000),
    }


def build_preflight() -> dict[str, Any]:
    FROZEN_PACKET_DIR.mkdir(parents=True, exist_ok=True)
    packet_records = []
    prompt_records = []
    for packet in PAIR["packets"]:
        payload = _load_json(packet["payload"])
        frozen_path = FROZEN_PACKET_DIR / f"{packet['packet_id']}.payload.json"
        frozen_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        system, user = _build_gov_prompt(packet, payload)
        packet_records.append(
            {
                "packet_id": packet["packet_id"],
                "pair_id": PAIR["pair_id"],
                "frozen_payload_path": str(frozen_path),
                "packet_payload_hash": _sha256_text(_canonical_json(payload)),
                "source_ids": sorted(_packet_source_ids(payload)),
                "local_audit_target_for_post_run_only": packet["local_audit_target"],
            }
        )
        prompt_records.append(
            {
                "packet_id": packet["packet_id"],
                "holo_full_prompt_hash": _sha256_text(system + "\n" + user),
            }
        )
    architecture_lock = {
        "run_name": "HOLOVERIFY_V_KITC_042_HARD_ALLOW_FP_DIAGNOSTIC_2026_06_28",
        "status": "pre_registered_holo_only_against_frozen_solo",
        "surface": "HoloVerify-V",
        "benchmark_credit": False,
        "post_generation_status_if_clean": "candidate_pair_holo_tested_pending_judge",
        "model_roster": {
            "frozen_solo_provider": "minimax",
            "frozen_solo_model": MODEL,
            "holo_gov_provider": "minimax",
            "holo_gov_model": MODEL,
            "gov_may_select_models": False,
            "fallback_policy": "NO_FALLBACK_PROVIDER_FAILURE_INVALIDATES_RUN",
        },
        "expected_counts": {
            "new_provider_calls": 2,
            "solo_rerun_calls": 0,
            "holo_gov_calls": 2,
            "worker_calls": 0,
            "judge_calls": 0,
        },
        "holo_inputs": ["current packet action/context", "source-neutral family atlas", "Gov-V structured schema"],
        "forbidden_inputs": ["hidden expected verdict", "correctness labels", "frozen Solo raw_text", "judge notes"],
    }
    preimage = _canonical_json(
        {
            "architecture_lock": architecture_lock,
            "packet_records": packet_records,
            "prompt_records": prompt_records,
            "source_solo_rows_hash": _sha256_text(_canonical_json(_source_solo_rows())),
        }
    )
    manifest = {
        "architecture_lock": architecture_lock,
        "packet_records": packet_records,
        "prompt_records": prompt_records,
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
    rows = []
    trace_path = out_dir / "TRACE_CALLS.jsonl"
    with trace_path.open("w") as trace:
        for call_index, packet in enumerate(PAIR["packets"], start=1):
            payload = _load_json(packet["payload"])
            valid_ids = _packet_source_ids(payload)
            system, user = _build_gov_prompt(packet, payload)
            meta = {
                "call_index": call_index,
                "called_at": datetime.now(timezone.utc).isoformat(),
                "lane": "holo",
                "label": "HOLOVERIFY_V_GOV_042_REPLAY",
                "provider": "minimax",
                "model": MODEL,
                "packet_id": packet["packet_id"],
                "pair_id": PAIR["pair_id"],
                "pre_run_root_signature": manifest["root_signature"],
                "prompt_chars": {"system": len(system), "user": len(user)},
            }
            try:
                response = _call_minimax(system, user)
                parsed = _json_from_text(response["text"])
                failures = _validate_output(packet, parsed, valid_ids)
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
                row = {**meta, "provider_call_ok": False, "parse_ok": False, "error": f"{type(exc).__name__}: {exc}", "admissible": False}
                trace.write(json.dumps(row) + "\n")
                rows.append(row)
                break
            trace.write(json.dumps(row) + "\n")
            rows.append(row)
    totals = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for row in rows:
        for key in totals:
            value = row.get(key)
            if isinstance(value, int):
                totals[key] += value
    complete = len(rows) == 2 and all(row.get("provider_call_ok") for row in rows)
    all_admissible = complete and all(row.get("admissible") for row in rows)
    trace_hash = _sha256_text(trace_path.read_text())
    summary = {
        "classification": "HOLOVERIFY_V_042_HOLO_ONLY_COMPLETE" if complete else "INVALID_OR_INCOMPLETE_HOLOVERIFY_V_042",
        "post_generation_status": "candidate_pair_holo_tested_pending_judge" if all_admissible else "diagnostic_or_repair_required",
        "benchmark_locked": False,
        "run_dir": str(out_dir),
        "pre_run_root_signature": manifest["root_signature"],
        "trace_hash": trace_hash,
        "provider_calls": len(rows),
        "solo_rerun_calls": 0,
        "worker_calls": 0,
        "judge_calls": 0,
        "totals": totals,
        "rows": [
            {
                "call_index": row.get("call_index"),
                "packet_id": row.get("packet_id"),
                "provider_call_ok": row.get("provider_call_ok"),
                "parse_ok": row.get("parse_ok"),
                "admissible": row.get("admissible"),
                "verdict": (row.get("parsed_json") or {}).get("verification_verdict") if isinstance(row.get("parsed_json"), dict) else None,
                "binding_class": ((row.get("parsed_json") or {}).get(PAIR["schema_key"]) or {}).get("binding_class") if isinstance(row.get("parsed_json"), dict) else None,
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
        "# HoloVerify-V 042 Hard ALLOW FP Diagnostic",
        "",
        f"Classification: `{summary['classification']}`",
        f"Post-generation status: `{summary['post_generation_status']}`",
        f"Provider calls: `{len(rows)}`",
        "Solo rerun calls: `0`",
        "Worker calls: `0`",
        "Judge calls: `0`",
        f"Trace hash: `{trace_hash[:16]}`",
        "",
        "| Packet | Verdict | Binding | Admissible | Failures |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in summary["rows"]:
        md.append(f"| `{row['packet_id']}` | `{row['verdict']}` | `{row['binding_class']}` | {row['admissible']} | {row.get('deterministic_failures') or row.get('error') or []} |")
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
