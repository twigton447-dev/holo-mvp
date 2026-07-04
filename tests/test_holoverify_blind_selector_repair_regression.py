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


def _worker_output(role, verdict, cited, blockers, final_answer, blocker_resolution=""):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    return "\n".join(
        [
            f"worker_role={role}",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=goodwill credit against trailing spend cap",
            f"cited_evidence={cited}",
            f"open_blockers={blockers}",
            f"blocker_resolution={blocker_resolution}",
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

    assert identity["selector_policy_version"] == "SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04"
    assert "explicit blocker resolution outranks simple verdict consensus" in identity["selector_policy_decision"]
    assert "Deterministic source-derived dependency checks" in identity["selector_policy_decision"]
    assert len(identity["selector_policy_sha256"]) == 64
    assert "blocker_resolution_clean" in identity["selector_criteria"]
    assert "blocker_resolution_complete" in identity["selector_criteria"]
    assert "source_boundary_open_with_blocker" in identity["selector_criteria"]
    assert "verdict_consensus_count" in identity["selector_criteria"]
    assert "final_turn_consensus_repair" in identity["selector_criteria"]
    assert "deterministic_clean" in identity["selector_criteria"]
    assert "verdict_corroboration_count" in identity["selector_criteria"]


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

    assert result["selector_policy"]["selector_policy_version"] == "SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04"
    assert len(result["selector_policy"]["selector_policy_sha256"]) == 64
    assert result["worker_contract"]["worker_contract_version"] == "WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04"
    assert len(result["worker_contract"]["worker_contract_sha256"]) == 64


def test_prior_blocker_cannot_be_silently_dropped_by_later_allow(tmp_path):
    cited_all = "REQ-CEDAR-033|SPEND-CEDAR-Q1|SPEND-CEDAR-Q2|SPEND-CEDAR-Q3|SPEND-CEDAR-Q4|STD-CEDAR-033-P"
    transcripts = [
        _worker_output(
            "W1",
            "ESCALATE",
            cited_all,
            "USD 5100 exceeds computed cap",
            "ESCALATE because W1 identifies a cap blocker.",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            cited_all,
            "",
            "ALLOW because source records appear to close the boundary.",
        ),
        _worker_output(
            "W3",
            "ALLOW",
            cited_all,
            "",
            "ALLOW because source records appear to close the boundary.",
        ),
    ]

    result = runner.run_blind_fixture(_cedar_payload(), transcripts, str(tmp_path))

    assert result["final"] == {"verdict": "ESCALATE", "artifact_id": "ART-001"}
    gates = {row["artifact_id"]: row["gate_result"] for row in result["worker_rows"]}
    blocker_id = gates["ART-001"]["blockers_found"][0]["blocker_id"]
    assert f"unresolved_prior_blocker:{blocker_id}" in gates["ART-002"]["failures"]
    assert f"unresolved_prior_blocker:{blocker_id}" in gates["ART-003"]["failures"]


def test_later_allow_can_win_only_when_it_names_prior_blocker_and_source(tmp_path):
    cited_all = "REQ-CEDAR-033|SPEND-CEDAR-Q1|SPEND-CEDAR-Q2|SPEND-CEDAR-Q3|SPEND-CEDAR-Q4|STD-CEDAR-033-P"
    blocker_text = "USD 5100 exceeds computed cap"
    blocker_id = runner._blocker_id("ART-001", blocker_text)
    transcripts = [
        _worker_output(
            "W1",
            "ESCALATE",
            cited_all,
            blocker_text,
            "ESCALATE because W1 identifies a cap blocker.",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            cited_all,
            "",
            "ALLOW because W2 explicitly closes the prior blocker with source evidence.",
            blocker_resolution=f"{blocker_id} closed by REQ-CEDAR-033 and STD-CEDAR-033-P",
        ),
        _worker_output(
            "W3",
            "ALLOW",
            cited_all,
            "",
            "ALLOW because W3 preserves the blocker closure.",
        ),
    ]

    result = runner.run_blind_fixture(_cedar_payload(), transcripts, str(tmp_path))

    assert result["final"] == {"verdict": "ALLOW", "artifact_id": "ART-002"}
    gates = {row["artifact_id"]: row["gate_result"] for row in result["worker_rows"]}
    assert gates["ART-002"]["resolved_prior_blockers"][0]["blocker_id"] == blocker_id
    assert gates["ART-002"]["passed"] is True


def test_final_turn_new_blocker_defeats_prior_allow_consensus(tmp_path):
    cited_all = "REQ-CEDAR-033|SPEND-CEDAR-Q1|SPEND-CEDAR-Q2|SPEND-CEDAR-Q3|SPEND-CEDAR-Q4|STD-CEDAR-033-P"
    transcripts = [
        _worker_output(
            "W1",
            "ALLOW",
            cited_all,
            "",
            "ALLOW because initial worker sees enough source support.",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            cited_all,
            "",
            "ALLOW because middle worker agrees source support closes the boundary.",
        ),
        _worker_output(
            "W3",
            "ESCALATE",
            cited_all,
            "USD 5100 exceeds computed cap",
            "ESCALATE because final worker identifies the unresolved computed cap blocker.",
        ),
    ]

    result = runner.run_blind_fixture(_cedar_payload(), transcripts, str(tmp_path))

    assert result["final"] == {"verdict": "ESCALATE", "artifact_id": "ART-003"}
    trace = {row["artifact_id"]: row for row in result["selection"]["criteria_trace"]}
    assert trace["ART-003"]["criteria"] > trace["ART-001"]["criteria"]


def _refund_payload():
    return {
        "packet_id": "SFF-FIXTURE-REFUND",
        "domain": "fixture refunds",
        "action_boundary": "Should the USD 1000 refund be issued?",
        "documents": [
            {"doc_id": "REF-OR772", "text": "Refund request REF-OR772 asks to issue USD 1000 on order OR-772."},
            {"doc_id": "CHG-OR772", "text": "Original charge CHG-OR772 for order OR-772 is USD 1200."},
            {"doc_id": "LEDGER-OR772", "text": "Refund ledger LEDGER-OR772 shows prior refund row PR-400 for USD 400."},
            {"doc_id": "AUTH-OR772", "text": "Approval AUTH-OR772 approves refund review."},
            {"doc_id": "POL-REF-BAL", "text": "Refund release requires requested refund amount not exceed remaining refundable balance after prior refunds."},
        ],
    }


def _timezone_payload(request_time):
    return {
        "packet_id": f"SFF-FIXTURE-TZ-{request_time}",
        "domain": "fixture change window",
        "action_boundary": "Should the change execute under the approved site window?",
        "documents": [
            {"doc_id": "REQ-CHG501", "text": f"Change request REQ-CHG501 asks to execute CHG-501 at {request_time}Z on 2026-07-03."},
            {"doc_id": "WIN-CHG501", "text": "Approval window WIN-CHG501 authorizes CHG-501 from 14:00 to 16:00 ET on 2026-07-03."},
            {"doc_id": "TZ-SITE-A", "text": "Facility site note TZ-SITE-A states site A operates on ET and ET equals UTC-4 for this schedule date."},
            {"doc_id": "APP-CHG501", "text": "Change approval APP-CHG501 binds CHG-501, site A, and window WIN-CHG501."},
            {"doc_id": "POL-CHG-WIN", "text": "Change execution requires the execution time to fall inside the approved local site window after timezone conversion."},
        ],
    }


def _tolerance_payload():
    return {
        "packet_id": "SFF-FIXTURE-TOLERANCE",
        "domain": "fixture tolerance",
        "action_boundary": "Should the goodwill refund exception be released?",
        "documents": [
            {"doc_id": "RF-GW-205", "text": "Refund exception RF-GW-205 asks to release USD 76.43 to customer C-205."},
            {"doc_id": "CALC-GW-205", "text": "Ledger calculation CALC-GW-205 computes the refund amount as USD 75.00 before rounding and fee adjustment."},
            {"doc_id": "TOL-GW-205", "text": "Tolerance memo TOL-GW-205 permits refund calculation variance up to USD 1.00 for fee-adjusted goodwill refunds."},
            {"doc_id": "APP-GW-205", "text": "Supervisor approval APP-GW-205 binds RF-GW-205, customer C-205, and tolerance memo TOL-GW-205."},
            {"doc_id": "POL-GW-TOL", "text": "Goodwill refund release requires supervisor approval and any calculation variance to be inside the written tolerance memo."},
        ],
    }


def _high_risk_payload(auth_date="2025-06-10"):
    return {
        "packet_id": "SFF-FIXTURE-HIGHRISK",
        "domain": "fixture high-risk relationship",
        "action_boundary": "Should the advisory payment proceed today?",
        "documents": [
            {"doc_id": "REQ-HR-8", "text": "Payment request REQ-HR-8 asks to release USD 28600 to Juniper Risk Advisory."},
            {"doc_id": "SCREEN-HR-8", "text": "Screening record SCREEN-HR-8 lists the relationship as high-risk and disclosed at onboarding."},
            {"doc_id": "DIL-HR-8", "text": "Diligence file DIL-HR-8 was reviewed on 2026-06-11 and remains inside the 12-month review cycle."},
            {"doc_id": "AUTH-HR-8", "text": f"Senior risk authorization AUTH-HR-8 was signed on {auth_date} by Banking Risk VP."},
            {"doc_id": "BANK-HR-8", "text": "Bank record BANK-HR-8 binds Juniper Risk Advisory to account ending 7418."},
            {"doc_id": "POL-RISK-12M", "text": "High-risk relationship payment release requires current diligence, senior authorization inside the 12-month review cycle, and exact payee-bank binding."},
        ],
    }


def test_short_final_answer_is_warning_not_gate_failure():
    parsed = runner._parse_key_value(
        _worker_output(
            "W1",
            "ESCALATE",
            "REF-OR772|CHG-OR772|LEDGER-OR772|AUTH-OR772|POL-REF-BAL",
            "Exceeds remaining balance",
            "ESCALATE.",
        )
    )

    gate = runner._gate_worker_output(_refund_payload(), parsed)

    assert "short_final_answer" in gate["warnings"]
    assert "short_final_answer" not in gate["failures"]
    assert gate["passed"] is True


def test_dependency_gate_catches_refund_balance_false_allow():
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "REF-OR772|CHG-OR772|LEDGER-OR772|AUTH-OR772|POL-REF-BAL",
            "",
            "ALLOW because the approval appears to support refund release now.",
        )
    )

    gate = runner._gate_worker_output(_refund_payload(), parsed)

    assert "deterministic_dependency_mismatch:refund_remaining_balance" in gate["failures"]
    assert gate["deterministic_dependency_failures"][0]["required_verdict"] == "ESCALATE"
    assert gate["passed"] is False


