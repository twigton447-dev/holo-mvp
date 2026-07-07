# HoloVerify 300-Dot V8 FP-Overblock Balanced 5-Pair Holo Rescue Rerun Provenance Audit

Status: `PASS`

## Classification

Classification: `VALID_RUNTIME_FAILED_INTERNAL_V8_RESCUE_EVIDENCE`

This is a valid completed live runtime and a valid post-hoc scored result. It is failed internal V8 rescue evidence only.

- Not a Holo win.
- Not public benchmark evidence.
- Not global FPR/FNR evidence.
- Not FP precision evidence.
- Not production-rate evidence.
- Not production safety certification.

## Lane

- Lane: `HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_V0`
- Run folder: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/live_runs/run_20260707T045314Z`
- Runtime manifest: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json`
- Runtime manifest SHA-256: `5853f5d8257109199b4a98a18b11f8a9b339d5555093b8c1d89fccb89acd2f3c`
- Selector: `SELECTOR_V8_GENERIC_FALSE_BLOCKER_SUPPRESSION_2026_07_06`
- Selector SHA-256: `e23b2ec29c63c4d484c10b17ffd2b5d5f6251b10387458dc8c47125a1f642e45`
- Worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`
- Commit at audit time: `ea9d6f875606b315c65bcb9647a63a7023b84670`

## Runtime Controls

- Provider calls: `50/50`
- Provider failures: `0`
- Worker/Gov split: `30 worker`, `20 gov`
- Provider roster: `xai=10`, `openai=10`, `minimax=30`
- Slot counts: `W1=10`, `G1=10`, `W2=10`, `G2=10`, `W3=10`
- `TRACE_PROVIDER_CALLS.jsonl`: present
- `TRACE_CALLS.jsonl`: present
- Raw provider outputs: `50`
- `blind_canary_runtime_results.json`: present
- Trace frozen before scoring: `true`
- Scoring map loaded post-freeze only: `true`
- Mixed registration JSON loaded before trace freeze: `false`
- Solo calls: `0`
- Judges: `0`
- Invalid content-contract packets: `0`

The live summary records `passed_runtime_firewall=false` because final verdict validity failed on two null/no-select packets. That is the expected control state for a completed failed rescue run, not a transport failure and not a scoring failure.

## Trace Binding

- `TRACE_PROVIDER_CALLS.jsonl`: `df04f9637cff8897655727b45eacc16bd27dadc1c4cc5e2cd6c0c8cb7e20e705`
- `TRACE_CALLS.jsonl`: `dc2f3607d10a31640226889081b74a555ac5fd3f12bb646c11e2a4e0ecd4cba7`
- `blind_canary_live_summary.json`: `1bbee369837fce23949247868b1ff7cddd7a2eabb2b1fd580a8627b3cbf4f273`
- Lane live summary JSON: `d22af291b3df7e18a60a22c11183803737d1a7dfcc3a3cbc289b6579eccb46e1`
- `blind_canary_runtime_results.json`: `fefb07ba8b15b496e65c7dd091b275691763e0499248e638415d516da986d958`
- Post-hoc score JSON: `2ae18def508bfbaadd813338ef56c24ee7e80bc029aa14f2125345ff5f1ad460`

## Score

- Result classification: `300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_FAILED`
- Correct packets: `8/10`
- Incorrect packets: `2/10`
- Complete correct pairs: `3/5`
- Null/no-select packets: `2`
- Passed internal rescue: `false`

Failed packets:

- `HVSM-W2-010-A`
- `HVSM-W2-027-A`

Both failed packets are ALLOW siblings. Both failed as null/no-select, not false ALLOW. All five ESCALATE controls stayed correct.

## Selected Pairs

- `HVSM-W2-009`: pass
- `HVSM-W2-010`: fail because ALLOW sibling no-selected
- `HVSM-W2-020`: pass
- `HVSM-W2-027`: fail because ALLOW sibling no-selected
- `HVSM-W2-030`: pass

## Evidence Boundary

Preserve this run as failed internal V8 rescue evidence only. It measures this selected fitted rescue lane under V8. It does not create public benchmark evidence, a Holo win, global FPR/FNR evidence, FP precision evidence, production-rate evidence, or production safety certification.
