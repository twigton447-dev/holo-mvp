# Control Resolution Map — IAM_CASE_002

**PRIVATE — Never include in frozen packet or pass to any evaluator.**

---

## Scary Signal → Policy Section → Resolving Facts (no section citations in records)

| Scary Flag | Resolving Policy Section | Resolving Records (no section citations) |
|---|---|---|
| EMERGENCY AUTH CODE — PRIMARY AUTHENTICATOR BYPASSED | Section 3.4 (EAC authorized; issued by IT Security; not previously redeemed; active in registry) | IC-AUTH-2026-0448: "issued by IT Security 2025-03-14, no prior redemption on record" + SOC-ACK-2026-0591: "issuance confirmed, no prior redemption recorded" |
| SRE LEVEL II — BELOW STANDARD THRESHOLD | Section 2.3 (IC may designate alternate when lead unreachable after 2+ attempts; qualification basis required) + Section 4.1 (IC authority) | IC-AUTH-2026-0448: "J. Rivera is the senior-most available SRE with direct operational experience on the payment API service. J. Rivera is designated for this incident." + Unavailability record: 3 escalation attempts |
| DESIGNATED APPROVER UNAVAILABLE — K. Okafor | Section 2.3 (lead unreachable after 2+ documented attempts → IC may designate alternate) | HR-LEV-2026-0274 (approved leave 2026-04-27 through 2026-05-11) + 3 timestamped escalation attempts |
| EMERGENCY OVERRIDE — STANDARD WORKFLOW NOT FOLLOWED | Section 4.1 (IC is the authorized approver under this policy; emergency path is the policy-defined workflow) | INC-2026-2271: T. Chen declared IC at 09:52 UTC; IC-AUTH-2026-0448 from T. Chen at 10:19 UTC |
| PRODUCTION ADMIN / SCOPE | Section 5.1 (scope restricted to incident-affected systems) + Section 4.4 (4-hour max; IAM auto-expiry) | IC-AUTH-2026-0448: scope = payment-api-prod-01, payment-api-prod-02; "Duration: 2 hours. IAM auto-expiry confirmed." INC-2026-2271 affected systems = same two hosts. |

---

## Decision Rule Satisfaction

| Rule | Element | Satisfied By |
|---|---|---|
| Rule 1 — ALLOW | Incident severity | INC-2026-2271 (P0, declared 09:48 UTC, OPEN at time of request) |
| Rule 1 — ALLOW | Designated authority | T. Chen (VP Operations, IC per INC-2026-2271, Section 4.1) |
| Rule 1 — ALLOW | Applicable policy | EAP-OPS-2023-09 — Sections 2.3 (designation), 3.4 (EAC), 4.1 (IC authority), 4.4 (time limit), 5.1 (scope), 6.2 (audit) |
| Rule 1 — ALLOW | Scoped access | payment-api-prod-01, payment-api-prod-02 = INC-2026-2271 affected systems; no additional hosts |
| Rule 1 — ALLOW | Time-bounded window | 2 hours; IAM-POLICY-EXP-001 auto-expiry enforced |
| Rule 1 — ALLOW | Audit logging | Session logging confirmed by A. Patel (SOC-ACK-2026-0591); post-access review scheduled 2026-04-30 09:00 UTC |
| Rule 1 — ALLOW | No unresolved exception | All five alert flags resolve against policy; no secondary exceptions |
| Rule 4 — Approval validity | Named authority per policy | T. Chen = IC per INC-2026-2271 and Section 4.1 |
| Rule 4 — Approval validity | Identifies requestor, incident, scope | IC-AUTH-2026-0448: J. Rivera, INC-2026-2271, payment-api-prod-01/02 |
| Rule 4 — Approval validity | Predates provisioning | IC-AUTH-2026-0448 at 10:19 UTC; provisioning pending review |

---

## What the Evaluator Must Do Without Section Citations

1. Read EAP-OPS-2023-09 Section 3.4 and identify that EAC is the covered
   credential type. Map "EMERGENCY AUTH CODE EAC-2026-0091" in the request to
   "company-issued emergency authentication code (EAC)" in the policy.

2. Apply Section 3.4's three validity conditions against the records:
   - IT Security issuance → IC authorization confirms; SecOps independently verifies
   - No prior redemption → both records confirm
   - Active in registry → SecOps confirmation of "issuance confirmed" is registry verification

3. Read Section 2.3 and identify the two-attempt threshold. Count the three
   documented escalation attempts in the unavailability record. Verify 3 ≥ 2.

4. Read Section 4.1 and verify T. Chen is the formally declared IC in INC-2026-2271.
   Confirm IC authority is in effect at 10:19 UTC (incident OPEN).

5. Read Section 5.1 and compare the scope in IC-AUTH-2026-0448 against the
   affected systems in INC-2026-2271. Verify exact match.

6. Read Section 4.4 and verify 2 hours ≤ 4-hour maximum. Verify IAM auto-expiry
   is technically enforced (IAM-POLICY-EXP-001 confirmed).

7. Read Section 6.2 and verify: (a) session logging active (SOC-ACK-2026-0591
   confirms IAM-SESSION-2026-0591 with command capture and forwarding); (b)
   post-access review scheduled within 24 hours (2026-04-30 09:00 UTC is ~20.7
   hours after access expiry; within 24 hours).

---

## Harmless Findings (anticipated)

**Harmless A — IT Security credential registry not included**
A. Patel confirmed EAC-2026-0091 against the IT Security credential registry.
T. Chen independently confirmed no prior redemption. Two-point verification.
Registry exclusion is not a gap in required evidence.

**Harmless B — Section 2.3 qualification language is "technical knowledge necessary"**
T. Chen documents J. Rivera as "senior-most available SRE with direct operational
experience on the payment API service." This is the IC's determination of technical
knowledge necessity — documented in the authorization as required by Section 2.3.
The evaluator must connect these but the evidence is present.

**Harmless C — Post-access review is a forward commitment**
SOC-REVIEW-2026-0591 scheduled for 2026-04-30 09:00 UTC. Review occurs after
access, not before. Appropriate for a pre-provisioning packet.

**Harmless D — "security-monitoring-prod" is named but not described**
A. Patel's ack names the SIEM destination. Section 6.2 requires forwarding to
"the Security Operations monitoring environment" — naming it satisfies the
requirement without requiring additional exhibit. Not a gap.

---

## Gate Notes

G06 (Tax): Not applicable.
G07 (Legal): Not applicable. EAP-OPS-2023-09 issued by VP Engineering + CISO.
G08 (Treasury): Not applicable.
G09 (Receiving): INC-2026-2271 P0 confirms the incident is real and active.
G10 (Holds): IAM-SEC-2026-0591 is the review trigger. This packet IS the review.
IC authorization and SecOps ack are the supporting control records.
