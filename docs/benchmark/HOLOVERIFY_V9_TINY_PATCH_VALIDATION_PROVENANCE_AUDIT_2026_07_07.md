# HoloVerify V9 Tiny Patch Validation Provenance Audit

Classification: `VALID_RUNTIME_FAILED_INTERNAL_V9_TINY_VALIDATION_EVIDENCE`

Run folder: `docs/benchmark/holoverify_v9_generic_blocker_resolution_tiny_patch_validation_2026_07_07/live_runs/run_20260707T122641Z`

## Control Result

| Check | Result |
| :--- | :--- |
| Provider calls | `30/30` |
| Provider failures | `0` |
| Trace frozen before scoring | `true` |
| Scoring map loaded post-freeze only | `true` |
| Post-hoc score exists | `true` |
| Post-hoc score is trace-bound | `true` |
| Raw provider outputs | `30` |
| Prompt files | `30` |
| `TRACE_CALLS.jsonl` rows | `30` |
| `TRACE_PROVIDER_CALLS.jsonl` rows | `30` |
| Runtime firewall | `failed` because final verdicts were not valid on the null/no-select ALLOW packets |
| Content contract failures | `0` |

## Score

| Metric | Result |
| :--- | :--- |
| Packet score | `3/6` |
| Pair score | `0/3` |
| Failed packets | `HVSM-W2-009-A`, `HVSM-W2-010-A`, `HVSM-W2-027-A` |
| Failed packet side | All `ALLOW` siblings |
| Failed verdict shape | All final `null` / no-select |
| ESCALATE controls | All correct |
| False ALLOW count | `0` |
| V9 tiny validation pass | `false` |

## Trace Binding

| Artifact | SHA-256 |
| :--- | :--- |
| `TRACE_CALLS.jsonl` | `6c2db3edfa3245f3ff9f02468f19c69db82d51964b3f1c93bf07913843f504c7` |
| `TRACE_PROVIDER_CALLS.jsonl` | `893ec17c72c76db48e27906335d792b8eca5736ea2db1360b96bc60ef929bd7a` |
| `blind_canary_live_summary.json` | `30011ddfd98808448534a57be813d3aa34650440c6d7eedc4dd60a109caf1efa` |
| `blind_canary_runtime_results.json` | `00b289a5bf389249aa9e485f34d325dfdfaa837f28169650ab832e6c8de5aecf` |
| `v9_generic_blocker_resolution_tiny_patch_validation_live_summary.json` | `4ce7ed3bc360b9767371155fef972e368773192452e7545f6638db74ca7664e5` |
| `v9_generic_blocker_resolution_tiny_patch_validation_posthoc_score_trace_bound_v0.json` | `101a42304d3a8cca1cf64588d8833e05ffd8cfa850c329e3a6e128cc73f7d041` |

## Classification

This is a valid completed runtime and a failed internal V9 tiny same-set validation result. It is not a provider failure, not a transport failure, and not a content-contract invalid run.

## Claim Boundary

Failed internal V9 tiny same-set validation evidence only. Not public benchmark evidence. Not a Holo win. Not global FPR/FNR. Not FP precision. Not production-rate evidence. Not production-safety evidence.
