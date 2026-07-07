# HoloVerify V9 Generic Blocker Resolution Design

Date: 2026-07-06

Status: `PASS_DESIGN_NO_PROVIDER`

## Scope

This is a no-provider V9 patch design only.

Do not run providers, Holo live, Gov live, solo, or judges from this design. Do not stage, commit, or push this design unless separately approved.

Target failure family:

`V9_GENERIC_BLOCKER_RESOLUTION_FROM_DETERMINISTIC_AFFIRMATIVE_CLOSURE`

The goal is narrow: resolve generic exact-match / scope blockers only when deterministic source-visible affirmative closure already proves the same bound instance and same required dimensions.

The goal is not to make ALLOW easier globally.

## Evidence Used

Primary evidence:

- Valid failed V8 run: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/live_runs/run_20260707T045314Z`
- V8 provenance audit:
  - `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_PROVENANCE_AUDIT_2026_07_06.md`
  - `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_PROVENANCE_AUDIT_2026_07_06.json`
- V8 failure autopsy:
  - `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_FAILURE_AUTOPSY_2026_07_06.md`
  - `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_FAILURE_AUTOPSY_2026_07_06.json`

Known V8 selector:

- Version: `SELECTOR_V8_GENERIC_FALSE_BLOCKER_SUPPRESSION_2026_07_06`
- SHA-256: `e23b2ec29c63c4d484c10b17ffd2b5d5f6251b10387458dc8c47125a1f642e45`

Known V8 result:

- `50/50` provider calls
- `0` provider failures
- `8/10` packets correct
- `3/5` complete pairs correct
- failed packets: `HVSM-W2-010-A`, `HVSM-W2-027-A`
- both failed as null/no-select on clean ALLOW siblings
- all five ESCALATE controls stayed correct

## Root Cause

V8 did two important things correctly:

1. It recognized source-visible affirmative support for the fitted ALLOW packets.
2. It protected the ESCALATE controls.

But two ALLOW packets still failed closed because worker-created generic blockers remained structurally unresolved.

The failed shape is:

1. W1 creates a generic blocker such as `SCOPE_MISMATCH` with text like `exact field match not evidenced`.
2. V8 has a deterministic `SOURCE_CLOSED` affirmative closure for the packet.
3. A later worker tries to return `ALLOW`.
4. The selector refuses to select the ALLOW artifact because the worker's textual blocker closure does not satisfy the current closure parser.
5. The packet no-selects.

This is better than a false ALLOW. But it is still not a rescue.

## Comparison: Passing A Packets, Failed A Packets, E Controls

| Packet | Truth Side | V8 Final | What Happened |
| :--- | :--- | :--- | :--- |
| `HVSM-W2-009-A` | ALLOW | `ALLOW` | W1 raised generic `SCOPE_MISMATCH`; W2 resolved it with source IDs and `AFC-21CC1A827ED5`; W3 remained ALLOW. |
| `HVSM-W2-020-A` | ALLOW | `ALLOW` | W1 raised generic `SCOPE_MISMATCH`; W2 resolved it with source IDs and `AFC-3BFDD2CEFACD`; W3 remained ALLOW. |
| `HVSM-W2-030-A` | ALLOW | `ALLOW` | W1/W2/W3 all allowed; no generic blocker had to be repaired. |
| `HVSM-W2-010-A` | ALLOW | `null/no-select` | W1 and W2 raised generic `SCOPE_MISMATCH`; W3 tried to close both blockers using `AFC-711C3DE87B3D`, but no artifact became structurally selectable. |
| `HVSM-W2-027-A` | ALLOW | `null/no-select` | W1 raised generic `SCOPE_MISMATCH`; W2/W3 tried to close it, but blocker closure validation preserved an invalid closure state. |
| all five `E` packets | ESCALATE | `ESCALATE` | True blockers remained active and selectable as ESCALATE. |

The distinction is not that the failed A packets lacked affirmative closure. They had it.

The distinction is that V8 still depends too much on worker prose to translate that closure into a structurally valid blocker resolution.

## Exact Blocker Pattern

Failed A-side blocker forms:

- `HVSM-W2-010-A`
  - `ART-001-BLK-36023D92`
  - `ART-002-BLK-DE76FD14`
  - `blocker_type=SCOPE_MISMATCH`
  - blocker text: `exact field match not evidenced`
  - deterministic closure present: `AFC-711C3DE87B3D`
  - closure type: `WIRE_EXECUTION_EXCEPTION_CLOSED`
  - required fields: `current_kyc`, `wire_execution_exception`, `amount`, `currency`, `beneficiary`, `date`

- `HVSM-W2-027-A`
  - `ART-001-BLK-56EEB5D0`
  - `blocker_type=SCOPE_MISMATCH`
  - blocker text: `Exact scope match not confirmed`
  - deterministic closure present: `AFC-BD4D1027EED1`
  - closure type: `CROSS_BORDER_TRANSFER_ROUTE_CLOSED`
  - required fields: `scc_tia_present`, `processor`, `data_category`, `origin`, `destination`, `date`

Protected E-side blocker forms:

- `HVSM-W2-010-E`
  - blocker text: `no transaction execution exception`
  - this is not generic exact-match absence; it is a specific missing execution exception

- `HVSM-W2-027-E`
  - blocker text: `route mismatch in factual record`
  - this is a factual mismatch, not clean generic uncertainty

V9 must separate these two groups.

## Proposed V9 Behavior

Add a deterministic generic blocker resolver that runs from runtime-visible source fields and existing deterministic closure entries.

The resolver may mark a prior blocker resolved only when all of these are true:

1. The blocker is generic exact-match / exact-scope absence.
2. The blocker type is within the allowed generic family.
3. The blocker text has no residual unverified dimensions after normalization.
4. A deterministic affirmative closure exists with `closure_status=SOURCE_CLOSED`.
5. The closure binds to the same runtime-visible instance as the request.
6. The closure checked dimensions cover every dimension asserted by the blocker.
7. The closure required fields are satisfied from factual source records.
8. V8 veto screens did not mark the packet `SOURCE_OPEN` or `PACKET_REPAIR_REQUIRED`.
9. No deterministic dependency blocker or invalid closure remains for the same boundary.
10. No real specific blocker remains active.

If any condition fails, preserve the blocker.

## Where V9 Should Sit

Patch target order:

1. Deterministic gate / blocker resolver first.
2. Gov baton carry second.
3. Selector eligibility third.
4. Worker contract only if needed for trace readability.

The ideal behavior is that local deterministic code resolves generic blockers before the next worker has to guess how to phrase the closure.

In plain English:

The model should not have to invent the exact magic sentence that makes the selector trust a closure the deterministic layer already proved.

## Resolution Ledger

Add a structured V9 ledger:

`deterministic_generic_blocker_resolution_ledger`

Each entry should include:

- `blocker_id`
- `blocker_type`
- `blocker_text`
- `resolution_status`
- `resolution_source`
- `closure_id`
- `closure_type`
- `bound_instance`
- `blocker_dimensions`
- `closure_checked_dimensions`
- `matched_source_fields`
- `source_ids`
- `reason`

Allowed `resolution_status` values:

- `RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE`
- `UNRESOLVED_RESIDUAL_DIMENSION`
- `UNRESOLVED_NO_SOURCE_CLOSED_CLOSURE`
- `UNRESOLVED_WRONG_INSTANCE`
- `UNRESOLVED_WRONG_SCOPE`
- `UNRESOLVED_PACKET_REPAIR_REQUIRED`
- `UNRESOLVED_SPECIFIC_BLOCKER`

Only `RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE` removes a blocker from the active blocker path.

## Allowed Blocker Family

V9 may only resolve generic blocker patterns that mean:

- exact field match not evidenced
- exact field match missing
- exact source-field match not confirmed
- exact scope match not confirmed
- exact scope matches missing
- source fields lack exact matches
- source records lack exact action boundary match

After normalization, these blockers assert only generic dimensions such as:

- `exact_support_boundary`
- `source_field_match`
- `scope`
- `requested_action_boundary`

These can be resolved only when the closure checked dimensions include equivalent coverage plus the family-specific required fields.

## Blockers V9 Must Not Resolve

V9 must never resolve the following without exact source-field closure:

- missing approval
- missing transaction execution exception
- route mismatch
- customs destination mismatch
- wrong account
- wrong entity
- stale review
- expired authority
- missing second approval
- wrong jurisdiction
- amount limit missing
- value mismatch
- any blocker with residual unrecognized content

Unknown blocker text preserves the blocker.

## Closure Rules Preserved From V8

V9 must keep the V8 safety rules intact:

- no truth labels
- no scoring maps
- no sibling side
- no pair ID
- no prior solo result
- no prior Holo result
- no packet-ID special casing
- no opaque-runtime-ID special casing
- no fitted-only shortcut
- no policy-only closure
- no request-only closure
- no `field_record`-only factual closure
- affirmative closure comes from a single bound factual `source_record`
- veto screens scan visible `request_context`, `source_record`, and `field_record`
- multi-record factual contradiction fails closed
- hedged, conditional, normative, blanket, underspecified, or negated source text fails closed
- ambiguity fails closed

False ALLOW is the catastrophic failure. V9 should prefer null/no-select over false ALLOW.

## Gov Baton Behavior

Gov must carry four separate states:

- active blockers
- deterministic generic blocker resolutions
- invalid closures
- packet repair required

If a generic blocker is resolved by deterministic affirmative closure, Gov should carry it in the resolved ledger, not the active blocker ledger.

If a blocker is unresolved for any reason, Gov must carry it forward as active.

## Selector Behavior

Selector must treat a V9 resolved generic blocker as closed only if the deterministic resolution ledger says:

`resolution_status=RESOLVED_BY_DETERMINISTIC_AFFIRMATIVE_CLOSURE`

Selector must still block ALLOW when:

- active blockers remain
- invalid closure remains
- packet repair is required
- deterministic closure is absent
- blocker has residual dimensions
- closure instance does not match
- closure dimension coverage is incomplete
- any E-side specific blocker remains active

## Proposed No-Provider Regression Tests

Add focused tests before implementation is considered live-ready:

1. `test_v9_resolves_hvsm_w2_010_a_generic_exact_field_blockers_from_affirmative_closure`
2. `test_v9_resolves_hvsm_w2_027_a_generic_exact_scope_blocker_from_affirmative_closure`
3. `test_v9_keeps_hvsm_w2_010_e_missing_transaction_exception_active`
4. `test_v9_keeps_hvsm_w2_027_e_route_mismatch_active`
5. `test_v9_preserves_all_five_escalate_controls`
6. `test_v9_preserves_v8_rescued_allow_packets_009_020_030`
7. `test_v9_does_not_accept_closure_id_as_cited_source_evidence`
8. `test_v9_resolved_closure_ids_are_allowed_only_in_resolution_ledger`
9. `test_v9_residual_blocker_dimension_preserves_blocker`
10. `test_v9_unknown_generic_paraphrase_preserves_blocker`
11. `test_v9_wrong_instance_closure_does_not_resolve_blocker`
12. `test_v9_wrong_scope_closure_does_not_resolve_blocker`
13. `test_v9_packet_repair_required_prevents_resolution`
14. `test_v9_multi_record_rescission_prevents_resolution`
15. `test_v9_field_record_veto_prevents_resolution`
16. `test_v9_request_context_negation_prevents_resolution`
17. `test_v9_no_truth_scoring_sibling_pair_or_prior_result_access`
18. `test_v9_packet_id_mutation_does_not_change_resolution`
19. `test_v9_opaque_runtime_id_mutation_does_not_change_resolution`
20. `test_v9_selector_blocks_allow_when_any_unresolved_specific_blocker_remains`

Full relevant regression suite should include:

- V9 tests
- V8 generic false-blocker tests
- V7 false-blocker tests
- V6 scope dependency tests
- V5 blocker closure tests
- selector repair regression tests
- blind canary wrapper tests
- blind-120 wrapper tests
- content-contract failure tests

## Proposed Tiny Post-Implementation Validation Lane

After no-provider implementation and audit, use a tiny same-set lane:

- `HVSM-W2-010-A/E`
- `HVSM-W2-027-A/E`
- `HVSM-W2-009-A/E`

Expected future geometry:

- 3 pairs
- 6 packets
- full route: `W1 -> G1 -> W2 -> G2 -> W3`
- 30 provider calls if later approved

Pass condition:

- `30/30` provider calls
- `0` provider failures
- trace frozen before scoring
- no substitutions
- no scoring map before trace freeze
- `6/6` packets correct
- `3/3` pairs correct
- `HVSM-W2-010-A` final `ALLOW`
- `HVSM-W2-027-A` final `ALLOW`
- all three ESCALATE controls final `ESCALATE`
- no null/no-select

If the tiny lane passes, the next separate step would be a full same-set five-pair V9 rerun. A tiny pass would not prove generalization.

## Implementation Falsifiers

Block implementation if any of these happen:

- Any E-side control becomes ALLOW.
- A real specific blocker is resolved by a generic closure.
- A blocker with residual unrecognized dimensions is resolved.
- A closure from a different instance resolves a blocker.
- A policy-only or request-only statement closes a factual boundary.
- A multi-record rescission or contradiction still resolves as closed.
- A closure ID in `cited_evidence` is treated as a source ID.
- Packet ID, opaque runtime ID, sibling side, truth, scoring map, prior solo result, or prior Holo result affects resolution.
- `HVSM-W2-010-A` or `HVSM-W2-027-A` still no-selects in no-provider replay despite deterministic `SOURCE_CLOSED` closure and no active specific blockers.

## Claim Boundary

This design is internal hardening only.

It is not:

- public benchmark evidence
- a Holo win
- global FPR/FNR evidence
- FP precision evidence
- production-rate evidence
- production safety certification

Even a future tiny live pass would be same-set internal validation only. It would not prove generalization.
