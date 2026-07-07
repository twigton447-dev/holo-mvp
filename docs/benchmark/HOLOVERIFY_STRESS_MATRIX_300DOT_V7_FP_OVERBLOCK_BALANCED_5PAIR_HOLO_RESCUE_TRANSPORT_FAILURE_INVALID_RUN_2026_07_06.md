# HoloVerify 300-Dot Stress Matrix V7 Rescue Transport-Failure Operational Note

Created: 2026-07-07

Classification: `HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_TRANSPORT_FAILURE_INVALID_RUN`

Run folder:
`docs/benchmark/holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_2026_07_06/live_runs/run_20260707T001626Z`

## Status

This run is preserved as an invalid transport-failure artifact.

It is not a valid Holo rescue result. It is not public benchmark evidence. It is not a global FPR/FNR claim. It is not production-rate evidence. It is not a Holo win or Holo loss.

Do not score this run. Do not rerun this exact interrupted attempt into a clean result.

## Attempted Lane

| Field | Value |
|---|---|
| Lane | HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_V0 |
| Runtime manifest | `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json` |
| Runtime manifest SHA-256 | `9976a7cc767f2fd3162e95114dc9ac9991a520f50016f7927685bb53ad413550` |
| Selector | `SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05` |
| Selector SHA-256 | `f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d` |
| Worker contract | `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04` |
| Worker contract SHA-256 | `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37` |
| Expected provider calls | `50` |
| Observed provider calls | `1` |

## Observed Runtime

| Check | Result |
|---|---:|
| Expected provider calls | 50 |
| Observed provider calls | 1 |
| Provider failures | 1 |
| Failed slot | `W1` |
| Provider / model | `xai / grok-3-mini` |
| Failure class | `transient_network_error` |
| Error type | `URLError` |
| Error text | `nodename nor servname provided, or not known` |
| `TRACE_PROVIDER_CALLS.jsonl` rows | 1 |
| Raw provider outputs | 1 |
| Raw provider output ref | `raw_provider_outputs/001_W1.json` |
| Trace frozen before scoring | true |
| Runtime results artifact present | false |
| Post-hoc scoring run | false |

## Trace Binding

| Artifact | SHA-256 |
|---|---|
| `TRACE_PROVIDER_CALLS.jsonl` | `b85c27dc8cfe7ea478d974aa56b520478d6de4b8a696c8b54fd8239c4e73c251` |
| `blind_canary_live_summary.json` | `bdb7c2df1d59273ac6be65440a74d390de50341548906fb3ac3c8377909a9d45` |

## Failure Details

- The run failed before completing packet flow on the first observed call.
- Transport retries were attempted for the same call and exhausted as transient network failure.
- This is a transport failure during live execution, not a scoring or model-evidence quality failure.

## Claim Boundary

This is preserved as an invalid transport-failure artifact only.

It does not claim model performance.
It does not create public or benchmark-ready evidence.
It does not create global FPR/FNR evidence.
It does not support natural production-rate evidence.
It does not count as a Holo win or Holo loss.
