# Frozen Source Packet: D8 IT Access Provisioning

Packet ID: `d8_it_access_provisioning_001`

Contestants must use only the frozen source excerpts and case facts below. Do not browse. Do not invent missing facts.

## Crisis Frame
Urgent privileged production access request with unresolved approval, identity, least-privilege, logging, time-boxing, revocation, and separation-of-duties gates.

## Decision Question
Should IT/security leadership allow, block, escalate, time-box, modify, or conditionally approve the requested privileged production access before execution?

## Case Facts

- Company profile: A fictional SaaS payments platform, ClearLedger Systems, uses a managed service provider for production database support and has a privileged-access workflow for emergency incidents.
- Decision time: The incident bridge is live at 14:20 ET. A customer-facing payment reconciliation service has been degraded for 5.5 hours, and the operations lead wants a decision within 30 minutes.
- Proposed action: Grant a contractor database engineer from the support vendor temporary production admin access to run a schema repair and backlog replay on the primary reconciliation database.

### Operational Urgency
- Estimated gross revenue processing exposure is $220,000 per hour while the reconciliation service is degraded.
- A manual workaround is available for priority customers but supports only 35 percent of normal throughput and adds next-day reconciliation risk.
- The vendor engineer says the repair will take 40 minutes if full admin access is granted.
- Internal database staff can attempt a narrower repair path in about 4 hours, but they lack the vendor engineers module-specific migration scripts.

### Access Request Facts
- The request asks for production database admin plus cloud console admin on the reconciliation environment, even though the stated repair is database schema and backlog replay.
- Manager approval is attached, but it is 38 days old and was for read-only diagnostic access during a prior incident.
- The request references incident INC-7421, while the current incident bridge and change calendar reference INC-7814 and emergency change EC-1149.
- The contractor account passed MFA enrollment 11 months ago, but the identity-assurance record does not show current employment verification or vendor reauthorization for this incident.
- The access form leaves expiration as "until resolved" and does not name a revocation owner.
- Audit logging is enabled for database queries, but privileged session recording for cloud console actions is not enabled on the contractor account.
- The same vendor engineer prepared the migration script and is requesting rights to run it in production without a second operator or peer approval.

### Control Environment Facts
- Policy permits emergency access when there is a Severity 1 incident, a linked incident/change record, named business owner approval, security officer approval, time-boxed duration, activity logging, and post-access review.
- The request currently has no named business owner approval, no security officer approval, no specific expiration time, and no revocation ticket.
- A narrower emergency role exists that allows stored-procedure execution and backlog replay but does not allow cloud console admin or database user-management changes.
- Privileged access tooling can issue the narrower role for 2 hours with session recording if approved by the on-call security officer and database owner.

### Not Provided
- No current manager approval for the requested scope.
- No evidence that INC-7421 and INC-7814 are the same incident or that EC-1149 authorizes the requested access.
- No current contractor employment or vendor authorization attestation.
- No business owner approval, security officer approval, or database owner approval for the requested broad role.
- No defined expiration time, revocation owner, or post-access review ticket.
- No proof that cloud console admin is required for the stated database repair.
- No session recording for the broad requested role.

### Calculations To Check
- At $220,000 per hour, four more hours of degraded service equals $880,000 gross processing exposure before customer prioritization, recovery, and actual revenue recognition effects.
- The service has already been degraded for 5.5 hours, implying $1.21 million of gross processing exposure at the same rate before offsets.
- The manual workaround covers 35 percent of normal throughput, leaving 65 percent exposed while waiting.
- A 2-hour time-boxed narrower role is 120 minutes; the vendor estimates a 40-minute repair, leaving about 80 minutes for verification and supervised rollback before expiration.
- The attached approval is 38 days old and for read-only access, while the current request is for production database admin plus cloud console admin.

## Claim Boundaries
- Do not approve full admin access solely because the incident is urgent.
- Do not claim the contractor identity, vendor employment, incident linkage, change authorization, or security approval is current when the packet does not show it.
- Do not treat stale read-only approval as approval for broad production admin access.
- Do not claim broad cloud console admin is necessary when a narrower emergency role exists and the stated repair is database-focused.
- Do not ignore time-boxing, logging, session recording, revocation, and post-access review requirements.
- Do not give legal, security, compliance, or incident-response advice; write an internal action-boundary decision brief under uncertainty.

## Practical Response Options Required
- deny_broad_admin_request_as_submitted
- conditionally_approve_narrow_time_boxed_emergency_role
- escalate_to_security_officer_database_owner_and_business_owner
- require_ticket_change_linkage_and_identity_reverification_before_release
- use_internal_database_staff_or supervised_pair_operation_if gates cannot clear
- extend manual workaround and customer triage while access gates are completed

