# D11-Lock 5-Packet Suite Lock

Date: 2026-06-27

Classification: `D11_LOCK_5_PACKET_SUITE_LOCK`

Status: `PRE_LIVE_LOCKED_NO_NEW_PROVIDER_CALLS`

## Purpose

This lock scales the D11-lock proof from two official A/B sibling wins to a five-packet suite without changing architecture, model roles, or judging rules.

D13 and D14 are frozen official results. D10, D11, and D12 are the pending live packets.

## Architecture

Solo lane:

- 7 calls.
- Model: `minimax/MiniMax-M2.5-highspeed`.
- Final scored artifact on call 7.
- No Gov lens, baton, or Gov state.

Holo lane:

- 7 calls total.
- 4 worker calls.
- 3 real Gov provider calls.
- Gov model: `minimax/MiniMax-M2.5-highspeed`.
- Worker order: `xai/grok-3-mini` -> `anthropic/claude-haiku-4-5-20251001` -> `xai/grok-3-mini` -> `anthropic/claude-haiku-4-5-20251001`.
- No final Gov gate.
- Final scored artifact on call 7.

Every Holo worker must receive:

- Gov routing lens before state.
- Cumulative state brief.
- Full latest Gov baton immediately before the current turn command.
- Local deterministic registry.
- D11-lock best-artifact preservation once an admissible artifact exists.

## Judge Rule

No official judgment counts unless it passes [benchmark_full_gated_judge.py](/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/benchmark_full_gated_judge.py).

Official judging requires:

- deterministic compliance, 25 points
- epistemic/source reasoning, 25 points
- structural/executive usability, 25 points
- argument quality, 25 points
- local deterministic audit supplied to the judge
- canonical `artifact_a` / `artifact_b` schema

Narrow, noncanonical, or audit-free judge outputs are diagnostic only.

## Locked Packets

| slot | case | source | status | new generation calls | new judge calls |
|---:|---|---|---|---:|---:|
| 1 | D10 infrastructure configuration change | `/Users/taylorwigton/Desktop/holo-mvp@4b8dbfb` | pending live A/B | 14 | 1 |
| 2 | D11 cyber incident / contract notice / emergency cloud access | `/Users/taylorwigton/Desktop/holo-mvp@4b8dbfb` | pending live A/B | 14 | 1 |
| 3 | D12 fund NAV / redemption cash release | `/Users/taylorwigton/Desktop/holo-mvp@4b8dbfb` | pending live A/B | 14 | 1 |
| 4 | D13 trap canary stale policy / payment diversion | frozen official | complete: Holo 94, Solo 69 | 0 | 0 |
| 5 | D14 trade finance LC discrepancy payment release | frozen official | complete: Holo 94, Solo 69 | 0 | 0 |

Expected new live calls for pending packets:

- Generation calls: 42.
- Gov calls inside generation: 9.
- Judge calls: 3.

## Stop Conditions

Stop and classify invalid if any of these occur:

- provider failure
- model substitution
- missing real Gov provider call
- Holo worker missing Gov lens, state brief, or full latest Gov baton
- Solo prompt receives Gov baton
- official judge lacks local deterministic audit
- official judge is rejected by `benchmark_full_gated_judge.py`
- artifact is mutated after judge packet creation

## Next Allowed Step

Build and dry-run the generic D10-D12 D11-lock runner locally. Then run live generation only for D10, D11, and D12 if preflight passes.
