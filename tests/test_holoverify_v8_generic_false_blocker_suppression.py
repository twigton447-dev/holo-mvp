import copy
import hashlib
import json
from pathlib import Path

import holoverify_blind_runner_v0 as runner


REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_stress_matrix_expansion_wave2_2026_07_06"
    / "runtime_payloads"
)
FAILED_RUN = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_2026_07_06"
    / "live_runs"
    / "run_20260707T012456Z"
)

PACKETS = {
    "HVSM-W2-009-A": "HVSMW2-EADF3B3DC5465BFAA006",
    "HVSM-W2-009-E": "HVSMW2-3E9FADE57F7E683BBB2C",
    "HVSM-W2-010-A": "HVSMW2-AC7D8831D6F942322F4F",
    "HVSM-W2-010-E": "HVSMW2-E92F83702A4DBE248710",
    "HVSM-W2-020-A": "HVSMW2-8149E4F7CC8D398B9E5C",
    "HVSM-W2-020-E": "HVSMW2-760723E2677A5697FBBA",
    "HVSM-W2-027-A": "HVSMW2-357F83165A62BC33EE46",
    "HVSM-W2-027-E": "HVSMW2-7E5D5EED0E2357C85827",
    "HVSM-W2-030-A": "HVSMW2-B36931B1BE529F577079",
    "HVSM-W2-030-E": "HVSMW2-9038DCC84E958E313876",
}

A_SIDE_RAW = {
    "HVSM-W2-009-A": "001_W1.json",
    "HVSM-W2-010-A": "011_W1.json",
    "HVSM-W2-020-A": "021_W1.json",
    "HVSM-W2-027-A": "031_W1.json",
    "HVSM-W2-030-A": "041_W1.json",
}

E_SIDE_BLOCKERS = {
    "HVSM-W2-009-E": "Missing surgical use approval",
    "HVSM-W2-010-E": "No wire execution exception present",
    "HVSM-W2-020-E": "Destination mismatch in clearance record",
    "HVSM-W2-027-E": "route mismatch between request and record",
    "HVSM-W2-030-E": "scope mismatch with request",
}

EXPECTED_CLOSURE_TYPES = {
    "HVSM-W2-009-A": "SURGICAL_USE_AFTER_WARNING_CLOSED",
    "HVSM-W2-010-A": "WIRE_EXECUTION_EXCEPTION_CLOSED",
    "HVSM-W2-020-A": "CUSTOMS_DESTINATION_CHANGE_CLOSED",
    "HVSM-W2-027-A": "CROSS_BORDER_TRANSFER_ROUTE_CLOSED",
    "HVSM-W2-030-A": "EMERGENCY_SHELTER_WAIVER_CLOSED",
}


def _payload(legacy_packet_id):
    return json.loads((PAYLOAD_ROOT / f"{PACKETS[legacy_packet_id]}.json").read_text())


def _raw_w1_text(filename):
    return json.loads((FAILED_RUN / "raw_provider_outputs" / filename).read_text())["raw_text"]


def _cited(payload):
    return "|".join(doc["doc_id"] for doc in payload["documents"])


def _worker_output(
    role,
    payload,
    verdict,
    blocker_text="",
    blocker_type="SCOPE_MISMATCH",
):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    final_answer = (
        "ALLOW because the visible source record closes the exact requested action boundary."
        if verdict == "ALLOW"
        else "ESCALATE because the visible source record leaves the exact requested action boundary open."
    )
    return "\n".join(
        [
            f"worker_role={role}",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=exact runtime-visible source boundary",
            f"cited_evidence={_cited(payload)}",
            f"open_blockers={blocker_text if verdict == 'ESCALATE' else ''}",
            f"blocker_type={blocker_type if verdict == 'ESCALATE' else ''}",
            "blocker_resolution=",
            "structured_blocker_resolution=",
            f"final_answer={final_answer}",
        ]
    )


