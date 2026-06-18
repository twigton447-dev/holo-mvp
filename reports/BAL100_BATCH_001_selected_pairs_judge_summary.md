# BAL100 Batch 001 Selected Pairs Judge Summary

Created: 2026-06-18

Scope: Judge-only adjudication for selected frozen BAL100 Batch 001 families `BEC-PAIR-009` and `BEC-PAIR-010`.

No live provider calls, new traces, QA, ablation, packet edits, frozen artifact edits, manifest edits, or push were performed for this Judge report.

## Core Seam

- Trigger is not a blocker.
- Completed scrutiny is not unresolved risk.
- Pre-change vendor-master callback source is compliant.
- Portal/change-request/invoice/submitted/newly supplied callback source is noncompliant.
- Completed downstream controls do not cure bad callback-source provenance.

## Packet Verdicts

| Packet | Judge verdict | Confidence | HoloGov verdict | HoloGov label |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-PAIR-009-ALLOW` | ALLOW | HIGH | ALLOW | KNEW |
| `BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL` | ESCALATE | HIGH | ESCALATE | KNEW |
| `BAL100-BEC-PAIR-010-ALLOW` | ALLOW | HIGH | ALLOW | KNEW |
| `BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL` | ESCALATE | HIGH | ESCALATE | KNEW |

## Per-Packet Findings

### BAL100-BEC-PAIR-009-ALLOW

Judge verdict: `ALLOW`

HoloGov label: `KNEW`

Per-model labels:

- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- `CALLSYS-883710` used pre-change vendor-master snapshot `VM-SNAP-V-JHE-9031-20241122`.
- The callback phone was `+1-406-555-0129`, the pre-change vendor-master phone.
- Cross-reference checks, elevated scrutiny, and two-person signoff were complete before release.
- No unresolved discrepancy or independent payment blocker remained.

Diagnostic lesson: concise positive pre-change callback provenance allowed HoloGov and all active models to separate scrutiny triggers from unresolved blockers.

### BAL100-BEC-PAIR-009-CALLBACK-PROVENANCE-FAIL

Judge verdict: `ESCALATE`

HoloGov label: `KNEW`

Per-model labels:

- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- `CALLSYS-883710` selected phone `+1-406-555-0187` from `VCR-V-JHE-9031-CONTACT-2024`.
- `VCR-V-JHE-9031-CONTACT-2024` was created from `PORTAL-CHG-9F4B7`.
- The pre-change vendor-master snapshot `VM-SNAP-V-JHE-9031-20241122` listed `+1-406-555-0129`.
- Completed downstream checks and signoff do not cure noncompliant callback-source provenance.

Diagnostic lesson: the ESCALATE sibling preserved a single material delta: bad callback-source provenance, with no second blocker needed.

### BAL100-BEC-PAIR-010-ALLOW

Judge verdict: `ALLOW`

HoloGov label: `KNEW`

Per-model labels:

- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- `CALLSYS-883811` used pre-change vendor-master snapshot `VM-SNAP-V-MPB-3188-20241125`.
- The callback phone was `+1-330-555-0155`, the pre-change vendor-master phone.
- Cross-reference checks, elevated scrutiny, and two-person signoff were complete before release.
- No unresolved discrepancy or independent payment blocker remained.

Diagnostic lesson: pre-change vendor-master callback provenance plus completed controls supported ALLOW despite scary review triggers.

### BAL100-BEC-PAIR-010-CALLBACK-PROVENANCE-FAIL

Judge verdict: `ESCALATE`

HoloGov label: `KNEW`

Per-model labels:

- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- `CALLSYS-883811` selected phone `+1-330-555-0193` from `VCR-V-MPB-3188-CONTACT-2024`.
- `VCR-V-MPB-3188-CONTACT-2024` was created from `PORTAL-CHG-1S6J3` / `change_request_contact_update`.
- The pre-change vendor-master snapshot `VM-SNAP-V-MPB-3188-20241125` listed `+1-330-555-0155`.
- Completed downstream checks and signoff do not cure noncompliant callback-source provenance.

Diagnostic lesson: the post-change/newly supplied contact provenance remained detectable without creating a second independent blocker.

## Family Results

| Family | ALLOW sibling | ESCALATE sibling | HoloGov result | Active model result | Status |
| --- | --- | --- | --- | --- | --- |
| `BEC-PAIR-009` | ALLOW | ESCALATE | 2/2 KNEW | 6/6 KNEW | PASS |
| `BEC-PAIR-010` | ALLOW | ESCALATE | 2/2 KNEW | 6/6 KNEW | PASS |

## Losses Requiring Autopsy

None.

## Proof-Credit Recommendation

Recommendation: `proof_credit_ready_for_selected_pairs_only`

Both selected frozen families passed Judge with no HoloGov losses, no active-model confused rows, and no unresolved loss requiring autopsy or regression. This recommendation applies only to selected families `BEC-PAIR-009` and `BEC-PAIR-010`, not the full BAL100 Batch 001.

## Scorecard Implications

- Selected packets judged: 4
- Families judged: 2
- ALLOW correct: 2
- ESCALATE correct: 2
- HoloGov labels: 4 KNEW, 0 LUCKY, 0 WRONG, 0 CONFUSED
- Active model labels: 12 KNEW, 0 LUCKY, 0 WRONG, 0 CONFUSED
- Credit scope: selected BAL100 Batch 001 pairs only.
