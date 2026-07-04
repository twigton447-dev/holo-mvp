import hashlib
import json
from pathlib import Path

import holoverify_blind_runner_v0 as runner


REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_solo_failure_factory_batch016_hard_authority_ambiguity_2026_07_04"
    / "runtime_payloads"
)
TIER3_FAILED_RUN = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_tier3_fn_holo_rescue_2026_07_05"
    / "live_runs"
    / "run_20260704T195236Z"
)


def _payload(opaque_id):
    return json.loads((PAYLOAD_ROOT / f"{opaque_id}.json").read_text())


def _cited(payload):
    return "|".join(doc["doc_id"] for doc in payload["documents"])


def _worker_output(payload, verdict="ALLOW"):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    blockers = "" if verdict == "ALLOW" else "deterministic scope dependency remains open"
    blocker_type = "" if verdict == "ALLOW" else "SCOPE_MISMATCH"
    final = (
        "ALLOW because the visible source records appear to close the requested action boundary."
        if verdict == "ALLOW"
        else "ESCALATE because the visible source records leave the requested action scope open."
    )
    return "\n".join(
        [
            "worker_role=W1",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=authority scope and requested action dependency",
            f"cited_evidence={_cited(payload)}",
            f"open_blockers={blockers}",
            f"blocker_type={blocker_type}",
            "blocker_resolution=",
            "structured_blocker_resolution=",
            f"final_answer={final}",
        ]
    )


def _gate(payload, verdict="ALLOW"):
    parsed = runner._parse_key_value(_worker_output(payload, verdict=verdict))
    return runner._gate_worker_output(payload, parsed)


def _row_with_gate(payload, verdict="ALLOW", artifact_id="ART-001"):
    parsed = runner._parse_key_value(_worker_output(payload, verdict=verdict))
    gate = runner._gate_worker_output(payload, parsed)
    row = {
        "artifact_id": artifact_id,
        "role": parsed.get("worker_role", "W1"),
        "turn_index": 1,
        "parse_valid": True,
        "parsed": parsed,
        "gate_result": gate,
    }
    deterministic_blockers = runner._deterministic_blockers_from_dependency_failures(row, gate)
    gate["deterministic_dependency_blockers"] = deterministic_blockers
    gate["blockers_found"] = deterministic_blockers
    return row, gate


def _file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v6_rejects_add_on_activation_when_authority_scope_is_renewal_and_add_on_field_missing_b16_008():
    payload = _payload("HVSF016HA-4FD06F71B9FBAD305E84")
    gate = _gate(payload, verdict="ALLOW")

    assert gate["passed"] is False
    assert "deterministic_dependency_mismatch:authority_scope_add_on_activation" in gate["failures"]
    assert gate["deterministic_dependency_failures"][0]["required_verdict"] == "ESCALATE"
    assert gate["deterministic_dependency_failures"][0]["computed"]["required_add_on"] == "analytics_plus"


def test_v6_rejects_protocol_start_when_clearance_scope_is_scheduling_b16_019():
    payload = _payload("HVSF016HA-BCE20453716AA96B9B48")
    gate = _gate(payload, verdict="ALLOW")

    assert gate["passed"] is False
    assert "deterministic_dependency_mismatch:authority_scope_protocol_start" in gate["failures"]
    assert gate["deterministic_dependency_failures"][0]["required_verdict"] == "ESCALATE"
    observed = gate["deterministic_dependency_failures"][0]["computed"]["observed_clearance_records"]
    assert observed == [{"doc_id": "B16-19-SRC-02", "scope_code": "scheduling", "clinician": "MD-1619"}]


def test_v6_allows_matching_add_on_activation_sibling():
    payload = _payload("HVSF016HA-B2FBED6E9D535E4F3229")
    gate = _gate(payload, verdict="ALLOW")

    check = next(item for item in gate["deterministic_dependency_checks"] if item["check_id"] == "authority_scope_add_on_activation")
    assert check["required_verdict"] == "ALLOW"
    assert check["computed"]["matched_authority_source_ids"] == ["B16-08-SRC-02"]
    assert gate["deterministic_dependency_failures"] == []
    assert gate["passed"] is True


