# HoloVerify V5 Blocker Closure Validation Patch Report

Date: 2026-07-04

Status: `NO_PROVIDER_ACCEPTANCE_TESTS_PASS`

## Claim Boundary

No providers were run.

No Holo live run was run.

No solo run was run.

No judge was run.

This is patch-validation infrastructure only. It is not benchmark evidence and not public claim material.

## What Changed

V5 adds deterministic blocker-closure validation to the blind HoloVerify runner.

The system no longer accepts a later `ALLOW` merely because it names a `blocker_id` and cites source IDs. A closure must now pass source-field checks for the blocker type.

The patch adds:

- `blocker_type` on worker artifacts.
- `structured_blocker_resolution` on worker artifacts.
- Runtime-visible source-record parsing for `KEY|field=value` records.
- Deterministic closure validation for wrong transaction type, wrong action type, wrong scope, missing amount limit, add-on scope mismatch, callback-field mismatch, and under-specified packet policy.
- Invalid closure ledgers in the Gov baton.
- Selector hard gates for `closure_validation_clean` and `all_prior_blockers_source_closed`.

## Primary Fixtures

The clean V5 fixtures are:

- `HVSF-FACTORY16-010-B`
- `HVSF-FACTORY16-020-B`

Both are `FALSE_BLOCKER_CLOSURE_ACCEPTED` cases from the V4 small rescue autopsy.

## Test Results

Focused V5 acceptance tests:

```text
python3 -m pytest tests/test_holoverify_v5_blocker_closure_validation.py -q
.........                                                                [100%]
9 passed in 0.06s
```

Nearby selector regression tests:

```text
python3 -m pytest tests/test_holoverify_blind_selector_repair_regression.py -q
................                                                         [100%]
16 passed in 0.07s
```

Nearby wrapper/preflight contract tests:

```text
python3 -m pytest tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_120_live_wrapper.py tests/test_holoverify_atlas_holo_rescue_patch_validation_gate.py -q
.....................................                                    [100%]
37 passed in 0.99s
```

Compile check:

```text
python3 -m py_compile holoverify_blind_runner_v0.py docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py docs/benchmark/run_holoverify_atlas_holo_rescue_live_2026_07_03.py
```

Passed.

## Acceptance Coverage

The new no-provider tests cover:

1. `test_v5_rejects_false_closure_wrong_transaction_type_b16_010`
2. `test_v5_rejects_false_closure_missing_amount_limit_b16_010`
3. `test_v5_rejects_false_closure_wrong_payment_release_scope_b16_020`
4. `test_v5_rejects_false_closure_missing_amount_limit_b16_020`
5. `test_v5_selector_blocks_allow_when_invalid_closure_exists`
6. `test_v5_gov_routes_invalid_closure_forward`
7. `test_v5_accepts_allow_when_closure_source_matches_required_scope_and_limit`
8. `test_v5_marks_policy_underspecified_packet_as_packet_repair_not_win_or_loss`
9. `test_v5_worker_contract_requires_blocker_type_and_structured_resolution`

## Readiness

V5 is ready for a small no-provider preflight package.

It is not yet ready for a live rerun until that preflight is built and explicitly approved.

