# HoloEngine Buyer Claim Register v0.1

Program: HoloEngine Trust & Assurance Program

From: HoloOps SOC / Taylor

To: HoloOps SOC and Taylor

Status: Buyer claim register draft

Date: 2026-07-07

Source artifacts used:

- `docs/trust/HOLOENGINE_DATA_FLOW_ARCHITECTURE_V0_1.md`
- `docs/trust/HOLOENGINE_SOC2_READINESS_GAP_ASSESSMENT_V0_1.md`
- `docs/trust/HOLOENGINE_PROVIDER_DATA_HANDLING_MATRIX_V0_1.md`
- `docs/trust/HOLOENGINE_TRUST_EVIDENCE_BINDER_INDEX_V0_1.md`

## Purpose And Claim Boundary

This register controls what HoloEngine can safely say to enterprise buyers at the current draft-trust stage.

This is not a SOC 2 report, SOC 2 readiness claim, SOC 2 certification claim, HIPAA readiness claim, DPA/BAA coverage claim, provider zero-retention claim, data residency guarantee, or proof of production operating effectiveness.

Every claim below is marked as:

- `approved_safe_draft`: safe only when phrased as draft, target, planned, TBD, or verification workstream language.
- `conditional_requires_evidence`: potentially useful later, but blocked until the listed evidence and review gate are complete.
- `blocked_must_not_claim`: do not use in buyer-facing materials at this stage.

## System And Mode Boundary

HoloEngine is the primary system taxonomy for buyer trust claims. HoloGov is included as the governance, selector, and control layer inside HoloEngine. HoloVerify is separate benchmark/evidence mode. HoloChat and HoloBuild are connected surfaces only where relevant and only if deployed as part of a customer-facing production system.

Production customer mode is distinct from HoloVerify benchmark/evidence mode:

- Production customer mode is the target flow for bounded ALLOW/ESCALATE review. Default audit logging is a metadata-only target unless a customer-enabled evidence-retention mode is configured.
- HoloVerify benchmark/evidence mode may preserve frozen prompts, raw outputs, scoring maps, trace files, runtime manifests, failure autopsies, provenance audits, and operational notes for benchmark integrity.
- Benchmark/evidence retention must not be used as production privacy, retention, or customer-data-handling proof.

## Approved-Safe Draft Claims

These claims are safe for design-partner and buyer-review conversations only if the caveats remain visible.

