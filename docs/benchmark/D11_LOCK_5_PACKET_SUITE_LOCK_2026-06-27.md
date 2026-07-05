# D11-Lock 5-Packet Suite Lock

Date: 2026-06-27

Classification: `D11_LOCK_5_PACKET_SUITE_LOCK`

Status: `POST_LIVE_SPLIT_RUN_PARTIAL_SUITE_LOCKED`

## Purpose

This lock records the five-packet suite attempt without changing architecture, model roles, or judging rules.

D13 and D14 are frozen official results. D10 and D11_CYBER added official Holo wins. D12 is frozen as a regression seed because both artifacts failed the deterministic word-band gate.

Important disclosure: D10 and D11-D12 were not one uninterrupted 45-call run. D10 was rerun as a patched canary after an invalid prepatch attempt exposed harness defects. D11-D12 were then run as a continuation sibling using the patched runner.

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
| 1 | D10 infrastructure configuration change | `/Users/taylorwigton/Desktop/holo-mvp@4b8dbfb` | complete: Holo 95, Solo 71 | 14 | 1 |
| 2 | D11 cyber incident / contract notice / emergency cloud access | `/Users/taylorwigton/Desktop/holo-mvp@4b8dbfb` | complete: Holo 96, Solo 94 | 14 | 1 |
| 3 | D12 fund NAV / redemption cash release | `/Users/taylorwigton/Desktop/holo-mvp@4b8dbfb` | regression: no official winner; both artifacts failed word band | 14 | 0 |
| 4 | D13 trap canary stale policy / payment diversion | frozen official | complete: Holo 94, Solo 69 | 0 | 0 |
| 5 | D14 trade finance LC discrepancy payment release | frozen official | complete: Holo 94, Solo 69 | 0 | 0 |

Executed live calls for D10-D12:

- Generation calls: 42.
- Gov calls inside generation: 9.
- Judge calls: 2.
- Total calls: 44.

D12 had no judge because the local deterministic audit left zero eligible artifacts.

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

Do not rerun D12 until the architecture has deterministic actuation for word-band control.

The next allowed local step is a provider-free patch/design pass for a deterministic form actuator:

- exact per-section word quotas from Gov
- local word-band delta computation
- final-worker hard quota prompt
- fail-closed or explicitly logged deterministic form-normalization step if the final worker still misses the hard band

Reference autopsy: [D11_LOCK_D10_D12_AUTOPSY_2026-06-27.md](/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001/docs/benchmark/D11_LOCK_D10_D12_AUTOPSY_2026-06-27.md).
