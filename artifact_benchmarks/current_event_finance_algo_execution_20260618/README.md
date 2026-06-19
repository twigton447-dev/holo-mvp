# Current Event Finance Algo Execution Packet

Packet: `current_event_finance_algo_execution_20260618`
Created: `2026-06-18T22:39:48.375563+00:00`

This packet is a frozen-context draft for a finance-facing HoloBuild report run. The intended artifact is a highly complex institutional report on adaptive execution intelligence for algorithmic trading under current June 2026 market conditions.

Live proof-of-concept report generation has been run from this packet with `benchmark_credit: false` and `public_claim: false`. Use the generated intelligence reports as diagnostics until a full frozen benchmark run is completed.

## Immutability Rule

The source pack, brief, rubric, Gov protocol, role flow, routing configs, judge panel, and solo-suite manifest are hash-locked. After live evidence exists for a suite, do not edit that suite in place. Add a new suite id instead.

## Intended Model Policy

Models do **not** browse during generation. Holo, solos, and judges receive the same frozen context pack.

## Verified Frontier Cohorts

Packetless smoke probes completed with no benchmark/source/artifact payload.

Main max-intelligence cohort:

- OpenAI: `gpt-5.5`
- Anthropic: `claude-opus-4-8`
- Google: `gemini-3.1-pro-preview`

Stable Google fallback:

- Google: `gemini-3.5-flash`

Robustness lane:

- xAI: `grok-4.3`

Solo sweep suites:

- `frontier_baseline` - primary three frontier solos.
- `mini_baseline` - OpenAI mini, Anthropic Haiku, Gemini Flash Lite, Grok mini, and MiniMax.
- `extended_solo_sweep` - mapped frontier, robustness, fallback, mini, and MiniMax solos.
- `frontier_plus_xai_baseline` - OpenAI, Anthropic, Google, and xAI Grok frontier solos for Frontier4 Holo comparisons.

Mini-Holo diagnostic matrix:

- `mini_order_a_openai_bookend`
- `mini_order_b_haiku_bookend`
- `mini_order_c_gemini_lite_bookend`
- `mini_order_d_grok_bookend`
- `mini_order_e_minimax_bookend`

Frontier4 diagnostic matrix:

- `frontier4_order_a_openai_bookend`
- `frontier4_order_b_opus_bookend`
- `frontier4_order_c_gemini_bookend`
- `frontier4_order_d_grok_bookend`

These routes add Grok 4.3 as a HoloAgent while preserving the same source pack, role flow, fixed Gov, word band, validity gate, and blind judges. Run all four before making Frontier4 route-insensitive claims.

These routes use all five locked minis as Holo analysts with one mini bookending each six-turn run. Run all five before making route-insensitive mini-Holo claims.

Mini-Holo Gov-ablation matrix:

- `mini_gov_haiku_order_a`
- `mini_gov_gemini_lite_order_a`
- `mini_gov_grok_order_a`
- `mini_gov_minimax_order_a`

These routes keep the same mini HoloAgent analyst order as `mini_order_a_openai_bookend` and change only Gov. Frontier judges remain fixed for all runs. Use these to measure Gov sensitivity, not to replace the order matrix.

Unavailable on this key:

- Anthropic: `claude-fable-5`

## Files

- `source_pack.json` - structured frozen source pack.
- `source_pack.md` - human-readable source pack and synthesis.
- `report_brief.json` - generation brief, turn design, judge design.
- `holo_frontier_run_prompt.md` - draft prompt for the generation run.
- `judge_brief.md` - human-readable judge scoring brief.
- `judge_rubric_8criteria.json` - weighted finance-specific scoring rubric.
- `judge_panel_frontier_blind.json` - four-judge blinded panel contract with no-self-DNA primary scoring.
- `solo_model_sweep.json` - immutable suite manifest for frontier, mini, and extended solo runs.
- `mini_holo_data_trail_matrix.json` - diagnostic matrix for every locked mini solo versus every all-mini Holo route.
- `frontier_plus_xai_holo_matrix.json` - diagnostic matrix for four-frontier solo baselines and Frontier4 Holo routes including Grok 4.3.
- `mini_holo_governor_ablation_matrix.json` - diagnostic matrix for fixed analyst order with different mini Gov models.

- `gov_technical_probe_protocol.json` / `.md` - technical probing requirements for Gov mission packets.
- `finance_algo_adversarial_role_flow.json` / `.md` - finance-specific six-turn adversarial role order.
- `build_benchmark_intelligence.py` - builds the client-readable intelligence report, deterministic insight extraction, and chart-ready data from completed run artifacts.
- `build_hash_locked_lift_rollup.py` - aggregates completed analyzed runs into mean Holo lift, current-lock match status, and chart-ready CSV.

## Approval Boundary

Before running Holo/frontier generation, Taylor should explicitly approve transmitting this frozen source pack and brief to the selected providers.
