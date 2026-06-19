# D1 Evidence Board - Capital Markets

Generated: `2026-06-19T22:08:04Z`

Domain: `capital_markets_trade_shock_execution`

## Executive Read

D1 now has a real data map. The current-lock HoloFactory frontier run generated a complete four-condition D1 set with `577,728` total tokens, `30` provider-call traces, `3` final judge packets, and `18` turn judge packets. It is not benchmark credit and not a public claim yet.

The key split:

- **Current-lock operational evidence:** HoloFactory live frontier run `holo_factory_live_20260619T180210Z`.
- **Current-lock scoring evidence:** `1` primary-clean row, `5` quarantined audit/retest rows, and `6` total outside-DNA proof-credit candidate rows are present.
- **Proof-credit rejudge queue:** `6 / 6` outside-DNA final judge scores are present.
- **Mini lane:** no current-lock mini proof-credit run is scored yet; older legacy mini/error attempts are excluded from this board.

## Current-Lock Frontier Snapshot

- Run: `holo_factory_live_20260619T180210Z`
- Status: `HOLO_FACTORY_LIVE_COMPLETE`
- Benchmark credit: `false`
- Public claim: `false`
- Conditions completed: `4 / 4`
- Valid after revalidation: `2 / 4`
- Total tokens: `577728`
- Latency: `31.585` minutes
- Holo vs mean solo token multiple: `3.212x`
- Final judge packets: `3`
- Turn judge packets: `18`
- Final judge scores observed: `6 / 6`
- Missing final judge scores: `0`
- Proof-credit outside-DNA judge scores observed: `6 / 6`

## Current-Lock Condition Matrix

| condition | condition_type | provider_model | revalidated_status | turns_complete | gov_turns_complete | total_tokens | latency_minutes | final_word_count | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| holo_frontier_fixed_v1 | holo | fixed_holo_route | valid_final | 6 | 5 | 298740 | 10.075 | 3086 |  |
| solo_openai | solo | openai:gpt-5.5 | valid_final | 6 | 0 | 86887 | 8.149 | 3247 |  |
| solo_anthropic | solo | anthropic:claude-opus-4-8 | invalid_final | 6 | 0 | 116592 | 8.011 | 2887 | missing_required_section:risk compliance and audit controls |
| solo_google | solo | google:gemini-3.1-pro-preview | invalid_final | 6 | 0 | 75509 | 5.349 | 3798 | word_count_out_of_band:3798 |

## Current Judge Scores Seen

| run_id | judge_id | judge_provider | solo_condition | holo_score | solo_score | gap_holo_minus_solo | percent_lift | analysis_bucket | analysis_flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| holo_factory_live_20260619T180210Z | judge_outside_minimax_01 | minimax | solo_anthropic | 6.92 | 5.86 | 1.06 | 18.089 | quarantine_invalid_final_retest | invalid_solo_baseline |
| holo_factory_live_20260619T180210Z | judge_outside_xai_01 | xai | solo_anthropic | 7.36 | 8.78 | -1.42 | -16.173 | quarantine_invalid_final_retest | invalid_solo_baseline;judge_family_variance_retest;negative_lift_outlier |
| holo_factory_live_20260619T180210Z | judge_outside_minimax_01 | minimax | solo_google | 8.22 | 5.96 | 2.26 | 37.919 | quarantine_invalid_final_retest | invalid_solo_baseline |
| holo_factory_live_20260619T180210Z | judge_outside_xai_01 | xai | solo_google | 9.26 | 6.08 | 3.18 | 52.303 | quarantine_invalid_final_retest | invalid_solo_baseline;judge_family_variance_retest;high_positive_outlier |
| holo_factory_live_20260619T180210Z | judge_outside_minimax_01 | minimax | solo_openai | 8.26 | 6.36 | 1.9 | 29.874 | primary_clean_metric |  |
| holo_factory_live_20260619T180210Z | judge_outside_xai_01 | xai | solo_openai | 9.28 | 7.44 | 1.84 | 24.731 | quarantine_judge_family_retest | judge_family_variance_retest |

These scores are only for scored current-lock outside-DNA packets already present on disk. Rows in `primary_clean_metric` are the only rows currently allowed to drive the clean metric. Quarantined rows are retained for audit and retest, not deleted.

## Validity-Adjusted Score Lens

Raw judge scores are preserved. This lens applies deterministic caps only when the artifact gate says a final is invalid.

- Rows adjusted: `6`
- Proof-credit rows adjusted: `6`
- Primary-clean rows adjusted: `1`
- Primary-clean raw mean lift: `29.874%`
- Primary-clean adjusted mean lift: `29.874%`
- Raw audit mean lift, all rows: `24.457%`
- Validity-adjusted audit mean lift, all rows: `25.819%`

