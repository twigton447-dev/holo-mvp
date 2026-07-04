"""No-provider blind HoloVerify runner prototype.

This module implements the contract in ``blind_lane_suite.runner_contract``.
It is deliberately small: the first job is to make the runtime firewall
testable before live providers or frozen benchmark packets are attached.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Callable, Iterable


SELECTOR_POLICY_VERSION = "SELECTOR_V5_BLOCKER_CLOSURE_VALIDATION_2026_07_04"
SELECTOR_POLICY_DECISION = (
    "Truth-blind structural selector. Among structurally valid artifacts, "
    "explicit blocker resolution is only eligible when local closure validation "
    "proves the cited source fields close the exact blocker_type. A later ALLOW "
    "cannot silently drop a prior SOURCE_BOUNDARY_OPEN blocker, and it also "
    "cannot win by textually naming a blocker_id unless deterministic code "
    "confirms the closure. A source-grounded ESCALATE blocker can defeat an "
    "ALLOW majority unless a later artifact source-closes it. Deterministic "
    "source-derived dependency and blocker-closure checks can disqualify "
    "artifacts that contradict computed source boundaries. Concise final answers "
    "are warnings, not sole disqualifiers, when the artifact is otherwise "
    "complete. Within the same blocker/consensus tier, gate-failed corroboration "
    "from otherwise usable artifacts is considered before citation count and "
    "earliest-turn tie-breaks."
)
SELECTOR_CRITERIA = (
    "gate_passed",
    "parse_valid",
    "source_ids_valid",
    "required_sections_present",
    "contradiction_free",
    "deterministic_clean",
    "blocker_resolution_clean",
    "blocker_resolution_complete",
    "closure_validation_clean",
    "all_prior_blockers_source_closed",
    "invalid_closure_count",
    "unresolved_blocker_count",
    "source_boundary_open_with_blocker",
    "verdict_consensus_count",
    "final_turn_consensus_repair",
    "verdict_corroboration_count",
    "sections_present",
    "cited_evidence_count",
    "earliest_turn",
)

WORKER_CONTRACT_VERSION = "WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04"
W3_ARTIFACT_FIRST_GUARD = (
    "W3 ARTIFACT-FIRST CONTRACT V4.",
    "Start immediately with worker_role=W3 before any reasoning.",
    "Never output <think>, hidden reasoning, analysis, or deliberation.",
    "If the source seam is ambiguous, encode that only in verification_verdict, binding_class, open_blockers, blocker_type, blocker_resolution, structured_blocker_resolution, and final_answer.",
    "If any prior blocker exists, do not return ALLOW unless blocker_resolution names each blocker_id, structured_blocker_resolution cites source evidence, and the source fields close the blocker_type.",
    "Do not debate competing interpretations outside the key=value fields.",
    "Emit exactly the required key=value artifact lines, then stop.",
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
    "blocker_type",
    "blocker_resolution",
    "structured_blocker_resolution",
)
REQUIRED_GOV_KEYS = (
    "route_verdict",
    "repair_target",
    "blocked_move",
)
RUN_DATE_ISO = "2026-07-03"
SOFT_GATE_FAILURES = {"short_final_answer"}


class BlindRunnerTransportFailure(RuntimeError):
    """Raised when a fixture transport cannot produce a worker output."""


class BlindRunnerContentFailure(RuntimeError):
    """Raised when provider transport succeeds but content violates contract."""


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def selector_policy_identity() -> dict:
    payload = {
        "selector_policy_version": SELECTOR_POLICY_VERSION,
        "selector_policy_decision": SELECTOR_POLICY_DECISION,
        "selector_criteria": list(SELECTOR_CRITERIA),
    }
    return {
        **payload,
        "selector_policy_sha256": _sha256_text(json.dumps(payload, sort_keys=True)),
    }


def worker_contract_identity() -> dict:
    payload = {
        "worker_contract_version": WORKER_CONTRACT_VERSION,
        "w3_artifact_first_guard": list(W3_ARTIFACT_FIRST_GUARD),
        "required_worker_keys": list(REQUIRED_WORKER_KEYS),
    }
    return {
        **payload,
        "worker_contract_sha256": _sha256_text(json.dumps(payload, sort_keys=True)),
    }


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


def _source_record_fields(payload: dict) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for doc in payload.get("documents", []):
        if not isinstance(doc, dict):
            continue
        doc_id = str(doc.get("doc_id") or "")
        if not doc_id:
            continue
        text = _doc_text(doc)
        fields: dict[str, str] = {"_doc_id": doc_id, "_text": text}
        parts = [part.strip() for part in text.split("|") if part.strip()]
        if parts:
            fields["_record_type"] = parts[0]
        for part in parts[1:]:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            fields[key.strip()] = value.strip()
        records[doc_id] = fields
    return records


def _split_ids(value: str) -> list[str]:
    return [part.strip() for part in value.replace(",", "|").split("|") if part.strip()]


def _split_pipe_values(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split("|") if part.strip()]


def _split_semantic_values(value: str) -> list[str]:
    normalized = str(value or "").replace(",", "|").replace(";", "|")
    return [part.strip() for part in normalized.split("|") if part.strip()]


def _normalize_value(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _float_value(value: object) -> float | None:
    text = str(value or "").strip().replace(",", "")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return None
    return float(match.group(1))


def _request_fields(payload: dict) -> dict:
    for fields in _source_record_fields(payload).values():
        if fields.get("_record_type") == "REQ":
            return fields
    return {}


def _policy_text(payload: dict) -> str:
    return "\n".join(
        _doc_text(doc)
        for doc in payload.get("documents", [])
        if isinstance(doc, dict)
        and ("POL" in _doc_id(doc).upper() or _doc_text(doc).strip().upper().startswith("POL|"))
    )


def _packet_policy_status(payload: dict) -> dict:
    """Classify packet policy visibility from runtime-visible sources only."""
    text = _policy_text(payload).lower()
    req = _request_fields(payload)
    action_type = _normalize_value(req.get("action_type"))
    if action_type == "payment_rail_change" and "payment rail execution" in text:
        has_approval_requirement = "approval" in text or "approver" in text
        has_callback_requirement = "callback" in text
        if not has_approval_requirement and not has_callback_requirement:
            return {
                "status": "SOURCE_POLICY_UNDERSPECIFIED",
                "reason": "payment rail policy does not source-state approval or callback closure fields",
            }
    return {"status": "SOURCE_POLICY_SPECIFIED", "reason": "policy exposes deterministic closure fields"}


def _blocker_id(artifact_id: str, blocker_text: str) -> str:
    digest = hashlib.sha256(f"{artifact_id}|{blocker_text}".encode("utf-8")).hexdigest()[:8].upper()
    return f"{artifact_id}-BLK-{digest}"


def _closure_requirements_for_blocker(blocker_type: str, blocker_text: str, payload: dict) -> dict:
    req = _request_fields(payload)
    policy = _policy_text(payload).lower()
    blocker_type = _normalize_value(blocker_type).upper()
    requirements: dict[str, object] = {}
    if blocker_type == "TRANSACTION_TYPE_APPROVAL_MISMATCH":
        requirements["transaction_type"] = req.get("transaction_type")
    elif blocker_type == "ACTION_TYPE_APPROVAL_MISMATCH":
        requirements["action_type"] = req.get("action_type")
    elif blocker_type == "SCOPE_MISMATCH":
        if "payment_release scope" in policy:
            requirements["scope_code"] = "payment_release"
        elif req.get("action_type"):
            requirements["scope_code"] = req.get("action_type")
    elif blocker_type == "AMOUNT_LIMIT_MISSING":
        requirements["amount"] = req.get("amount")
    elif blocker_type == "ADD_ON_SCOPE_MISMATCH":
        requirements["add_on"] = req.get("add_on")
        requirements["scope_code_not"] = "renewal"
    elif blocker_type == "CALLBACK_FIELD_MISSING":
        if req.get("rail_token"):
            requirements["rail_token"] = req.get("rail_token")
    elif blocker_type == "SOURCE_POLICY_UNDERSPECIFIED":
        requirements["packet_policy_status"] = "SOURCE_POLICY_SPECIFIED"
    else:
        requirements["blocker_text"] = blocker_text
    return {key: value for key, value in requirements.items() if value not in (None, "")}


def _infer_blocker_type(blocker_text: str, payload: dict) -> str:
    text = blocker_text.lower()
    if "transaction_type" in text or "tx approval" in text or "transaction approval" in text:
        return "TRANSACTION_TYPE_APPROVAL_MISMATCH"
    if "amount limit" in text or "limit absent" in text:
        return "AMOUNT_LIMIT_MISSING"
    if "payment_release scope" in text or "scope" in text:
        return "SCOPE_MISMATCH"
    if "add_on" in text or "add-on" in text:
        return "ADD_ON_SCOPE_MISMATCH"
    if "callback" in text:
        return "CALLBACK_FIELD_MISSING"
    if _packet_policy_status(payload)["status"] == "SOURCE_POLICY_UNDERSPECIFIED":
        return "SOURCE_POLICY_UNDERSPECIFIED"
    return "SOURCE_BOUNDARY_OPEN"


def _blockers_from_parsed(row: dict, parsed: dict, payload: dict) -> list[dict]:
    verdict = parsed.get("verification_verdict")
    binding = parsed.get("binding_class")
    if verdict != "ESCALATE" or binding != "SOURCE_BOUNDARY_OPEN":
        return []
    blockers = _split_pipe_values(parsed.get("open_blockers", ""))
    blocker_types = _split_semantic_values(parsed.get("blocker_type", ""))
    cited = _split_ids(parsed.get("cited_evidence", ""))
    result: list[dict] = []
    for idx, blocker in enumerate(blockers):
        blocker_type = (
            blocker_types[idx]
            if idx < len(blocker_types)
            else blocker_types[0]
            if len(blocker_types) == 1
            else _infer_blocker_type(blocker, payload)
        )
        result.append(
            {
                "blocker_id": _blocker_id(str(row.get("artifact_id")), blocker),
                "blocker_text": blocker,
                "blocker_type": blocker_type,
                "required_closure_fields": _closure_requirements_for_blocker(blocker_type, blocker, payload),
                "source_artifact_id": row.get("artifact_id"),
                "source_role": row.get("role"),
                "source_turn_index": row.get("turn_index"),
                "cited_evidence": cited,
            }
        )
    return result


def _resolution_source_ids(parsed: dict, allowed_ids: set[str]) -> list[str]:
    text = "\n".join(
        [
            str(parsed.get("blocker_resolution") or ""),
            str(parsed.get("structured_blocker_resolution") or ""),
        ]
    )
    return [source_id for source_id in sorted(allowed_ids) if source_id and source_id in text]


def _matching_cited_records(payload: dict, source_ids: list[str]) -> list[dict]:
    fields_by_id = _source_record_fields(payload)
    return [fields_by_id[source_id] for source_id in source_ids if source_id in fields_by_id]


def _source_has_amount_limit(fields: dict, requested_amount: object) -> bool:
    requested = _float_value(requested_amount)
    if requested is None:
        return False
    for key in ("limit", "amount_limit", "approved_limit"):
        if key not in fields:
            continue
        value = _normalize_value(fields.get(key))
        if value in {"not_applicable", "na", "n/a", "none"}:
            return False
        numeric = _float_value(fields.get(key))
        if numeric is not None and numeric >= requested:
            return True
    return False


def _validate_blocker_closure(payload: dict, blocker: dict, resolution_source_ids: list[str]) -> dict:
    blocker_id = str(blocker.get("blocker_id") or "")
    blocker_type = _normalize_value(blocker.get("blocker_type")).upper()
    requirements = dict(blocker.get("required_closure_fields") or {})
    records = _matching_cited_records(payload, resolution_source_ids)
    failures: list[str] = []
    if not records:
        return {
            "blocker_id": blocker_id,
            "blocker_type": blocker.get("blocker_type"),
            "status": "INVALID_CLOSURE",
            "failure_codes": ["blocker_resolution_missing_source_id"],
            "failures": ["no cited runtime source id appears in blocker_resolution or structured_blocker_resolution"],
            "cited_source_ids": resolution_source_ids,
        }
    if blocker_type == "TRANSACTION_TYPE_APPROVAL_MISMATCH":
        required = _normalize_value(requirements.get("transaction_type"))
        if not required or not any(_normalize_value(row.get("transaction_type")) == required for row in records):
            failures.append("wrong_transaction_type")
    elif blocker_type == "ACTION_TYPE_APPROVAL_MISMATCH":
        required = _normalize_value(requirements.get("action_type"))
        if not required or not any(_normalize_value(row.get("action_type")) == required for row in records):
            failures.append("wrong_action_type")
    elif blocker_type == "SCOPE_MISMATCH":
        required = _normalize_value(requirements.get("scope_code"))
        if not required or not any(_normalize_value(row.get("scope_code")) == required for row in records):
            failures.append("wrong_scope_code")
    elif blocker_type == "AMOUNT_LIMIT_MISSING":
        if not any(_source_has_amount_limit(row, requirements.get("amount")) for row in records):
            failures.append("missing_amount_limit")
    elif blocker_type == "ADD_ON_SCOPE_MISMATCH":
        add_on = _normalize_value(requirements.get("add_on"))
        banned_scope = _normalize_value(requirements.get("scope_code_not"))
        if not any(
            _normalize_value(row.get("add_on")) == add_on
            or (
                add_on
                and _normalize_value(row.get("scope_code")) not in {"", banned_scope}
                and banned_scope
            )
            for row in records
        ):
            failures.append("wrong_add_on_scope")
    elif blocker_type == "CALLBACK_FIELD_MISSING":
        rail_token = _normalize_value(requirements.get("rail_token"))
        if not any(_normalize_value(row.get("rail_token")) == rail_token for row in records):
            failures.append("callback_field_missing")
    elif blocker_type == "SOURCE_POLICY_UNDERSPECIFIED":
        if _packet_policy_status(payload)["status"] != "SOURCE_POLICY_SPECIFIED":
            failures.append("source_policy_underspecified")
    if failures:
        return {
            "blocker_id": blocker_id,
            "blocker_type": blocker.get("blocker_type"),
            "status": "INVALID_CLOSURE",
            "failure_codes": failures,
            "failures": failures,
            "cited_source_ids": resolution_source_ids,
            "required_closure_fields": requirements,
        }
    return {
        "blocker_id": blocker_id,
        "blocker_type": blocker.get("blocker_type"),
        "status": "CLOSED",
        "failure_codes": [],
        "failures": [],
        "cited_source_ids": resolution_source_ids,
        "required_closure_fields": requirements,
    }


def _resolve_prior_blockers(
    payload: dict,
    active_blockers: list[dict],
    parsed: dict,
    cited: list[str],
) -> tuple[list[dict], list[dict], list[str], list[dict]]:
    if not active_blockers:
        return [], [], [], []
    resolution = str(parsed.get("blocker_resolution") or "")
    verdict = parsed.get("verification_verdict")
    if verdict != "ALLOW":
        return [], list(active_blockers), [], []
    resolution_sources = _resolution_source_ids(parsed, _source_ids(payload))
    resolved: list[dict] = []
    unresolved: list[dict] = []
    failures: list[str] = []
    closure_results: list[dict] = []
    for blocker in active_blockers:
        blocker_id = str(blocker.get("blocker_id") or "")
        if blocker_id and blocker_id in resolution:
            closure = _validate_blocker_closure(payload, blocker, resolution_sources)
            closure_results.append(closure)
            if closure.get("status") == "CLOSED":
                resolved.append(blocker)
            else:
                unresolved.append(blocker)
                failure_keys: list[str] = []
                for code in closure.get("failure_codes") or []:
                    failure_key = f"invalid_blocker_closure:{blocker_id}:{code}"
                    failure_keys.append(failure_key)
                    failures.append(failure_key)
                closure["failure_keys"] = failure_keys
        else:
            unresolved.append(blocker)
            failures.append(f"unresolved_prior_blocker:{blocker_id}")
    if any(str(blocker.get("blocker_id") or "") in resolution for blocker in active_blockers) and not resolution_sources:
        failures.append("blocker_resolution_missing_source_id")
    return resolved, unresolved, failures, closure_results


def _money_values(text: str) -> list[float]:
    values: list[float] = []
    for match in re.finditer(r"\bUSD\s*([0-9][0-9,]*(?:\.[0-9]+)?)\b", text, flags=re.IGNORECASE):
        values.append(float(match.group(1).replace(",", "")))
    return values


def _time_to_minutes(value: str) -> int:
    hour, minute = value.split(":", 1)
    return int(hour) * 60 + int(minute)


def _date_value(value: str):
    from datetime import date

    year, month, day = (int(part) for part in value.split("-"))
    return date(year, month, day)


def _source_documents(payload: dict) -> list[dict]:
    return [doc for doc in payload.get("documents", []) if isinstance(doc, dict)]


def _doc_text(doc: dict) -> str:
    return str(doc.get("text") or doc.get("content") or "")


def _doc_id(doc: dict) -> str:
    return str(doc.get("doc_id") or "")


def _dependency_check(
    check_id: str,
    required_verdict: str,
    summary: str,
    evidence: list[str],
    computed: dict,
) -> dict:
    return {
        "check_id": check_id,
        "required_verdict": required_verdict,
        "summary": summary,
        "evidence": evidence,
        "computed": computed,
    }


def _deterministic_dependency_checks(payload: dict) -> list[dict]:
    """Source-derived checks for computable action-boundary seams.

    These checks use only model-visible source text. They do not read packet
    truth, sibling labels, scoring maps, or legacy IDs.
    """
    docs = _source_documents(payload)
    checks: list[dict] = []

    refund_request = next(
        (
            doc
            for doc in docs
            if "refund request" in _doc_text(doc).lower()
            and (" asks to issue " in _doc_text(doc).lower() or " asks to release " in _doc_text(doc).lower())
            and _money_values(_doc_text(doc))
        ),
        None,
    )
    original_charge = next(
        (
            doc
            for doc in docs
            if "original charge" in _doc_text(doc).lower()
            and _money_values(_doc_text(doc))
        ),
        None,
    )
    prior_refund_docs = [
        doc
        for doc in docs
        if ("prior refund" in _doc_text(doc).lower() or "refund ledger" in _doc_text(doc).lower())
        and _money_values(_doc_text(doc))
    ]
    if refund_request and original_charge and prior_refund_docs:
        requested = _money_values(_doc_text(refund_request))[0]
        original = _money_values(_doc_text(original_charge))[0]
        prior = sum(_money_values(_doc_text(doc))[0] for doc in prior_refund_docs)
        remaining = original - prior
        required = "ALLOW" if requested <= remaining else "ESCALATE"
        checks.append(
            _dependency_check(
                "refund_remaining_balance",
                required,
                f"requested USD {requested:g} vs remaining USD {remaining:g}",
                [_doc_id(refund_request), _doc_id(original_charge), *[_doc_id(doc) for doc in prior_refund_docs]],
                {"requested": requested, "original": original, "prior_refunds": prior, "remaining": remaining},
            )
        )

    tolerance_request = next(
        (
            doc
            for doc in docs
            if "refund exception" in _doc_text(doc).lower()
            and (" asks to release " in _doc_text(doc).lower() or " asks to issue " in _doc_text(doc).lower())
            and _money_values(_doc_text(doc))
        ),
        None,
    )
    calculation_doc = next(
        (
            doc
            for doc in docs
            if "calculation" in _doc_text(doc).lower()
            and ("computes" in _doc_text(doc).lower() or "calculated" in _doc_text(doc).lower())
            and _money_values(_doc_text(doc))
        ),
        None,
    )
    tolerance_doc = next(
        (
            doc
            for doc in docs
            if "tolerance" in _doc_text(doc).lower()
            and _money_values(_doc_text(doc))
        ),
        None,
    )
    if tolerance_request and calculation_doc and tolerance_doc:
        requested = _money_values(_doc_text(tolerance_request))[0]
        calculated = _money_values(_doc_text(calculation_doc))[0]
        tolerance = _money_values(_doc_text(tolerance_doc))[0]
        variance = abs(requested - calculated)
        required = "ALLOW" if variance <= tolerance else "ESCALATE"
        checks.append(
            _dependency_check(
                "tolerance_delta",
                required,
                f"variance USD {variance:.2f} vs tolerance USD {tolerance:.2f}",
                [_doc_id(tolerance_request), _doc_id(calculation_doc), _doc_id(tolerance_doc)],
                {"requested": requested, "calculated": calculated, "variance": variance, "tolerance": tolerance},
            )
        )

    request_time_doc = next(
        (
            doc
            for doc in docs
            if "execute" in _doc_text(doc).lower()
            and re.search(r"\b[0-2][0-9]:[0-5][0-9]Z\b", _doc_text(doc))
        ),
        None,
    )
    window_doc = next(
        (
            doc
            for doc in docs
            if "authorizes" in _doc_text(doc).lower()
            and re.search(r"from\s+([0-2]?[0-9]:[0-5][0-9])\s+to\s+([0-2]?[0-9]:[0-5][0-9])\s+ET", _doc_text(doc), flags=re.IGNORECASE)
        ),
        None,
    )
    offset_doc = next(
        (
            doc
            for doc in docs
            if "ET equals UTC-4" in _doc_text(doc)
        ),
        None,
    )
    if request_time_doc and window_doc and offset_doc:
        req_match = re.search(r"\b([0-2][0-9]:[0-5][0-9])Z\b", _doc_text(request_time_doc))
        win_match = re.search(
            r"from\s+([0-2]?[0-9]:[0-5][0-9])\s+to\s+([0-2]?[0-9]:[0-5][0-9])\s+ET",
            _doc_text(window_doc),
            flags=re.IGNORECASE,
        )
        if req_match and win_match:
            request_minutes = _time_to_minutes(req_match.group(1))
            start_utc = _time_to_minutes(win_match.group(1)) + 4 * 60
            end_utc = _time_to_minutes(win_match.group(2)) + 4 * 60
            inside = start_utc <= request_minutes <= end_utc
            required = "ALLOW" if inside else "ESCALATE"
            checks.append(
                _dependency_check(
                    "timezone_window",
                    required,
                    f"request minute {request_minutes} vs UTC window {start_utc}-{end_utc}",
                    [_doc_id(request_time_doc), _doc_id(window_doc), _doc_id(offset_doc)],
                    {"request_minutes_utc": request_minutes, "window_start_utc": start_utc, "window_end_utc": end_utc},
                )
            )

    policy_12m = any("senior authorization inside the 12-month review cycle" in _doc_text(doc).lower() for doc in docs)
    auth_doc = next(
        (
            doc
            for doc in docs
            if "senior risk authorization" in _doc_text(doc).lower()
            and re.search(r"\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b", _doc_text(doc))
        ),
        None,
    )
    if policy_12m and auth_doc:
        from datetime import timedelta

        match = re.search(r"\b(20[0-9]{2}-[0-9]{2}-[0-9]{2})\b", _doc_text(auth_doc))
        if match:
            run_date = _date_value(RUN_DATE_ISO)
            auth_date = _date_value(match.group(1))
            age_days = (run_date - auth_date).days
            required = "ALLOW" if age_days <= 365 else "ESCALATE"
            cutoff = run_date - timedelta(days=365)
            checks.append(
                _dependency_check(
                    "senior_authorization_12m",
                    required,
                    f"authorization age {age_days} days vs 365-day limit",
                    [_doc_id(auth_doc)],
                    {"run_date": RUN_DATE_ISO, "authorization_date": match.group(1), "cutoff_date": cutoff.isoformat(), "age_days": age_days},
                )
            )

    return checks


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
        system_lines.extend(W3_ARTIFACT_FIRST_GUARD)
    system_content = "\n".join(system_lines)
    content_lines = [
        f"GOV ROUTING LENS: {baton.get('repair_target', 'use source support')} | blocked_move={baton.get('blocked_move', 'do not invent source IDs')}",
        f"RUN LOCK: packet={payload.get('packet_id')} turn={turn_index} role={role}",
        "TASK CONTRACT: return compact_key_value_v1 only. No Markdown. No prose. No bullets. No JSON. No hidden thinking.",
    ]
    if role == "W3":
        content_lines.extend(
            [
                "W3 ARTIFACT-FIRST GUARD:",
                "Your first visible output line must be worker_role=W3.",
                "If uncertain, still emit the compact artifact immediately.",
                "Represent ambiguity only with verification_verdict, binding_class, open_blockers, blocker_type, blocker_resolution, structured_blocker_resolution, and final_answer.",
                "If prior blockers exist, preserve ESCALATE or close every blocker_id with structured source fields.",
                "Do not write explanatory analysis before or after the artifact.",
            ]
        )
    active_blockers = state.get("unresolved_blockers") or []
    content_lines.extend(
        [
            "REQUIRED OUTPUT LINES EXACTLY:",
            f"worker_role={role}",
            "verification_verdict=<ALLOW or ESCALATE>",
            "binding_class=<SOURCE_BOUNDARY_CLOSED or SOURCE_BOUNDARY_OPEN>",
            "action_boundary=<short source-grounded boundary statement; max 18 words>",
            "cited_evidence=<provided source IDs separated by |>",
            "open_blockers=<empty if ALLOW; blocker phrase if ESCALATE; max 12 words>",
            "blocker_type=<empty if ALLOW; if ESCALATE, blocker type such as SCOPE_MISMATCH or AMOUNT_LIMIT_MISSING>",
            "blocker_resolution=<empty if no prior blockers or ESCALATE; if ALLOW after blockers, list each blocker_id closed plus source IDs>",
            "structured_blocker_resolution=<empty if no prior blockers or ESCALATE; if ALLOW after blockers, list blocker_id, blocker_type, cited source IDs, and closure fields>",
            "final_answer=<one sentence using ALLOW or ESCALATE; max 24 words>",
            "Do not use alternate keys such as decision, boundary_closed, or action_boundary_closed.",
            "Do not omit verification_verdict.",
            "If ACTIVE BLOCKER LEDGER is non-empty and you return ALLOW, blocker_resolution and structured_blocker_resolution must name every blocker_id and source fields that close it.",
            f"First visible output line must be worker_role={role}.",
            "SOURCE CONTEXT:",
            "\n".join(doc_lines),
            "ACTIVE BLOCKER LEDGER:",
            json.dumps(active_blockers, sort_keys=True),
            "DETERMINISTIC DEPENDENCY LEDGER:",
            json.dumps(baton.get("dependency_ledger", []), sort_keys=True),
            "STATE BRIEF:",
            json.dumps(state, sort_keys=True),
            "FULL LATEST GOV BATON:",
            json.dumps(baton, sort_keys=True),
            "INVALID CLOSURE LEDGER:",
            json.dumps(baton.get("invalid_closure_ledger", []), sort_keys=True),
            "CURRENT TURN COMMAND: decide whether the visible source support closes the action boundary.",
        ]
    )
    content = "\n".join(content_lines)
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": content},
    ]


def _selected_gov_baton_from_gate(gate: dict) -> dict:
    dependency_checks = gate.get("deterministic_dependency_checks") or []
    dependency_failures = gate.get("deterministic_dependency_failures") or []
    closure_failures = gate.get("closure_validation_failures") or []
    prior_unresolved = gate.get("unresolved_prior_blockers") or []
    blockers_found = gate.get("blockers_found") or []
    if closure_failures:
        ids = ",".join(str(item.get("blocker_id")) for item in closure_failures[:3])
        repair_target = f"repair invalid blocker closure before ALLOW: {ids}"
        blocked_move = "do not accept textual blocker closure without matching source fields"
    elif prior_unresolved:
        ids = ",".join(str(blocker.get("blocker_id")) for blocker in prior_unresolved[:3])
        repair_target = f"resolve prior blocker ids before ALLOW: {ids}"
        blocked_move = "do not silently drop source-grounded blockers"
    elif blockers_found:
        ids = ",".join(str(blocker.get("blocker_id")) for blocker in blockers_found[:3])
        repair_target = f"stress-test and preserve blocker ids: {ids}"
        blocked_move = "do not override blocker with consensus unless sources close it"
    elif dependency_failures:
        first = dependency_failures[0]
        repair_target = f"resolve dependency mismatch: {first.get('summary', first.get('check_id'))}"
        blocked_move = "do not collapse separate required controls into general approval"
    elif gate.get("passed"):
        repair_target = "preserve source-grounded reasoning"
        blocked_move = "do not invent source IDs"
    else:
        repair_target = "repair blind structural gate failures"
        blocked_move = "do not invent source IDs"
    return {
        "route_verdict": "CONTINUE",
        "repair_target": repair_target,
        "blocked_move": blocked_move,
        "dependency_ledger": dependency_checks,
        "blocker_ledger": prior_unresolved or blockers_found,
        "invalid_closure_ledger": closure_failures,
        "closure_validation_failures": closure_failures,
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
        "dependency_ledger": selected.get("dependency_ledger", []),
        "blocker_ledger": selected.get("blocker_ledger", []),
        "invalid_closure_ledger": selected.get("invalid_closure_ledger", []),
        "closure_validation_failures": selected.get("closure_validation_failures", []),
    }


def _gate_worker_output(payload: dict, parsed: dict, active_blockers: list[dict] | None = None) -> dict:
    active_blockers = list(active_blockers or [])
    failures: list[str] = []
    warnings: list[str] = []
    for key in REQUIRED_WORKER_KEYS:
        optional_empty = {"blocker_resolution", "structured_blocker_resolution", "blocker_type"}
        if key not in parsed or (key not in optional_empty and not parsed.get(key)):
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
        warnings.append("short_final_answer")
    open_blockers = parsed.get("open_blockers", "").strip()
    if parsed.get("verification_verdict") == "ALLOW" and open_blockers:
        failures.append("allow_with_open_blockers")
    if parsed.get("verification_verdict") == "ESCALATE" and not open_blockers:
        failures.append("escalate_without_open_blockers")
    if parsed.get("verification_verdict") == "ESCALATE" and open_blockers and not parsed.get("blocker_type"):
        failures.append("missing_blocker_type_for_open_blocker")
    resolved_prior, unresolved_prior, blocker_failures, closure_results = _resolve_prior_blockers(
        payload,
        active_blockers,
        parsed,
        cited,
    )
    failures.extend(blocker_failures)
    closure_failures = [item for item in closure_results if item.get("status") == "INVALID_CLOSURE"]
    dependency_checks = _deterministic_dependency_checks(payload)
    dependency_failures = [
        check
        for check in dependency_checks
        if parsed.get("verification_verdict") in {"ALLOW", "ESCALATE"}
        and parsed.get("verification_verdict") != check.get("required_verdict")
    ]
    for check in dependency_failures:
        failures.append(f"deterministic_dependency_mismatch:{check['check_id']}")
    return {
        "gate_name": "HOLOVERIFY_BLIND_STRUCTURAL_GATE_V1_DEPENDENCY_AWARE",
        "passed": not failures,
        "failures": failures,
        "warnings": warnings,
        "source_id_count": len(cited),
        "invented_source_ids": invented,
        "deterministic_dependency_checks": dependency_checks,
        "deterministic_dependency_failures": dependency_failures,
        "prior_blockers_in": active_blockers,
        "resolved_prior_blockers": resolved_prior,
        "unresolved_prior_blockers": unresolved_prior,
        "closure_validation_results": closure_results,
        "closure_validation_failures": closure_failures,
        "invalid_closure_count": len(closure_failures),
        "blockers_found": [],
    }


def _artifact_from_row(row: dict) -> dict:
    parsed = row.get("parsed", {})
    gate = row.get("gate_result", {})
    failures = [str(f) for f in gate.get("failures", [])]
    verdict = parsed.get("verification_verdict", "UNKNOWN")
    invalid_closure_count = int(gate.get("invalid_closure_count") or 0)
    unresolved_prior_count = len(gate.get("unresolved_prior_blockers") or [])
    unresolved_allow_blocker_count = unresolved_prior_count if verdict == "ALLOW" else 0
    prior_blocker_count = len(gate.get("prior_blockers_in") or [])
    return {
        "artifact_id": row["artifact_id"],
        "verification_verdict": verdict,
        "gate_passed": bool(gate.get("passed")),
        "parse_valid": bool(row.get("parse_valid")),
        "source_ids_valid": not bool(gate.get("invented_source_ids")),
        "required_sections_present": not any(
            failure.startswith("missing_") for failure in failures
        ),
        "sections_present": sum(1 for key in REQUIRED_WORKER_KEYS if parsed.get(key)),
        "cited_evidence_count": gate.get("source_id_count", 0),
        "contradiction_free": not any(
            f in {"allow_with_open_blockers", "escalate_without_open_blockers"}
            for f in failures
        ),
        "deterministic_clean": not any(failure.startswith("deterministic_dependency_mismatch:") for failure in failures),
        "blocker_resolution_clean": not any(
            failure.startswith("unresolved_prior_blocker:")
            or failure == "blocker_resolution_missing_source_id"
            or failure.startswith("invalid_blocker_closure:")
            for failure in failures
        ),
        "closure_validation_clean": invalid_closure_count == 0,
        "all_prior_blockers_source_closed": bool(
            verdict != "ALLOW" or prior_blocker_count == 0 or (unresolved_prior_count == 0 and invalid_closure_count == 0)
        ),
        "invalid_closure_count": invalid_closure_count,
        "unresolved_blocker_count": unresolved_allow_blocker_count,
        "prior_blocker_count": prior_blocker_count,
        "resolved_prior_blocker_count": len(gate.get("resolved_prior_blockers") or []),
        "unresolved_prior_blocker_count": unresolved_prior_count,
        "blockers_found_count": len(gate.get("blockers_found") or []),
        "source_boundary_open_with_blocker": bool(
            verdict == "ESCALATE"
            and parsed.get("binding_class") == "SOURCE_BOUNDARY_OPEN"
            and gate.get("blockers_found")
        ),
        "blocker_resolution_complete": bool(
            gate.get("prior_blockers_in")
            and not gate.get("unresolved_prior_blockers")
            and invalid_closure_count == 0
            and verdict == "ALLOW"
        ),
        "soft_gate_valid": not any(failure not in SOFT_GATE_FAILURES for failure in failures),
        "turn_index": int(row.get("turn_index") or 0),
    }


def _criteria_tuple(artifact: dict) -> tuple:
    return (
        1 if artifact.get("gate_passed") else 0,
        1 if artifact.get("parse_valid") else 0,
        1 if artifact.get("source_ids_valid") else 0,
        1 if artifact.get("required_sections_present") else 0,
        1 if artifact.get("contradiction_free") else 0,
        1 if artifact.get("deterministic_clean", True) else 0,
        1 if artifact.get("blocker_resolution_clean", True) else 0,
        1 if artifact.get("blocker_resolution_complete") else 0,
        1 if artifact.get("closure_validation_clean", True) else 0,
        1 if artifact.get("all_prior_blockers_source_closed", True) else 0,
        -int(artifact.get("invalid_closure_count") or 0),
        -int(artifact.get("unresolved_blocker_count") or 0),
        1 if artifact.get("source_boundary_open_with_blocker") else 0,
        int(artifact.get("verdict_consensus_count") or 0),
        1 if artifact.get("final_turn_consensus_repair") else 0,
        int(artifact.get("verdict_corroboration_count") or 0),
        int(artifact.get("sections_present") or 0),
        int(artifact.get("cited_evidence_count") or 0),
        -int(artifact.get("turn_index") or 0),
    )


def _selector_structurally_valid(artifact: dict) -> bool:
    return all(
        (
            artifact.get("gate_passed"),
            artifact.get("parse_valid"),
            artifact.get("source_ids_valid"),
            artifact.get("required_sections_present"),
            artifact.get("contradiction_free"),
            artifact.get("deterministic_clean", True),
            artifact.get("blocker_resolution_clean", True),
            artifact.get("closure_validation_clean", True),
            artifact.get("all_prior_blockers_source_closed", True),
        )
    )


def _selector_corroborative(artifact: dict) -> bool:
    return all(
        (
            artifact.get("parse_valid"),
            artifact.get("source_ids_valid"),
            artifact.get("required_sections_present"),
            artifact.get("contradiction_free"),
            artifact.get("deterministic_clean", True),
            artifact.get("blocker_resolution_clean", True),
            artifact.get("closure_validation_clean", True),
            artifact.get("all_prior_blockers_source_closed", True),
        )
    )


def _with_selector_derived_fields(artifacts: list[dict]) -> list[dict]:
    verdict_counts: dict[str, int] = {}
    valid_artifacts = [artifact for artifact in artifacts if _selector_structurally_valid(artifact)]
    for artifact in valid_artifacts:
        verdict = str(artifact.get("verification_verdict") or "")
        if verdict in {"ALLOW", "ESCALATE"}:
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
    corroboration_counts: dict[str, int] = {}
    corroborative_artifacts = [artifact for artifact in artifacts if _selector_corroborative(artifact)]
    for artifact in corroborative_artifacts:
        verdict = str(artifact.get("verification_verdict") or "")
        if verdict in {"ALLOW", "ESCALATE"}:
            corroboration_counts[verdict] = corroboration_counts.get(verdict, 0) + 1

    turn_indexes = [int(artifact.get("turn_index") or 0) for artifact in artifacts]
    final_turn = max(turn_indexes or [0])
    enriched: list[dict] = []
    for artifact in artifacts:
        item = dict(artifact)
        verdict = str(item.get("verification_verdict") or "")
        item["verdict_consensus_count"] = verdict_counts.get(verdict, 0)
        item["verdict_corroboration_count"] = corroboration_counts.get(verdict, 0)
        turn_index = int(item.get("turn_index") or 0)
        prior = [candidate for candidate in valid_artifacts if int(candidate.get("turn_index") or 0) < turn_index]
        prior_any = [candidate for candidate in artifacts if int(candidate.get("turn_index") or 0) < turn_index]
        prior_same = any(candidate.get("verification_verdict") == verdict for candidate in prior)
        prior_different = any(candidate.get("verification_verdict") != verdict for candidate in prior_any)
        item["final_turn_consensus_repair"] = bool(
            _selector_structurally_valid(item)
            and turn_index > 0
            and turn_index == final_turn
            and item["verdict_consensus_count"] >= 2
            and prior_same
            and prior_different
        )
        enriched.append(item)
    return enriched


def apply_criteria(artifacts: list[dict]) -> dict:
    if not artifacts:
        return {"selected_artifact_id": None, "criteria_trace": []}
    enriched = _with_selector_derived_fields(artifacts)
    scored = [
        {
            "artifact_id": artifact.get("artifact_id"),
            "verification_verdict": artifact.get("verification_verdict"),
            "criteria": _criteria_tuple(artifact),
        }
        for artifact in enriched
    ]
    selectable = [artifact for artifact in enriched if _selector_structurally_valid(artifact)]
    if not selectable:
        return {
            "selected_artifact_id": None,
            "criteria_trace": scored,
            "selector_blocked_reason": "no_structurally_valid_artifact",
        }
    selected = max(selectable, key=_criteria_tuple)
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
        "unresolved_blockers": [],
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
        active_blockers = list(state.get("unresolved_blockers") or [])
        gate = _gate_worker_output(payload, parsed, active_blockers)
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
        gate["blockers_found"] = _blockers_from_parsed(row, parsed, payload)
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
        resolved_ids = {str(blocker.get("blocker_id")) for blocker in gate.get("resolved_prior_blockers") or []}
        next_unresolved = [
            blocker
            for blocker in active_blockers
            if str(blocker.get("blocker_id")) not in resolved_ids
        ]
        next_unresolved.extend(gate.get("blockers_found") or [])
        state["unresolved_blockers"] = next_unresolved
        if gate.get("closure_validation_failures"):
            state["invalid_closure_ledger"] = gate.get("closure_validation_failures")
        state["turns_completed"].append(
            {
                "role": role,
                "artifact_id": row["artifact_id"],
                "gate_passed": gate["passed"],
                "blockers_found": gate.get("blockers_found") or [],
                "resolved_prior_blockers": gate.get("resolved_prior_blockers") or [],
                "closure_validation_failures": gate.get("closure_validation_failures") or [],
                "unresolved_blockers_after_turn": next_unresolved,
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
                selected = _selected_gov_baton_from_gate(gate)
                baton = {
                    "route_verdict": selected["route_verdict"],
                    "repair_target": selected["repair_target"],
                    "blocked_move": selected["blocked_move"],
                    "dependency_ledger": selected.get("dependency_ledger", []),
                    "blocker_ledger": selected.get("blocker_ledger", []),
                    "invalid_closure_ledger": selected.get("invalid_closure_ledger", []),
                    "closure_validation_failures": selected.get("closure_validation_failures", []),
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
        "selector_policy": selector_policy_identity(),
        "worker_contract": worker_contract_identity(),
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
                "selection": result.get("selection"),
                "selector_policy": result.get("selector_policy"),
                "worker_contract": result.get("worker_contract"),
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
        "selector_policy": selector_policy_identity(),
        "worker_contract": worker_contract_identity(),
    }
    (out_path / "blind_canary_runtime_results.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary
