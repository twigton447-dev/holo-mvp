#!/usr/bin/env python3
"""Run the MiniMax control versus HoloVerify-V callback provenance diagnostic.

The runner builds sanitized prompts from the existing post-patch rerun records.
It intentionally excludes hidden expected verdicts and old HoloGov outputs from
provider prompts. It writes trace artifacts beside this script.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
LOCK_PATH = ROOT / "ARCHITECTURE_LOCK.json"
OUT_BASE = ROOT / "live_runs"

DOCTRINE = """
Callback provenance controls the ALLOW/ESCALATE decision.

If callback number_source is portal_change_record, change_request, invoice,
submitted_contact_phone, or another newly supplied contact source, the payment
must ESCALATE. Completed AP signoff, vendor-master audit, elevated scrutiny,
invoice cross-reference, or hold release cannot cure a noncompliant callback
source.

If callback number_source is pre-change vendor_master_snapshot and required
controls are closed, portal-change context elsewhere in the packet must not
force escalation.
""".strip()

CONTROL_SCHEMA = {
    "lane": "MINIMAX_CONTROL_RAW_VERIFY",
    "verification_verdict": "ALLOW | ESCALATE",
    "callback_source_binding": {
        "callback_record_id": "string",
        "number_source_field": "string",
        "binding_class": "COMPLIANT_PRECHANGE_VENDOR_MASTER | NONCOMPLIANT_NEWLY_SUPPLIED_SOURCE | UNRESOLVED",
        "controlling_source_fact": "string",
    },
    "blocked_inferences": ["string"],
    "deterministic_gate_checks": {
        "exact_callback_source_field_cited": "boolean",
        "portal_context_not_treated_as_callback_source": "boolean",
        "downstream_controls_not_used_to_cure_bad_source": "boolean",
        "closed_controls_recognized_when_source_is_compliant": "boolean",
    },
    "cited_evidence": ["string"],
    "open_blockers": ["string"],
    "reasoning": "string",
}

GOV_SCHEMA = {
    "gov_mode": "CONTROL_ROUTER",
    "surface": "HOLOVERIFY_V",
    "route_verdict": "FINAL_COMPILER | FAIL_CLOSED",
    "verification_verdict": "ALLOW | ESCALATE",
    "callback_source_binding": CONTROL_SCHEMA["callback_source_binding"],
    "blocked_inferences": ["string"],
    "worker_disagreement_ledger": [
        {
            "worker": "string",
            "verdict": "ALLOW | ESCALATE",
            "agreement_status": "AGREES_WITH_SOURCE_GATE | CONFLICTS_WITH_SOURCE_GATE | UNRESOLVED",
            "reason": "string",
        }
    ],
    "deterministic_gate_checks": CONTROL_SCHEMA["deterministic_gate_checks"],
    "cited_evidence": ["string"],
    "open_blockers": ["string"],
    "final_compiler_allowed": "boolean",
}

FORBIDDEN_PROMPT_TERMS = (
    "hidden_expected_verdict",
    "old_hologov_outcome",
    "old HoloGov verdict",
    "packet_role",
    "CORRECT",
    "WRONG",
    "KNEW",
    "LUCKY",
)

FORBIDDEN_GOV_OUTPUT_KEYS = {
    "model",
    "model_id",
    "model_choice",
    "model_selection",
    "next_model",
    "selected_model",
    "selected_provider",
    "provider",
    "provider_choice",
    "worker_model",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _extract_payload_from_prompt_card(path: Path) -> dict[str, Any]:
    card = _load_json(path)
    user = json.loads(card["user"])
    return {"action": user["action"], "context": user["context"]}


def _source_record(packet: dict[str, Any]) -> dict[str, Any]:
    return _load_json(Path(packet["record_path"]))


def _active_worker_responses(record: dict[str, Any]) -> list[dict[str, Any]]:
    rows = record["calls"]["active_non_gov"]
    responses: list[dict[str, Any]] = []
    for row in rows:
        if row.get("provider_call_ok") is not True or row.get("parse_ok") is not True:
            continue
        responses.append(
            {
                "provider": row.get("provider"),
                "model": row.get("model"),
                "verdict": row.get("verdict"),
                "material_blocker": row.get("material_blocker"),
                "evidence": row.get("evidence"),
                "reasoning": row.get("reasoning"),
            }
        )
    return responses


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


def _strip_thinking_blocks(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text or "", flags=re.S | re.I)
    text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.S | re.I)
    return text.strip()


def _forbidden_gov_keys(payload: Any, path: str = "output") -> list[str]:
    failures: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in FORBIDDEN_GOV_OUTPUT_KEYS:
                failures.append(f"{path}.{key}")
            failures.extend(_forbidden_gov_keys(value, f"{path}.{key}"))
    elif isinstance(payload, list):
        for i, item in enumerate(payload):
            failures.extend(_forbidden_gov_keys(item, f"{path}[{i}]"))
    return failures


def _build_control_prompt(packet: dict[str, Any], payload: dict[str, Any]) -> tuple[str, str]:
    system = "\n".join(
        [
            "You are the MiniMax control verifier for a HoloVerify diagnostic.",
            "No benchmark credit. No worker evidence. No judge evidence. No fallback.",
            "Return only valid JSON. No markdown fences.",
            DOCTRINE,
            "Required JSON shape:",
            json.dumps(CONTROL_SCHEMA, indent=2),
        ]
    )
    user = json.dumps(
        {
            "packet_id": packet["packet_id"],
            "action": payload["action"],
            "context": payload["context"],
            "command": "Adjudicate whether AP may release the payment. Bind the verdict to the exact callback number_source field.",
        },
        separators=(",", ":"),
    )
    _assert_prompt_clean(system, user)
    return system, user


def _build_gov_prompt(
    packet: dict[str, Any], payload: dict[str, Any], workers: list[dict[str, Any]]
) -> tuple[str, str]:
    system = "\n".join(
        [
            "You are HoloVerify-V Gov in a diagnostic replay.",
            "Gov does not choose models. Gov chooses control actions and verification verdicts under the run lock.",
            "No benchmark credit. No worker calls. No judge evidence. No fallback.",
            "Return only valid JSON. No markdown fences.",
            DOCTRINE,
            "Required JSON shape:",
            json.dumps(GOV_SCHEMA, indent=2),
        ]
    )
    user = json.dumps(
        {
            "packet_id": packet["packet_id"],
            "action": payload["action"],
            "context": payload["context"],
            "frozen_active_non_gov_worker_responses": workers,
            "command": "Adjudicate the packet. Resolve worker disagreement by binding to the exact callback number_source field.",
        },
        separators=(",", ":"),
    )
    _assert_prompt_clean(system, user)
    return system, user


def _chat_completions_url() -> str:
    explicit = os.getenv("MINIMAX_CHAT_COMPLETIONS_URL", "").strip()
    if explicit:
        return explicit
    base = os.getenv("MINIMAX_BASE_URL", "").strip()
    if base:
        return base.rstrip("/") + "/chat/completions"
    return "https://api.minimaxi.chat/v1/chat/completions"


def _call_minimax(model: str, system: str, user: str) -> dict[str, Any]:
    started = time.time()
    payload = {
        "model": model,
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
        status = getattr(response, "status", None)
        content_type = response.headers.get("content-type", "")
        body = response.read().decode("utf-8", errors="replace")
    try:
        data = json.loads(body)
    except Exception as exc:
        excerpt = body[:500].replace(os.getenv("MINIMAX_API_KEY", ""), "[REDACTED]")
        raise RuntimeError(
            f"minimax_non_json_response status={status} content_type={content_type!r} "
            f"body_excerpt={excerpt!r}"
        ) from exc
    elapsed_ms = int((time.time() - started) * 1000)
    choices = data.get("choices") or [{}]
    message = choices[0].get("message") if isinstance(choices[0], dict) else {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    return {
        "text": _strip_thinking_blocks((message or {}).get("content") or ""),
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "elapsed_ms": elapsed_ms,
    }


def _validate_output(lane: str, packet_id: str, obj: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    verdict = obj.get("verification_verdict")
    if verdict not in {"ALLOW", "ESCALATE"}:
        failures.append("verification_verdict_invalid")
    binding = obj.get("callback_source_binding")
    if not isinstance(binding, dict):
        failures.append("callback_source_binding_missing")
    else:
        if not str(binding.get("number_source_field", "")).strip():
            failures.append("number_source_field_missing")
        if binding.get("binding_class") not in {
            "COMPLIANT_PRECHANGE_VENDOR_MASTER",
            "NONCOMPLIANT_NEWLY_SUPPLIED_SOURCE",
            "UNRESOLVED",
        }:
            failures.append("binding_class_invalid")
    checks = obj.get("deterministic_gate_checks")
    if not isinstance(checks, dict):
        failures.append("deterministic_gate_checks_missing")
    if lane == "gov":
        if obj.get("gov_mode") != "CONTROL_ROUTER":
            failures.append("gov_mode_invalid")
        if obj.get("route_verdict") not in {"FINAL_COMPILER", "FAIL_CLOSED"}:
            failures.append("route_verdict_invalid")
        failures.extend(f"forbidden_gov_key:{p}" for p in _forbidden_gov_keys(obj))
    if packet_id == "HBB-BEC-001-CALLBACK-PROVENANCE-FAIL":
        if verdict != "ESCALATE":
            failures.append("packet_a_expected_escalate")
        text = json.dumps(obj)
        if "CALLSYS-448219" not in text:
            failures.append("packet_a_missing_callsys")
        if "portal_change_record" not in text and "submitted_contact_phone" not in text:
            failures.append("packet_a_missing_new_source_binding")
    if packet_id == "HBB-BEC-002-HARD-ALLOW":
        if verdict != "ALLOW":
            failures.append("packet_b_expected_allow")
        text = json.dumps(obj)
        if "CALLSYS-771904" not in text:
            failures.append("packet_b_missing_callsys")
        if "vendor_master_snapshot" not in text:
            failures.append("packet_b_missing_vendor_master_binding")
    return failures


def main() -> int:
    lock = _load_json(LOCK_PATH)
    if lock.get("expected_live_counts_after_explicit_approval", {}).get("total_provider_calls") != 4:
        raise RuntimeError("lock_expected_call_count_not_4")

    api_key = os.getenv("MINIMAX_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("MINIMAX_API_KEY missing")

    model = lock["run_model_lock"]["control_model"]
    if model != lock["run_model_lock"]["gov_v_model"]:
        raise RuntimeError("control_and_gov_model_mismatch")

    run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")
    out_dir = OUT_BASE / run_id
    if out_dir.exists():
        raise RuntimeError(f"refusing to overwrite existing run directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=False)

    trace_path = out_dir / "TRACE_CALLS.jsonl"
    result_rows: list[dict[str, Any]] = []

    with trace_path.open("w") as trace:
        call_index = 0
        for packet in lock["packets"]:
            record = _source_record(packet)
            payload = _extract_payload_from_prompt_card(Path(packet["prompt_card_paths"][0]))
            workers = _active_worker_responses(record)

            for lane in ("control", "gov"):
                call_index += 1
                if lane == "control":
                    system, user = _build_control_prompt(packet, payload)
                    label = "MINIMAX_CONTROL_RAW_VERIFY"
                else:
                    system, user = _build_gov_prompt(packet, payload, workers)
                    label = "HOLOVERIFY_V_GOV_REPLAY"

                call_meta = {
                    "call_index": call_index,
                    "called_at": datetime.now(timezone.utc).isoformat(),
                    "lane": lane,
                    "label": label,
                    "provider": "minimax",
                    "model": model,
                    "transport": "direct_https_chat_completions",
                    "chat_completions_url": _chat_completions_url(),
                    "packet_id": packet["packet_id"],
                    "prompt_chars": {"system": len(system), "user": len(user)},
                }
                try:
                    response = _call_minimax(model, system, user)
                    parsed = _json_from_text(response["text"])
                    failures = _validate_output(lane, packet["packet_id"], parsed)
                    row = {
                        **call_meta,
                        **response,
                        "parse_ok": True,
                        "parsed_json": parsed,
                        "deterministic_failures": failures,
                        "admissible": not failures,
                    }
                except Exception as exc:  # fail closed and preserve trace
                    row = {
                        **call_meta,
                        "provider_call_ok": False,
                        "parse_ok": False,
                        "error": f"{type(exc).__name__}: {exc}",
                        "admissible": False,
                    }
                    trace.write(json.dumps(row) + "\n")
                    result_rows.append(row)
                    break

                row["provider_call_ok"] = True
                trace.write(json.dumps(row) + "\n")
                result_rows.append(row)
            else:
                continue
            break

    totals: dict[str, dict[str, int]] = {}
    for row in result_rows:
        lane = row.get("lane", "unknown")
        totals.setdefault(lane, {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0})
        for field in ("input_tokens", "output_tokens", "total_tokens"):
            value = row.get(field)
            if isinstance(value, int):
                totals[lane][field] += value

    complete = len(result_rows) == 4 and all(r.get("provider_call_ok") for r in result_rows)
    all_admissible = complete and all(r.get("admissible") for r in result_rows)
    summary = {
        "run_label": lock["lock_name"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "classification": "LIVE_DIAGNOSTIC_COMPLETE" if complete else "INVALID_OR_INCOMPLETE_DIAGNOSTIC",
        "run_dir": str(out_dir),
        "complete": complete,
        "all_admissible": all_admissible,
        "provider_calls": len(result_rows),
        "expected_provider_calls": 4,
        "totals": totals,
        "rows": [
            {
                "call_index": r.get("call_index"),
                "lane": r.get("lane"),
                "packet_id": r.get("packet_id"),
                "provider_call_ok": r.get("provider_call_ok"),
                "parse_ok": r.get("parse_ok"),
                "admissible": r.get("admissible"),
                "verification_verdict": (r.get("parsed_json") or {}).get("verification_verdict")
                if isinstance(r.get("parsed_json"), dict)
                else None,
                "deterministic_failures": r.get("deterministic_failures"),
                "error": r.get("error"),
                "input_tokens": r.get("input_tokens"),
                "output_tokens": r.get("output_tokens"),
                "total_tokens": r.get("total_tokens"),
            }
            for r in result_rows
        ],
    }
    (out_dir / "live_results.json").write_text(json.dumps(summary, indent=2))

    md = [
        "# MiniMax Control vs HoloVerify-V Live Diagnostic",
        "",
        f"Classification: `{summary['classification']}`",
        "",
        f"Provider calls: {len(result_rows)} / 4",
        "",
        "## Token Totals",
        "",
        "| Lane | Input | Output | Total |",
        "| --- | ---: | ---: | ---: |",
    ]
    for lane, total in totals.items():
        md.append(
            f"| `{lane}` | {total['input_tokens']} | {total['output_tokens']} | {total['total_tokens']} |"
        )
    md.extend(["", "## Rows", "", "| Call | Lane | Packet | Verdict | Admissible | Failures |"])
    md.append("| ---: | --- | --- | --- | --- | --- |")
    for r in summary["rows"]:
        md.append(
            f"| {r['call_index']} | `{r['lane']}` | `{r['packet_id']}` | `{r['verification_verdict']}` | {r['admissible']} | {r.get('deterministic_failures') or r.get('error') or []} |"
        )
    (out_dir / "live_summary.md").write_text("\n".join(md) + "\n")

    print(json.dumps(summary, indent=2))
    return 0 if complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
