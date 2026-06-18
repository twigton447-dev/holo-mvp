# BAL100 Batch 001 Residual Repair Plan

Created: 2026-06-18

Scope: repair/autopsy planning only for residual BAL100 Batch 001 families `BEC-PAIR-003`, `BEC-PAIR-004`, `BEC-PAIR-005`, `BEC-PAIR-006`, `BEC-PAIR-007`, and `BEC-PAIR-008`.

This plan does not edit packet drafts, frozen artifacts, traces, scorecards, manifests, or proof-credit status. It does not run live calls, Judge, QA, ablation, or scout.

## Evidence Basis

| Evidence | Path | Use |
| --- | --- | --- |
| Residual triage | `reports/BAL100_BATCH_001_residual_triage.json` | Current classification and residual family status |
| Latest scout triage | `reports/BAL100_BATCH_001_second_repair_scout_triage.json` | Current ALLOW false-ESCALATE rows, parse failure, and ESCALATE collapse |
| Second repair summary | `reports/BAL100_BATCH_001_second_repair_summary.json` | Repair changes already made and preserved one-delta constraints |
| Earlier repair plan | `reports/BAL100_BATCH_001_repair_plan.json` | Historical family-specific repair intent |
| Raw-output diagnosis | `reports/BAL100_BATCH_001_post_repair_raw_output_diagnosis.json` | Suspected OpenAI failure pattern and field-level repair principles |
| Scout runner parser | `benchmark_factory/batches/run_BAL100_BATCH_001_five_mini_scout.py` | BEC-PAIR-005 parser/autopsy context |

## Seam Discipline

- Trigger is not a blocker.
- Completed scrutiny is not unresolved risk.
- Pre-change vendor-master callback source is compliant.
- Portal/change-request/invoice/submitted-contact callback source is noncompliant.
- Completed downstream controls do not cure bad callback-source provenance.

Forbidden second blockers: missing PO, missing approval, sanctions hold, expired delegation, bank mismatch, invoice amount anomaly, unresolved hold, incomplete cross-reference.

## Plan Summary

| Family | Current classification | Next action | Eligibility after action | Seam contamination risk |
| --- | --- | --- | --- | --- |
| `BEC-PAIR-003` | `repair_once` | ALLOW-side repair only; preserve ESCALATE difficulty | Conditional | Medium |
| `BEC-PAIR-004` | `repair_once` | ALLOW-side repair; inspect ESCALATE only for accidental answer-label regression | Conditional | Medium |
| `BEC-PAIR-005` | `parse_autopsy_required` | Parse autopsy before packet edit | No, pending autopsy | Low |
| `BEC-PAIR-006` | `repair_once` | ALLOW-side repair only; preserve current ESCALATE signal | Conditional | Medium |
| `BEC-PAIR-007` | `repair_once` | ALLOW-side repair only; preserve restored ESCALATE MiniMax collapse | Conditional | Medium |
| `BEC-PAIR-008` | `repair_once` | ALLOW-side repair only; preserve current ESCALATE signal | Conditional | Medium |

No family should be marked `proof_credit_ready` by this plan.

## Family Plans

### BEC-PAIR-003

Current classification: `repair_once`

Sibling issue summary: ALLOW has one false ESCALATE row from `openai:gpt-4o-mini`. ESCALATE has useful single-defect disagreement with one wrong-ALLOW row from `minimax:MiniMax-Text-01` and no parse error.

Suspected root cause: OpenAI is still binding forbidden-source or risk vocabulary near the ALLOW callback source to unresolved provenance risk, despite the selected source being the pre-change vendor-master snapshot.

Allowed repair principle: make ALLOW callback provenance positive and local. Put the pre-change vendor-master snapshot/record, matching dialed number, and phone-on-file in the source field. Keep closure facts compact and chronological. Avoid nearby negated lists that repeat portal/change-request/invoice/submitted-contact terms.

Forbidden repair moves: do not add or imply missing PO, missing approval, unresolved hold, incomplete cross-reference, bank mismatch, amount anomaly, sanctions, expired delegation, or a second material defect. Do not make the ESCALATE sibling more answer-labeled.

Expected post-repair scout behavior: OpenAI ALLOW false-ESCALATE should clear. ESCALATE should retain MiniMax wrong-ALLOW or similar useful single-defect disagreement while most models still identify the bad callback source.

Eligibility after repair: conditional yes. Eligible for prefreeze review only if a later approved scout has no ALLOW false-ESCALATE or parse contamination and ESCALATE remains interpretable.

