# D14 Holo T3 Failure Autopsy

## Scope

This report uses committed D14 Holo run evidence only. It does not run providers, judge, score, unblind, or rerun any D14 condition.

Packet:
`artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001`

Run:
`d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_20260622T210025Z`

Evidence inspected:
- `frontier_holo_optimized_opus_gpt55_v1/raw_outputs/turn_003.json`
- `frontier_holo_optimized_opus_gpt55_v1/prompt_cards/turn_003.md`
- `frontier_holo_optimized_opus_gpt55_v1/raw_outputs/turn_003_intermediate_repair_001.json`
- `frontier_holo_optimized_opus_gpt55_v1/prompt_cards/turn_003_intermediate_repair_001.md`
- `frontier_holo_optimized_opus_gpt55_v1/arch_evidence.json`
- `frontier_holo_optimized_opus_gpt55_v1/artifact_metadata.json`

## Packet And Run Identity

- Packet hash: `4a5c6258039acd423a18c77cb53cabd10647438cd06f604b5199312022ccfa17`
- Final artifact hash: `7d4860fd18f33b31a50ceebf39131476b08d0fae8c5efd3130f24c122cba13be`
- Provider calls in committed run: `9`
- Repair calls in committed run: `3`
- Scores generated: `0`
- Judging runs: `0`
- Unblinding runs: `0`

## T3 Original Output

Role: `contradiction_uncertainty_source_fidelity_reviewer`

The original T3 output had the required five section headings and cited all ten D14 source IDs, but failed the compact-audit contract:

- Word count: `980`
- Target: `700-900`
- Output tokens: `3800`
- Max tokens requested: `3800`
- Hit token ceiling: `true`
- Clean ending: `false`
- Bullet or numbered lines: `27`
- Recorded failures:
  - `unclean_or_mid_sentence_intermediate_ending`
  - `provider_output_hit_max_tokens_with_unclean_intermediate_ending`
  - `t3_compact_audit_over_target_words`

Terminal line:

```text
- Maintain governing/strong vs stale/weak/derived separation throughout, and include the required disclaimer within the 900-1,300 word band
```

## T3 Repair Output

The repair output also had the required five section headings and passed the old role-specific section/source-ID check, but it remained incomplete:

- Repair max tokens requested: `3600`
- Word count: `863`
- Output tokens: `3600`
- Max tokens requested: `3600`
- Hit token ceiling: `true`
- Clean ending: `false`
- Repair accepted: `false`
- Recorded failures:
  - `unclean_or_mid_sentence_intermediate_ending`
  - `provider_output_hit_max_tokens_with_unclean_intermediate_ending`

Terminal line:

```text
Preserve the central thesis: accelerate everything reversible; do not cross the irreversible release boundary until bank-
```

## Registry And Final Synthesis

The registry correctly rejected T3:

- Registry status: `rejected`
- Repair required: `true`
- Repair succeeded: `false`
- Role compliance status: `fail`
- Intermediate completeness status: `fail`
- State audit status: `pass`
- Registry failures:
  - `role_compliance_failed`
  - `intermediate_completeness_failed`
  - `required_repair_not_validated`

The final synthesis correctly avoided consuming the failed required T3:

- `failed_required_turns_consumed_by_final`: `[]`
- `no_failed_required_turn_consumed_by_final`: `true`
- `final_synthesis_blocked`: `true`
- `proof_credit_eligible`: `false`

## Autopsy Answers

Why did T3 exceed target?

The T3 contract required five sections, including three "Top 5" sections, but it had only a total word target and a minimum bullet count. It did not cap bullets per section, words per bullet, words per section, or prose-like paragraph expansion. The role also had to preserve exact long D14 source IDs. That combination let a source-fidelity audit satisfy the visible shape while expanding beyond the 900-word ceiling.

Did the repair prompt restart or compress?

It restarted. The repair prompt said the previous T3 failed because it was incomplete/truncated and asked for a corrected compact audit. It did not tell the model to compress the already-present five-section audit, and it did not use the bounded over-word repair contract because the old selector only chose that path when over-word was the sole failure with a clean ending and no token ceiling.

Did the repair have enough budget?

Not for the restart-shaped prompt it received. The repair had a 3,600-token ceiling and hit it while ending mid-sentence. The evidence does not show that the task required more budget; it shows that the repair was allowed to re-expand instead of being forced into a capped compression-only format.

Did the T3 contract allow too much prose?

Yes. It said "compact bullets or numbered items" but did not ban prose paragraphs, did not set section-level caps, and did not limit bullet length. D14 exposed that a long-bullet audit can be mechanically too large even while carrying useful source-fidelity content.

Did validator target and prompt target mismatch?

The numeric target did not mismatch: prompt and validator both used 700-900 words. The structural target did mismatch: the prompt allowed five top-level audit sections without section caps, while the validator enforced only the total word band, minimum bullets, and source-ID presence. The repair selector also mismatched the actual failure shape by treating mixed over-word plus unclean/token-ceiling failure as an incomplete/truncated restart case.

Did final correctly avoid consuming failed T3?

Yes. The final synthesis input guard recorded no failed required turns consumed by final, and final synthesis remained blocked for proof credit. The D14 run failure is therefore a T3 repair/contract failure, not a final-contamination failure.

## Hardening Patch

The patch changes the T3 source-fidelity audit contract and deterministic gate:

- Keeps the hard target aligned at `700-900` words, with a preferred `720-820` window.
- Requires bullet-only format with no intro, conclusion, prose paragraphs, appendix, or word-count footer.
- Caps T3 at `3-5` bullets per section and `25` bullets total.
- Caps bullets at `48` words and sections at `185` words.
- Adds deterministic failures for too many bullets, prose paragraphs, section overages, and overlong bullets.
- Routes complete-shape T3 failures caused by over-word, section/bullet overage, token-ceiling, or unclean ending into the bounded compression-only repair path.
- Keeps full-budget repair for true missing-substance failures such as missing required sections, under-target output, missing bullets, or missing exact source IDs.

Regression coverage adds D14 as a committed failed-T3 fixture and verifies:

- The original D14 T3 failure is still rejected.
- The new repair selector uses compression-only repair with the capped T3 repair budget.
- The old D14 repair output remains rejected.
- The final synthesis did not consume rejected T3.
- The positive synthetic capped T3 audit still passes.
- D11, D13, and V4.2 no-provider validation lanes remain covered by existing tests.

## Boundary

D14 remains a failed Holo run under the committed evidence. This patch does not convert the prior run into proof-clean evidence and does not create a score. It only hardens the no-provider harness and future live T3 repair behavior.
