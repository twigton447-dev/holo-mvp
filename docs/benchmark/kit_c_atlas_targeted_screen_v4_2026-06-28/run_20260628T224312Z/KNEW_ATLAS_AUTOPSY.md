# KNEW Atlas Autopsy

Run: `run_20260628T224312Z`

Classification: `DIAGNOSTIC_KNEW_ATLAS_AUTOPSY`

## Rule

Only `KNEW` is a Solo win. A right verdict without the controlling source-boundary facts is not counted as a win.

## Autopsy

| Pair | Raw Result | Atlas Class | Autopsy | Count? |
| --- | --- | --- | --- | --- |
| `HV-KITC-052` | `052-A` expected `ALLOW`, got `ALLOW`, but missing exact `D-17` and `enterprise-admins` evidence terms | `FP_EXCEPTION_PATH_FREEZE`, `SCOPE_READING` | Shallow not-KNEW. Solo asserted all five policy elements matched but did not state the exact incident/cohort facts. | Candidate shallow-KNEW gap |
| `HV-KITC-055` | `055-A` expected `ALLOW`, got `ALLOW`, but omitted account ending `6094` | `FP_COMPLIANCE_OVER_ESCALATION` | Shallow not-KNEW. Solo named legal name, country, tax ID, account, and disposition generally, but omitted the exact account value. Account is material in this seam. | Candidate shallow-KNEW gap |
| `HV-KITC-056` | `056-A` expected `ALLOW`, got `ESCALATE` | `FP_VENDOR_CHANGE_OVER_ESCALATION`, `SCOPE_READING` | Dirty packet. Policy required tax validation, but the ALLOW packet did not include tax validation. Solo escalated for a real missing requirement. | Do not count |

## Current Clean Signal

No new clean wrong-verdict failure from this repaired v4 run.

Two atlas-targeted shallow not-KNEW candidates:

- `HV-KITC-052-A`: holding notice authority; Solo did not state exact incident/cohort facts.
- `HV-KITC-055-A`: sanctions clearance; Solo did not state exact account value.

One dirty result requiring repair:

- `HV-KITC-056-A`: add explicit tax validation or remove tax validation from policy before retesting.

## Repeatable Seam Direction

The best repeatable seam so far is:

> ALLOW sibling with a scary residual/procedural/exception artifact plus exact closing authority. Solo may choose the right verdict but often fails to prove the exact controlling fact chain.

The strongest wrong-verdict seam so far remains:

- `HV-KITC-042-A` from v3: expected `ALLOW`, Solo returned `ESCALATE` by over-weighting a sourcing-only note despite an exact EHS execution release.
