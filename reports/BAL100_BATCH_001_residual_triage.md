# BAL100 Batch 001 Residual Triage

Created: 2026-06-18

Scope: Residual triage for BAL100 Batch 001 families `BEC-PAIR-003` through `BEC-PAIR-008` only.

This is triage only. It is not benchmark proof, not prefreeze review, not freeze, not an official trace, not Judge, not QA, not ablation, and not proof-credit accounting.

## Boundaries

- Do not touch `BEC-PAIR-009` or `BEC-PAIR-010` except as comparison references.
- Do not touch `HBB-BEC-001` or `HBB-BEC-002`.
- Do not edit frozen artifacts.
- Do not mark anything `proof_credit_ready`.
- Preserve the callback provenance seam only.

## Callback Provenance Rule

- Trigger is not a blocker.
- Completed scrutiny is not unresolved risk.
- Pre-change vendor-master callback source is compliant.
- Portal/change-request/invoice/submitted-contact callback source is noncompliant.
- Completed downstream controls do not cure bad callback-source provenance.

Do not introduce missing PO, missing approval, sanctions hold, expired delegation, bank mismatch, invoice amount anomaly, unresolved hold, or incomplete cross-reference.

## Evidence Basis

| Evidence | Path | Use |
| --- | --- | --- |
| Latest residual scout triage | `reports/BAL100_BATCH_001_second_repair_scout_triage.json` | Primary family-level status for 003-008 after second repair scout |
| Second repair summary | `reports/BAL100_BATCH_001_second_repair_summary.json` | Repair context and preserved one-delta constraints |
| Earlier repair plan | `reports/BAL100_BATCH_001_repair_plan.json` | Prior family-specific repair intent |
| Post-repair raw diagnosis | `reports/BAL100_BATCH_001_post_repair_raw_output_diagnosis.json` | Field-level failure patterns and repair principles |
| Selected-pair scorecard | `reports/BAL100_scorecard.json` | Comparison boundary: only 009/010 have proof credit |

## Classification Summary

| Family | Classification | Eligible for prefreeze after one repair | Quarantine from BAL100 proof-credit path |
| --- | --- | --- | --- |
| `BEC-PAIR-003` | `repair_once` | Yes, if ALLOW OpenAI false-ESCALATE clears and no parse contamination appears | No |
| `BEC-PAIR-004` | `repair_once` | Yes, if ALLOW OpenAI false-ESCALATE clears and ESCALATE remains interpretable | No |
| `BEC-PAIR-005` | `parse_autopsy_required` | Not until parse autopsy resolves or explains the Anthropic parse failure | No |
| `BEC-PAIR-006` | `repair_once` | Yes, if ALLOW OpenAI false-ESCALATE clears and ESCALATE remains interpretable | No |
| `BEC-PAIR-007` | `repair_once` | Yes, if ALLOW OpenAI false-ESCALATE clears and ESCALATE keeps MiniMax collapse | No |
| `BEC-PAIR-008` | `repair_once` | Yes, if ALLOW OpenAI false-ESCALATE clears and ESCALATE remains interpretable | No |

No residual family is ready to promote to prefreeze as-is. No residual family should be retired or quarantined on current evidence.

## Family Triage

### BEC-PAIR-003

Current status: `promising_but_allow_openai_false_escalate_remains`

ALLOW sibling issue: `BAL100-BEC-PAIR-003-ALLOW` still has one false ESCALATE row from `openai:gpt-4o-mini`. The latest scout note says OpenAI still escalates the ALLOW sibling on scrutiny/trigger reasoning.

ESCALATE sibling issue: `BAL100-BEC-PAIR-003-CALLBACK-PROVENANCE-FAIL` has useful ESCALATE-side disagreement: one wrong-ALLOW row from `minimax:MiniMax-Text-01`, with no ESCALATE parse error.

Scout/scout-repair evidence pointer: `reports/BAL100_BATCH_001_second_repair_scout_triage.json` family-level triage; `reports/BAL100_BATCH_001_second_repair_summary.json` ALLOW-side language repair; `reports/BAL100_BATCH_001_post_repair_raw_output_diagnosis.json` ALLOW OpenAI false-escalation pattern.

Recommended next action: `repair_once`

Exact repair principle: keep the ALLOW callback evidence positive and local. State the selected callback source as the pre-change vendor-master snapshot/record with matching dialed number and phone-on-file. Reduce nearby negated forbidden-source lists and risk vocabulary so portal/change/invoice/submitted-contact terms are not bound to the compliant callback source. Preserve the ESCALATE material delta; do not make it more answer-labeled.

Eligible for prefreeze after one repair: yes, if the ALLOW OpenAI false-ESCALATE clears while the ESCALATE sibling retains non-trivial single-defect disagreement.

Quarantine from BAL100 proof-credit path: no.

### BEC-PAIR-004

Current status: `promising_but_allow_openai_false_escalate_remains`

ALLOW sibling issue: `BAL100-BEC-PAIR-004-ALLOW` still has one false ESCALATE row from `openai:gpt-4o-mini`.

ESCALATE sibling issue: `BAL100-BEC-PAIR-004-CALLBACK-PROVENANCE-FAIL` now has one wrong-ALLOW row from `minimax:MiniMax-Text-01`, with no ESCALATE parse error in the latest scout. This is useful collapse, not a proof-ready result.

Scout/scout-repair evidence pointer: `reports/BAL100_BATCH_001_second_repair_scout_triage.json` family-level triage; `reports/BAL100_BATCH_001_repair_plan.json` earlier repair-both-siblings diagnosis; `reports/BAL100_BATCH_001_post_repair_raw_output_diagnosis.json` field-level OpenAI failure pattern.

Recommended next action: `repair_once`

Exact repair principle: repair the ALLOW sibling only unless packet inspection reveals a current ESCALATE wording regression. Make the ALLOW source line cleanly pre-change vendor-master, timestamp closure facts compactly, and avoid second-blocker wording. Preserve ESCALATE as an inferable change-request/submitted-contact provenance defect rather than adding neon labels.

Eligible for prefreeze after one repair: yes, if the ALLOW OpenAI false-ESCALATE clears and the ESCALATE sibling keeps interpretable MiniMax wrong-ALLOW collapse.

Quarantine from BAL100 proof-credit path: no.

### BEC-PAIR-005

Current status: `blocked_by_parse_contamination`

ALLOW sibling issue: `BAL100-BEC-PAIR-005-ALLOW` has no counted false ESCALATE row in the latest scout, but it has an Anthropic parse failure: `anthropic:claude-haiku-4-5-20251001`. The provider call succeeded and the raw excerpt was semantically `ALLOW`, but the parser did not accept the fenced JSON response.

ESCALATE sibling issue: `BAL100-BEC-PAIR-005-CALLBACK-PROVENANCE-FAIL` has useful ESCALATE-side disagreement: one wrong-ALLOW row from `minimax:MiniMax-Text-01`, with no ESCALATE parse error.

Scout/scout-repair evidence pointer: `reports/BAL100_BATCH_001_second_repair_scout_triage.json` parse failure entry and family-level triage; `reports/BAL100_BATCH_001_repair_plan.json` earlier preserve-escalate-candidate plan.

Recommended next action: `parse_autopsy_required`

Exact repair principle: do not edit the packet first. Inspect the raw Anthropic response and parser behavior to decide whether this is parser rigidity around fenced JSON or packet-induced response formatting. If a later packet repair is required, keep it limited to callback provenance clarity and do not alter the clean ESCALATE sibling unless the parse autopsy points there.

Eligible for prefreeze after one repair: no. It may become eligible after parse autopsy if the parse failure is tooling-only or after a minimal parser/format-facing fix clears contamination without changing proof semantics.

Quarantine from BAL100 proof-credit path: no, but hold it out of prefreeze until parse contamination is resolved.

### BEC-PAIR-006

Current status: `promising_but_allow_openai_false_escalate_remains`

ALLOW sibling issue: `BAL100-BEC-PAIR-006-ALLOW` still has one false ESCALATE row from `openai:gpt-4o-mini`. The latest scout reason says OpenAI still treats recent payment-profile change plus scrutiny trigger as unresolved risk.

ESCALATE sibling issue: `BAL100-BEC-PAIR-006-CALLBACK-PROVENANCE-FAIL` has one wrong-ALLOW row from `minimax:MiniMax-Text-01`, with no ESCALATE parse error. This is an improved scout signal compared with the earlier parse-contaminated/weak state.

Scout/scout-repair evidence pointer: `reports/BAL100_BATCH_001_second_repair_scout_triage.json` family-level triage; `reports/BAL100_BATCH_001_repair_plan.json` earlier repair-allow-and-strengthen-escalate plan.

