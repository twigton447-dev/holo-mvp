# Current Event Finance Algo Execution Packet

Packet: `current_event_finance_algo_execution_20260618`
Created: `2026-06-18T22:39:48.375563+00:00`

This packet is a frozen-context draft for a finance-facing HoloBuild report run. The intended artifact is a highly complex institutional report on adaptive execution intelligence for algorithmic trading under current June 2026 market conditions.

No full report generation has been run from this packet yet. A tiny live smoke transmitted the frozen packet to the frontier providers with `benchmark_credit: false`.

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

Unavailable on this key:

- Anthropic: `claude-fable-5`

## Files

- `source_pack.json` - structured frozen source pack.
- `source_pack.md` - human-readable source pack and synthesis.
- `report_brief.json` - generation brief, turn design, judge design.
- `holo_frontier_run_prompt.md` - draft prompt for the generation run.
- `judge_brief.md` - human-readable judge scoring brief.
- `judge_rubric_8criteria.json` - weighted finance-specific scoring rubric.
- `judge_panel_frontier_blind.json` - three-frontier blinded judge panel contract.

- `gov_technical_probe_protocol.json` / `.md` - technical probing requirements for Gov mission packets.
- `finance_algo_adversarial_role_flow.json` / `.md` - finance-specific six-turn adversarial role order.

## Approval Boundary

Before running Holo/frontier generation, Taylor should explicitly approve transmitting this frozen source pack and brief to the selected providers.