| ID | Claim Text | Status | Evidence Source | Missing Evidence | Claim Risk | Owner | Review Gate | Buyer-Facing Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| BCR-SAFE-001 | HoloEngine has draft trust architecture artifacts for enterprise trust review, including data-flow architecture, a SOC 2 readiness/gap assessment, a provider data-handling matrix, and an evidence binder index. | `approved_safe_draft` | All four source artifacts. | Formal legal/security approval for external package. | Low if described as draft artifacts; high if framed as certification or completed readiness. | Trust Lead | Trust/Legal review before external sharing. | Opening response to buyer security diligence. |
| BCR-SAFE-002 | HoloEngine is the primary trust system taxonomy; HoloGov is part of HoloEngine, while HoloChat and HoloBuild are connected surfaces only where they are deployed in a customer-facing production system. | `approved_safe_draft` | Data-flow architecture; SOC 2 gap assessment; binder index. | Deployment-specific scope confirmation. | Medium if connected surfaces are implied to be automatically covered. | Trust Lead / Product Lead | Scope review for each buyer deployment. | Scope clarification during procurement. |
| BCR-SAFE-003 | HoloEngine separates target production customer mode from HoloVerify benchmark/evidence mode in its trust architecture and claim language. | `approved_safe_draft` | All four source artifacts. | Storage, access-control, retention, and environment-separation evidence. | Medium: safe as an architecture boundary, not as implementation proof. | Trust Lead / HoloVerify Owner | Trust review plus evidence binder update. | Explaining benchmark artifacts without creating production privacy claims. |
| BCR-SAFE-004 | In target production customer mode, HoloEngine is designed to process bounded ALLOW/ESCALATE review requests rather than execute downstream customer business actions by default. | `approved_safe_draft` | Data-flow architecture; SOC 2 gap assessment. | Deployment-specific execution-boundary evidence and UI/API wording review. | Medium if shortened into a stronger operational guarantee. | Product Lead / Engineering Lead | Product/legal wording review. | Clarifying action-boundary and customer-responsibility model. |
| BCR-SAFE-005 | HoloEngine's target production audit-log design is metadata-only by default and excludes customer payload text, full prompt text, raw provider output text, private source documents, and unredacted conversations by default. | `approved_safe_draft` | Data-flow architecture; SOC 2 gap assessment; provider matrix. | Runtime log samples, redaction tests, log storage/access evidence, retention settings. | High if described as implemented production behavior. | Engineering Lead / SRE | Security evidence review before claiming implementation. | Buyer discussion of intended audit logging. |
| BCR-SAFE-006 | Customer-enabled evidence-retention mode is treated as a separate target mode requiring explicit configuration, retention settings, access controls, and deletion procedures. | `approved_safe_draft` | Data-flow architecture; SOC 2 gap assessment; provider matrix; binder index. | Product configuration, deletion/export tests, support-access boundaries, customer documentation. | High if implied to exist in production now. | Product Lead / Privacy Lead | Product, Privacy, and Legal review. | Regulated audit and dispute-review discussions. |
| BCR-SAFE-007 | Provider/vendor handling is a verification workstream covering provider terms, DPAs, subprocessors, retention settings, zero-retention eligibility, regional handling, and healthcare eligibility if healthcare customers are pursued. | `approved_safe_draft` | Data-flow architecture; SOC 2 gap assessment; provider matrix; binder index. | Provider-specific contract review and legal signoff. | Low if kept as a workstream; high if treated as verified coverage. | Legal / Trust Lead | Legal review after provider evidence is collected. | Buyer questions about OpenAI, xAI, and MiniMax handling. |
| BCR-SAFE-008 | OpenAI, xAI, and MiniMax are listed as current benchmark/provider route vendors in the draft provider data-handling matrix, with retention, DPA, BAA/HIPAA, subprocessor, and data-residency posture marked TBD or VERIFY/TBD. | `approved_safe_draft` | Provider data-handling matrix; binder index. | Provider account/configuration mapping and contract evidence. | Medium: safe if TBD status remains explicit. | Legal / Trust Lead | Provider review gate. | Vendor disclosure during early diligence. |
| BCR-SAFE-009 | HoloVerify benchmark/evidence mode may preserve frozen prompts, raw outputs, scoring maps, traces, runtime manifests, failure autopsies, provenance audits, and operational notes for benchmark integrity. | `approved_safe_draft` | Data-flow architecture; provider matrix; binder index. | Benchmark storage/access/retention proof and separation evidence. | Medium: must not be presented as production customer data handling. | HoloVerify Owner / Trust Lead | Trust review for any external benchmark explanation. | Explaining evaluation reproducibility. |
| BCR-SAFE-010 | HoloEngine has identified SOC 2 Trust Services Criteria areas and gaps across Security, Availability where applicable, Confidentiality, Privacy where applicable, and Processing Integrity where applicable. | `approved_safe_draft` | SOC 2 gap assessment; binder index. | Auditor-scoped control matrix, implementation evidence, operating evidence. | High if framed as SOC 2 readiness or compliance. | Trust Lead / Security Lead | Legal/security review before buyer sharing. | Showing structured readiness planning without claiming readiness. |
| BCR-SAFE-011 | HoloEngine has identified AI governance evidence workstreams for provider routing logs, selector version/hash logging, no scoring-map leakage, trace integrity, failure autopsy, model change control, and customer evidence-retention mode. | `approved_safe_draft` | SOC 2 gap assessment; binder index. | Runtime samples, leakage tests, release/change records, trace integrity proof. | Medium: safe as a workstream; high as operating proof. | AI Governance Lead / HoloGov Owner | Evidence binder review. | AI assurance discussion with technical buyers. |
| BCR-SAFE-012 | The current trust package is intended for design-partner diligence and gap closure planning, not for claims of certification, compliance, audit completion, or production operating effectiveness. | `approved_safe_draft` | All four source artifacts. | External-use approval and final buyer FAQ. | Low if included prominently. | Trust Lead / Legal | Legal review before external use. | Opening disclaimer in design-partner conversations. |

## Conditional Claims Requiring More Evidence

These claims may become useful later, but must remain blocked until evidence and review gates are complete.

