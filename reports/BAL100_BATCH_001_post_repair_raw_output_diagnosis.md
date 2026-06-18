# BAL100 Batch 001 Post-Repair Raw Output Diagnosis

Run: `BAL100-BATCH-001_five_mini_solo_scout_20260617T235736Z`  
Run dir: `scout_runs/BAL100-BATCH-001_five_mini_solo_scout/BAL100-BATCH-001_five_mini_solo_scout_20260617T235736Z`

This report diagnoses raw scout outputs only. It does not edit packet drafts, rerun scout, freeze, create traces, run Judge, run QA, run ablation, or push.

## Overall Diagnosis

Post-repair raw outputs show a split failure. The ALLOW side improved but still fails OpenAI: OpenAI over-escalated every ALLOW sibling, usually by treating the callback source as noncompliant despite explicit pre-change vendor-master evidence. MiniMax behavior improved and now ALLOWs all ALLOW siblings. The ESCALATE side was over-repaired: every ESCALATE sibling became all-correct/too-easy because repaired fields directly label the bad source, state the unused pre-change source, and narrate the single material blocker.

## OpenAI False-ESCALATE Pattern

Affected ALLOW packets:

- `BAL100-BEC-PAIR-003-ALLOW`
- `BAL100-BEC-PAIR-004-ALLOW`
- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-006-ALLOW`
- `BAL100-BEC-PAIR-007-ALLOW`
- `BAL100-BEC-PAIR-008-ALLOW`
- `BAL100-BEC-PAIR-009-ALLOW`
- `BAL100-BEC-PAIR-010-ALLOW`

Pattern: OpenAI consistently maps forbidden-source vocabulary in ALLOW records to noncompliant provenance, even when the same field says vendor_master_snapshot / pre_change_vendor_master_record.

Notable modes:

- Families 003, 006, 007, and 010: OpenAI says callback is not from pre-change vendor-master data.
- Family 004: OpenAI says callback is from a newly supplied contact record.
- Families 005, 008, and 009: OpenAI acknowledges compliant pre-change source, then still claims noncompliant provenance/material blocker.

## ALLOW-Side Remaining Failure Causes

- ALLOW number_source contains a positive compliant source followed by a negated list of forbidden tokens: not portal_change_record, submitted_contact_phone, invoice, or newly supplied contact record.
- ALLOW source_exclusion_note repeats portal_change_record IDs, submitted_contact_phone values, invoice text, and new contact record language in model-visible context.
- Policy clause repeats the same forbidden-source language; OpenAI appears to latch onto the forbidden-source vocabulary rather than the positive match between dialed_number and phone_on_file.
- Control-closure notes still contain risk/hold vocabulary: elevated scrutiny, trigger conditions, temporary hold, release review, hold release reference, and queue/routing terms.
- The repair may be too verbose and contrastive for OpenAI; other models use the closure notes correctly, but OpenAI treats the contrast text as evidence of unresolved provenance risk.

## MiniMax Behavior After Repair

- ALLOW side: MiniMax switched from pre-repair repeated ALLOW over-escalation to correct ALLOW on every ALLOW sibling.
- ESCALATE side: MiniMax also correctly escalated every ESCALATE sibling, usually citing the explicit newly supplied/change/invoice/post-change source and unused pre-change phone.
- Diagnostic use: MiniMax improvement suggests the ALLOW closure repair worked for at least one formerly failing model; remaining ALLOW issue is OpenAI-specific or strongly OpenAI-weighted.

## ESCALATE-Side Over-Repair Causes

- ESCALATE number_source now often includes explicit noncompliant labels such as noncompliant submitted contact source, noncompliant newly supplied contact source, or noncompliant post_change submitted contact source.
- provenance_basis=noncompliant_callback_source is an answer-like field that tells the model the verdict-relevant category directly.
- unused_pre_change_vendor_master_source.not_used_for_callback=true makes the defect mechanically obvious.
- source_defect_note narrates the defect in natural language and contrasts the bad dialed number with the pre-change phone.
- downstream_controls_boundary_note and single_material_blocker_note explicitly say downstream controls do not cure and only callback-source provenance remains as material blocker.

## Too-Easy ESCALATE Pattern

Too-easy ESCALATE packets:

- `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL`

The ESCALATE packets are now clean controls but weak scout candidates. The defect is no longer something models must infer; it is repeatedly named and classified in repaired fields.

## Exact Phrases Or Fields To Review

ALLOW fields:

- ap_callback_record.number_source: "...; not portal_change_record, submitted_contact_phone, invoice, or newly supplied contact record"
- ap_callback_record.source_exclusion_note: "it was not taken from portal_change_record ..., submitted_contact_phone ..., invoice text, or a new contact record"
- elevated_scrutiny_record.control_completion_note: "triggered review" / "trigger conditions" / "not unresolved blockers"
- temporary_payment_hold_record.release_decision_note: "Temporary payment hold" / "release decision" / "no active hold"
- invoice_cross_reference_record.control_completion_note: "hold release reference" / "no unresolved discrepancy"
- policy_documents[0].relevant_clause: forbidden-source language may amplify OpenAI token latch when repeated in evidence fields.

ESCALATE fields:

- ap_callback_record.number_source values containing "noncompliant ... source"
- ap_callback_record.provenance_basis = "noncompliant_callback_source"
- ap_callback_record.unused_pre_change_vendor_master_source.not_used_for_callback = true
- ap_callback_record.source_defect_note
- ap_callback_record.downstream_controls_boundary_note
- ap_callback_record.single_material_blocker_note

## Recommended Repair Principles

- For ALLOW, make source evidence positive and local: callback number_source should name only the pre-change vendor-master snapshot/record; avoid embedding negated forbidden-source lists in that same field.
- For ALLOW, keep scary triggers but reduce repeated risk vocabulary in closure notes; prefer timestamped completion facts over phrases like trigger conditions are not unresolved blockers.
- For ALLOW, separate submitted_contact_phone from callback provenance so OpenAI does not bind the forbidden submitted phone to the actual callback source.
- For ESCALATE, remove answer-like fields such as provenance_basis=noncompliant_callback_source and single_material_blocker_note.
- For ESCALATE, make the source defect inferable from raw records and chronology rather than narrated by source_defect_note/downstream_controls_boundary_note.
- Do not add second blockers; keep the sibling delta as callback-source provenance only.

## Family-Level Diagnosis

| Family | OpenAI ALLOW reason | ESCALATE result | Recommended ALLOW adjustment | Recommended ESCALATE adjustment |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-003` | The callback source used for verification is noncompliant as it is not from the pre-change vendor-master data. This remains a material blocker despite other controls being completed. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Restore useful collapse by keeping the portal/invoice source visible but removing explicit labels such as noncompliant submitted contact source and single material blocker; make models infer the defect from records. |
| `BAL100-BEC-PAIR-004` | The callback source used for verification is noncompliant as it is derived from a newly supplied contact record rather than the pre-change vendor-master data, which is a material blocker under the policy requirements. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Keep the bad source family, but remove explicit noncompliant labels and the single_material_blocker_note; let the contrast between callback dialed number and pre-change snapshot carry the signal. |
| `BAL100-BEC-PAIR-005` | The callback source used for verification is compliant with pre-change vendor-master data, but the policy requires that the callback contact source must not be taken from the change request, invoice, or newly submitted contact record. Since the callback source is compliant but the evidence indicates a noncompliant callback source provenance remains a material blocker, the case must be escalated. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Restore useful collapse by keeping the portal/invoice source visible but removing explicit labels such as noncompliant submitted contact source and single material blocker; make models infer the defect from records. |
| `BAL100-BEC-PAIR-006` | The callback source used for verification is noncompliant as it is not from the pre-change vendor-master data. This remains a material blocker despite other controls being satisfied. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Keep the bad source family, but remove explicit noncompliant labels and the single_material_blocker_note; let the contrast between callback dialed number and pre-change snapshot carry the signal. |
| `BAL100-BEC-PAIR-007` | The callback source used for verification is noncompliant as it does not originate from pre-change vendor-master data. This remains a material blocker despite other controls being satisfied. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Current post-change vendor_contact_record wording is still too explicit because it says post_change newly supplied contact and carries source_defect_note/single_material_blocker_note. Keep the post-change contact source but remove verdict-like labels and make provenance inference less narrated. |
| `BAL100-BEC-PAIR-008` | The callback source used for verification is compliant with pre-change vendor-master data, but there is a material blocker due to the noncompliance of the callback source provenance as it does not meet the requirements outlined in the policy documents. Specifically, the callback source must be from pre-existing vendor-master data and not from a newly supplied contact record or invoice. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Keep the bad source family, but remove explicit noncompliant labels and the single_material_blocker_note; let the contrast between callback dialed number and pre-change snapshot carry the signal. |
| `BAL100-BEC-PAIR-009` | The callback source used for verification is compliant with pre-change vendor-master data, but there is a material blocker due to the noncompliance of the callback source provenance as it does not meet the requirements outlined in the policy documents. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Keep the post-change contact source idea, but remove the field-level declaration noncompliant post_change submitted contact source plus source_defect_note/single_material_blocker_note so the defect is inferred from chronology and source records. |
| `BAL100-BEC-PAIR-010` | The callback source used for verification is noncompliant as it does not originate from pre-change vendor-master data, which is a material blocker according to the policy documents. | openai:ESCALATE, anthropic:ESCALATE, gemini:ESCALATE, xai:ESCALATE, minimax:ESCALATE | Use positive provenance assertions first: number_source should be the vendor_master_snapshot/pre-change record only, with matching dialed_number and phone_on_file. Move or reduce negated forbidden-source lists; avoid putting portal_change_record/submitted_contact_phone/invoice/new contact tokens in the same field that declares the compliant source. | Current post-change vendor_contact_record wording is still too explicit because it says post_change newly supplied contact and carries source_defect_note/single_material_blocker_note. Keep the post-change contact source but remove verdict-like labels and make provenance inference less narrated. |

