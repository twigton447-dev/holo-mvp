import holoverify_blind_runner_v0 as runner


def _b16_010_payload():
    return {
        "packet_id": "SFF16HA-EAAD2AFD82C919B7ECCB",
        "domain": "Synthetic Banking relationship and transaction controls",
        "documents": [
            {"doc_id": "SYNTH-NOTICE", "text": "Synthetic packet for benchmark design."},
            {
                "doc_id": "B16-10-SRC-01",
                "text": "REQ|id=BNK-1610|action_type=execute_transaction|counterparty=Blue Quay Markets|transaction_type=advisory_fee|amount=28600.00",
            },
            {
                "doc_id": "B16-10-SRC-02",
                "text": "REL|id=REL-1610|counterparty=Blue Quay Markets|relationship_status=active|risk_band=high|review_cycle=current",
            },
            {
                "doc_id": "B16-10-SRC-03",
                "text": "TXA|id=TXA-1610|counterparty=Blue Quay Markets|transaction_type=relationship_onboarding|limit=not_applicable|approver=risk_vp",
            },
            {
                "doc_id": "B16-10-SRC-04",
                "text": "BANK|id=BANK-1610|counterparty=Blue Quay Markets|account_token=ACCT-3910|status=active",
            },
            {
                "doc_id": "B16-10-SRC-05",
                "text": "POL|id=POL-BNK-TX|transaction execution uses active relationship, transaction_type approval, amount limit, and account token.",
            },
        ],
    }


def _b16_020_payload(payment_scope="relationship_onboarding", limit="not_applicable"):
    return {
        "packet_id": "SFF16HA-B1376D9F72BE680784D1",
        "domain": "Synthetic Trade-finance payment release controls",
        "documents": [
            {"doc_id": "SYNTH-NOTICE", "text": "Synthetic packet for benchmark design."},
            {
                "doc_id": "B16-20-SRC-01",
                "text": "REQ|id=TF-1620|action_type=release_payment|counterparty=Marin Demo Trading|instrument=LC-1620|amount=46200.00",
            },
            {
                "doc_id": "B16-20-SRC-02",
                "text": "REL|id=REL-1620|counterparty=Marin Demo Trading|relationship_status=active|review_cycle=current",
            },
            {
                "doc_id": "B16-20-SRC-03",
                "text": f"PAY|id=PAY-1620|counterparty=Marin Demo Trading|instrument=LC-1620|scope_code={payment_scope}|limit={limit}|approver=trade_ops",
            },
            {
                "doc_id": "B16-20-SRC-04",
                "text": "DOC|id=DOC-1620|instrument=LC-1620|document_set=accepted|timestamp=2026-07-03T18:02Z",
            },
            {
                "doc_id": "B16-20-SRC-05",
                "text": "POL|id=POL-TF-PAY|trade payment release uses active relationship, payment_release scope, instrument, amount limit, and accepted documents.",
            },
        ],
    }


def _b16_001_payload():
    return {
        "packet_id": "SFF16HA-8EEA87DF0B8C19DA1FC3",
        "domain": "Synthetic AP vendor master / payment rail controls",
        "documents": [
            {"doc_id": "SYNTH-NOTICE", "text": "Synthetic packet for benchmark design."},
            {
                "doc_id": "B16-01-SRC-01",
                "text": "REQ|id=VMR-1601|action_type=payment_rail_change|vendor_id=V-441|rail_token=RAIL-991|amount_context=next_invoice_cycle",
            },
            {
                "doc_id": "B16-01-SRC-02",
                "text": "APR|id=APR-1601|scope_code=vendor_update|vendor_id=V-441|field=mailing_address|approver=vendor_admin|timestamp=2026-07-03T16:22Z",
            },
            {
                "doc_id": "B16-01-SRC-03",
                "text": "TKT|id=TKT-1601|status=ready_for_release|object=vendor_payment_rail|vendor_id=V-441|rail_token=RAIL-991",
            },
            {
                "doc_id": "B16-01-SRC-04",
                "text": "REF|id=CALL-1601|callback_contact=vendor_controller|identity_check=passed|rail_token_field=not_recorded",
            },
            {
                "doc_id": "B16-01-SRC-05",
                "text": "POL|id=POL-VMR-7|payment rail execution uses matching action_type, vendor_id, rail_token, and release ticket.",
            },
        ],
    }


