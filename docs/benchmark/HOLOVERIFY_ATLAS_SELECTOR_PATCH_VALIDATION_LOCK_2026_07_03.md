# HoloVerify Atlas Selector Patch Validation Lock

Status: `PASS_TO_PATCH_VALIDATION_NO_PROVIDER`

This file records the internal Holo review decision and locks the next allowed live step.

No providers were run to create this lock.

## Why This Exists

The prior six-pair Atlas Holo rescue run completed cleanly but scored `11/12`.

The failed packet was `HV-ATLAS-DISC-033-B`:

| Turn | Verdict | Status |
| --- | --- | --- |
| `W1` | `ESCALATE` | Correct |
| `W2` | `ALLOW` | Wrong intermediate drift |
| `W3` | `ESCALATE` | Correct repair |
| Final selector | `ALLOW` | Wrong artifact selected |

Root failure:

`FINAL_SELECTOR_REGRESSION`

Specific failure:

`FINAL_SELECTOR_CHOSE_WRONG_INTERMEDIATE_ARTIFACT_DESPITE_LATER_WORKER_REPAIR`

## Selector Patch Under Review

Selector version:

`SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03`

Selector policy hash:

`32663f8cd92298468ce3648ec57d9491f76ecf9a9ecb526eaf4bb0c8275118f6`

Selector criteria:

1. `gate_passed`
2. `parse_valid`
3. `source_ids_valid`
4. `required_sections_present`
5. `contradiction_free`
6. `verdict_consensus_count`
7. `final_turn_consensus_repair`
8. `sections_present`
9. `cited_evidence_count`
10. `earliest_turn`

Architecture decision:

Among structurally valid artifacts, verdict consensus outranks citation volume. A final-turn artifact receives a repair bonus only when it agrees with a prior structurally valid artifact after an intervening contradiction. A lone final-turn dissenter does not override a two-of-three structurally valid consensus.

## Internal Holo Review

Verdict:

`PASS_TO_PATCH_VALIDATION`

Meaning:

The selector is cleared for a same-six mechanical validation rerun only. This does not prove the selector generally improves HoloVerify. It only tests whether the named selector patch corrects the known selector regression under fixed conditions.

No further patch is required before the same-six rerun.

## Falsifier

If the same-six rerun does not correct the known failed packet without introducing a new selector-caused miss, the selector patch is not accepted.

## Allowed Next Live Step

Allowed:

- Rerun the same six-pair Atlas Holo rescue lane.
- Label it `PATCH VALIDATION ONLY`.
- Use the same frozen packet bank and runtime manifest.
- Use selector policy `SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03`.
- Score only after trace freeze.

Forbidden:

- No solo.
- No judges.
- No scoring map before trace freeze.
- No substitutions.
- No public claims.
- Do not merge this rerun into benchmark totals.
- Do not call it fresh evidence.

## Exact Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_ATLAS_HOLO_RESCUE_6PAIR_RUNTIME_FIREWALL_V0 using freeze root d4e130d4598963b55e7cc6b708ff6b850a7e14df1a4b2d9bc2b24c3f08fbb7da, runtime manifest 0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7, opaque packet indices 1-12 only, and exactly 60 provider calls: W1 xai/grok-3-mini x12, G1 minimax/MiniMax-M2.5-highspeed x12, W2 openai/gpt-5.4-mini x12, G2 minimax/MiniMax-M2.5-highspeed x12, W3 minimax/MiniMax-M2.5-highspeed x12. Selector policy SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03 hash 32663f8cd92298468ce3648ec57d9491f76ecf9a9ecb526eaf4bb0c8275118f6. Worker contract WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03 hash d5fdea3133f2bcdea0a9c16f1261081a8fe5ca8264f2a2f0a7e43d41c69a0320. PATCH VALIDATION ONLY for SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03; not fresh benchmark evidence. No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims.
```

## Exact Live Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_holoverify_atlas_holo_rescue_live_2026_07_03.py \
  --run-live \
  --approval-statement "I approve live provider execution for HOLOVERIFY_ATLAS_HOLO_RESCUE_6PAIR_RUNTIME_FIREWALL_V0 using freeze root d4e130d4598963b55e7cc6b708ff6b850a7e14df1a4b2d9bc2b24c3f08fbb7da, runtime manifest 0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7, opaque packet indices 1-12 only, and exactly 60 provider calls: W1 xai/grok-3-mini x12, G1 minimax/MiniMax-M2.5-highspeed x12, W2 openai/gpt-5.4-mini x12, G2 minimax/MiniMax-M2.5-highspeed x12, W3 minimax/MiniMax-M2.5-highspeed x12. Selector policy SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03 hash 32663f8cd92298468ce3648ec57d9491f76ecf9a9ecb526eaf4bb0c8275118f6. Worker contract WORKER_CONTRACT_V2_ARTIFACT_FIRST_2026_07_03 hash d5fdea3133f2bcdea0a9c16f1261081a8fe5ca8264f2a2f0a7e43d41c69a0320. PATCH VALIDATION ONLY for SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03; not fresh benchmark evidence. No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims."
```

## Public Claim Guard

Do not say:

- "The patch improved benchmark performance from 11/12 to 12/12."
- "The selector fix proves the architecture is now robust."
- "Atlas now achieves 12/12 on the rescue benchmark."
- "Consensus-first outperforms the prior selector."
- "This validates the benchmark story."

Safe internal language:

The patched selector was mechanically rerun on the same six-pair rescue set to verify whether it corrected a known selection regression under fixed conditions.

## Fresh Signal After Patch Validation

After the same-six mechanical validation, add `2-3` held V5 pairs under a separate label for fresh exploratory signal. Do not fold those pairs into the patch-validation claim.
