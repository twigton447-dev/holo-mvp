# Decision Brief: Emergency Change EC-9217 — PortBridge Systems Ingestion Outage

## 1. Bottom line recommendation

**Deny broad EC-9217 as submitted.** Authorize only a narrow, time-boxed, observable, reversible emergency attempt — customer /29 for 90 minutes, prefix-scoped read/write without delete, object-level logging on every touched bucket and prefix, and a 20-file canary — and only if the missing approvals, scoped access, logging/query coverage, rollback mechanics, and backup-exception review clear immediately. If any of those gates cannot be measured before the customer window becomes unrecoverable, continue the manual workaround and escalate rather than widen blast radius blindly. The outage is real and expensive, but speed without reversibility is not execution readiness.

## 2. What is happening and why it matters now

PortBridge Systems is 3.5 hours into a customer-impacting ingestion outage; a major customer's contractual processing window closes in 90 minutes. EC-9217 would open TCP 443 from 0.0.0.0/0 to the ingestion edge for 24 hours, grant the ingestion role read/write/delete across two production buckets, and lower storage-blocking controls so delayed files can be replayed. Urgency is genuine: the customer estimates $48,000/hour, and missing the window may defer workflow to the next business day and trigger executive escalation.

The problem is that the submitted change is far broader than the known need. The customer source range is a /29, yet the rule opens 0.0.0.0/0. Replay needs the customer ingest prefix, yet the grant spans two whole buckets including delete. These are not paperwork defects — they are precisely the controls that let leadership detect, contain, and reverse a bad emergency change, and the packet shows them missing.

## 3. Strongest evidence

The quantitative case is anchored in S9_DERIVED_D10_PRODUCTION_CHANGE_BOUNDARY_TABLE: 3.5 hours at $48,000/hour implies $168,000 gross exposure now; a further 90 minutes is a $72,000 gross ceiling; the manual workaround covers 45 percent throughput, leaving 55 percent exposed; a 90-minute scoped rule is only 6.25 percent of the requested 24-hour opening by duration; and a 45-minute staging rollback test plus a 10-minute policy/access preview totals 55 minutes, fitting inside 90 minutes only if started immediately and no failures appear.

The case against the broad submission is that narrower alternatives exist and core gates are unresolved. The packet itself supplies the narrower implementation: customer /29 for 90 minutes, prefix-scoped read/write without delete, object-level logging, and a 20-file canary. Control disciplines reinforce that path without auditing this change: S3_AWS_IAM_SECURITY_BEST_PRACTICES supports least privilege, conditions, Access Analyzer, and policy validation; S4_NIST_SP800_207_ZERO_TRUST_ARCHITECTURE supports explicit authorization rather than implicit trust from network location; S1_NIST_SP800_53_R5_CONFIGURATION_AUDIT_CONTROLS supports formal change control, logging, and risk-based selection over ad hoc change; S6_CIS_CONTROLS_V8_1_LOGGING_CHANGE_ACCESS supports audit log and change discipline. None proves this environment or policy was validated; each is principle, not incident-specific clearance.

## 4. Weak, stale, or conflicting evidence

The engineer's 20-minute restoration belief is relevant but weak: no staging dry-run was performed with the customer file pattern. Incident commander approval exists, but business-owner and security approval are not provided, and the change-window approval expired 2 hours ago after the first fix failed — three separate unresolved gates, not one.

S5_NIST_SP800_34_R1_CONTINGENCY_PLANNING is the contradiction hot-spot: it supports continuity and recovery pressure (favoring action), but its own limitation states it does not excuse missing rollback, backup freshness, logging, approval, or least-privilege gates. It is used here only with that limiter, never as a green light. S2_NIST_SP800_128_CONFIGURATION_MANAGEMENT_STALE (withdrawn), S7_NIST_SP800_61_R2_INCIDENT_HANDLING_WITHDRAWN (withdrawn), and S8_WIKIPEDIA_ITSM_CHANGE_MANAGEMENT_LIMITED_CONTEXT (weak) are contextual only and carry no decision weight.

## 5. Calculations or data interpretation

Per S9_DERIVED_D10_PRODUCTION_CHANGE_BOUNDARY_TABLE, current gross exposure is $168,000 and a further 90-minute delay carries a $72,000 gross ceiling before offsets. The workaround covers 45 percent throughput. A naive linear estimate would leave 55 percent of $72,000, or $39,600, at risk — but this is an **unproven linear inference**, not a packet fact; the packet does not state exposure scales linearly or that partial throughput satisfies the contractual window. The backup is materially out of objective: a 19-hour snapshot against a 4-hour RPO is a 15-hour miss. The 55-minute validation figure is a **best-case validation subset only**; it excludes obtaining approvals, renewing the change window, implementing the narrowed change, running and analyzing the canary, and completing actual replay.

