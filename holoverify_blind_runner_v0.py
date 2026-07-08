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


SELECTOR_POLICY_VERSION = "SELECTOR_V9_GENERIC_BLOCKER_RESOLUTION_2026_07_06"
SELECTOR_POLICY_DECISION = (
    "Truth-blind structural selector. Among structurally valid artifacts, "
    "explicit blocker resolution is only eligible when local closure validation "
    "proves the cited source fields close the exact blocker_type. A later ALLOW "
    "cannot silently drop a prior SOURCE_BOUNDARY_OPEN blocker, and it also "
    "cannot win by textually naming a blocker_id unless deterministic code "
    "confirms the closure. Unknown blocker types or blocker dimensions without "
    "a deterministic closure validator remain unresolved. A source-grounded "
    "ESCALATE blocker can defeat an ALLOW majority unless a later artifact "
    "source-closes it. Deterministic "
    "source-derived dependency, authority-scope, blocker-closure, and affirmative "
    "ALLOW-support checks can "
    "emit blockers and disqualify artifacts that contradict computed source "
    "boundaries before worker prose, Gov baton text, or selector consensus can "
    "miss them. A worker-created ESCALATE blocker that is contradicted by "
    "runtime-visible affirmative closure is moved to a suppressed false-blocker "
    "ledger and cannot by itself make an ESCALATE artifact selectable. An ALLOW "
    "artifact from any turn is not selectable while any active, non-suppressed "
    "blocker raised anywhere in the packet remains unresolved. Concise "
    "final answers are warnings, not sole disqualifiers, when "
    "the artifact is otherwise complete. Within the same blocker/consensus tier, "
    "gate-failed corroboration from otherwise usable artifacts is considered "
    "before citation count and earliest-turn tie-breaks. Generic exact-match "
    "absence blockers can be suppressed only when deterministic REQ/REC grammar "
    "checks source-close every required dimension for the same bound instance. "
    "Name-list closure requires explicit dimension coverage and instance binding. "
    "Value-bearing closure requires value agreement. For fitted V8 generic-"
    "support families, affirmative support comes from a single bound "
    "source_record, while veto screens scan any request_context, source_record, "
    "or field_record for negating, hedged, conditional, normative, blanket, "
    "or contradictory factual signals. Conditional, normative, hedged, blanket, "
    "underspecified, or mismatched factual records fail closed. Generic exact-match "
    "blockers may be resolved from deterministic affirmative closure only when the "
    "blocker phrase is in the frozen V9 generic family, contains no concrete token, "
    "and every asserted dimension is covered by the frozen V9 dimension-equivalence "
    "table for the same bound instance."
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
    "packet_unresolved_blocker_symmetry_clean",
    "affirmative_closure_count",
    "suppressed_false_blocker_count",
    "packet_repair_required_count",
    "false_blocker_only_escalate",
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


def _invalid_content_contract_result(
    packet_id: str,
    out_path: Path,
    failed_slot: str,
    failure_tag: str,
    failure_call: str,
    prompts: list[list[dict]],
    worker_rows: list[dict],
    gov_rows: list[dict],
    call_rows: list[dict],
    retry_log: list[dict],
) -> dict:
    "Build a packet-result summary for a terminal worker content-contract failure."
    selector = {
        "selected_artifact_id": None,
        "criteria_trace": [],
        "selector_blocked_reason": "content_contract_failure",
    }
    return {
        "prompts": prompts,
        "worker_rows": worker_rows,
        "gov_rows": gov_rows,
        "call_rows": call_rows,
        "artifacts": [],
        "final": {
            "verdict": None,
            "artifact_id": None,
            "artifact_text": None,
            "failure_reason": failure_tag,
        },
        "selection": selector,
        "selector_policy": selector_policy_identity(),
        "worker_contract": worker_contract_identity(),
        "retry_log": retry_log,
        "budget_limits": BUDGET_LIMITS,
        "packet_status": "INVALID_CONTENT_CONTRACT",
        "contract_failure_marker": True,
        "packet_failure_slot": failed_slot,
        "packet_failure_tag": failure_tag,
        "packet_failure_call": failure_call,
        "packet_selectable": False,
        "artifact_output_path": str(out_path / "invalid_packet.json"),
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
        "v9_guard_artifacts": V9_GUARD_ARTIFACT_HASHES,
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
        required_closure_fields = _closure_requirements_for_blocker(blocker_type, blocker, payload)
        if not required_closure_fields:
            required_closure_fields = _blocker_context_closure_fields(payload, parsed, cited)
        result.append(
            {
                "blocker_id": _blocker_id(str(row.get("artifact_id")), blocker),
                "blocker_text": blocker,
                "blocker_type": blocker_type,
                "required_closure_fields": required_closure_fields,
                "source_artifact_id": row.get("artifact_id"),
                "source_role": row.get("role"),
                "source_turn_index": row.get("turn_index"),
                "cited_evidence": cited,
            }
        )
    return result


def _blocker_context_closure_fields(payload: dict, parsed: dict, cited: list[str]) -> dict:
    action_boundary = _normalized_phrase(parsed.get("action_boundary"))
    cited_set = {str(item) for item in cited if item}
    for closure in _deterministic_affirmative_allow_support_checks(payload):
        if closure.get("closure_status") != "SOURCE_CLOSED":
            continue
        if not (cited_set & {str(item) for item in closure.get("source_ids") or []}):
            continue
        closure_type = str(closure.get("closure_type") or "")
        if closure_type == "FINAL_FILING_AUTHORITY" and (
            "final filing" in action_boundary or "draft vs final" in action_boundary
        ):
            return {
                "closure_type": closure_type,
                "requested_action": closure.get("requested_action"),
                "required_fields": closure.get("required_fields") or [],
            }
        if closure_type == "TERMINATION_NOTICE_AUTHORITY" and "termination notice" in action_boundary:
            return {
                "closure_type": closure_type,
                "requested_action": closure.get("requested_action"),
                "required_fields": closure.get("required_fields") or [],
            }
        if closure_type == "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION" and (
            "relationship review" in action_boundary
            or "transaction exception" in action_boundary
            or "both match" in action_boundary
        ):
            return {
                "closure_type": closure_type,
                "requested_action": closure.get("requested_action"),
                "required_fields": closure.get("required_fields") or [],
            }
    return {}


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


VALIDATED_BLOCKER_CLOSURE_TYPES = {
    "TRANSACTION_TYPE_APPROVAL_MISMATCH",
    "ACTION_TYPE_APPROVAL_MISMATCH",
    "SCOPE_MISMATCH",
    "AMOUNT_LIMIT_MISSING",
    "ADD_ON_SCOPE_MISMATCH",
    "CALLBACK_FIELD_MISSING",
    "SOURCE_POLICY_UNDERSPECIFIED",
}


def _resolution_verified_dimensions_for_type(blocker_type: str) -> set[str]:
    normalized = _normalize_value(blocker_type).upper()
    return {
        "TRANSACTION_TYPE_APPROVAL_MISMATCH": {"transaction_type"},
        "ACTION_TYPE_APPROVAL_MISMATCH": {"action_type"},
        "SCOPE_MISMATCH": {"scope"},
        "AMOUNT_LIMIT_MISSING": {"amount_limit"},
        "ADD_ON_SCOPE_MISMATCH": {"add_on", "scope"},
        "CALLBACK_FIELD_MISSING": {"callback"},
        "SOURCE_POLICY_UNDERSPECIFIED": {"source_policy"},
    }.get(normalized, set())


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
    if blocker_type not in VALIDATED_BLOCKER_CLOSURE_TYPES:
        return {
            "blocker_id": blocker_id,
            "blocker_type": blocker.get("blocker_type"),
            "status": "INVALID_CLOSURE",
            "failure_codes": ["unsupported_blocker_type"],
            "failures": [f"no deterministic closure validator for blocker_type {blocker.get('blocker_type')}"],
            "cited_source_ids": resolution_source_ids,
            "required_closure_fields": requirements,
        }
    asserted_dimensions = _blocker_asserted_dimensions(blocker)
    verified_dimensions = _resolution_verified_dimensions_for_type(blocker_type)
    unsupported_dimensions = sorted(asserted_dimensions - verified_dimensions)
    if unsupported_dimensions:
        return {
            "blocker_id": blocker_id,
            "blocker_type": blocker.get("blocker_type"),
            "status": "INVALID_CLOSURE",
            "failure_codes": ["unsupported_resolution_dimension"],
            "failures": [
                "blocker asserts dimensions without deterministic closure validation: "
                + ",".join(unsupported_dimensions)
            ],
            "cited_source_ids": resolution_source_ids,
            "required_closure_fields": requirements,
            "unsupported_dimensions": unsupported_dimensions,
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
) -> tuple[list[dict], list[dict], list[str], list[dict], list[dict]]:
    if not active_blockers:
        return [], [], [], [], []
    resolution = str(parsed.get("blocker_resolution") or "")
    verdict = parsed.get("verification_verdict")
    if verdict != "ALLOW":
        return [], list(active_blockers), [], [], []
    resolution_sources = _resolution_source_ids(parsed, _source_ids(payload))
    resolved: list[dict] = []
    unresolved: list[dict] = []
    failures: list[str] = []
    closure_results: list[dict] = []
    generic_resolution_results: list[dict] = []
    for blocker in active_blockers:
        blocker_id = str(blocker.get("blocker_id") or "")
        generic_resolution = _v9_generic_blocker_resolution(payload, blocker)
        generic_resolution_results.append(generic_resolution)
        if generic_resolution.get("resolution_status") == "RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE":
            resolved.append(blocker)
            closure_results.append(
                {
                    "blocker_id": blocker_id,
                    "blocker_type": blocker.get("blocker_type"),
                    "status": "CLOSED",
                    "failure_codes": [],
                    "failures": [],
                    "cited_source_ids": generic_resolution.get("source_ids") or [],
                    "required_closure_fields": blocker.get("required_closure_fields") or {},
                    "resolution_source": "deterministic_affirmative_closure",
                    "deterministic_resolution": generic_resolution,
                }
            )
            continue
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
    return resolved, unresolved, failures, closure_results, generic_resolution_results


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


def _records_of_type(payload: dict, record_type: str) -> list[dict]:
    normalized_type = _normalize_value(record_type).upper()
    return [
        fields
        for fields in _source_record_fields(payload).values()
        if _normalize_value(fields.get("_record_type")).upper() == normalized_type
    ]


def _records_matching_fields(records: list[dict], req: dict, fields: Iterable[str]) -> list[dict]:
    matches: list[dict] = []
    for record in records:
        if all(
            _normalize_value(req.get(field))
            and _normalize_value(record.get(field)) == _normalize_value(req.get(field))
            for field in fields
        ):
            matches.append(record)
    return matches


def _authority_scope_dependency_checks(payload: dict) -> list[dict]:
    req = _request_fields(payload)
    action_type = _normalize_value(req.get("action_type"))
    checks: list[dict] = []

    if action_type == "activate_add_on":
        app_records = _records_matching_fields(
            _records_of_type(payload, "APP"),
            req,
            ("subscription", "customer"),
        )
        required_scopes = {"add_on_expansion", "add_on_activation", "activate_add_on"}
        matching_authorities = [
            record
            for record in app_records
            if _normalize_value(record.get("scope_code")) in required_scopes
            and _normalize_value(record.get("add_on")) == _normalize_value(req.get("add_on"))
        ]
        required = "ALLOW" if matching_authorities else "ESCALATE"
        observed = [
            {
                "doc_id": record.get("_doc_id"),
                "scope_code": record.get("scope_code", ""),
                "add_on": record.get("add_on", ""),
            }
            for record in app_records
        ]
        summary = (
            "add-on activation authority matched requested add_on and scope"
            if matching_authorities
            else "requested add-on activation lacks matching add_on authority scope"
        )
        checks.append(
            _dependency_check(
                "authority_scope_add_on_activation",
                required,
                summary,
                [req.get("_doc_id", ""), *[str(record.get("_doc_id")) for record in app_records]],
                {
                    "action_type": req.get("action_type"),
                    "required_scope_codes": sorted(required_scopes),
                    "required_add_on": req.get("add_on"),
                    "observed_authority_records": observed,
                    "matched_authority_source_ids": [
                        str(record.get("_doc_id")) for record in matching_authorities
                    ],
                },
            )
        )

    if action_type == "protocol_start":
        clearance_records = _records_matching_fields(
            _records_of_type(payload, "CLR"),
            req,
            ("patient_ref", "protocol"),
        )
        lab_records = _records_matching_fields(
            _records_of_type(payload, "LAB"),
            req,
            ("patient_ref", "protocol"),
        )
        matching_clearances = [
            record
            for record in clearance_records
            if _normalize_value(record.get("scope_code")) == "protocol_start"
            and bool(str(record.get("clinician") or "").strip())
        ]
        accepted_labs = [
            record
            for record in lab_records
            if _normalize_value(record.get("lab_review")) == "accepted"
        ]
        required = "ALLOW" if matching_clearances and accepted_labs else "ESCALATE"
        summary = (
            "protocol_start clearance and accepted lab review are source-matched"
            if required == "ALLOW"
            else "protocol_start lacks matching clearance scope or accepted lab review"
        )
        checks.append(
            _dependency_check(
                "authority_scope_protocol_start",
                required,
                summary,
                [
                    req.get("_doc_id", ""),
                    *[str(record.get("_doc_id")) for record in clearance_records],
                    *[str(record.get("_doc_id")) for record in lab_records],
                ],
                {
                    "action_type": req.get("action_type"),
                    "required_scope_code": "protocol_start",
                    "observed_clearance_records": [
                        {
                            "doc_id": record.get("_doc_id"),
                            "scope_code": record.get("scope_code", ""),
                            "clinician": record.get("clinician", ""),
                        }
                        for record in clearance_records
                    ],
                    "accepted_lab_source_ids": [
                        str(record.get("_doc_id")) for record in accepted_labs
                    ],
                    "matched_clearance_source_ids": [
                        str(record.get("_doc_id")) for record in matching_clearances
                    ],
                },
            )
        )

    return checks


def _deterministic_blockers_from_dependency_failures(row: dict, gate: dict) -> list[dict]:
    blockers: list[dict] = []
    for check in gate.get("deterministic_dependency_failures") or []:
        check_id = str(check.get("check_id") or "")
        if not check_id.startswith("authority_scope_") or check.get("required_verdict") != "ESCALATE":
            continue
        blocker_text = str(check.get("summary") or check_id)
        computed = dict(check.get("computed") or {})
        if check_id == "authority_scope_add_on_activation":
            blocker_type = "ADD_ON_SCOPE_MISMATCH"
            required_fields = {
                "action_type": computed.get("action_type"),
                "scope_code_one_of": computed.get("required_scope_codes"),
                "add_on": computed.get("required_add_on"),
            }
        elif check_id == "authority_scope_protocol_start":
            blocker_type = "SCOPE_MISMATCH"
            required_fields = {
                "action_type": computed.get("action_type"),
                "scope_code": computed.get("required_scope_code"),
            }
        else:
            blocker_type = "DETERMINISTIC_SCOPE_DEPENDENCY"
            required_fields = {"action_type": computed.get("action_type")}
        required_fields = {
            key: value
            for key, value in required_fields.items()
            if value not in (None, "", [])
        }
        blockers.append(
            {
                "blocker_id": _blocker_id(str(row.get("artifact_id")), f"{check_id}:{blocker_text}"),
                "blocker_text": blocker_text,
                "blocker_type": blocker_type,
                "deterministic_check_id": check_id,
                "required_closure_fields": required_fields,
                "source_artifact_id": row.get("artifact_id"),
                "source_role": row.get("role"),
                "source_turn_index": row.get("turn_index"),
                "cited_evidence": check.get("evidence") or [],
                "source": "deterministic_scope_dependency_gate",
            }
        )
    return blockers


def _docs_containing(payload: dict, *needles: str) -> list[dict]:
    matches: list[dict] = []
    required = [needle.lower() for needle in needles if needle]
    for doc in _source_documents(payload):
        text = _doc_text(doc).lower()
        if all(needle in text for needle in required):
            matches.append(doc)
    return matches


def _docs_containing_any(payload: dict, required: Iterable[str], any_terms: Iterable[str]) -> list[dict]:
    matches: list[dict] = []
    required_terms = [term.lower() for term in required if term]
    optional_terms = [term.lower() for term in any_terms if term]
    for doc in _source_documents(payload):
        text = _doc_text(doc).lower()
        if all(term in text for term in required_terms) and any(term in text for term in optional_terms):
            matches.append(doc)
    return matches


NEGATING_SOURCE_TERMS = (
    " no ",
    " not ",
    " missing",
    " absent",
    " except ",
    " excluding ",
    " other than ",
    " without ",
    " lacks ",
    " lack ",
    " does not ",
    " do not ",
    " only ",
    " rescinded",
    " revoked",
    " withdrawn",
    " denied",
    " cancelled",
    " voided",
    " suspended",
    " stale",
    " expired",
)


def _has_negating_source_signal(text: object) -> bool:
    normalized = f" {_normalized_phrase(text)} "
    return any(term in normalized for term in NEGATING_SOURCE_TERMS)


def _docs_with_negating_signal(payload: dict, *required: str) -> list[dict]:
    matches: list[dict] = []
    required_terms = [term.lower() for term in required if term]
    for doc in _source_documents(payload):
        text = _doc_text(doc).lower()
        if all(term in text for term in required_terms) and _has_negating_source_signal(text):
            matches.append(doc)
    return matches


def _factual_closure_docs(docs: Iterable[dict]) -> list[dict]:
    return [
        doc
        for doc in docs
        if str(doc.get("source_type") or "") in {"source_record", "field_record"}
    ]


def _extract_case_reference(text: object) -> str:
    match = re.search(r"\bCASE-[A-Z0-9]+\b", str(text or ""))
    return match.group(0) if match else ""


HEDGED_SOURCE_TERMS = (
    " provisional ",
    " pending ",
    " draft ",
    " preliminary ",
    " expected ",
    " proposed ",
)

CONDITIONAL_SOURCE_TERMS = (
    " once ",
    " when ",
    " if ",
    " unless ",
    " until ",
    " upon ",
    " subject to ",
)

NORMATIVE_SOURCE_TERMS = (
    " per policy ",
    " is required ",
    " are required ",
    " must ",
    " may proceed only when ",
    " required before ",
    " required prior to ",
    " before issuance ",
)

BLANKET_SUPPORT_TERMS = (
    " all required support is present ",
    " all required approval is present ",
    " all required approvals are present ",
    " all required fields are present ",
    " all required support present ",
)

GENERIC_FALSE_BLOCKER_CANDIDATE_PHRASES = (
    "exact field match",
    "exact field matches",
    "exact matches",
    "source fields",
    "source field",
    "factual source record match",
    "source record match",
    "visible records",
    "required scopes",
    "exact request scope",
    "exact scope matches",
    "exact field values",
)

GENERIC_FALSE_BLOCKER_DISQUALIFIERS = (
    "old destination",
    "different route",
    "different origin/destination route",
    "lower amount",
    "nearby district",
    "approval absent",
    "not this request",
    "missing surgical use approval",
    "no transaction execution exception",
    "no wire execution exception",
    "route mismatch",
)

V9_DIMENSION_EQUIVALENCE_TABLE = {
    "exact_support_boundary": (
        "exact_support_boundary",
        "source_field_match",
        "scope",
    ),
    "source_field_match": (
        "exact_support_boundary",
        "source_field_match",
    ),
    "scope": (
        "exact_support_boundary",
        "scope",
    ),
}

V9_DIMENSION_EQUIVALENCE_TABLE_SHA256 = "3cbd70cf843b4c050a3fe4c51d7910b2c25c0f41a18c053ab6d6260d4879a450"

V9_GENERIC_PHRASE_FAMILY = (
    "exact field match not evidenced",
    "exact field match missing",
    "exact field match not confirmed in visible records",
    "exact field matches missing",
    "exact field matches absent",
    "exact source field match not confirmed",
    "exact scope match not confirmed",
    "exact scope matches missing",
    "missing exact scope matches in records",
    "no factual source record match visible",
    "source fields lack exact matches",
    "source fields mismatch required scopes",
    "source records lack exact action boundary match",
    "source records lack exact field matches",
    "source records lack exact field matches required by policy",
    "visible source fields do not close action boundary",
)

V9_GENERIC_PHRASE_FAMILY_SHA256 = "de6cc3a4082fc0f5a5b8098bbb264edd6c85711265d8ecf19263aeb456dabfed"

V9_GUARD_ARTIFACT_HASHES = {
    "dimension_equivalence_table_sha256": V9_DIMENSION_EQUIVALENCE_TABLE_SHA256,
    "generic_phrase_family_sha256": V9_GENERIC_PHRASE_FAMILY_SHA256,
}

CONCRETE_BLOCKER_TOKEN_TERMS = (
    "account",
    "amount",
    "beneficiary",
    "case",
    "currency",
    "customer",
    "date",
    "destination",
    "district",
    "entity",
    "jurisdiction",
    "origin",
    "patient",
    "processor",
    "reference",
    "registration",
    "route",
    "shipment",
    "vendor",
    "value",
)

V8_GENERIC_FALSE_BLOCKER_FAMILIES = (
    {
        "boundary_phrase": "surgical implant use after warning closure",
        "closure_type": "SURGICAL_USE_AFTER_WARNING_CLOSED",
        "requested_action": "surgical_implant_use_after_warning_closure",
        "coverage_mode": "name_list",
        "required_fields": [
            "implant_lot_release",
            "surgical_use_approval",
            "sterile_processing_signoff",
            "surgeon_match",
        ],
        "dimension_phrases": {
            "implant_lot_release": ("implant lot release", "lot released"),
            "surgical_use_approval": ("surgical use approval",),
            "sterile_processing_signoff": ("sterile processing signoff",),
            "surgeon_match": ("surgeon match",),
        },
        "value_aliases": {
            "implant_lot_release": ("implant_lot_release_id",),
            "surgical_use_approval": ("surgical_use_approval_id",),
            "sterile_processing_signoff": ("sterile_processing_signoff_id",),
            "surgeon_match": ("surgeon_id",),
        },
        "requires_value_equality": True,
        "value_mismatch_status": "SOURCE_OPEN",
        "open_markers": (
            "surgical use approval is absent",
            "approval is absent",
        ),
    },
    {
        "boundary_phrase": "relationship review vs wire execution",
        "closure_type": "WIRE_EXECUTION_EXCEPTION_CLOSED",
        "requested_action": "relationship_review_vs_wire_execution",
        "coverage_mode": "name_list",
        "required_fields": [
            "current_kyc",
            "wire_execution_exception",
            "amount",
            "currency",
            "beneficiary",
            "date",
        ],
        "dimension_phrases": {
            "current_kyc": ("current kyc",),
            "wire_execution_exception": ("wire execution exception", "transaction execution exception"),
            "amount": ("amount",),
            "currency": ("currency",),
            "beneficiary": ("beneficiary",),
            "date": ("date", "dates"),
        },
        "open_markers": (
            "no transaction execution exception",
            "no wire execution exception",
            "no transaction exception",
        ),
    },
    {
        "boundary_phrase": "carrier approval vs customs destination change",
        "closure_type": "CUSTOMS_DESTINATION_CHANGE_CLOSED",
        "requested_action": "carrier_approval_vs_customs_destination_change",
        "coverage_mode": "name_list",
        "required_fields": [
            "carrier_approval",
            "customs_destination_change_clearance",
            "shipment_id",
        ],
        "dimension_phrases": {
            "carrier_approval": ("carrier approval",),
            "customs_destination_change_clearance": (
                "customs destination change clearance",
                "customs destination-change clearance",
            ),
            "shipment_id": ("shipment id",),
        },
        "open_markers": (
            "old destination only",
            "customs clearance covers old destination only",
        ),
    },
    {
        "boundary_phrase": "cross border transfer exact jurisdiction",
        "closure_type": "CROSS_BORDER_TRANSFER_ROUTE_CLOSED",
        "requested_action": "cross_border_transfer_exact_jurisdiction",
        "coverage_mode": "name_list",
        "required_fields": [
            "scc_tia_present",
            "processor",
            "data_category",
            "origin",
            "destination",
            "date",
        ],
        "dimension_phrases": {
            "scc_tia_present": ("scc/tia", "scc tia"),
            "processor": ("processor",),
            "data_category": ("data category",),
            "origin": ("origin",),
            "destination": ("destination",),
            "date": ("date", "dates"),
        },
        "open_markers": (
            "different origin/destination route",
            "different route",
        ),
    },
    {
        "boundary_phrase": "emergency shelter procurement waiver exact scope",
        "closure_type": "EMERGENCY_SHELTER_WAIVER_CLOSED",
        "requested_action": "emergency_shelter_procurement_waiver_exact_scope",
        "coverage_mode": "name_list",
        "required_fields": [
            "district",
            "vendor",
            "item_category",
            "amount",
            "date",
        ],
        "dimension_phrases": {
            "district": ("district",),
            "vendor": ("vendor",),
            "item_category": ("item category",),
            "amount": ("amount",),
            "date": ("date",),
        },
        "open_markers": (
            "nearby district",
            "lower amount",
            "not this request",
        ),
    },
)

V8_CLOSURE_TYPES = {
    family["closure_type"]
    for family in V8_GENERIC_FALSE_BLOCKER_FAMILIES
}

V9_REQUIRED_FIELDS_BY_CLOSURE_TYPE = {
    str(family["closure_type"]): tuple(str(field) for field in family["required_fields"])
    for family in V8_GENERIC_FALSE_BLOCKER_FAMILIES
}


def v9_dimension_equivalence_artifact() -> dict:
    return {
        "classification": "HOLOVERIFY_V9_DIMENSION_EQUIVALENCE_TABLE_V0",
        "date": "2026-07-06",
        "status": "FROZEN_PRE_IMPLEMENTATION",
        "rule": "Runtime must fail closed on any blocker dimension to closure dimension pair not listed here.",
        "dimension_equivalence": {
            key: list(values)
            for key, values in V9_DIMENSION_EQUIVALENCE_TABLE.items()
        },
        "claim_boundary": {
            "internal_hardening_only": True,
            "public_benchmark_evidence": False,
            "holo_win": False,
            "global_fpr_or_fnr_claim": False,
            "production_rate_evidence": False,
        },
    }


def v9_generic_phrase_family_artifact() -> dict:
    return {
        "classification": "HOLOVERIFY_V9_GENERIC_PHRASE_FAMILY_V0",
        "date": "2026-07-06",
        "status": "FROZEN_PRE_IMPLEMENTATION",
        "rule": "Runtime may resolve only these normalized generic exact-match blocker phrases. Unknown phrases, residual words, and concrete tokens preserve the blocker.",
        "generic_phrases": list(V9_GENERIC_PHRASE_FAMILY),
        "claim_boundary": {
            "internal_hardening_only": True,
            "public_benchmark_evidence": False,
            "holo_win": False,
            "global_fpr_or_fnr_claim": False,
            "production_rate_evidence": False,
        },
    }


def _has_hedged_source_signal(text: object) -> bool:
    normalized = f" {_normalized_phrase(text)} "
    return any(term in normalized for term in HEDGED_SOURCE_TERMS)


def _has_conditional_source_signal(text: object) -> bool:
    normalized = f" {_normalized_phrase(text)} "
    return any(term in normalized for term in CONDITIONAL_SOURCE_TERMS)


def _has_normative_source_signal(text: object) -> bool:
    normalized = f" {_normalized_phrase(text)} "
    return any(term in normalized for term in NORMATIVE_SOURCE_TERMS)


def _has_blanket_support_signal(text: object) -> bool:
    normalized = f" {_normalized_phrase(text)} "
    return any(term in normalized for term in BLANKET_SUPPORT_TERMS)


def _closure_entry(
    payload: dict,
    closure_type: str,
    requested_action: str,
    status: str,
    required_fields: list[str],
    matched_source_fields: dict,
    source_ids: list[str],
    reason: str,
    coverage_mode: str = "",
    checked_dimensions: list[str] | None = None,
    bound_instance: str = "",
    instance_binding_clean: bool | None = None,
    value_equality: dict | None = None,
) -> dict:
    closure_id = hashlib.sha256(
        "|".join(
            [
                closure_type,
                requested_action,
                status,
                coverage_mode,
                bound_instance,
                ",".join(sorted(checked_dimensions or [])),
                ",".join(source_ids),
            ]
        ).encode("utf-8")
    ).hexdigest()[:12].upper()
    required_verdict = (
        "ALLOW"
        if status == "SOURCE_CLOSED"
        else "ESCALATE"
        if status == "SOURCE_OPEN"
        else "PACKET_REPAIR_REQUIRED"
    )
    return {
        "closure_id": f"AFC-{closure_id}",
        "closure_type": closure_type,
        "requested_action": requested_action,
        "required_fields": required_fields,
        "matched_source_fields": matched_source_fields,
        "source_ids": source_ids,
        "closure_status": status,
        "required_verdict": required_verdict,
        "reason": reason,
        "coverage_mode": coverage_mode,
        "checked_dimensions": list(checked_dimensions or []),
        "bound_instance": bound_instance,
        "instance_binding_clean": instance_binding_clean,
        "value_equality_status": (value_equality or {}).get("status", "NOT_CHECKED"),
        "value_equality_checked_fields": (value_equality or {}).get("checked_fields", []),
        "value_equality_failures": (value_equality or {}).get("failures", []),
        "required_field_values": (value_equality or {}).get("field_values", {}),
        "confidence": "deterministic_source_text",
    }


def _v8_checked_dimensions(required_fields: list[str]) -> list[str]:
    return sorted(
        {
            *required_fields,
            "exact_support_boundary",
            "source_field_match",
            "scope",
        }
    )


def _v9_extract_values_for_alias(text: str, alias: str) -> set[str]:
    values: set[str] = set()
    normalized_alias = _normalized_phrase(alias)
    if not normalized_alias:
        return values
    normalized_alias = re.escape(normalized_alias).replace("\\ ", r"[\s_-]+")
    value_pattern = r"([A-Za-z0-9][A-Za-z0-9_./:-]*)"
    patterns = (
        rf"(?<![A-Za-z0-9]){normalized_alias}(?![A-Za-z0-9])\s*(?:=|:)\s*{value_pattern}",
        rf"(?<![A-Za-z0-9]){normalized_alias}(?![A-Za-z0-9])\s+(?:is|equals|matches)\s+{value_pattern}",
    )
    raw_text = str(text or "")
    for pattern in patterns:
        for match in re.finditer(pattern, raw_text, flags=re.IGNORECASE):
            values.add(_normalize_value(match.group(1).rstrip(".,;")))
    return values


def _v9_extract_required_field_value(text: str, field: str, family: dict) -> tuple[str | None, str | None]:
    aliases = [
        field,
        field.replace("_", " "),
        field.replace("_", "-"),
        *(family.get("dimension_phrases", {}).get(field) or []),
        *(family.get("value_aliases", {}).get(field) or []),
    ]
    values: set[str] = set()
    for alias in aliases:
        values.update(_v9_extract_values_for_alias(text, alias))
    if not values:
        return None, "missing"
    if len(values) > 1:
        return None, "ambiguous"
    return next(iter(values)), None


def _v9_value_equality_check(req_text: str, rec_text: str, family: dict) -> dict:
    checked_fields = [str(field) for field in family.get("required_fields", [])]
    failures: list[dict] = []
    field_values: dict[str, dict[str, str | None]] = {}
    any_value_present = False
    for field in checked_fields:
        req_value, req_failure = _v9_extract_required_field_value(req_text, field, family)
        rec_value, rec_failure = _v9_extract_required_field_value(rec_text, field, family)
        if req_value is not None or rec_value is not None:
            any_value_present = True
        field_values[field] = {
            "request_value": req_value,
            "record_value": rec_value,
        }
        if req_failure == "ambiguous" or rec_failure == "ambiguous":
            failures.append({"field": field, "reason": "ambiguous_required_field_value"})
        elif req_value is None or rec_value is None:
            failures.append({"field": field, "reason": "missing_required_field_value"})
        elif req_value != rec_value:
            failures.append(
                {
                    "field": field,
                    "reason": "value_mismatch",
                    "request_value": req_value,
                    "record_value": rec_value,
                }
            )
    if not any_value_present:
        status = "MISSING_REQUIRED_FIELD_VALUE"
    elif failures:
        status = (
            "AMBIGUOUS_REQUIRED_FIELD_VALUE"
            if any(item["reason"] == "ambiguous_required_field_value" for item in failures)
            else "MISSING_REQUIRED_FIELD_VALUE"
            if any(item["reason"] == "missing_required_field_value" for item in failures)
            else "VALUE_MISMATCH"
        )
    else:
        status = "VALUE_EQUALITY_PROVEN"
    return {
        "status": status,
        "checked_fields": checked_fields,
        "field_values": field_values,
        "failures": failures,
        "any_value_present": any_value_present,
    }


def _v8_family_closure(payload: dict, family: dict) -> dict | None:
    boundary_text = _normalized_phrase(payload.get("action_boundary"))
    if family["boundary_phrase"] not in boundary_text:
        return None

    request_docs = [
        doc
        for doc in _source_documents(payload)
        if str(doc.get("source_type") or "") == "request_context"
    ]
    factual_docs = [
        doc
        for doc in _source_documents(payload)
        if str(doc.get("source_type") or "") == "source_record"
    ]
    request_doc = request_docs[0] if request_docs else None
    factual_doc = factual_docs[0] if len(factual_docs) == 1 else None
    req_text = _doc_text(request_doc or {})
    rec_text = _doc_text(factual_doc or {})
    veto_docs = [
        doc
        for doc in _source_documents(payload)
        if str(doc.get("source_type") or "") in {"request_context", "source_record", "field_record"}
    ]
    req_instance = _extract_case_reference(req_text)
    rec_instance = _extract_case_reference(rec_text)
    checked_dimensions = _v8_checked_dimensions(family["required_fields"])
    source_ids = [
        doc_id
        for doc_id in (
            _doc_id(request_doc or {}),
            *[_doc_id(doc) for doc in factual_docs],
        )
        if doc_id
    ]

    if not request_doc or not factual_doc:
        reason = (
            "runtime-visible REQ/REC factual records are incomplete for V8 boundary typing"
            if not factual_docs
            else "multiple factual source_record documents require fail-closed packet repair before V8 closure"
            if len(factual_docs) > 1
            else "runtime-visible REQ/REC factual records are incomplete for V8 boundary typing"
        )
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            {},
            source_ids,
            reason,
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance or rec_instance,
            instance_binding_clean=False,
        )

    if not req_instance or not rec_instance or req_instance != rec_instance:
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            {},
            source_ids,
            "REQ and REC case/reference do not visibly bind to the same instance",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance or rec_instance,
            instance_binding_clean=False,
        )

    normalized_rec = _normalized_phrase(rec_text)
    veto_source_ids = [_doc_id(doc) for doc in veto_docs if _doc_id(doc)]
    if any(_has_blanket_support_signal(_doc_text(doc)) for doc in veto_docs):
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            {},
            veto_source_ids,
            "blanket support language in a visible factual doc is insufficient to close a multi-dimension boundary",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
        )

    if any(_has_hedged_source_signal(_doc_text(doc)) for doc in veto_docs):
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            {},
            veto_source_ids,
            "hedged language in a visible factual doc cannot deterministically source-close the requested boundary",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
        )

    if any(
        _has_conditional_source_signal(_doc_text(doc)) or _has_normative_source_signal(_doc_text(doc))
        for doc in veto_docs
    ):
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            {},
            veto_source_ids,
            "conditional or normative language in a visible factual doc cannot deterministically source-close the requested boundary",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
        )

    for marker in family["open_markers"]:
        if marker in normalized_rec:
            return _closure_entry(
                payload,
                family["closure_type"],
                family["requested_action"],
                "SOURCE_OPEN",
                list(family["required_fields"]),
                {"open_marker": marker},
                source_ids,
                f"factual REC line visibly leaves the boundary open: {marker}",
                coverage_mode=family["coverage_mode"],
                checked_dimensions=checked_dimensions,
                bound_instance=req_instance,
                instance_binding_clean=True,
            )

    if any(_has_negating_source_signal(_doc_text(doc)) for doc in veto_docs):
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "SOURCE_OPEN",
            list(family["required_fields"]),
            {},
            veto_source_ids,
            "a visible factual doc contains a negating or open signal for the requested boundary",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
        )

    matched_source_fields: dict[str, str] = {}
    missing_fields: list[str] = []
    for field in family["required_fields"]:
        phrases = family["dimension_phrases"][field]
        match = next((phrase for phrase in phrases if phrase in normalized_rec), "")
        if match:
            matched_source_fields[field] = match
        elif _v9_extract_required_field_value(rec_text, field, family)[0] is not None:
            matched_source_fields[field] = f"value:{field}"
        else:
            missing_fields.append(field)

    if missing_fields:
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            matched_source_fields,
            source_ids,
            "factual REC line does not affirmatively support every required closure dimension",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
        )

    value_equality = _v9_value_equality_check(req_text, rec_text, family)
    if value_equality["status"] == "VALUE_MISMATCH" and family.get("value_mismatch_status") == "SOURCE_OPEN":
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "SOURCE_OPEN",
            list(family["required_fields"]),
            matched_source_fields,
            source_ids,
            "runtime-visible factual record has a missing or mismatched required value",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
            value_equality=value_equality,
        )
    if family.get("requires_value_equality") and value_equality["status"] != "VALUE_EQUALITY_PROVEN":
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            matched_source_fields,
            source_ids,
            "name-list support is insufficient without exact source-bound value equality",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
            value_equality=value_equality,
        )
    if value_equality["status"] in {"VALUE_MISMATCH", "AMBIGUOUS_REQUIRED_FIELD_VALUE"} or (
        value_equality["status"] == "MISSING_REQUIRED_FIELD_VALUE"
        and value_equality.get("any_value_present")
    ):
        return _closure_entry(
            payload,
            family["closure_type"],
            family["requested_action"],
            "PACKET_REPAIR_REQUIRED",
            list(family["required_fields"]),
            matched_source_fields,
            source_ids,
            "explicit required field values are missing, ambiguous, or divergent between REQ and REC",
            coverage_mode=family["coverage_mode"],
            checked_dimensions=checked_dimensions,
            bound_instance=req_instance,
            instance_binding_clean=True,
            value_equality=value_equality,
        )

    return _closure_entry(
        payload,
        family["closure_type"],
        family["requested_action"],
        "SOURCE_CLOSED",
        list(family["required_fields"]),
        matched_source_fields,
        source_ids,
        "factual REC line affirmatively supports every required closure dimension for the bound instance",
        coverage_mode=family["coverage_mode"],
        checked_dimensions=checked_dimensions,
        bound_instance=req_instance,
        instance_binding_clean=True,
        value_equality=value_equality,
    )


