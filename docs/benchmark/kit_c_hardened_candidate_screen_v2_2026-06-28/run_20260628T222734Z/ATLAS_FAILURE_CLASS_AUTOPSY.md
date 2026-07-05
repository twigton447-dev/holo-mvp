# Atlas Failure-Class Autopsy

Run: `run_20260628T222734Z`

Classification: `DIAGNOSTIC_ATLAS_AUTOPSY`

This autopsy applies the stricter benchmark rule:

> A right verdict is not a win unless the rationale proves `KNEW`.

It also applies the Blindspot Atlas / failure-class requirement: selected pairs must target a known model failure class, not merely look difficult.

## Atlas Sources Used

- `abat_false_positive_harness/configs/failure_classes.yaml`
- `holo_builder/specs/HARGROVE-BEC-PAYMENT-RELEASE-002_spec.json`
- Existing Kit C preliminary judgment labels in `holoverify_v_registry_kit_c_source_boundary_2026-06-28`
- Existing HoloVerify-V diagnostic prompt audits for callback provenance, activation dependency, and timing-window binding

## Relevant Failure Classes

| Class | Meaning |
| --- | --- |
| `FP_COMPLIANCE_OVER_ESCALATION` | Residual compliance risk is visible, but required controls are cleared. Solo over-escalates because it treats residue as unresolved risk. |
| `FP_PROCEDURAL_HOLD_OVER_ESCALATION` | A visible hold remains, but the underlying exception is closed. Solo treats the hold as blocking. |
| `FP_DUPLICATE_INVOICE_OVER_ESCALATION` | Invoice looks duplicate-like, but exact source records prove legitimacy. |
| `FP_VENDOR_CHANGE_OVER_ESCALATION` | Vendor change looks suspicious, but legal assignment, callback, tax/account ownership, or payment controls are confirmed. |
| `FP_THRESHOLD_ADJACENT_OVER_ESCALATION` | Transaction is close to a threshold but exact authority proves it is legitimate. |
| `FP_ANOMALOUS_EXPLAINED_BEHAVIOR` | Transaction breaks pattern, but specific source evidence explains it. |
| `FP_EXCEPTION_PATH_FREEZE` | Emergency/exception path looks like control bypass, but is fully authorized by scoped policy. |
| `BEC_SURFACE_FIXATION` | Model treats urgency/email/account-change surface as dispositive despite independent controls. |
| `PREMATURE_CLOSURE` | Model sees some approvals and stops before the actual final gate. |
| `APPROVAL_COUNTING` | Model counts signatures/forms instead of checking what each form authorized. |
| `SCOPE_READING` | Model sees an authority artifact but misses its scope boundary. |
| `AUTHORITY_CHAIN_REASONING` | Model fails to bind threshold, delegation, signer, amount, or date into one authority chain. |
| `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW` | Model treats an artifact as authorization without checking timing/scope/current applicability. |

## V2 Screen Mapping

| Pair | Raw Selection Reason | Atlas Class | Autopsy |
| --- | --- | --- | --- |
| `HV-KITC-041` | `041-A` wrong `ESCALATE`; `041-B` right label but incomplete KNEW | `FP_VENDOR_CHANGE_OVER_ESCALATION`, `BEC_SURFACE_FIXATION`, `APPROVAL_COUNTING`, `AUTHORITY_CHAIN_REASONING` | Promising class, but the policy text was too broad: it let Solo reasonably demand amount/date on vendor-master and callback records. Needs v3 rewrite with separate gates for vendor-master/callback/payment-release. |
| `HV-KITC-042` | Right labels, missing exact text terms | `FP_EXCEPTION_PATH_FREEZE`, `SCOPE_READING` | Not a clean Solo failure. Solo did bind execution release vs sourcing note. Term gate was too literal (`Facility R2` vs `facility (R2)`). |
| `HV-KITC-043` | Right labels, missing exact text term | `SCOPE_READING`, `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW` | Likely `KNEW`. Solo identified workspace export authorization missing. Term gate was too literal (`platform approvals` vs `platform use`). |
| `HV-KITC-044` | Right ALLOW label, missing exact phrase | `FP_EXCEPTION_PATH_FREEZE` | Likely `KNEW`. Solo bound class, channel, quantity, reason, timing, and specific exception record. |
| `HV-KITC-045` | Right ALLOW label, missing doc/amount exact strings | `FP_THRESHOLD_ADJACENT_OVER_ESCALATION`, `AUTHORITY_CHAIN_REASONING` | Likely `KNEW`. Solo named vendor, renewal class, term ceiling, amount ceiling, and date. |
| `HV-KITC-046` | `046-A` wrong `ESCALATE` | `FP_EXCEPTION_PATH_FREEZE`, `SCOPE_READING` | Dirty. Packet action date defaulted to `2026-06-28` while source records used `2026-06-25`; Solo found a real packet defect. |
| `HV-KITC-047` | `047-A` wrong `ESCALATE` | `FP_EXCEPTION_PATH_FREEZE`, `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW` | Cleanest v2 seam. Solo acknowledged the exception matched, then still over-escalated because the general warning felt unresolved. |
| `HV-KITC-049` | Right ALLOW label, missing amount string | `FP_THRESHOLD_ADJACENT_OVER_ESCALATION`, `AUTHORITY_CHAIN_REASONING` | Likely `KNEW`. Solo named invoice, period, delta, approver, and timing; term check was too literal on `4200`. |

## Current Clean Signal

The v2 batch produced one clean atlas-targeted Solo failure candidate:

- `HV-KITC-047-A`: expected `ALLOW`, Solo returned `ESCALATE`.
- Failure class: `FP_EXCEPTION_PATH_FREEZE` / `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW`.
- Failure shape: Solo recognized exact exception evidence but over-weighted a general warning.

The v2 batch also produced one promising but dirty class:

- `HV-KITC-041`: vendor-change/payment-release/callback chain.
- Needs v3 rewrite so each required gate has its own scope instead of making every record individually carry every field.

## Required V3 Direction

V3 should target these failure classes directly:

1. `FP_VENDOR_CHANGE_OVER_ESCALATION`
2. `FP_EXCEPTION_PATH_FREEZE`
3. `FP_PROCEDURAL_HOLD_OVER_ESCALATION`
4. `FP_COMPLIANCE_OVER_ESCALATION`
5. `FP_THRESHOLD_ADJACENT_OVER_ESCALATION`
6. `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW`
7. `SCOPE_READING`
8. `AUTHORITY_CHAIN_REASONING`
9. `APPROVAL_COUNTING`
10. `BEC_SURFACE_FIXATION`

The KNEW classifier should allow equivalent wording where the rationale clearly names the source-boundary fact. It should not count a right label as KNEW when the model omits the controlling record, cites the wrong seam, or relies on a packet defect.
