# HoloVerify V4 Blocker Preservation Small Rescue Live Rollup

Date: 2026-07-04

Status: `PRESERVED_PATCH_VALIDATION_DIAGNOSTIC_FAILURE`

Lane: `HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_PATCH_VALIDATION_V0`

Run directory:

`docs/benchmark/holoverify_v4_blocker_preservation_small_rescue_2026_07_04/live_runs/run_20260704T051943Z`

## Claim Boundary

This is patch validation only.

It is not benchmark evidence.

It is not public claim material.

It does not change the Batch016 score.

## Execution Integrity

- Expected provider calls: `25`
- Observed provider calls: `25`
- Provider failures: `0`
- Solo calls: `0`
- Judge calls: `0`
- Runtime manifest: `docs/benchmark/HOLOVERIFY_V4_BLOCKER_PRESERVATION_SMALL_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_04.json`
- Runtime manifest SHA-256: `4f8ec7a398b4b98be98695882ee90554884b2ffd939c6af2a1db41efc2553f60`
- Mixed registration JSON loaded before trace freeze: `false`
- Trace frozen before scoring: `true`

Selector:

`SELECTOR_V4_BLOCKER_PRESERVATION_2026_07_04`

Worker contract:

`WORKER_CONTRACT_V3_BLOCKER_PRESERVATION_2026_07_04`

## Result

Post-freeze score: `1/5`

Correct:

- `HVSF-FACTORY16-004-B`

Incorrect:

- `HVSF-FACTORY16-001-B`
- `HVSF-FACTORY16-008-B`
- `HVSF-FACTORY16-010-B`
- `HVSF-FACTORY16-020-B`

## What Happened

V4 did not produce a clean rescue.

It solved one case where workers kept the blocker alive:

- `HVSF-FACTORY16-004-B`: all three live worker artifacts were `ESCALATE`, and the selector selected `ESCALATE`.

It failed two cases because no worker surfaced a blocker in the live run:

- `HVSF-FACTORY16-001-B`: all three workers returned `ALLOW`.
- `HVSF-FACTORY16-008-B`: all three workers returned `ALLOW`.

It failed two cases because the later worker did not silently drop the blocker. It explicitly claimed to close it:

- `HVSF-FACTORY16-010-B`: W1 and W2 found blockers, but W3 returned `ALLOW` with `blocker_resolution` claiming the blockers were closed.
- `HVSF-FACTORY16-020-B`: W1 found a blocker, but W2 returned `ALLOW` with `blocker_resolution` claiming the blocker was closed.

That means V4 blocker preservation fixed the silent-drop shape, but it did not fix false blocker closure.

## Hardening Conclusion

The next architecture target is not just blocker preservation.

It is blocker-closure validation.

A later `ALLOW` should not be eligible merely because it names the old `blocker_id` and cites source IDs. Local code needs to verify that the cited evidence actually closes the exact blocker.

## Trace Hashes

| Artifact | SHA-256 |
| :--- | :--- |
| `TRACE_CALLS.jsonl` | `e71f712729a0d33e67c573665c04e8581819c1bebb28ab044e546866f5170735` |
| `TRACE_PROVIDER_CALLS.jsonl` | `915bd6c4e93e6253f5c70851160fe2ce09cabf46cdeee1ffaf3a24bcce1333e9` |
| `blind_canary_runtime_results.json` | `628c6a4bb9eb77ab79bb02f1035e0abbbea7fd43a9e9e50e446aa5641bc73a16` |
| `blind_canary_live_summary.json` | `769c7818c20fcd94ef0083df049954f2e9732f8692387b4d77c26fbf10559432` |
| `v4_blocker_preservation_small_rescue_live_summary.json` | `f633910463b7de3d279e3dd6492cd5f681e5eb036515b5b914a9b04d519ba3c1` |
| `solo_failure_factory_batch016_hard_authority_rescue_posthoc_score_trace_bound_v1.json` | `e51bba7b95d9415764cdbc86bc5cc11261d5973cd914841273be991d76abf486` |

## Preserved Preflights

- `docs/benchmark/holoverify_v4_blocker_preservation_small_rescue_2026_07_04/live_runs/preflight_20260704T051234Z`
- `docs/benchmark/holoverify_v4_blocker_preservation_small_rescue_2026_07_04/live_runs/preflight_20260704T051915Z`
