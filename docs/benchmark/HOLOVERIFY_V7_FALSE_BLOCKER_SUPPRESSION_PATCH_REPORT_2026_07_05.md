# HoloVerify V7 False-Blocker Suppression Patch Report

Date: 2026-07-05

Status: `PASS_NO_PROVIDER_PATCH_IMPLEMENTED_FABLE_ROUND5_PATCH_MORE_REPAIRED`

Patch target:

`V7_FALSE_BLOCKER_SUPPRESSION_AND_AFFIRMATIVE_CLOSURE_GATE`

## Scope

This was a no-provider implementation pass.

No providers were run. No Holo live run was performed. No solo calls were run. No Gov live lane was run. No judges were run. No staging, commit, or push was performed.

The patch uses only runtime-visible packet source fields during runtime logic. It does not read design docs, scoring maps, truth labels, sibling side, pair IDs, prior solo results, prior Holo results, or post-hoc metadata.

## Implemented Behavior

V7 adds deterministic affirmative source-closure checks for the Wave 1 false-overblock fixtures:

- `HVSM-W1-009-A`: final filing authority is source-closed when board resolution and counsel signoff both cover final filing.
- `HVSM-W1-011-A`: termination notice authority is source-closed when signer authority covers termination notice.
- `HVSM-W1-019-A`: relationship-review / transaction-exception authority is source-closed when both fields match.
- `HVSM-W1-019-E`: remains source-open when relationship review exists but transaction exception is missing.

The gate now emits:

- `affirmative_closure_ledger`
- `suppressed_false_blocker_ledger`
- `packet_repair_required_ledger`

If a worker creates an ESCALATE blocker that is contradicted by deterministic source-visible affirmative closure, the blocker is moved to `suppressed_false_blocker_ledger` and is not carried as an unresolved active blocker.

If source-visible closure is absent or incomplete, real blockers remain active. The negative control `HVSM-W1-019-E` remains ESCALATE.

## HoloArchitecture Blocker Repair

HoloArchitecture found an over-suppression defect in the first V7 implementation:

`_blocker_matches_affirmative_closure()` suppressed generic `SOURCE_BOUNDARY_OPEN` / `SCOPE_MISMATCH` blockers too broadly. A generic blocker type alone could be suppressed by an unrelated `SOURCE_CLOSED` affirmative closure.

Repair:

- generic blocker type alone is no longer sufficient for suppression
- suppression now requires field/action alignment through closure type, requested action, required fields, matched source fields, or clearly matching blocker text
- unrelated generic source-boundary blockers remain active

## Fable Blocker Repair

Fable found a remaining hard blocker after the HoloArchitecture repair:

The generic `exact action boundary not closed` exception was still unsafe because the affirmative closure library does not model every possible seam. A packet could have one modeled boundary closed while a real unmodeled blocker remained open.

Repair:

- removed the generic `_is_generic_exact_boundary_blocker` / `_only_one_closed_boundary` suppression path
- replaced shared-word suppression with structured dimension alignment
- blocker suppression now requires blocker asserted dimensions to be a subset of closure verified dimensions
- stale, expired, wrong-entity, wrong-scope, missing-role, missing-second-approval, and other unverified dimensions remain active
- closure classification is negation-hardened: source text with missing/not/no/stale/expired signals cannot become clean `SOURCE_CLOSED`
- closure/open conflicts classify as `PACKET_REPAIR_REQUIRED` or `SOURCE_OPEN`, not clean ALLOW support

## Fable Round-2 Patch-More Repair

Fable found that the round-1 repair still allowed false ALLOWs when blocker text used unrecognized paraphrases.

Repair:

- default inversion added: unknown blocker content preserves the blocker
- suppression is allowed only when the blocker asserts no dimensions outside the closure's verified dimensions
- residual/unaccounted blocker text blocks suppression
- paraphrases survive unless structurally accounted for by recognized dimensions
- negation handling now catches closure-looking text with same-doc negators such as `no delegation on file covers termination notice`
- live failed-run W1 phrasing is regression-tested from raw provider outputs