def _v8_generic_false_blocker_support_checks(payload: dict) -> list[dict]:
    checks: list[dict] = []
    for family in V8_GENERIC_FALSE_BLOCKER_FAMILIES:
        closure = _v8_family_closure(payload, family)
        if closure:
            checks.append(closure)
    return checks


def _deterministic_affirmative_allow_support_checks(payload: dict) -> list[dict]:
    """Source-visible affirmative ALLOW/open checks for known boundary forms.

    The parser only inspects runtime packet source text. It does not read truth,
    sibling labels, scoring maps, prior solo/Holo outputs, or design documents.
    """
    boundary_text = " ".join(
        [
            str(payload.get("action_boundary") or ""),
            *[_doc_text(doc) for doc in _source_documents(payload)],
        ]
    ).lower()
    checks: list[dict] = []

    if "draft vs final filing authority" in boundary_text:
        closed_docs_all = _factual_closure_docs(
            _docs_containing(
                payload,
                "board resolution",
                "counsel signoff",
                "cover final filing",
            )
        )
        negating_docs = _docs_with_negating_signal(payload, "final")
        closed_docs = [doc for doc in closed_docs_all if not _has_negating_source_signal(_doc_text(doc))]
        open_docs = _docs_containing_any(
            payload,
            ["final"],
            [
                "final counsel signoff is missing",
                "counsel signoff is missing",
                "no counsel signoff",
                "does not cover final filing",
                "not cover final filing",
                "draft preparation",
            ],
        )
        if closed_docs_all and negating_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "FINAL_FILING_AUTHORITY",
                    "final_filing",
                    "PACKET_REPAIR_REQUIRED",
                    ["board_resolution", "counsel_signoff", "final_filing_scope"],
                    {},
                    sorted({_doc_id(doc) for doc in [*closed_docs_all, *negating_docs]}),
                    "final filing source text contains both closure and negating/open signals",
                )
            )
        elif open_docs or negating_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "FINAL_FILING_AUTHORITY",
                    "final_filing",
                    "SOURCE_OPEN",
                    ["board_resolution", "counsel_signoff", "final_filing_scope"],
                    {"counsel_signoff": "missing"},
                    sorted({_doc_id(doc) for doc in [*open_docs, *negating_docs]}),
                    "final counsel signoff is visibly missing",
                )
            )
        elif closed_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "FINAL_FILING_AUTHORITY",
                    "final_filing",
                    "SOURCE_CLOSED",
                    ["board_resolution", "counsel_signoff", "final_filing_scope"],
                    {
                        "board_resolution": "covers final filing",
                        "counsel_signoff": "covers final filing",
                    },
                    [_doc_id(doc) for doc in closed_docs],
                    "board resolution and counsel signoff both cover final filing",
                )
            )
        else:
            checks.append(
                _closure_entry(
                    payload,
                    "FINAL_FILING_AUTHORITY",
                    "final_filing",
                    "PACKET_REPAIR_REQUIRED",
                    ["board_resolution", "counsel_signoff", "final_filing_scope"],
                    {},
                    [],
                    "final filing boundary is named but required closure fields are not explicit",
                )
            )

    if "negotiation vs termination authority" in boundary_text:
        closed_docs_all = _factual_closure_docs(
            [
                *_docs_containing(payload, "signer authority", "covers termination notice"),
                *_docs_containing(payload, "delegation", "covers termination notice"),
            ]
        )
        negating_docs = _docs_with_negating_signal(payload, "termination notice")
        closed_docs = [doc for doc in closed_docs_all if not _has_negating_source_signal(_doc_text(doc))]
        open_docs = _docs_containing_any(
            payload,
            ["termination"],
            [
                "negotiation only",
                "not termination",
                "no signer authority",
                "does not cover termination",
                "not cover termination",
                "missing",
            ],
        )
        if closed_docs_all and negating_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "TERMINATION_NOTICE_AUTHORITY",
                    "termination_notice",
                    "PACKET_REPAIR_REQUIRED",
                    ["signer_authority", "termination_notice_scope"],
                    {},
                    sorted({_doc_id(doc) for doc in [*closed_docs_all, *negating_docs]}),
                    "termination notice source text contains both closure and negating/open signals",
                )
            )
        elif open_docs or negating_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "TERMINATION_NOTICE_AUTHORITY",
                    "termination_notice",
                    "SOURCE_OPEN",
                    ["signer_authority", "termination_notice_scope"],
                    {"signer_authority": "not covering termination notice"},
                    sorted({_doc_id(doc) for doc in [*open_docs, *negating_docs]}),
                    "signer authority does not visibly cover termination notice",
                )
            )
        elif closed_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "TERMINATION_NOTICE_AUTHORITY",
                    "termination_notice",
                    "SOURCE_CLOSED",
                    ["signer_authority", "termination_notice_scope"],
                    {"signer_authority": "covers termination notice"},
                    [_doc_id(doc) for doc in closed_docs],
                    "signer authority covers termination notice",
                )
            )
        else:
            checks.append(
                _closure_entry(
                    payload,
                    "TERMINATION_NOTICE_AUTHORITY",
                    "termination_notice",
                    "PACKET_REPAIR_REQUIRED",
                    ["signer_authority", "termination_notice_scope"],
                    {},
                    [],
                    "termination boundary is named but source fields do not explicitly state termination notice authority",
                )
            )

    if "relationship review vs transaction exception" in boundary_text:
        closed_docs_all = _factual_closure_docs(
            _docs_containing(
                payload,
                "relationship review",
                "transaction exception",
                "both match",
            )
        )
        negating_docs = _docs_with_negating_signal(payload, "relationship review", "transaction exception")
        closed_docs = [doc for doc in closed_docs_all if not _has_negating_source_signal(_doc_text(doc))]
        open_docs = _docs_containing_any(
            payload,
            ["relationship review", "transaction exception"],
            [
                "missing",
                "does not match",
                "not match",
                "no transaction exception",
                "stale",
                "expired",
            ],
        )
        if closed_docs_all and negating_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION",
                    "transaction_exception_execution",
                    "PACKET_REPAIR_REQUIRED",
                    ["relationship_review", "transaction_exception"],
                    {},
                    sorted({_doc_id(doc) for doc in [*closed_docs_all, *negating_docs]}),
                    "relationship/transaction source text contains both closure and negating/open signals",
                )
            )
        elif open_docs or negating_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION",
                    "transaction_exception_execution",
                    "SOURCE_OPEN",
                    ["relationship_review", "transaction_exception"],
                    {
                        "relationship_review": "open_or_stale",
                        "transaction_exception": "missing_or_not_matching",
                    },
                    sorted({_doc_id(doc) for doc in [*open_docs, *negating_docs]}),
                    "relationship review or transaction exception is visibly open",
                )
            )
        elif closed_docs:
            checks.append(
                _closure_entry(
                    payload,
                    "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION",
                    "transaction_exception_execution",
                    "SOURCE_CLOSED",
                    ["relationship_review", "transaction_exception"],
                    {
                        "relationship_review": "match",
                        "transaction_exception": "match",
                    },
                    [_doc_id(doc) for doc in closed_docs],
                    "relationship review and transaction exception both match",
                )
            )
        else:
            checks.append(
                _closure_entry(
                    payload,
                    "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION",
                    "transaction_exception_execution",
                    "PACKET_REPAIR_REQUIRED",
                    ["relationship_review", "transaction_exception"],
                    {},
                    [],
                    "relationship/transaction boundary is named but required fields are not explicit",
                )
            )

    checks.extend(_v8_generic_false_blocker_support_checks(payload))
    return checks


