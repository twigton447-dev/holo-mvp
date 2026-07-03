import holoverify_blind_runner_v0 as runner


def _artifact(aid, verdict, turn_index, cited=6, truth_marker=None):
    artifact = {
        "artifact_id": aid,
        "verification_verdict": verdict,
        "gate_passed": True,
        "parse_valid": True,
        "source_ids_valid": True,
        "required_sections_present": True,
        "contradiction_free": True,
        "sections_present": 6,
        "cited_evidence_count": cited,
        "turn_index": turn_index,
    }
    if truth_marker is not None:
        artifact["truth"] = truth_marker
        artifact["expected_verdict"] = truth_marker
    return artifact


def _grid_artifacts(pattern, truth_marker=None):
    return [
        _artifact("ART-001", pattern[0], 1, cited=6, truth_marker=truth_marker),
        _artifact("ART-002", pattern[1], 2, cited=7, truth_marker=truth_marker),
        _artifact("ART-003", pattern[2], 3, cited=6, truth_marker=truth_marker),
    ]


def _cedar_payload():
    return {
        "packet_id": "ATLASRESCUE-FIXTURE-033B",
        "domain": "fixture",
        "action_boundary": "May customer operations approve the goodwill credit under the trailing-spend cap?",
        "communication_boundary": "Decide only from source-control records.",
        "documents": [
            {
                "doc_id": "REQ-CEDAR-033",
                "source_type": "source_record",
                "text": "Goodwill credit request asks for USD 5100 for customer C-881.",
            },
            {"doc_id": "SPEND-CEDAR-Q1", "source_type": "source_record", "text": "Q1 spend is USD 9200."},
            {"doc_id": "SPEND-CEDAR-Q2", "source_type": "source_record", "text": "Q2 spend is USD 8100."},
            {"doc_id": "SPEND-CEDAR-Q3", "source_type": "source_record", "text": "Q3 spend is USD 7400."},
            {"doc_id": "SPEND-CEDAR-Q4", "source_type": "source_record", "text": "Q4 spend is USD 8800."},
            {
                "doc_id": "STD-CEDAR-033-P",
                "source_type": "policy_control",
                "text": "Goodwill credit may not exceed 15 percent of trailing twelve-month spend.",
            },
        ],
    }


def _worker_output(role, verdict, cited, blockers, final_answer):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    return "\n".join(
        [
            f"worker_role={role}",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=goodwill credit against trailing spend cap",
            f"cited_evidence={cited}",
            f"open_blockers={blockers}",
            f"final_answer={final_answer}",
        ]
    )


def test_selector_prefers_final_source_grounded_repair_over_wrong_middle_artifact(tmp_path):
    cited_all = "REQ-CEDAR-033|SPEND-CEDAR-Q1|SPEND-CEDAR-Q2|SPEND-CEDAR-Q3|SPEND-CEDAR-Q4|STD-CEDAR-033-P"
    transcripts = [
        _worker_output(
            "W1",
            "ESCALATE",
            cited_all,
            "USD 5100 exceeds computed USD 5025 cap",
            "ESCALATE because USD 5100 exceeds the 15 percent trailing spend cap.",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            cited_all,
            "",
            "ALLOW because source records appear to close the goodwill credit boundary.",
        ),
        _worker_output(
            "W3",
            "ESCALATE",
            cited_all,
            "USD 5100 exceeds computed USD 5025 cap",
            "ESCALATE because USD 5100 is greater than the computed USD 5025 cap.",
        ),
    ]

    result = runner.run_blind_fixture(_cedar_payload(), transcripts, str(tmp_path))

    assert result["final"] == {"verdict": "ESCALATE", "artifact_id": "ART-003"}
    trace = {row["artifact_id"]: row for row in result["selection"]["criteria_trace"]}
    assert trace["ART-003"]["verification_verdict"] == "ESCALATE"
    assert trace["ART-003"]["criteria"] > trace["ART-002"]["criteria"]


