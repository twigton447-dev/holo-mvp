# HoloVerify Fable Seam Bank 40-Design Rollup

Status: `DISCOVERY_ROLLUP_NO_PROVIDERS`

Date: `2026-07-03`

## What Exists

Fable has produced two seam-design banks:

| Bank | Source file | Pair count | Main thesis |
| --- | --- | ---: | --- |
| Batch 1 | `FABLE_SEAM_MINING_20_PAIR_DESIGNS_2026_07_03.md` | `20` | Human-pressure false positives + provenance false negatives |
| Batch 2 | `FABLE_SEAM_HUNTER_20_NEW_PAIRS_2026_07_03.md` | `20` | Non-human-alarm false positives + unit/coordinate/arithmetic false negatives |

Total banked designs: `40` sibling-pair designs.

These are discovery designs, not benchmark-credit packets.

## Batch 1 Thesis

Batch 1 expands the original `004-A` and `001-B` seams:

- hard-ALLOW false positives where a valid action is surrounded by human pressure, urgency, executive demand, patient impact, stale flags, ambient news, or BEC-looking surfaces.
- hard-ESCALATE false negatives where a calm packet hides a provenance, channel, evidence-binding, revision, identity, or arithmetic gap.

First scout was V3 Fable subset:

- `HV-ATLAS-DISC-011`
- `HV-ATLAS-DISC-013`
- `HV-ATLAS-DISC-016`
- `HV-ATLAS-DISC-020`

V3 result:

- `24/24` provider calls
- `0` provider failures
- `2/4` strict candidates
- `2` wrong verdicts

## Batch 2 Thesis

Batch 2 deliberately shifts the mining thesis:

1. **False-positive vein:** from human pressure to non-human alarms.
   - duplicate-payment system alerts
   - after-hours monitoring flags
   - velocity anomalies
   - anonymous tips with wrong case numbers
   - legal-hold banners with limited scope
   - auditor letters about remediated findings

2. **False-negative vein:** from callback provenance to unit blindness.
   - EUR vs USD with identical numerals
   - timezone conversion
   - role-code inflation
   - homonym entities
   - wrong insurance type
   - remaining-balance arithmetic
   - dual-control identity collapse

Fable's intended first scout:

- `NFP-2`
- `NFP-9`
- `NFN-1`
- `NFN-2`
- `NFN-8`

## V4 Result, Preserved

V4 was a provisional Fable-inspired scout built from Taylor's summary before the full Batch-2 file was reconciled.

It produced strong signal:

- `30/30` provider calls
- `0` provider failures
- `4/5` strict candidates
- `8/30` wrong-verdict solo outputs
- `2` all-three false-positive solo collapses

But V4 should not be described as the exact Fable Batch-2 first scout because its NFP mapping drifted:

- it tested after-hours under `NFP-2`
- it tested BEC/rebrand under `NFP-9`
- it did not test Fable's exact duplicate-payment installment `NFP-2`

V4 run artifact:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/solo_scout_3mini_v4_fable_bank/run_20260703T062121Z/three_mini_seam_summary.md`

## V5 Corrective Scout

V5 is the exact Fable Batch-2 first scout under fresh local IDs:

| Fable ID | V5 local pair | Seam |
| --- | --- | --- |
| `NFP-2` | `HV-ATLAS-DISC-026` | Duplicate-payment alert on legitimate installment billing |
| `NFP-9` | `HV-ATLAS-DISC-027` | After-hours flag on scheduled batch |
| `NFN-1` | `HV-ATLAS-DISC-028` | EUR vs USD identical numerals |
| `NFN-2` | `HV-ATLAS-DISC-029` | Timezone conversion across approval window |
| `NFN-8` | `HV-ATLAS-DISC-030` | Refund exceeding remaining balance |

V5 local validation:

- `py_compile`: `PASS`
- preflight: `PASS`
- pairs: `5`
- packets: `10`
- ALLOW truths: `5`
- ESCALATE truths: `5`
- expected calls: `30`
- provider calls so far: `0`
- Holo / Gov / judge calls: `0 / 0 / 0`

V5 handoff:

- `HOLOVERIFY_ATLAS_DISCOVERY_V5_FABLE_BATCH2_EXACT_LIVE_SCOUT_HANDOFF_2026_07_03.md`

## Recommended Next Move

Run V5 only if Taylor approves the exact provider sentence in the V5 handoff.

If V5 bites:

1. promote the strongest seams into a freeze-ready packet plan,
2. ask Fable to design sibling variants around the strongest collapse class,
3. only then decide whether to run Holo rescue on the discovered seams.

If V5 does not bite:

1. preserve the 0/3 results as taxonomy feedback,
2. keep V4's false-positive overblocking vein as the active seam,
3. ask Fable to mine more non-human-alarm variants around executed controls and scope-limited warnings.

