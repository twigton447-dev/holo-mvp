# HoloVerify Tier 3 FN Holo Rescue Accounting Correction - 2026-07-05

CALLSIGN: STATS SUBAGENT

## Scope

This is a no-provider accounting correction. No providers, Holo live run, solo run, judge run, staging, commit, push, or runtime evidence edit was performed by this audit.

Run folder verified from disk:

`docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z`

## Corrected Classification

`AUTHORIZED_RUNTIME_VALID_SELECTED_GATE_FAILED`

The Tier 3 FN Holo rescue live run was authorized, runtime-valid, and selected-gate failed. It is preserved failed internal rescue evidence.

## Correction To Prior Statement

The prior "no live run" statement is superseded. It was stale because it described the preflight/runtime-package state, where the preflight artifact records `holo_live_runs: 0` and `providers_run: 0`. That preflight statement did not account for the later authorized live run now present in `run_20260704T195236Z`.

The provenance audit records that Miner executed the live wrapper after the approval sentence and classifies the run provenance as `AUTHORIZED_LIVE_RUN`.

## Disk Verification

| Check | Verified Value | Status |
|---|---:|---|
| Expected provider calls | 70 | PASS |
| Observed provider calls | 70 | PASS |
| Raw provider output files | 70 | PASS |
| Provider failures | 0 | PASS |
| Worker calls | 42 | PASS |
| Gov calls | 28 | PASS |
| W1 calls | 14 | PASS |
| G1 calls | 14 | PASS |
| W2 calls | 14 | PASS |
| G2 calls | 14 | PASS |
| W3 calls | 14 | PASS |
| Solo calls | 0 | PASS |
| Judge calls | 0 | PASS |
| Runtime manifest hash | `d570c6f6d8f55d36da7401eb32f8c7531c58d7fdd71274addf917edef5646de5` | PASS |
| Trace frozen before scoring | `true` | PASS |
| Scoring map loaded post-freeze | `true` | PASS |
| Packet score | 12/14 | PASS |
| Pair score | 5/7 | PASS |

## Failed Packets

| Packet | Pair | Truth | Holo Final Verdict | Failure Class |
|---|---|---|---|---|
| `HVSF-FACTORY16-008-B` | `HVSF-FACTORY16-008` | `ESCALATE` | `ALLOW` | `FN_FALSE_ALLOW` |
| `HVSF-FACTORY16-019-B` | `HVSF-FACTORY16-019` | `ESCALATE` | `ALLOW` | `FN_FALSE_ALLOW` |

## Claim Boundary

Allowed internal language:

Tier 3 FN Holo rescue was an authorized full-HoloGov run with valid runtime controls and failed the selected rescue gate: 12/14 packets and 5/7 pairs correct.

Forbidden language:

- Do not call this a Holo win.
- Do not call this public benchmark evidence.
- Do not use it as a global FNR claim.
- Do not use it as FP precision evidence.
- Do not merge it into the strict public denominator.
- Do not describe the selected-gate failure as a provider/control failure.

## Commit Readiness

PASS for committing the failed live evidence plus provenance/accounting correction, provided the commit preserves the failed-live status and claim boundary. This should be committed only as internal failed rescue evidence with provenance, not as a win or public benchmark result.

## Source Map

- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_PREFLIGHT_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_PROVENANCE_AUDIT_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_LIVE_ROLLUP_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z/blind_canary_live_summary.json`
- `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z/tier3_fn_holo_rescue_live_summary.json`
- `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z/tier3_fn_holo_rescue_posthoc_score_trace_bound_v1.json`
- `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z/TRACE_CALLS.jsonl`
- `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z/TRACE_PROVIDER_CALLS.jsonl`
- `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z/raw_provider_outputs/`