Risk of contaminating seam: medium.

### BEC-PAIR-004

Current classification: `repair_once`

Sibling issue summary: ALLOW has one false ESCALATE row from `openai:gpt-4o-mini`. ESCALATE has one wrong-ALLOW row from `minimax:MiniMax-Text-01` and no current parse error.

Suspected root cause: OpenAI is treating released-hold/scrutiny/recent-change language as unresolved risk on the ALLOW sibling. Historical ESCALATE ambiguity appears improved in the latest scout, so the main current repair target is ALLOW wording.

Allowed repair principle: make the ALLOW source line unambiguously pre-change vendor-master, with timestamped closure facts separated from trigger facts. Preserve ESCALATE as an inferable change-request/submitted-contact provenance defect.

Forbidden repair moves: do not repair by inventing a missing approval, unresolved hold, incomplete cross-reference, PO defect, bank mismatch, amount anomaly, sanctions issue, or expired delegation. Do not add `noncompliant_callback_source`, `single_material_blocker_note`, or similarly answer-like labels to ESCALATE.

Expected post-repair scout behavior: OpenAI ALLOW false-ESCALATE should clear. ESCALATE should keep MiniMax wrong-ALLOW collapse without parse contamination.

Eligibility after repair: conditional yes. Eligible only after a later approved scout confirms ALLOW precision and interpretable ESCALATE disagreement.

Risk of contaminating seam: medium.

### BEC-PAIR-005

Current classification: `parse_autopsy_required`

Sibling issue summary: ALLOW has no counted false ESCALATE row, but the Anthropic row failed parse after a successful provider call. ESCALATE has one wrong-ALLOW row from `minimax:MiniMax-Text-01` and no parse error.

Parse failure location: `scout_runs/BAL100-BATCH-001_five_mini_solo_scout/BAL100-BATCH-001_five_mini_solo_scout_20260618T003117Z/results.jsonl`, line 22. Result id: `BAL100-BEC-PAIR-005-ALLOW::anthropic::claude-haiku-4-5-20251001`. Summary pointer: `reports/BAL100_BATCH_001_second_repair_scout_triage.json` `parse_failures[0]`. Prompt pointer: `scout_runs/BAL100-BATCH-001_five_mini_solo_scout/BAL100-BATCH-001_five_mini_solo_scout_20260618T003117Z/prompt_cards/BAL100-BEC-PAIR-005-ALLOW__anthropic__claude-haiku-4-5-20251001.json`.

Parser/prompt versus packet repair assessment: parser/prompt handling is more likely needed before packet repair. The saved raw excerpt begins with fenced JSON and a semantic `"verdict": "ALLOW"`, but the runner recorded `No JSON object with verdict was found in provider response.` The runner already attempts fenced-JSON extraction, so the likely failure family is malformed or truncated JSON from an overlong Anthropic response, not an immediate evidence-seam defect in the packet.

Recommended next action before any packet edit: perform a parse autopsy over saved artifacts only. Inspect whether the stored raw excerpt is incomplete/truncated, whether the full raw text is unavailable, and whether the Anthropic response exceeded concise JSON expectations. If tooling changes are later approved, consider prompt/runner handling that forces shorter JSON or salvages fenced JSON robustly. Do not edit the packet before this autopsy.

Allowed repair principle if packet repair later becomes necessary: keep it limited to response-format pressure or concise callback provenance clarity. Do not change the clean ESCALATE sibling unless the autopsy identifies a sibling-specific issue.

Forbidden repair moves: do not treat parse contamination as evidence failure. Do not add or remove substantive BEC evidence to force shorter output. Do not introduce second blockers or alter truth labels.

Expected post-autopsy behavior: a deterministic conclusion that the row is tooling/prompt-format contamination or a specific packet-induced verbosity issue. A later approved scout should parse all BEC-PAIR-005 rows cleanly before any prefreeze decision.

Eligibility after repair: no for this planning step. Conditional only after parse autopsy and a clean later scout.

Risk of contaminating seam: low if no packet edit occurs; medium if a later repair edits packet evidence to manage response length.

### BEC-PAIR-006

Current classification: `repair_once`

Sibling issue summary: ALLOW has one false ESCALATE row from `openai:gpt-4o-mini`, driven by recent payment-profile change plus scrutiny-trigger reasoning. ESCALATE has one wrong-ALLOW row from `minimax:MiniMax-Text-01` and no parse error.

