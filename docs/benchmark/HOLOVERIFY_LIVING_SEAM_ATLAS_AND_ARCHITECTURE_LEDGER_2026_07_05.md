# HoloVerify Living Seam Atlas And Architecture Ledger

Date: 2026-07-05

Callsign: HoloStats

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
| Internal directional rescue work | Validate V5/V6 behavior on selected solo-failure rescue seams | Internal-only; not public FPR/FNR or benchmark denominator | V6 Tier 3 selected-lane rerun completed and passed internal repair gate; future live work needs separate explicit approval |
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
- Tier 3 FN V5 status: authorized live run completed and failed the selected gate.
- Tier 3 V5 scope: internal directional FN rescue only; not public benchmark evidence and not a global FNR claim.

Tier 3 FN eligibility audit:

| Metric | Count |
|---|---:|
| Clean promoted FN pairs currently eligible | 8 |
| Tier 3 target clean FN pairs | 7 |
| Deficit | 0 |

Tier 3 FN Holo rescue was unlocked for runtime-package build because the eligible clean FN pool met the 7-pair target. The later V5 live run completed under authorization and failed the selected gate; future V6 rerun or expansion still requires separate explicit provider approval.

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

Tier 3 V5 FN Holo rescue live run:

| Metric | Value |
|---|---|
| Classification | `AUTHORIZED_RUNTIME_VALID_SELECTED_GATE_FAILED` |
| Run folder | `docs/benchmark/holoverify_tier3_fn_holo_rescue_2026_07_05/live_runs/run_20260704T195236Z` |
| Provider calls | 70/70 |
| Provider failures | 0 |
| Runtime controls | Trace frozen before scoring; scoring map loaded post-freeze |
| Packet score | 12/14 |
| Pair score | 5/7 |
| Failed packets | `HVSF-FACTORY16-008-B`, `HVSF-FACTORY16-019-B` |

Tier 3 V5 FN Holo rescue is failed-live internal evidence. It is not a Holo win, not public benchmark evidence, not a global FNR claim, and not FP precision evidence.

V6 tiny scope-dependency patch-validation:

| Metric | Value |
|---|---|
| Classification | `V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_PASSED` |
| Commit | `dcf44cd2b benchmark: preserve v6 scope dependency patch validation` |
| Valid scored run | `docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/live_runs/run_20260705T014301Z` |
| Failed DNS/network attempt | `docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/live_runs/run_20260705T014145Z` preserved separately and excluded from scoring |
| Valid-run provider calls | 20/20 |
| Valid-run provider failures | 0 |
| Post-hoc score | 4/4 packets, 2/2 pairs |
| Scope | Internal patch-validation only |

V6 meaning:

- V6 patches deterministic source-field authority/scope dependency detection.
- It addresses the Tier 3 V5 miss class: `V5_SCOPE_DEPENDENCY_NON_DETECTION`.
- The same selected Tier 3 lane that failed under V5 now passes under V6.
- It does not yet make a broad benchmark claim.

V6 Tier 3 FN Holo rescue rerun:

| Metric | Value |
|---|---|
| Classification | `V6_TIER3_FN_HOLO_RESCUE_RERUN_SELECTED_LANE_REPAIR_PASSED` |
| Commit | `5c6e70063 benchmark: preserve v6 tier3 fn rerun evidence` |
| Run folder | `docs/benchmark/holoverify_v6_tier3_fn_holo_rescue_rerun_2026_07_05/live_runs/run_20260705T023842Z` |
| Provider calls | 70/70 |
| Provider failures | 0 |
| Route | `W1 -> G1 -> W2 -> G2 -> W3` x14 |
| Packet score | 14/14 |
| Pair score | 7/7 |
| Failed packets | `[]` |
| V5 prior result for same selected lane | 12/14 packets, 5/7 pairs |
| V6 repair result for same selected lane | 14/14 packets, 7/7 pairs |
| Scope | Internal selected-lane repair evidence only |

Current scorecard:

