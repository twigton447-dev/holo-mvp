# D1 Evidence Board - Capital Markets

Generated: `2026-06-19T19:45:52Z`

Domain: `capital_markets_trade_shock_execution`

## Executive Read

D1 now has a real data map. The current-lock HoloFactory frontier run generated a complete four-condition D1 set with `577,728` total tokens, `30` provider-call traces, `3` final judge packets, and `18` turn judge packets. It is not benchmark credit and not a public claim yet.

The key split:

- **Current-lock operational evidence:** HoloFactory live frontier run `holo_factory_live_20260619T180210Z`.
- **Current-lock scoring evidence:** incomplete; `2 / 12` expected final judge scores are present.
- **Historical judged lift evidence:** legacy finance runs with measured Holo lift, but `matches_current_lock=false`.

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
- Final judge scores observed: `2 / 12`
- Missing final judge scores: `10`
- Final score status counts: `{'scored': 2, 'attempted_no_parsed_score': 1, 'not_attempted': 9}`

## Current-Lock Condition Matrix

| condition | condition_type | provider_model | revalidated_status | turns_complete | gov_turns_complete | total_tokens | latency_minutes | final_word_count | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| holo_frontier_fixed_v1 | holo | fixed_holo_route | valid_final | 6 | 5 | 298740 | 10.075 | 3086 |  |
| solo_openai | solo | openai:gpt-5.5 | valid_final | 6 | 0 | 86887 | 8.149 | 3247 |  |
| solo_anthropic | solo | anthropic:claude-opus-4-8 | invalid_final | 6 | 0 | 116592 | 8.011 | 2887 | missing_required_section:risk compliance and audit controls |
| solo_google | solo | google:gemini-3.1-pro-preview | invalid_final | 6 | 0 | 75509 | 5.349 | 3798 | word_count_out_of_band:3798 |

## Current Judge Scores Seen

| run_id | judge_id | solo_condition | holo_score | solo_score | gap_holo_minus_solo | percent_lift |
| --- | --- | --- | --- | --- | --- | --- |
| holo_factory_live_20260619T180210Z | judge_frontier_01 | solo_anthropic | 8.6 | 9.06 | -0.46 | -5.077 |
| holo_factory_live_20260619T180210Z | judge_frontier_02 | solo_anthropic | 8.76 | 8.36 | 0.4 | 4.785 |

These scores are only for scored packets already present on disk. They are not enough for a full D1 claim.

## Validity-Adjusted Score Lens

Raw judge scores are preserved. This lens applies deterministic caps only when the artifact gate says a final is invalid.

- Rows adjusted: `2`
- Raw observed mean gap: `-0.03`
- Raw observed mean lift: `-0.146%`
- Validity-adjusted observed mean gap: `0.68`
- Validity-adjusted observed mean lift: `8.5%`

| judge_id | solo_condition | raw_holo_score | raw_solo_score | raw_gap_holo_minus_solo | adjusted_holo_score | adjusted_solo_score | adjusted_gap_holo_minus_solo | adjusted_percent_lift | solo_validity_cap_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| judge_frontier_01 | solo_anthropic | 8.6 | 9.06 | -0.46 | 8.6 | 8.0 | 0.6 | 7.5 | missing_required_section_cap_8_0 |
| judge_frontier_02 | solo_anthropic | 8.76 | 8.36 | 0.4 | 8.76 | 8.0 | 0.76 | 9.5 | missing_required_section_cap_8_0 |

This is still not a final claim because the current-lock score queue is incomplete.

## Missing Current-Lock Final Judging Queue

