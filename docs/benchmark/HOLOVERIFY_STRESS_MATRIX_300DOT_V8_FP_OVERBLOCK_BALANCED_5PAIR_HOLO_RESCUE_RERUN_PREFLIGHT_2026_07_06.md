# HoloVerify 300-Dot V8 FP-Overblock Balanced 5-Pair Holo Rescue Rerun Preflight

Status: `PASS`

## Claim Boundary

Internal Holo/V8 rescue rerun only. Not public benchmark evidence. Not global FPR/FNR. Not production-rate evidence. Not FP precision evidence. Not a Holo win until measured.

## Selection Basis

Selected from observed 300-dot solo outcomes as pure FP-overblock all-three-collapse ALLOW cases, regardless of original authoring target lane; rerun under V8 after tiny validation passed.

## Selected Pairs

| Pair | Domain | ALLOW solo shape | ESCALATE control | Packets |
| :--- | :--- | :--- | :--- | :--- |
| `HVSM-W2-009` | Clinical & Regulated Activation | 3/3 FALSE_POSITIVE_ESCALATE_ON_ALLOW | 3/3 KNEW_ADMISSIBLE | `HVSM-W2-009-A, HVSM-W2-009-E` |
| `HVSM-W2-010` | Banking, KYC & Risk | 3/3 FALSE_POSITIVE_ESCALATE_ON_ALLOW | 3/3 KNEW_ADMISSIBLE | `HVSM-W2-010-A, HVSM-W2-010-E` |
| `HVSM-W2-020` | Operations, Insurance & Industrial | 3/3 FALSE_POSITIVE_ESCALATE_ON_ALLOW | 3/3 KNEW_ADMISSIBLE | `HVSM-W2-020-A, HVSM-W2-020-E` |
| `HVSM-W2-027` | Legal, Privacy & Regulatory | 3/3 FALSE_POSITIVE_ESCALATE_ON_ALLOW | 3/3 KNEW_ADMISSIBLE | `HVSM-W2-027-A, HVSM-W2-027-E` |
| `HVSM-W2-030` | Public Sector, Benefits & Grants | 3/3 FALSE_POSITIVE_ESCALATE_ON_ALLOW | 3/3 KNEW_ADMISSIBLE | `HVSM-W2-030-A, HVSM-W2-030-E` |

## Runtime Binding

- Runtime-only manifest: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json`
- Runtime manifest SHA-256: `5853f5d8257109199b4a98a18b11f8a9b339d5555093b8c1d89fccb89acd2f3c`
- Current head: `aee842b310073bbbd2a740daec76318fb481f231`
- Blind runner: `holoverify_blind_runner_v0.py`
- Blind runner SHA-256: `80c39e963a80058f00e430b3d0b985e5b2e545f22a6e4c51b9e30ea91882d822`
- Blind canary wrapper: `docs/benchmark/run_holoverify_blind_canary_live_2026_07_02.py`
- Blind canary wrapper SHA-256: `ca5af165ebf7cd04e625ec72de8f9cd2c7bff90437decf5482d9133f34e4fc63`
- Lane live wrapper: `docs/benchmark/run_holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_live_2026_07_06.py`
- Lane live wrapper SHA-256: `f772bb1164dc720e865dc1e4df8918669d31f749128ac9a0968895a81c3dd4d0`
- Post-hoc scoring map: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_scoring_map_2026_07_06.json`
- Post-hoc scoring map SHA-256: `bae892dad8398ed5ea18bfe0294d3c93e039ab1589bbe11c5f4384d370634f0b`
- Selector: `SELECTOR_V8_GENERIC_FALSE_BLOCKER_SUPPRESSION_2026_07_06`
- Selector SHA-256: `e23b2ec29c63c4d484c10b17ffd2b5d5f6251b10387458dc8c47125a1f642e45`
- Worker contract: `WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04`
- Worker contract SHA-256: `5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37`
- Expected route: `W1 -> G1 -> W2 -> G2 -> W3` per packet
- Expected provider calls: `50` total (`10` per slot)