| ID | Claim Text | Status | Evidence Source | Missing Evidence | Claim Risk | Owner | Review Gate | Buyer-Facing Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| BCR-COND-001 | HoloEngine production audit logs are metadata-only by default. | `conditional_requires_evidence` | Data-flow architecture; SOC 2 gap assessment; provider matrix. | Runtime log samples, schema validation, redaction tests, log access controls, retention settings. | High | Engineering Lead / SRE | Security evidence review and Trust approval. | Security questionnaire response. |
| BCR-COND-002 | HoloEngine production payloads are minimized before provider routing. | `conditional_requires_evidence` | Data-flow architecture; provider matrix; SOC 2 gap assessment. | Prompt builder evidence, request schemas, minimization tests, redaction tests, route logs. | High | Engineering Lead / HoloGov Owner | Engineering and Security review. | Data handling and AI governance diligence. |
| BCR-COND-003 | HoloEngine enforces authentication, authorization, and tenant binding in production. | `conditional_requires_evidence` | Data-flow architecture; SOC 2 gap assessment; binder index. | Auth design, MFA/service auth, RBAC matrix, tenant model, cross-tenant negative tests. | High | Engineering Lead / Security Lead | Security architecture review. | Enterprise access-control review. |
| BCR-COND-004 | HoloEngine enforces tenant isolation across runtime, storage, logs, traces, evidence stores, queues, and provider routing. | `conditional_requires_evidence` | SOC 2 gap assessment; binder index. | Tenant isolation tests, storage/log partitioning proof, provider route isolation evidence. | High | Engineering Lead | Security test review. | Enterprise security diligence. |
| BCR-COND-005 | HoloEngine encrypts data in transit and at rest in the deployed environment. | `conditional_requires_evidence` | Data-flow architecture; SOC 2 gap assessment; binder index. | TLS configuration, provider API transport verification, storage encryption proof, key-management evidence. | High | SRE / Security Lead | Deployment security review. | Security questionnaire and architecture review. |
| BCR-COND-006 | HoloEngine has provider DPA coverage for OpenAI, xAI, or MiniMax. | `conditional_requires_evidence` | Provider matrix; binder index. | Signed/accepted DPAs, contract exhibits, account mapping, legal signoff. | High | Legal / Trust Lead | Legal contract review. | Vendor risk questionnaire. |
| BCR-COND-007 | HoloEngine has BAA coverage or HIPAA-eligible provider handling for a healthcare deployment. | `conditional_requires_evidence` | Provider matrix; binder index. | BAA availability, healthcare scope, HIPAA legal analysis, deployment controls, audit controls. | High | Legal / Privacy Lead | Healthcare legal/security review. | Healthcare buyer qualification. |
| BCR-COND-008 | A provider route offers zero-retention handling for HoloEngine data. | `conditional_requires_evidence` | Provider matrix; binder index. | Provider-specific contract proof, account/config mapping, route evidence, legal signoff. | High | Legal / Security Lead | Provider retention review. | Sensitive data-handling negotiation. |
| BCR-COND-009 | HoloEngine can meet a customer data-residency or regional-processing requirement. | `conditional_requires_evidence` | Provider matrix; binder index. | Regional provider terms, infrastructure region mapping, route restrictions, legal review. | High | Legal / SRE | Data-residency review. | Enterprise regional procurement. |
| BCR-COND-010 | HoloEngine supports customer data deletion requests in production. | `conditional_requires_evidence` | Data-flow architecture; SOC 2 gap assessment; binder index. | Deletion SOP, request workflow, identity verification, backup handling, evidence-retention exceptions, test evidence. | High | Privacy Lead | Privacy/legal review. | Privacy review and DPA negotiation. |
| BCR-COND-011 | HoloEngine has production incident response procedures. | `conditional_requires_evidence` | SOC 2 gap assessment; binder index. | IR policy, severity matrix, notification templates, escalation/on-call, tabletop records. | High | Security Lead | IR tabletop and legal review. | Security questionnaire response. |
| BCR-COND-012 | HoloEngine has controlled model/provider route change management. | `conditional_requires_evidence` | SOC 2 gap assessment; provider matrix; binder index. | Model route inventory, approval workflow, eval gates, rollback plan, customer notice criteria. | High | AI Governance Lead / Engineering Lead | AI governance change review. | AI governance diligence. |
| BCR-COND-013 | HoloEngine records selector version/hash and provider/model route metadata for production decisions. | `conditional_requires_evidence` | Data-flow architecture; SOC 2 gap assessment; binder index. | Runtime audit samples, selector release records, provider/model route logs, retention/access evidence. | High | HoloGov Owner / Engineering Lead | Runtime evidence review. | Technical auditability discussion. |
| BCR-COND-014 | HoloEngine prevents scoring-map leakage into production or provider prompts. | `conditional_requires_evidence` | SOC 2 gap assessment; provider matrix; binder index. | Access controls, prompt-leakage tests, production runtime separation proof, negative tests. | High | HoloVerify Owner / Security Lead | Security test review. | AI benchmark integrity discussion. |
| BCR-COND-015 | HoloEngine maintains tamper-evident production trace integrity. | `conditional_requires_evidence` | SOC 2 gap assessment; binder index. | Hash manifests, immutable storage configuration, access logs, chain-of-custody procedure. | Medium | HoloVerify Owner / Security Lead | Evidence-retention control review. | Dispute review and regulated audit discussions. |
| BCR-COND-016 | HoloChat or HoloBuild is included in a buyer's HoloEngine trust scope. | `conditional_requires_evidence` | Data-flow architecture; SOC 2 gap assessment; binder index. | Deployment-specific architecture, data inventory, retention/deletion model, access controls, scope approval. | High | Product Lead / Trust Lead | Deployment scope review. | Buyer-specific implementation scoping. |

