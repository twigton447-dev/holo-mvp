# HoloVerify Fable V4 Taxonomy and V6 Affordance Scout Plan

Status: `DISCOVERY_PLAN_NO_PROVIDERS`

Date: `2026-07-03`

## What Fable Found In V4

Fable read the V4 trace directly:

- V4 run: `solo_scout_3mini_v4_fable_bank/run_20260703T062121Z`
- provider calls: `30/30`
- provider failures: `0`
- Holo / Gov / judge calls: `0 / 0 / 0`
- strict candidates: `4/5`
- wrong solo verdicts: `8`
- false ESCALATEs: `8`
- false ALLOWs: `0`

The sharp finding is not "unit blindness worked." It did not.

The planted printed unit gaps were caught. The clean siblings collapsed.

## Taxonomy Update

### Falsified Class

`printed_one_join_unit_blindness_FN`

Scope:

- these three mini models
- printed values
- one comparison away
- V4 packet style

Interpretation:

The models did not miss the printed EUR/USD, timezone, or remaining-balance defects on B-siblings. Preserve this as taxonomy knowledge.

### Active Class

`verification_affordance_overblocking`

Plain English:

When a packet contains something that looks checkable, the solo model may treat the mere existence of that check as evidence of a problem, even when the check passes.

Observed triggers now include:

1. human pressure / warning language
2. machine alarms
3. arithmetic or unit-check affordances

Commercial interpretation:

This is a precision problem at the action boundary. Solo agents can block legitimate business because they over-defer to warning-shaped or check-shaped surfaces.

## Discovery Rule

Full three-model collapse is not required.

One wrong solo verdict is enough to count as a scout candidate because the benchmark thesis is solo inconsistency at the action boundary.

Candidate rule remains strict:

1. wrong verdict signal: at least one completed mini output has the wrong verdict, or
2. heavy non-KNEW signal: at least three completed mini outputs are unproven/malformed with failures present on both siblings.

Loose one-off non-KNEW is not enough.

## V6 Scout

Local executable name:

- `build_holoverify_atlas_seam_discovery_minirun_v6_fable_v5_affordance_2026_07_03.py`

Why V6:

Fable calls this design bank `V5`, but the repo already uses local `V5` for the exact Batch-2 reconciliation scout. Local `V6` avoids overwriting history.

Fable top-five mapping:

| Fable design | Local pair | Vein | Purpose |
| --- | --- | --- | --- |
| `V5-1` | `HV-ATLAS-DISC-031` | arithmetic-affordance FP | Documented FX conversion |
| `V5-3` | `HV-ATLAS-DISC-032` | arithmetic-affordance FP | 43-cent mismatch inside $1 tolerance |
| `V5-10` | `HV-ATLAS-DISC-033` | computed FN frontier | 15 percent cap over summed quarterly spend |
| `V5-15` | `HV-ATLAS-DISC-034` | computed FN frontier | depletion across separate release notices |
| `V5-6` | `HV-ATLAS-DISC-035` | executed-control BEC lookalike | acquisition novation / legitimate payee-name change |

## No-Provider Validation

Validation completed:

- `py_compile`: `PASS`
- preflight: `PASS`
- pairs: `5`
- packets: `10`
- ALLOW truths: `5`
- ESCALATE truths: `5`
- expected solo scout calls: `30`
- provider calls: `0`
- Holo calls: `0`
- Gov calls: `0`
- judge calls: `0`
- forbidden model-visible hits: `0`

Preflight artifact:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T063354Z/ATLAS_DISCOVERY_PREFLIGHT.json`

## Next Step

Run V6 only with explicit provider approval.

If V6 bites, promote the strongest candidates into a freeze-ready packet plan.

If V6 does not bite, preserve the negative result as taxonomy feedback and move the scout toward deeper computed-FN hop depth.

