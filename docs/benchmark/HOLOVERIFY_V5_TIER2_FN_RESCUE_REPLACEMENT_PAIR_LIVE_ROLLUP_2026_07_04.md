# HoloVerify V5 Tier 2 Replacement Pair Live Rollup

Status: `REPLACEMENT_PAIR_PASSED`

Date: 2026-07-04

This file summarizes the replacement-pair run for the quarantined Tier 2 pair `HVSF-FACTORY14F-017`.

## Runtime

- Lane: `HOLOVERIFY_V5_TIER2_FN_RESCUE_REPLACEMENT_PAIR_V0`
- Run folder: `docs/benchmark/holoverify_v5_tier2_fn_rescue_replacement_pair_2026_07_04/live_runs/run_20260704T074130Z`
- Provider calls: `10/10`
- Provider failures: `0`
- Solo calls: `0`
- Judge calls: `0`
- Scoring map before trace freeze: `NO`
- Mixed registration JSON before trace freeze: `NO`
- Substitutions: `0`

## Score

- Packets: `2/2`
- Complete pairs: `1/1`
- ALLOW sibling: `PASS`
- ESCALATE sibling: `PASS`

The replacement pair fixed the denominator defect in the original `HVSF-FACTORY14F-017` pair by making `current_cycle=2026-Q3` visible in the runtime sources.

## Claim Boundary

Allowed internal claim:

`V5 replacement pair for quarantined HVSF-FACTORY14F-017 passed on 2/2 packets after blind runtime execution and post-freeze scoring.`

Forbidden:

- No public benchmark claim.
- No global false-negative-rate claim.
- No false-positive precision claim.
- No claim outside this replacement pair.
- No claim before independent audit reviews trace and scorer.