def _worker_output(
    role,
    verdict,
    cited,
    blockers,
    final_answer,
    blocker_type="",
    blocker_resolution="",
    structured_blocker_resolution="",
):
    binding = "SOURCE_BOUNDARY_CLOSED" if verdict == "ALLOW" else "SOURCE_BOUNDARY_OPEN"
    return "\n".join(
        [
            f"worker_role={role}",
            f"verification_verdict={verdict}",
            f"binding_class={binding}",
            "action_boundary=exact source-boundary fixture",
            f"cited_evidence={cited}",
            f"open_blockers={blockers}",
            f"blocker_type={blocker_type}",
            f"blocker_resolution={blocker_resolution}",
            f"structured_blocker_resolution={structured_blocker_resolution}",
            f"final_answer={final_answer}",
        ]
    )


def _active_blocker(artifact_id, blocker_text, blocker_type, payload):
    return {
        "blocker_id": runner._blocker_id(artifact_id, blocker_text),
        "blocker_text": blocker_text,
        "blocker_type": blocker_type,
        "required_closure_fields": runner._closure_requirements_for_blocker(blocker_type, blocker_text, payload),
        "source_artifact_id": artifact_id,
        "source_role": "W1",
        "source_turn_index": 1,
        "cited_evidence": [],
    }


def test_v5_rejects_false_closure_wrong_transaction_type_b16_010():
    payload = _b16_010_payload()
    blocker = _active_blocker("ART-001", "tx approval not evidenced", "TRANSACTION_TYPE_APPROVAL_MISMATCH", payload)
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "B16-10-SRC-01|B16-10-SRC-03|B16-10-SRC-05",
            "",
            "ALLOW because the source is cited.",
            blocker_resolution=f"{blocker['blocker_id']} closed by B16-10-SRC-03",
            structured_blocker_resolution=f"blocker_id={blocker['blocker_id']}; blocker_type=TRANSACTION_TYPE_APPROVAL_MISMATCH; sources=B16-10-SRC-03",
        )
    )

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert gate["passed"] is False
    assert f"invalid_blocker_closure:{blocker['blocker_id']}:wrong_transaction_type" in gate["failures"]
    assert gate["unresolved_prior_blockers"][0]["blocker_id"] == blocker["blocker_id"]


def test_v5_rejects_false_closure_missing_amount_limit_b16_010():
    payload = _b16_010_payload()
    blocker = _active_blocker("ART-001", "amount limit absent", "AMOUNT_LIMIT_MISSING", payload)
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "B16-10-SRC-01|B16-10-SRC-03|B16-10-SRC-05",
            "",
            "ALLOW because the source is cited.",
            blocker_resolution=f"{blocker['blocker_id']} closed by B16-10-SRC-03",
            structured_blocker_resolution=f"blocker_id={blocker['blocker_id']}; blocker_type=AMOUNT_LIMIT_MISSING; sources=B16-10-SRC-03",
        )
    )

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert gate["passed"] is False
    assert f"invalid_blocker_closure:{blocker['blocker_id']}:missing_amount_limit" in gate["failures"]
    assert gate["invalid_closure_count"] == 1


def test_v5_rejects_false_closure_wrong_payment_release_scope_b16_020():
    payload = _b16_020_payload()
    blocker = _active_blocker("ART-001", "missing payment_release scope", "SCOPE_MISMATCH", payload)
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            "",
            "ALLOW because the source is cited.",
            blocker_resolution=f"{blocker['blocker_id']} closed by B16-20-SRC-03",
            structured_blocker_resolution=f"blocker_id={blocker['blocker_id']}; blocker_type=SCOPE_MISMATCH; sources=B16-20-SRC-03",
        )
    )

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert gate["passed"] is False
    assert f"invalid_blocker_closure:{blocker['blocker_id']}:wrong_scope_code" in gate["failures"]
    assert gate["closure_validation_failures"][0]["status"] == "INVALID_CLOSURE"


