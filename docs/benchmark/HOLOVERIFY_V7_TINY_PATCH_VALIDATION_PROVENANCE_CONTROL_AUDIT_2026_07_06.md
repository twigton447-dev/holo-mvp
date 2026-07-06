# HoloVerify V7 Tiny Patch Validation Provenance / Control Audit

Created: 2026-07-06

Lane: `HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_V0`

Run folder:
`docs/benchmark/holoverify_v7_false_blocker_suppression_tiny_patch_validation_2026_07_05/live_runs/run_20260706T192200Z`

## Classification

This is a valid completed live run and failed internal patch-validation evidence.

It is not a provider failure. It is not public benchmark evidence. It is not a Holo win. It is not a global FPR/FNR result. It is not FP precision evidence. It is not production safety evidence.

## Control Result

| Check | Result |
|---|---:|
| Expected provider calls | 30 |
| Observed provider calls | 30 |
| Provider failures | 0 |
| Raw provider output files | 30 |
| Trace frozen before scoring | true |
| Scoring map loaded after trace hash binding | true |
| Mixed registration JSON before trace freeze | false |
| Post-hoc scoring only | true |
| Packet score | 4/6 |
| Pair score | 1/3 |
| Result classification | `V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_FAILED` |

## Trace Binding

| Artifact | SHA-256 |
|---|---|
| `TRACE_CALLS.jsonl` | `aed8cd38a0a4813da73f5f5a4133814520a1a05fb0c03b39296c7b18aaac3edd` |
| `TRACE_PROVIDER_CALLS.jsonl` | `b5504493ce067bf2e9b340ea2d514bfa7f665acd03320ef723c13e1f7f79d4d8` |
| `blind_canary_live_summary.json` | `0aaba1496a22f61044b9163233391bb8585be93584c28a6d525d9a401a3d9313` |
| `v7_false_blocker_suppression_tiny_patch_validation_live_summary.json` | `298f0953c4c74a7124f69ee99fe3b10304d341fdd0d8d004d5ee0ddb4d159b15` |
| `blind_canary_runtime_results.json` | `1a00c2160bb7824431f81ed2c447c4058717a6930f7e258e975a96e8e6a73c0e` |
| `v7_false_blocker_suppression_tiny_patch_validation_posthoc_score_trace_bound_v0.json` | `8f784677d12818cfd4ec89e667a4548296d8c3b1c0814875e52f829f29af11a9` |
| Post-hoc scoring map | `d373168a818b5337855970a84217f7caf98e8c1f666dfa409ba4c78edc7a69bb` |

## Score Summary

Passed pair:

- `HVSM-W1-009`

Failed packets:

- `HVSM-W1-011-A`: truth `ALLOW`, final verdict `null`
- `HVSM-W1-019-A`: truth `ALLOW`, final verdict `null`

Protected ESCALATE negative controls:

- `HVSM-W1-009-E`: final verdict `ESCALATE`
- `HVSM-W1-011-E`: final verdict `ESCALATE`
- `HVSM-W1-019-E`: final verdict `ESCALATE`

## Evidence Preservation

This audit did not rerun providers, Holo live, solo live, Gov live, judges, or substitutions. The frozen run folder was inspected read-only. Raw provider outputs, traces, live summaries, runtime results, and post-hoc score artifacts remain preserved as generated.
