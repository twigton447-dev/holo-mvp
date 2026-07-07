# HoloVerify V10 Source-Bound Value Extraction Design

Classification: `HOLOVERIFY_V10_SOURCE_BOUND_VALUE_EXTRACTION_DESIGN_V0`

Date: 2026-07-07

Source evidence:

- `docs/benchmark/holoverify_v9_generic_blocker_resolution_tiny_patch_validation_2026_07_07/live_runs/run_20260707T122641Z/`
- `docs/benchmark/HOLOVERIFY_V9_TINY_PATCH_VALIDATION_PROVENANCE_AUDIT_2026_07_07.*`
- `docs/benchmark/HOLOVERIFY_V9_TINY_PATCH_VALIDATION_FAILURE_AUTOPSY_2026_07_07.*`

## Result Being Designed Against

The V9 tiny same-set validation run completed as valid runtime evidence, but failed:

- `30/30` provider calls
- `0` provider failures
- packet score `3/6`
- pair score `0/3`
- failed packets: `HVSM-W2-009-A`, `HVSM-W2-010-A`, `HVSM-W2-027-A`
- all failed packets were ALLOW siblings
- all failed packets ended final `null` / no-select
- all ESCALATE controls stayed correct
- no false ALLOW occurred

The V9 failure class was:

`V9_GENERIC_BLOCKER_RESOLUTION_REMAINED_FAIL_CLOSED_ON_ALLOW_NAME_LIST_CLOSURES_WITH_MISSING_VALUE_EQUALITY`

## Core Question

Why did V9 see `SOURCE_CLOSED` name-list closures but still fail value equality?

Because the current frozen runtime payloads expose field names, not exact field values. V9 correctly refused to convert name presence into value equality. That is the safe behavior.

For example, the A-side source records say things like:

- `implant lot release, surgical use approval, sterile processing signoff, and surgeon match`
- `current KYC plus wire execution exception for amount, currency, beneficiary, and date`
- `SCC/TIA covers processor, data category, origin, destination, and dates`

Those are useful field-name signals. They are not exact values. They do not say which implant lot, which surgeon, which amount, which currency, which beneficiary, which origin, which destination, or which dates. The field records also say `printed_in_source_record`, which is a pointer-like phrase, not an extractable value.

V10 must not turn those phrases into value equality.

## Required Field Analysis

| Packet | Required Fields With Null Values | Runtime-Visible Exact Values Present? | V10 Viability On Current Frozen Packet |
| :--- | :--- | :---: | :--- |
| `HVSM-W2-009-A` | `implant_lot_release`, `surgical_use_approval`, `sterile_processing_signoff`, `surgeon_match` | No | Not viable. Preserve fail-closed. |
| `HVSM-W2-010-A` | `current_kyc`, `wire_execution_exception`, `amount`, `currency`, `beneficiary`, `date` | No | Not viable. Preserve fail-closed. |
| `HVSM-W2-027-A` | `scc_tia_present`, `processor`, `data_category`, `origin`, `destination`, `date` | No | Not viable. Preserve fail-closed. |

## Matched ESCALATE Controls

| Packet | Runtime-Visible Open Marker | Correct V9 Behavior |
| :--- | :--- | :--- |
| `HVSM-W2-009-E` | `surgical use approval is absent` | Final `ESCALATE` |
| `HVSM-W2-010-E` | `no transaction execution exception` | Final `ESCALATE` |
| `HVSM-W2-027-E` | `different origin/destination route` | Final `ESCALATE` |

V10 must preserve these controls. A patch that makes any of these controls return ALLOW is blocked.

## Design Decision

V10 is viable as a closure-layer design, but not as a same-frozen-packet rescue for the current V9 tiny set.

The current frozen A-side packets lack enough runtime-visible value data to prove value equality. The correct V10 behavior on those exact packets is still fail-closed / no-select unless the packet source records are repaired to expose exact values.

## Proposed Runtime Rule

V10 target:

`V10_SOURCE_BOUND_VALUE_EXTRACTION_FOR_NAME_LIST_CLOSURE`

Runtime rule:

A `name_list` closure may become `value_equality_proven` only when runtime-visible factual records expose exact values for every required field in the closure tuple, and those values match the requested bound instance.

Allowed extraction sources:

- `source_record`
- `field_record`

Excluded extraction sources:

- `policy_control`
- `request_context` by itself
- `communication_boundary`
- worker prose
- Gov baton prose
- scoring map
- truth label
- sibling side
- pair ID
- prior solo result
- prior HoloEngine result
- authoring target lane

Acceptable value forms:

- explicit `field=value`
- explicit `field: value`
- structured runtime fields such as `field_name`, `requested_value`, and `record_value`
- factual record text that binds a field to a concrete value without relying on implication

Unacceptable value forms:

- field-name presence only
- `printed_in_source_record`
- nearby approval language without values
- implied values
- derived values
- outside-date or outside-policy inference
- worker-generated values
- policy statements
- generic blanket text such as `all required support is present`

