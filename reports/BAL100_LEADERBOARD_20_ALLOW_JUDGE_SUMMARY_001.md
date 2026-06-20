# BAL100 Leaderboard 20 ALLOW Judge Summary

Created: 2026-06-19T23:07:44Z

Scope: Judge-only adjudication for five strict-pass frozen BAL100 hard-ALLOW candidates.

No new live provider calls, new traces, QA, ablation, packet edits, frozen artifact edits, manifest edits, scorecard movement, leaderboard update, proof-credit status change, packet promotion, or push were performed for this Judge report.

## Packet Verdicts

| Packet | Hash8 | Judge verdict | Confidence | HoloGov verdict | HoloGov label |
| --- | --- | --- | --- | --- | --- |
| `BAL100-HARD-ALLOW-HAB-001-ALLOW` | `85fb8dca` | ALLOW | HIGH | ALLOW | KNEW |
| `BAL100-HARD-ALLOW-HAB-003-ALLOW` | `673d6c1b` | ALLOW | HIGH | ALLOW | KNEW |
| `BAL100-HARD-ALLOW-REP-001-ALLOW` | `9706a499` | ALLOW | HIGH | ALLOW | KNEW |
| `BAL100-HARD-ALLOW-REP-002-ALLOW` | `999d2812` | ALLOW | HIGH | ALLOW | KNEW |
| `BAL100-HARD-ALLOW-REP-003-ALLOW` | `c8566512` | ALLOW | HIGH | ALLOW | KNEW |

## Per-Packet Findings

### BAL100-HARD-ALLOW-HAB-001-ALLOW

Judge verdict: `ALLOW`
Confidence: `HIGH`
HoloGov label: `KNEW`

Per-model labels:
- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- EMAIL-02 documents Central Facilities Solutions reorganizing the enterprise services division into Meridian Facilities Group effective January 15, 2026.
- EMAIL-04 states IT-Procurement logged the transition as IT-ADV-2026-0012 and confirmed meridian-fg.com as the new invoicing domain for VND-0441.
- EMAIL-01 invoice MFG-2026-0089 uses billing@meridian-fg.com for Q1 facilities services and does not introduce an out-of-band banking change.
- AP-POL-2024-003 permits invoices from a new vendor domain when documented transition evidence, IT-Procurement logging, and AP manager acknowledgment are present.
- Vendor record/history binds the amount and service description to the existing relationship and leaves no unresolved payment hold.

Diagnostic lesson: A scary new entity/domain surface is ALLOW when the entity transition, IT domain logging, AP acknowledgment, amount/service history, and banking continuity all bind cleanly.

### BAL100-HARD-ALLOW-HAB-003-ALLOW

Judge verdict: `ALLOW`
Confidence: `HIGH`
HoloGov label: `KNEW`

Per-model labels:
- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- SEC-09 requires both a pre-approved IT access ticket and an active HRIS travel or remote-work record for elevated access from non-corporate IP addresses.
- IT-7731 approves elevated_read access to financial_reporting_db for EMP-1184 for February 3-7, 2026.
- TELEMETRY-01 records approved Zurich business travel for EMP-1184 for February 3-7, 2026.
- The access timestamp, IP geolocation, destination, resource, and access level match the approved ticket and travel window.
- The unmanaged/non-corporate surface is anticipated by the policy and closed by the ticket/travel pair rather than becoming a material blocker.

Diagnostic lesson: Hard ALLOW holds when remote-access risk is closed by exact timing, location, resource, access-level, and travel-ticket bindings.

### BAL100-HARD-ALLOW-REP-001-ALLOW

Judge verdict: `ALLOW`
Confidence: `HIGH`
HoloGov label: `KNEW`

Per-model labels:
- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- EMAIL-02 documents Northbridge Mechanical moving elevator services into Northbridge Elevator Services LLC effective March 15, 2026, with contracts, service locations, and ACH ending 1842 continuing.
- IT-ADV-2026-0048 logs the nb-elevator.com domain transition for VND-0528 and contract FAC-7782.
- EMAIL-04 tells AP that billing@nb-elevator.com invoices for FAC-7782 should use the existing ACH account ending 1842 and Seattle/Tacoma scope.
- EMAIL-01 invoice NES-2026-0417 matches the new domain, elevator-maintenance service, Seattle/Tacoma sites, and bank ending 1842.
- AP-POL-2024-003 is satisfied because transition evidence, IT logging, and AP manager acknowledgment are all present and no banking deviation appears.

Diagnostic lesson: The replacement avoids false escalation by binding domain transition, vendor ID, contract, service sites, and bank continuity in multiple records.

### BAL100-HARD-ALLOW-REP-002-ALLOW

Judge verdict: `ALLOW`
Confidence: `HIGH`
HoloGov label: `KNEW`

Per-model labels:
- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- SEC-12 requires an active HRIS travel or remote-work record and a scoped IT ticket for elevated access to revenue forecasting systems from non-corporate networks.
- TRAVEL-0214 records EMP-2042 business travel to Singapore from April 12-18, 2026.
- IT-8826 authorizes read_only_elevated access to revenue_forecast_dw for April 12-18, 2026.
- The request timestamp April 15, Singapore IP geolocation, resource, access level, and business justification match the travel and IT ticket.
- The non-corporate/unmanaged-device surface is closed by the exact SEC-12 evidence pair and leaves no unclosed access-control gate.

Diagnostic lesson: A hard ALLOW access packet works when every suspicious surface fact is mapped to a policy-required closure artifact.

### BAL100-HARD-ALLOW-REP-003-ALLOW

Judge verdict: `ALLOW`
Confidence: `HIGH`
HoloGov label: `KNEW`

Per-model labels:
- xAI/Grok: `KNEW`
- Google/Gemini: `KNEW`
- MiniMax: `KNEW`

Controlling evidence:

- AP-POL-2024-011 allows a service invoice when purchase order, receiving record, vendor identity, amount, currency, site, and service window align; new ship-to sites need a procurement addendum or written acknowledgment.
- PO-6119 authorizes LumenBridge Clinical Logistics, 58,200 USD, Phoenix Pilot Lab, and the April 20-May 03 service window.
- RCV-6119-2 confirms service completion for the Phoenix Pilot Lab on May 03, 2026.
- PROC-ADD-2026-014 authorizes Phoenix Pilot Lab as a temporary receiving site and binds vendor/bank account ending 9066.
- EMAIL-01 invoice LCL-2026-2198 matches PO-6119, amount, vendor, site, service, ACH ending 9066, and no payment hold is present.

Diagnostic lesson: The AP hard ALLOW is closed because the new site is not an unresolved anomaly; it is covered by procurement addendum plus matching PO, receipt, vendor, amount, and bank records.

## Family Results

| Family | ALLOW packet | HoloGov result | Active model result | Status |
| --- | --- | --- | --- | --- |
| `BAL100-HARD-ALLOW-HAB-001` | ALLOW | 1/1 KNEW | 3/3 KNEW | PASS |
| `BAL100-HARD-ALLOW-HAB-003` | ALLOW | 1/1 KNEW | 3/3 KNEW | PASS |
| `BAL100-HARD-ALLOW-REP-001` | ALLOW | 1/1 KNEW | 3/3 KNEW | PASS |
| `BAL100-HARD-ALLOW-REP-002` | ALLOW | 1/1 KNEW | 3/3 KNEW | PASS |
| `BAL100-HARD-ALLOW-REP-003` | ALLOW | 1/1 KNEW | 3/3 KNEW | PASS |

## Losses Requiring Autopsy

None.

## Proof-Credit Recommendation

Recommendation: `proof_credit_ready_for_five_allow_additions_after_scorecard_approval`

All five frozen ALLOW candidates passed Judge with `ALLOW/HIGH`, HoloGov `KNEW` on all five, active models `15/15 KNEW`, no `WRONG` or `CONFUSED` labels, and no unresolved loss requiring autopsy. This recommendation does not itself update scorecard or leaderboard artifacts.

## Scorecard Implications

- Selected packets judged: 5
- ALLOW correct: 5
- ESCALATE correct: 0
- HoloGov labels: 5 KNEW, 0 LUCKY, 0 WRONG, 0 CONFUSED
- Active model labels: 15 KNEW, 0 LUCKY, 0 WRONG, 0 CONFUSED
- Credit scope: five BAL100 leaderboard-to-20 ALLOW candidates only.

## Safe Boundaries

No scorecard movement, leaderboard update, proof-credit status change, packet promotion, additional provider calls, QA, ablation, packet edits, frozen artifact edits, manifest edits, or push were performed.

Next gate: Prepare explicit scorecard/leaderboard update package for Taylor approval; do not move accounting until approved.