## Runtime Hardening

- V8 generic false-blocker suppression is active.
- Content-contract hardening remains active at the blind runner boundary.
- A worker content-contract failure invalidates that packet, preserves evidence, skips remaining turns for that packet, and continues the runtime manifest.
- Invalid packets remain non-selectable and keep `selection.selected_artifact_id = None`.
- Runtime firewall pass requires zero `INVALID_CONTENT_CONTRACT` packets.
- Gov content-contract failures remain a follow-up scope note and are not covered by this refresh.

## Canonical No-Provider Preflight

- Folder: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/live_runs/preflight_20260707T042524Z`
- Lane preflight JSON: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/live_runs/preflight_20260707T042524Z/300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_preflight.json`
- Lane preflight JSON SHA-256: `91d089c3dcaf41c00b245a9d493762e5a7d138805e0b5e78625b5e0450059e2c`
- Blind canary preflight JSON: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/live_runs/preflight_20260707T042524Z/blind_canary_live_preflight.json`
- Blind canary preflight JSON SHA-256: `444faf4aed8c80672d40ab91f79924966aeec44611215d976278de1bf0acdc6c`
- Prompt-probe trace: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/live_runs/preflight_20260707T042524Z/preflight_prompt_probe/TRACE_CALLS.jsonl`
- Prompt-probe trace SHA-256: `e54bbac94d614d4f254cbfa2860910670187609c1ca420fb21e1899b72d2e41b`
- Prompt-probe results: `docs/benchmark/holoverify_stress_matrix_300dot_v8_fp_overblock_balanced_5pair_holo_rescue_rerun_2026_07_06/live_runs/preflight_20260707T042524Z/preflight_prompt_probe/blind_canary_runtime_results.json`
- Prompt-probe results SHA-256: `6a15e47bbb574d8ba85e89fd93d15c328ee96c89a32d8abe69739a0de81cd998`
- Prompt-probe calls: `50`
- Provider trace created: `False`
- Raw provider outputs created: `False`

## Pass Condition

- `50/50` provider calls and `0` provider failures.
- No substitutions, no scoring map before trace freeze, and post-hoc scoring only after trace hash binding.
- `10/10` packets and `5/5` pairs correct.
- All ALLOW siblings final `ALLOW`; all ESCALATE siblings final `ESCALATE`.
- No null/no-select final verdicts.

## Future Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_STRESS_MATRIX_300DOT_V8_FP_OVERBLOCK_BALANCED_5PAIR_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_06.json with SHA-256 5853f5d8257109199b4a98a18b11f8a9b339d5555093b8c1d89fccb89acd2f3c, selector SELECTOR_V8_GENERIC_FALSE_BLOCKER_SUPPRESSION_2026_07_06 hash e23b2ec29c63c4d484c10b17ffd2b5d5f6251b10387458dc8c47125a1f642e45, worker contract WORKER_CONTRACT_V4_BLOCKER_CLOSURE_VALIDATION_2026_07_04 hash 5606bf87e6757e9635ed0309bcab16364e91a3100ffda30db2003951daefdf37, and exactly 50 provider calls: W1 xai/grok-3-mini x10, G1 minimax/MiniMax-M2.5-highspeed x10, W2 openai/gpt-5.4-mini x10, G2 minimax/MiniMax-M2.5-highspeed x10, W3 minimax/MiniMax-M2.5-highspeed x10. INTERNAL HOLO/V8 RESCUE RERUN ONLY from the 300-dot stress baseline; not public benchmark evidence, not a global FPR/FNR claim, not production-rate evidence, not FP precision evidence, and not a Holo win until measured. Selected from observed 300-dot solo outcomes as pure FP-overblock all-three-collapse ALLOW cases, regardless of original authoring target lane; rerun under V8 after tiny validation passed. No solo, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```
