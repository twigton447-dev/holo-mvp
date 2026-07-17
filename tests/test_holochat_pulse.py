from holochat_pulse import HoloVerifyPulseGate, PulseDisposition, PulseSignal
from holochat_scope import AccessContext, ScopeKind


def _personal(principal="elliot"):
    return AccessContext(principal, "personal-elliot", ScopeKind.PERSONAL)


def _enterprise(principal="elliot"):
    return AccessContext(
        principal,
        "enterprise-meridian",
        ScopeKind.ENTERPRISE,
        tenant_id="meridian",
        membership_id="member-elliot",
    )


def test_holopulse_admits_only_minimized_allowlisted_signals():
    decision = HoloVerifyPulseGate().evaluate(
        PulseSignal("availability", "limited", _personal(), _enterprise())
    )

    assert decision.disposition is PulseDisposition.ALLOW
    assert decision.reason == "minimized_signal_admitted"
    assert decision.receipt["signal_type"] == "availability"
    assert "limited" not in decision.receipt.values()


def test_holoverify_blocks_injected_medical_detail_even_when_mislabeled():
    decision = HoloVerifyPulseGate().evaluate(
        PulseSignal(
            "availability",
            "limited",
            _personal(),
            _enterprise(),
            {"raw_context": "migraine medication changed; cannot tolerate screens"},
        )
    )

    assert decision.disposition is PulseDisposition.BLOCK
    assert decision.reason == "raw_or_sensitive_metadata_denied"


def test_holoverify_blocks_enterprise_client_detail_before_personal_admission():
    decision = HoloVerifyPulseGate().evaluate(
        PulseSignal(
            "client_update", "high", _enterprise(), _personal(),
            {"client_name": "confidential issuer"},
        )
    )

    assert decision.disposition is PulseDisposition.BLOCK
    assert decision.reason == "signal_type_not_allowlisted"


def test_holoverify_blocks_employee_exfiltration_disguised_as_pressure():
    decision = HoloVerifyPulseGate().evaluate(
        PulseSignal(
            "workload_pressure",
            "high",
            _enterprise(),
            _personal(),
            {"source_text": "Meridian bid committee approved an $84m ceiling"},
        )
    )

    assert decision.disposition is PulseDisposition.BLOCK
    assert decision.reason == "raw_or_sensitive_metadata_denied"
    assert "84m" not in decision.receipt.values()


def test_holoverify_blocks_cross_principal_bug():
    decision = HoloVerifyPulseGate().evaluate(
        PulseSignal("availability", "limited", _personal("elliot"), _enterprise("taylor"))
    )

    assert decision.disposition is PulseDisposition.BLOCK
    assert decision.reason == "different_principal"


def test_enterprise_pressure_can_reach_personal_without_work_details():
    decision = HoloVerifyPulseGate().evaluate(
        PulseSignal("workload_pressure", "high", _enterprise(), _personal())
    )

    assert decision.disposition is PulseDisposition.ALLOW
    assert decision.reason == "minimized_signal_admitted"
