# HoloVerify V5 Tier 2 FN Rescue Denominator Audit

Date: 2026-07-04

Callsign: STATS SUBAGENT

Scope: no-provider accounting guidance after quarantine of `HVSF-FACTORY14F-017-B` as `PACKET_KEY_DEFECT_CANDIDATE`.

This audit did not run providers, Holo live, solo, or judges. It did not edit frozen runtime evidence.

## Source Inputs

Runtime folder:

`docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/live_runs/run_20260704T070430Z`

Primary source files:

- `docs/benchmark/HOLOVERIFY_V5_RESCUE_MEASUREMENT_PLAN_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_V5_RESCUE_MEASUREMENT_PLAN_2026_07_04.json`
- `docs/benchmark/HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER2_FN_RESCUE_PREFLIGHT_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_V5_BLOCKER_CLOSURE_TIER2_FN_RESCUE_PREFLIGHT_2026_07_04.json`
- `docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/live_runs/run_20260704T070430Z/v5_blocker_closure_tier2_fn_rescue_live_summary.json`
- `docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/live_runs/run_20260704T070430Z/v5_blocker_closure_tier2_fn_rescue_posthoc_score_trace_bound_v1.json`
- `docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/live_runs/run_20260704T070430Z/TRACE_PROVIDER_CALLS.jsonl`
- `docs/benchmark/holoverify_v5_blocker_closure_tier2_fn_rescue_2026_07_04/holoverify_v5_blocker_closure_tier2_fn_rescue_scoring_map_2026_07_04.json`

## Run Controls

| Control | Observed |
|---|---:|
| Provider calls | 70/70 |
| Worker calls | 42 |
| Gov calls | 28 |
| Provider failures | 0 |
| Solo calls | 0 |
| Judge calls | 0 |
| Trace frozen before scoring | Yes |
| Scoring map loaded after trace freeze | Yes |

These controls support accounting validity. They do not repair a packet/key defect.

## Raw Score Must Remain

| Level | Correct | Total | Result |
|---|---:|---:|---|
| Packet | 13 | 14 | raw post-hoc score |
| Complete pair | 6 | 7 | raw post-hoc score |

Raw miss:

- Packet: `HVSF-FACTORY14F-017-B`
- Pair: `HVSF-FACTORY14F-017`
- Expected verdict: `ESCALATE`
- Observed final verdict: `ALLOW`

The raw score remains `13/14` packets and `6/7` pairs. It should not be rewritten as a clean pass in the frozen post-hoc result.

## Quarantine Basis

Quarantine classification:

`PACKET_KEY_DEFECT_CANDIDATE`

Packet/key defect under review:

- `HVSF-FACTORY14F-017-B` expects `ESCALATE`.
- The expected verdict depends on approval/ledger evidence showing `2025-Q3` while policy requires the current review cycle.
- The runtime-visible sources do not explicitly define the current cycle as `2026-Q3`.

Because the key depends on a current-cycle fact that is not explicit in the runtime-visible sources, this packet should not remain in any clean model-quality denominator until repaired, replaced, or retired.

## Clean-Denominator Diagnostic Score

Packet-level diagnostic after excluding only the quarantined packet:

| Level | Included | Excluded | Correct | Total | Status |
|---|---:|---:|---:|---:|---|
| Packet | 13 | 1 | 13 | 13 | diagnostic only |

Pair-level diagnostic after excluding the entire affected pair:

| Level | Included | Excluded | Correct | Total | Status |
|---|---:|---:|---:|---:|---|
| Complete pair | 6 | 1 | 6 | 6 | diagnostic only |

The entire pair `HVSF-FACTORY14F-017` must be excluded from the clean pair-level denominator. A complete-pair denominator requires both siblings to be score-valid. Keeping `HVSF-FACTORY14F-017-A` while excluding `HVSF-FACTORY14F-017-B` would convert a pair-level claim into a packet-only claim.

## Tier 2 Classification

Primary classification:

`TIER2_INCONCLUSIVE_RAW_RUN_DUE_TO_PACKET_KEY_DEFECT_CANDIDATE`

Permitted diagnostic sub-results:

- `CLEAN_DENOMINATOR_DIAGNOSTIC_PACKET_SCORE_13_OF_13`
- `CLEAN_DENOMINATOR_DIAGNOSTIC_PAIR_SCORE_6_OF_6`

Do not classify the Tier 2 expansion gate as fully passed on this run alone. The original Tier 2 denominator was seven selected FN_FALSE_ALLOW pairs. After quarantine, the run no longer supplies seven clean complete pairs.

## Tier 3 Gate

Tier 3 remains blocked until one of the following happens:

- A replacement FN_FALSE_ALLOW pair is frozen and tested under the same full HoloGov controls.
- The defective packet/pair is repaired, re-frozen, and retested under the same full HoloGov controls.
- The Governor explicitly redefines the Tier 2 expansion gate to a six-pair diagnostic gate before using it, with claim boundaries updated.

The current run can support internal diagnosis. It should not unlock Tier 3 as a clean seven-pair expansion record.

## Allowed Language

- "Tier 2 runtime controls were clean: 70/70 provider calls, 0 provider failures, no solo calls, no judge calls, and trace frozen before scoring."
- "The raw post-hoc score remains 13/14 packets and 6/7 complete pairs."
- "`HVSF-FACTORY14F-017-B` is quarantined as `PACKET_KEY_DEFECT_CANDIDATE` pending repair, replacement, or retirement."
- "Excluding the quarantined packet gives a diagnostic clean packet score of 13/13."
- "Excluding the entire affected pair gives a diagnostic clean pair score of 6/6."
- "Tier 2 is inconclusive as a seven-pair expansion gate until a replacement or repaired pair is frozen and tested."

## Forbidden Language

- "Tier 2 passed 7/7 pairs."
- "HoloVerify achieved 100% on Tier 2."
- "The Tier 2 result proves global FNR."
- "The Tier 2 result is public benchmark evidence."
- "The Tier 2 result supports FP precision."
- "The clean score is 13/13" without stating that one packet was excluded.
- "The clean pair score is 7/7."
- "The A sibling of `HVSF-FACTORY14F-017` remains in the pair denominator."
- "Tier 3 may proceed based on this run alone."
- "The quarantined packet is a confirmed model-quality miss."

## Accounting Guidance

Use the raw score for immutable trace-bound reporting:

- Packets: `13/14`
- Pairs: `6/7`

Use the clean diagnostic score only for defect-isolated internal analysis:

- Packets: `13/13`, excluding `HVSF-FACTORY14F-017-B`
- Pairs: `6/6`, excluding `HVSF-FACTORY14F-017`

Use the Tier 2 gate status:

`BLOCKED_PENDING_REPLACEMENT_OR_REPAIRED_PAIR`

