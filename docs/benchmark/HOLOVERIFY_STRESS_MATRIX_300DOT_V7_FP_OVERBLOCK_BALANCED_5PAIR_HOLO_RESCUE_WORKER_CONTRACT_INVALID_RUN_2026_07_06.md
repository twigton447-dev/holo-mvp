# HoloVerify 300-Dot Stress Matrix V7 Rescue Worker-Contract Invalid Run Operational Note

Created: 2026-07-07

Classification: `HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_WORKER_CONTRACT_INVALID_RUN`

Run folder:
`docs/benchmark/holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_2026_07_06/live_runs/run_20260707T002631Z`

## Status

This run is preserved as an invalid worker-contract/content-failure artifact.

It is not a valid Holo rescue result. It is not public benchmark evidence. It is not a global FPR/FNR claim. It is not production-rate evidence. It is not a Holo win or Holo loss.

Do not score this run. Do not rerun this exact interrupted attempt into a clean result.

## Attempted Lane

| Field | Value |
|---|---|
| Lane | `HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_V0` |
| Runtime manifest | `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json` |
| Runtime manifest SHA-256 | `9976a7cc767f2fd3162e95114dc9ac9991a520f50016f7927685bb53ad413550` |
| Selector | `SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05` |
| Selector SHA-256 | `f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d` |
| Worker contract | `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04` |
| Worker contract SHA-256 | `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37` |
| Expected provider calls | `50` |
| Observed provider calls | `21` |
| Live summary | `docs/benchmark/holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_2026_07_06/live_runs/run_20260707T002631Z/blind_canary_live_summary.json` |
| Live summary SHA-256 | `c176b582d740b474a79a40287d6f928831330b02d3f863ec3fb5013bf8583064` |

## Observed Runtime

| Check | Result |
|---|---:|
| Expected provider calls | 50 |
| Observed provider calls | 21 |
| Provider failures | 1 |
| Failed slot | `W1` |
| Provider / model | `xai / grok-3-mini` |
| Failure class | `worker output contract failure / content failure` |
| Failure tag | `W1_worker_contract_missing:cited_evidence` |
| `TRACE_PROVIDER_CALLS.jsonl` rows | 21 |
| Trace SHA-256 | `47615b4473cc0844359a85177ab2ba219996a0094a94d62273cbe6f9029cb80f` |
| Raw provider outputs | 21 |
| Runtime result file | **missing** |
| Post-hoc scoring | not run |
| Packet-level final verdicts | unavailable |
| Failed packets | none (no complete packets) |
| Holo result | none |

## Failure Notes

- Failure occurred on `call_number: 21`.
- Failed output reference: `raw_provider_outputs/021_W1.json`.
- Failure reason in live summary: `W1_worker_contract_missing:cited_evidence`.
- This is a worker-contract/content-failure and does not represent a valid adjudicative result.
- Trace remains in `run_20260707T002631Z` and is preserved with all partial artifacts unchanged.

## Claim Boundary

This is preserved as an invalid worker-contract run artifact only.

It does not claim model performance.
It does not claim valid rescue evidence.
It does not create public or benchmark-ready evidence.
It does not create global FPR/FNR evidence.
It does not support production-rate evidence.