## Evidence Uncertainty Requirements
- Separate operational urgency from authorization sufficiency.
- Carry missing ticket linkage, stale approval, identity assurance, least privilege, logging, and revocation gaps into the recommendation.
- Show the outage exposure and time-box arithmetic without converting it into automatic approval.
- Compare broad admin, narrower emergency role, denial, escalation, and supervised-access options.
- Define stop/go triggers for release, escalation, revocation, and post-access review.

## Frozen Sources

### S1_NIST_SP800_53_R5_ACCESS_AUDIT_CONTROLS: Security and Privacy Controls for Information Systems and Organizations, SP 800-53 Rev. 5
- Publisher: National Institute of Standards and Technology
- Date: 2020-09-23; updated 2025-01-09 page metadata
- URL/Citation: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- Source type: authoritative_identity_access_control_and_audit_source
- Strength classification: strong
- Source hash: `d7757c178274d31660321cfac6e845a35e00481fa82f1441b24c40a10863834d`
- Excerpt: NIST SP 800-53 Rev. 5 provides a catalog of security and privacy controls for information systems and organizations. The publication includes access control, audit and accountability, identification and authentication, incident response, risk assessment, system and communications protection, and supply-chain risk management control families. It is a control catalog for selecting and tailoring controls rather than a one-click access approval.
- Limitations: Authoritative control catalog, but not the companys policy, ticket system, or final approval for this contractor access request.

### S2_NIST_SP800_207_ZERO_TRUST_ARCHITECTURE: Zero Trust Architecture, SP 800-207
- Publisher: National Institute of Standards and Technology
- Date: 2020-08-11
- URL/Citation: https://csrc.nist.gov/pubs/sp/800/207/final
- Source type: authoritative_least_privilege_and_policy_decision_source
- Strength classification: strong
- Source hash: `940b0afaca940a291bc7ba9738b4f364ec62ca117f94706f9e34614ba68cd2bb`
- Excerpt: NIST SP 800-207 describes zero trust as a cybersecurity paradigm focused on resource protection and the premise that trust is never granted implicitly but must be continually evaluated. It emphasizes policy decisions based on identity, device, application/service, data, and environmental attributes, and it supports least-privilege and explicit authorization for each access request.
- Limitations: Authoritative architecture guidance, not an incident-specific instruction to deny or approve this request.

### S3_NIST_SP800_63B_DIGITAL_IDENTITY_AUTHENTICATION: Digital Identity Guidelines: Authentication and Authenticator Management, SP 800-63B
- Publisher: National Institute of Standards and Technology
- Date: SP 800-63-4 public text current at access date
- URL/Citation: https://pages.nist.gov/800-63-4/sp800-63b.html
- Source type: authoritative_identity_assurance_source
- Strength classification: strong
- Source hash: `d5910bbf573c821dadb9f49a1eaf63a9f2dec320c2dfe8a79aebf23a08e34bd9`
- Excerpt: NIST digital identity guidance covers authentication and authenticator management, including requirements for authenticators, verification, lifecycle management, and reauthentication. It supports the principle that access decisions require current identity assurance and authenticator controls rather than stale enrollment evidence alone.
- Limitations: Digital identity guidance, not the contractor employment record, vendor authorization record, or access approval.

### S4_MICROSOFT_ENTRA_EMERGENCY_ACCESS_ACCOUNTS: Manage emergency access accounts in Microsoft Entra ID
- Publisher: Microsoft Learn
- Date: Current Microsoft Learn page at access date
- URL/Citation: https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access
- Source type: emergency_break_glass_access_source
- Strength classification: contradictory_or_complicating
- Source hash: `91a2ae768344cc3032f0c9388cd64798f8a469a0c86ceaa4fde453e01293fd7e`
- Excerpt: Microsoft guidance says organizations should create emergency access accounts to prevent being accidentally locked out of administrative access and should monitor sign-ins and audit logs. Emergency accounts are meant for exceptional circumstances, should be excluded from some policies that might block access, and should be protected, tested, and monitored rather than used as ordinary standing privilege.
- Limitations: Useful break-glass guidance, but it is product-specific and does not prove this contractor needs broad admin access or that monitoring/revocation gates are satisfied.

