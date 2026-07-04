# HoloVerify Blocker Preservation Patch Report

Date: 2026-07-04

Status: `NO_PROVIDER_PATCH_COMPLETE`

## Purpose

This patch hardens the HoloVerify blind runner after the Batch016 hard-authority Holo rescue run failed by silently losing source-grounded blockers between turns.

Batch016 produced a valid live run but poor rescue behavior:

- 28 packets completed.
- 18/28 final verdicts correct.
- 4/14 sibling pairs both siblings correct.
- All 10 misses were false negatives: truth `ESCALATE`, final `ALLOW`.
- In 6 misses, at least one worker found an `ESCALATE` blocker, but later selection/Gov did not preserve or explicitly resolve it.

This patch is not a benchmark result and does not repair or overwrite Batch016. It changes the runner contract for future runs only.

## Patch Identity

Selector policy:

- Version: `SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04`
- SHA-256: `3ed2a01eb16a8ea84bd096e6c1cfd352e6b0f8f9eb7565a5327680f77fa7affe`

Worker contract:

- Version: `WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04`
- SHA-256: `00b692a07b1036f70b0756e16458e811c7aee3afb62c1351893a4722aab9ad5a`

## What Changed

The runner now creates a source-grounded blocker ledger when a worker returns:

- `verification_verdict=ESCALATE`
- `binding_class=SOURCE_BOUNDARY_OPEN`
- a non-empty `open_blockers` field

Each blocker receives a deterministic `blocker_id` derived from the artifact ID and blocker text.

Later workers receive an `ACTIVE BLOCKER LEDGER` in the worker prompt. If a later worker returns `ALLOW`, it must explicitly close every active `blocker_id` in `blocker_resolution` and cite source IDs that support the closure.

Gov baton creation now prioritizes unresolved blockers before generic dependency repair or consensus handling.

The selector now ranks blocker preservation ahead of simple verdict consensus:

1. Structural validity.
2. Deterministic cleanliness.
3. Blocker-resolution cleanliness.
4. Complete blocker resolution.
5. Source-boundary-open artifact with blocker.
6. Verdict consensus and corroboration.

## New Fail-Closed Conditions

Future artifacts fail deterministic gates if they:

- Return `ALLOW` while active prior blockers remain unresolved.
- Mention prior blockers without citing source IDs in `blocker_resolution`.
- Try to drop a prior `SOURCE_BOUNDARY_OPEN` blocker silently.
- Return `ALLOW` while `open_blockers` is non-empty.
- Return `ESCALATE` without an `open_blockers` field.

## No-Provider Validation

No provider calls were run.

No judges were run.

No frozen packets, traces, raw outputs, or scoring maps were edited.

Validation performed:

- `python3 -m py_compile holoverify_blind_runner_v0.py docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py docs/benchmark/run_holoverify_blind_120_live_2026_07_03.py docs/benchmark/run_holoverify_atlas_holo_rescue_live_2026_07_03.py`
- `python3 -m pytest tests/test_holoverify_blind_selector_repair_regression.py tests/test_holoverify_blind_canary_live_wrapper.py tests/test_holoverify_blind_120_live_wrapper.py tests/test_holoverify_atlas_holo_rescue_patch_validation_gate.py`

Result:

- Py compile: `PASS`
- Focused pytest suite: `53 passed`

## Regression Cases Added

The selector regression suite now covers:

- A prior source-grounded blocker cannot be silently dropped by later `ALLOW`.
- A later `ALLOW` can win only when it names the prior blocker ID and cites source evidence.
- A final-turn new source-grounded blocker can defeat prior `ALLOW` consensus.
- Selector criteria and policy identity expose the new blocker-preservation fields.

## Claim Boundary

This patch means future Holo rescue runs can test whether blocker preservation improves the false-negative failure mode.

It does not mean:

- Batch016 is repaired.
- Holo has a new valid score.
- Any public denominator changes.
- The architecture is proven on harder seams.

Next valid move is a no-provider preflight of a fresh run lane using the V4 selector and V3 worker contract, followed by live execution only if explicitly approved.
