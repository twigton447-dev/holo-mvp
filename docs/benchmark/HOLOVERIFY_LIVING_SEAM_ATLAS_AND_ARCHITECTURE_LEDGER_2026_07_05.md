# HoloVerify Living Seam Atlas And Architecture Ledger

Date: 2026-07-05

Callsign: STATS SUBAGENT

Scope: living evidence ledger and Phase 1 sample-size roadmap. This update did not run providers, Holo live, solo, or judges. It did not edit frozen runtime evidence.

## 1. Strict Public Denominator

Current strict public denominator:

| Lane | Packets | ALLOW | ESCALATE | Holo score | Scope |
|---|---:|---:|---:|---:|---|
| Blind Holo lane | 120 | 60 | 60 | 120/120 | strict current public denominator |

Source-backed status:

- Packet bank freeze: 120 packets, 60 sibling pairs, 60 ALLOW and 60 ESCALATE.
- Holo post-hoc checkpoint: 120 packets scored, 120 correct, 0 incorrect.
- The checkpoint represents 600 provider calls from the fixed-Gov Holo runtime batches; scoring itself made 0 provider calls, 0 solo calls, and 0 judge calls.

Why the old `614` is not the current public denominator:

- `614` appears in older benchmark-page draft material as a prior clean-denominator framing.
- The current strict public denominator rule counts only the blind-120 lane because it has its own blind packet bank, balanced truth split, runtime-manifest separation from scoring map, batch execution lock, trace-bound post-hoc scoring, and current claim boundary.
- Older 614-era evidence remains historical/internal unless re-admitted under the current strict rule. It must not be combined with the blind-120 denominator for public FPR/FNR or Wilson claims.

## 2. Phase 1 Wilson Target

Phase 1 target:

| Target | Packets |
|---|---:|
| Total clean balanced packets | 762 |
| ALLOW packets | 381 |
| ESCALATE packets | 381 |
| Current strict blind-120 packets | 120 |
| Remaining packets needed | 642 |
| Remaining ALLOW packets needed | 321 |
| Remaining ESCALATE packets needed | 321 |

Plain-English Wilson explanation:

If Holo has zero observed misses, the Wilson 95% upper bound asks: "Given this many clean trials and no observed errors, how high could the true error rate still plausibly be?" With 381 clean packets on one side, the side-specific Wilson 95% upper bound is just under 1%. That is why Phase 1 targets 381 ALLOW and 381 ESCALATE packets, instead of relying on the overall 120-packet blind lane.

Current strict blind-120 status:

- Current ALLOW side: 60/60 observed correct.
- Current ESCALATE side: 60/60 observed correct.
- Current side-specific sample size is 60 per side, so the side-specific Wilson upper bound is still above the Phase 1 target band.
- Phase 1 needs 321 more clean ALLOW packets and 321 more clean ESCALATE packets.

## 3. Solo Failure Factory

Solo Failure Factory scoreboard totals:

| Metric | Count |
|---|---:|
| Solo scout pairs inspected | 210 |
| Pairs with at least one solo failure | 104 |
| Pairs with wrong-verdict solo failure | 79 |
| FP_OVERBLOCK pairs | 33 |
| FN_FALSE_ALLOW pairs | 18 |
| All-three solo-collapse pairs | 18 |
| Mixed pairs | 27 |
| Parse/admissibility-only pairs | 25 |
| Quarantined packet/key defects | 1 |
| Holo rescue runs attempted | 6 |

Evidence class boundary:

- Solo failure evidence records where one-shot solo models failed.
- Holo rescue evidence records Holo rescue runs.
- Holo failure evidence remains separate from rescue evidence.
- Patch-validation evidence remains separate from fresh benchmark evidence.
- Packet/key defects are quarantined and do not enter clean denominators.
- Parse/admissibility-only pairs are held separately from wrong-verdict denominators.

## 4. Holo Rescue Status

V5 Tier 1:

- Status: `V5_TIER1_PATCH_VALIDATION_PASSED`.
- Corrected score fields: 2 packets, 2 correct, 0 incorrect.
- Complete pairs: 0.
- Scope: patch validation only; no public denominator, no FPR/FNR claim, no complete-pair claim.

V5 Tier 2 raw run:

- Runtime controls: 70/70 provider calls, 0 provider failures, 0 solo calls, 0 judge calls, trace frozen before scoring.
- Raw score: 13/14 packets and 6/7 complete pairs.
- Raw miss: `HVSF-FACTORY14F-017-B`.
- Raw score remains preserved and must not be rewritten.

Quarantined Tier 2 packet:

- Packet: `HVSF-FACTORY14F-017-B`.
- Pair: `HVSF-FACTORY14F-017`.
- Status: `PACKET_KEY_DEFECT_CANDIDATE`.
- Reason: expected ESCALATE depended on knowing that review cycle `2025-Q3` was stale, but runtime-visible sources did not explicitly define `current_cycle=2026-Q3`.

Replacement pair:

