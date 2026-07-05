# HoloVerify Atlas Discovery V4/V5 Reconciliation

Status: `NO_PROVIDER_RECONCILIATION`

Date: `2026-07-03`

## Plain English

The V4 scout result is real and useful, but after the full Fable Batch-2 design file was inspected, the V4 executable was found to be a provisional mapping, not the exact Fable Batch-2 scout.

V4 should stay preserved as discovery evidence:

- `30/30` provider calls completed.
- `0` provider failures.
- `0` Holo / Gov / judge calls.
- `4/5` pairs fired under the strict wrong-verdict rule.
- `2` all-three solo false-positive collapses.

But V4 should not be described as the exact Fable Batch-2 scout because the non-human alarm pair labels drifted.

## What Drifted

Fable Batch-2 intended the first scout to be:

| Fable ID | Intended seam |
| --- | --- |
| `NFP-2` | Duplicate-payment system alert on legitimate installment billing |
| `NFP-9` | After-hours flag on a scheduled batch |
| `NFN-1` | EUR vs USD with identical numerals |
| `NFN-2` | Timezone conversion across approval window |
| `NFN-8` | Refund exceeding remaining balance |

The provisional V4 scout used:

| Local pair | Claimed Fable ID | Actually tested |
| --- | --- | --- |
| `HV-ATLAS-DISC-021` | `NFP-2` | After-hours scheduled batch |
| `HV-ATLAS-DISC-022` | `NFP-9` | BEC/rebrand surface with executed change-control |
| `HV-ATLAS-DISC-023` | `NFN-1` | EUR/USD numerals |
| `HV-ATLAS-DISC-024` | `NFN-2` | Timezone math |
| `HV-ATLAS-DISC-025` | `NFN-8` | Remaining-balance arithmetic |

So V4's unit-blindness results remain aligned with Fable's NFN picks, but V4 did not test Fable's exact `NFP-2` duplicate-payment installment seam.

## Corrective Action

Created an exact Fable Batch-2 scout spec under fresh local IDs:

- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v5_fable_batch2_exact_2026_07_03.py`

Fresh local mapping:

| Fable ID | Local pair | Seam |
| --- | --- | --- |
| `NFP-2` | `HV-ATLAS-DISC-026` | Duplicate-payment alert on legitimate installment billing |
| `NFP-9` | `HV-ATLAS-DISC-027` | After-hours flag on scheduled batch |
| `NFN-1` | `HV-ATLAS-DISC-028` | EUR vs USD identical numerals |
| `NFN-2` | `HV-ATLAS-DISC-029` | Timezone conversion across approval window |
| `NFN-8` | `HV-ATLAS-DISC-030` | Refund exceeding remaining balance |

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
- forbidden model-visible terms: `0`

Preflight artifact:

- `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T062818Z/ATLAS_DISCOVERY_PREFLIGHT.json`

## Claim Boundary

V4 may be described as:

> A provisional Fable-inspired scout that produced strong false-positive collapse signal, especially around unit/arithmetic and warning-shaped artifacts.

V5 may be described as:

> The exact Fable Batch-2 first scout, preflighted locally and ready for explicit provider approval.

Neither V4 nor V5 carries benchmark credit. These are discovery scouts only.

