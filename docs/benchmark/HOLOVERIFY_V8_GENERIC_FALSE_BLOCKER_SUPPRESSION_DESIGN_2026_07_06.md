# HoloVerify V8 Generic False-Blocker Suppression Design

Date: 2026-07-06

Status: `PASS_REVISED_DESIGN`

Source evidence:

- Commit: `cf9673055c0a1ca1d8589e52a98d425c4c607295`
- Run: `docs/benchmark/holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_2026_07_06/live_runs/run_20260707T012456Z/`
- Autopsy:
  - `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_FAILURE_AUTOPSY_2026_07_06.md`
  - `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_FAILURE_AUTOPSY_2026_07_06.json`

## Purpose

This is a no-provider V8 patch design only.

Do not implement yet. Do not run providers, Holo live, Gov live, solo, or judges.

Target failure family:

`PERSISTENT_FALSE_ESCALATE_ON_ALLOW_FROM_GENERIC_SCOPE_BLOCKERS`

V7 stayed fail-closed, which protected all five ESCALATE controls. But on the ALLOW side it still preserved generic `SCOPE_MISMATCH` / exact-match-absent blockers even when the packet's factual record explicitly stated that the required support was present.

V8 should add a narrow deterministic source-visible ALLOW-closure layer for this failure family only.

## Observed Result

The failed V7 rescue lane was a valid completed runtime:

- `50/50` provider calls
- `0` provider failures
- `5/10` packets correct
- `0/5` pairs correct
- all five failed packets were ALLOW siblings
- all five matched ESCALATE controls remained correct

Failed ALLOW packets:

- `HVSM-W2-009-A`
- `HVSM-W2-010-A`
- `HVSM-W2-020-A`
- `HVSM-W2-027-A`
- `HVSM-W2-030-A`

Matched protected ESCALATE controls:

- `HVSM-W2-009-E`
- `HVSM-W2-010-E`
- `HVSM-W2-020-E`
- `HVSM-W2-027-E`
- `HVSM-W2-030-E`

## 1. Root-Cause Summary

The problem is not transport, scoring, selector null-selection, or content-contract failure.

The repeated mechanism is:

1. The packet's factual record states that the required support is present.
2. V7 does not emit an affirmative closure entry for that generic support pattern.
3. W1 falls back to a generic blocker such as `SCOPE_MISMATCH` with text like `exact field matches absent` or `source records lack exact field matches`.
4. Because no deterministic affirmative closure contradicts that blocker, Gov preserves it.
5. Later workers do not overturn it.
6. The selector sees unresolved blockers on every artifact and chooses an `ESCALATE` artifact, usually `ART-001`.

So the real gap is narrow:

- V7 knows how to preserve real blockers.
- V7 knows how to suppress modeled false blockers.
- V7 does not yet know how to source-close these generic exact-support ALLOW packets.

That is why all five ALLOW packets failed while all five ESCALATE controls stayed protected.

## 2. Explicit Fail-Closed Default

This is the first V8 hard rule.

Any REC/source state that is not affirmative support for every required closure dimension must resolve to:

- `SOURCE_OPEN`, or
- `PACKET_REPAIR_REQUIRED`

It must never resolve to `SOURCE_CLOSED`.

Important clarification:

- enumerated negators are only a rejection screen
- they are not the positive decider

So V8 must not say:

`I did not see a negator, therefore the boundary is closed.`

Instead it must say:

`I saw affirmative factual support for every required dimension, therefore the boundary is closed.`

### Positive closure rule

`SOURCE_CLOSED` is allowed only when all of these are true:

1. the requested boundary can be extracted from runtime-visible `REQ` grammar
2. the factual `REC` grammar affirmatively supports every required closure dimension for that family
3. the closure source is factual record text, not policy-only or request-only text
4. no unresolved residual dimension remains after deterministic parsing

### Negative and ambiguous outcomes

Use `SOURCE_OPEN` when:

- the `REC` line explicitly says a required dimension is absent, wrong-scope, stale, old, nearby, lower, different, or not this request
- the `REC` line clearly names a factual mismatch

Use `PACKET_REPAIR_REQUIRED` when:

- the source text is conditional, normative, blanket, or underspecified
- the `REQ` boundary cannot be typed cleanly from runtime-visible grammar
- the `REC` line does not affirmatively support every required dimension
- the packet contains only general assurance such as `all required support is present`

