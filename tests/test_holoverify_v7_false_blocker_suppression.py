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
    / "holoverify_stress_matrix_expansion_wave1_2026_07_05"
    / "runtime_payloads"
)
FAILED_RUN = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_2026_07_05"
    / "live_runs"
    / "run_20260705T232606Z"
)

PACKETS = {
    "HVSM-W1-009-A": "HVSMW1-316A3AE43F672C195074",
    "HVSM-W1-009-E": "HVSMW1-03C30A6F1E979B8E83F2",
    "HVSM-W1-011-A": "HVSMW1-69783CD745C350A4E102",
    "HVSM-W1-011-E": "HVSMW1-23E475812EFFC431B231",
    "HVSM-W1-019-A": "HVSMW1-C88BFEC273EB0852CB10",
    "HVSM-W1-019-E": "HVSMW1-A429A3E0E82B25839382",
}


def _payload(legacy_packet_id):
    return json.loads((PAYLOAD_ROOT / f"{PACKETS[legacy_packet_id]}.json").read_text())


def _cited(payload):
    return "|".join(doc["doc_id"] for doc in payload["documents"])


def _worker_output(
    role,
    payload,
    verdict,
    blocker_text="",
    blocker_type="SCOPE_MISMATCH",
    blocker_resolution="",
    structured_blocker_resolution="",
):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    blocker_value = blocker_text if verdict == "ESCALATE" else ""
    emitted_blocker_type = blocker_type if blocker_value else ""
    final_answer = (
        "ALLOW because the visible source records close the requested action boundary."
        if verdict == "ALLOW"
        else "ESCALATE because the visible source records leave the requested action boundary open."
    )
    return "\n".join(
        [
            f"worker_role={role}",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=exact authority and action boundary",
            f"cited_evidence={_cited(payload)}",
            f"open_blockers={blocker_value}",
            f"blocker_type={emitted_blocker_type}",
            f"blocker_resolution={blocker_resolution}",
            f"structured_blocker_resolution={structured_blocker_resolution}",
            f"final_answer={final_answer}",
        ]
    )


def _run_false_blocker_fixture(payload, tmp_path, blocker_text):
    transcripts = [
        _worker_output("W1", payload, "ESCALATE", blocker_text),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]
    return runner.run_blind_fixture(payload, transcripts, str(tmp_path))


def _synthetic_payload(action_boundary, source_texts):
    documents = [
        {
            "doc_id": f"SRC-SYN-{idx:02d}",
            "source_type": "source_record" if text.lower().startswith("current source record") else "request_context" if text.lower().startswith("request context") else "policy_control",
            "text": text,
        }
        for idx, text in enumerate(source_texts, start=1)
    ]
    documents.extend(
        [
            {
                "doc_id": "SRC-SYN-FLD",
                "source_type": "field_record",
                "text": "Visible decision fields for this case are printed in the source records.",
            },
            {
                "doc_id": "SRC-SYN-POL",
                "source_type": "policy_control",
                "text": "Policy: the action may proceed only when visible source records close the exact requested action boundary.",
            },
        ]
    )
    return {
        "packet_id": "SYN-V7-FABLE-COUNTEREXAMPLE",
        "domain": "Synthetic V7 counterexample",
        "action_boundary": action_boundary,
        "communication_boundary": "Use exact visible source fields only.",
        "documents": documents,
    }


def _synthetic_payload_docs(action_boundary, docs):
    return {
        "packet_id": "SYN-V7-FABLE-COUNTEREXAMPLE-DOCS",
        "domain": "Synthetic V7 counterexample",
        "action_boundary": action_boundary,
        "communication_boundary": "Use exact visible source fields only.",
        "documents": docs,
    }


def _file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _raw_w1_text(filename):
    return json.loads((FAILED_RUN / "raw_provider_outputs" / filename).read_text())["raw_text"]


