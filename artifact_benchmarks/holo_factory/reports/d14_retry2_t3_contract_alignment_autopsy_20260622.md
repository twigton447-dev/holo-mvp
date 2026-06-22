# D14 Retry2 T3 Contract-Alignment Autopsy

## Scope

No providers, solo runs, judging, scoring, or unblinding were performed for this note. It uses committed D14 retry2 evidence only:

- `artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs/d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_same_packet_patch_validation_20260622T212753Z/frontier_holo_optimized_opus_gpt55_v1/raw_outputs/turn_003.json`
- `artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs/d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_same_packet_patch_validation_20260622T212753Z/frontier_holo_optimized_opus_gpt55_v1/raw_outputs/turn_003_intermediate_repair_001.json`
- `artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs/d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_same_packet_patch_validation_20260622T212753Z/frontier_holo_optimized_opus_gpt55_v1/arch_evidence.json`

## Findings

The retry2 T3 original was 654 words, ended cleanly, did not hit the token ceiling, and cited the exact D14 packet source IDs. It still failed because the T3 contract itself required a meta section named `Final synthesis instructions`. The model copied that required section from the prompt into the output, and the validator counted the actual output section. This was not hidden prompt scaffolding over-captured by the validator.

The repair output repeated the same contract shape. It remained clean-ending and below the old 700-word floor, but the real alignment issue was still the meta section plus trailing final-drafter instruction prose.

The 700-word lower bound was too high for the newly capped format. With five sections, 3-5 bullets per section, 25 bullets total, 48 words per bullet, and 185 words per section, a valid compact audit can be materially complete below 700 words. The patch moves the target to `550-800` and makes the lower bound nonblocking when required sections, exact source IDs, and substantive bullet checks pass.

The bullet/prose checks were not rejecting clean compact bullets. They were rejecting a standalone non-bullet drafter instruction and, before the patch, numbered section headings were being double-counted as bullets. The patch classifies T3 section headings before bullet counting.

## Patch Summary

- Replaced the required T3 meta section `Final synthesis instructions` with `Action-boundary cautions`.
- Added explicit rejection for forbidden meta headings such as `Final synthesis instructions`.
- Changed the T3 compact audit target from `700-900` to `550-800`.
- Kept the hard upper bound and sprawl checks.
- Made under-target word count nonblocking when all required sections, exact source IDs, and substantive compact-audit checks pass.
- Preserved clean-ending, exact-source-ID, no-invented-ID, and no-prose-essay checks.
- Added D14 retry2 T3 original and repair outputs as regression fixtures.

## Boundary

D14 retry2 remains failed same-packet patch-validation evidence. This patch aligns the no-provider T3 contract and validator for future runs; it does not convert retry2 into proof-clean evidence and does not create a score.