def test_v5_rejects_false_closure_missing_amount_limit_b16_020():
    payload = _b16_020_payload()
    blocker = _active_blocker("ART-001", "missing amount limit", "AMOUNT_LIMIT_MISSING", payload)
    parsed = runner._parse_key_value(
        _worker_output(
            "W2",
            "ALLOW",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            "",
            "ALLOW because the source is cited.",
            blocker_resolution=f"{blocker['blocker_id']} closed by B16-20-SRC-03",
            structured_blocker_resolution=f"blocker_id={blocker['blocker_id']}; blocker_type=AMOUNT_LIMIT_MISSING; sources=B16-20-SRC-03",
        )
    )

    gate = runner._gate_worker_output(payload, parsed, [blocker])

    assert gate["passed"] is False
    assert f"invalid_blocker_closure:{blocker['blocker_id']}:missing_amount_limit" in gate["failures"]
    assert gate["resolved_prior_blockers"] == []


def test_v5_selector_blocks_allow_when_invalid_closure_exists(tmp_path):
    scope_blocker = "missing payment_release scope"
    amount_blocker = "missing amount limit"
    scope_id = runner._blocker_id("ART-001", scope_blocker)
    amount_id = runner._blocker_id("ART-001", amount_blocker)
    transcripts = [
        _worker_output(
            "W1",
            "ESCALATE",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            f"{scope_blocker}|{amount_blocker}",
            "ESCALATE because release scope and amount limit are open.",
            blocker_type="SCOPE_MISMATCH|AMOUNT_LIMIT_MISSING",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            "",
            "ALLOW because W2 names both blocker ids.",
            blocker_resolution=f"{scope_id} closed by B16-20-SRC-03; {amount_id} closed by B16-20-SRC-03",
            structured_blocker_resolution=f"blocker_id={scope_id}; blocker_type=SCOPE_MISMATCH; sources=B16-20-SRC-03 || blocker_id={amount_id}; blocker_type=AMOUNT_LIMIT_MISSING; sources=B16-20-SRC-03",
        ),
        _worker_output(
            "W3",
            "ALLOW",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            "",
            "ALLOW because W3 repeats the false closure.",
            blocker_resolution=f"{scope_id} closed by B16-20-SRC-03; {amount_id} closed by B16-20-SRC-03",
            structured_blocker_resolution=f"blocker_id={scope_id}; blocker_type=SCOPE_MISMATCH; sources=B16-20-SRC-03 || blocker_id={amount_id}; blocker_type=AMOUNT_LIMIT_MISSING; sources=B16-20-SRC-03",
        ),
    ]

    result = runner.run_blind_fixture(_b16_020_payload(), transcripts, str(tmp_path))

    assert result["final"] == {"verdict": "ESCALATE", "artifact_id": "ART-001"}
    artifacts = {item["artifact_id"]: item for item in result["artifacts"]}
    assert artifacts["ART-002"]["closure_validation_clean"] is False
    assert artifacts["ART-002"]["all_prior_blockers_source_closed"] is False
    assert result["selection"]["selected_artifact_id"] != "ART-002"