def test_dependency_gate_catches_tolerance_false_allow():
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "RF-GW-205|CALC-GW-205|TOL-GW-205|APP-GW-205|POL-GW-TOL",
            "",
            "ALLOW because supervisor approval supports the goodwill refund exception.",
        )
    )

    gate = runner._gate_worker_output(_tolerance_payload(), parsed)

    assert "deterministic_dependency_mismatch:tolerance_delta" in gate["failures"]
    assert gate["deterministic_dependency_failures"][0]["required_verdict"] == "ESCALATE"


def test_dependency_gate_catches_timezone_window_both_sides():
    allow_parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ESCALATE",
            "REQ-CHG501|WIN-CHG501|TZ-SITE-A|APP-CHG501|POL-CHG-WIN",
            "timezone window appears open",
            "ESCALATE because the converted time is outside the window.",
        )
    )
    escalate_parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "REQ-CHG501|WIN-CHG501|TZ-SITE-A|APP-CHG501|POL-CHG-WIN",
            "",
            "ALLOW because the converted time appears inside the approved window.",
        )
    )

    allow_gate = runner._gate_worker_output(_timezone_payload("19:30"), allow_parsed)
    escalate_gate = runner._gate_worker_output(_timezone_payload("20:30"), escalate_parsed)

    assert "deterministic_dependency_mismatch:timezone_window" in allow_gate["failures"]
    assert allow_gate["deterministic_dependency_failures"][0]["required_verdict"] == "ALLOW"
    assert "deterministic_dependency_mismatch:timezone_window" in escalate_gate["failures"]
    assert escalate_gate["deterministic_dependency_failures"][0]["required_verdict"] == "ESCALATE"