def test_v7_suppresses_false_blocker_hvsm_w1_009_a(tmp_path):
    result = _run_false_blocker_fixture(
        _payload("HVSM-W1-009-A"),
        tmp_path,
        "final filing counsel signoff is missing",
    )
    gate = result["worker_rows"][0]["gate_result"]

    assert result["final"]["verdict"] == "ALLOW"
    assert gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED"
    assert gate["affirmative_closure_ledger"][0]["closure_type"] == "FINAL_FILING_AUTHORITY"
    assert gate["blockers_found"] == []
    assert len(gate["suppressed_false_blocker_ledger"]) == 1
    assert "deterministic_affirmative_closure_mismatch:" in "|".join(gate["failures"])


def test_v7_suppresses_false_blocker_hvsm_w1_011_a(tmp_path):
    result = _run_false_blocker_fixture(
        _payload("HVSM-W1-011-A"),
        tmp_path,
        "termination notice signer authority is missing",
    )
    gate = result["worker_rows"][0]["gate_result"]

    assert result["final"]["verdict"] == "ALLOW"
    assert gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED"
    assert gate["affirmative_closure_ledger"][0]["closure_type"] == "TERMINATION_NOTICE_AUTHORITY"
    assert gate["blockers_found"] == []
    assert len(gate["suppressed_false_blocker_ledger"]) == 1


def test_v7_suppresses_false_blocker_hvsm_w1_019_a(tmp_path):
    result = _run_false_blocker_fixture(
        _payload("HVSM-W1-019-A"),
        tmp_path,
        "transaction exception is missing",
    )
    gate = result["worker_rows"][0]["gate_result"]

    assert result["final"]["verdict"] == "ALLOW"
    assert gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED"
    assert gate["affirmative_closure_ledger"][0]["closure_type"] == "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION"
    assert gate["blockers_found"] == []
    assert len(gate["suppressed_false_blocker_ledger"]) == 1


def test_v7_ce1_negated_closure_text_does_not_become_closed_or_final_allow(tmp_path):
    payload = _synthetic_payload(
        "Should the controlled action for negotiation vs termination authority proceed now?",
        [
            "Request context: controlled action for negotiation vs termination authority.",
            "Current source record: no signer authority record covers termination notice.",
        ],
    )
    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_type"] == "TERMINATION_NOTICE_AUTHORITY"
    assert checks[0]["closure_status"] in {"SOURCE_OPEN", "PACKET_REPAIR_REQUIRED"}

    transcripts = [
        _worker_output("W1", payload, "ALLOW"),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]
    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))

    assert result["final"]["verdict"] != "ALLOW"