- Strict public denominator remains blind-120 only.
- Old `614` remains stale/historical.
- Tier 3 V5 FN rescue remains failed-live evidence: 12/14 packets and 5/7 pairs.
- V6 tiny validation passed on 4 packets / 2 pairs.
- V6 Tier 3 FN rerun passed on the same selected lane: 14/14 packets and 7/7 pairs.
- This supports the engineering hardening story, not a public reliability denominator.

## 5. Wave 1 Stress Matrix And V7 Status

Wave 1 solo scout:

| Metric | Value |
|---|---:|
| Evidence commit | `ef4d72c62` |
| Pairs | 20 |
| Packets | 40 |
| Solo calls | 120 |
| Green dots | 90 |
| Red dots | 30 |
| False positives | 23 |
| False negatives | 0 |
| Parse/admissibility failures | 7 |
| Pairs with at least one red | 16/20 |
| Wrong-verdict pairs | 13 |
| Parse-only holdouts | 3 |

Wave 1 is internal stress-matrix seam discovery only. It is not public benchmark evidence, not a global FPR/FNR denominator, and not natural production-rate evidence.

Wave 1 Top 5 FP-overblock Holo rescue:

| Metric | Value |
|---|---|
| Evidence commit | `ae5227c47` |
| Provider calls | 50/50 |
| Provider failures | 0 |
| Packet score | 7/10 |
| Pair score | 2/5 |
| Failed packets | `HVSM-W1-009-A`, `HVSM-W1-011-A`, `HVSM-W1-019-A` |
| Failure class | `FALSE_BLOCKER_CREATED_AND_PRESERVED_ON_ALLOW_PACKET` |
| Status | failed internal hardening evidence only |

The failed rescue is preserved as internal hardening evidence. It is not a Holo win, not public benchmark evidence, not a global FPR/FNR claim, not FP precision evidence, and not natural production-rate evidence.

V7 hardening:

| Metric | Value |
|---|---|
| Hardening commit | `573d21fa248691b9248f380240a61acba0228290` |
| Selector | `SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05` |
| Selector hash | `f653240e87b1062dfca2b651cae846459ccb524820803d6386cc0dddc808b71d` |
| Fable final verdict | PASS |
| HoloArchitecture post-commit | PASS |
| HoloStats | PASS |
| No-provider validation | 101 passed; architecture rerun 84 passed |
| Claim boundary | internal hardening only |

V7 adds deterministic false-blocker suppression and affirmative closure handling for the Wave 1 false-blocker-preservation failure class. This hardening is not public benchmark evidence and does not create a live validation result by itself.

V7 tiny preflight:

| Metric | Value |
|---|---|
| Preflight commit | `1d3ab6ec3af18b6ea1d7c21386e67a5e5b127c89` |
| Runtime manifest hash | `f1f55f0c5b69f8bffa9c9a770f1b21a845e51e7bab5b810156f799175e213db8` |
| Package status | committed |
| Pre-live HoloArchitecture | PASS |
| Expected calls | 30 |
| Status | preflight ready |

V7 live attempt:

| Metric | Value |
|---|---|
| Blocked-attempt note commit | `f975e2e00541a124f5c288a875c0b01122d54768` |
| Status | `LIVE_EXECUTION_BLOCKED_BY_POLICY_BEFORE_PROVIDER_CALLS` |
| Actual calls | 0 |
| Live run folder | none |
| `TRACE_PROVIDER_CALLS.jsonl` | absent |
| Raw provider outputs | absent |
| Scoring | not run |
| Live validation result | none |

The blocked live attempt is an operational policy block before provider contact. It is not a failed Holo run, not a failed model run, and not a rescue result.

Current V7 public claim boundary:

- Strict public denominator remains blind-120 only.
- There is no V7 public benchmark evidence.
- There is no V7 Holo win.
- There is no V7 global FPR/FNR claim.
- There is no V7 FP precision claim.
- There is no V7 production safety certification.

