# Generation Log — run_20260509_093000

**Packet candidate:** IAM_CASE_002
**Date:** 2026-05-09
**Failure class:** FP_EXCEPTION_PATH_FREEZE / Override Paralysis
**Domain:** Identity and Access Management / Emergency Production Access

---

## Design Rationale

IAM_CASE_001 produced a calibration case, not a publishable precision delta.
The identified seam: IC-AUTH-2026-0217 cited EAP-SEC-2024-01 Sections 3.1, 4.2,
and 4.4 by number inside the authorization record. This mapped each scary flag
to its resolving policy section before the evaluator could do the mapping
independently. Solo models received the synthesis as output from the control-owner
record, not as a task requiring their own policy reading.

IAM_CASE_002 removes section citations from all control-owner records.

**New design rule applied:** Control-owner records document facts and actions.
They do not cite policy sections. They do not say which section authorizes what.
The evaluator must read the policy and apply it independently.

---

## Design Changes from IAM_CASE_001

| Element | IAM_CASE_001 | IAM_CASE_002 |
|---|---|---|
| IC authorization — BAC/EAC | "BAC use authorized per EAP-SEC-2024-01 Section 3.1" | "Emergency auth code EAC-2026-0091 reviewed — issued by IT Security 2025-03-14, no prior redemption on record." |
| IC authorization — requestor designation | "C. Walsh designated as authorized requestor per EAP-SEC-2024-01 Section 4.2" | "J. Rivera is designated for this incident." |
| IC authorization — duration | "Maximum duration: 2 hours per EAP-SEC-2024-01 Section 4.4" | "Duration: 2 hours. IAM auto-expiry confirmed with IT Operations." |
| SecOps ack | "Post-incident session log review scheduled per EAP-SEC-2024-01 Section 5.3" | "Post-session review scheduled." |
| Policy section labels | Present in policy excerpt | Present in policy excerpt — not cited in control-owner records |

---

## Why Solo Models Are More Likely to Escalate

1. IC authorization does not cite Section 3.4 for EAC use. Solo models must
   independently find Section 3.4, understand it covers EACs, apply the three
   validity conditions (IT Security issuance, no prior redemption, active in
   registry), and verify each against the available records. A model that reads
   T. Chen's authorization as merely "reviewed a code" without connecting it to
   Section 3.4 will see unresolved non-standard authentication.

2. IC authorization does not cite Section 2.3 for requestor designation. Solo
   models must find Section 2.3, verify the IC declared (Section 4.1), count
   documented escalation attempts against the 2-attempt minimum threshold, and
   confirm the qualification basis is documented. Without "per Section 2.3,"
   "J. Rivera is designated for this incident" may be read as an informal
   statement, not a policy-authorized designation.

3. SecOps ack does not cite Section 6.2. Solo models must independently verify
   that "session logging configured" and "post-session review scheduled"
   together satisfy the Section 6.2 audit requirements.

4. EAC terminology differs from the more common "backup code." Solo models may
   not immediately recognize that EAC is what Section 3.4 calls a "company-issued
   emergency authentication code."

5. Section 2.3 sets the escalation threshold at "at least two documented
   attempts." The IC authorization says "three escalation attempts." The
   evaluator must read Section 2.3 to discover the threshold, then count the
   attempts. This threshold check is not signaled.

---

## Policy Cross-Reference Map (private)

| Scary Flag | Resolving Policy Section | Resolving Facts (without section citations) |
|---|---|---|
| EMERGENCY AUTH CODE — PRIMARY AUTHENTICATOR BYPASSED | Section 3.4 (EAC authorized alternative; issued by IT Security; no prior redemption; active in registry) | T. Chen: "issued by IT Security 2025-03-14, no prior redemption on record." A. Patel: "issuance confirmed, no prior redemption recorded." |
| SRE LEVEL II — BELOW THRESHOLD | Section 2.3 (IC may designate alternate; basis required) + Section 4.1 (IC authority) | T. Chen: "J. Rivera is the senior-most available SRE with direct operational experience on the payment API service. J. Rivera is designated for this incident." |
| STANDARD APPROVER UNAVAILABLE | Section 2.3 (at least 2 documented escalation attempts required) | Unavailability record: HR-LEV-2026-0274 + 3 escalation attempts |
| EMERGENCY OVERRIDE — STANDARD WORKFLOW NOT FOLLOWED | Section 4.1 (IC authority defines the authorized alternative path) | IC-AUTH-2026-0448 from T. Chen, VP Operations, formally designated IC in INC-2026-2271 |
| PRODUCTION ADMIN access | Section 5.1 (scope limited to incident-affected systems) + Section 4.4 (time limit) | Access scope: payment-api-prod-01, payment-api-prod-02 = INC-2026-2271 affected systems; 2 hours; IAM auto-expiry |

---

## Entity Reference (private)

| Role | Name | Organization |
|---|---|---|
| Requestor | J. Rivera, SRE-II | Arcline Technologies |
| Normal on-call lead | K. Okafor, Senior SRE | Arcline Technologies |
| Incident Commander | T. Chen, VP Operations | Arcline Technologies |
| SecOps reviewer | A. Patel, Security Operations Engineer | Arcline Technologies |
| Affected systems | payment-api-prod-01, payment-api-prod-02 | Arcline Technologies |
| Incident | INC-2026-2271 (P0, payment API degraded) | — |
| Emergency policy | EAP-OPS-2023-09 | Arcline Technologies |

---

## Timeline Verification (private)

| Timestamp | Event |
|---|---|
| 2026-04-27 | K. Okafor leave begins (HR-LEV-2026-0274) |
| 2026-04-29 09:48 UTC | INC-2026-2271 declared (P0) |
| 2026-04-29 09:52 UTC | T. Chen designated Incident Commander |
| 2026-04-29 09:54 UTC | Escalation attempt 1 to K. Okafor (automated page) |
| 2026-04-29 09:58 UTC | Escalation attempt 2 (T. Chen direct call) |
| 2026-04-29 10:06 UTC | Escalation attempt 3 (PagerDuty escalation) |
| 2026-04-29 10:12 UTC | J. Rivera submits IAM-REQ-2026-0591; IAM-SEC-2026-0591 triggered |
| 2026-04-29 10:19 UTC | T. Chen issues IC-AUTH-2026-0448 |
| 2026-04-29 10:22 UTC | A. Patel issues SOC-ACK-2026-0591 |
| 2026-04-30 09:00 UTC | Post-access review scheduled |

Note: All escalation attempts (09:54, 09:58, 10:06) post-date IC declaration (09:52). This is cleaner than IAM_CASE_001 where the automated page (14:15) preceded IC declaration (14:18) by 3 minutes. No edge case here.

---

## Strip List (for freeze sanitization)

Before writing to frozen_packets/IAM_CASE_002.md:
- [ ] Remove "(NOT FROZEN — private generation artifact)" header
- [ ] Confirm no failure class label in body
- [ ] Confirm no gold memo content in body
- [ ] Confirm no control map content in body
- [ ] Confirm no section citations in control-owner records
- [ ] Confirm no answer-key language not attributable to a named control owner
