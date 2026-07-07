import json
from pathlib import Path

import holoverify_blind_runner_v0 as runner
from blind_lane_suite.fixtures import model_visible_payload, SYNTHETIC_PAIR_SPEC


def _simple_payload(packet_id: str) -> dict:
    payload = model_visible_payload(SYNTHETIC_PAIR_SPEC, "A")
    payload.update(
        {
            "packet_id": packet_id,
            "documents": [
                {"doc_id": "SRC-FIXTURE", "text": "source record A"},
                {"doc_id": "SRC-FIXTURE-ALT", "text": "source record B"},
            ],
        }
    )
    return payload


def _worker_output(role: str) -> str:
    return "\n".join(
        [
            f"worker_role={role}",
            "verification_verdict=ALLOW",
            "binding_class=SOURCE_BOUNDARY_CLOSED",
            "action_boundary=fixture closure boundary",
            "cited_evidence=SRC-FIXTURE",
            "open_blockers=",
            "blocker_type=",
            "blocker_resolution=",
            "structured_blocker_resolution=",
            "final_answer=ALLOW because the source record fully closes the requested boundary in the fixture.",
        ]
    )


def _gov_output() -> str:
    return "\n".join(
        [
            "route_verdict=CONTINUE",
            "repair_target=preserve blind source-grounded reasoning",
            "blocked_move=do not invent source IDs",
        ]
    )


def _slot_for_call(call_index: int) -> str:
    return ["W1", "G1", "W2", "G2", "W3"][(call_index - 1) % 5]


def test_worker_contract_missing_cited_evidence_marks_packet_invalid_not_exception(tmp_path):
    payload = _simple_payload("PKT-FCC-1")

    def transport(_messages):
        raise runner.BlindRunnerContentFailure("W1_worker_contract_missing:cited_evidence")

    result = runner.run_blind_fixture(payload, [], str(tmp_path), transport=transport)

    assert result["packet_status"] == "INVALID_CONTENT_CONTRACT"
    assert result["contract_failure_marker"] is True
    assert result["packet_failure_slot"] == "W1"
    assert result["packet_failure_tag"] == "W1_worker_contract_missing:cited_evidence"
    assert result["final"]["verdict"] is None
    assert result["selection"]["selected_artifact_id"] is None
    assert result["selection"]["selector_blocked_reason"] == "content_contract_failure"
    assert result["packet_selectable"] is False
    call = json.loads(result["packet_failure_call"])
    assert call["packet_id"] == "PKT-FCC-1"
    assert call["failure"] == "W1_worker_contract_missing:cited_evidence"


def test_content_contract_failure_is_not_retried(tmp_path):
    payload = _simple_payload("PKT-FCC-2")
    state = {"count": 0}

    def transport(_messages):
        state["count"] += 1
        raise runner.BlindRunnerContentFailure("W1_worker_contract_missing:cited_evidence")

    result = runner.run_blind_fixture(payload, [], str(tmp_path), transport=transport)

    assert result["packet_status"] == "INVALID_CONTENT_CONTRACT"
    assert state["count"] == 1
    assert result["retry_log"] == []


def test_content_contract_failure_packet_is_skipped_and_next_packet_completes(tmp_path):
    payload_a = _simple_payload("PKT-FCC-3-A")
    payload_b = _simple_payload("PKT-FCC-3-B")
    payload_a_path = tmp_path / "PKT-FCC-3-A.json"
    payload_b_path = tmp_path / "PKT-FCC-3-B.json"
    payload_a_path.write_text(json.dumps(payload_a, indent=2, sort_keys=True) + "\n")
    payload_b_path.write_text(json.dumps(payload_b, indent=2, sort_keys=True) + "\n")

    runtime_manifest = {
        "runtime_consumable": True,
        "packet_count": 2,
        "packets": [
            {"runtime_payload_ref": str(payload_a_path), "packet_id": payload_a["packet_id"]},
            {"runtime_payload_ref": str(payload_b_path), "packet_id": payload_b["packet_id"]},
        ],
    }
    runtime_path = tmp_path / "runtime_manifest.json"
    runtime_path.write_text(json.dumps(runtime_manifest, indent=2, sort_keys=True) + "\n")

    state = {"call": 0}

    def transport(messages):
        state["call"] += 1
        if state["call"] == 1:
            raise runner.BlindRunnerContentFailure("W1_worker_contract_missing:cited_evidence")
        slot = _slot_for_call(state["call"])
        if slot in {"G1", "G2"}:
            return _gov_output()
        return _worker_output(slot)

    results = runner.run_blind_runtime_manifest(str(runtime_path), str(tmp_path / "out"), transport=transport)

    assert results["packet_count"] == 2
    assert len(results["results"]) == 2
    assert results["observed_call_count"] == 6
    assert results["results"][0]["packet_status"] == "INVALID_CONTENT_CONTRACT"
    assert results["results"][0]["packet_failure_slot"] == "W1"
    assert results["results"][0]["packet_selectable"] is False
    assert results["results"][1]["packet_status"] == "SELECTED"
    assert results["results"][1]["final"]["verdict"] == "ALLOW"
    assert results["results"][1]["packet_selectable"] is True
    assert state["call"] == 6
    assert not any(row.get("packet_status") == "INVALID_CONTENT_CONTRACT" for row in results["results"][1:])
    assert not results["results"][1]["selection"]["selected_artifact_id"] is None