## 6. Practical response options

- **deny_broad_change_as_submitted** — Reject EC-9217 as written; its 24-hour 0.0.0.0/0 opening, bucket-wide read/write/delete, expired window, incomplete approvals, stale backup, partial logging, blind monitoring, and vague rollback create unbounded execution risk.
- **conditionally_approve_narrow_time_boxed_change** — Permit only customer /29 for 90 minutes, prefix-scoped read/write without delete, explicit expiry, logging on every touched bucket/prefix. Conditional, not assumed safe.
- **stage_canary_replay_then_expand_only_if_metrics_pass** — Run the 20-file canary first; expand only on positive evidence, using metrics that directly observe delete calls, cross-customer access, and prefix bleed — not just global 5xx.
- **require business_owner_security_and_incident_commander approval before release** — Severity 1 emergency change needs all three; the packet has incident commander only. The expired change window must be renewed or replaced, separately.
- **require rollback_command_owner_verification_and_backup exception review** — Two distinct gates: procedural reversibility (exact rule ID, IAM policy version, storage setting, owner, command, verification query, success criterion) and data recoverability (accept/reject the 15-hour RPO miss).
- **continue manual workaround while scoped controls are prepared** — The bridge state at 45 percent throughput, not a final recovery strategy.

## 7. Risks of acting

Approving the broad change trades a known outage for less-bounded confidentiality, integrity, deletion, and recovery risk. The packet gives no evidence 0.0.0.0/0 is required over the /29, no proof bucket-wide delete is necessary, and no dry-run. Because object-level logging is disabled on one bucket and monitoring lacks cross-customer/delete/prefix-bleed alerts, such failures would be hard to see and prove contained. The "revert if errors increase" rollback lacks rule ID, policy version, owner, command, and verification query. Disclosure, deletion, corrupted replay state, and a missed window may not be reversible after the fact; the 19-hour snapshot means metadata recovery may not meet the 4-hour RPO.

## 8. Risks of waiting

Waiting is not harmless. Another 90 minutes carries a $72,000 gross ceiling per S9_DERIVED_D10_PRODUCTION_CHANGE_BOUNDARY_TABLE; the workaround leaves 55 percent exposed; missing the window may defer workflow and trigger escalation. A blanket block could convert a contained technical incident into contractual and executive fallout. The recommendation is therefore not "wait for perfect" — it is move immediately through a narrowed, testable, reversible path.

## 9. Recommended next steps — executable trigger taxonomy

- **Broad-action go/no-go:** NO-GO on EC-9217 as submitted.
- **Narrow/conditional go:** GO on the scoped change only if all minimum gates are green: business-owner, security, and incident commander approvals present; change window renewed/replaced; customer /29 and 90-minute expiry; prefix-scoped read/write without delete; policy-lint/access-preview clean; object-level logging and query coverage on every touched bucket/prefix; rollback owner, exact command, identifiers, verification query, and success criterion documented; backup/RPO exception accepted by an accountable owner; 20-file canary ready.
- **Canary-expansion go:** Expand only on positive evidence — expected files replay, writes confined to the customer prefix, no unexpected deletes, no cross-customer access, no prefix bleed, no material 5xx rise, rollback verification tested. Absence of alarms is insufficient because those alerts do not currently exist.
- **Hold/escalate:** If any gate cannot be measured before the window becomes unrecoverable, continue the manual workaround and escalate the customer-impact decision.
- **Revoke/rollback/stop:** Stop on unexpected delete calls, cross-customer access, prefix bleed, material 5xx increase, failed rollback verification, logging/query failure, access-preview showing broader-than-approved access, or divergence from scoped configuration.
- **Post-action review:** Expire the rule at 90 minutes, remove emergency policy, reconcile replay outputs, review logs, and document the control gaps that forced this posture.

## 10. Strongest counterargument and answer

The strongest temptation: the window closes in 90 minutes, exposure is already $168,000, and the engineer believes broad EC-9217 restores service in 20 minutes — so approve it. The disciplined answer: the packet provides no proof 0.0.0.0/0 is required over the /29, no proof bucket-wide delete is necessary, no dry-run, no current business-owner/security approval, no RPO-compliant snapshot, no exact rollback, and no monitoring for the exact failure modes the broad change would create. The narrow path is not delay for perfection; it is the fastest responsible route that preserves least privilege and detectability while staying reversible.

## 11. Claim boundaries / disclaimer

This brief uses only the frozen packet. It does not prove the narrow change is safe, that staging will pass, that backups are acceptable, or that monitoring is sufficient — only that the narrow path is the least-bad actionable path under uncertainty. The $39,600 figure is an unproven linear inference; $72,000 is the gross ceiling. This is an internal action-boundary decision brief under uncertainty, not legal, security, reliability, or cloud-architecture advice.