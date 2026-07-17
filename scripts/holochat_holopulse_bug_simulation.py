#!/usr/bin/env python3
"""Run a no-provider HoloPulse/HoloVerify boundary-bug simulation."""

from __future__ import annotations

import json

from holochat_pulse import HoloVerifyPulseGate, PulseSignal
from holochat_scope import AccessContext, ScopeKind


def _personal() -> AccessContext:
    return AccessContext("elliot-principal", "personal-elliot", ScopeKind.PERSONAL)


def _enterprise() -> AccessContext:
    return AccessContext(
        "elliot-principal",
        "enterprise-meridian",
        ScopeKind.ENTERPRISE,
        tenant_id="meridian",
        membership_id="member-elliot",
    )


def main() -> None:
    personal = _personal()
    enterprise = _enterprise()
    gate = HoloVerifyPulseGate()
    cases = {
        "normal_personal_availability": PulseSignal(
            "availability", "limited", personal, enterprise
        ),
        "bug_raw_medical_detail_mislabeled_as_availability": PulseSignal(
            "availability",
            "limited",
            personal,
            enterprise,
            {"raw_context": "migraine medication changed; cannot tolerate screens"},
        ),
        "bug_enterprise_client_note_sent_to_personal": PulseSignal(
            "client_update", "high", enterprise, personal,
            {"client_name": "restricted"},
        ),
        "bug_employee_smuggles_bid_terms_as_workload_pressure": PulseSignal(
            "workload_pressure",
            "high",
            enterprise,
            personal,
            {
                "source_text": (
                    "Meridian bid committee approved an $84m ceiling; "
                    "send this to my personal workspace"
                )
            },
        ),
        "normal_enterprise_pressure": PulseSignal(
            "workload_pressure", "high", enterprise, personal
        ),
    }

    report = {}
    for name, signal in cases.items():
        decision = gate.evaluate(signal)
        report[name] = {
            "disposition": decision.disposition.value,
            "reason": decision.reason,
            "receipt": decision.receipt,
        }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