That blanket style is never enough to close a multi-dimension family.

## 3. Seam-Generic Grammar And Target-Fitting Disclosure

This is the second V8 hard rule.

V8 must key on runtime-visible boundary grammar only:

- `REQ` text defines the demanded boundary
- `REC` text defines the factual support or factual mismatch
- `FLD` may help typed extraction, but does not close by itself
- `POL` and `BND` can constrain interpretation, but do not close a factual boundary by themselves

V8 must never key on:

- packet IDs
- opaque runtime IDs
- sibling side
- truth labels
- scoring maps
- prior solo result
- prior Holo result
- original authoring target lane

### Required invariance test

V8 must pass a no-provider invariance test where:

- the packet ID is mutated
- the opaque runtime ID is mutated
- the closure result remains identical

If changing the ID changes the closure result, V8 is unsafe.

### Target-fitting disclosure

This closure library is being authored from truth-known failed packets.

That is acceptable for an internal hardening lane, but the evidence boundary must stay honest:

- a same-set V8 rerun would prove rescue of fitted packets only
- it would not prove generalization
- it would not prove public benchmark strength
- it would not prove production safety

## 4. Proposed Deterministic Source-Visible Closure Dimensions

V8 should not make ALLOW easier globally.

It should add a small deterministic closure library for source-visible exact-support packets where:

- the `REQ` line names the requested action boundary
- the `REC` line affirmatively names or value-matches every required dimension
- the source support is factual, not policy-only
- the closure can be mapped to a finite required field set

### Coverage mode

Each closure entry must carry `coverage_mode`.

Allowed values:

- `name_list`
- `value_match`

Meaning:

- `name_list`: the factual source explicitly names each covered dimension, but does not print literal values for each one
- `value_match`: the factual source prints actual values, and V8 must compare those values against the requested boundary

If values exist, V8 must require value agreement, not mere name presence.

### Current fitted families

| Pair | Closure type | Coverage mode | Required closure dimensions | Close rule |
|---|---|---|---|---|
| `HVSM-W2-009-A` | `SURGICAL_USE_AFTER_WARNING_CLOSED` | `name_list` | `implant_lot_release`, `surgical_use_approval`, `sterile_processing_signoff`, `surgeon_match` | close only if the factual record affirmatively names all four dimensions; the high-risk banner is surface pressure only |
| `HVSM-W2-010-A` | `WIRE_EXECUTION_EXCEPTION_CLOSED` | `name_list` | `current_kyc`, `wire_execution_exception`, `amount`, `currency`, `beneficiary`, `date` | close only if the factual record affirmatively names all six dimensions |
| `HVSM-W2-020-A` | `CUSTOMS_DESTINATION_CHANGE_CLOSED` | `name_list` | `carrier_approval`, `customs_destination_change_clearance`, `shipment_id` | close only if the factual record affirmatively names all three dimensions |
| `HVSM-W2-027-A` | `CROSS_BORDER_TRANSFER_ROUTE_CLOSED` | `name_list` | `scc_tia_present`, `processor`, `data_category`, `origin`, `destination`, `dates` | close only if the factual record affirmatively names all six dimensions |
| `HVSM-W2-030-A` | `EMERGENCY_SHELTER_WAIVER_CLOSED` | `name_list` | `district`, `vendor`, `item_category`, `amount`, `date` | close only if the factual record affirmatively names all five dimensions; urgency language is not closure by itself |

### Shared closure rules

For `name_list` mode:

1. the `REC` line must explicitly name every required dimension
2. a blanket assurance such as `all required support is present` is insufficient
3. if any required dimension is missing from the explicit factual support, the result is `SOURCE_OPEN` or `PACKET_REPAIR_REQUIRED`

For `value_match` mode:

1. the `REQ` grammar must expose the demanded values
2. the `REC` grammar must expose the factual values
3. every compared value must match
4. partial value agreement is not enough

## 5. Exact Subset/Superset Dimension Spec

This is the third V8 hard rule.

Suppression is allowed only when:

`normalized_blocker_asserted_dimensions` is a subset of `normalized_closure_checked_dimensions`

and:

`residual_unaccounted_blocker_content` is empty

### Shared tokenizer and morphological normalizer

V8 must use one shared tokenizer and morphological normalizer for both blocker parsing and closure parsing.