Important result:

- `HVSM-W1-009-A` and `HVSM-W1-019-A` live W1 blocker phrases remain suppressible because they are structurally accounted for.
- `HVSM-W1-011-A` live W1 blocker phrase remains active because it asserts an unaccounted `negotiation` action. Under Fable's default-inversion rule, that is the safer outcome.

## Fable Round-3 Patch-More Repair

Fable found two remaining false-ALLOW paths:

1. The closure library trusted closed phrases in non-factual docs.
2. Dimension-empty blockers could still suppress through source overlap alone.

Repair:

- `SOURCE_CLOSED` closure now derives only from factual docs: `source_record` and `field_record`
- `policy_control`, `request_context`, and `communication_boundary` docs cannot close a factual action boundary by themselves
- source-overlap fallback was removed from `_blocker_matches_affirmative_closure`
- dimension-empty/vague blockers survive, including `required closure missing`
- raw live W1 phrase recovery remains bounded: current patched behavior appears to recover 2 of the 3 failed Wave 1 packets, not 3 of 3, because `HVSM-W1-011-A`'s live phrase remains active

Gov baton state now carries:

- active blockers
- affirmative closures
- suppressed false blockers
- packet-repair-required state
- invalid closure state

The selector now rejects an ESCALATE artifact whose only support is a suppressed false blocker, and still allows ESCALATE when a source-valid active blocker remains.

## Fable Round-4 Patch-More Repair

Fable found that suppression itself was sound, but selection still had a turn-order asymmetry.

Failure shape:

1. The closure library could be fooled by a factual-looking `source_record` sentence that was actually normative or conditional.
2. Later workers could raise real active blockers that survived suppression.
3. Those later ESCALATE artifacts were structurally invalid because they contradicted the deterministic closure library.
4. The selector could still choose an earlier ALLOW artifact because that earlier artifact did not have to answer blockers raised later in the packet.

Repair:

- added packet-wide unresolved-active-blocker symmetry
- an ALLOW artifact from any turn is not selectable while any active, non-suppressed blocker raised anywhere in the packet remains unresolved
- suppressed false blockers do not count as active dissent
- real active blockers still make the packet fail closed even if the closure library misclassifies a source phrase as closed

This closes the A10/A10b class. The remaining irreducible case is a mis-closed packet where all workers unanimously ALLOW and no worker raises an active blocker.

## Fable Round-5 Patch-More Repair

Fable found the mirror image of the suppression default-inversion bug on the blocker-resolution side.

Failure shape:

1. A worker raises a real active blocker that survives suppression.
2. A later ALLOW artifact names the `blocker_id` and cites any runtime source record.
3. `_validate_blocker_closure()` had no branch for the blocker type, so the empty failure list returned `CLOSED`.
4. The blocker left `unresolved_blockers`, packet-wide symmetry saw no active dissent, and the selector could choose ALLOW.

Repair:

- `_validate_blocker_closure()` now fails closed for unsupported blocker types
- `SOURCE_BOUNDARY_OPEN` and other non-enumerated blocker types cannot be resolved by citation alone
- supported blocker types can close only dimensions their validator actually checks
- if a blocker asserts freshness, entity, authority, sanctions, missing-role, missing-second-approval, or any other unvalidated dimension, resolution returns `INVALID_CLOSURE`
- the suppression and resolution surfaces now share the same default direction: if code cannot affirmatively justify removing a blocker, the blocker remains active

This closes the blocker-resolution laundering class. The remaining irreducible case is a packet where no worker raises the real blocker.

## Efficacy Boundary

A contentless generic false blocker such as `exact action boundary not closed` on a clean packet is now intentionally unsuppressable. It blocks ALLOW and fails closed. That may create overblocks, but it prevents false ALLOW. This is the intended burden-on-ALLOW tradeoff.

No blocker leaves the packet unless its removal is affirmatively justified by something the validator actually checked.

## Files Changed

