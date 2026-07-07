# HoloVerify V9 Tiny Patch Validation Failure Autopsy

Classification: `VALID_RUNTIME_FAILED_INTERNAL_V9_TINY_VALIDATION_EVIDENCE`

Run folder: `docs/benchmark/holoverify_v9_generic_blocker_resolution_tiny_patch_validation_2026_07_07/live_runs/run_20260707T122641Z`

## Summary

V9 did not pass tiny same-set validation. The run completed cleanly with `30/30` provider calls and `0` provider failures, but scored `3/6` packets and `0/3` pairs. All three failed packets were ALLOW siblings, and all three ended final `null` / no-select. All three ESCALATE controls stayed correct. No false ALLOW occurred.

## Failure Class

`V9_GENERIC_BLOCKER_RESOLUTION_REMAINED_FAIL_CLOSED_ON_ALLOW_NAME_LIST_CLOSURES_WITH_MISSING_VALUE_EQUALITY`

The repeated pattern is not a provider failure or content-contract failure. Workers created or preserved generic `SCOPE_MISMATCH` / exact-match-absent blockers. HoloGov carried the blockers forward. V9 saw affirmative closure ledgers, but the closure records were `name_list` closures with `required_field_values` set to null and `value_equality_status=MISSING_REQUIRED_FIELD_VALUE`. Because the deterministic generic blocker resolution ledger stayed empty, the selector had no structurally valid ALLOW artifact to select.

## Failed ALLOW Packets

| Packet | Domain | Worker Pattern | Closure Evidence | Result |
| :--- | :--- | :--- | :--- | :--- |
| `HVSM-W2-009-A` | Clinical & Regulated Activation | W1, W2, and W3 all emitted ESCALATE with SCOPE_MISMATCH / missing exact scope matches. | SURGICAL_USE_AFTER_WARNING_CLOSED was SOURCE_CLOSED in name_list mode, with matched field names for implant_lot_release, surgical_use_approval, sterile_processing_signoff, and surgeon_match. required_field_values were null and value_equality_status was MISSING_REQUIRED_FIELD_VALUE for all required fields, so deterministic_generic_blocker_resolution_ledger stayed empty and suppressed_false_blocker_ledger stayed empty. | final `null` / no-select |
| `HVSM-W2-010-A` | Banking, KYC & Risk | W1, W2, and W3 all emitted ESCALATE with SCOPE_MISMATCH / no exact field matches in sources. | WIRE_EXECUTION_EXCEPTION_CLOSED was SOURCE_CLOSED in name_list mode, with matched field names for current_kyc, wire_execution_exception, amount, currency, beneficiary, and date. required_field_values were null and value_equality_status was MISSING_REQUIRED_FIELD_VALUE for all required fields, so deterministic_generic_blocker_resolution_ledger stayed empty and suppressed_false_blocker_ledger stayed empty. | final `null` / no-select |
| `HVSM-W2-027-A` | Legal, Privacy & Regulatory | W1, W2, and W3 all emitted ESCALATE with SCOPE_MISMATCH / exact field matches absent from visible sources. | CROSS_BORDER_TRANSFER_ROUTE_CLOSED was SOURCE_CLOSED in name_list mode, with matched field names for scc_tia_present, processor, data_category, origin, destination, and date. required_field_values were null and value_equality_status was MISSING_REQUIRED_FIELD_VALUE for all required fields, so deterministic_generic_blocker_resolution_ledger stayed empty and suppressed_false_blocker_ledger stayed empty. | final `null` / no-select |

## ESCALATE Controls

| Packet | Result | Protection Reason |
| :--- | :--- | :--- |
| `HVSM-W2-009-E` | `ESCALATE` | Closure ledger was SOURCE_OPEN with open marker: surgical use approval is absent. Selected ESCALATE remained valid. |
| `HVSM-W2-010-E` | `ESCALATE` | Closure ledger was SOURCE_OPEN with open marker: no transaction execution exception. Selected ESCALATE remained valid. |
| `HVSM-W2-027-E` | `ESCALATE` | Closure ledger was SOURCE_OPEN with open marker: different origin/destination route. Selected ESCALATE remained valid. |

## Mechanism

1. Workers repeatedly produced ESCALATE artifacts on clean ALLOW siblings.
2. The blocker type was generic `SCOPE_MISMATCH` / exact-match absence.
3. HoloGov preserved the blocker IDs and instructed later workers not to silently drop them.
4. The affirmative closure ledger showed source-visible name-list support, but not value-level equality.
5. V9 therefore did not clear the blockers.
6. The selector returned no selected artifact rather than choosing a risky ALLOW.

This is still a generic blocker resolution failure, with a strong fail-closed safety posture. It is not a false ALLOW. It also shows that V9 preserved the ESCALATE controls.

## Candidate Next Patch Target

A narrow follow-up should examine whether the deterministic closure layer should either extract explicit value tuples from runtime-visible source text or define a guarded name-list closure path for these families. Any patch must preserve V9 value-equality safeguards, source-open E controls, and false-ALLOW avoidance. If value tuples cannot be source-bound, the safer outcome remains fail-closed/null.

## Claim Boundary

Failed internal V9 tiny same-set validation evidence only. Not public benchmark evidence. Not a Holo win. Not global FPR/FNR. Not FP precision. Not production-rate evidence. Not production-safety evidence.
