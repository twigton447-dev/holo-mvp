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

Phase 1 workstreams:

| Workstream | Purpose | Denominator treatment | Provider approval status |
|---|---|---|---|
| Strict public denominator work | Build clean balanced ALLOW/ESCALATE packets toward 762 total | Public denominator only after freeze, clean runtime controls, and trace-bound scoring | Requires separate explicit approval per run |
| Internal directional rescue work | Validate V5 behavior on selected solo-failure rescue seams | Internal-only; not public FPR/FNR or benchmark denominator | Tier 3 FN package build is accounting-safe after Scout 3 promotion review; live providers require separate explicit approval |
| Seam mining work | Find and audit new FN_FALSE_ALLOW / FP_OVERBLOCK candidates | Candidate discovery only; no denominator credit by itself | No provider approval from mining artifacts alone |

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
- Tier 2 gate result: unlocked only as an internal directional FN_FALSE_ALLOW rescue expansion gate.
- Tier 3 FN build status: `UNLOCKED_ACCOUNTING_SAFE_TO_BUILD_RUNTIME_PACKAGE`.
- Tier 3 live provider approval status: not granted by this ledger update.

Tier 3 FN eligibility audit:

| Metric | Count |
|---|---:|
| Clean promoted FN pairs currently eligible | 8 |
| Tier 3 target clean FN pairs | 7 |
| Deficit | 0 |

Tier 3 FN Holo rescue is unlocked for runtime-package build because the eligible clean FN pool now meets or exceeds the 7-pair target. A live run still requires separate explicit provider approval.

Expected full HoloGov call count for a 7-pair Tier 3 FN package:

| Route slot | Calls |
|---|---:|
| W1 | 14 |
| G1 | 14 |
| W2 | 14 |
| G2 | 14 |
| W3 | 14 |
| Worker calls | 42 |
| Gov calls | 28 |
| Total provider calls | 70 |

Accounting rule: build exactly 7 clean FN pairs / 14 packets unless a separate plan updates the denominator and provider-call math. An 8-pair run would require a new accounting plan.

Tier 3 targeted-mining solo scout:

| Metric | Count |
|---|---:|
| Solo provider calls completed | 60/60 |
| Provider failures | 0 |
| KNEW_ADMISSIBLE | 58/60 |
| FALSE_NEGATIVE_ALLOW_ON_ESCALATE | 2/60 |
| False positives | 0 |
| Parse/admissibility failures | 0 |

New useful FN pairs from targeted mining:

- `T3FN-MINE-006`
- `T3FN-MINE-010`

This scout updates the internal clean FN pool from 3 pairs to 5 pairs. It remains internal directional mining only; it is not public benchmark evidence and does not create a global FNR claim.

Tier 3 targeted-mining solo scout 2:

| Metric | Count |
|---|---:|
| Solo provider calls completed | 60/60 |
| Provider failures | 0 |
| KNEW_ADMISSIBLE | 59/60 |
| FALSE_NEGATIVE_ALLOW_ON_ESCALATE | 1/60 |
| False positives | 0 |
| Parse/admissibility failures | 0 |

New useful FN pair from Scout 2:

- `T3FN2-MINE-003`

Scout 2 updates the internal clean FN pool from 5 pairs to 6 pairs. Tier 3 target remains 7 clean FN pairs, leaving a deficit of 1. This remains internal directional mining only; it is not public benchmark evidence and does not create a global FNR claim.

Tier 3 targeted-mining solo Scout 3:

| Metric | Count |
|---|---:|
| Solo provider calls completed | 60/60 |
| Provider failures | 0 |
| KNEW_ADMISSIBLE | 58/60 |
| FALSE_NEGATIVE_ALLOW_ON_ESCALATE | 2/60 |
| False positives | 0 |
| Parse/admissibility failures | 0 |

Promoted Scout 3 FN candidates:

- `T3FN3-MINE-003`
- `T3FN3-MINE-009`

Scout 3 promotion updates the internal clean FN pool from 6 pairs to 8 pairs. Tier 3 target remains 7 clean FN pairs, leaving a deficit of 0. This unlocks Tier 3 FN Holo rescue for runtime-package build only; it remains internal directional FN rescue, not public benchmark evidence and not a global FNR claim.

