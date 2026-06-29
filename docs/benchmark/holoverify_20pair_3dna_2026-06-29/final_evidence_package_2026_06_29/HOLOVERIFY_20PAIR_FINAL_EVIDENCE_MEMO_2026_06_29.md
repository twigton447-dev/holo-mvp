# HoloVerify 20-Pair Final Evidence Memo

On a frozen 40-packet action-boundary benchmark, HoloVerify's 3-DNA governed architecture solved 40/40 packets. Matching one-shot solo baselines using the same mini-model families completed 120/120 calls but produced only 6/120 KNEW/admissible outputs. Fourteen sibling pairs showed complete solo collapse across all six one-shot solo attempts while Holo solved both the hard-ALLOW and hard-ESCALATE siblings. The Holo run used about 2.06x the solo token budget and passed no-leakage checks.

| Metric | Value |
| --- | --- |
| Holo solved packets | 40/40 |
| valid sibling pairs | 20/20 |
| solo one-shot calls | 120/120 |
| solo KNEW/admissible | 6/120 |
| clean all-six-solo-fail pairs | 14 |
| mixed pairs | 6 |
| leakage scan | 240 prompt files, 0 forbidden hits |
| Holo tokens | 426002 |
| Solo tokens | 206839 |
| Holo/Solo token ratio | 2.06x |
| autopsy lock | `730c31344a7d38ab2feb3c4d7c4b38127794c295d021f7c5b02c3f9e059b99b6` |
| no-provider audit | PASS |

## Claim Boundaries

- Do not claim: Holo beats all models
- Do not claim: Holo is generally superior
- Do not claim: Holo solved safety
- Do not claim: solo models cannot do this universally
- Do not claim: internal Holo misses are standalone solo failures

## Evidence References

- `holo_live_results`: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T052822Z/live_results.json`
- `holo_trace`: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/live_runs/run_20260629T052822Z/TRACE_CALLS.jsonl`
- `frozen_holo_lock_summary`: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/frozen_complete_run_20260629T052822Z/LOCK_SUMMARY.md`
- `solo_results`: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/solo_one_shot_against_frozen_run_20260629T052822Z/run_20260629T060938Z/solo_one_shot_results.json`
- `solo_trace`: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/solo_one_shot_against_frozen_run_20260629T052822Z/run_20260629T060938Z/SOLO_ONE_SHOT_TRACE.jsonl`
- `solo_prompts`: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/solo_one_shot_against_frozen_run_20260629T052822Z/run_20260629T060938Z/prompts`
- `comparison_autopsy_no_leakage`: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/holoverify_20pair_3dna_2026-06-29/solo_one_shot_against_frozen_run_20260629T052822Z/run_20260629T060938Z/comparison_autopsy_no_leakage.json`
- `subset_package`: `HOLOVERIFY_14PAIR_CLEAN_SOLO_COLLAPSE_SUBSET_2026_06_29.json`