| judge_id | solo_condition | raw_holo_score | raw_solo_score | raw_percent_lift | adjusted_percent_lift | analysis_bucket | analysis_flags | solo_validity_cap_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| judge_outside_minimax_01 | solo_anthropic | 6.92 | 5.86 | 18.089 | 18.089 | quarantine_invalid_final_retest | invalid_solo_baseline | missing_required_section_cap_8_0 |
| judge_outside_xai_01 | solo_anthropic | 7.36 | 8.78 | -16.173 | -8.0 | quarantine_invalid_final_retest | invalid_solo_baseline;judge_family_variance_retest;negative_lift_outlier | missing_required_section_cap_8_0 |
| judge_outside_minimax_01 | solo_google | 8.22 | 5.96 | 37.919 | 37.919 | quarantine_invalid_final_retest | invalid_solo_baseline | word_count_out_of_band_cap_8_5 |
| judge_outside_xai_01 | solo_google | 9.26 | 6.08 | 52.303 | 52.303 | quarantine_invalid_final_retest | invalid_solo_baseline;judge_family_variance_retest;high_positive_outlier | word_count_out_of_band_cap_8_5 |
| judge_outside_minimax_01 | solo_openai | 8.26 | 6.36 | 29.874 | 29.874 | primary_clean_metric |  | valid_final_no_cap |
| judge_outside_xai_01 | solo_openai | 9.28 | 7.44 | 24.731 | 24.731 | quarantine_judge_family_retest | judge_family_variance_retest | valid_final_no_cap |

This is still not a final public architecture claim because D1 is one domain. The proof-credit queue is scored for the current-lock frontier lane; the next proof burden is matched mini, order-permutation, and cross-domain replication.

## Outside-DNA Rejudge Queue

This queue is the proof-credit path for D1. It is not executed by this board builder.

- Expected proof-credit outside-DNA final judge scores: `6`
- Observed proof-credit outside-DNA final judge scores: `6`
- Score status counts: `{'scored': 6}`

| solo_condition | judge_id | judge_provider | judge_model | proof_credit_eligible | score_status | rejudge_reason |
| --- | --- | --- | --- | --- | --- | --- |
| solo_anthropic | judge_outside_xai_01 | xai | grok-4.3 | True | scored | outside_dna_required_for_proof_credit |
| solo_anthropic | judge_outside_minimax_01 | minimax | MiniMax-M2.5-highspeed | True | scored | outside_dna_required_for_proof_credit |
| solo_google | judge_outside_xai_01 | xai | grok-4.3 | True | scored | outside_dna_required_for_proof_credit |
| solo_google | judge_outside_minimax_01 | minimax | MiniMax-M2.5-highspeed | True | scored | outside_dna_required_for_proof_credit |
| solo_openai | judge_outside_xai_01 | xai | grok-4.3 | True | scored | outside_dna_required_for_proof_credit |
| solo_openai | judge_outside_minimax_01 | minimax | MiniMax-M2.5-highspeed | True | scored | outside_dna_required_for_proof_credit |

## Current-Lock Run Inventory

- D1 run records shown: `1`
- Complete/pass records: `1`
- Live/partial-live records: `1`
- HoloFactory suite records: `1`

| lane | run_id | status | run_class | condition_count | total_tokens | latency_minutes | final_judge_packets | turn_judge_packets | judge_scores |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| holo_factory | holo_factory_live_20260619T180210Z | HOLO_FACTORY_LIVE_COMPLETE | holo_factory_live | 4 | 577728 | 31.585 | 3 | 18 | 8 |

## Five-Domain Projection

Using the current-lock D1 HoloFactory frontier run as the base:

- Frontier generation tokens for 5 domains: `2888640`
- Frontier generation latency for 5 domains: `157.925` minutes
- Frontier provider calls for 5 domains: `150`
- Frontier final judge packets for 5 domains: `15`
- Frontier turn judge packets for 5 domains: `90`
- Final judge scores expected for 5 domains: `30`
- Turn judge scores if enabled for 5 domains: `360`

Mini-lane projection is not proof evidence. No current-lock HoloFactory mini live run is scored yet:

- Mini current-lock status: `pending_not_scored`
- Mini current-lock note: `No current-lock HoloFactory mini live proof run is scored. Legacy mini/error attempts are excluded.`

## Claim Boundaries

- Do not claim architecture-wide benchmark lift from D1 alone; mini, order, and cross-domain replication are still pending.
- Do not merge historical or legacy judged lift with current-lock D1 proof analytics.
- Do not use invalid-baseline rows, same-DNA rows, or high-variance/outlier judge rows in the primary clean metric.
- Do not publish dollar cost projections until a model-pricing table is separately locked.
- Current-lock D1 frontier has outside-DNA proof-credit candidate scoring; two solo baseline finals carry validity flags.
- D1 has enough data to plan mini, order, and D2-D5 replication, but not enough to make the architecture-wide headline claim.

## Immediate Data Gaps

1. Retest quarantined D1 rows with additional outside-DNA judges.
2. Repair/rerun invalid solo baselines under the current lock.
3. Keep raw audit score, primary-clean score, validity-adjusted score, and provider reliability score separate.
4. Run the current-lock mini lane cleanly.
5. Add dollar-cost estimates only after pricing assumptions are locked.
