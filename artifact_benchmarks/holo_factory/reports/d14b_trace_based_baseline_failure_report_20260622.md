# D14B Trace-Based Baseline Failure Report

Date: 2026-06-22

Result classification: `HOLO_COMPLETION_SUCCESS_VS_SOLO_BASELINE_ELIGIBILITY_FAILURE`

## Scope

This report uses committed evidence only:

- D14B frozen packet.
- D14B proof-clean Holo run.
- D14B bounded solo Opus baseline failure.

No provider calls, reruns, judging, scoring, unblinding, or push were performed for this report.

## Packet Identity

- Packet ID: `d14b_trade_finance_lc_amendment_discrepancy_release_001`
- Domain: D14B Trade Finance LC Amendment / Discrepancy / Payment Release
- Packet path: `artifact_benchmarks/holo_factory/mini_scouts/d14b_trade_finance_lc_amendment_discrepancy_release_001`
- Source count: 10
- Source mix: 3 strong, 3 useful_normal, 1 stale_tempting, 1 contradictory_or_complicating, 1 weak_or_limited, 1 table_chart_stat_element
- Source packet hash: `80443b39a6f6c4cd0149bdc88e8016442d448521aabba78619e770f350131ef4`
- Source packet Markdown hash: `46738f52f305653850d36d3f61d2465cc72746f57fa7850b2139542284bb2a52`
- Task brief hash: `bc69e59758848452deec3d425b8a2f30e2a0d7c31e3454dfb9aadbe9bf687ae9`
- Source manifest hash: `1296f118cdf88f2cbde877d6fe7a3f313fb141eed4cc9e97cdf98063ca35d5b8`
- Packet lock hash: `94a8d2524c12440a75744e72abe322f92aaad69fa5c107b6db1f4e2446beb2f2`
- Freeze manifest hash: `c67a4166d9d6f1ca66e987cf2882c5f9ad953f93e05a042a93a1f29d62a4fb15`

## Holo Run Status

- Holo run ID: `d14b_trade_finance_lc_amendment_discrepancy_release_001_frontier_optimized_opus_gpt55_holo_only_live_20260622T221941Z`
- Holo artifact hash: `0b1a2b2e695796f32918ea691f9b7b67650953d335e1090a0dc688c5cf12575b`
- Provider calls: 7
- Repair calls: 1
- Input tokens: 123070
- Output tokens: 19525
- Proof credit eligible: true
- Deterministic gate pass: true
- Required roles all completed: true
- Role compliance all pass: true
- Intermediate completeness all pass: true
- State audit all pass: true
- Registry acceptance all pass: true
- No failed required turn consumed by final: true
- Final artifact completeness pass: true
- Final word band pass: true
- Final repair succeeded if used: true
- Final synthesis blocked: false
- Contamination scan: PASS, findings []
- Blind export integrity: PASS

The Holo run produced a complete, proof-clean governed artifact under the D14B packet constraints.

## Solo Opus Baseline Status

- Solo run ID: `d14b_trade_finance_lc_amendment_discrepancy_release_001_solo_opus_4_8_baseline_live_20260622T223900Z`
- Solo artifact hash: `5b357e28971f7aa2acc95b396b961d434a29c04bef73c82ef37386375ce3277d`
- Provider calls: 6
- Input tokens: 58216
- Output tokens: 20751
- Solo baseline eligible: false
- Deterministic gate pass: true
- Final artifact completeness pass: false
- Final word band pass: true
- Solo word count: 966
- Solo clean-ending status: false
- Solo claim-boundary/disclaimer status: false; required `claim_boundaries` section missing
- Missing sections: `claim_boundaries`
- Eligibility failure: `final_artifact_completeness_failed`
- Deterministic failure reasons: `unclean_or_mid_sentence_ending`, `missing_final_section:claim_boundaries`
- Contamination scan: PASS, findings []
- Blind export integrity: PASS

The solo artifact satisfied the deterministic word band but failed baseline eligibility because it ended mid-sentence and omitted the required claim-boundaries/disclaimer material. The artifact tail cuts off at:

```text
Route open gates to owners in parallel: discrepancy register to Trade Operations document exam (S2_C
```

The truncated string `S2_C` appears because the artifact cut off mid-source-ID. It should be treated as part of the truncation/completion failure, not as a standalone source-hallucination claim.

## Blind Comparison Status

No D14B two-artifact blind comparison packet was created. The hard gate required stopping when `solo_baseline_eligible=false`, so the Holo artifact and solo artifact were not placed into a comparison packet and no held-out judging or scoring was run.

Run-level single-artifact blind exports exist for preservation and integrity checks only. Both run-level exports report contamination PASS and blind-export integrity PASS. They are not a scored Holo-vs-solo comparison.

## Public-Safe Summary

In D14B, Holo produced a proof-clean governed trade-finance payment-release brief on a fresh LC discrepancy holdout. The bounded solo Opus baseline did not produce a baseline-eligible artifact: it stayed inside the 900-1300 word band, but ended mid-sentence and omitted the required claim-boundaries/disclaimer section. Because the solo baseline did not clear deterministic eligibility, no official numeric Holo-vs-Opus score was produced.

## Recommendation

Preserve D14B as baseline-failure evidence, not scored flagship proof. The clean claim is completion discipline at the action boundary: Holo completed the governed artifact inside the benchmark lane, while bounded solo Opus failed deterministic baseline eligibility. Do not convert D14B into a numeric comparison unless a future protocol explicitly authorizes a new eligible baseline and clearly labels any new run lineage.
