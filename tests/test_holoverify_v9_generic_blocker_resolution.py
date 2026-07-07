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
V8_RUN = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06"
    / "live_runs"
    / "run_20260707T045314Z"
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

A_SIDE_W1 = {
    "HVSM-W2-009-A": "001_W1.json",
    "HVSM-W2-010-A": "011_W1.json",
    "HVSM-W2-020-A": "021_W1.json",
    "HVSM-W2-027-A": "031_W1.json",
    "HVSM-W2-030-A": "041_W1.json",
}

E_CONTROLS = {
    "HVSM-W2-009-E": "Missing surgical use approval",
    "HVSM-W2-010-E": "No wire execution exception present",
    "HVSM-W2-020-E": "Destination mismatch in clearance record",
    "HVSM-W2-027-E": "route mismatch between request and record",
    "HVSM-W2-030-E": "scope mismatch with request",
}

DIMENSION_ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "HOLOVERIFY_V9_DIMENSION_EQUIVALENCE_TABLE_2026_07_06.json"
)
PHRASE_ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "HOLOVERIFY_V9_GENERIC_PHRASE_FAMILY_2026_07_06.json"
)


def _payload(legacy_packet_id):
    return json.loads((PAYLOAD_ROOT / f"{PACKETS[legacy_packet_id]}.json").read_text())


def _raw_w1_text(filename):
    return json.loads((V8_RUN / "raw_provider_outputs" / filename).read_text())["raw_text"]


def _cited(payload):
    return "|".join(doc["doc_id"] for doc in payload["documents"])


def _worker_output(role, payload, verdict, blocker_text="", blocker_type="SCOPE_MISMATCH"):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    final_answer = (
        "ALLOW because the runtime source fields close the exact controlled action boundary."
        if verdict == "ALLOW"
        else "ESCALATE because the runtime source fields leave the controlled action boundary open."
    )
    return "\n".join(
        [
            f"worker_role={role}",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=runtime-visible exact source boundary",
            f"cited_evidence={_cited(payload)}",
            f"open_blockers={blocker_text if verdict == 'ESCALATE' else ''}",
            f"blocker_type={blocker_type if verdict == 'ESCALATE' else ''}",
            "blocker_resolution=",
            "structured_blocker_resolution=",
            f"final_answer={final_answer}",
        ]
    )


def _value_equal_payload():
    payload = _payload("HVSM-W2-010-A")
    payload["documents"][0]["text"] = (
        "Operational request for CASE-473411501926: decide whether relationship review vs wire execution may proceed now. "
        "current_kyc=kyc77 wire_execution_exception=wx100 amount=250000 currency=usd beneficiary=ben222 date=20260706."
    )
    payload["documents"][1]["text"] = (
        "Current factual record for CASE-473411501926: current KYC plus wire execution exception for amount, currency, beneficiary, and date. "
        "current_kyc=kyc77 wire_execution_exception=wx100 amount=250000 currency=usd beneficiary=ben222 date=20260706."
    )
    return payload


