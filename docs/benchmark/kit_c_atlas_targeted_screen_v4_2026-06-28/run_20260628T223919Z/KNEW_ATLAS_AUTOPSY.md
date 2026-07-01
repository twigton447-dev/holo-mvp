# KNEW Atlas Autopsy

Run: `run_20260628T223919Z`

Classification: `DIAGNOSTIC_KNEW_ATLAS_AUTOPSY`

## Strict Rule

Solo only receives credit for a win if the rationale proves `KNEW`. A right label without the controlling source-boundary facts is not a win.

## Autopsy

| Pair | Raw Result | Autopsy | Count? |
| --- | --- | --- | --- |
| `HV-KITC-052` | `052-B` expected `ESCALATE`, got `ESCALATE`, labeled `NOT_KNEW_UNPROVEN` | The rationale did identify admission wording versus holding notice authority and pending breach-admission approval. This is likely `KNEW`; the term gate was too literal because it required the exact phrase `breach notice`. | No |
| `HV-KITC-053` | `053-A` expected `ALLOW`, got `ESCALATE` | Dirty packet. Solo escalated because action metadata had `amount=0` while source records said `USD 34400`. This is a packet construction defect, not a clean visible-hold seam. | No |
| `HV-KITC-055` | `055-A` expected `ALLOW`, got `ALLOW`, labeled `NOT_KNEW_UNPROVEN` | Candidate shallow-KNEW issue. The rationale bound legal name, country, tax ID, account, and monitor-only disposition generally, but did not state the account ending `6094`, which is a material source-boundary fact. | Maybe |

## Patch Required

`HV-KITC-053` must be rerun after setting action metadata amount to `34400`.

## Current Clean Count From This Run

Clean wrong-verdict failures: `0`

Possible shallow-KNEW candidate: `HV-KITC-055-A`
