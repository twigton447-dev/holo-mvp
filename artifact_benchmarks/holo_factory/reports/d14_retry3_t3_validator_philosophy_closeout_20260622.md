# D14 Retry3 T3 Validator Philosophy Closeout

No providers, solo runs, judging, scoring, unblinding, or reruns were performed for this note. It uses committed D14 evidence only.

## Evidence Used

- D14 original Holo run: `artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs/d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_20260622T210025Z`
- D14 retry2 same-packet patch-validation run: `artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs/d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry2_same_packet_patch_validation_20260622T212753Z`
- D14 retry3 same-packet patch-validation run: `artifact_benchmarks/holo_factory/mini_scouts/d14_trade_finance_lc_discrepancy_payment_release_001/runs/d14_trade_finance_lc_discrepancy_payment_release_001_frontier_optimized_opus_gpt55_holo_only_live_retry3_same_packet_patch_validation_20260622T215419Z`

## Closeout

D14 original exposed a real T3 sprawl and token-ceiling failure. The original T3 exceeded the compact audit target, copied a forbidden meta section, missed the action-boundary section, hit the requested token ceiling, and ended uncleanly. That was a genuine safety harness failure because a required intermediate source-fidelity turn could not be accepted, and final synthesis correctly remained blocked for proof credit.

D14 retry2 showed that the first hardening patch over-tightened the T3 contract. Retry2 no longer had the same dangerous truncation profile, but the required section list still included or induced a meta-instruction section shape. The validator properly rejected meta-instruction leakage, but the fixture showed the contract was still misaligned.

D14 retry3 eliminated the dangerous T3 failure mode. The retry3 T3 original was 515 words, ended cleanly, did not hit the provider token ceiling, cited exact D14 source IDs, had all required T3 sections, and had no invented source IDs. Its repair was 548 words, also clean-ending, with the same source-discipline profile.

D14 retry3 still failed under the then-current validator because style constraints treated one prose paragraph line and the 550-word lower target as hard failures. Those were contract-overconstraint failures, not evidence of T3 sprawl, truncation, invented source IDs, missing required sections, or missing source-fidelity substance.

Classification: D14 is a T3 contract-overconstraint fixture, not proof evidence. The committed retry3 run remains not proof-credit eligible because the runtime registry rejected T3 under the old gate, but the corrected no-provider validator now treats the retry3 T3 text as a compact source-fidelity audit rather than a dangerous failure.

## Validator Philosophy Locked By This Patch

The T3 lower-bound word count is nonblocking when required sections, exact source IDs, clean ending, source-fidelity substance, and compactness caps are satisfied. A prose paragraph detection is a warning unless it coincides with essay sprawl, missing structure, upper word cap breach, section cap breach, or bullet cap breach.

Hard failures remain for unclean or mid-sentence endings, provider token-ceiling hits with unclean endings, invented source IDs, missing exact source IDs, missing required T3 sections, missing contradiction/uncertainty/source-fidelity substance, upper word cap or clear sprawl, and meta-instruction leakage.
