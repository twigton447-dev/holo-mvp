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

Mini-Holo diagnostic matrix:

- `mini_order_a_openai_bookend`
- `mini_order_b_haiku_bookend`
- `mini_order_c_gemini_lite_bookend`
- `mini_order_d_grok_bookend`
- `mini_order_e_minimax_bookend`

These routes use all five locked minis as Holo analysts with one mini bookending each six-turn run. Run all five before making route-insensitive mini-Holo claims.

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

- `gov_technical_probe_protocol.json` / `.md` - technical probing requirements for Gov mission packets.
- `finance_algo_adversarial_role_flow.json` / `.md` - finance-specific six-turn adversarial role order.
- `build_benchmark_intelligence.py` - builds the client-readable intelligence report and chart-ready data from completed run artifacts.

## Approval Boundary

Before running Holo/frontier generation, Taylor should explicitly approve transmitting this frozen source pack and brief to the selected providers.