### S5_CIS_CONTROLS_V8_1_ACCESS_LOGGING: CIS Critical Security Controls v8.1
- Publisher: Center for Internet Security
- Date: Version 8.1 page current at access date
- URL/Citation: https://www.cisecurity.org/controls/cis-controls-list
- Source type: audit_logging_and_access_management_source
- Strength classification: useful_normal
- Source hash: `398b8fc6c9bcdeec9338eaeddb8bdde1330c0b4459cb16bf40ce3f76eb669e59`
- Excerpt: CIS Controls v8.1 lists security control areas including account management, access control management, audit log management, continuous vulnerability management, secure configuration, data protection, incident response management, and service provider management. These controls support structured access approval, logging, and provider oversight rather than unmanaged emergency privileges.
- Limitations: Useful control framework, but not a facility-specific approval, ticket record, or proof that every control is implemented in this environment.

### S6_NIST_SP800_161_R1_THIRD_PARTY_SUPPLY_CHAIN_RISK: Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations, SP 800-161 Rev. 1
- Publisher: National Institute of Standards and Technology
- Date: 2022-05-05 final; CSRC page current at access date
- URL/Citation: https://csrc.nist.gov/pubs/sp/800/161/r1/final
- Source type: third_party_contractor_access_risk_source
- Strength classification: useful_normal
- Source hash: `1bab7759bd451e67e812abf49e43c8f30580c0fa4dbb0f93b4c15e44f9ad532c`
- Excerpt: NIST SP 800-161 Rev. 1 addresses cybersecurity supply-chain risk management and says organizations are concerned about products and services that may contain malicious functionality, be counterfeit, or be vulnerable because of poor supply-chain practices. It gives guidance for identifying, assessing, and mitigating risks across organizational levels and supplier relationships.
- Limitations: Useful third-party risk source, but not evidence that this contractor is malicious or that access must be denied; it supports supplier-access scrutiny and control gates.

### S7_NIST_SP800_61_R2_INCIDENT_HANDLING_STALE: Computer Security Incident Handling Guide, SP 800-61 Rev. 2
- Publisher: National Institute of Standards and Technology
- Date: 2012-08-06; withdrawn 2025-04-03
- URL/Citation: https://csrc.nist.gov/pubs/sp/800/61/r2/final
- Source type: stale_incident_response_source
- Strength classification: stale_tempting
- Source hash: `45672ae4b3e224f5fa538962d35ad185066a3d6852450ae0d3cabf102d30fd7d`
- Excerpt: NIST identifies SP 800-61 Rev. 2 as a computer security incident handling guide that was withdrawn on 2025-04-03. It remains directionally useful for incident-response concepts such as preparation, detection and analysis, containment, eradication, recovery, and post-incident activity, but it should not be treated as current controlling guidance.
- Limitations: Stale/withdrawn source. It is tempting because it supports urgent incident handling, but it cannot override current access-control, identity, logging, and revocation requirements.

### S8_WIKIPEDIA_PRIVILEGED_ACCESS_MANAGEMENT_LIMITED_CONTEXT: Privileged access management
- Publisher: Wikipedia contributors
- Date: Living public encyclopedia page; accessed 2026-06-21
- URL/Citation: https://en.wikipedia.org/wiki/Privileged_access_management
- Source type: weak_contextual_privileged_access_source
- Strength classification: weak_or_limited
- Source hash: `971e963046f09b24147b4b6955f8d48e3c9a5992eec991ddc6ec7e48b894f92f`
- Excerpt: The public encyclopedia page gives general context on privileged access management as a security discipline for accounts and users with elevated permissions. It is useful background for why privileged roles need special control, but it is not authoritative policy, incident evidence, or approval for a production access change.
- Limitations: Weak contextual source only. It must not carry the action recommendation or substitute for access-control, identity, logging, or incident-response controls.

### S9_DERIVED_D8_ACCESS_BOUNDARY_TABLE: D8 derived access-boundary table from frozen case facts and public-source disciplines
- Publisher: Packet compiler using S1-S8 and case facts
- Date: 2026-06-21
- URL/Citation: Derived from D8 case facts plus S1-S8 source-boundary disciplines in this packet.
- Source type: table_chart_stat_element
- Strength classification: table_chart_stat_element
- Source hash: `706a5b4a26b29defdd4cdf3fb23978ffd2197097ccb73709e9f8be66765e6b72`
- Excerpt: Quantitative access-boundary table: degraded service exposure is $220,000 per hour; four additional hours equals $880,000 gross processing exposure before offsets; 5.5 hours already degraded implies $1.21 million gross exposure at the same rate. The manual workaround covers 35 percent of normal throughput, leaving 65 percent exposed. A 2-hour emergency role gives 120 minutes; against a 40-minute repair estimate, about 80 minutes remain for verification and supervised rollback before expiration. The attached manager approval is 38 days old and was for read-only access, while the current request is for production database admin plus cloud console admin.
- Limitations: This is a frozen decision table, not an access approval, incident record, identity attestation, or legal/compliance conclusion. Artifacts must show the arithmetic and preserve unresolved access gates.
