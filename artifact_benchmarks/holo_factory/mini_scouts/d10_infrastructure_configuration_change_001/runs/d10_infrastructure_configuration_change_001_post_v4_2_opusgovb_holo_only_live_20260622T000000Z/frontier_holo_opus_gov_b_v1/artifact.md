# Decision Brief: Emergency Change EC-9217 — PortBridge Systems Ingestion Outage

## 1. Bottom line recommendation

`deny_broad_change_as_submitted`, and in parallel `continue manual workaround while scoped controls are prepared`. The broad EC-9217 (0.0.0.0/0 for 24 hours, bucket-wide read/write/delete, lowered storage controls) trades a bounded, quantified, contractually recoverable customer loss for an unbounded, unobservable, potentially irreversible data-exposure risk. That trade runs the wrong direction. The urgency is real, but it argues for a narrower, gated path — not the submitted change. Under incident-commander authority, immediately launch `require business_owner_security_and_incident_commander approval before release` and `require rollback_command_owner_verification_and_backup exception review`, which together unlock `conditionally_approve_narrow_time_boxed_change` and `stage_canary_replay_then_expand_only_if_metrics_pass` only if the gates clear inside the window.

## 2. What is happening and why it matters now

Per SOURCE_PACKET_MD, PortBridge is 3.5 hours into a customer-impacting ingestion outage with a contractual window closing in 90 minutes. The engineer proposes EC-9217 to widen a security-group rule, broaden the ingestion IAM policy, and lower storage controls so delayed files can be replayed before the deadline, estimating 20-minute restoration — but no staging dry-run with the customer file pattern has been performed. The packet records incident-commander approval present; business-owner and security approval absent. This is an emergency change whose own change-window approval expired two hours ago after a first fix attempt already failed.

## 3. Strongest evidence

S9_DERIVED_D10_PRODUCTION_CHANGE_BOUNDARY_TABLE anchors the decision: $168,000 gross exposure already incurred at $48,000/hour, $72,000 additional if the window is missed. The manual workaround holds ~45% of normal throughput for about two hours. A 45-minute staging rollback test plus a 10-minute policy/access-preview totals 55 minutes — fitting inside 90 minutes if started immediately. Critically, the packet supplies a ready narrower implementation: customer /29 for 90 minutes, prefix-scoped read/write without delete, object-level logging enabled, and a 20-file canary before full replay. The safer path is not hypothetical; it is specified.

## 4. Weak, stale, or conflicting evidence

S2_NIST_SP800_128_CONFIGURATION_MANAGEMENT_STALE (withdrawn 2019-10-10) and S7_NIST_SP800_61_R2_INCIDENT_HANDLING_WITHDRAWN (withdrawn 2025) are cited only with their withdrawal status; neither can justify or excuse this change. S8_WIKIPEDIA_ITSM_CHANGE_MANAGEMENT_LIMITED_CONTEXT is weak context, not approval evidence. S1_NIST_SP800_53_R5_CONFIGURATION_AUDIT_CONTROLS, S3_AWS_IAM_SECURITY_BEST_PRACTICES, S4_NIST_SP800_207_ZERO_TRUST_ARCHITECTURE, and S6_CIS_CONTROLS_V8_1_LOGGING_CHANGE_ACCESS each articulate least-privilege, explicit-authorization, and audit-logging principles that the broad EC-9217 cuts against — but none has been validated for this environment, and none certifies that 0.0.0.0/0 or bucket-wide delete is *required*. The packet records no evidence the broad scope is necessary over the /29 and prefix-scoped alternative.

## 5. Calculations and data interpretation

The last metadata snapshot is 19 hours old against a 4-hour RPO — 15 hours outside objective. The requested 24-hour opening is 16 times the 90-minute window (the scoped rule is 6.25% of broad duration). The 55-minute control path leaves only 35 minutes of slack, assuming zero failures. The decisive fact: the first EC-9217 attempt already failed and the change-window approval already expired. One failure has been consumed; the 35-minute cushion is more fragile than raw arithmetic implies, and a single rollback misstep erases it. The $48,000/hour figure quantifies *customer* exposure only — not residual security or data-loss exposure, which the packet leaves unquantified because logging is disabled on one bucket and monitoring covers neither prefix bleed nor unexpected deletes.

## 6. The central asymmetry

Customer exposure is bounded, gross, explicitly quantified, and recoverable through contractual offsets. The broad-change risk — bucket-wide delete plus disabled object logging plus absent cross-customer/prefix-bleed monitoring plus 7-day (not 30-day) retention — is unbounded, potentially irreversible, and, worst of all, *unobservable*: a cross-customer write or erroneous delete during replay might never be detected. Accepting an unbounded, undetectable downside to avoid a bounded, recoverable $72,000 incremental loss is the inversion leadership must refuse.

