# BAL100 Batch 001 Second Repair Summary

Basis commit: `c07b888`  
Branch: `holo-builder-freeze-manifest-gate-001`

This repair recalibrated the 16 BAL100 Batch 001 draft packets only. It did not rerun scout, freeze, create official traces, run Judge, run QA, run ablation, edit frozen artifacts, or push.

## Families Changed

`BEC-PAIR-003`, `BEC-PAIR-004`, `BEC-PAIR-005`, `BEC-PAIR-006`, `BEC-PAIR-007`, `BEC-PAIR-008`, `BEC-PAIR-009`, `BEC-PAIR-010`

## ALLOW-Side Language Repair

ALLOW callback provenance now reads as a normal closed AP record. The callback record names the pre-change vendor-master snapshot, records `callback_phone_lineage.selected_record_type=vendor_master_snapshot`, and marks the pre-change source as selected for callback. The noisy contrast list that repeated portal/change/invoice/submitted-contact vocabulary near the callback source was removed from the ALLOW callback record.

Closure remains explicit through compact status facts: `callback_complete`, `signoff_complete`, `scrutiny_completed`, `hold_released`, `xref_complete`, `release_checklist_complete`, and `no unresolved discrepancy remains`.

## ESCALATE-Side Subtlety Repair

ESCALATE siblings still carry the same material provenance defect, but the answer-like labels were removed. The callback record now presents source-lineage facts: selected source record, `created_from` where applicable, `contact_phone_source`, selected phone, and the different pre-change vendor-master phone.

Removed neon labels include `noncompliant_callback_source`, `source_defect_note`, `single_material_blocker_note`, explicit `not_used_for_callback`, and callback-record wording that directly said noncompliant/material blocker.

## Preserved Constraints

The only material delta remains callback-source provenance. The repair did not add missing PO, missing approval, sanctions hold, expired delegation, bank mismatch, invoice amount anomaly, unresolved hold, or incomplete cross-reference. Model-visible payload keys remain `action` and `context` only.

## Test Updates

- ALLOW callback records are protected against noisy forbidden-source vocabulary near provenance.
- ESCALATE callback records must preserve submitted/update/invoice lineage without neon answer labels.
- Closure tests now check compact completed/released status facts.
- The formerly too-easy `007` and `010` variants keep vendor-contact-record lineage without spelling it as newly supplied in `number_source`.

## Next Validation

A later Taylor-approved scout rerun is needed to measure whether OpenAI ALLOW over-escalation drops while ESCALATE siblings regain useful difficulty.