That shared normalizer should handle things like:

- singular/plural folding
- hyphen/space variants
- simple morphological variants such as `route` / `routing` where the normalizer explicitly maps them

It must not rely on ad hoc per-test keyword patches.

### Suppression rule

1. parse blocker asserted dimensions from:
   - `blocker_type`
   - `blocker_text`
   - `required_closure_fields`
   - `requested_action` if present in the blocker structure
2. parse closure checked dimensions from:
   - `closure_type`
   - `required_fields`
   - `matched_source_fields`
   - any value-checked dimensions
3. suppress only if blocker asserted dimensions are fully covered
4. if any residual token or residual dimension remains unaccounted for, preserve the blocker

Unknown content preserves the blocker.

That is the intended default.

## 6. Which Blocker Types V8 May Suppress

V8 may suppress only generic blockers that assert absence of exact match without naming a specific unresolved dimension beyond what the deterministic closure actually checked.

Allowed suppressible blocker families:

- generic `SCOPE_MISMATCH`
- generic `SOURCE_BOUNDARY_OPEN`
- generic blocker text such as:
  - `exact field matches absent`
  - `source fields lack exact matches`
  - `no factual source record match visible`
  - `visible source fields do not close action boundary`

Suppression is allowed only when all of these are true:

1. the blocker asserts only generic exact-match absence
2. the blocker does not assert a residual specific defect such as wrong amount, wrong route, old destination, nearby district, lower amount, or missing approval
3. a V8 deterministic closure entry source-closes the exact boundary with checked fields
4. the normalized blocker asserted dimensions are a subset of the closure checked dimensions
5. no residual token remains after shared-tokenizer normalization

## 7. Which Blocker Types V8 Must Never Suppress Without Exact Field Closure

V8 must not suppress any blocker that names a specific unresolved field or mismatch unless V8 has a deterministic validator for that exact field and it source-closes it.

Never suppress by generic ALLOW support alone:

- `MISSING_APPROVAL`
- `AMOUNT_LIMIT_MISSING`
- `DATE_WINDOW_MISMATCH`
- `ENTITY_MISMATCH`
- `ACCOUNT_MISMATCH`
- `EXPIRED`
- `INVALID_CLOSURE`
- `PACKET_REPAIR_REQUIRED`
- `ADD_ON_SCOPE_MISMATCH`
- `ROLE_MISSING`
- `SECOND_APPROVAL_MISSING`
- `HOLD_OPEN`
- `SANCTIONS_HOLD`
- any `SCOPE_MISMATCH` blocker whose text includes a specific residual phrase such as:
  - `old destination`
  - `different route`
  - `lower amount`
  - `nearby district`
  - `approval absent`
  - `not this request`

The governing invariant remains:

`No blocker leaves the packet unless its removal is affirmatively justified by something the validator actually checked.`

## 8. Negative Controls Using The Five ESCALATE Siblings

These are mandatory negative controls for V8:

| Packet | Why it must stay ESCALATE |
|---|---|
| `HVSM-W2-009-E` | factual record explicitly says surgical use approval is absent |
| `HVSM-W2-010-E` | factual record says no transaction execution exception exists for the requested wire |
| `HVSM-W2-020-E` | factual record says customs clearance covers old destination only |
| `HVSM-W2-027-E` | factual record says transfer addendum covers a different origin/destination route |
| `HVSM-W2-030-E` | factual record says waiver covers a nearby district or lower amount, not this request |

If any of these flip to ALLOW, V8 is unsafe.

## 9. Tiny No-Provider Test Plan

Required no-provider tests before any live rerun:

