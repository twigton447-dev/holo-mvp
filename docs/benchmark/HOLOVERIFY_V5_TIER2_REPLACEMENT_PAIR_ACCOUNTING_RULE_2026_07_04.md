# HoloVerify V5 Tier 2 Replacement Pair Accounting Rule

Date: 2026-07-04

Callsign: STATS SUBAGENT

Scope: no-provider accounting rule for a Tier 2 replacement sibling-pair supplement after exclusion of `HVSF-FACTORY14F-017` from the clean pair denominator due to `PACKET_KEY_DEFECT_CANDIDATE`.

This rule does not run providers, Holo live, solo, or judges. It does not edit frozen runtime evidence.

## Starting Denominators

Immutable raw Tier 2 score:

| Level | Correct | Total | Status |
|---|---:|---:|---|
| Packet | 13 | 14 | raw trace-bound score |
| Complete pair | 6 | 7 | raw trace-bound score |

Current clean diagnostic denominator after quarantine:

| Level | Correct | Total | Exclusion |
|---|---:|---:|---|
| Packet diagnostic | 13 | 13 | excludes `HVSF-FACTORY14F-017-B` only |
| Pair gate | 6 | 6 | excludes entire pair `HVSF-FACTORY14F-017` |

The raw Tier 2 score remains `13/14` packets and `6/7` pairs. The replacement supplement must not rewrite that score.

## Replacement Supplement Shape

The replacement must be a single sibling pair built to replace `HVSF-FACTORY14F-017` at the pair-gate level.

Minimum requirements:

- 2 packets.
- 1 complete sibling pair.
- FN_FALSE_ALLOW rescue lane only.
- Runtime-visible sources must explicitly state the current-cycle fact needed by the key.
- Full HoloGov route per packet: `W1 -> G1 -> W2 -> G2 -> W3`.
- No solo calls.
- No judge calls.
- Trace frozen before post-hoc scoring.
- Scoring map loaded only after trace freeze.

Expected provider-call count:

| Slot | Calls |
|---|---:|
| W1 | 2 |
| G1 | 2 |
| W2 | 2 |
| G2 | 2 |
| W3 | 2 |
| Total worker calls | 6 |
| Total Gov calls | 4 |
| Total provider calls | 10 |

Formula:

`2 packets x 5 provider calls per packet = 10 provider calls`

Gov calls count because this lane is full HoloGov provider-backed. If Gov is deterministic or local, the run is a separate ablation or patch-validation lane and must not be merged into the full-HoloGov Tier 2 supplement.

## Merge Rule

The replacement supplement is merged only after the supplement run is control-valid and post-hoc scored.

Control-valid means:

- Exactly 10 provider calls.
- Slot counts are `W1 x2`, `G1 x2`, `W2 x2`, `G2 x2`, `W3 x2`.
- Role counts are 6 worker calls and 4 Gov calls.
- 0 provider failures.
- 0 solo calls.
- 0 judge calls.
- Trace frozen before scoring.
- Scoring map loaded after trace freeze.
- Packet hashes, prompt hashes, run IDs, and lock manifests validate.
- No packet/key defect is identified in either replacement sibling.

If the supplement is control-valid and both replacement siblings pass:

| Level | Merge | Result | Status |
|---|---|---:|---|
| Packet diagnostic | `13/13 + 2/2` | `15/15` | all score-valid packets across original Tier 2 plus supplement |
| Pair gate | `6/6 + 1/1` | `7/7` | clean complete-pair expansion gate restored |
| Pair-equivalent packets | `12/12 + 2/2` | `14/14` | packets belonging only to the seven clean complete pairs |

Use the pair gate, not the orphan packet diagnostic, for Tier 3 unlocking.

The `15/15` packet diagnostic includes the valid A sibling from the excluded original pair. The `14/14` pair-equivalent packet count excludes both original `HVSF-FACTORY14F-017` siblings and counts only packets that belong to the seven clean complete pairs.

## Pass/Fail Rule For Tier 3 Unlock

Tier 3 may unlock only if all of the following are true:

- The supplement run is control-valid.
- Both replacement sibling packets are score-valid.
- Both replacement sibling packets are correct.
- The replacement pair has no packet/key defect.
- The merged clean pair gate is `7/7`.

If all conditions hold, the internal gate status is:

`TIER2_SUPPLEMENTED_CLEAN_PAIR_GATE_PASSED_DIRECTIONAL_FN_RESCUE`

If only one replacement sibling passes:

- Replacement packet result is `1/2`.
- Replacement pair result is `0/1`.
- Merged packet diagnostic is `14/15`.
- Merged pair gate is `6/7`.
- Tier 3 remains blocked.
- The result is a clean supplement failure only if both packets are score-valid and the run controls are valid.

If either replacement sibling has a packet/key defect:

- Do not treat the affected sibling as a model-quality miss.
- Do not merge the pair into the clean pair gate.
- Classify the supplement as inconclusive.
- Tier 3 remains blocked.

If provider, routing, trace-freeze, scoring-order, hash, or manifest controls fail:

- Classify the supplement as `INVALID_RUN_CONTROL_FAILURE`.
- Do not merge the supplement.
- Tier 3 remains blocked.

## Allowed Internal Language If Replacement Passes

- "The original Tier 2 raw score remains 13/14 packets and 6/7 pairs."
- "After excluding `HVSF-FACTORY14F-017` from the pair gate and adding the passing replacement sibling pair, the supplemented clean pair gate is 7/7."
- "The score-valid packet diagnostic across original Tier 2 plus supplement is 15/15."
- "The pair-equivalent packet count for the seven clean complete pairs is 14/14."
- "Tier 3 is unlocked as an internal directional FN_FALSE_ALLOW rescue expansion gate."
- "This remains patch-validation / directional rescue evidence, not public benchmark evidence."

## Forbidden Language

- "The original Tier 2 run passed 7/7 pairs."
- "The original Tier 2 raw score was 14/14."
- "HoloVerify achieved public benchmark 100% on Tier 2."
- "This proves global FNR."
- "This proves FP precision."
- "This is public benchmark evidence."
- "The quarantined packet was solved by replacement."
- "The replacement run rewrites the frozen Tier 2 trace."
- "The clean denominator is 14/14" without specifying that this is the pair-equivalent packet count excluding both original `HVSF-FACTORY14F-017` siblings.
- "Tier 3 is unlocked if one replacement sibling passes."
- "A deterministic-Gov supplement is equivalent to the full HoloGov Tier 2 lane."

## Evidence Class

This remains:

`PATCH_VALIDATION_DIRECTIONAL_FN_RESCUE_ONLY`

It does not become:

- Public benchmark evidence.
- Global FNR evidence.
- FP precision evidence.
- Statistical superiority evidence.
- Evidence for parse/admissibility-only failures.

## Final Accounting Rule

Do not merge a replacement supplement unless the supplement is control-valid.

If the replacement pair passes `2/2`, merge as:

- Packet diagnostic: `13/13 + 2/2 = 15/15`
- Pair gate: `6/6 + 1/1 = 7/7`
- Pair-equivalent packets: `12/12 + 2/2 = 14/14`
- Tier 3 status: `UNLOCKED_INTERNAL_DIRECTIONAL_FN_RESCUE`

If the replacement pair scores `1/2` or `0/2`, merge as a failed valid supplement and keep Tier 3 blocked.

If the replacement run has a control failure or packet/key defect, do not merge it and keep Tier 3 blocked.

