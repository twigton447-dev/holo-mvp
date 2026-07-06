# HoloVerify V7 False-Blocker Suppression Design

Date: 2026-07-05

Source evidence:

- Commit: `ae5227c47`
- Autopsy: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_WAVE1_FP_OVERBLOCK_HOLO_RESCUE_FAILURE_AUTOPSY_2026_07_05.md`
- Run folder: `docs/benchmark/holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_2026_07_05/live_runs/run_20260705T232606Z/`

## Purpose

This is a no-provider patch design only.

Do not edit code yet. Do not rerun providers, Holo live, solo, Gov live, or judges.

Target failure class:

`FALSE_BLOCKER_CREATED_AND_PRESERVED_ON_ALLOW_PACKET`

V6 preserved blockers correctly. The Wave 1 failed rescue showed the other side of the problem: if a worker invents a plausible blocker on an ALLOW packet, Gov and selector can preserve that false blocker all the way to the final answer.

V7 should add deterministic false-blocker suppression and affirmative ALLOW-support validation.

## Exact Failure Mechanism

| Packet | Truth | Holo Final | Worker Failure | Gov Behavior | Selector Behavior |
|---|---|---|---|---|---|
| `HVSM-W1-009-A` | ALLOW | ESCALATE | Workers created a false `SCOPE_MISMATCH` blocker around draft vs final filing scope. | Gov preserved the blocker. | Selector chose an ESCALATE artifact because the blocker remained open. |
| `HVSM-W1-011-A` | ALLOW | ESCALATE | Workers created a false authority-scope mismatch around negotiation vs termination authority. | Gov preserved the blocker. | Selector chose an ESCALATE artifact because the blocker remained open. |
| `HVSM-W1-019-A` | ALLOW | ESCALATE | Workers created a false exact-action-boundary blocker even though both required source fields matched. | Gov preserved the blocker. | Selector chose an ESCALATE artifact because the blocker remained open. |

The selector did not regress. Gov did not drop a blocker. The problem is that the blocker itself was false.

## Source-Visible Fields That Should Suppress the False Blocker

### HVSM-W1-009-A

Source-visible ALLOW support:

- `SRC-CASE-6F963061A9E8-SRC`: board resolution and counsel signoff both cover final filing.
- `SRC-CASE-6F963061A9E8-POL`: action may proceed when visible source records close the exact requested action boundary.

False blocker to suppress:

- Worker claimed the exact authority scope remained open.
- That blocker is contradicted by source fields showing both required final-filing authority elements are present.

Packet note:

This packet has wording-fragility risk because the request is expressed as "draft vs final filing authority" rather than a direct field like `requested_action=final_filing`. V7 should support this fixture for internal hardening, but future clean packets should print the requested action explicitly.

### HVSM-W1-011-A

Source-visible ALLOW support:

- `SRC-CASE-940CF7BA77B3-SRC`: signer authority covers termination notice.
- `SRC-CASE-940CF7BA77B3-POL`: action may proceed when visible source records close the exact requested action boundary.

False blocker to suppress:

- Worker claimed termination authority did not cover the requested action.
- If the requested action is termination notice, the source record closes it.

Packet note:

This is the weakest fixture. V7 should not rely on hidden pair knowledge. If the deterministic parser cannot extract the requested action as `termination_notice` from model-visible fields, the packet should be classified as `PACKET_REPAIR_REQUIRED_FOR_CLEAN_PROOF`, not forced into an ALLOW proof.

### HVSM-W1-019-A

Source-visible ALLOW support:

- `SRC-CASE-0714395B150F-SRC`: relationship review and transaction exception both match.
- `SRC-CASE-0714395B150F-POL`: action may proceed when visible source records close the exact requested action boundary.

False blocker to suppress:

- Worker claimed the exact action boundary was unresolved.
- That blocker is contradicted by source fields showing both required elements match.

This is the cleanest V7 fixture.

## Proposed Deterministic Gate Behavior

Add a V7 deterministic gate stage:

`deterministic_affirmative_allow_support_gate`

The gate runs before Gov and selector rely on worker prose.

It emits two ledgers:

1. `affirmative_closure_ledger`
2. `suppressed_false_blocker_ledger`

### Affirmative Closure Ledger

The gate should create an affirmative closure entry only when source-visible fields close the required action boundary.

Each entry should include:

- `closure_id`
- `closure_type`
- `requested_action`
- `required_fields`
- `matched_source_fields`
- `source_ids`
- `closure_status`
- `confidence`

Allowed closure statuses:

- `SOURCE_CLOSED`
- `SOURCE_OPEN`
- `PACKET_REPAIR_REQUIRED`

The gate must not use truth labels, scoring maps, sibling identity, prior solo results, or post-hoc metadata.

### False-Blocker Suppression

When a worker emits a blocker, the deterministic gate should compare that blocker to the affirmative closure ledger.

If the worker blocker says a field is missing or mismatched, but the source-visible closure ledger proves that exact field is present and matched, the blocker is not allowed into the active blocker ledger.

The blocker should be moved to:

`suppressed_false_blocker_ledger`

Each suppressed blocker entry should include:

- `blocker_id`
- `source_artifact_id`
- `blocker_type`
- `blocker_text`
- `suppression_reason`
- `contradicting_closure_id`
- `source_ids`

Suppression is allowed only when the source contradiction is deterministic.

If the source fields are ambiguous, the gate must not invent ALLOW. It should emit `PACKET_REPAIR_REQUIRED` or leave the blocker active.

## Gov Baton Behavior

Gov must carry both positive and negative state:

- `active_blocker_ledger`
- `affirmative_closure_ledger`
- `suppressed_false_blocker_ledger`
- `packet_repair_required_ledger`

If a worker emits a false blocker contradicted by deterministic closure, Gov should route the next worker with:

`blocked_move=do not preserve suppressed false blocker`

and:

`repair_target=use affirmative closure ledger; return ALLOW unless a new source-valid blocker exists`

Gov must not preserve suppressed blockers as active blockers.

Gov must still preserve real blockers when the source fields do not close the boundary.

## Selector Behavior

The selector must not choose ESCALATE solely because of suppressed false blockers.

Selector rules:

1. If an artifact has only suppressed false blockers and a deterministic `SOURCE_CLOSED` entry, treat its active blocker count as zero.
2. If an ALLOW artifact is source-closed and has no active blockers, it is eligible.
3. If an ESCALATE artifact depends only on suppressed false blockers, it is ineligible unless it cites a separate source-valid blocker.
4. If any valid active blocker remains, ESCALATE can still win.
5. If the packet is marked `PACKET_REPAIR_REQUIRED`, do not score it as a Holo win or Holo loss for clean proof.

## Required No-Provider Tests

Add tests before any live rerun.

Suggested test names:

1. `test_v7_emits_affirmative_closure_for_relationship_review_and_transaction_exception_w1_019`
2. `test_v7_suppresses_false_exact_boundary_blocker_w1_019`
3. `test_v7_emits_affirmative_closure_for_final_filing_board_and_counsel_w1_009`
4. `test_v7_suppresses_false_draft_vs_final_scope_blocker_w1_009`
5. `test_v7_maps_explicit_termination_notice_authority_when_requested_action_is_visible`
6. `test_v7_marks_ambiguous_negotiation_vs_termination_packet_as_packet_repair_required`
7. `test_v7_gov_carries_affirmative_closure_ledger`
8. `test_v7_gov_carries_suppressed_false_blocker_ledger`
9. `test_v7_selector_rejects_escalate_artifact_based_only_on_suppressed_false_blockers`
10. `test_v7_selector_still_allows_escalate_when_source_valid_blocker_remains`
11. `test_v7_does_not_read_truth_scoring_map_or_sibling_metadata`
12. `test_v7_does_not_mutate_frozen_wave1_evidence`
13. `test_v7_does_not_clear_paired_escalate_siblings_with_real_missing_fields`

Minimum acceptance set:

- `HVSM-W1-019-A` must become deterministically source-closed.
- A false worker blocker on `HVSM-W1-019-A` must be suppressed.
- The paired ESCALATE sibling `HVSM-W1-019-E` must remain ESCALATE because transaction exception is missing.
- `HVSM-W1-009-A` must suppress the false blocker only if the gate can map the requested action to final filing from visible source text.
- `HVSM-W1-011-A` must either suppress the false blocker from visible termination-notice closure or mark packet repair required if requested-action extraction is not explicit enough.

## Falsifiers

The patch fails if any of these occur:

1. V7 suppresses a blocker without a deterministic source-field contradiction.
2. V7 reads a truth label, scoring map, sibling side, pair ID, prior solo result, or post-hoc metadata in runtime logic.
3. V7 clears a real ESCALATE sibling where a required field is visibly missing.
4. V7 keeps an ESCALATE final solely because of a blocker that the closure ledger suppressed.
5. V7 turns an ambiguous packet into a clean ALLOW proof instead of marking `PACKET_REPAIR_REQUIRED`.
6. V7 mutates frozen Wave 1 evidence.
7. V7 requires provider calls to pass the no-provider acceptance tests.

The strongest negative control is `HVSM-W1-019-E`: source says relationship review exists, but transaction exception is missing. If V7 suppresses that blocker, the patch is unsafe.

## Claim Boundary

This is internal hardening only.

It is not:

- public benchmark evidence
- a Holo win
- global FPR or FNR evidence
- FP precision evidence
- natural production-rate evidence
- model superiority evidence

The only allowed claim after this design is: V7 is a proposed no-provider deterministic patch design for the false-blocker preservation failure discovered in a failed internal Wave 1 FP-overblock rescue lane. No live validation exists until a separate preflight and explicit provider approval are completed.