def test_direct_selector_repair_consensus_is_truth_blind():
    artifacts = [
        {
            "artifact_id": "ART-001",
            "verification_verdict": "ESCALATE",
            "gate_passed": True,
            "parse_valid": True,
            "source_ids_valid": True,
            "required_sections_present": True,
            "contradiction_free": True,
            "sections_present": 6,
            "cited_evidence_count": 6,
            "turn_index": 1,
        },
        {
            "artifact_id": "ART-002",
            "verification_verdict": "ALLOW",
            "gate_passed": True,
            "parse_valid": True,
            "source_ids_valid": True,
            "required_sections_present": True,
            "contradiction_free": True,
            "sections_present": 6,
            "cited_evidence_count": 7,
            "turn_index": 2,
        },
        {
            "artifact_id": "ART-003",
            "verification_verdict": "ESCALATE",
            "gate_passed": True,
            "parse_valid": True,
            "source_ids_valid": True,
            "required_sections_present": True,
            "contradiction_free": True,
            "sections_present": 6,
            "cited_evidence_count": 6,
            "turn_index": 3,
        },
    ]

    selected = runner.select_final(artifacts)

    assert selected["selected_artifact_id"] == "ART-003"


def test_selector_policy_identity_is_stable_and_explicit():
    identity = runner.selector_policy_identity()

    assert identity["selector_policy_version"] == "SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03"
    assert "two-of-three structurally valid consensus" in identity["selector_policy_decision"]
    assert len(identity["selector_policy_sha256"]) == 64
    assert "verdict_consensus_count" in identity["selector_criteria"]
    assert "final_turn_consensus_repair" in identity["selector_criteria"]


def test_selector_full_verdict_grid_documents_consensus_tradeoffs():
    expected = {
        ("ALLOW", "ALLOW", "ALLOW"): "ART-002",
        ("ALLOW", "ALLOW", "ESCALATE"): "ART-002",
        ("ALLOW", "ESCALATE", "ALLOW"): "ART-003",
        ("ALLOW", "ESCALATE", "ESCALATE"): "ART-003",
        ("ESCALATE", "ALLOW", "ALLOW"): "ART-003",
        ("ESCALATE", "ALLOW", "ESCALATE"): "ART-003",
        ("ESCALATE", "ESCALATE", "ALLOW"): "ART-002",
        ("ESCALATE", "ESCALATE", "ESCALATE"): "ART-002",
    }

    actual = {
        pattern: runner.select_final(_grid_artifacts(pattern))["selected_artifact_id"]
        for pattern in expected
    }

    assert actual == expected


def test_selector_verdict_grid_is_invariant_under_truth_swap_markers():
    patterns = [
        ("ALLOW", "ALLOW", "ALLOW"),
        ("ALLOW", "ALLOW", "ESCALATE"),
        ("ALLOW", "ESCALATE", "ALLOW"),
        ("ALLOW", "ESCALATE", "ESCALATE"),
        ("ESCALATE", "ALLOW", "ALLOW"),
        ("ESCALATE", "ALLOW", "ESCALATE"),
        ("ESCALATE", "ESCALATE", "ALLOW"),
        ("ESCALATE", "ESCALATE", "ESCALATE"),
    ]

    for pattern in patterns:
        picks = {
            truth: runner.select_final(_grid_artifacts(pattern, truth_marker=truth))["selected_artifact_id"]
            for truth in ("ALLOW", "ESCALATE")
        }
        assert picks["ALLOW"] == picks["ESCALATE"], (pattern, picks)


def test_runtime_result_stamps_selector_version_and_hash(tmp_path):
    transcripts = [
        _worker_output(
            "W1",
            "ESCALATE",
            "REQ-CEDAR-033|SPEND-CEDAR-Q1|SPEND-CEDAR-Q2|SPEND-CEDAR-Q3|SPEND-CEDAR-Q4|STD-CEDAR-033-P",
            "USD 5100 exceeds computed cap",
            "ESCALATE because USD 5100 exceeds the computed cap.",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            "REQ-CEDAR-033|SPEND-CEDAR-Q1|SPEND-CEDAR-Q2|SPEND-CEDAR-Q3|SPEND-CEDAR-Q4|STD-CEDAR-033-P",
            "",
            "ALLOW because source records appear to close the boundary.",
        ),
        _worker_output(
            "W3",
            "ESCALATE",
            "REQ-CEDAR-033|SPEND-CEDAR-Q1|SPEND-CEDAR-Q2|SPEND-CEDAR-Q3|SPEND-CEDAR-Q4|STD-CEDAR-033-P",
            "USD 5100 exceeds computed cap",
            "ESCALATE because final repair restores the cap failure.",
        ),
    ]

    result = runner.run_blind_fixture(_cedar_payload(), transcripts, str(tmp_path))

    assert result["selector_policy"]["selector_policy_version"] == "SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03"
    assert len(result["selector_policy"]["selector_policy_sha256"]) == 64
    assert result["worker_contract"]["worker_contract_version"] == "WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03"
    assert len(result["worker_contract"]["worker_contract_sha256"]) == 64