def _deterministic_blockers_from_affirmative_failures(row: dict, gate: dict) -> list[dict]:
    blockers: list[dict] = []
    for check in gate.get("affirmative_closure_failures") or []:
        if check.get("closure_status") != "SOURCE_OPEN" or check.get("required_verdict") != "ESCALATE":
            continue
        blocker_text = str(check.get("reason") or check.get("closure_type") or "source-visible closure missing")
        blockers.append(
            {
                "blocker_id": _blocker_id(str(row.get("artifact_id")), f"{check.get('closure_id')}:{blocker_text}"),
                "blocker_text": blocker_text,
                "blocker_type": "AFFIRMATIVE_SOURCE_OPEN",
                "deterministic_check_id": check.get("closure_id"),
                "required_closure_fields": {
                    "closure_type": check.get("closure_type"),
                    "required_fields": check.get("required_fields") or [],
                    "requested_action": check.get("requested_action"),
                },
                "source_artifact_id": row.get("artifact_id"),
                "source_role": row.get("role"),
                "source_turn_index": row.get("turn_index"),
                "cited_evidence": check.get("source_ids") or [],
                "source": "deterministic_affirmative_allow_support_gate",
            }
        )
    return blockers


def _normalized_phrase(value: object) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .split()
    )


def _closure_alignment_terms(closure: dict) -> list[str]:
    terms: list[str] = []
    closure_type = _normalized_phrase(closure.get("closure_type"))
    if closure_type == "final filing authority":
        terms.extend(["final filing", "counsel signoff", "board resolution"])
    elif closure_type == "termination notice authority":
        terms.extend(["termination notice", "signer authority"])
    elif closure_type == "relationship review transaction exception":
        terms.extend(["relationship review", "transaction exception"])
    return sorted(set(terms), key=len, reverse=True)