| solo_condition | judge_id | judge_provider | judge_model | outside_judge | score_status | prompt_card_exists | trace_exists |
| --- | --- | --- | --- | --- | --- | --- | --- |
| solo_anthropic | judge_frontier_03 | google | gemini-3.1-pro-preview | False | attempted_no_parsed_score | True | True |
| solo_anthropic | judge_frontier_04 | xai | grok-4.3 | True | not_attempted | False | False |
| solo_google | judge_frontier_01 | openai | gpt-5.5 | False | not_attempted | False | False |
| solo_google | judge_frontier_02 | anthropic | claude-opus-4-8 | False | not_attempted | False | False |
| solo_google | judge_frontier_03 | google | gemini-3.1-pro-preview | False | not_attempted | False | False |
| solo_google | judge_frontier_04 | xai | grok-4.3 | True | not_attempted | False | False |
| solo_openai | judge_frontier_01 | openai | gpt-5.5 | False | not_attempted | False | False |
| solo_openai | judge_frontier_02 | anthropic | claude-opus-4-8 | False | not_attempted | False | False |
| solo_openai | judge_frontier_03 | google | gemini-3.1-pro-preview | False | not_attempted | False | False |
| solo_openai | judge_frontier_04 | xai | grok-4.3 | True | not_attempted | False | False |

## Historical Diagnostic Lift

The legacy hash-locked lift rollup contains judged final-output comparisons, but those runs do not match the current lock. Treat as directional diagnostics, not public benchmark claims.

- Historical scored pair rows: `4`
- Historical mean lift, all rows: `10.713%`
- Historical mean lift, clean rows: `13.808%`
- Historical lift range, all rows: `[3.494, 23.767]`
- Current-lock matching historical rows: `0`

| run_id | solo_condition | holo_score | solo_score | gap_holo_minus_solo | percent_lift | clean_percent_lift | matches_current_lock |
| --- | --- | --- | --- | --- | --- | --- | --- |
| full_frontier_finance_algo_execution_20260618T232008Z | solo_openai | 8.87 | 8.527 | 0.343 | 4.023 | 4.808 | False |
| full_frontier_finance_algo_execution_20260618T232008Z | solo_anthropic | 8.887 | 8.587 | 0.3 | 3.494 | 5.532 | False |
| full_frontier_finance_algo_execution_20260618T232008Z | solo_xai | 8.962 | 7.241 | 1.721 | 23.767 | 32.454 | False |
| patent_grade_finance_opus_canary_parity_a6b5a41_20260619T0520Z | solo_anthropic | 9.193 | 8.24 | 0.953 | 11.566 | 12.439 | False |

## Run Inventory Summary

- Total D1 run records found: `41`
- Complete/pass records: `33`
- Live/partial-live records: `11`
- HoloFactory suite records: `3`
- Legacy finance-algo records: `38`