## 6. Quarantine Register

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
- Tier 3 V5 FN Holo rescue live run: authorized and runtime-valid but selected-gate failed; internal failed rescue evidence only.
- V6 tiny patch-validation: internal patch-validation only; not public benchmark evidence.
- V6 Tier 3 FN rerun: internal selected-lane repair evidence only; not public benchmark evidence.
- Wave 1 solo scout: internal stress-matrix seam discovery only; not public benchmark evidence or natural production-rate evidence.
- Wave 1 Top 5 FP-overblock Holo rescue: failed internal hardening evidence only; not a Holo win or public benchmark evidence.
- V7 tiny preflight: preflight-ready package only; no live validation result exists.
- V7 blocked live attempt: policy block before provider contact; no provider calls, no raw outputs, no scoring, and no live validation result.

## 7. Claim Boundary

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
- Tier 3 V5 FN Holo rescue completed as an authorized runtime-valid selected-gate failure: 12/14 packets and 5/7 pairs.
- V6 tiny scope-dependency patch-validation passed on 4/4 packets and 2/2 pairs.
- V6 addresses the Tier 3 V5 miss class `V5_SCOPE_DEPENDENCY_NON_DETECTION` within the tiny patch-validation lane and the same selected Tier 3 rerun lane.
- V6 Tier 3 FN rerun passed on the same selected lane that failed under V5: 14/14 packets and 7/7 pairs.
- Tier 3 targeted-mining solo scout found 2 useful FN pairs, `T3FN-MINE-006` and `T3FN-MINE-010`, for internal directional mining only.
- Tier 3 targeted-mining solo Scout 2 found 1 useful FN pair, `T3FN2-MINE-003`, for internal directional mining only.
- Tier 3 targeted-mining solo Scout 3 promoted 2 FN candidates, `T3FN3-MINE-003` and `T3FN3-MINE-009`, for internal directional mining only.
- Any future 7-pair / 14-packet full HoloGov Tier 3 FN rerun expects 70 provider calls: W1 x14, G1 x14, W2 x14, G2 x14, W3 x14.
- Wave 1 solo scout found 90 green and 30 red solo attempts across 20 stress-selected pairs / 120 solo calls, for internal seam discovery only.
- Wave 1 Top 5 FP-overblock Holo rescue completed with 50/50 provider calls and failed at 7/10 packets and 2/5 pairs, with failure class `FALSE_BLOCKER_CREATED_AND_PRESERVED_ON_ALLOW_PACKET`.
- V7 hardening is committed internal hardening for false-blocker suppression, with selector `SELECTOR_V7_FALSE_BLOCKER_SUPPRESSION_2026_07_05`.
- V7 tiny preflight is package-ready with expected 30 calls, but no live validation result exists.
- The V7 live attempt was blocked by policy before provider calls; actual calls were 0.

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
- "Future Tier 3 FN or V6 rescue runs may run live without separate explicit approval."
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
- "The V6 tiny patch-validation pass is public benchmark evidence."
- "The V6 tiny patch-validation pass proves global FNR or FP precision."
- "The V6 Tier 3 selected-lane rerun is public benchmark evidence."
- "The V6 Tier 3 selected-lane rerun proves global FNR or FP precision."
- "The V6 Tier 3 selected-lane rerun proves general model superiority."
- "V6 has been validated broadly beyond the tiny patch-validation and selected-lane rerun evidence."
- "Wave 1 solo scout is public benchmark evidence."
- "Wave 1 solo scout proves global FPR/FNR or natural production-rate prevalence."
- "Wave 1 Top 5 FP-overblock rescue is a Holo win."
- "Wave 1 Top 5 FP-overblock rescue proves FP precision."
- "V7 hardening is public benchmark evidence."
- "V7 hardening is a Holo win."
- "V7 tiny preflight is a live validation result."
- "The V7 blocked live attempt is a failed Holo run or failed model run."
- "V7 proves global FPR/FNR, FP precision, production safety, or general model superiority."

## 8. Plain-English Status For Taylor

What is proven:

- The strict public scorecard is still the blind-120 lane: 120/120 packets, balanced 60 ALLOW and 60 ESCALATE.
- V5 found the selected-lane failure: the Tier 3 FN rescue run was real, authorized, and runtime-valid, but it failed at 12/14 packets and 5/7 pairs.
- V6 patched the failure class and the same selected Tier 3 lane now passes at 14/14 packets and 7/7 pairs.
- Wave 1 exposed an FP-overblock seam where Holo V6 still failed on 3 ALLOW siblings in the Top 5 rescue lane.
- V7 hardening was implemented and passed no-provider validation, but the live V7 attempt was blocked before any provider calls.

