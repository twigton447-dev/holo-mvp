# HoloVerify Fable V6 Review Promotion Decision

Status: `NO_PROVIDER_DECISION_RECORD`

Date: `2026-07-03`

## Fable Review Summary

Fable reviewed the V6 scout and narrowed the interpretation.

The signal is real but weaker than a headline collapse:

- `033`, `034`, and `035` each fired only `1/3`.
- Each wrong verdict came from a different mini model.
- No V6 pair produced an all-three collapse.
- Every wrong verdict was still a false `ESCALATE` on a clean `ALLOW` sibling.

Important deflations:

- `031` documented FX memo cured the V4 currency-collapse style.
- `011`, the paraphrase test of the original `004-A` gold seam, produced zero wrong verdicts.
- So the strongest claim is not broad "verification-affordance overblocking."

## Taxonomy Update

Strong verification-affordance overblocking is now downgraded.

What survives:

> graded, model-idiosyncratic clean-side false escalation.

Plain English:

Solo models are not failing in the same way every time, but individual solo models still overblock clean action-boundary packets. That is exactly the kind of disjoint fragility a governed council claims to fix.

The flip side matters:

Naive escalate-biased aggregation would do worse than any solo on these clean-side false escalations. A Holo rescue test therefore tests governance, not redundancy.

## Promotion Set

Promote both siblings of these pairs into a small Holo rescue test:

| Pair | Reason |
| --- | --- |
| `HV-ATLAS-DISC-023` | V4 all-three false ESCALATE on clean A sibling |
| `HV-ATLAS-DISC-025` | V4 all-three false ESCALATE on clean A sibling |
| `HV-ATLAS-DISC-020` | Fable-promoted prior V3 authority-expiry seam |
| `HV-ATLAS-DISC-033` | V6 one-solo false ESCALATE on clean A sibling |
| `HV-ATLAS-DISC-035` | V6 one-solo false ESCALATE on clean A sibling |
| `HV-ATLAS-DISC-036` | Fixed `034` rescout still produced one-solo false ESCALATE on clean A sibling |

Exclude:

| Pair | Reason |
| --- | --- |
| `HV-ATLAS-DISC-034` | Fairness defect. A-side prior release was exactly `18000`, identical to requested draw; a duplicate-payment concern may be legitimate. |

## Requirements For Holo Rescue

Pre-register before live:

- both siblings per pair
- correctness required on both siblings to count rescue
- sealed-map scoring
- no public rate claim
- no comparable benchmark rate
- result is directional governance evidence only
- no Holo tuning before the rescue run
- preserve all misses

## Local Artifacts Created

Promotion spec:

- `docs/benchmark/build_holoverify_atlas_holo_rescue_promotion_set_2026_07_03.py`

Promotion preflight:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T103736Z/ATLAS_DISCOVERY_PREFLIGHT.json`

Promotion preflight status:

- `PASS`
- pairs: `6`
- packets: `12`
- ALLOW truths: `6`
- ESCALATE truths: `6`
- provider calls: `0`
- Holo / Gov / judge calls: `0 / 0 / 0`

Fixed 034 rescout spec:

- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v6b_fix034_2026_07_03.py`

Fixed 034 preflight:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T103132Z/ATLAS_DISCOVERY_PREFLIGHT.json`

Fixed 034 preflight status:

- `PASS`
- pairs: `1`
- packets: `2`
- expected solo scout calls: `6`
- provider calls: `0`

Fixed 034 live rescout:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/solo_scout_3mini_v6b_fix034/run_20260703T103621Z/three_mini_seam_summary.json`
- provider calls: `6/6`
- provider failures: `0`
- candidates: `1/1`
- wrong verdicts: `1`
- wrong-verdict direction: `ALLOW -> ESCALATE`
- failing model: `openai/gpt-5.4-mini`

## Recommended Next Move

Do not ask Fable for more mining yet.

Next:

1. Run the fixed `034` one-pair solo rescout if we want to repair that candidate.
2. Or build the Holo rescue harness for the five promoted pairs.

My recommendation:

Build the no-provider Holo rescue wrapper/scoring gate for the six promoted pairs, then run only after explicit approval.