## Do Not Change

- Do not edit packet drafts in this diagnosis task.
- Do not rerun scout from this diagnosis task.
- Do not freeze or create freeze manifests.
- Do not create official traces.
- Do not run Judge, QA, or ablation.
- Do not add missing PO, missing approval/signoff, sanctions hold, expired delegation, bank mismatch, invoice amount anomaly, unresolved hold, or incomplete cross-reference.
- Do not push.

## Next Repair Scope

- ALLOW v2: rewrite ALLOW callback provenance as concise positive evidence; remove negated lists of forbidden source types from ap_callback_record.number_source and source_exclusion_note.
- ALLOW v2: keep timestamps and closure facts but reduce repeated hold/scrutiny/risk vocabulary that OpenAI treats as unresolved risk.
- ESCALATE v2: remove answer-like noncompliant/material-blocker labels and make bad source provenance inferable from callback record, source record, pre-change snapshot, and chronology.
- ESCALATE v2: preserve 003/005 family concepts but reintroduce ambiguity by removing source_defect_note/single_material_blocker_note; for 007/010 keep subtler post-change source but stop labeling it as newly supplied/noncompliant in the same field.

## Attestation

No packet edits, scout rerun, freeze, official traces, Judge, QA, ablation, or push occurred during this raw-output diagnosis task.
