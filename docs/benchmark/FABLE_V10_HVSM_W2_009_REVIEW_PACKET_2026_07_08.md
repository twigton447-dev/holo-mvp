# Fable V10 HVSM-W2-009 Review Packet

Date: 2026-07-08
Owner: ++HoloOps++
Reviewer requested: Fable
Scope: no-provider implementation kill audit only

## Current Gate Status

Fable's audit result is accepted:

- verdict: `BLOCK_NEEDS_DIFF_REVIEW`
- visible-ref diagnosis: original Wave 2 / V9 tiny `HVSM-W2-009-A` is packet-schema insufficient and must remain fail-closed because it exposes field names without exact values
- clearance: blocked pending visible diff and updated no-provider regression evidence
- live rerun: blocked
- required next condition: make the patch reviewable and show the original Wave 2 009-A name-list-only packet still fails closed while the repaired V10 009-A value tuple can close

## Review Branch

Repo: `twigton447-dev/holo-mvp`
Local review path: `/Users/taylorwigton/Desktop/HoloEngine/holo-v10-fable-review-ap`
Review branch: `fable/v10-hvsm-w2-009-review-ap-20260708`
Base branch: `origin/codex/ap-publication-integration`

This review branch is intentionally not the broad recovery branch. It is a narrow branch on top of the visible AP publication/design branch, containing only the V10 correction surface and the small repaired-packet fixtures needed by the regression test.

## Audit Question

Autopsy `HVSM-W2-009` and determine whether the no-select/null verdict came from:

- packet schema
- V10 value-tuple closure
- selector behavior
- scorer extraction
- live-wrapper trace parsing

## Current HoloOps Finding

Root cause for the 07-07 repaired-packet-bank null verdict is the V10 surgical value-tuple closure path.

Important distinction:

- Original Wave 2 / V9 tiny 009-A is name-list-only. It lacks exact source-bound values and must remain fail-closed.
- Repaired V10 009-A exposes exact request/record `*_id` values. It may close only when exact value equality is proven.

The frozen runtime produced `PACKET_REPAIR_REQUIRED` for both 009 siblings, which made every artifact structurally invalid. The selector then correctly failed closed with:

- `packet_selectable=false`
- `final.artifact_id=null`
- `final.verdict=null`
- `selector_blocked_reason=no_structurally_valid_artifact`

The selector did not create the underlying failure; it enforced the structural-validity contract.

## Patch Boundary

Changed file:

- `holoverify_blind_runner_v0.py`

New test file:

- `tests/test_holoverify_v10_value_tuple_closure.py`

Patch behavior:

- adds surgical value aliases:
  - `implant_lot_release -> implant_lot_release_id`
  - `surgical_use_approval -> surgical_use_approval_id`
  - `sterile_processing_signoff -> sterile_processing_signoff_id`
  - `surgeon_match -> surgeon_id`
- preserves raw value tokens during alias extraction
- allows record-side concrete value support to satisfy an old name-list dimension
- requires exact value equality for the surgical 009 family before name-list support can clear
- classifies surgical value mismatch as `SOURCE_OPEN`
- keeps missing required tuple values as `PACKET_REPAIR_REQUIRED`
- keeps original Wave 2 009-A name-list-only support as `PACKET_REPAIR_REQUIRED`

This is not an alias-only patch. It is a narrow V10 surgical value-tuple closure patch.

## Decisive Local Check

Unpatched `HEAD` runner, using the repaired V10 runtime payloads:

- 009-A: `PACKET_REPAIR_REQUIRED`, `value_equality_status=NOT_CHECKED`
- 009-E: `PACKET_REPAIR_REQUIRED`, `value_equality_status=NOT_CHECKED`

Patched runner:

- repaired V10 009-A: `SOURCE_CLOSED`, `VALUE_EQUALITY_PROVEN`, final `ALLOW`
- repaired V10 009-E: `SOURCE_OPEN`, `VALUE_MISMATCH`, final `ESCALATE`
- repaired V10 009-A with missing required surgical value: still `PACKET_REPAIR_REQUIRED`
- original Wave 2 009-A name-list-only payload: `PACKET_REPAIR_REQUIRED`, `MISSING_REQUIRED_FIELD_VALUE`, final not `ALLOW`

## No-Provider Validation

Local test runtime:

- `.venv312`
- Python 3.12.13
- pytest 9.1.1

Focused branch gate:

```text
/Users/taylorwigton/Desktop/HoloEngine/holo-v10-recovery/.venv312/bin/python -m pytest \
  tests/test_holoverify_v10_value_tuple_closure.py
```

Focused branch result: `4 passed`.

Broader recovered-worktree gate:

```text
.venv312/bin/python -m pytest \
  tests/test_holoverify_v10_value_tuple_closure.py \
  tests/test_holoverify_v9_generic_blocker_resolution.py \
  tests/test_holoverify_v6_scope_dependency_gate.py \
  tests/test_holoverify_blind_selector_repair_regression.py \
  tests/test_holoverify_v5_blocker_closure_validation.py
```

Latest local result after Fable's block and the fail-closed guard: V10/V9/V8 focused gate `41 passed`; V6/selector/V5 gate `33 passed`.

Adjacent safety gate:

```text
.venv312/bin/python -m pytest \
  tests/test_holoverify_v7_false_blocker_suppression.py \
  tests/test_holoverify_v8_generic_false_blocker_suppression.py \
  tests/test_holoverify_blind_canary_live_wrapper.py \
  tests/test_holoverify_blind_120_live_wrapper.py \
  tests/test_holoverify_content_contract_failure_no_retry.py \
  tests/test_blind_lane_t4_selector_sweep.py
```

Adjacent safety gate after the fail-closed guard: `90 passed, 3 skipped`.

Bytecode compile check: `PASS`.

No providers were called for patch validation.

## Risk Boundary

False-ALLOW risk is the primary risk because the patch widens closure recognition. Current guardrails:

- matched 009-E control remains selectable `ESCALATE`
- mismatched surgical value becomes `SOURCE_OPEN`, not `SOURCE_CLOSED`
- missing surgical value remains `PACKET_REPAIR_REQUIRED`
- original Wave 2 009-A field-name/name-list support remains `PACKET_REPAIR_REQUIRED`
- V5/V6/V7/V8/V9 closure and selector regressions passed
- live rerun remains blocked

Reward-hacking risk remains moderate until Fable or another reviewer sees the actual diff. This packet does not create live evidence or public claim evidence.

## Request To Fable

Review the actual patch diff on `fable/v10-hvsm-w2-009-review-ap-20260708`. Do not review or bless the broad recovered branch. This branch contains only:

- `holoverify_blind_runner_v0.py`
- `tests/test_holoverify_v10_value_tuple_closure.py`
- V10 autopsy/review packet docs
- no secrets, `.env`, or unrelated recovered history

Answer:

1. Does the patch preserve fail-closed behavior for missing and mismatched surgical values?
2. Is any alias or raw-token extraction rule too broad?
3. Are the negative controls sufficient to block false-ALLOW?
4. Is the no-provider gate complete enough to proceed to preflight build?
5. If blocked, name the smallest code/test change required.

Return one of:

- `PASS_NO_PROVIDER_ONLY`
- `BLOCK_NEEDS_PATCH`
- `BLOCK_NEEDS_DIFF_REVIEW`

Live provider execution remains blocked either way until HoloOps issues a separate scoped approval request.