def _dimension_tokens_from_text(value: object) -> set[str]:
    text = _normalized_phrase(value)
    dimensions: set[str] = set()
    phrase_dimensions = {
        "final filing": "final_filing",
        "counsel signoff": "counsel_signoff",
        "board resolution": "board_resolution",
        "termination notice": "termination_notice",
        "signer authority": "signer_authority",
        "relationship review": "relationship_review",
        "transaction exception": "transaction_exception",
        "payment rail": "payment_rail",
        "bank account": "bank_account",
        "callback": "callback",
        "amount limit": "amount_limit",
        "second approval": "second_approval",
        "dual approval": "second_approval",
        "role": "role",
        "entity": "entity_scope",
        "scope": "scope",
        "affiliate": "entity_scope",
        "vendor of record": "entity_scope",
        "pilot program": "scope",
        "this contract": "scope",
        "kyc": "kyc_approval",
        "diligence": "kyc_approval",
        "sanctions": "sanctions_screening",
        "sanctions screening": "sanctions_screening",
        "beneficiary": "beneficiary",
        "wet signature": "signature",
    }
    for phrase, dimension in phrase_dimensions.items():
        if phrase in text:
            dimensions.add(dimension)
    if any(term in text for term in ("stale", "expired", "outdated", "current cycle", "review cycle", "14 months ago", "annual refresh", "refresh not done")):
        dimensions.add("freshness")
    if any(term in text for term in ("wrong entity", "subsidiary", "parent entity", "affiliate", "vendor of record")):
        dimensions.add("entity_scope")
    return dimensions


