"""No-provider blind HoloVerify runner prototype.

This module implements the contract in ``blind_lane_suite.runner_contract``.
It is deliberately small: the first job is to make the runtime firewall
testable before live providers or frozen benchmark packets are attached.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable, Iterable


SELECTOR_CRITERIA = (
    "gate_passed",
    "parse_valid",
    "source_ids_valid",
    "required_sections_present",
    "contradiction_free",
    "sections_present",
    "cited_evidence_count",
    "earliest_turn",
)

BUDGET_LIMITS = {
    "max_worker_turns_per_packet": 3,
    "max_calls_per_packet": 5,
    "transport_retry_limit": 1,
    "max_output_tokens": 1024,
}

WORKER_ROLES = ("W1", "W2", "W3")
GOV_ROLES = ("G1", "G2")
REQUIRED_WORKER_KEYS = (
    "worker_role",
    "verification_verdict",
    "action_boundary",
    "binding_class",
    "cited_evidence",
    "final_answer",
)
REQUIRED_GOV_KEYS = (
    "route_verdict",
    "repair_target",
    "blocked_move",
)


class BlindRunnerTransportFailure(RuntimeError):
    """Raised when a fixture transport cannot produce a worker output."""


class BlindRunnerContentFailure(RuntimeError):
    """Raised when provider transport succeeds but content violates contract."""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parse_key_value(text: str) -> dict:
    parsed: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            parsed[key] = value.strip()
    return parsed


def _source_ids(payload: dict) -> set[str]:
    return {
        str(doc.get("doc_id"))
        for doc in payload.get("documents", [])
        if isinstance(doc, dict) and doc.get("doc_id")
    }


def _split_ids(value: str) -> list[str]:
    return [part.strip() for part in value.replace(",", "|").split("|") if part.strip()]


def _build_worker_messages(payload: dict, turn_index: int, state: dict, baton: dict) -> list[dict]:
    docs = payload.get("documents", [])
    doc_lines = [
        f"{doc.get('doc_id')}: {doc.get('text')}"
        for doc in docs
        if isinstance(doc, dict)
    ]
    role = WORKER_ROLES[turn_index - 1]
    system_lines = [
        "SYSTEM ROLE: HoloVerify blind worker.",
        "OUTPUT FIREWALL: emit compact_key_value_v1 only.",
        "Do not emit hidden thinking, analysis, markdown, JSON, bullets, or prose.",
        f"The first output characters must be exactly: worker_role={role}",
    ]
    if role == "W3":
        system_lines.extend(
            [
                "FINAL COMPILER STRICT MODE.",
                "Do not explain your reasoning before the fields.",
                "Keep each field short enough to complete before the output limit.",
                "Your entire response must be the required key=value lines and nothing else.",
            ]
        )
    system_content = "\n".join(system_lines)
    content = "\n".join(
        [
            "GOV ROUTING LENS: use only source support, unresolved dependencies, and internal consistency.",
            f"RUN LOCK: packet={payload.get('packet_id')} turn={turn_index} role={role}",
            "TASK CONTRACT: return compact_key_value_v1 only. No Markdown. No prose. No bullets. No JSON. No hidden thinking.",
            "REQUIRED OUTPUT LINES EXACTLY:",
            f"worker_role={role}",
            "verification_verdict=<ALLOW or ESCALATE>",
            "binding_class=<SOURCE_BOUNDARY_CLOSED or SOURCE_BOUNDARY_OPEN>",
            "action_boundary=<short source-grounded boundary statement; max 18 words>",
            "cited_evidence=<provided source IDs separated by |>",
            "open_blockers=<empty if ALLOW; blocker phrase if ESCALATE; max 12 words>",
            "final_answer=<one sentence using ALLOW or ESCALATE; max 24 words>",
            "Do not use alternate keys such as decision, boundary_closed, or action_boundary_closed.",
            "Do not omit verification_verdict.",
            f"First visible output line must be worker_role={role}.",
            "SOURCE CONTEXT:",
            "\n".join(doc_lines),
            "STATE BRIEF:",
            json.dumps(state, sort_keys=True),
            "FULL LATEST GOV BATON:",
            json.dumps(baton, sort_keys=True),
            "CURRENT TURN COMMAND: decide whether the visible source support closes the action boundary.",
        ]
    )
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": content},
    ]


def _selected_gov_baton_from_gate(gate: dict) -> dict:
    if gate.get("passed"):
        repair_target = "preserve source-grounded reasoning"
    else:
        repair_target = "repair blind structural gate failures"
    return {
        "route_verdict": "CONTINUE",
        "repair_target": repair_target,
        "blocked_move": "do not invent source IDs",
    }


def _build_gov_messages(payload: dict, worker_row: dict, state: dict) -> list[dict]:
    gate = worker_row.get("gate_result", {})
    selected = _selected_gov_baton_from_gate(gate)
    selected_lines = [f"{key}={selected[key]}" for key in REQUIRED_GOV_KEYS]
    system_content = "\n".join(
        [
            "Data formatting task.",
            "Return a plain text record with three key=value lines.",
            "Fields, in order: route_verdict, repair_target, blocked_move.",
            "Do not add headings, explanations, JSON, Markdown, or extra lines.",
            "Begin with route_verdict=.",
        ]
    )
    user_content = "\n".join(
        [
            f"packet_id={payload.get('packet_id')}",
            "status_values:",
            *selected_lines,
            "Return the three-line status record.",
        ]
    )
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


def _parse_gov_baton(raw: str, fallback_gate: dict) -> dict:
    parsed = _parse_key_value(raw)
    selected = _selected_gov_baton_from_gate(fallback_gate)
    return {
        "route_verdict": parsed.get("route_verdict", selected["route_verdict"]),
        "repair_target": parsed.get("repair_target", selected["repair_target"]),
        "blocked_move": parsed.get("blocked_move", selected["blocked_move"]),
    }


def _gate_worker_output(payload: dict, parsed: dict) -> dict:
    failures: list[str] = []
    for key in REQUIRED_WORKER_KEYS:
        if not parsed.get(key):
            failures.append(f"missing_{key}")
    if parsed.get("verification_verdict") not in {"ALLOW", "ESCALATE"}:
        failures.append("invalid_verification_verdict")
    allowed_ids = _source_ids(payload)
    cited = _split_ids(parsed.get("cited_evidence", ""))
    if not cited:
        failures.append("missing_cited_evidence")
    invented = [sid for sid in cited if sid not in allowed_ids]
    if invented:
        failures.append("invented_source_id")
    if len(parsed.get("final_answer", "").split()) < 8:
        failures.append("short_final_answer")
    open_blockers = parsed.get("open_blockers", "").strip()
    if parsed.get("verification_verdict") == "ALLOW" and open_blockers:
        failures.append("allow_with_open_blockers")
    if parsed.get("verification_verdict") == "ESCALATE" and not open_blockers:
        failures.append("escalate_without_open_blockers")
    return {
        "gate_name": "HOLOVERIFY_BLIND_STRUCTURAL_GATE_V0",
        "passed": not failures,
        "failures": failures,
        "source_id_count": len(cited),
        "invented_source_ids": invented,
    }


def _artifact_from_row(row: dict) -> dict:
    parsed = row.get("parsed", {})
    gate = row.get("gate_result", {})
    return {
        "artifact_id": row["artifact_id"],
        "verification_verdict": parsed.get("verification_verdict", "UNKNOWN"),
        "gate_passed": bool(gate.get("passed")),
        "parse_valid": bool(row.get("parse_valid")),
        "source_ids_valid": not bool(gate.get("invented_source_ids")),
        "required_sections_present": not any(
            str(f).startswith("missing_") for f in gate.get("failures", [])
        ),
        "sections_present": sum(1 for key in REQUIRED_WORKER_KEYS if parsed.get(key)),
        "cited_evidence_count": gate.get("source_id_count", 0),
        "contradiction_free": not any(
            f in {"allow_with_open_blockers", "escalate_without_open_blockers"}
            for f in gate.get("failures", [])
        ),
        "turn_index": int(row.get("turn_index") or 0),
    }


def _criteria_tuple(artifact: dict) -> tuple:
    return (
        1 if artifact.get("gate_passed") else 0,
        1 if artifact.get("parse_valid") else 0,
        1 if artifact.get("source_ids_valid") else 0,
        1 if artifact.get("required_sections_present") else 0,
        1 if artifact.get("contradiction_free") else 0,
        int(artifact.get("sections_present") or 0),
        int(artifact.get("cited_evidence_count") or 0),
        -int(artifact.get("turn_index") or 0),
    )


def apply_criteria(artifacts: list[dict]) -> dict:
    if not artifacts:
        return {"selected_artifact_id": None, "criteria_trace": []}
    scored = [
        {
            "artifact_id": artifact.get("artifact_id"),
            "criteria": _criteria_tuple(artifact),
        }
        for artifact in artifacts
    ]
    selected = max(artifacts, key=_criteria_tuple)
    return {
        "selected_artifact_id": selected.get("artifact_id"),
        "criteria_trace": scored,
    }


def select_final(artifacts: list[dict]) -> dict:
    return apply_criteria(artifacts)


def _next_transcript(transcripts: Iterable[str], index: int) -> str:
    values = list(transcripts)
    if index >= len(values):
        raise BlindRunnerTransportFailure(f"missing fixture transcript for worker {index + 1}")
    return values[index]


def _call_transport(transport: Callable, messages: list[dict], retry_log: list[dict]) -> str:
    limit = BUDGET_LIMITS["transport_retry_limit"]
    for attempt in range(limit + 1):
        try:
            return transport(messages)
        except BlindRunnerContentFailure:
            raise
        except Exception as exc:
            if attempt >= limit:
                raise BlindRunnerTransportFailure(str(exc)) from exc
            retry_log.append({"kind": "transport", "attempt": attempt + 1})
    raise BlindRunnerTransportFailure("transport exhausted")


def _write_prompt(prompt_dir: Path, name: str, messages: list[dict]) -> None:
    prompt_dir.mkdir(parents=True, exist_ok=True)
    payload = {"messages": messages}
    (prompt_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def run_blind_fixture(
    payload: dict,
    transcripts: list[str],
    out_dir: str,
    transport=None,
    call_gov_transport: bool = False,
) -> dict:
    out_path = Path(out_dir)
    prompt_dir = out_path / "prompts"
    packet_id = str(payload.get("packet_id", "PKT-OPAQUE"))
    state = {
        "packet_id": packet_id,
        "turns_completed": [],
        "unresolved_dependencies": [],
        "blocked_moves": [],
    }
    baton = {
        "route_verdict": "CONTINUE",
        "repair_target": "source support and dependency closure",
        "blocked_move": "do not invent source IDs",
    }
    prompts: list[list[dict]] = []
    worker_rows: list[dict] = []
    gov_rows: list[dict] = []
    call_rows: list[dict] = []
    artifacts: list[dict] = []
    retry_log: list[dict] = []

    for idx, role in enumerate(WORKER_ROLES):
        messages = _build_worker_messages(payload, idx + 1, state, baton)
        prompts.append(messages)
        _write_prompt(prompt_dir, f"{packet_id}_{role}.json", messages)
        raw = _call_transport(transport, messages, retry_log) if transport else _next_transcript(transcripts, idx)
        parsed = _parse_key_value(raw)
        gate = _gate_worker_output(payload, parsed)
        raw_hash = _sha256_text(raw)
        row = {
            "artifact_id": f"ART-{idx + 1:03d}",
            "role": role,
            "turn_index": idx + 1,
            "raw_output_sha256": raw_hash,
            "artifact_text": raw,
            "parse_valid": bool(parsed),
            "parsed": parsed,
            "gate_result": gate,
            "gate_input_sha256": raw_hash,
            "selector_input_sha256": raw_hash,
            "scorer_input_sha256": raw_hash,
        }
        worker_rows.append(row)
        call_rows.append(
            {
                "packet_id": packet_id,
                "call_kind": "worker",
                "role": role,
                "turn_index": idx + 1,
                "prompt_sha256": _sha256_text(json.dumps(messages, sort_keys=True)),
                "raw_output_sha256": raw_hash,
                "transport_called": bool(transport),
            }
        )
        artifacts.append(_artifact_from_row(row))
        state["turns_completed"].append(
            {
                "role": role,
                "artifact_id": row["artifact_id"],
                "gate_passed": gate["passed"],
            }
        )
        if idx < len(GOV_ROLES):
            gov_messages = _build_gov_messages(payload, row, state)
            prompts.append(gov_messages)
            _write_prompt(prompt_dir, f"{packet_id}_{GOV_ROLES[idx]}.json", gov_messages)
            if call_gov_transport and transport:
                gov_raw = _call_transport(transport, gov_messages, retry_log)
                gov_hash = _sha256_text(gov_raw)
                baton = _parse_gov_baton(gov_raw, gate)
                gov_row = {
                    "packet_id": packet_id,
                    "call_kind": "gov",
                    "role": GOV_ROLES[idx],
                    "turn_index": idx + 1,
                    "prompt_sha256": _sha256_text(json.dumps(gov_messages, sort_keys=True)),
                    "raw_output_sha256": gov_hash,
                    "transport_called": True,
                    "parse_valid": bool(_parse_key_value(gov_raw)),
                }
                gov_rows.append(gov_row)
                call_rows.append(gov_row)
            else:
                baton = {
                    "route_verdict": "CONTINUE",
                    "repair_target": "repair blind structural failures" if not gate["passed"] else "preserve source-grounded reasoning",
                    "blocked_move": "do not invent source IDs",
                    "previous_gate_passed": gate["passed"],
                }

    selection = select_final(artifacts)
    selected_id = selection["selected_artifact_id"]
    selected_artifact = next((a for a in artifacts if a.get("artifact_id") == selected_id), {})
    return {
        "prompts": prompts,
        "worker_rows": worker_rows,
        "gov_rows": gov_rows,
        "call_rows": call_rows,
        "artifacts": artifacts,
        "final": {
            "verdict": selected_artifact.get("verification_verdict"),
            "artifact_id": selected_id,
        },
        "selection": selection,
        "retry_log": retry_log,
        "budget_limits": BUDGET_LIMITS,
    }


def _load_runtime_json(path: Path) -> dict:
    return json.loads(path.read_text(errors="replace"))


def run_blind_runtime_manifest(runtime_manifest_path: str, out_dir: str, transport) -> dict:
    """Execute the blind runtime over opaque runtime inputs only.

    The caller supplies provider transport. This function loads only the runtime
    manifest and its opaque payload refs, then writes frozen trace artifacts.
    """
    if transport is None:
        raise ValueError("transport is required for runtime execution")

    manifest_path = Path(runtime_manifest_path)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    manifest = _load_runtime_json(manifest_path)
    if not manifest.get("runtime_consumable"):
        raise ValueError("runtime manifest is not runtime-consumable")

    rows = manifest.get("packets") or []
    trace_rows: list[dict] = []
    packet_results: list[dict] = []
    for row in rows:
        payload_ref = Path(row["runtime_payload_ref"])
        payload = _load_runtime_json(payload_ref)
        packet_out = out_path / str(payload.get("packet_id"))
        result = run_blind_fixture(
            payload,
            [],
            str(packet_out),
            transport=transport,
            call_gov_transport=True,
        )
        packet_results.append(
            {
                "packet_id": payload.get("packet_id"),
                "final": result.get("final"),
                "retry_log": result.get("retry_log", []),
            }
        )
        for call in result.get("call_rows", []):
            trace_rows.append(call)

    trace_path = out_path / "TRACE_CALLS.jsonl"
    with trace_path.open("w", encoding="utf-8") as trace:
        for row in trace_rows:
            trace.write(json.dumps(row, sort_keys=True) + "\n")

    summary = {
        "classification": "HOLOVERIFY_BLIND_CANARY_RUNTIME_RESULT_V0",
        "runtime_manifest": str(manifest_path),
        "packet_count": len(packet_results),
        "expected_call_count": len(packet_results) * BUDGET_LIMITS["max_calls_per_packet"],
        "observed_call_count": len(trace_rows),
        "results": packet_results,
        "trace_ref": str(trace_path),
    }
    (out_path / "blind_canary_runtime_results.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary
