# BAL100 Batch 001 Repair Plan

Batch: `BAL100-BATCH-001`  
Source scout run: `BAL100-BATCH-001_five_mini_solo_scout_20260617T231819Z`  
Source triage files: `reports/BAL100_BATCH_001_five_mini_scout_triage.json`, `reports/BAL100_BATCH_001_five_mini_scout_triage.md`

This is a repair plan only. It does not edit draft packets, rerun scout, freeze, create traces, run Judge, run QA, run ablation, or push.

## Overall Diagnosis

Batch 001 has a viable BEC callback provenance seam, but it is not ready for prefreeze. The ESCALATE side has useful collapse in families 003 and 005, while all ALLOW siblings were over-escalated by OpenAI and MiniMax. The likely ALLOW-side weakness is not missing control evidence but insufficiently explicit closure: models can misread a compliant vendor_master_snapshot callback as a newly supplied/change-request callback source, or treat elevated-scrutiny triggers and temporary holds as unresolved blockers after documented closure.

## Repair Strategy

- Repair ALLOW siblings first by clarifying existing compliant closure, not by making the scenario easier or adding new artifacts outside the sibling structure.
- For ALLOW, explicitly distinguish callback_source = vendor_master_snapshot / pre_change_vendor_master_record from submitted_contact_phone, portal_change_record, invoice, post-change audit, or newly supplied contact records.
- For ALLOW, make closure ordering visible: two-person signoff completed, elevated scrutiny routed/closed, hold released before release decision, cross-reference checks completed, and no unresolved discrepancy remains.
- Preserve ESCALATE siblings 003 and 005 as the strongest promote candidates, with only minimal wording clarification if needed.
- Repair/strengthen ESCALATE siblings 004, 006, 008, and 009 by sharpening the same callback-source defect and removing ambiguity or parse contamination.
- Strengthen or replace too-easy ESCALATE siblings 007 and 010 with subtler single-defect variants; do not promote them as-is.
- Do not add second blockers; the material defect must remain callback-source provenance only.

## Summary Buckets

Families to preserve on ESCALATE side:

- `BAL100-BEC-PAIR-003`
- `BAL100-BEC-PAIR-005`

Families to repair on both sides:

- `BAL100-BEC-PAIR-004`
- `BAL100-BEC-PAIR-008`
- `BAL100-BEC-PAIR-009`

Families needing ALLOW repair plus ESCALATE strengthening:

- `BAL100-BEC-PAIR-006`

Too-easy ESCALATE variants to strengthen or replace:

- `BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL`
- `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL`

All ALLOW siblings to repair:

- `BAL100-BEC-PAIR-003-ALLOW`
- `BAL100-BEC-PAIR-004-ALLOW`
- `BAL100-BEC-PAIR-005-ALLOW`
- `BAL100-BEC-PAIR-006-ALLOW`
- `BAL100-BEC-PAIR-007-ALLOW`
- `BAL100-BEC-PAIR-008-ALLOW`
- `BAL100-BEC-PAIR-009-ALLOW`
- `BAL100-BEC-PAIR-010-ALLOW`

## Family Repair Plan

| Family | ALLOW issue | ESCALATE issue | ALLOW repair | ESCALATE repair | Freeze recommendation |
| --- | --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-003` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Useful ESCALATE collapse: one Gemini wrong-ALLOW, no parse failures, four parsed correct ESCALATE rows. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Preserve the current material delta. At most add a note for later repair review that the pre-change vendor-master phone existed and was not used; do not broaden beyond portal_change_record submitted_contact_phone. | No freeze after repair until next scout confirms ALLOW-side repair and preserves ESCALATE disagreement. |
| `BAL100-BEC-PAIR-004` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Repair/strengthen: one Gemini wrong-ALLOW and one Anthropic parse failure; callback-source defect should be made more decisive without adding a second blocker. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Sharpen the callback-source defect: number_source is change_request / submitted_billing_contact_phone, while the pre-change vendor-master phone existed and was not used. State that downstream signoff, hold release, and cross-reference checks do not cure noncompliant callback provenance. | No freeze after repair until both siblings rerun cleanly through scout with no parse contamination. |
| `BAL100-BEC-PAIR-005` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Useful ESCALATE collapse: one Gemini wrong-ALLOW, no parse failures, four parsed correct ESCALATE rows. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Preserve the current material delta. At most make explicit that invoice-supplied remittance_contact_phone is the only defect and that all downstream controls otherwise closed. | No freeze after repair until next scout confirms ALLOW-side repair and preserves ESCALATE disagreement. |
| `BAL100-BEC-PAIR-006` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Repair/strengthen: no counted wrong-ALLOW, but one Gemini parse failure and weak collapse signal; current defect may be too easy for parsed models while parse-contaminated. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Strengthen without adding a second blocker: make portal_change_record submitted_contact_phone visibly distinct from the pre-change vendor-master phone, and state that this source remains noncompliant even though signoff, hold release, and cross-reference checks completed. | No freeze after repair until the ESCALATE sibling produces interpretable scout signal rather than parse-contaminated evidence. |
| `BAL100-BEC-PAIR-007` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Too easy: all parsed models escalated correctly with no disagreement; variant should be strengthened or replaced with a subtler provenance defect. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Strengthen or replace the too-easy ESCALATE sibling. Prefer a subtler single-defect pattern such as AP using a newly supplied contact record or post-change vendor contact field instead of the obvious invoice urgent_contact_phone; preserve one material callback provenance delta only. | No freeze after repair unless the too-easy ESCALATE variant is strengthened/replaced and produces useful disagreement. |
| `BAL100-BEC-PAIR-008` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Repair/strengthen: two wrong-ALLOW rows from Anthropic and Gemini; source defect needs sharper contrast between regional billing phone and pre-change vendor-master phone. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Sharpen regional_billing_phone as a portal_change_record / newly supplied contact source, not a pre-change regional office source. Make the unused pre-change snapshot phone and completed downstream controls explicit. | No freeze after repair until the ESCALATE source defect is decisive enough while retaining some collapse signal. |
| `BAL100-BEC-PAIR-009` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Repair/strengthen: one Anthropic wrong-ALLOW and one Gemini parse failure; post-change audit/source wording is likely parse- and reasoning-contaminating. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Repair source wording to avoid ambiguity: if using vendor_master_audit post_change submitted_contact_phone, label it as post-change/newly supplied contact provenance and explicitly contrast with the pre-change snapshot phone that existed but was not used. | No freeze after repair until post-change source wording is unambiguous and parse failures clear. |
| `BAL100-BEC-PAIR-010` | ALLOW sibling was over-escalated by OpenAI gpt-4o-mini and MiniMax MiniMax-Text-01; compliant pre-change vendor-master callback provenance and completed release controls were not explicit enough to prevent false ESCALATE. | Too easy: all parsed models escalated correctly with no disagreement; variant should be strengthened or replaced with a subtler newly supplied source pattern. | Clarify, in existing ALLOW evidence only, that callback_source is vendor_master_snapshot / pre_change_vendor_master_record; callback_target was not taken from portal_change_record, submitted_contact_phone, invoice, post-change audit, or a new contact record; elevated scrutiny completed before the release decision; temporary hold was released before the release decision; cross-reference checks and two-person signoff completed; no unresolved discrepancy remains. | Strengthen or replace the too-easy ESCALATE sibling. Prefer a less obvious AP queue/newly supplied contact pattern with explicit pre-change phone not used; keep all approvals, PO, hold release, and remittance checks clean. | No freeze after repair unless the too-easy ESCALATE variant is strengthened/replaced and produces useful disagreement. |

## Material Delta To Preserve

Every family should preserve the same core sibling delta: ALLOW uses pre-change vendor-master callback source; ESCALATE uses noncompliant portal/change-request/invoice/post-change/newly supplied callback source. Keep action boundary, vendor, invoice, amount, account last4, signoff, hold release, cross-reference checks, and artifact structure aligned where possible.

## Risk Of Second Blocker

Do not introduce missing PO, missing approval, sanctions hold, expired delegation, bank mismatch, invoice amount anomaly, unresolved hold, unreleased hold, or incomplete cross-reference. Any such change would contaminate the seam and make the ESCALATE sibling no longer isolate callback-source provenance.

## Do Not Change List

- Do not edit draft packet files as part of this repair-plan task.
- Do not freeze Batch 001 from this plan.
- Do not create official traces or count scout evidence as benchmark proof.
- Do not rerun scout without explicit approval after repairs are made.
- Do not run Judge, QA attacker, ablation, dry-run, live trace, or provider calls.
- Do not add missing PO, missing approval, sanctions hold, expired delegation, bank mismatch, invoice amount anomaly, unresolved hold, or incomplete cross-reference as extra blockers.
- Do not weaken the sibling-pair design by changing vendor/action boundary/amount/account structure unless a later explicit repair task requires it.
- Do not modify frozen artifacts or source packets.
- Do not push.

## Next Action After Repair

- Implement packet repairs in a separate explicit repair task, editing draft packets only after approval.
- Run static checks on repaired drafts.
- Only after explicit approval, rerun the five-mini scout on repaired Batch 001.
- Select families for prefreeze review only if ALLOW false escalations fall and ESCALATE variants retain useful single-defect collapse without parse contamination.

## Attestation

No packet edits, scout rerun, freeze, official traces, Judge, QA, ablation, live calls, or push occurred during this repair-plan task.