| lane | run_id | status | run_class | condition_count | total_tokens | latency_minutes | final_judge_packets | turn_judge_packets | judge_scores |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| holo_factory | holo_factory_live_20260619T180210Z | HOLO_FACTORY_LIVE_COMPLETE | holo_factory_live | 4 | 577728 | 31.585 | 3 | 18 | 2 |
| holo_factory | holo_factory_no_provider_smoke_20260619T175124Z | HOLO_FACTORY_NO_PROVIDER_SMOKE_PASS | no_provider_smoke | None | None | None | 8 | 48 | None |
| holo_factory | holo_factory_no_provider_smoke_live_adapter_canary_20260619T000000Z | HOLO_FACTORY_NO_PROVIDER_SMOKE_PASS | no_provider_smoke | None | None | None | 3 | 18 | None |
| legacy_finance_algo | full_frontier_finance_algo_execution_20260618T232008Z | FULL_FRONTIER_FINANCE_E2E_COMPLETE | live_or_partial_live | 4 |  |  | 3 | 0 | 9 |
| legacy_finance_algo | full_frontier_finance_algo_execution_20260619T031544Z | running_generation_solo_anthropic | live_or_partial_live | 1 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | full_frontier_finance_algo_execution_mini_order_a_openai_bookend_20260619T151124Z | FULL_FRONTIER_FINANCE_E2E_ERROR | live_or_partial_live | 5 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | full_frontier_finance_algo_execution_mini_order_a_openai_bookend_20260619T160811Z | FULL_FRONTIER_FINANCE_E2E_ERROR | live_or_partial_live | 5 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | full_frontier_finance_algo_execution_order_a_current_20260619T033659Z | FULL_FRONTIER_FINANCE_E2E_COMPLETE | live_or_partial_live | 4 |  |  | 3 | 0 | 9 |
| legacy_finance_algo | full_frontier_finance_algo_execution_order_a_current_20260619T061158Z | FULL_FRONTIER_FINANCE_E2E_ERROR | live_or_partial_live | 1 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | holo_only_mini_order_a_openai_bookend_patched_20260619T1724Z | FULL_FRONTIER_FINANCE_E2E_ERROR | live_or_partial_live | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_20260618T225956Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_20260619T023030Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_20260619T023536Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_20260619T031544Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_20260619T032749Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_20260619T033303Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_20260619T033305Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_frontier4_order_d_grok_bookend_frontier_plus_xai_baseline_20260619T151700Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 24 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_mini_gov_haiku_order_a_mini_baseline_20260619T073129Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 30 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_mini_order_a_openai_bookend_mini_baseline_20260619T071738Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 30 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_mini_order_a_openai_bookend_mini_baseline_20260619T071940Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 30 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_mini_order_a_openai_bookend_mini_baseline_20260619T151124Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 30 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_mini_order_a_openai_bookend_mini_baseline_20260619T172138Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 30 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T033352Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T045733Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T045833Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T050844Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T055546Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 18 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T055643Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 18 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T055831Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 18 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_20260619T061024Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 18 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_extended_solo_sweep_20260619T065738Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 66 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_frontier_baseline_20260619T065731Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 18 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_a_current_mini_baseline_20260619T065718Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 30 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_b_opus_bookend_20260619T033401Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | no_provider_smoke_finance_algo_execution_order_c_gemini_bookend_20260619T033408Z | NO_PROVIDER_SMOKE_PASS | no_provider_smoke | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | patent_grade_finance_opus_canary_20260619T0500Z | running_generation_solo_anthropic | live_or_partial_live | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | patent_grade_finance_opus_canary_parity_a6b5a41_20260619T0520Z | FULL_FRONTIER_FINANCE_E2E_COMPLETE | live_or_partial_live | 2 |  |  | 1 | 0 | 3 |
| legacy_finance_algo | routing_robustness_finance_algo_execution_20260619T004734Z | ROUTING_ROBUSTNESS_RUNNING | routing_robustness_diagnostic | 0 |  |  | 0 | 0 | 0 |
| legacy_finance_algo | routing_robustness_finance_algo_execution_20260619T010216Z | ROUTING_ROBUSTNESS_RUNNING | routing_robustness_diagnostic | 0 |  |  | 0 | 0 | 0 |

## Five-Domain Projection

Using the current-lock D1 HoloFactory frontier run as the base:

- Frontier generation tokens for 5 domains: `2888640`
- Frontier generation latency for 5 domains: `157.925` minutes
- Frontier provider calls for 5 domains: `150`
- Frontier final judge packets for 5 domains: `15`
- Frontier turn judge packets for 5 domains: `90`
- Final judge scores expected for 5 domains: `60`
- Turn judge scores if enabled for 5 domains: `360`

Mini-lane projection is available but should be treated as diagnostic because the observed D1 mini source run ended with an error/partial status:

- Mini diagnostic D1 tokens: `892818`
- Mini diagnostic 5-domain tokens: `4464090`
- Mini diagnostic 5-domain latency: `262.88` minutes

## Claim Boundaries

- Do not claim current benchmark lift from D1 until current-lock final judge scoring is complete.
- Do not merge historical judged lift with current-lock operational data as if they are the same benchmark.
- Do not publish dollar cost projections until a model-pricing table is separately locked.
- Current-lock D1 shows operational feasibility and validity gaps; historical D1 shows directional lift.
- D1 has enough data to plan D2-D5, but not enough current-lock judging to make the headline claim.

## Immediate Data Gaps

1. Score the remaining current-lock final judge packets.
2. Build a current-lock judge rollup.
3. Decide validity-penalty reporting: raw quality score, validity-adjusted score, and provider reliability score.
4. Run or rebuild the current-lock mini lane cleanly if mini claims matter.
5. Add dollar-cost estimates only after pricing assumptions are locked.