## Blocked / Must-Not-Claim Statements

These statements must not be used in buyer-facing materials at this stage.

| ID | Claim Text | Status | Evidence Source | Missing Evidence | Claim Risk | Owner | Review Gate | Buyer-Facing Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| BCR-BLOCK-001 | HoloEngine is SOC 2 ready. | `blocked_must_not_claim` | SOC 2 gap assessment; binder index. | Auditor-scoped readiness work, implementation evidence, operating evidence, legal review. | Critical | Trust Lead / Legal | Block until formal readiness decision by counsel/auditor. | Not approved. |
| BCR-BLOCK-002 | HoloEngine is SOC 2 certified, SOC 2 compliant, SOC 2 Type I complete, or SOC 2 Type II complete. | `blocked_must_not_claim` | All four source artifacts. | Independent auditor report and approved scope language. | Critical | Trust Lead / Legal | Block until actual report exists and wording is approved. | Not approved. |
| BCR-BLOCK-003 | HoloEngine is HIPAA ready or HIPAA compliant. | `blocked_must_not_claim` | SOC 2 gap assessment; provider matrix; binder index. | HIPAA legal analysis, BAA coverage, healthcare deployment controls, audit controls. | Critical | Legal / Privacy Lead | Block until healthcare scope is formally approved. | Not approved. |
| BCR-BLOCK-004 | HoloEngine has DPA coverage with OpenAI, xAI, MiniMax, or all providers. | `blocked_must_not_claim` | Provider matrix; binder index. | Signed/accepted provider DPAs, account mapping, legal signoff. | Critical | Legal / Trust Lead | Block until contract evidence is collected. | Not approved. |
| BCR-BLOCK-005 | HoloEngine has BAA coverage with OpenAI, xAI, MiniMax, or all providers. | `blocked_must_not_claim` | Provider matrix; binder index. | BAA contracts, healthcare scope, legal review. | Critical | Legal / Privacy Lead | Block until BAA evidence exists. | Not approved. |
| BCR-BLOCK-006 | OpenAI, xAI, or MiniMax provide zero retention for HoloEngine data. | `blocked_must_not_claim` | Provider matrix; binder index. | Provider-specific contract proof, account/config mapping, route evidence. | Critical | Legal / Security Lead | Block until provider-specific retention evidence exists. | Not approved. |
| BCR-BLOCK-007 | HoloEngine guarantees customer regional processing or data residency. | `blocked_must_not_claim` | Provider matrix; binder index. | Regional-processing proof, infrastructure mapping, route restrictions, legal approval. | Critical | Legal / SRE | Block until residency evidence exists for the deployment. | Not approved. |
| BCR-BLOCK-008 | Customer payloads are never sent to providers. | `blocked_must_not_claim` | Provider matrix; data-flow architecture. | Deployment evidence proving route behavior for every production path, provider terms, tests. | Critical | Engineering Lead / Legal | Block; current target design allows minimum necessary provider-bound content where needed. | Not approved. |
| BCR-BLOCK-009 | Customer payloads are never stored by HoloEngine. | `blocked_must_not_claim` | Data-flow architecture; SOC 2 gap assessment; provider matrix. | End-to-end deployment evidence covering logs, evidence-retention mode, backups, support workflows, and provider flows. | Critical | Engineering Lead / Privacy Lead | Block until full storage/retention proof exists. | Not approved. |
| BCR-BLOCK-010 | HoloEngine production controls are implemented and operating effectively. | `blocked_must_not_claim` | SOC 2 gap assessment; binder index. | Implemented controls, operating evidence, review period evidence, independent validation if claimed. | Critical | Trust Lead / Security Lead | Block until evidence and review period exist. | Not approved. |
| BCR-BLOCK-011 | HoloEngine has verified TLS 1.3, encryption coverage, or key-management specifics in production. | `blocked_must_not_claim` | Data-flow architecture; SOC 2 gap assessment; binder index. | Deployment TLS evidence, encryption at rest proof, key-management evidence. | High | SRE / Security Lead | Block until deployment security verification. | Not approved. |
| BCR-BLOCK-012 | HoloEngine uses RAM-only processing, 0 ms retention, or memory zeroing. | `blocked_must_not_claim` | Data-flow architecture; SOC 2 gap assessment. | Implementation proof, runtime tests, legal/security review. | Critical | Engineering Lead / Legal | Block until implemented and verified. | Not approved. |
| BCR-BLOCK-013 | HoloVerify benchmark/evidence retention is equivalent to production customer data handling. | `blocked_must_not_claim` | Data-flow architecture; provider matrix; binder index. | Not applicable; source artifacts require separation. | Critical | Trust Lead / HoloVerify Owner | Permanently block unless architecture changes and legal/security approve. | Not approved. |
| BCR-BLOCK-014 | HoloChat and HoloBuild are automatically covered by HoloEngine trust scope. | `blocked_must_not_claim` | Data-flow architecture; SOC 2 gap assessment; binder index. | Deployment-specific scope and evidence. | High | Product Lead / Trust Lead | Block until deployment scope is approved. | Not approved. |
| BCR-BLOCK-015 | HoloEngine executes downstream customer business actions. | `blocked_must_not_claim` | Data-flow architecture; SOC 2 gap assessment. | Separate customer deployment with controlled execution layer and approved claim language. | High | Product Lead / Legal | Block by default. | Not approved. |