- `holoverify_blind_runner_v0.py`
- `tests/test_holoverify_v7_false_blocker_suppression.py`
- `tests/test_holoverify_blind_selector_repair_regression.py`
- `tests/test_holoverify_blind_canary_live_wrapper.py`
- `tests/test_holoverify_blind_120_live_wrapper.py`
- `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_DESIGN_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_DESIGN_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_PATCH_REPORT_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_PATCH_REPORT_2026_07_05.json`

## Selector And Contract Identity

Selector:

- version: `SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05`
- SHA-256: `f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d`

Worker contract:

- version: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`

## Tests Added

New focused no-provider tests cover:

- false blocker suppression on `HVSM-W1-009-A`
- false blocker suppression on `HVSM-W1-011-A`
- false blocker suppression on `HVSM-W1-019-A`
- CE1: negated closure text does not become `SOURCE_CLOSED` or final ALLOW
- CE2: modeled boundary closed plus unmodeled real defect remains blocked
- CE3: stale relationship-review blocker survives suppression
- CE4: one closed modeled boundary plus one open modeled boundary fails closed
- E-side controls for `HVSM-W1-009-E` and `HVSM-W1-011-E`
- structured-alignment regression proving unrelated closures do not suppress unrelated blockers
- A1 staleness paraphrase survives suppression
- A2 entity-mismatch paraphrase survives suppression
- A3 negation paraphrase does not close termination authority
- A4 scope-restriction paraphrase survives suppression
- property-style boundary-name plus unrecognized clause survives suppression
- raw failed-run W1 phrasing regression from preserved provider outputs
- policy-sentence non-closure
- dimension-empty `required closure missing` survival
- A6 ordering symmetry over one closed modeled boundary plus one open modeled boundary
- A10 normative source-record misclosure with worker dissent in both orderings
- A10b conditional source-record misclosure with worker dissent in both orderings
- rescue preservation for `HVSM-W1-009-A` and `HVSM-W1-019-A` when dissent is suppressed
- blocker-resolution laundering fails closed for a real `SOURCE_BOUNDARY_OPEN` sanctions blocker
- citation-only closure returns `INVALID_CLOSURE` for non-enumerated types and V7 suppression dimensions
- supported blocker types reject closure when the blocker asserts unvalidated dimensions
- unrelated generic source-boundary blocker preservation when a different closure is source-closed
- real blocker preservation on `HVSM-W1-019-E`
- Gov baton carry of affirmative and suppressed ledgers
- selector rejection of ESCALATE based only on suppressed blockers
- selector selection of ESCALATE when a source-valid blocker remains
- truth/scoring/prior-result isolation
- frozen Wave 1 evidence immutability

## Validation

Commands run:

```bash
python3 -m py_compile holoverify_blind_runner_v0.py tests/test_holoverify_v7_false_blocker_suppression.py tests/test_holoverify_blind_selector_repair_regression.py tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_120_live_wrapper.py
```

Result: `PASS`

```bash
python3 -m pytest tests/test_holoverify_v7_false_blocker_suppression.py tests/test_holoverify_blind_selector_repair_regression.py tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_120_live_wrapper.py
```

Result: `84 passed`

## Evidence Preservation

The V7 immutability test hashes the frozen Wave 1 failed rescue trace files and raw provider outputs before and after no-provider fixture execution. Hashes remained unchanged.

Frozen evidence preserved:

- `TRACE_CALLS.jsonl`
- `TRACE_PROVIDER_CALLS.jsonl`
- `blind_canary_runtime_results.json`
- selected raw provider output files from `run_20260705T232606Z`

## Claim Boundary

This is internal hardening only.

It is not:

- public benchmark evidence
- a Holo win
- a global FPR or FNR claim
- FP precision evidence
- natural production-rate evidence
- model superiority evidence
- production safety certification

Allowed status:

V7 has no-provider tests showing deterministic false-blocker suppression and affirmative closure behavior for the selected Wave 1 failure fixtures. Live validation would require a separate preflight and explicit provider approval.