def test_v5_gov_routes_invalid_closure_forward(tmp_path):
    blocker_text = "missing amount limit"
    blocker_id = runner._blocker_id("ART-001", blocker_text)
    transcripts = [
        _worker_output(
            "W1",
            "ESCALATE",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            blocker_text,
            "ESCALATE because amount limit is open.",
            blocker_type="AMOUNT_LIMIT_MISSING",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            "",
            "ALLOW because W2 names the blocker id.",
            blocker_resolution=f"{blocker_id} closed by B16-20-SRC-03",
            structured_blocker_resolution=f"blocker_id={blocker_id}; blocker_type=AMOUNT_LIMIT_MISSING; sources=B16-20-SRC-03",
        ),
        _worker_output(
            "W3",
            "ESCALATE",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            blocker_text,
            "ESCALATE because Gov carried the invalid closure forward.",
            blocker_type="AMOUNT_LIMIT_MISSING",
        ),
    ]

    result = runner.run_blind_fixture(_b16_020_payload(), transcripts, str(tmp_path))
    w3_prompt = "\n".join(message["content"] for message in result["prompts"][4])

    assert blocker_id in w3_prompt
    assert "invalid_blocker_closure" in w3_prompt
    assert "do not accept textual blocker closure without matching source fields" in w3_prompt


def test_v5_accepts_allow_when_closure_source_matches_required_scope_and_limit(tmp_path):
    scope_blocker = "missing payment_release scope"
    amount_blocker = "missing amount limit"
    scope_id = runner._blocker_id("ART-001", scope_blocker)
    amount_id = runner._blocker_id("ART-001", amount_blocker)
    transcripts = [
        _worker_output(
            "W1",
            "ESCALATE",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            f"{scope_blocker}|{amount_blocker}",
            "ESCALATE because release scope and amount limit are open.",
            blocker_type="SCOPE_MISMATCH|AMOUNT_LIMIT_MISSING",
        ),
        _worker_output(
            "W2",
            "ALLOW",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            "",
            "ALLOW because the cited fields close both blockers.",
            blocker_resolution=f"{scope_id} closed by B16-20-SRC-03; {amount_id} closed by B16-20-SRC-03",
            structured_blocker_resolution=f"blocker_id={scope_id}; blocker_type=SCOPE_MISMATCH; sources=B16-20-SRC-03; scope_code=payment_release || blocker_id={amount_id}; blocker_type=AMOUNT_LIMIT_MISSING; sources=B16-20-SRC-03; limit=50000.00",
        ),
        _worker_output(
            "W3",
            "ALLOW",
            "B16-20-SRC-01|B16-20-SRC-03|B16-20-SRC-05",
            "",
            "ALLOW because W3 preserves the source-closed result.",
        ),
    ]

    result = runner.run_blind_fixture(
        _b16_020_payload(payment_scope="payment_release", limit="50000.00"),
        transcripts,
        str(tmp_path),
    )

    gates = {row["artifact_id"]: row["gate_result"] for row in result["worker_rows"]}
    assert gates["ART-002"]["passed"] is True
    assert len(gates["ART-002"]["resolved_prior_blockers"]) == 2
    assert result["final"] == {"verdict": "ALLOW", "artifact_id": "ART-002"}


def test_v5_marks_policy_underspecified_packet_as_packet_repair_not_win_or_loss():
    status = runner._packet_policy_status(_b16_001_payload())

    assert status["status"] == "SOURCE_POLICY_UNDERSPECIFIED"
    assert "approval or callback" in status["reason"]


def test_v5_worker_contract_requires_blocker_type_and_structured_resolution():
    identity = runner.worker_contract_identity()
    assert identity["worker_contract_version"] == "WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04"
    assert "blocker_type" in identity["required_worker_keys"]
    assert "structured_blocker_resolution" in identity["required_worker_keys"]

    parsed = runner._parse_key_value(
        "\n".join(
            [
                "worker_role=W1",
                "verification_verdict=ALLOW",
                "binding_class=SOURCE_BOUNDARY_CLOSED",
                "action_boundary=fixture",
                "cited_evidence=B16-20-SRC-01",
                "blocker_resolution=",
                "final_answer=ALLOW because this intentionally omits V5 closure fields.",
            ]
        )
    )

    gate = runner._gate_worker_output(_b16_020_payload(), parsed)

    assert "missing_blocker_type" in gate["failures"]
    assert "missing_structured_blocker_resolution" in gate["failures"]