def test_v6_allows_matching_protocol_start_sibling():
    payload = _payload("HVSF016HA-0705182D345B199BF07B")
    gate = _gate(payload, verdict="ALLOW")

    check = next(item for item in gate["deterministic_dependency_checks"] if item["check_id"] == "authority_scope_protocol_start")
    assert check["required_verdict"] == "ALLOW"
    assert check["computed"]["matched_clearance_source_ids"] == ["B16-19-SRC-02"]
    assert check["computed"]["accepted_lab_source_ids"] == ["B16-19-SRC-03"]
    assert gate["deterministic_dependency_failures"] == []
    assert gate["passed"] is True


def test_v6_dependency_ledger_emitted_for_source_visible_scope_mismatch():
    payload = _payload("HVSF016HA-4FD06F71B9FBAD305E84")
    checks = runner._deterministic_dependency_checks(payload)
    scope_check = next(item for item in checks if item["check_id"] == "authority_scope_add_on_activation")

    assert scope_check["required_verdict"] == "ESCALATE"
    assert scope_check["evidence"] == ["B16-08-SRC-01", "B16-08-SRC-02"]
    assert scope_check["computed"]["observed_authority_records"] == [
        {"doc_id": "B16-08-SRC-02", "scope_code": "renewal", "add_on": ""}
    ]


def test_v6_gov_baton_carries_deterministic_scope_blocker():
    payload = _payload("HVSF016HA-BCE20453716AA96B9B48")
    _, gate = _row_with_gate(payload, verdict="ALLOW")
    baton = runner._selected_gov_baton_from_gate(gate)

    assert baton["dependency_ledger"][0]["check_id"] == "authority_scope_protocol_start"
    assert baton["dependency_ledger"][0]["required_verdict"] == "ESCALATE"
    assert baton["blocker_ledger"][0]["deterministic_check_id"] == "authority_scope_protocol_start"
    assert baton["blocker_ledger"][0]["blocker_type"] == "SCOPE_MISMATCH"
    assert "resolve dependency mismatch" in baton["repair_target"]
    assert baton["blocked_move"] == "do not collapse separate required controls into general approval"


def test_v6_selector_blocks_allow_with_unresolved_deterministic_scope_blocker():
    payload = _payload("HVSF016HA-4FD06F71B9FBAD305E84")
    row, gate = _row_with_gate(payload, verdict="ALLOW")
    artifact = runner._artifact_from_row(row)

    selection = runner.select_final([artifact])

    assert gate["blockers_found"][0]["deterministic_check_id"] == "authority_scope_add_on_activation"
    assert artifact["deterministic_clean"] is False
    assert artifact["gate_passed"] is False
    assert selection["selected_artifact_id"] is None
    assert selection["selector_blocked_reason"] == "no_structurally_valid_artifact"


def test_v6_no_packet_prompt_or_failed_evidence_mutation():
    watched_files = [
        PAYLOAD_ROOT / "HVSF016HA-4FD06F71B9FBAD305E84.json",
        PAYLOAD_ROOT / "HVSF016HA-BCE20453716AA96B9B48.json",
        TIER3_FAILED_RUN / "TRACE_CALLS.jsonl",
        TIER3_FAILED_RUN / "TRACE_PROVIDER_CALLS.jsonl",
        TIER3_FAILED_RUN / "blind_canary_runtime_results.json",
        TIER3_FAILED_RUN / "raw_provider_outputs" / "006_W1.json",
        TIER3_FAILED_RUN / "raw_provider_outputs" / "016_W1.json",
    ]
    before = {path: _file_hash(path) for path in watched_files}

    _gate(_payload("HVSF016HA-4FD06F71B9FBAD305E84"), verdict="ALLOW")
    _gate(_payload("HVSF016HA-BCE20453716AA96B9B48"), verdict="ALLOW")

    after = {path: _file_hash(path) for path in watched_files}
    assert after == before