## Safe Design-Partner Wording

Use this wording for design-partner conversations when a concise answer is needed:

> HoloEngine is in a trust-readiness buildout stage. We have draft repo-backed trust artifacts covering data flow, SOC 2 gap assessment, provider data handling, and an evidence binder index. These documents separate target production customer mode from HoloVerify benchmark/evidence mode and identify the evidence we still need before making stronger enterprise claims. We are not claiming SOC 2 readiness, SOC 2 certification, HIPAA readiness, DPA/BAA coverage, provider zero retention, data residency guarantees, or production operating effectiveness.

Short version:

> We can share our current trust architecture and gap register. It is useful for diligence and design-partner planning, but it is not a compliance or certification claim.

Provider-specific version:

> OpenAI, xAI, and MiniMax are listed as current benchmark/provider route vendors in our draft provider matrix. Provider retention, DPA, BAA/HIPAA, subprocessor, zero-retention, and data-residency posture are still verification workstreams and should be treated as TBD until contract and deployment evidence are reviewed.

Production versus benchmark version:

> HoloEngine production customer mode and HoloVerify benchmark/evidence mode are intentionally separated in our trust architecture. Benchmark evidence may preserve artifacts for reproducibility; that should not be read as production customer-data retention behavior.

## Review Gates

1. Trust Lead review for any externally shared trust artifact.
2. Legal review for SOC 2, HIPAA, DPA, BAA, provider, retention, residency, and customer-data claims.
3. Security review for authentication, RBAC, tenant isolation, encryption, logging, monitoring, incident response, and vulnerability claims.
4. Privacy review for retention, deletion, support access, privacy notice, and evidence-retention claims.
5. Engineering/HoloGov review for model/provider routing logs, selector version/hash logging, trace integrity, no scoring-map leakage, model change control, and production evidence claims.