What is not proven:

- V6 has not yet proved a broad benchmark improvement.
- V6 has not created a new public denominator.
- V6 has not proved global FNR reduction, FP precision, or general HoloVerify superiority.
- V7 has not produced a live validation result.
- V7 has not created public benchmark evidence, a Holo win, global FPR/FNR evidence, FP precision evidence, or production safety certification.

What changed with V6:

- The deterministic layer now checks the source-field authority/scope dependency that V5 missed on the two Tier 3 B-side failures.
- The tiny validation passed first, then the full same-set Tier 3 rerun passed under V6.
- This supports the engineering hardening story, not a public reliability denominator.
- V7 is the next hardening step for false blockers created and preserved on ALLOW packets.
- The current environment blocked the live V7 run before provider contact, so the V7 state is preflight-ready plus no-provider-tested, not live-validated.

Next two possible moves:

- Build a broader V6 validation set first, so the next live run tests the patch beyond the two known miss pairs.
- Keep Phase 1 strict public denominator work separate and continue only with clean blind/balanced packets.
- If V7 live validation is still desired, move it to an approved environment or process that is allowed to export the runtime packet contents to providers.

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
- Tier 3 V5 FN accounting correction: `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_ACCOUNTING_CORRECTION_2026_07_05.json`
- Tier 3 V5 FN live rollup: `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_LIVE_ROLLUP_2026_07_05.json`
- V6 patch report: `docs/benchmark/HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_PATCH_REPORT_2026_07_05.json`
- V6 tiny preflight: `docs/benchmark/HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_PREFLIGHT_2026_07_05.json`
- V6 tiny post-live architecture audit: `docs/benchmark/HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_POSTLIVE_ARCHITECTURE_AUDIT_2026_07_05.json`
- V6 tiny valid scored run: `docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/live_runs/run_20260705T014301Z`
- V6 tiny failed DNS/network attempt: `docs/benchmark/holoverify_v6_scope_dependency_gate_tiny_patch_validation_2026_07_05/live_runs/run_20260705T014145Z`
- V6 Tier 3 rerun preflight: `docs/benchmark/HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_PREFLIGHT_2026_07_05.json`
- V6 Tier 3 rerun runtime-only manifest: `docs/benchmark/HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- V6 Tier 3 rerun scored run: `docs/benchmark/holoverify_v6_tier3_fn_holo_rescue_rerun_2026_07_05/live_runs/run_20260705T023842Z`
- Wave 1 solo scout rollup: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_ROLLUP_2026_07_05.json`
- Wave 1 solo scout run: `docs/benchmark/holoverify_stress_matrix_expansion_wave1_solo_scout_runs_2026_07_05/run_20260705T215904Z`
- Wave 1 FP-overblock rescue provenance audit: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_WAVE1_FP_OVERBLOCK_HOLO_RESCUE_PROVENANCE_AUDIT_2026_07_05.json`
- Wave 1 FP-overblock rescue failure autopsy: `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_WAVE1_FP_OVERBLOCK_HOLO_RESCUE_FAILURE_AUTOPSY_2026_07_05.json`
- Wave 1 FP-overblock rescue scored run: `docs/benchmark/holoverify_stress_matrix_wave1_fp_overblock_holo_rescue_2026_07_05/live_runs/run_20260705T232606Z`
- V7 hardening patch report: `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_PATCH_REPORT_2026_07_05.json`
- V7 hardening design: `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_DESIGN_2026_07_05.json`
- V7 tiny preflight: `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_PREFLIGHT_2026_07_05.json`
- V7 tiny runtime-only manifest: `docs/benchmark/HOLOVERIFY_V7_FALSE_BLOCKER_SUPPRESSION_TINY_PATCH_VALIDATION_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- V7 blocked live-attempt operational note: `docs/benchmark/HOLOVERIFY_V7_TINY_PATCH_VALIDATION_LIVE_ATTEMPT_BLOCKED_OPERATIONAL_NOTE_2026_07_06.json`
