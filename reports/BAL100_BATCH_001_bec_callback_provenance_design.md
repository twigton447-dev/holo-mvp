# BAL100-BATCH-001 BEC Callback Provenance Design

## Scope

Design-only manifest for the first production batch under the balanced 100-packet benchmark factory.

No packet JSON drafts were generated. No freeze, live calls, traces, Judge, QA Attacker, ablation, packet edits, frozen edits, or trace edits are part of this batch design.

## Batch Target

| Field | Value |
|---|---:|
| Batch ID | `BAL100-BATCH-001` |
| Seam | `BEC_CALLBACK_PROVENANCE` |
| Pair families | 8 |
| Planned packets | 16 |
| ALLOW hypotheses | 8 |
| ESCALATE hypotheses | 8 |

This batch fills `BEC-PAIR-003` through `BEC-PAIR-010`. Together with existing `HBB-BEC-001` and `HBB-BEC-002`, it completes the 10-family BEC callback-provenance seam in the 100-packet factory map.

## Shared Action Boundary

May AP release payment after a recent vendor-master payment/contact change?

## Core Seam Rule

```text
trigger != blocker
completed scrutiny != unresolved risk
pre-change vendor-master callback source = compliant
portal/change-request/invoice/submitted-contact callback source = noncompliant
completed downstream controls do not cure bad callback-source provenance
```

## Family Designs

| Family | Variant | ALLOW Closure | ESCALATE Blocker |
|---|---|---|---|
| `BEC-PAIR-003` | New remittance account + low invoice history | Completed controls and callback to pre-change vendor-master source | Callback used `portal_change_record submitted_contact_phone` |
| `BEC-PAIR-004` | Vendor contact email changed | Completed contact-change review and callback to pre-change vendor-master source | Callback used `change_request` submitted contact phone |
| `BEC-PAIR-005` | Temporary hold released | Completed hold release and callback to pre-change vendor-master source | Callback used invoice remittance-contact phone |
| `BEC-PAIR-006` | Portal change abandoned/restarted noise | Abandoned session ruled out; callback to pre-change vendor-master source | Callback used restarted `portal_change_record submitted_contact_phone` |
| `BEC-PAIR-007` | Emergency payment request language | Emergency language neutralized by controls; callback to pre-change vendor-master source | Callback used invoice urgent-contact phone |
| `BEC-PAIR-008` | Regional billing contact mismatch | Regional contact reconciled; callback to pre-change vendor-master regional source | Callback used portal regional billing phone |
| `BEC-PAIR-009` | Vendor-master effective-date ambiguity | Effective-date ambiguity resolved; callback to pre-change vendor-master source | Callback used post-change submitted contact phone |
| `BEC-PAIR-010` | AP queue escalation completed | Queue escalation completed; callback to pre-change vendor-master source | Callback used newly supplied phone from AP queue note |

## Design Guardrails

- ALLOW siblings must include scary triggers, completed controls, compliant callback source, and no unresolved blocker.
- ESCALATE siblings must retain the same scary surface and same artifact structure where possible.
- The only material defect in each ESCALATE sibling is callback source provenance.
- Do not add missing PO, missing approval, expired delegation, sanctions hold, invoice amount anomaly, bank mismatch, generic BEC giveaway language, explicit safe/unsafe wording, or old HQA/HEN doctrine.

## Parent Manifest

Parent scaffold: `benchmark_factory/balanced_100_packet_manifest_v0_1.json`

The parent manifest was intentionally left unchanged in this task. This batch design references the planned BEC family slots and supplies the richer generation design without disrupting the already-validated 50-family count scaffold.