## 5. Quarantine Register

Packet/key defects:

| Item | Status | Reason | Denominator treatment |
|---|---|---|---|
| `HVSF-FACTORY14F-017-B` | `PACKET_KEY_DEFECT_CANDIDATE` | Runtime-visible sources omitted explicit `current_cycle=2026-Q3` needed by key | Excluded from clean packet denominator; entire pair excluded from clean pair denominator |
| `HVSF-FACTORY13X-002` / `HVSF-FACTORY13X-002-A` | quarantine recommended | Likely packet/key defect: ALLOW unsupported by visible sources | Exclude pending review |

Tier 3 FN exclusions:

- `HVSF-FACTORY14F-017`: excluded from the clean Tier 3 FN pool because the original B packet is a packet/key defect candidate; the replacement pair is Tier 2 supplement accounting, not a fresh Tier 3 candidate.
- `HVSF-FACTORY13X-002`: excluded pending quarantine review because the ALLOW key appears unsupported by visible sources.
- `HVSF-FACTORY-001`: excluded from fresh Tier 3 FN rescue because the current readiness audit treats it as patch-validation-only, not fresh rescue evidence.

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
- Tier 2 internal gate restoration after replacement pair.
- Tier 3 FN status is accounting-safe to build as a 7-pair / 14-packet runtime package after Scout 3 promotion review.
- Tier 3 targeted-mining solo scout found 2 useful FN pairs, `T3FN-MINE-006` and `T3FN-MINE-010`, for internal directional mining only.
- Tier 3 targeted-mining solo Scout 2 found 1 useful FN pair, `T3FN2-MINE-003`, for internal directional mining only.
- Tier 3 targeted-mining solo Scout 3 promoted 2 FN candidates, `T3FN3-MINE-003` and `T3FN3-MINE-009`, for internal directional mining only.
- A 7-pair / 14-packet full HoloGov Tier 3 FN package expects 70 provider calls: W1 x14, G1 x14, W2 x14, G2 x14, W3 x14.

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
- "Tier 3 FN provider approval is allowed now."
- "Tier 3 FN Holo rescue may run live without separate explicit approval."
- "Tier 3 FN rescue is public benchmark evidence."
- "Tier 3 FN rescue proves global FNR."
- "An 8-pair Tier 3 FN run can use the 70-call plan."
- "The Tier 2 replacement supplement creates a fresh Tier 3 candidate."
- "Five clean promoted FN pairs satisfy the seven-pair Tier 3 target."
- "The targeted-mining solo scout is public benchmark evidence."
- "The targeted-mining solo scout proves global FNR."
- "Scout 2 is public benchmark evidence."
- "Scout 2 proves global FNR."
- "Six clean promoted FN pairs satisfy the seven-pair Tier 3 target."
- "Scout 3 is public benchmark evidence."
- "Scout 3 proves global FNR."

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
- Tier 3 FN readiness audit: `docs/benchmark/HOLOVERIFY_TIER3_FN_RESCUE_CANDIDATE_READINESS_2026_07_05.json`
- Tier 3 targeted-mining solo scout rollup: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_SOLO_ROLLUP_2026_07_05.json`
- Tier 3 targeted-mining solo scout rollup memo: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_SOLO_ROLLUP_2026_07_05.md`
- Tier 3 targeted-mining Scout 2 solo rollup: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT2_SOLO_ROLLUP_2026_07_05.json`
- Tier 3 targeted-mining Scout 2 solo rollup memo: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT2_SOLO_ROLLUP_2026_07_05.md`
- Tier 3 FN rescue eligibility audit: `docs/benchmark/HOLOVERIFY_TIER3_FN_RESCUE_ELIGIBILITY_AUDIT_2026_07_05.json`
- Tier 3 FN rescue eligibility audit memo: `docs/benchmark/HOLOVERIFY_TIER3_FN_RESCUE_ELIGIBILITY_AUDIT_2026_07_05.md`
- Tier 3 targeted-mining Scout 3 solo rollup: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT3_SOLO_ROLLUP_2026_07_05.json`
- Tier 3 targeted-mining Scout 3 solo rollup memo: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT3_SOLO_ROLLUP_2026_07_05.md`