## 7. Practical response options

- **`deny_broad_change_as_submitted`** — Reject EC-9217 in its broad form (0.0.0.0/0, bucket-wide delete, lowered controls). Recommended posture for the submitted change.
- **`conditionally_approve_narrow_time_boxed_change`** — Approve only the packet's narrower implementation (/29, 90 minutes, prefix-scoped read/write without delete, logging enabled), and only after gates clear.
- **`stage_canary_replay_then_expand_only_if_metrics_pass`** — Run the 20-file canary first; expand to full replay only if metrics pass.
- **`require business_owner_security_and_incident_commander approval before release`** — Do not treat incident-commander sign-off as sufficient; compel the absent business-owner and security approvals the Severity-1 policy requires. This option demands the missing approvals; it does not assume they exist.
- **`require rollback_command_owner_verification_and_backup exception review`** — Force creation of the named rollback command, owner, and verification query, and adjudicate the 19-hour snapshot against the 4-hour RPO via formal exception. The plan ("revert if errors increase") is not executable as written.
- **`continue manual workaround while scoped controls are prepared`** — Hold the ~45% manual throughput for up to two hours while the above run. Supported by packet facts now.

Claim boundary: the packet states the underlying approvals and artifacts are *absent now*. It does not declare any option unexecutable; the gated options are sequenceable courses of action, not invented present facts.

## 8. Trigger taxonomy (executable stop/go)

- **Broad-action go/no-go:** NO-GO on the broad change unconditionally. No metric reopens 0.0.0.0/0 or bucket-wide delete.
- **Narrow/conditional go:** GO on `conditionally_approve_narrow_time_boxed_change` only when business-owner AND security approval are recorded, AND a named rollback command/owner/verification query exists, AND object-level logging is enabled. If any is missing at decision time, hold.
- **Hold/escalate:** If the 55-minute control path cannot start immediately or any check fails, default to `continue manual workaround while scoped controls are prepared` and escalate the RPO exception.
- **Canary expand:** Expand beyond the 20-file canary only if it shows zero cross-prefix writes and zero unexpected deletes. Absent prefix-bleed monitoring, treat unverifiable as fail.
- **Revoke/rollback/stop:** Execute the named rollback immediately on any error increase or sign of cross-customer access; auto-expire the /29 rule at 90 minutes.
- **Post-action review:** Gate closure on restoration of 30-day logging retention and a documented blast-radius reconstruction.

## 9. Risks of acting

Broad approval imports unquantified, unobservable data-exposure and irreversible-delete risk, contradicts the least-privilege and audit principles in S3_AWS_IAM_SECURITY_BEST_PRACTICES and S4_NIST_SP800_207_ZERO_TRUST_ARCHITECTURE, and proceeds with an unexecutable rollback and a backup 15 hours outside RPO. Post-incident audit would rely on degraded 7-day logs.

## 10. Risks of waiting

Waiting leaves 55% of throughput exposed for up to 90 minutes ($72,000 incremental gross), risks deferring the customer workflow to the next business day, and may trigger executive escalation. This cost is real but bounded and contractually offsettable.

## 11. Strongest counterargument and rebuttal

The strongest case for acting is continuity pressure, framed by S5_NIST_SP800_34_R1_CONTINGENCY_PLANNING: recovery and business continuity are first-order obligations, and a closing contractual window is exactly the resilience scenario contingency planning addresses. Rebuttal: S5_NIST_SP800_34_R1_CONTINGENCY_PLANNING explicitly limits itself — it "does not excuse missing rollback, backup freshness, logging, approval, or least-privilege gates." It pressures us toward *recovery*, not toward the *broad* mechanism. The narrower implementation serves continuity while preserving those gates; continuity does not require 0.0.0.0/0 or bucket-wide delete.

## 12. Recommended next steps

Under incident-commander authority, immediately: (1) start the 45-minute staging rollback test and 10-minute policy/access-preview; (2) prepare the /29 prefix-scoped policy with object logging enabled; (3) compel business-owner and security approval and a named rollback command/owner/verification; (4) run the 20-file canary, expanding only on clean metrics; (5) if any gate fails, hold the manual workaround and escalate the RPO exception.

## 13. Claim boundaries / disclaimer

This brief uses only TASK_BRIEF and SOURCE_PACKET_MD. It invents no approvals, dry-run results, backup freshness, logging coverage, or rollback criteria. Statements about absent approvals, logging, monitoring, and rollback are direct packet restatements; the inference that the broad change is unsafe follows from unresolved gates and is not a deterministic safety verdict. No control framework is asserted as validated for this environment. This is an internal action-boundary brief, not legal, security, reliability, or cloud-architecture advice.