Recommended next action: `repair_once`

Exact repair principle: make ALLOW closure facts boring and chronological: callback complete, signoff complete, scrutiny completed, hold released, cross-reference complete, release checklist complete, and no unresolved discrepancy. Keep the selected callback source as pre-change vendor-master only. Do not add or imply an unresolved hold or incomplete cross-reference.

Eligible for prefreeze after one repair: yes, if the ALLOW OpenAI false-ESCALATE clears and ESCALATE remains interpretable with MiniMax collapse.

Quarantine from BAL100 proof-credit path: no.

### BEC-PAIR-007

Current status: `promising_but_allow_openai_false_escalate_remains`

ALLOW sibling issue: `BAL100-BEC-PAIR-007-ALLOW` still has one false ESCALATE row from `openai:gpt-4o-mini`. The latest scout reason says OpenAI still treats low trailing invoice count/recent profile change as unresolved blockers on ALLOW.

ESCALATE sibling issue: `BAL100-BEC-PAIR-007-CALLBACK-PROVENANCE-FAIL` has one wrong-ALLOW row from `minimax:MiniMax-Text-01`, with no ESCALATE parse error. The prior too-easy concern has improved after second repair, but it still is not prefreeze-ready while the ALLOW sibling false-escalates.

Scout/scout-repair evidence pointer: `reports/BAL100_BATCH_001_second_repair_scout_triage.json` family-level triage; `reports/BAL100_BATCH_001_second_repair_summary.json` note that formerly too-easy variants kept vendor-contact-record lineage without spelling it as newly supplied in `number_source`.

Recommended next action: `repair_once`

Exact repair principle: repair the ALLOW side by separating recent-change/scary-trigger facts from unresolved-risk semantics. Keep the pre-change vendor-master callback source concise and selected. Do not strengthen the ESCALATE sibling with answer labels; preserve its now-useful MiniMax collapse.

Eligible for prefreeze after one repair: yes, if the ALLOW OpenAI false-ESCALATE clears and ESCALATE retains useful disagreement.

Quarantine from BAL100 proof-credit path: no.

### BEC-PAIR-008

Current status: `promising_but_allow_openai_false_escalate_remains`

ALLOW sibling issue: `BAL100-BEC-PAIR-008-ALLOW` still has one false ESCALATE row from `openai:gpt-4o-mini`. The latest scout reason says OpenAI still treats scrutiny/recent profile change language as material blockers on ALLOW.

ESCALATE sibling issue: `BAL100-BEC-PAIR-008-CALLBACK-PROVENANCE-FAIL` has one wrong-ALLOW row from `minimax:MiniMax-Text-01`, with no ESCALATE parse error. Earlier repair-plan concerns about sharper source contrast should be treated as historical unless current packet inspection shows ambiguity.

Scout/scout-repair evidence pointer: `reports/BAL100_BATCH_001_second_repair_scout_triage.json` family-level triage; `reports/BAL100_BATCH_001_repair_plan.json` earlier repair-both-siblings diagnosis; `reports/BAL100_BATCH_001_post_repair_raw_output_diagnosis.json` ALLOW OpenAI false-escalation pattern.

Recommended next action: `repair_once`

Exact repair principle: keep the ALLOW callback source affirmative and source-local: pre-change vendor-master snapshot selected, dialed number matches phone-on-file, and controls closed before release. Avoid placing regional/new/submitted/change-source terms in the ALLOW callback provenance field. Preserve ESCALATE as a single portal/change/newly supplied callback-source defect.

Eligible for prefreeze after one repair: yes, if the ALLOW OpenAI false-ESCALATE clears and ESCALATE remains interpretable.

Quarantine from BAL100 proof-credit path: no.

## Recommended Queue

1. Parse autopsy: `BEC-PAIR-005-ALLOW`.
2. One narrow ALLOW-side repair pass: `BEC-PAIR-003`, `BEC-PAIR-004`, `BEC-PAIR-006`, `BEC-PAIR-007`, `BEC-PAIR-008`.
3. Do not repair, freeze, trace, Judge, QA, ablate, or mark proof credit without a separate explicit approval.

## Attestation

No live calls, scout rerun, Judge, QA, ablation, traces, packet edits, frozen artifact edits, proof-credit status changes, or push occurred during this residual triage task.