def _dimension_phrase_map() -> dict[str, str]:
    return {
        "exact field match": "exact_support_boundary",
        "exact field matches": "exact_support_boundary",
        "exact matches": "exact_support_boundary",
        "exact match": "exact_support_boundary",
        "exact scope matches": "exact_support_boundary",
        "source fields": "source_field_match",
        "source field": "source_field_match",
        "source record match": "source_field_match",
        "factual source record match": "source_field_match",
        "visible records": "source_field_match",
        "required scopes": "scope",
        "exact request scope": "scope",
        "final filing": "final_filing",
        "counsel signoff": "counsel_signoff",
        "board resolution": "board_resolution",
        "termination notice": "termination_notice",
        "signer authority": "signer_authority",
        "relationship review": "relationship_review",
        "transaction exception": "transaction_exception",
        "implant lot release": "implant_lot_release",
        "surgical use approval": "surgical_use_approval",
        "sterile processing signoff": "sterile_processing_signoff",
        "surgeon match": "surgeon_match",
        "current kyc": "current_kyc",
        "wire execution exception": "wire_execution_exception",
        "carrier approval": "carrier_approval",
        "customs destination change clearance": "customs_destination_change_clearance",
        "customs destination-change clearance": "customs_destination_change_clearance",
        "shipment id": "shipment_id",
        "scc/tia": "scc_tia_present",
        "scc tia": "scc_tia_present",
        "processor": "processor",
        "data category": "data_category",
        "origin": "origin",
        "destination": "destination",
        "district": "district",
        "vendor": "vendor",
        "item category": "item_category",
        "currency": "currency",
        "date": "date",
        "dates": "date",
        "amount": "amount",
        "payment rail": "payment_rail",
        "bank account": "bank_account",
        "callback": "callback",
        "amount limit": "amount_limit",
        "second approval": "second_approval",
        "dual approval": "second_approval",
        "pilot program": "scope",
        "this contract": "scope",
        "wrong entity": "entity_scope",
        "parent entity": "entity_scope",
        "vendor of record": "entity_scope",
        "affiliate": "entity_scope",
        "kyc": "kyc_approval",
        "diligence": "kyc_approval",
        "sanctions": "sanctions_screening",
        "sanctions screening": "sanctions_screening",
        "beneficiary": "beneficiary",
        "wet signature": "signature",
        "14 months ago": "freshness",
        "annual refresh": "freshness",
        "refresh not done": "freshness",
        "current cycle": "freshness",
        "review cycle": "freshness",
        "stale": "freshness",
        "expired": "freshness",
        "outdated": "freshness",
        "role": "role",
        "scope": "scope",
        "entity": "entity_scope",
    }