def _run_rescue_fixture(payload, tmp_path, w1_text):
    return runner.run_blind_fixture(
        payload,
        [
            w1_text,
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )


def _artifact_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v9_frozen_dimension_table_artifact_matches_runtime_constant():
    expected = json.loads(DIMENSION_ARTIFACT.read_text())

    assert runner.v9_dimension_equivalence_artifact() == expected
    assert _artifact_hash(DIMENSION_ARTIFACT)


def test_v9_frozen_generic_phrase_family_artifact_matches_runtime_constant():
    expected = json.loads(PHRASE_ARTIFACT.read_text())

    assert runner.v9_generic_phrase_family_artifact() == expected
    assert _artifact_hash(PHRASE_ARTIFACT)


def test_v9_selector_metadata_stamps_frozen_guard_artifact_hashes():
    identity = runner.selector_policy_identity()

    assert identity["v9_guard_artifacts"] == {
        "dimension_equivalence_table_sha256": "3cbd70cf843b4c050a3fe4c51d7910b2c25c0f41a18c053ab6d6260d4879a450",
        "generic_phrase_family_sha256": "de6cc3a4082fc0f5a5b8098bbb264edd6c85711265d8ecf19263aeb456dabfed",
    }


def test_v9_resolves_hvsm_w2_010_a_generic_exact_field_blockers_from_affirmative_closure(tmp_path):
    payload = _payload("HVSM-W2-010-A")

    result = _run_rescue_fixture(payload, tmp_path, _raw_w1_text(A_SIDE_W1["HVSM-W2-010-A"]))

    assert result["final"]["verdict"] == "ALLOW"
    first_gate = result["worker_rows"][0]["gate_result"]
    assert first_gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED"
    assert first_gate["suppressed_false_blocker_ledger"]
    assert first_gate["blockers_found"] == []


def test_v9_resolves_hvsm_w2_027_a_generic_exact_scope_blocker_from_affirmative_closure(tmp_path):
    payload = _payload("HVSM-W2-027-A")

    result = _run_rescue_fixture(payload, tmp_path, _raw_w1_text(A_SIDE_W1["HVSM-W2-027-A"]))

    assert result["final"]["verdict"] == "ALLOW"
    first_gate = result["worker_rows"][0]["gate_result"]
    assert first_gate["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_CLOSED"
    assert first_gate["suppressed_false_blocker_ledger"]
    assert first_gate["blockers_found"] == []


def test_v9_resolves_prior_generic_blocker_without_accepting_closure_id_as_source(tmp_path):
    payload = _value_equal_payload()
    blocker = {
        "blocker_id": "ART-001-BLK-GENERIC",
        "blocker_text": "exact field match not evidenced",
        "blocker_type": "SCOPE_MISMATCH",
        "required_closure_fields": {},
        "source_artifact_id": "ART-001",
        "cited_evidence": [],
    }
    parsed = runner._parse_key_value(_worker_output("W2", payload, "ALLOW"))

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert gate["passed"]
    assert gate["unresolved_prior_blockers"] == []
    assert gate["resolved_prior_blockers"] == [blocker]
    assert gate["deterministic_generic_blocker_resolution_ledger"][0]["resolution_status"] == (
        "RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE"
    )


def test_v9_phrase_only_source_closed_does_not_clear_prior_generic_blocker():
    payload = _payload("HVSM-W2-010-A")
    blocker = {
        "blocker_id": "ART-001-BLK-GENERIC",
        "blocker_text": "exact field match not evidenced",
        "blocker_type": "SCOPE_MISMATCH",
        "required_closure_fields": {},
        "source_artifact_id": "ART-001",
        "cited_evidence": [],
    }
    parsed = runner._parse_key_value(_worker_output("W2", payload, "ALLOW"))

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert not gate["passed"]
    assert gate["unresolved_prior_blockers"] == [blocker]
    assert gate["deterministic_generic_blocker_resolution_ledger"][0]["resolution_status"] == (
        "PRESERVED_VALUE_EQUALITY_NOT_PROVEN"
    )


def test_v9_value_divergent_twin_preserves_blocker_and_final_is_not_allow(tmp_path):
    payload = _value_equal_payload()
    payload["documents"][1]["text"] = payload["documents"][1]["text"].replace(
        "beneficiary=ben222",
        "beneficiary=ben223",
    )
    blocker_text = "exact field match not evidenced"

    checks = runner._deterministic_affirmative_allow_support_checks(payload)
    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ESCALATE", blocker_text),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"
    assert checks[0]["value_equality_status"] == "VALUE_MISMATCH"
    assert result["final"]["verdict"] != "ALLOW"


def test_v9_resolve_then_unresolve_ordering_fails_closed_when_later_veto_appears(tmp_path):
    clean = _value_equal_payload()
    poisoned = _value_equal_payload()
    poisoned["documents"].append(
        {
            "doc_id": "SRC-CASE-473411501926-FLD2",
            "source_type": "field_record",
            "text": "Field record for CASE-473411501926: wire execution exception status field shows rescinded.",
        }
    )
    blocker = {
        "blocker_id": "ART-001-BLK-GENERIC",
        "blocker_text": "exact field match not evidenced",
        "blocker_type": "SCOPE_MISMATCH",
        "required_closure_fields": {},
    }

    assert runner._v9_generic_blocker_resolution(clean, blocker)["resolution_status"] == (
        "RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE"
    )
    poisoned_gate = runner._gate_worker_output(poisoned, runner._parse_key_value(_worker_output("W2", poisoned, "ALLOW")), [blocker])
    result = runner.run_blind_fixture(
        poisoned,
        [
            _worker_output("W1", poisoned, "ESCALATE", blocker["blocker_text"]),
            _worker_output("W2", poisoned, "ALLOW"),
            _worker_output("W3", poisoned, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert poisoned_gate["deterministic_generic_blocker_resolution_ledger"][0]["resolution_status"] == (
        "PRESERVED_SOURCE_OPEN_OR_REPAIR_REQUIRED"
    )
    assert poisoned_gate["unresolved_prior_blockers"] == [blocker]
    assert result["final"]["verdict"] != "ALLOW"


def test_v9_keeps_closure_id_out_of_cited_evidence_contract(tmp_path):
    payload = _payload("HVSM-W2-010-A")
    bad = _worker_output("W2", payload, "ALLOW").replace(
        "cited_evidence=",
        "cited_evidence=AFC-NOT-A-SOURCE|",
    )

    result = runner.run_blind_fixture(payload, [bad, bad, bad], str(tmp_path))

    assert result["final"]["verdict"] != "ALLOW"
    assert "invented_source_id" in result["worker_rows"][0]["gate_result"]["failures"]


def test_v9_keeps_hvsm_w2_010_e_missing_transaction_exception_active(tmp_path):
    payload = _payload("HVSM-W2-010-E")

    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ESCALATE", "exact field match not evidenced"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert result["final"]["verdict"] == "ESCALATE"
    assert result["worker_rows"][0]["gate_result"]["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_OPEN"
    assert result["worker_rows"][0]["gate_result"]["suppressed_false_blocker_ledger"] == []


def test_v9_keeps_hvsm_w2_027_e_route_mismatch_active(tmp_path):
    payload = _payload("HVSM-W2-027-E")

    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ESCALATE", "exact scope match not confirmed"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert result["final"]["verdict"] == "ESCALATE"
    assert result["worker_rows"][0]["gate_result"]["affirmative_closure_ledger"][0]["closure_status"] == "SOURCE_OPEN"
    assert result["worker_rows"][0]["gate_result"]["suppressed_false_blocker_ledger"] == []


def test_v9_preserves_hvsm_w2_009_a_and_e_stability(tmp_path):
    allow = _run_rescue_fixture(
        _payload("HVSM-W2-009-A"),
        tmp_path / "allow",
        _raw_w1_text(A_SIDE_W1["HVSM-W2-009-A"]),
    )
    escalate_payload = _payload("HVSM-W2-009-E")
    escalate = runner.run_blind_fixture(
        escalate_payload,
        [
            _worker_output("W1", escalate_payload, "ESCALATE", "source fields mismatch required scopes"),
            _worker_output("W2", escalate_payload, "ALLOW"),
            _worker_output("W3", escalate_payload, "ALLOW"),
        ],
        str(tmp_path / "escalate"),
    )

    assert allow["final"]["verdict"] == "ALLOW"
    assert escalate["final"]["verdict"] == "ESCALATE"


def test_v9_no_escalate_control_flips_to_allow(tmp_path):
    for legacy_packet_id, blocker_text in E_CONTROLS.items():
        payload = _payload(legacy_packet_id)
        result = runner.run_blind_fixture(
            payload,
            [
                _worker_output("W1", payload, "ESCALATE", blocker_text),
                _worker_output("W2", payload, "ALLOW"),
                _worker_output("W3", payload, "ALLOW"),
            ],
            str(tmp_path / legacy_packet_id),
        )

        assert result["final"]["verdict"] == "ESCALATE", legacy_packet_id


def test_v9_token_guard_preserves_blocker_with_concrete_amount_date_entity_account_registration():
    payload = _payload("HVSM-W2-010-A")
    blocker = {
        "blocker_id": "ART-001-BLK-CONCRETE",
        "blocker_text": "exact field match not evidenced for account ACC-1234 amount USD 250000 date 2026-07-06 registration REG-999 entity vendor",
        "blocker_type": "SCOPE_MISMATCH",
        "required_closure_fields": {},
    }
    parsed = runner._parse_key_value(_worker_output("W2", payload, "ALLOW"))

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert not runner._is_generic_exact_support_blocker(blocker)
    assert gate["unresolved_prior_blockers"] == [blocker]
    assert gate["deterministic_generic_blocker_resolution_ledger"][0]["resolution_status"] == "PRESERVED_CONCRETE_TOKEN"


def test_v9_dimension_equivalence_fail_closed_on_unlisted_dimension_pair():
    payload = _value_equal_payload()
    blocker = {
        "blocker_id": "ART-001-BLK-SANCTIONS",
        "blocker_text": "exact field match not evidenced",
        "blocker_type": "SCOPE_MISMATCH",
        "required_closure_fields": {"blocker_text": "sanctions screening"},
    }
    parsed = runner._parse_key_value(_worker_output("W2", payload, "ALLOW"))

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert gate["unresolved_prior_blockers"] == [blocker]
    assert gate["deterministic_generic_blocker_resolution_ledger"][0]["resolution_status"] == (
        "PRESERVED_UNLISTED_DIMENSION_EQUIVALENCE"
    )


def test_v9_instance_binding_jurisdiction_twin_registration_digit_mismatch_survives(tmp_path):
    payload = _payload("HVSM-W2-027-A")
    mutated = copy.deepcopy(payload)
    mutated["documents"][1]["text"] = mutated["documents"][1]["text"].replace(
        "CASE-89333831CBD7",
        "CASE-89333831CBD8",
    )

    result = runner.run_blind_fixture(
        mutated,
        [
            _worker_output("W1", mutated, "ESCALATE", "exact scope match not confirmed"),
            _worker_output("W2", mutated, "ALLOW"),
            _worker_output("W3", mutated, "ALLOW"),
        ],
        str(tmp_path),
    )

    checks = runner._deterministic_affirmative_allow_support_checks(mutated)
    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"
    assert result["final"]["verdict"] != "ALLOW"


def test_v9_truth_scoring_sibling_pair_and_prior_result_fields_do_not_affect_resolution():
    clean = _payload("HVSM-W2-027-A")
    contaminated = copy.deepcopy(clean)
    contaminated.update(
        {
            "truth": "ESCALATE",
            "expected_verdict": "ESCALATE",
            "scoring_map": {"expected": "ESCALATE"},
            "sibling": "E",
            "pair_id": "HVSM-W2-027",
            "prior_solo_result": "false_positive",
            "prior_holo_result": "failed_v8_rescue",
            "authoring_target_lane": "fp_lane",
        }
    )
    blocker = {
        "blocker_id": "ART-001-BLK-GENERIC",
        "blocker_text": "exact scope match not confirmed",
        "blocker_type": "SCOPE_MISMATCH",
        "required_closure_fields": {},
    }

    assert runner._v9_generic_blocker_resolution(clean, blocker) == runner._v9_generic_blocker_resolution(contaminated, blocker)