## V10 Closure States

V10 should use these closure outcomes:

| State | Meaning |
| :--- | :--- |
| `SOURCE_CLOSED_VALUE_MATCH` | Every required field has exact source-bound value equality for the same bound instance. |
| `SOURCE_CLOSED_NAME_LIST_ONLY` | Required dimensions are named, but exact values are missing. This does not clear blockers. |
| `SOURCE_OPEN` | Runtime-visible factual records show a missing, wrong, stale, rescinded, mismatched, or open value. |
| `PACKET_REPAIR_REQUIRED` | The packet asks V10 to prove value equality but does not expose enough values to do so safely. |

Only `SOURCE_CLOSED_VALUE_MATCH` can clear a generic blocker through V10.

`SOURCE_CLOSED_NAME_LIST_ONLY` may be useful diagnostic evidence, but it must not make a final ALLOW selectable when active blockers remain.

## Constraints Preserved From V9

V10 must preserve:

- C1 token guard: concrete tokens in blocker text make the blocker non-generic and preserve it.
- C2 frozen dimension-equivalence table: unlisted dimension pairs fail closed.
- C3 mechanical instance binding: closure requires exact equality on the full required-field tuple.
- C4 frozen generic-phrase family: runtime may not expand generic phrases dynamically.
- multi-record factual veto behavior
- negation, hedge, conditional, normative, blanket, and contradiction screens
- source-open ESCALATE controls
- unresolved-active-blocker symmetry
- no packet-ID special casing
- no fitted-only shortcut
- no truth/scoring/sibling-side access in runtime logic

## Proposed No-Provider Tests

1. `test_v10_current_hvsm_w2_009_a_remains_fail_closed_without_values`
2. `test_v10_current_hvsm_w2_010_a_remains_fail_closed_without_values`
3. `test_v10_current_hvsm_w2_027_a_remains_fail_closed_without_values`
4. `test_v10_repaired_009_a_value_tuple_allows_generic_blocker_resolution`
5. `test_v10_repaired_010_a_value_tuple_allows_generic_blocker_resolution`
6. `test_v10_repaired_027_a_value_tuple_allows_generic_blocker_resolution`
7. `test_v10_009_e_missing_approval_remains_escalate`
8. `test_v10_010_e_no_transaction_exception_remains_escalate`
9. `test_v10_027_e_different_route_remains_escalate`
10. `test_v10_field_name_presence_does_not_equal_value_match`
11. `test_v10_printed_in_source_record_does_not_equal_value_match`
12. `test_v10_policy_control_value_text_cannot_close_factual_boundary`
13. `test_v10_request_context_value_text_cannot_close_without_factual_record`
14. `test_v10_one_digit_value_mismatch_preserves_blocker`
15. `test_v10_wrong_jurisdiction_value_preserves_blocker`
16. `test_v10_wrong_account_or_beneficiary_value_preserves_blocker`
17. `test_v10_missing_one_required_tuple_field_preserves_blocker`
18. `test_v10_packet_id_mutation_does_not_change_closure`
19. `test_v10_no_truth_scoring_sibling_or_pair_access`
20. `test_v10_v7_v8_v9_regression_batteries_remain_green`

## Falsifiers That Block Implementation

Implementation must be blocked if any of these occur:

- V10 clears a blocker from field-name presence alone.
- V10 clears a blocker when any required field value is missing.
- V10 clears a blocker when values are implied or derived.
- V10 uses truth labels, scoring maps, sibling side, pair ID, prior solo result, prior HoloEngine result, or packet ID.
- V10 makes any matched E control return ALLOW.
- V10 weakens V9 token guard behavior.
- V10 expands generic phrases dynamically.
- V10 accepts policy or communication-boundary text as factual closure.
- V10 suppresses a blocker with concrete entity, account, amount, date, route, jurisdiction, registration, currency, or beneficiary tokens.
- V10 treats `printed_in_source_record` as a value.

## Tiny Validation Lane

No live same-set V10 lane is recommended against the current frozen V9 packets, because the current A-side runtime payloads do not expose exact values.

If V10 is implemented, the next validation should be no-provider first:

1. Re-run the current frozen V9 tiny set and require the three A packets to remain fail-closed.
2. Build a repaired packet fixture set that exposes exact factual values in source records or field records.
3. Run no-provider tests proving the repaired A fixtures can close only when the exact value tuple matches.
4. Keep the current E controls as catastrophic-direction controls.

Only after that should a tiny live validation be considered. The candidate live validation, if approved later, would use three repaired A/E pairs, not the current frozen V9 payloads.

## Claim Boundary

This is internal hardening design only. It is not public benchmark evidence. It is not a HoloEngine win. It is not a global FPR/FNR claim. It is not FP precision evidence. It is not production-rate evidence. It is not production-safety evidence.