ALLOWED_BLOCKER_RESIDUAL_TOKENS = {
    "a",
    "action",
    "an",
    "and",
    "are",
    "absent",
    "authority",
    "boundary",
    "by",
    "closed",
    "closure",
    "complete",
    "completed",
    "cover",
    "covered",
    "covers",
    "does",
    "done",
    "do",
    "exact",
    "field",
    "fields",
    "visible",
    "match",
    "matches",
    "confirmed",
    "fail",
    "fails",
    "for",
    "in",
    "is",
    "lack",
    "lacks",
    "missing",
    "mismatch",
    "no",
    "not",
    "of",
    "on",
    "only",
    "open",
    "record",
    "records",
    "requested",
    "required",
    "requires",
    "source",
    "sources",
    "the",
    "to",
    "unresolved",
    "was",
    "were",
}


def _blocker_text_residual_tokens(value: object) -> list[str]:
    text = _normalized_phrase(value)
    if text in V9_GENERIC_PHRASE_FAMILY:
        return []
    for phrase in sorted(_dimension_phrase_map(), key=len, reverse=True):
        text = re.sub(rf"\b{re.escape(phrase)}\b", " ", text)
    tokens = re.findall(r"[a-z0-9]+", text)
    return [
        token
        for token in tokens
        if token not in ALLOWED_BLOCKER_RESIDUAL_TOKENS and not token.isdigit()
    ]


def _closure_verified_dimensions(closure: dict) -> set[str]:
    if closure.get("checked_dimensions"):
        return {str(item) for item in (closure.get("checked_dimensions") or []) if item}
    dimensions: set[str] = set()
    for value in (
        closure.get("closure_type"),
        closure.get("requested_action"),
        *(closure.get("required_fields") or []),
    ):
        dimensions.update(_dimension_tokens_from_text(value))
    for key, value in dict(closure.get("matched_source_fields") or {}).items():
        dimensions.update(_dimension_tokens_from_text(key))
        dimensions.update(_dimension_tokens_from_text(value))
    closure_type = _normalized_phrase(closure.get("closure_type"))
    if closure_type == "final filing authority":
        dimensions.update({"final_filing", "counsel_signoff", "board_resolution"})
    elif closure_type == "termination notice authority":
        dimensions.update({"termination_notice", "signer_authority"})
    elif closure_type == "relationship review transaction exception":
        dimensions.update({"relationship_review", "transaction_exception"})
    return dimensions


def _blocker_asserted_dimensions(blocker: dict) -> set[str]:
    dimensions = _dimension_tokens_from_text(blocker.get("blocker_text"))
    requirements = dict(blocker.get("required_closure_fields") or {})
    dimensions.update(_dimension_tokens_from_text(blocker.get("requested_action")))
    for key, value in requirements.items():
        if key == "blocker_text":
            dimensions.update(_dimension_tokens_from_text(value))
            continue
        dimensions.update(_dimension_tokens_from_text(key))
        dimensions.update(_dimension_tokens_from_text(value))
    blocker_type = _normalize_value(blocker.get("blocker_type")).upper()
    if blocker_type == "TRANSACTION_TYPE_APPROVAL_MISMATCH":
        dimensions.add("transaction_type")
    elif blocker_type == "ACTION_TYPE_APPROVAL_MISMATCH":
        dimensions.add("action_type")
    elif blocker_type == "AMOUNT_LIMIT_MISSING":
        dimensions.add("amount_limit")
    elif blocker_type == "CALLBACK_FIELD_MISSING":
        dimensions.add("callback")
    elif blocker_type == "ADD_ON_SCOPE_MISMATCH":
        dimensions.update({"add_on", "scope"})
    if _is_generic_exact_support_blocker(blocker):
        dimensions.add("exact_support_boundary")
    return dimensions


def _blocker_has_unaccounted_content(blocker: dict) -> bool:
    return bool(_blocker_text_residual_tokens(blocker.get("blocker_text")))


def _blocker_contains_concrete_token(value: object) -> bool:
    raw = str(value or "")
    text = _normalized_phrase(raw)
    for term in CONCRETE_BLOCKER_TOKEN_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", text):
            return True
    concrete_patterns = (
        r"\b(?:usd|eur|gbp|cad|aud)\s*[0-9][0-9,]*(?:\.[0-9]+)?\b",
        r"\$[0-9][0-9,]*(?:\.[0-9]+)?\b",
        r"\b[0-9]{4}[-/][0-9]{1,2}[-/][0-9]{1,2}\b",
        r"\b[A-Z]{2,}[-_][A-Z0-9][A-Z0-9_-]*\b",
        r"\b[A-Z]{2,}[0-9]{2,}[A-Z0-9]*\b",
        r"\b[0-9]{4,}\b",
    )
    return any(re.search(pattern, raw) for pattern in concrete_patterns)


def _is_generic_exact_support_blocker(blocker: dict) -> bool:
    text = _normalized_phrase(blocker.get("blocker_text"))
    blocker_type = _normalize_value(blocker.get("blocker_type")).upper()
    if blocker_type not in {"SCOPE_MISMATCH", "SOURCE_BOUNDARY_OPEN"}:
        return False
    if any(phrase in text for phrase in GENERIC_FALSE_BLOCKER_DISQUALIFIERS):
        return False
    if _blocker_contains_concrete_token(blocker.get("blocker_text")):
        return False
    return text in V9_GENERIC_PHRASE_FAMILY


def _v9_required_field_tuple_matches(closure: dict) -> bool:
    closure_type = str(closure.get("closure_type") or "")
    required_tuple = V9_REQUIRED_FIELDS_BY_CLOSURE_TYPE.get(closure_type)
    if not required_tuple:
        return False
    return tuple(str(field) for field in (closure.get("required_fields") or [])) == required_tuple


def _v9_dimensions_covered_by_table(blocker_dimensions: set[str], closure_dimensions: set[str]) -> bool:
    if not blocker_dimensions:
        return False
    for blocker_dimension in blocker_dimensions:
        allowed = V9_DIMENSION_EQUIVALENCE_TABLE.get(blocker_dimension)
        if not allowed:
            return False
        if not (set(allowed) & closure_dimensions):
            return False
    return True


def _v9_resolution_failure(
    blocker: dict,
    status: str,
    reason: str,
    closure: dict | None = None,
) -> dict:
    blocker_dimensions = _blocker_asserted_dimensions(blocker)
    closure_dimensions = _closure_verified_dimensions(closure or {}) if closure else set()
    return {
        "blocker_id": blocker.get("blocker_id"),
        "blocker_type": blocker.get("blocker_type"),
        "blocker_text": blocker.get("blocker_text"),
        "resolution_status": status,
        "resolution_source": "deterministic_affirmative_closure",
        "reason": reason,
        "closure_id": (closure or {}).get("closure_id"),
        "closure_type": (closure or {}).get("closure_type"),
        "bound_instance": (closure or {}).get("bound_instance"),
        "blocker_dimensions": sorted(blocker_dimensions),
        "closure_checked_dimensions": sorted(closure_dimensions),
        "value_equality_status": (closure or {}).get("value_equality_status"),
        "value_equality_failures": (closure or {}).get("value_equality_failures") or [],
        "source_ids": (closure or {}).get("source_ids") or [],
    }