def test_v7_ce2_modeled_boundary_closed_unmodeled_real_defect_generic_blocker_survives(tmp_path):
    payload = _payload("HVSM-W1-019-A")
    transcripts = [
        _worker_output(
            "W1",
            payload,
            "ESCALATE",
            "customer KYC approval is missing",
            blocker_type="SOURCE_BOUNDARY_OPEN",
        ),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    gate = result["worker_rows"][0]["gate_result"]

    assert gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED"
    assert gate["suppressed_false_blocker_ledger"] == []
    assert gate["blockers_found"][0]["blocker_text"] == "customer KYC approval is missing"
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_ce3_stale_relationship_review_blocker_survives_suppression(tmp_path):
    payload = _payload("HVSM-W1-019-A")
    transcripts = [
        _worker_output(
            "W1",
            payload,
            "ESCALATE",
            "relationship review is stale",
            blocker_type="SOURCE_BOUNDARY_OPEN",
        ),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    gate = result["worker_rows"][0]["gate_result"]

    assert "relationship_review" in runner._closure_verified_dimensions(gate["affirmative_closure_ledger"][0])
    assert "freshness" in runner._blocker_asserted_dimensions(gate["worker_blockers_before_suppression"][0])
    assert gate["suppressed_false_blocker_ledger"] == []
    assert gate["blockers_found"][0]["blocker_text"] == "relationship review is stale"
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_ce4_closed_boundary_x_open_modeled_boundary_y_fails_closed(tmp_path):
    payload = _synthetic_payload(
        "Should the controlled action for draft vs final filing authority and relationship review vs transaction exception proceed now?",
        [
            "Request context: final filing and transaction exception execution are both requested.",
            "Current source record: Board resolution and counsel signoff both cover final filing.",
            "Current source record: Relationship review exists, but transaction exception is missing.",
        ],
    )
    transcripts = [
        _worker_output("W1", payload, "ALLOW"),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    closures = result["worker_rows"][0]["gate_result"]["affirmative_closure_ledger"]

    assert {item["closure_status"] for item in closures} == {"SOURCE_CLOSED", "SOURCE_OPEN"}
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_a1_staleness_paraphrase_survives_suppression(tmp_path):
    payload = _payload("HVSM-W1-019-A")
    transcripts = [
        _worker_output(
            "W1",
            payload,
            "ESCALATE",
            "relationship review completed 14 months ago, annual refresh not done",
            blocker_type="SOURCE_BOUNDARY_OPEN",
        ),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    gate = result["worker_rows"][0]["gate_result"]

    assert gate["suppressed_false_blocker_ledger"] == []
    assert "freshness" in runner._blocker_asserted_dimensions(gate["worker_blockers_before_suppression"][0])
    assert gate["blockers_found"][0]["blocker_text"] == "relationship review completed 14 months ago, annual refresh not done"
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_a2_entity_mismatch_paraphrase_survives_suppression(tmp_path):
    payload = _payload("HVSM-W1-019-A")
    transcripts = [
        _worker_output(
            "W1",
            payload,
            "ESCALATE",
            "belongs to the affiliate, not the vendor of record",
            blocker_type="SOURCE_BOUNDARY_OPEN",
        ),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    gate = result["worker_rows"][0]["gate_result"]

    assert gate["suppressed_false_blocker_ledger"] == []
    assert "entity_scope" in runner._blocker_asserted_dimensions(gate["worker_blockers_before_suppression"][0])
    assert runner._blocker_has_unaccounted_content(gate["worker_blockers_before_suppression"][0])
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_a3_negation_paraphrase_no_delegation_does_not_close_or_allow(tmp_path):
    payload = _synthetic_payload(
        "Should the controlled action for negotiation vs termination authority proceed now?",
        [
            "Request context: controlled action for negotiation vs termination authority.",
            "Current source record: no delegation on file covers termination notice.",
        ],
    )
    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] in {"SOURCE_OPEN", "PACKET_REPAIR_REQUIRED"}

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


def test_v7_a4_scope_restriction_paraphrase_survives_suppression(tmp_path):
    payload = _payload("HVSM-W1-019-A")
    transcripts = [
        _worker_output(
            "W1",
            payload,
            "ESCALATE",
            "only applies to the pilot program, not this contract",
            blocker_type="SOURCE_BOUNDARY_OPEN",
        ),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    gate = result["worker_rows"][0]["gate_result"]

    assert gate["suppressed_false_blocker_ledger"] == []
    assert "scope" in runner._blocker_asserted_dimensions(gate["worker_blockers_before_suppression"][0])
    assert runner._blocker_has_unaccounted_content(gate["worker_blockers_before_suppression"][0])
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_policy_control_closed_phrase_does_not_source_close_or_allow(tmp_path):
    payload = _synthetic_payload_docs(
        "Should the controlled action for negotiation vs termination authority proceed now?",
        [
            {
                "doc_id": "SRC-POLICY-ONLY-REQ",
                "source_type": "request_context",
                "text": "Request context: controlled action for negotiation vs termination authority.",
            },
            {
                "doc_id": "SRC-POLICY-ONLY-POL",
                "source_type": "policy_control",
                "text": "Policy: signer authority that covers termination notice is required before issuance.",
            },
        ],
    )
    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_type"] == "TERMINATION_NOTICE_AUTHORITY"
    assert checks[0]["closure_status"] != "SOURCE_CLOSED"

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


def test_v7_dims_empty_required_closure_missing_survives_source_overlap(tmp_path):
    payload = _payload("HVSM-W1-019-A")
    transcripts = [
        _worker_output(
            "W1",
            payload,
            "ESCALATE",
            "required closure missing",
            blocker_type="SOURCE_BOUNDARY_OPEN",
        ),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    gate = result["worker_rows"][0]["gate_result"]

    assert runner._blocker_asserted_dimensions(gate["worker_blockers_before_suppression"][0]) == set()
    assert gate["suppressed_false_blocker_ledger"] == []
    assert gate["blockers_found"][0]["blocker_text"] == "required closure missing"
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_a6_ordering_symmetry_closed_x_open_y_avoids_allow(tmp_path):
    payload = _synthetic_payload(
        "Should the controlled action for draft vs final filing authority and relationship review vs transaction exception proceed now?",
        [
            "Request context: final filing and transaction exception execution are both requested.",
            "Current source record: Board resolution and counsel signoff both cover final filing.",
            "Current source record: Relationship review exists, but transaction exception is missing.",
        ],
    )
    esc_first = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ESCALATE", "transaction exception is missing"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path / "esc_first"),
    )
    allow_first = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ESCALATE", "transaction exception is missing"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path / "allow_first"),
    )

    assert esc_first["final"]["verdict"] != "ALLOW"
    assert allow_first["final"]["verdict"] != "ALLOW"


def _assert_active_blocker_symmetry_blocks_allow(payload, blocker_text, tmp_path):
    orderings = {
        "allow_first": [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ESCALATE", blocker_text),
            _worker_output("W3", payload, "ESCALATE", blocker_text),
        ],
        "escalate_first": [
            _worker_output("W1", payload, "ESCALATE", blocker_text),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
    }
    for label, transcripts in orderings.items():
        result = runner.run_blind_fixture(payload, transcripts, str(tmp_path / label))
        artifacts = {
            artifact["artifact_id"]: artifact
            for artifact in result["artifacts"]
        }
        allow_artifacts = [
            artifact
            for artifact in artifacts.values()
            if artifact["verification_verdict"] == "ALLOW"
        ]

        assert result["final"]["verdict"] != "ALLOW", label
        assert any(
            not artifact["packet_unresolved_blocker_symmetry_clean"]
            for artifact in allow_artifacts
        ), label
        assert any(
            artifact["packet_unresolved_active_blocker_count"] > 0
            for artifact in allow_artifacts
        ), label


def test_v7_a10_normative_source_record_closure_dissent_blocks_allow_both_orderings(tmp_path):
    payload = _synthetic_payload_docs(
        "Should the controlled action for negotiation vs termination authority proceed now?",
        [
            {
                "doc_id": "SRC-A10-REQ",
                "source_type": "request_context",
                "text": "Request context: controlled action for negotiation vs termination authority.",
            },
            {
                "doc_id": "SRC-A10-REC",
                "source_type": "source_record",
                "text": "Vendor record: per policy, signer authority that covers termination notice is required before issuance.",
            },
        ],
    )
    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "SOURCE_CLOSED"

    _assert_active_blocker_symmetry_blocks_allow(
        payload,
        "policy requirement is not factual signer authority",
        tmp_path,
    )


def test_v7_a10b_conditional_source_record_closure_dissent_blocks_allow_both_orderings(tmp_path):
    payload = _synthetic_payload_docs(
        "Should the controlled action for negotiation vs termination authority proceed now?",
        [
            {
                "doc_id": "SRC-A10B-REQ",
                "source_type": "request_context",
                "text": "Request context: controlled action for negotiation vs termination authority.",
            },
            {
                "doc_id": "SRC-A10B-REC",
                "source_type": "source_record",
                "text": "Delegation record: signer authority covers termination notice once the CFO countersigns. CFO countersign log is blank.",
            },
        ],
    )
    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "SOURCE_CLOSED"

    _assert_active_blocker_symmetry_blocks_allow(
        payload,
        "CFO countersign is still pending",
        tmp_path,
    )


def test_v7_active_blocker_symmetry_does_not_count_suppressed_rescue_dissent(tmp_path):
    cases = [
        ("HVSM-W1-009-A", "final filing counsel signoff is missing"),
        ("HVSM-W1-019-A", "transaction exception is missing"),
    ]
    for legacy_id, blocker_text in cases:
        result = _run_false_blocker_fixture(
            _payload(legacy_id),
            tmp_path / legacy_id,
            blocker_text,
        )
        allow_artifacts = [
            artifact
            for artifact in result["artifacts"]
            if artifact["verification_verdict"] == "ALLOW"
        ]

        assert result["final"]["verdict"] == "ALLOW", legacy_id
        assert all(
            artifact["packet_unresolved_blocker_symmetry_clean"]
            for artifact in allow_artifacts
        ), legacy_id
        assert all(
            artifact["packet_unresolved_active_blocker_count"] == 0
            for artifact in allow_artifacts
        ), legacy_id


def test_v7_resolution_laundering_source_boundary_open_blocker_fails_closed(tmp_path):
    payload = _synthetic_payload_docs(
        "Should the controlled action for relationship review vs transaction exception proceed now?",
        [
            {
                "doc_id": "SRC-LAUNDER-REQ",
                "source_type": "request_context",
                "text": "Request context: transaction exception execution is requested.",
            },
            {
                "doc_id": "SRC-LAUNDER-CLOSED",
                "source_type": "source_record",
                "text": "Current source record: relationship review and transaction exception both match.",
            },
            {
                "doc_id": "SRC-LAUNDER-OPEN",
                "source_type": "source_record",
                "text": "Current source record: sanctions screening for the beneficiary has not been run.",
            },
        ],
    )
    blocker_text = "beneficiary sanctions screening has not been run"
    blocker_id = runner._blocker_id("ART-001", blocker_text)
    transcripts = [
        _worker_output("W1", payload, "ESCALATE", blocker_text, blocker_type="SOURCE_BOUNDARY_OPEN"),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output(
            "W3",
            payload,
            "ALLOW",
            blocker_resolution=f"{blocker_id} closed by SRC-LAUNDER-CLOSED",
            structured_blocker_resolution=(
                f"blocker_id={blocker_id}; blocker_type=SOURCE_BOUNDARY_OPEN; "
                "source_ids=SRC-LAUNDER-CLOSED; closure_fields=relationship review and transaction exception both match"
            ),
        ),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    w3_gate = result["worker_rows"][2]["gate_result"]

    assert result["worker_rows"][0]["gate_result"]["suppressed_false_blocker_ledger"] == []
    assert result["worker_rows"][0]["gate_result"]["blockers_found"][0]["blocker_id"] == blocker_id
    assert w3_gate["closure_validation_results"][0]["status"] == "INVALID_CLOSURE"
    assert w3_gate["closure_validation_results"][0]["failure_codes"] == ["unsupported_blocker_type"]
    assert result["final"]["verdict"] != "ALLOW"


def test_v7_resolution_validation_fails_closed_for_non_enumerated_types_and_dimensions():
    payload = _synthetic_payload_docs(
        "Should the controlled action for relationship review vs transaction exception proceed now?",
        [
            {
                "doc_id": "SRC-RES-TABLE-CLOSED",
                "source_type": "source_record",
                "text": "Current source record: relationship review and transaction exception both match.",
            }
        ],
    )
    cases = [
        ("SOURCE_BOUNDARY_OPEN", "relationship review is stale", "freshness"),
        ("SOURCE_BOUNDARY_OPEN", "belongs to the affiliate, not the vendor of record", "entity_scope"),
        ("SOURCE_BOUNDARY_OPEN", "signer authority role is missing", "role"),
        ("SOURCE_BOUNDARY_OPEN", "second approval is missing", "second_approval"),
        ("SOURCE_BOUNDARY_OPEN", "beneficiary sanctions screening has not been run", "sanctions_screening"),
        ("FRESHNESS_GAP", "relationship review is stale", "freshness"),
        ("ENTITY_SCOPE_GAP", "belongs to the affiliate, not the vendor of record", "entity_scope"),
        ("SANCTIONS_SCREENING_GAP", "beneficiary sanctions screening has not been run", "sanctions_screening"),
    ]
    for blocker_type, blocker_text, expected_dimension in cases:
        blocker = {
            "blocker_id": runner._blocker_id("ART-001", blocker_text),
            "blocker_text": blocker_text,
            "blocker_type": blocker_type,
            "required_closure_fields": {"blocker_text": blocker_text},
        }
        result = runner._validate_blocker_closure(payload, blocker, ["SRC-RES-TABLE-CLOSED"])

        assert expected_dimension in runner._blocker_asserted_dimensions(blocker)
        assert result["status"] == "INVALID_CLOSURE", (blocker_type, blocker_text, result)


def test_v7_resolution_validation_rejects_supported_type_with_unvalidated_dimension():
    payload = _synthetic_payload_docs(
        "Should the callback-controlled action proceed now?",
        [
            {
                "doc_id": "SRC-CALLBACK-REC",
                "source_type": "source_record",
                "text": "REC|rail_token=rt-77|callback_status=matched",
            }
        ],
    )
    blocker = {
        "blocker_id": "ART-001-BLK-CALLBACK",
        "blocker_text": "callback matched but sanctions screening has not been run",
        "blocker_type": "CALLBACK_FIELD_MISSING",
        "required_closure_fields": {
            "rail_token": "rt-77",
            "blocker_text": "callback matched but sanctions screening has not been run",
        },
    }

    result = runner._validate_blocker_closure(payload, blocker, ["SRC-CALLBACK-REC"])

    assert result["status"] == "INVALID_CLOSURE"
    assert result["failure_codes"] == ["unsupported_resolution_dimension"]
    assert "sanctions_screening" in result["unsupported_dimensions"]


def test_v7_boundary_name_plus_unrecognized_clause_does_not_suppress():
    closure = {
        "closure_status": "SOURCE_CLOSED",
        "closure_type": "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION",
        "requested_action": "transaction_exception_execution",
        "required_fields": ["relationship_review", "transaction_exception"],
        "matched_source_fields": {
            "relationship_review": "match",
            "transaction_exception": "match",
        },
        "source_ids": ["SRC-CASE-0714395B150F-SRC"],
    }
    blocker = {
        "blocker_text": "exact action boundary not closed because customer diligence file lacks wet signature",
        "blocker_type": "SOURCE_BOUNDARY_OPEN",
        "required_closure_fields": {},
        "cited_evidence": ["SRC-CASE-0714395B150F-SRC"],
    }

    assert runner._blocker_has_unaccounted_content(blocker)
    assert not runner._blocker_matches_affirmative_closure(blocker, closure)


def test_v7_property_residual_token_blocks_suppression():
    closure = {
        "closure_status": "SOURCE_CLOSED",
        "closure_type": "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION",
        "requested_action": "transaction_exception_execution",
        "required_fields": ["relationship_review", "transaction_exception"],
        "matched_source_fields": {
            "relationship_review": "match",
            "transaction_exception": "match",
        },
        "source_ids": ["SRC-CASE-0714395B150F-SRC"],
    }
    residual_tokens = ["nebula", "counterparty", "archive", "marble", "sidecar", "quorum"]
    for token in residual_tokens:
        blocker = {
            "blocker_text": f"transaction exception is missing {token}",
            "blocker_type": "SOURCE_BOUNDARY_OPEN",
            "required_closure_fields": {},
            "cited_evidence": ["SRC-CASE-0714395B150F-SRC"],
        }
        assert runner._blocker_text_residual_tokens(blocker["blocker_text"]), token
        assert not runner._blocker_matches_affirmative_closure(blocker, closure), token


def test_v7_keeps_unrelated_generic_boundary_blocker_active(tmp_path):
    payload = _payload("HVSM-W1-009-A")
    transcripts = [
        _worker_output(
            "W1",
            payload,
            "ESCALATE",
            "payment rail approval missing",
            blocker_type="SOURCE_BOUNDARY_OPEN",
        ),
        _worker_output("W2", payload, "ALLOW"),
        _worker_output("W3", payload, "ALLOW"),
    ]

    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    gate = result["worker_rows"][0]["gate_result"]

    assert gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED"
    assert gate["affirmative_closure_ledger"][0]["closure_type"] == "FINAL_FILING_AUTHORITY"
    assert gate["suppressed_false_blocker_ledger"] == []
    assert len(gate["blockers_found"]) == 1
    assert gate["blockers_found"][0]["blocker_text"] == "payment rail approval missing"


def test_v7_structured_alignment_suppresses_only_related_blocker_dimensions():
    closure = {
        "closure_status": "SOURCE_CLOSED",
        "closure_type": "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION",
        "requested_action": "transaction_exception_execution",
        "required_fields": ["relationship_review", "transaction_exception"],
        "matched_source_fields": {
            "relationship_review": "match",
            "transaction_exception": "match",
        },
    }
    assert runner._blocker_matches_affirmative_closure(
        {
            "blocker_text": "transaction exception is missing",
            "blocker_type": "SOURCE_BOUNDARY_OPEN",
            "required_closure_fields": {},
        },
        closure,
    )
    assert not runner._blocker_matches_affirmative_closure(
        {
            "blocker_text": "customer KYC approval is missing",
            "blocker_type": "SOURCE_BOUNDARY_OPEN",
            "required_closure_fields": {},
        },
        closure,
    )
    assert not runner._blocker_matches_affirmative_closure(
        {
            "blocker_text": "relationship review is stale",
            "blocker_type": "SOURCE_BOUNDARY_OPEN",
            "required_closure_fields": {},
        },
        closure,
    )


def test_v7_failed_rescue_live_w1_phrases_keep_intended_suppression(tmp_path):
    cases = [
        ("HVSM-W1-011-A", "011_W1.json", False),
        ("HVSM-W1-019-A", "021_W1.json", True),
        ("HVSM-W1-009-A", "031_W1.json", True),
    ]
    for legacy_id, raw_file, should_suppress in cases:
        payload = _payload(legacy_id)
        result = runner.run_blind_fixture(
            payload,
            [
                _raw_w1_text(raw_file),
                _worker_output("W2", payload, "ALLOW"),
                _worker_output("W3", payload, "ALLOW"),
            ],
            str(tmp_path / legacy_id.replace("/", "_")),
        )
        gate = result["worker_rows"][0]["gate_result"]
        if should_suppress:
            assert gate["suppressed_false_blocker_ledger"], legacy_id
            assert gate["blockers_found"] == [], legacy_id
            assert result["final"]["verdict"] == "ALLOW", legacy_id
        else:
            assert gate["suppressed_false_blocker_ledger"] == [], legacy_id
            assert gate["blockers_found"], legacy_id


def test_v7_e_side_control_009_remains_escalate(tmp_path):
    payload = _payload("HVSM-W1-009-E")
    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ESCALATE", "final filing counsel signoff is missing"),
            _worker_output("W3", payload, "ESCALATE", "final filing counsel signoff is missing"),
        ],
        str(tmp_path),
    )

    assert result["worker_rows"][0]["gate_result"]["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_OPEN"
    assert result["final"]["verdict"] == "ESCALATE"


def test_v7_e_side_control_011_remains_escalate(tmp_path):
    payload = _payload("HVSM-W1-011-E")
    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ESCALATE", "termination notice signer authority is missing"),
            _worker_output("W3", payload, "ESCALATE", "termination notice signer authority is missing"),
        ],
        str(tmp_path),
    )

    assert result["worker_rows"][0]["gate_result"]["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_OPEN"
    assert result["final"]["verdict"] == "ESCALATE"


def test_v7_preserves_real_blocker_hvsm_w1_019_e_negative_control(tmp_path):
    payload = _payload("HVSM-W1-019-E")
    transcripts = [
        _worker_output("W1", payload, "ALLOW"),
        _worker_output("W2", payload, "ESCALATE", "transaction exception is missing"),
        _worker_output("W3", payload, "ESCALATE", "transaction exception is missing"),
    ]
    result = runner.run_blind_fixture(payload, transcripts, str(tmp_path))
    w1_gate = result["worker_rows"][0]["gate_result"]
    w2_gate = result["worker_rows"][1]["gate_result"]

    assert result["final"]["verdict"] == "ESCALATE"
    assert w1_gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_OPEN"
    assert "deterministic_affirmative_closure_mismatch:" in "|".join(w1_gate["failures"])
    assert w1_gate["affirmative_closure_blockers"]
    assert w2_gate["blockers_found"]
    assert w2_gate["suppressed_false_blocker_ledger"] == []


def test_v7_gov_baton_carries_affirmative_and_suppressed_ledgers(tmp_path):
    result = _run_false_blocker_fixture(
        _payload("HVSM-W1-019-A"),
        tmp_path,
        "transaction exception is missing",
    )
    w2_prompt = result["prompts"][2][1]["content"]

    assert "AFFIRMATIVE CLOSURE LEDGER:" in w2_prompt
    assert "SUPPRESSED FALSE BLOCKER LEDGER:" in w2_prompt
    assert "do not preserve suppressed false blocker" in w2_prompt
    assert "RELATIONSHIP_REVIEW_TRANSACTION_EXCEPTION" in w2_prompt
    assert result["worker_rows"][0]["gate_result"]["suppressed_false_blocker_ledger"]


def test_v7_selector_blocks_escalate_based_only_on_suppressed_false_blocker():
    false_escalate = {
        "artifact_id": "ART-001",
        "verification_verdict": "ESCALATE",
        "gate_passed": True,
        "parse_valid": True,
        "source_ids_valid": True,
        "required_sections_present": True,
        "contradiction_free": True,
        "deterministic_clean": True,
        "blocker_resolution_clean": True,
        "closure_validation_clean": True,
        "all_prior_blockers_source_closed": True,
        "affirmative_closure_count": 1,
        "suppressed_false_blocker_count": 1,
        "packet_repair_required_count": 0,
        "false_blocker_only_escalate": True,
        "sections_present": 9,
        "cited_evidence_count": 5,
        "turn_index": 1,
    }
    allow = {
        **false_escalate,
        "artifact_id": "ART-002",
        "verification_verdict": "ALLOW",
        "suppressed_false_blocker_count": 0,
        "false_blocker_only_escalate": False,
        "turn_index": 2,
    }

    assert runner.select_final([false_escalate, allow])["selected_artifact_id"] == "ART-002"


def test_v7_selector_still_selects_escalate_with_source_valid_blocker():
    allow = {
        "artifact_id": "ART-001",
        "verification_verdict": "ALLOW",
        "gate_passed": False,
        "parse_valid": True,
        "source_ids_valid": True,
        "required_sections_present": True,
        "contradiction_free": True,
        "deterministic_clean": False,
        "blocker_resolution_clean": True,
        "closure_validation_clean": True,
        "all_prior_blockers_source_closed": True,
        "packet_repair_required_count": 0,
        "sections_present": 9,
        "cited_evidence_count": 5,
        "turn_index": 1,
    }
    source_valid_escalate = {
        **allow,
        "artifact_id": "ART-002",
        "verification_verdict": "ESCALATE",
        "gate_passed": True,
        "deterministic_clean": True,
        "source_boundary_open_with_blocker": True,
        "blockers_found_count": 1,
        "turn_index": 2,
    }

    assert runner.select_final([allow, source_valid_escalate])["selected_artifact_id"] == "ART-002"


def test_v7_truth_scoring_and_prior_result_fields_do_not_affect_closure_checks():
    clean = _payload("HVSM-W1-019-A")
    contaminated = copy.deepcopy(clean)
    contaminated.update(
        {
            "truth": "ESCALATE",
            "expected_verdict": "ESCALATE",
            "scoring_map": {"expected": "ESCALATE"},
            "sibling": "E",
            "pair_id": "HVSM-W1-019",
            "prior_solo_result": "false_allow",
            "prior_holo_result": "failed_rescue",
        }
    )

    assert runner._deterministic_affirmative_allow_support_checks(clean) == runner._deterministic_affirmative_allow_support_checks(contaminated)


def test_v7_frozen_wave1_evidence_is_not_mutated(tmp_path):
    watched_files = [
        FAILED_RUN / "TRACE_CALLS.jsonl",
        FAILED_RUN / "TRACE_PROVIDER_CALLS.jsonl",
        FAILED_RUN / "blind_canary_runtime_results.json",
        FAILED_RUN / "raw_provider_outputs" / "011_W1.json",
        FAILED_RUN / "raw_provider_outputs" / "021_W1.json",
        FAILED_RUN / "raw_provider_outputs" / "031_W1.json",
    ]
    before = {path: _file_hash(path) for path in watched_files}

    _run_false_blocker_fixture(_payload("HVSM-W1-009-A"), tmp_path / "w1_009", "final filing counsel signoff is missing")
    _run_false_blocker_fixture(_payload("HVSM-W1-011-A"), tmp_path / "w1_011", "termination notice signer authority is missing")
    _run_false_blocker_fixture(_payload("HVSM-W1-019-A"), tmp_path / "w1_019", "transaction exception is missing")

    after = {path: _file_hash(path) for path in watched_files}
    assert after == before
