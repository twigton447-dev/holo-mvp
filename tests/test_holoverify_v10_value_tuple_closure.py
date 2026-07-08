import copy
import json
from pathlib import Path

import holoverify_blind_runner_v0 as runner


REPO_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_v10_repaired_packet_bank_2026_07_07"
    / "runtime_payloads"
)
ORIGINAL_WAVE2_PAYLOAD_ROOT = (
    REPO_ROOT
    / "docs"
    / "benchmark"
    / "holoverify_stress_matrix_expansion_wave2_2026_07_06"
    / "runtime_payloads"
)

PACKETS = {
    "HVSM-W2-009-A": "PKT-B5B6E467B0E5DA2DC74DDC3D",
    "HVSM-W2-009-E": "PKT-12511FF461EBEA702CEAF17E",
}
ORIGINAL_WAVE2_PACKETS = {
    "HVSM-W2-009-A": "HVSMW2-EADF3B3DC5465BFAA006",
}


def _payload(legacy_packet_id):
    return json.loads((PAYLOAD_ROOT / f"{PACKETS[legacy_packet_id]}.json").read_text())


def _original_wave2_payload(legacy_packet_id):
    return json.loads(
        (ORIGINAL_WAVE2_PAYLOAD_ROOT / f"{ORIGINAL_WAVE2_PACKETS[legacy_packet_id]}.json").read_text()
    )


def _cited(payload):
    return "|".join(doc["doc_id"] for doc in payload["documents"])


def _worker_output(role, payload, verdict, blocker_text="", blocker_type="SCOPE_MISMATCH"):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    final_answer = (
        "ALLOW because the exact runtime value tuple closes the source boundary."
        if verdict == "ALLOW"
        else "ESCALATE because the exact runtime value tuple leaves the source boundary open."
    )
    return "\n".join(
        [
            f"worker_role={role}",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=runtime-visible exact value tuple boundary",
            f"cited_evidence={_cited(payload)}",
            f"open_blockers={blocker_text if verdict == 'ESCALATE' else ''}",
            f"blocker_type={blocker_type if verdict == 'ESCALATE' else ''}",
            "blocker_resolution=",
            "structured_blocker_resolution=",
            f"final_answer={final_answer}",
        ]
    )


def test_v10_repaired_009_a_value_tuple_source_closes_and_selects_allow(tmp_path):
    payload = _payload("HVSM-W2-009-A")

    checks = runner._deterministic_affirmative_allow_support_checks(payload)
    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ESCALATE", "exact field match not evidenced"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert checks[0]["closure_type"] == "SURGICAL_USE_AFTER_WARNING_CLOSED"
    assert checks[0]["closure_status"] == "SOURCE_CLOSED"
    assert checks[0]["value_equality_status"] == "VALUE_EQUALITY_PROVEN"
    assert checks[0]["matched_source_fields"]["surgeon_match"] == "value:surgeon_match"
    assert result["final"]["verdict"] == "ALLOW"
    assert result["packet_selectable"] is True


def test_v10_repaired_009_e_absent_approval_is_source_open_and_selects_escalate(tmp_path):
    payload = _payload("HVSM-W2-009-E")

    checks = runner._deterministic_affirmative_allow_support_checks(payload)
    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ESCALATE", "exact field match not evidenced"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert checks[0]["closure_type"] == "SURGICAL_USE_AFTER_WARNING_CLOSED"
    assert checks[0]["closure_status"] == "SOURCE_OPEN"
    assert checks[0]["required_verdict"] == "ESCALATE"
    assert checks[0]["value_equality_status"] == "VALUE_MISMATCH"
    assert result["final"]["verdict"] == "ESCALATE"
    assert result["packet_selectable"] is True


def test_v10_repaired_009_missing_value_still_requires_packet_repair():
    payload = copy.deepcopy(_payload("HVSM-W2-009-A"))
    payload["documents"][1]["text"] = payload["documents"][1]["text"].replace(
        " surgeon_id=SURG-2049;",
        " ",
    )

    checks = runner._deterministic_affirmative_allow_support_checks(payload)

    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"
    assert checks[0]["matched_source_fields"].get("surgeon_match") is None


def test_v10_original_wave2_009_a_name_list_only_stays_fail_closed(tmp_path):
    payload = _original_wave2_payload("HVSM-W2-009-A")

    checks = runner._deterministic_affirmative_allow_support_checks(payload)
    result = runner.run_blind_fixture(
        payload,
        [
            _worker_output("W1", payload, "ALLOW"),
            _worker_output("W2", payload, "ALLOW"),
            _worker_output("W3", payload, "ALLOW"),
        ],
        str(tmp_path),
    )

    assert checks[0]["closure_type"] == "SURGICAL_USE_AFTER_WARNING_CLOSED"
    assert checks[0]["closure_status"] == "PACKET_REPAIR_REQUIRED"
    assert checks[0]["value_equality_status"] == "MISSING_REQUIRED_FIELD_VALUE"
    assert result["final"]["verdict"] != "ALLOW"
    assert result["packet_selectable"] is False