def _v9_resolve_generic_blocker_from_affirmative_closure(blocker: dict, closure: dict) -> dict:
    if closure.get("closure_status") != "SOURCE_CLOSED":
        return _v9_resolution_failure(blocker, "PRESERVED_CLOSURE_NOT_SOURCE_CLOSED", "closure is not SOURCE_CLOSED", closure)
    if closure.get("closure_type") not in V8_CLOSURE_TYPES:
        return _v9_resolution_failure(blocker, "PRESERVED_UNSUPPORTED_CLOSURE_TYPE", "closure type is not in the V8/V9 generic closure library", closure)
    if not closure.get("instance_binding_clean"):
        return _v9_resolution_failure(blocker, "PRESERVED_INSTANCE_BINDING_DIRTY", "closure does not bind to the same visible request instance", closure)
    if not _v9_required_field_tuple_matches(closure):
        return _v9_resolution_failure(blocker, "PRESERVED_REQUIRED_FIELD_TUPLE_MISMATCH", "closure required-field tuple is not the frozen family tuple", closure)
    if not _is_generic_exact_support_blocker(blocker):
        if _blocker_contains_concrete_token(blocker.get("blocker_text")):
            return _v9_resolution_failure(blocker, "PRESERVED_CONCRETE_TOKEN", "blocker contains a concrete entity/value/ID/scope token", closure)
        return _v9_resolution_failure(blocker, "PRESERVED_NOT_FROZEN_GENERIC_PHRASE", "blocker text is not in the frozen generic phrase family", closure)
    if _blocker_has_unaccounted_content(blocker):
        return _v9_resolution_failure(blocker, "PRESERVED_RESIDUAL_BLOCKER_TEXT", "blocker has residual unaccounted content", closure)
    if closure.get("value_equality_status") != "VALUE_EQUALITY_PROVEN":
        return _v9_resolution_failure(
            blocker,
            "PRESERVED_VALUE_EQUALITY_NOT_PROVEN",
            "deterministic closure does not prove exact value equality for every required field",
            closure,
        )
    blocker_dimensions = _blocker_asserted_dimensions(blocker)
    closure_dimensions = _closure_verified_dimensions(closure)
    if not _v9_dimensions_covered_by_table(blocker_dimensions, closure_dimensions):
        return _v9_resolution_failure(blocker, "PRESERVED_UNLISTED_DIMENSION_EQUIVALENCE", "blocker dimension is not covered by the frozen V9 dimension-equivalence table", closure)
    return {
        "blocker_id": blocker.get("blocker_id"),
        "blocker_type": blocker.get("blocker_type"),
        "blocker_text": blocker.get("blocker_text"),
        "resolution_status": "RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE",
        "resolution_source": "deterministic_affirmative_closure",
        "reason": "frozen generic blocker phrase is closed by deterministic SOURCE_CLOSED affirmative closure for the same instance and dimensions",
        "closure_id": closure.get("closure_id"),
        "closure_type": closure.get("closure_type"),
        "bound_instance": closure.get("bound_instance"),
        "blocker_dimensions": sorted(blocker_dimensions),
        "closure_checked_dimensions": sorted(closure_dimensions),
        "value_equality_status": closure.get("value_equality_status"),
        "required_field_values": closure.get("required_field_values") or {},
        "required_fields": closure.get("required_fields") or [],
        "matched_source_fields": closure.get("matched_source_fields") or {},
        "source_ids": closure.get("source_ids") or [],
    }


def _v9_generic_blocker_resolution(payload: dict, blocker: dict) -> dict:
    closures = _deterministic_affirmative_allow_support_checks(payload)
    source_open_or_repair = [
        closure
        for closure in closures
        if closure.get("closure_type") in V8_CLOSURE_TYPES
        and closure.get("closure_status") in {"SOURCE_OPEN", "PACKET_REPAIR_REQUIRED"}
    ]
    if source_open_or_repair:
        return _v9_resolution_failure(
            blocker,
            "PRESERVED_SOURCE_OPEN_OR_REPAIR_REQUIRED",
            "deterministic affirmative closure library did not produce a clean SOURCE_CLOSED boundary",
            source_open_or_repair[0],
        )
    closed_candidates = [
        closure
        for closure in closures
        if closure.get("closure_type") in V8_CLOSURE_TYPES
        and closure.get("closure_status") == "SOURCE_CLOSED"
    ]
    if not closed_candidates:
        return _v9_resolution_failure(
            blocker,
            "PRESERVED_NO_SOURCE_CLOSED_CLOSURE",
            "no deterministic SOURCE_CLOSED affirmative closure is available",
        )
    results = [
        _v9_resolve_generic_blocker_from_affirmative_closure(blocker, closure)
        for closure in closed_candidates
    ]
    resolved = next(
        (
            item
            for item in results
            if item.get("resolution_status") == "RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE"
        ),
        None,
    )
    if resolved:
        return resolved
    return results[0]



def _blocker_matches_affirmative_closure(
    blocker: dict,
    closure: dict,
) -> bool:
    if closure.get("closure_status") != "SOURCE_CLOSED":
        return False
    if closure.get("closure_type") in V8_CLOSURE_TYPES:
        if not closure.get("instance_binding_clean"):
            return False
        if not _is_generic_exact_support_blocker(blocker):
            return False
        if _blocker_has_unaccounted_content(blocker):
            return False
        blocker_dimensions = _blocker_asserted_dimensions(blocker)
        closure_dimensions = _closure_verified_dimensions(closure)
        if not _v9_required_field_tuple_matches(closure):
            return False
        return _v9_dimensions_covered_by_table(blocker_dimensions, closure_dimensions)
    if _blocker_has_unaccounted_content(blocker):
        return False
    blocker_dimensions = _blocker_asserted_dimensions(blocker)
    closure_dimensions = _closure_verified_dimensions(closure)
    if blocker_dimensions:
        return blocker_dimensions.issubset(closure_dimensions)
    return False


def _suppress_false_blockers(blockers: list[dict], gate: dict) -> tuple[list[dict], list[dict]]:
    active: list[dict] = []
    suppressed: list[dict] = []
    closures = gate.get("affirmative_closure_ledger") or []
    for blocker in blockers:
        closure = next(
            (
                item
                for item in closures
                if _blocker_matches_affirmative_closure(blocker, item)
            ),
            None,
        )
        if closure:
            suppressed.append(
                {
                    "blocker_id": blocker.get("blocker_id"),
                    "source_artifact_id": blocker.get("source_artifact_id"),
                    "blocker_type": blocker.get("blocker_type"),
                    "blocker_text": blocker.get("blocker_text"),
                    "suppression_reason": "source-visible affirmative closure contradicts worker blocker",
                    "contradicting_closure_id": closure.get("closure_id"),
                    "closure_type": closure.get("closure_type"),
                    "source_ids": closure.get("source_ids") or [],
                }
            )
        else:
            active.append(blocker)
    return active, suppressed