- Replacement pair: `HVSF-FACTORY14F-017R`.
- Provider calls: 10/10.
- Provider failures: 0.
- Score: 2/2 packets, 1/1 complete pair.
- Scope: replacement supplement for the quarantined pair; not public benchmark evidence.

Merged clean internal gate:

- Clean diagnostic after quarantine: 13/13 packets, 6/6 pairs.
- Replacement supplement: 2/2 packets, 1/1 pair.
- Merged clean internal gate: 15/15 score-valid packet diagnostic and 7/7 clean internal pair gate.
- Tier 3 readiness: unlocked only as an internal directional FN_FALSE_ALLOW rescue expansion gate, subject to separate preflight, approval, runtime-only manifest, trace freeze, and post-hoc scoring.

## 5. Quarantine Register

Packet/key defects:

| Item | Status | Reason | Denominator treatment |
|---|---|---|---|
| `HVSF-FACTORY14F-017-B` | `PACKET_KEY_DEFECT_CANDIDATE` | Runtime-visible sources omitted explicit `current_cycle=2026-Q3` needed by key | Excluded from clean packet denominator; entire pair excluded from clean pair denominator |
| `HVSF-FACTORY13X-002` / `HVSF-FACTORY13X-002-A` | quarantine recommended | Likely packet/key defect: ALLOW unsupported by visible sources | Exclude pending review |

Underspecified packets:

- `HVSF-FACTORY14F-017-B`: stale-current-cycle trap underspecified because the packet did not expose the current cycle required to score the B-side ESCALATE key cleanly.
- No additional underspecified packet register was confirmed in this ledger pass.

Stale or invalid lanes:

- Old `614` public-denominator draft: stale for current public denominator; do not use as current public FPR/FNR denominator.
- First full blind-120 execution attempt `run_20260703T020428Z`: invalid failed-closed run preserved by execution lock; not denominator evidence.
- Tier 2 raw run before quarantine/replacement: preserved raw score, not clean Tier 2 proof by itself.
- Solo Failure Factory Holo failure lanes and patch-validation lanes: internal architecture/debug evidence only unless separately promoted under a clean denominator rule.

## 6. Claim Boundary

Public-safe claims:

- "The current strict public denominator is the blind Holo lane: 120 packets, 60 ALLOW and 60 ESCALATE."
- "Holo scored 120/120 on that strict blind lane."
- "The Phase 1 target is 762 clean balanced packets: 381 ALLOW and 381 ESCALATE."
- "The old 614-packet denominator is historical/stale for current public denominator accounting unless re-admitted under the current strict rule."
- "Wilson upper bounds describe uncertainty after observing zero misses; they do not prove the true error rate is zero."

Internal-only claims:

- Solo Failure Factory totals and seam counts.
- V5 Tier 1 patch-validation pass.
- V5 Tier 2 raw 13/14, quarantine, replacement supplement, and merged clean internal gate.
- Tier 3 internal readiness after the replacement pair, subject to its own controls.

Forbidden claims:

- "The current public denominator is 614."
- "The old 614 and blind-120 can be combined for public FPR/FNR."
- "The Solo Failure Factory is public benchmark evidence."
- "V5 Tier 1 or Tier 2 proves global FPR/FNR."
- "Tier 2 rescue evidence proves FP precision."
- "The merged V5 Tier 2 internal gate is a public benchmark result."
- "HoloVerify has proven production reliability."
- "HoloVerify has zero true error rate."
- "HoloVerify beats all models."
- "Parse/admissibility-only failures are wrong-verdict failures."
- "Quarantined packet/key defects can stay in clean denominators."

## Source Map

- Blind packet freeze: `docs/benchmark/HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_2026_07_03.json`
- Blind Holo score checkpoint: `docs/benchmark/HOLOVERIFY_BLIND_120_BATCH001_012_POSTHOC_SCORE_CHECKPOINT_2026_07_03.json`
- Blind batch execution lock: `docs/benchmark/HOLOVERIFY_BLIND_120_BATCH_EXECUTION_LOCK_2026_07_03.md`
- Solo Failure Factory scoreboard: `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_MASTER_SCOREBOARD_2026_07_04.json`
- Tier 1 claim-boundary patch: `docs/benchmark/HOLOVERIFY_V5_TIER1_POSTHOC_CLAIM_BOUNDARY_PATCH_2026_07_04.json`
- Tier 2 denominator audit: `docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_DENOMINATOR_AUDIT_2026_07_04.json`
- Tier 2 packet defect review: `docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_PACKET_DEFECT_REVIEW_2026_07_04.json`
- Tier 2 replacement rollup: `docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_REPLACEMENT_PAIR_LIVE_ROLLUP_2026_07_04.json`
- Tier 2 merged gate update: `docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_MERGED_GATE_UPDATE_2026_07_04.json`
- Tier 2 replacement accounting rule: `docs/benchmark/HOLOVERIFY_V5_TIER2_REPLACEMENT_PAIR_ACCOUNTING_RULE_2026_07_04.json`
