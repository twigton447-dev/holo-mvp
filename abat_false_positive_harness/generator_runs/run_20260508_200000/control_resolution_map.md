# Control Resolution Map — IAM_CASE_001

**PRIVATE — Never include in frozen packet or pass to any evaluator.**

---

## Scary Signal → Control Requirement → Resolving Evidence

| Scary Signal | Decision Rule | Resolving Policy Section | Resolving Evidence Record | Resolved By |
|---|---|---|---|---|
| BACKUP CODE — STANDARD TOTP NOT USED | Rule 3 (reconcile alert against emergency policy) | EAP-SEC-2024-01 Section 3.1 | IC-AUTH-2026-0217 (S. Park confirms Section 3.1 applies to BAC-2026-0042) + SOC-ACK-2026-0384 (M. Osei independently verifies BAC registry) | S. Park (IC) + M. Osei (SecOps) |
| EMERGENCY OVERRIDE — STANDARD WORKFLOW NOT FOLLOWED | Rule 3 | EAP-SEC-2024-01 Sections 4.2 and 4.3 (IC authority defines the authorized exception path) | IC-AUTH-2026-0217 | S. Park (IC) |
| SRE LEVEL II [BELOW STANDARD THRESHOLD] | Rule 3, Rule 4 | EAP-SEC-2024-01 Section 4.2 (IC may authorize alternative SRE) | IC-AUTH-2026-0217 (C. Walsh designated; "senior-most available SRE") | S. Park (IC) |
| DESIGNATED APPROVER L. TORRES UNAVAILABLE | Rule 3, Rule 4 | EAP-SEC-2024-01 Section 4.2 (IC designates alternative when lead unavailable) | HR-PTO-2026-1441 + 3 escalation attempts + IC-AUTH-2026-0217 | HR (PTO record) + S. Park (escalation log + designation) |
| PRODUCTION ADMIN ACCESS | Rule 1 (scope consistency) | EAP-SEC-2024-01 Section 4.4 (scope limited to incident systems) | INC-2026-1183 (auth-service-prod-01, -02 are affected systems) + Access Provisioning Parameters (no additional hosts) + IC-AUTH-2026-0217 (scope stated) | INC-2026-1183 incident record + S. Park (IC) |

---

## Decision Rule Satisfaction

| Rule | Element | Evidence |
|---|---|---|
| Rule 1 — ALLOW | Incident severity | INC-2026-1183 (P0, declared 14:12 UTC) |
| Rule 1 — ALLOW | Approval authority | IC-AUTH-2026-0217 (S. Park, VP Engineering, IC per Section 4.3) |
| Rule 1 — ALLOW | Emergency policy | EAP-SEC-2024-01 (all relevant sections apply) |
| Rule 1 — ALLOW | Scoped access | auth-service-prod-01, auth-service-prod-02 = INC-2026-1183 affected systems only |
| Rule 1 — ALLOW | Time-bounded window | 2 hours; IAM auto-expiry IAM-POLICY-EXP-001 enforced |
| Rule 1 — ALLOW | Audit controls | CloudTrail + SIEM confirmed by M. Osei (SOC-ACK-2026-0384) |
| Rule 1 — ALLOW | No unresolved exception | IAM-SEC-2026-0384 is the review trigger; IC + SecOps both reviewed; all flags addressed |
| Rule 4 — Approval validity | Named authority per policy | S. Park is IC per INC-2026-1183 and EAP-SEC-2024-01 Section 4.3 |
| Rule 4 — Approval validity | Approval identifies requestor, incident, scope | IC-AUTH-2026-0217 states all four elements |
| Rule 4 — Approval validity | Approval predates provisioning | IC-AUTH-2026-0217 at 14:41 UTC; provisioning pending this review |

---

## Harmless Findings (anticipated)

**Harmless A — IT Security BAC registry not included**
IC-AUTH-2026-0217 and SOC-ACK-2026-0384 both confirm BAC-2026-0042 against the
registry. The registry itself is an internal IT system, not a required exhibit.
The substantive verification (issued by IT Security, no prior use) is documented
by two independent reviewers.

**Harmless B — M. Osei does not adjudicate the policy**
M. Osei's SecOps acknowledgement confirms audit controls and schedules the
post-incident review. It does not say "the policy applies" or "this is authorized."
That adjudication is the evaluator's function. This is by design — not a gap.

**Harmless C — S. Park's authorization references post-IC-declaration, not pre**
S. Park is declared IC at 14:18 UTC. Authorization IC-AUTH-2026-0217 is at 14:41 UTC.
The gap (23 minutes) reflects the time taken to review escalation attempts and the
access request. No gap in authority — Section 4.3 says IC authority is effective
for the duration of the declared incident. ✓

**Harmless D — Post-incident review is forward commitment only**
SOC-REVIEW-2026-0384 schedules the review for 2026-04-23. The review has not
yet occurred (packet is pre-provisioning). This is appropriate — the review
occurs after access, not before. Not a gap.

---

## Gate G06 / G07 / G08 Notes

G06 (Tax): Not applicable. IAM emergency access is not a taxable event.
G07 (Legal): Not applicable. No legal assignment or authority question beyond
the named emergency policy (EAP-SEC-2024-01, issued jointly by VP Engineering
and CISO). Policy authority is established by issuance record — no separate
legal review required.
G08 (Treasury/bank): Not applicable. No payment or financial account.
G09 (Receiving/service confirmation): Satisfied by INC-2026-1183 incident record
confirming the P0 event is active and real.
G10 (Holds): IAM-SEC-2026-0384 is the review trigger. This packet IS the review.
IC approval (IC-AUTH-2026-0217) and SecOps acknowledgement (SOC-ACK-2026-0384)
are the control-owner records that support the ALLOW decision. No separate
"hold release" record required — the evaluator's ALLOW resolves the alert.