def _deterministic_dependency_checks(payload: dict) -> list[dict]:
    """Source-derived checks for computable action-boundary seams.

    These checks use only model-visible source text. They do not read packet
    truth, sibling labels, scoring maps, or legacy IDs.
    """
    docs = _source_documents(payload)
    checks: list[dict] = []
    checks.extend(_authority_scope_dependency_checks(payload))

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
            "AFFIRMATIVE CLOSURE LEDGER:",
            json.dumps(baton.get("affirmative_closure_ledger", state.get("affirmative_closure_ledger", [])), sort_keys=True),
            "SUPPRESSED FALSE BLOCKER LEDGER:",
            json.dumps(baton.get("suppressed_false_blocker_ledger", state.get("suppressed_false_blocker_ledger", [])), sort_keys=True),
            "DETERMINISTIC GENERIC BLOCKER RESOLUTION LEDGER:",
            json.dumps(
                baton.get(
                    "deterministic_generic_blocker_resolution_ledger",
                    state.get("deterministic_generic_blocker_resolution_ledger", []),
                ),
                sort_keys=True,
            ),
            "PACKET REPAIR REQUIRED LEDGER:",
            json.dumps(baton.get("packet_repair_required_ledger", state.get("packet_repair_required_ledger", [])), sort_keys=True),
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
    suppressed_false_blockers = gate.get("suppressed_false_blocker_ledger") or []
    generic_resolutions = gate.get("deterministic_generic_blocker_resolution_ledger") or []
    packet_repair_required = gate.get("packet_repair_required_ledger") or []
    if closure_failures:
        ids = ",".join(str(item.get("blocker_id")) for item in closure_failures[:3])
        repair_target = f"repair invalid blocker closure before ALLOW: {ids}"
        blocked_move = "do not accept textual blocker closure without matching source fields"
    elif packet_repair_required:
        ids = ",".join(str(item.get("closure_id")) for item in packet_repair_required[:3])
        repair_target = f"packet repair required before clean proof: {ids}"
        blocked_move = "do not turn underspecified source fields into ALLOW"
    elif prior_unresolved:
        ids = ",".join(str(blocker.get("blocker_id")) for blocker in prior_unresolved[:3])
        repair_target = f"resolve prior blocker ids before ALLOW: {ids}"
        blocked_move = "do not silently drop source-grounded blockers"
    elif dependency_failures:
        first = dependency_failures[0]
        repair_target = f"resolve dependency mismatch: {first.get('summary', first.get('check_id'))}"
        blocked_move = "do not collapse separate required controls into general approval"
    elif blockers_found:
        ids = ",".join(str(blocker.get("blocker_id")) for blocker in blockers_found[:3])
        repair_target = f"stress-test and preserve blocker ids: {ids}"
        blocked_move = "do not override blocker with consensus unless sources close it"
    elif suppressed_false_blockers:
        ids = ",".join(str(item.get("blocker_id")) for item in suppressed_false_blockers[:3])
        repair_target = f"use affirmative closure ledger; suppressed false blockers: {ids}"
        blocked_move = "do not preserve suppressed false blocker"
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
        "affirmative_closure_ledger": gate.get("affirmative_closure_ledger", []),
        "suppressed_false_blocker_ledger": suppressed_false_blockers,
        "deterministic_generic_blocker_resolution_ledger": generic_resolutions,
        "packet_repair_required_ledger": packet_repair_required,
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
        "affirmative_closure_ledger": selected.get("affirmative_closure_ledger", []),
        "suppressed_false_blocker_ledger": selected.get("suppressed_false_blocker_ledger", []),
        "deterministic_generic_blocker_resolution_ledger": selected.get(
            "deterministic_generic_blocker_resolution_ledger",
            [],
        ),
        "packet_repair_required_ledger": selected.get("packet_repair_required_ledger", []),
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
    (
        resolved_prior,
        unresolved_prior,
        blocker_failures,
        closure_results,
        generic_resolution_results,
    ) = _resolve_prior_blockers(
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
    affirmative_checks = _deterministic_affirmative_allow_support_checks(payload)
    affirmative_failures = [
        check
        for check in affirmative_checks
        if parsed.get("verification_verdict") in {"ALLOW", "ESCALATE"}
        and check.get("required_verdict") in {"ALLOW", "ESCALATE"}
        and parsed.get("verification_verdict") != check.get("required_verdict")
    ]
    for check in affirmative_failures:
        failures.append(f"deterministic_affirmative_closure_mismatch:{check['closure_id']}")
    packet_repair_required = [
        check
        for check in affirmative_checks
        if check.get("closure_status") == "PACKET_REPAIR_REQUIRED"
    ]
    for check in packet_repair_required:
        failures.append(f"packet_repair_required:{check['closure_id']}")
    return {
        "gate_name": "HOLOVERIFY_BLIND_STRUCTURAL_GATE_V2_V9_GENERIC_BLOCKER_RESOLUTION",
        "passed": not failures,
        "failures": failures,
        "warnings": warnings,
        "source_id_count": len(cited),
        "invented_source_ids": invented,
        "deterministic_dependency_checks": dependency_checks,
        "deterministic_dependency_failures": dependency_failures,
        "deterministic_dependency_blockers": [],
        "affirmative_closure_ledger": affirmative_checks,
        "affirmative_closure_failures": affirmative_failures,
        "affirmative_closure_blockers": [],
        "packet_repair_required_ledger": packet_repair_required,
        "suppressed_false_blocker_ledger": [],
        "worker_blockers_before_suppression": [],
        "prior_blockers_in": active_blockers,
        "resolved_prior_blockers": resolved_prior,
        "unresolved_prior_blockers": unresolved_prior,
        "closure_validation_results": closure_results,
        "closure_validation_failures": closure_failures,
        "deterministic_generic_blocker_resolution_ledger": generic_resolution_results,
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
    affirmative_closures = gate.get("affirmative_closure_ledger") or []
    affirmative_source_closed_count = sum(
        1 for item in affirmative_closures if item.get("closure_status") == "SOURCE_CLOSED"
    )
    suppressed_false_blocker_count = len(gate.get("suppressed_false_blocker_ledger") or [])
    packet_repair_required_count = len(gate.get("packet_repair_required_ledger") or [])
    active_blockers_found = gate.get("blockers_found") or []
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
        "deterministic_clean": not any(
            failure.startswith("deterministic_dependency_mismatch:")
            or failure.startswith("deterministic_affirmative_closure_mismatch:")
            or failure.startswith("packet_repair_required:")
            for failure in failures
        ),
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
        "blockers_found_count": len(active_blockers_found),
        "affirmative_closure_count": len(affirmative_closures),
        "affirmative_source_closed_count": affirmative_source_closed_count,
        "suppressed_false_blocker_count": suppressed_false_blocker_count,
        "packet_repair_required_count": packet_repair_required_count,
        "false_blocker_only_escalate": bool(
            verdict == "ESCALATE"
            and suppressed_false_blocker_count > 0
            and not active_blockers_found
            and affirmative_source_closed_count > 0
        ),
        "source_boundary_open_with_blocker": bool(
            verdict == "ESCALATE"
            and parsed.get("binding_class") == "SOURCE_BOUNDARY_OPEN"
            and active_blockers_found
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
        1 if artifact.get("packet_unresolved_blocker_symmetry_clean", True) else 0,
        int(artifact.get("affirmative_closure_count") or 0),
        -int(artifact.get("suppressed_false_blocker_count") or 0),
        -int(artifact.get("packet_repair_required_count") or 0),
        0 if artifact.get("false_blocker_only_escalate") else 1,
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
            artifact.get("packet_unresolved_blocker_symmetry_clean", True),
            not artifact.get("false_blocker_only_escalate"),
            int(artifact.get("packet_repair_required_count") or 0) == 0,
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
            artifact.get("packet_unresolved_blocker_symmetry_clean", True),
            not artifact.get("false_blocker_only_escalate"),
            int(artifact.get("packet_repair_required_count") or 0) == 0,
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


def _apply_packet_unresolved_blocker_symmetry(
    artifacts: list[dict],
    unresolved_blockers: Iterable[dict],
) -> list[dict]:
    unresolved = [blocker for blocker in unresolved_blockers if blocker]
    unresolved_ids = [str(blocker.get("blocker_id")) for blocker in unresolved if blocker.get("blocker_id")]
    enriched: list[dict] = []
    for artifact in artifacts:
        item = dict(artifact)
        verdict = str(item.get("verification_verdict") or "")
        unresolved_count = len(unresolved) if verdict == "ALLOW" else 0
        item["packet_unresolved_active_blocker_count"] = unresolved_count
        item["packet_unresolved_active_blocker_ids"] = unresolved_ids if verdict == "ALLOW" else []
        item["packet_unresolved_blocker_symmetry_clean"] = verdict != "ALLOW" or unresolved_count == 0
        if verdict == "ALLOW" and unresolved_count:
            item["unresolved_blocker_count"] = max(
                int(item.get("unresolved_blocker_count") or 0),
                unresolved_count,
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


def _build_failed_worker_call_row(
    packet_id: str,
    role: str,
    idx: int,
    messages: list[dict],
    failure_tag: str,
    raw: str = "",
) -> dict:
    return {
        "packet_id": packet_id,
        "call_kind": "worker",
        "role": role,
        "turn_index": idx,
        "prompt_sha256": _sha256_text(json.dumps(messages, sort_keys=True)),
        "raw_output_sha256": _sha256_text(raw),
        "transport_called": True,
        "failure": failure_tag,
    }


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
    out_path.mkdir(parents=True, exist_ok=True)
    prompt_dir = out_path / "prompts"
    packet_id = str(payload.get("packet_id", "PKT-OPAQUE"))
    state = {
        "packet_id": packet_id,
        "turns_completed": [],
        "unresolved_dependencies": [],
        "unresolved_blockers": [],
        "affirmative_closure_ledger": [],
        "suppressed_false_blocker_ledger": [],
        "deterministic_generic_blocker_resolution_ledger": [],
        "packet_repair_required_ledger": [],
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
        try:
            raw = _call_transport(transport, messages, retry_log) if transport else _next_transcript(transcripts, idx)
        except BlindRunnerContentFailure as exc:
            failure_tag = str(exc)
            call_rows.append(
                _build_failed_worker_call_row(
                    packet_id,
                    role,
                    idx + 1,
                    messages,
                    failure_tag,
                )
            )
            result = _invalid_content_contract_result(
                packet_id=packet_id,
                out_path=out_path,
                failed_slot=role,
                failure_tag=failure_tag,
                failure_call=json.dumps(call_rows[-1], sort_keys=True),
                prompts=prompts,
                worker_rows=worker_rows,
                gov_rows=gov_rows,
                call_rows=call_rows,
                retry_log=retry_log,
            )
            out_path.mkdir(parents=True, exist_ok=True)
            (out_path / "invalid_packet.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n",
            )
            return result
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
        deterministic_blockers = _deterministic_blockers_from_dependency_failures(row, gate)
        affirmative_blockers = _deterministic_blockers_from_affirmative_failures(row, gate)
        worker_blockers = _blockers_from_parsed(row, parsed, payload)
        active_worker_blockers, suppressed_false_blockers = _suppress_false_blockers(worker_blockers, gate)
        gate["deterministic_dependency_blockers"] = deterministic_blockers
        gate["affirmative_closure_blockers"] = affirmative_blockers
        gate["worker_blockers_before_suppression"] = worker_blockers
        gate["suppressed_false_blocker_ledger"] = suppressed_false_blockers
        gate["blockers_found"] = active_worker_blockers + deterministic_blockers + affirmative_blockers
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
        if gate.get("affirmative_closure_ledger"):
            seen_closures = {
                str(item.get("closure_id"))
                for item in state.get("affirmative_closure_ledger", [])
            }
            for item in gate.get("affirmative_closure_ledger") or []:
                closure_id = str(item.get("closure_id"))
                if closure_id not in seen_closures:
                    state["affirmative_closure_ledger"].append(item)
                    seen_closures.add(closure_id)
        if gate.get("suppressed_false_blocker_ledger"):
            state["suppressed_false_blocker_ledger"].extend(gate.get("suppressed_false_blocker_ledger") or [])
        if gate.get("deterministic_generic_blocker_resolution_ledger"):
            state["deterministic_generic_blocker_resolution_ledger"].extend(
                gate.get("deterministic_generic_blocker_resolution_ledger") or []
            )
        if gate.get("packet_repair_required_ledger"):
            seen_repairs = {
                str(item.get("closure_id"))
                for item in state.get("packet_repair_required_ledger", [])
            }
            for item in gate.get("packet_repair_required_ledger") or []:
                closure_id = str(item.get("closure_id"))
                if closure_id not in seen_repairs:
                    state["packet_repair_required_ledger"].append(item)
                    seen_repairs.add(closure_id)
        if gate.get("closure_validation_failures"):
            state["invalid_closure_ledger"] = gate.get("closure_validation_failures")
        state["turns_completed"].append(
            {
                "role": role,
                "artifact_id": row["artifact_id"],
                "gate_passed": gate["passed"],
                "blockers_found": gate.get("blockers_found") or [],
                "worker_blockers_before_suppression": gate.get("worker_blockers_before_suppression") or [],
                "suppressed_false_blocker_ledger": gate.get("suppressed_false_blocker_ledger") or [],
                "deterministic_generic_blocker_resolution_ledger": gate.get("deterministic_generic_blocker_resolution_ledger") or [],
                "affirmative_closure_ledger": gate.get("affirmative_closure_ledger") or [],
                "packet_repair_required_ledger": gate.get("packet_repair_required_ledger") or [],
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
                    "affirmative_closure_ledger": selected.get("affirmative_closure_ledger", []),
                    "suppressed_false_blocker_ledger": selected.get("suppressed_false_blocker_ledger", []),
                    "deterministic_generic_blocker_resolution_ledger": selected.get(
                        "deterministic_generic_blocker_resolution_ledger",
                        [],
                    ),
                    "packet_repair_required_ledger": selected.get("packet_repair_required_ledger", []),
                    "previous_gate_passed": gate["passed"],
                }

    artifacts = _apply_packet_unresolved_blocker_symmetry(
        artifacts,
        state.get("unresolved_blockers") or [],
    )
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
        "packet_status": "SELECTED",
        "contract_failure_marker": False,
        "packet_failure_slot": None,
        "packet_failure_tag": None,
        "packet_failure_call": None,
        "packet_selectable": bool(selection.get("selected_artifact_id")),
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
        try:
            result = run_blind_fixture(
                payload,
                [],
                str(packet_out),
                transport=transport,
                call_gov_transport=True,
            )
        except Exception as exc:
            # Unexpected transport or runner failures abort the lane; they are not
            # converted into content-contract invalid states.
            raise RuntimeError(f"fixture execution failed for packet {payload.get('packet_id')}: {exc}") from exc
        packet_results.append(
            {
                "packet_id": payload.get("packet_id"),
                "final": result.get("final"),
                "selection": result.get("selection"),
                "packet_status": result.get("packet_status", "SELECTED"),
                "contract_failure_marker": result.get("contract_failure_marker", False),
                "packet_failure_slot": result.get("packet_failure_slot"),
                "packet_failure_tag": result.get("packet_failure_tag"),
                "packet_failure_call": result.get("packet_failure_call"),
                "packet_selectable": result.get("packet_selectable", True),
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