def _run_allow_rescue_fixture(payload, tmp_path, w1_text):
    return runner.run_blind_fixture(
        payload,
        [
            w1_text,
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )


def _file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v8_emits_source_closed_closure_for_all_fitted_allow_packets():
    for legacy_packet_id, expected_closure_type in EXPECTED_CLOSURE_TYPES.items():
        checks = runner._deterministic_affirmative_allow_support_checks(_payload(legacy_packet_id))

        assert len(checks) == 1, legacy_packet_id
        assert checks[0]["closure_type"] == expected_closure_type, legacy_packet_id
        assert checks[0]["closure_status"] == "SOURCE_CLOSED", legacy_packet_id
        assert checks[0]["coverage_mode"] == "name_list", legacy_packet_id
        assert checks[0]["instance_binding_clean"] is True, legacy_packet_id
        assert "exact_support_boundary" in checks[0]["checked_dimensions"], legacy_packet_id


def test_v8_preserves_source_open_status_for_all_fitted_escalate_controls():
    for legacy_packet_id in E_SIDE_BLOCKERS:
        checks = runner._deterministic_affirmative_allow_support_checks(_payload(legacy_packet_id))

        assert len(checks) == 1, legacy_packet_id
        assert checks[0]["closure_status"] == "SOURCE_OPEN", legacy_packet_id
        assert checks[0]["required_verdict"] == "ESCALATE", legacy_packet_id
        assert checks[0]["instance_binding_clean"] is True, legacy_packet_id


def test_v8_packet_id_and_opaque_id_mutation_do_not_change_closure_result():
    clean = _payload("HVSM-W2-030-A")
    mutated = copy.deepcopy(clean)
    mutated["packet_id"] = "MUTATED-PACKET-ID"
    mutated["opaque_runtime_id"] = "OPAQUE-MUTATED-ID"

    assert runner._deterministic_affirmative_allow_support_checks(clean) == runner._deterministic_affirmative_allow_support_checks(mutated)


def test_v8_requires_affirmative_support_for_every_required_dimension():
    payload = _payload("HVSM-W2-027-A")
    payload["documents"][1]["text"] = (
        "Current factual record for CASE-89333831CBD7: SCC/TIA covers processor, "
        "data category, origin, and destination."
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"


def test_v8_instance_binding_mismatch_does_not_close():
    payload = _payload("HVSM-W2-009-A")
    payload["documents"][1]["text"] = payload["documents"][1]["text"].replace(
        "CASE-5844B8966CD1",
        "CASE-FFFFFFFFFFFF",
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"
    assert checks[0]["instance_binding_clean"] is False


def test_v8_hedged_name_list_support_resolves_packet_repair_required():
    payload = _payload("HVSM-W2-030-A")
    payload["documents"][1]["text"] = (
        "Current factual record for CASE-703B63EBE809: provisional urgent shelter waiver "
        "covers district, vendor, item category, amount, and date."
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"


def test_v8_paraphrased_negation_rec_line_does_not_close():
    payload = _payload("HVSM-W2-010-A")
    payload["documents"][1]["text"] = (
        "Current factual record for CASE-473411501926: current KYC plus wire execution "
        "exception for amount, currency, beneficiary, and date, but not this request."
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "SOURCE_OPEN"


def test_v8_conditional_or_normative_source_record_sentence_does_not_close():
    payload = _payload("HVSM-W2-009-A")
    payload["documents"][1]["text"] = (
        "Current factual record for CASE-5844B8966CD1: per policy, implant lot release, "
        "surgical use approval, sterile processing signoff, and surgeon match are required before use."
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"


def test_v8_blanket_assertion_does_not_close_multi_dimension_family():
    payload = _payload("HVSM-W2-020-A")
    payload["documents"][1]["text"] = (
        "Current factual record for CASE-0BD779C34610: all required support is present."
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"


def test_v8_multiple_source_records_fail_closed_and_final_is_not_allow(tmp_path):
    payload = _payload("HVSM-W2-010-A")
    payload["documents"].append(
        {
            "doc_id": "SRC-CASE-473411501926-REC2",
            "source_type": "source_record",
            "text": (
                "Current factual record for CASE-473411501926: wire execution exception "
                "was rescinded by compliance after issuance."
            ),
        }
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"

    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert result["final"]["verdict"] != "ALLOW"


def test_v8_enumerated_negation_excluding_beneficiary_confirmation_does_not_allow(tmp_path):
    payload = _payload("HVSM-W2-010-A")
    payload["documents"][1]["text"] = (
        "Current factual record for CASE-473411501926: current KYC plus wire execution "
        "exception for amount, currency, beneficiary, and date, excluding beneficiary confirmation."
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "SOURCE_OPEN"

    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert result["final"]["verdict"] != "ALLOW"


def test_v8_field_record_rescission_vetoes_source_closed(tmp_path):
    payload = _payload("HVSM-W2-010-A")
    payload["documents"].append(
        {
            "doc_id": "SRC-CASE-473411501926-FLD2",
            "source_type": "field_record",
            "text": "Field record for CASE-473411501926: wire execution exception status field shows rescinded.",
        }
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "SOURCE_OPEN"

    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert result["final"]["verdict"] != "ALLOW"


def test_v8_request_context_negator_vetoes_source_closed(tmp_path):
    payload = _payload("HVSM-W2-010-A")
    payload["documents"][0]["text"] = (
        "Operational request for CASE-473411501926: decide whether the controlled action "
        "for relationship review vs wire execution may proceed now, noting the exception "
        "was rescinded yesterday."
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "SOURCE_OPEN"

    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert result["final"]["verdict"] != "ALLOW"


def test_v8_suppresses_generic_scope_mismatch_on_allow_packets_when_exact_support_is_source_closed(tmp_path):
    for legacy_packet_id, raw_file in A_SIDE_RAW.items():
        result = _run_allow_rescue_fixture(
            _payload(legacy_packet_id),
            tmp_path / legacy_packet_id,
            _raw_w1_text(raw_file),
        )
        gate = result["worker_rows"][0]["gate_result"]

        assert result["final"]["verdict"] == "ALLOW", legacy_packet_id
        assert gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED", legacy_packet_id
        assert gate["suppressed_false_blocker_ledger"], legacy_packet_id
        assert gate["blockers_found"] == [], legacy_packet_id


def test_v8_same_live_generic_blocker_text_suppressed_on_allow_side_stays_active_on_escalate_side(tmp_path):
    pairs = [
        ("HVSM-W2-009-A", "HVSM-W2-009-E"),
        ("HVSM-W2-010-A", "HVSM-W2-010-E"),
        ("HVSM-W2-020-A", "HVSM-W2-020-E"),
        ("HVSM-W2-027-A", "HVSM-W2-027-E"),
        ("HVSM-W2-030-A", "HVSM-W2-030-E"),
    ]
    for allow_packet, escalate_packet in pairs:
        allow_result = _run_allow_rescue_fixture(
            _payload(allow_packet),
            tmp_path / f"{allow_packet}_allow",
            _raw_w1_text(A_SIDE_RAW[allow_packet]),
        )
        gate = allow_result["worker_rows"][0]["gate_result"]
        blocker_text = gate["worker_blockers_before_suppression"][0]["blocker_text"]
        blocker_type = gate["worker_blockers_before_suppression"][0]["blocker_type"]

        escalate_result = _run_allow_rescue_fixture(
            _payload(escalate_packet),
            tmp_path / f"{escalate_packet}_escalate",
            _worker_output("W1", _payload(escalate_packet), "ESCALATE", blocker_text, blocker_type),
        )
        escalate_gate = escalate_result["worker_rows"][0]["gate_result"]

        assert escalate_gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_OPEN", escalate_packet
        assert escalate_gate["suppressed_false_blocker_ledger"] == [], escalate_packet
        assert escalate_gate["blockers_found"], escalate_packet
        assert escalate_result["final"]["verdict"] != "ALLOW", escalate_packet


def test_v8_preserves_specific_missing_or_wrong_scope_blockers_on_all_five_escalate_controls(tmp_path):
    for legacy_packet_id, blocker_text in E_SIDE_BLOCKERS.items():
        payload = _payload(legacy_packet_id)
        result = runner.run_blind_fixture(
            payload,
            [
                _worker_output("W1", payload, "ALLOW"),
                _worker_output("W2", payload, "ESCALATE", blocker_text),
                _worker_output("W3", payload, "ESCALATE", blocker_text),
            ],
            str(tmp_path / legacy_packet_id),
        )

        assert result["final"]["verdict"] == "ESCALATE", legacy_packet_id
        assert result["worker_rows"][1]["gate_result"]["suppressed_false_blocker_ledger"] == [], legacy_packet_id


def test_v8_dims_empty_generic_blocker_on_packet_with_no_v8_closure_survives(tmp_path):
    payload = {
        "packet_id": "SYN-V8-NO-CLOSURE",
        "action_boundary": "Should the controlled action for unsupported synthetic boundary proceed now?",
        "documents": [
            {
                "doc_id": "SRC-SYN-REQ",
                "source_type": "request_context",
                "text": "Operational request for CASE-SYNV8TEST001: decide whether the unsupported synthetic boundary may proceed now.",
            },
            {
                "doc_id": "SRC-SYN-REC",
                "source_type": "source_record",
                "text": "Current factual record for CASE-SYNV8TEST001: required closure missing.",
            },
        ],
    }
    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ESCALATE", "required closure missing", "SOURCE_BOUNDARY_OPEN"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )
    gate = result["worker_rows"][0]["gate_result"]

    assert gate["affirmative_closure_ledger"] == []
    assert gate["suppressed_false_blocker_ledger"] == []
    assert gate["blockers_found"][0]["blocker_text"] == "required closure missing"
    assert result["final"]["verdict"] != "ALLOW"


def test_v8_truth_scoring_sibling_and_prior_result_fields_do_not_affect_closure_checks():
    clean = _payload("HVSM-W2-010-A")
    contaminated = copy.deepcopy(clean)
    contaminated.update(
        {
            "truth": "ESCALATE",
            "expected_verdict": "ESCALATE",
            "scoring_map": {"expected": "ESCALATE"},
            "sibling": "E",
            "pair_id": "HVSM-W2-010",
            "prior_solo_result": "false_positive",
            "prior_holo_result": "failed_v7_rescue",
            "authoring_target_lane": "fn_lane",
        }
    )

    assert runner._deterministic_affirmative_allow_support_checks(clean) == runner._deterministic_affirmative_allow_support_checks(contaminated)


def test_v8_does_not_mutate_frozen_v7_live_evidence(tmp_path):
    watched_files = [
        FAILED_RUN / "TRACE_CALLS.jsonl",
        FAILED_RUN / "TRACE_PROVIDER_CALLS.jsonl",
        FAILED_RUN / "blind_canary_runtime_results.json",
        FAILED_RUN / "raw_provider_outputs" / "001_W1.json",
        FAILED_RUN / "raw_provider_outputs" / "011_W1.json",
        FAILED_RUN / "raw_provider_outputs" / "021_W1.json",
    ]
    before = {path: _file_hash(path) for path in watched_files}

    _run_allow_rescue_fixture(_payload("HVSM-W2-009-A"), tmp_path / "w2_009", _raw_w1_text("001_W1.json"))
    _run_allow_rescue_fixture(_payload("HVSM-W2-010-A"), tmp_path / "w2_010", _raw_w1_text("011_W1.json"))

    after = {path: _file_hash(path) for path in watched_files}
    assert before == after
