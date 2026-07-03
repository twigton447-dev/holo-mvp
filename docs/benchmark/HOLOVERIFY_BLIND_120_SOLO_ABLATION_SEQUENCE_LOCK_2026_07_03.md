# HoloVerify Blind 120 Solo + Ablation Sequence Lock

Status: `NO_PROVIDER_SEQUENCE_LOCK`
Date: `2026-07-03`

This document locks the order for the next evidence steps after the completed HoloVerify blind-120 Holo runtime lane.

## Current Frozen Holo Lane

- Lane: `HOLOVERIFY_BLIND_120_RUNTIME_FIREWALL_V0`
- Packet bank: `120` opaque blind packets
- Holo provider calls: `600`
- Holo scoring: post-freeze only
- Holo observed result: `120/120` correct after post-hoc scoring
- Judges: `0`
- Solo calls: `0`
- Public claims: still locked

## Why Ablation Is Not First

Ablation tells us which architectural component matters.

It does not tell us whether the packets create solo collapses.

The collapse detector is the same-model solo one-shot baseline. We need to run the same three model families alone on the same 120 blind packets, then score post-freeze. That tells us:

- which packets solo models miss,
- which failures are parse/source/admissibility failures,
- which failures are wrong-verdict failures,
- whether the bank has enough solo collapse signal to justify ablation,
- which packets should be sampled for the ablation subset.

## Next Provider Lane

The next live provider lane should be:

`HOLOVERIFY_BLIND_120_SOLO_ONE_SHOT_3MODEL_BASELINE_V0`

Scope:

- Same 120 opaque blind runtime packets
- Same runtime manifest
- No scoring map before trace freeze
- No Holo state
- No Gov
- No Gov baton
- No artifact registry
- No best-artifact selector
- No judges
- No substitutions

Solo model roster:

- `xai/grok-3-mini`
- `openai/gpt-5.4-mini`
- `minimax/MiniMax-M2.5-highspeed`

Expected provider calls:

- `120` xAI one-shot calls
- `120` OpenAI one-shot calls
- `120` MiniMax one-shot calls
- `360` total provider calls

Each solo call must produce one verdict for one packet. Parse failures, malformed output, invented source IDs, missing verdicts, missing evidence, or contract failures remain solo failures.

## Scoring Order

1. Freeze solo traces.
2. Hash-bind solo trace artifacts.
3. Load scoring map only after trace freeze.
4. Score each solo model independently.
5. Report:
   - KNEW/admissible count by model,
   - wrong-verdict count by model,
   - parse/content/admissibility failure count by model,
   - false positives,
   - false negatives,
   - all-three-solo collapse packets,
   - one-or-two-solo collapse packets,
   - solo-correct control packets.

## Ablation Order

Ablation starts only after solo baseline scoring.

Recommended ablation subset:

- all solo-failure packets found by the post-hoc solo baseline
- plus a randomized control set from all-three-solo-KNEW packets
- preserve ALLOW/ESCALATE balance where possible

Recommended ablation arms:

1. `SOLO_ONE_SHOT_BASELINE`
   - Already covered by the full 120 solo baseline.
2. `WORKERS_ONLY_3DNA_NO_GOV`
   - Same worker models and continuity, but no Gov calls and no baton.
3. `FULL_HOLO_FIXED_GOV`
   - Already covered by the completed full Holo blind-120 lane.

Deferred engineering diagnostics:

- `GOV_NO_DETERMINISTIC_ACTUATOR`
- `GOV_WITH_GATE_NO_FINAL_SELECTOR`
- `GOV_ROTATION`

These are useful only if the three-arm ablation shows something ambiguous.

## Stop Rules

Stop and preserve invalid if:

- any runner reads the scoring map before trace freeze,
- packet payloads drift from the blind runtime manifest,
- model substitution is required,
- a provider failure cannot be recovered under the registered transport policy,
- a content/parse failure is retried as if it were transport,
- solo prompt includes Gov/Holo state, baton, answer key, packet truth, or legacy packet IDs,
- ablation arm changes more than the declared component under test.

## Claim Boundary

Before the solo baseline, the Holo 120 result only says the governed blind runtime lane scored `120/120` after post-freeze scoring.

After the solo baseline, we may discuss whether identical solo model families collapsed on the same packets.

After ablation, we may discuss which Holo components appear responsible for rescue behavior.

Do not update public claims until solo and ablation evidence are both packaged.