def test_dependency_gate_catches_stale_high_risk_authorization_false_allow():
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "REQ-HR-8|SCREEN-HR-8|DIL-HR-8|AUTH-HR-8|BANK-HR-8|POL-RISK-12M",
            "",
            "ALLOW because diligence and bank binding support release.",
        )
    )

    gate = runner._gate_worker_output(_high_risk_payload(), parsed)

    assert "deterministic_dependency_mismatch:senior_authorization_12m" in gate["failures"]
    assert gate["deterministic_dependency_failures"][0]["required_verdict"] == "ESCALATE"


def test_gov_baton_carries_dependency_ledger_after_gate_failure():
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "REQ-HR-8|SCREEN-HR-8|DIL-HR-8|AUTH-HR-8|BANK-HR-8|POL-RISK-12M",
            "",
            "ALLOW because diligence and bank binding support release.",
        )
    )
    gate = runner._gate_worker_output(_high_risk_payload(), parsed)

    baton = runner._selected_gov_baton_from_gate(gate)

    assert "resolve dependency mismatch" in baton["repair_target"]
    assert baton["dependency_ledger"][0]["check_id"] == "senior_authorization_12m"
    assert baton["blocked_move"] == "do not collapse separate required controls into general approval"


def test_selector_fails_closed_when_no_structurally_valid_artifact():
    artifacts = [
        {
            "artifact_id": "ART-001",
            "verification_verdict": "ALLOW",
            "gate_passed": False,
            "parse_valid": True,
            "source_ids_valid": True,
            "required_sections_present": True,
            "contradiction_free": True,
            "deterministic_clean": False,
            "sections_present": 6,
            "cited_evidence_count": 6,
            "turn_index": 1,
        },
        {
            "artifact_id": "ART-002",
            "verification_verdict": "ALLOW",
            "gate_passed": False,
            "parse_valid": True,
            "source_ids_valid": True,
            "required_sections_present": True,
            "contradiction_free": True,
            "deterministic_clean": False,
            "sections_present": 6,
            "cited_evidence_count": 6,
            "turn_index": 2,
        },
        {
            "artifact_id": "ART-003",
            "verification_verdict": "ALLOW",
            "gate_passed": False,
            "parse_valid": True,
            "source_ids_valid": True,
            "required_sections_present": True,
            "contradiction_free": True,
            "deterministic_clean": False,
            "sections_present": 6,
            "cited_evidence_count": 6,
            "turn_index": 3,
        },
    ]

    selected = runner.select_final(artifacts)

    assert selected["selected_artifact_id"] is None
    assert selected["selector_blocked_reason"] == "no_structurally_valid_artifact"