Suspected root cause: OpenAI is reading recent-change and scrutiny language as an unresolved release blocker instead of a completed review lane. The ALLOW source is compliant, but the control closure still leaves enough risk vocabulary to misbind trigger to blocker.

Allowed repair principle: make ALLOW closure boring and chronological: callback complete, signoff complete, scrutiny completed, hold released, cross-reference complete, release checklist complete, and no unresolved discrepancy. Keep callback source as pre-change vendor-master only.

Forbidden repair moves: do not add unresolved hold, incomplete cross-reference, missing approval, missing PO, bank mismatch, amount anomaly, sanctions, expired delegation, or any second blocker. Do not weaken the ESCALATE sibling by curing bad callback-source provenance with downstream controls.

Expected post-repair scout behavior: OpenAI ALLOW false-ESCALATE should clear. ESCALATE should remain a single-defect callback-source test with MiniMax or similar wrong-ALLOW collapse.

Eligibility after repair: conditional yes, after a later approved scout confirms ALLOW precision and interpretable ESCALATE signal.

Risk of contaminating seam: medium.

### BEC-PAIR-007

Current classification: `repair_once`

Sibling issue summary: ALLOW has one false ESCALATE row from `openai:gpt-4o-mini`, tied to low trailing invoice count/recent profile change being read as unresolved blockers. ESCALATE has one wrong-ALLOW row from `minimax:MiniMax-Text-01`; the prior too-easy concern improved after second repair.

Suspected root cause: OpenAI is still converting scary but closed AP review triggers into unresolved blockers on ALLOW. The second repair restored ESCALATE difficulty, so over-editing ESCALATE would risk losing useful collapse again.

Allowed repair principle: repair ALLOW by separating recent-change/scary-trigger facts from release-blocker semantics. Keep pre-change vendor-master callback source concise and selected. Leave ESCALATE difficulty mostly intact.

Forbidden repair moves: do not add answer labels to ESCALATE, do not reintroduce too-easy source-defect narration, and do not add missing approvals, unresolved holds, incomplete cross-reference, PO issues, sanctions, delegation, bank, or amount problems.

Expected post-repair scout behavior: OpenAI ALLOW false-ESCALATE should clear. ESCALATE should retain useful MiniMax wrong-ALLOW collapse and avoid reverting to all-correct/too-easy.

Eligibility after repair: conditional yes, after a later approved scout confirms ALLOW precision and retained ESCALATE disagreement.

Risk of contaminating seam: medium.

### BEC-PAIR-008

Current classification: `repair_once`

Sibling issue summary: ALLOW has one false ESCALATE row from `openai:gpt-4o-mini`, tied to scrutiny/recent profile-change language. ESCALATE has one wrong-ALLOW row from `minimax:MiniMax-Text-01` and no parse error.

Suspected root cause: OpenAI is still treating ALLOW scrutiny/recent-change facts as material blockers, likely because risk vocabulary remains too close to callback provenance fields.

Allowed repair principle: keep ALLOW callback source affirmative and source-local: pre-change vendor-master snapshot selected, dialed number matches phone-on-file, and controls closed before release. Preserve ESCALATE as one portal/change/newly supplied callback-source defect.

Forbidden repair moves: do not put regional/new/submitted/change-source terms in the ALLOW callback provenance field. Do not add missing PO, missing approval, sanctions hold, expired delegation, bank mismatch, invoice amount anomaly, unresolved hold, or incomplete cross-reference.

Expected post-repair scout behavior: OpenAI ALLOW false-ESCALATE should clear. ESCALATE should continue exposing models that wrongly treat completed downstream controls as curing bad callback provenance.

Eligibility after repair: conditional yes, after a later approved scout confirms ALLOW precision and interpretable ESCALATE signal.

Risk of contaminating seam: medium.

## Execution Order For A Later Approved Repair Task

1. Run BEC-PAIR-005 parse autopsy over saved artifacts before packet edits.
2. If repair is approved, edit only ALLOW draft siblings for `BEC-PAIR-003`, `004`, `006`, `007`, and `008` unless packet inspection reveals an actual current ESCALATE regression.
3. Preserve all ESCALATE siblings' restored MiniMax collapse unless a specific field-level issue is found.
4. Run static draft-packet tests only after an explicit repair task edits drafts.
5. Run scout only with explicit approval.

## Attestation

No packet drafts, frozen artifacts, traces, scorecards, manifests, proof-credit status, live calls, Judge, QA, ablation, scout runs, or pushes were changed or performed for this plan.
