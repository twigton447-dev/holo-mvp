# HoloVerify 300-Dot V7 FP-Overblock Balanced 5-Pair Holo Rescue Provenance Audit

Status: `PASS`

## Classification

Classification: `VALID_RUNTIME_FAILED_INTERNAL_RESCUE_EVIDENCE`

This is a valid completed live run and a valid post-hoc scored result for internal rescue validation only.

- Preserve as failed internal evidence.
- Do not treat as public benchmark evidence.
- Do not treat as a Holo win.
- Do not treat as global FPR/FNR evidence.
- Do not treat as production-rate evidence.

## Lane

- Lane: `HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_V0`
- Runtime manifest: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json`
- Runtime manifest SHA-256: `9976a7cc767f2fd3162e95114dc9ac9991a520f50016f7927685bb53ad413550`
- Selector: `SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05`
- Selector SHA-256: `f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d`
- Worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`
- Commit at run time: `f24ad85987d47e94fbc55adae1e1cf4c78ee1f50`

## Run Folder

- Run folder: `docs/benchmark/holoverify_stress_matrix_300dot_v7_fp_overblock_balanced_5pair_holo_rescue_2026_07_06/live_runs/run_20260707T012456Z`
- Provider calls: `50/50`
- Provider failures: `0`
- Worker/Gov split: `30 worker`, `20 gov`
- Provider roster: `xai=10`, `openai=10`, `minimax=30`
- Trace frozen before scoring: `true`
- Scoring map loaded post-freeze only: `true`
- Invalid content-contract packets: `0`
- Null/no-select packets: `0`
- Runtime firewall passed: `true`

## Trace Binding

- `TRACE_PROVIDER_CALLS.jsonl`: `15228b0b7a0353cd031793d6fab49ac20718e5b6eebc68e1b1433b609b7883f0`
- `TRACE_CALLS.jsonl`: `7bdf45fdb0f172999ee2b457d25fc688c6e5bd4e4c29a360bef5be20e51a79f3`
- `blind_canary_live_summary.json`: `af994a2164e8784d5259c99f2464da2d1694131d4ad737bf6824816074b8a523`
- `blind_canary_runtime_results.json`: `1859c4b8f648b40ac521c9c380136d622c443cf4eaf63e32457c38f7017d02f5`
- Post-hoc score JSON: `94eed0b302f175d676cd04aec44bb3c14745f3a2e49143e8546b9b90d97940a0`

## Score

- Result classification: `300DOT_V7_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_FAILED`
- Correct packets: `5/10`
- Incorrect packets: `5/10`
- Complete correct pairs: `0/5`
- Passed internal rescue: `false`

## Failure Family

- Failed packets are all ALLOW siblings.
- All matched ESCALATE controls are correct.
- Failure family: `V7 overblock on ALLOW packets`
- Likely next patch target: `V8 suppression of generic false SCOPE_MISMATCH / exact-match-absent blockers when source-visible ALLOW support exists`

## Separation From Earlier Invalid Attempts

This audit covers only `run_20260707T012456Z`.

- `run_20260707T001626Z` remains a transport-failure invalid artifact.
- `run_20260707T002631Z` remains a worker-contract invalid artifact.
- Those invalid attempts are not merged into this valid completed run.