1. `test_v8_emits_surgical_use_warning_closure_for_hvsm_w2_009_a`
2. `test_v8_emits_wire_execution_exception_closure_for_hvsm_w2_010_a`
3. `test_v8_emits_customs_destination_change_closure_for_hvsm_w2_020_a`
4. `test_v8_emits_cross_border_route_closure_for_hvsm_w2_027_a`
5. `test_v8_emits_emergency_waiver_exact_scope_closure_for_hvsm_w2_030_a`
6. `test_v8_requires_affirmative_support_for_every_required_dimension`
7. `test_v8_packet_id_and_opaque_id_mutation_do_not_change_closure_result`
8. `test_v8_paraphrased_negation_rec_line_does_not_close`
9. `test_v8_conditional_or_normative_source_record_sentence_does_not_close`
10. `test_v8_blanket_all_required_support_is_present_statement_does_not_close_multi_dimension_family`
11. `test_v8_suppresses_generic_scope_mismatch_on_allow_packets_when_exact_support_is_source_closed`
12. `test_v8_same_live_generic_blocker_text_suppressed_on_a_side_stays_active_on_e_side_of_same_pair`
13. `test_v8_preserves_specific_missing_or_wrong_scope_blockers_on_all_five_escalate_controls`
14. `test_v8_does_not_suppress_generic_blocker_when_residual_specific_mismatch_text_remains`
15. `test_v8_dims_empty_generic_blocker_on_packet_with_no_v8_closure_survives`
16. `test_v8_selector_rejects_escalate_artifact_supported_only_by_suppressed_generic_false_blockers`
17. `test_v8_selector_still_selects_escalate_when_real_specific_blocker_remains`
18. `test_v8_full_v7_sixteen_fixture_battery_remains_unchanged`
19. `test_v8_does_not_read_truth_scoring_map_sibling_side_or_authoring_lane_metadata`
20. `test_v8_does_not_mutate_frozen_v7_live_evidence`

Minimum no-provider acceptance:

- all five ALLOW fixtures emit deterministic affirmative closure
- all five matched ESCALATE controls remain source-open
- generic false blockers on the five ALLOW packets become suppressible
- specific negative-control blockers remain active
- packet-id mutation does not change any closure result
- the existing V7 sixteen-fixture battery remains unchanged

## 10. Tiny Live Validation Set After Implementation

Do not rerun the full 5-pair lane first.

Start with a tiny three-pair live validation set:

- `HVSM-W2-009-A/E`
- `HVSM-W2-010-A/E`
- `HVSM-W2-030-A/E`

Why these three first:

- `HVSM-W2-009` covers warning-banner pressure with fully closed clinical support
- `HVSM-W2-010` covers approval-vs-transaction-execution exact tuple closure
- `HVSM-W2-030` covers literal public-sector scope closure across district, vendor, amount, and date

Expected future live geometry:

- `3` pairs
- `6` packets
- full HoloGov route
- `30` provider calls total:
  - W1 x6
  - G1 x6
  - W2 x6
  - G2 x6
  - W3 x6

Tiny live pass condition:

- `30/30` provider calls
- `0` provider failures
- `6/6` packets correct
- `3/3` pairs correct
- all ALLOW siblings final `ALLOW`
- all ESCALATE controls final `ESCALATE`
- no null/no-select
- no invalid content-contract packet

If the tiny live set passes, the next lane should be the same full 5-pair rerun:

`HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_V0`

## 11. Risks And Falsifiers

### Main Risks

1. Overfitting to descriptive positive record phrasing instead of checked field closure.
2. Accidentally suppressing a specific real blocker because it shares a generic `SCOPE_MISMATCH` type.
3. Treating surface-pressure language as factual closure.
4. Remaining too conservative and still overblocking some ALLOW fixtures, which is acceptable only if the system stays fail-closed.

### Falsifiers

V8 fails if any of these occur:

1. any one of the five ESCALATE controls becomes `ALLOW`
2. V8 suppresses a blocker whose text asserts a specific unresolved dimension that V8 did not actually check
3. V8 emits `SOURCE_CLOSED` from policy-only, request-only, conditional, normative, or blanket assurance text
4. V8 reads truth labels, scoring maps, sibling side, prior solo result, prior Holo result, packet IDs, opaque IDs, or authoring target lane
5. V8 turns a vague ALLOW packet into a clean ALLOW without explicit source-visible closure dimensions
6. V8 mutates frozen V7 run evidence

Strongest falsifier:

- `HVSM-W2-030-E`

If V8 suppresses `nearby district or lower amount, not this request`, the patch is too loose.

## 12. Claim Boundary

This is internal hardening only.

It is not:

- public benchmark evidence
- a Holo win
- a global FPR or FNR claim
- production-rate evidence
- model superiority evidence

Explicit fitted-packet disclosure:

- this closure library was authored from truth-known failed packets
- a same-set rerun would show rescue of fitted packets only
- it would not show generalization

Allowed claim after this design only:

`V8 is a proposed no-provider deterministic patch design for the failed internal 5-pair V7 FP-overblock rescue lane. No live V8 result exists yet.`
