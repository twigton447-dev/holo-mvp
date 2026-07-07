# HoloEngine Data Flow Architecture v0.1

Program: HoloEngine Trust & Assurance Program

Status: Target/control architecture draft

Date: 2026-07-07

## Purpose

This document is a foundation draft for enterprise trust review, SOC 2 readiness, ISO 27001 readiness, AI governance readiness, and buyer security review for HoloEngine.

This is not a certification claim. It is not a statement that every control described here is already implemented, tested, or contractually verified. It is a target/control architecture draft that separates intended production customer handling from benchmark and evidence-retention workflows.

## Product Taxonomy

| Name | Meaning | Trust Scope Notes |
| :--- | :--- | :--- |
| HoloEngine | Core runtime trust layer and primary assurance scope. | Primary target for SOC 2 and ISO 27001 readiness. |
| HoloChat | User-facing conversational/workspace interface that may send requests into HoloEngine. | In scope only when deployed as part of a customer-facing production system. |
| HoloBuild | Workflow, agent, or build layer that may prepare or propose actions for HoloEngine review. | In scope only when deployed as part of a customer-facing production system. |
| HoloVerify | Benchmark and evaluation system for HoloEngine. | Separate from production customer payload handling. |
| HoloGov | Governance, selector, and control layer inside HoloEngine. | In scope as part of HoloEngine runtime assurance. |
| HoloBrain | Optional memory/evidence substrate if actually part of a deployment. | Out of scope unless enabled in the customer deployment architecture. |

## Production Customer-Mode Data Flow

This section describes the target production customer-mode flow. It should be read as a control design until each control is implemented, verified, and mapped to deployment evidence.

1. Enterprise source system sends an operational request, evidence packet, workflow event, or decision-review payload to HoloEngine.
2. The request crosses an identity/auth boundary. The target control is to authenticate the caller, identify the tenant, validate authorization, and bind the request to a tenant/request ID.
3. HoloEngine performs request validation. The target control is to reject malformed requests, missing required fields, unsupported action types, or requests that fail tenant routing rules.
4. HoloEngine creates a bounded runtime payload. The target control is to use only the data needed for the review, avoid unnecessary raw transcript accumulation, and separate customer payload text from metadata used for audit.
5. HoloEngine routes the bounded payload through model/provider routing. The target control is to route only the minimum required prompt content to selected model providers under approved provider/vendor terms.
6. HoloGov evaluates worker artifacts and deterministic gates. The target control is to combine local deterministic checks, governance state, selector rules, model outputs, and source-boundary validation before producing a final decision.
7. HoloEngine returns an `ALLOW` or `ESCALATE` response. The target control is that HoloEngine advises or gates the decision review. HoloEngine should not be described as executing downstream business actions unless a separate customer deployment explicitly implements and controls that execution.
8. HoloEngine writes a metadata-only audit log by default. The target control is to log decision metadata without customer payload text unless a customer-enabled evidence-retention mode is explicitly configured.
9. Retention and disposal controls apply. The target control is to define retention periods, deletion procedures, access controls, and customer deletion workflows before production use.

### Production Data Flow Table

| Stage | Data Entering | Target Processing | Data Leaving | Primary Control Goal |
| :--- | :--- | :--- | :--- | :--- |
| Enterprise source system | Customer request, operational facts, evidence references, source fields | Customer system prepares request | Request to HoloEngine | Keep request scoped to the decision being reviewed. |
| Identity/auth boundary | Request, tenant identity, caller identity | Authentication, tenant binding, authorization check | Accepted or rejected request | Prevent unauthorized access and cross-tenant mixing. |
| Request validation | Accepted request | Schema validation, required field checks, action-boundary checks | Bounded runtime payload or rejection | Reject malformed or unsupported requests early. |
| Payload processing lifecycle | Bounded runtime payload | Normalize, route, evaluate, select, return decision | ALLOW/ESCALATE plus metadata | Keep payload handling bounded and auditable. |
| Model/provider routing | Prompt content needed for review | Provider/model call under approved configuration | Model artifacts | Minimize provider exposure and track provider/model version. |
| HoloGov governance/selector | Model artifacts, local gate output, deterministic ledger | Selector and governance control | Final governed artifact | Prevent weak final artifacts from overriding source-grounded blockers or verified support. |
| HoloEngine response | Final governed artifact | Response shaping | `ALLOW` or `ESCALATE` decision response | Return a clear decision without claiming downstream execution. |
| Metadata audit log | Metadata only by default | Log timestamp, IDs, route, versions, verdict, latency, tokens | Audit record | Preserve reviewability without retaining payload text by default. |
| Retention/disposal | Audit metadata and configured evidence artifacts | Retain, delete, or dispose by policy | Deleted or retained records | Make retention explicit and customer-governed. |

## Connected Product Surfaces

HoloEngine is the primary assurance scope. Connected product surfaces may feed HoloEngine or use HoloEngine output, but they should have separate data boundaries and deployment-scoped control decisions.

### HoloChat

HoloChat is a user-facing conversational/workspace interface. In a production deployment, HoloChat may send user requests, conversation-derived tasks, document references, or workspace context into HoloEngine for review.

Target boundary:

- HoloChat should not be treated as automatically in scope for HoloEngine SOC 2 or ISO 27001 readiness unless it is part of the production customer deployment.
- HoloChat payload text should not be retained by HoloEngine by default unless a customer-enabled evidence-retention mode is configured.
- If HoloChat stores conversation history, that storage requires its own retention, deletion, access-control, and privacy review.

### HoloBuild

HoloBuild is a workflow, agent, or build layer that may prepare proposed actions for HoloEngine review.

Target boundary:

- HoloBuild may submit proposed actions, source packets, workflow artifacts, or operational decisions to HoloEngine.
- HoloEngine should review and return `ALLOW` or `ESCALATE`.
- HoloEngine should not be described as executing the action unless the deployment includes a separately controlled execution layer.
- HoloBuild is in scope for enterprise trust review only when it is part of the customer-facing production system.

### HoloVerify

HoloVerify is a benchmark and evaluation system for HoloEngine.

Target boundary:

- HoloVerify is not production customer payload handling.
- HoloVerify may intentionally preserve frozen prompts, raw outputs, scoring maps, traces, and failure autopsies for benchmark integrity.
- HoloVerify evidence must remain separate from production customer data handling.
- HoloVerify evidence should not be mixed into production audit logs or customer payload retention claims.

### HoloGov

HoloGov is the governance, selector, and control layer inside HoloEngine.

Target boundary:

- HoloGov is in scope as part of HoloEngine runtime assurance.
- HoloGov should record selector version/hash, route, deterministic gate status, and final verdict metadata.
- HoloGov should not rely on customer payload text retention by default to be auditable.

### HoloBrain

HoloBrain is an optional memory/evidence substrate only if actually part of deployment.

Target boundary:

- HoloBrain should be out of scope unless enabled.
- If enabled, HoloBrain requires a separate data inventory, retention model, deletion process, access-control design, and customer opt-in/opt-out model.

## In-Scope And Out-of-Scope Readiness

| Surface | Default Readiness Scope | Notes |
| :--- | :--- | :--- |
| HoloEngine | In scope for target SOC 2 and ISO 27001 readiness. | Core runtime trust layer. |
| HoloGov | In scope as part of HoloEngine. | Governance and selector controls. |
| HoloChat | Conditional. | In scope only if deployed for production customers. |
| HoloBuild | Conditional. | In scope only if deployed for production customers. |
| HoloVerify | Separate benchmark/evidence scope. | Not production customer handling. |
| HoloBrain | Conditional. | In scope only if enabled in deployment. |

## Benchmark And Evidence Mode

Benchmark/evidence mode is separate from production customer-mode handling.

In benchmark/evidence mode, HoloVerify may intentionally preserve:

- frozen prompts
- raw provider outputs
- trace files
- scoring maps
- runtime manifests
- failure autopsies
- provenance audits
- operational notes for invalid or blocked runs

This preservation exists for benchmark integrity, reproducibility, and failure analysis. It is not the same as production customer payload handling.

Production customer-mode should default to metadata-only audit logging unless the customer explicitly enables evidence retention. Benchmark evidence should remain separated by storage location, access control, retention policy, and claim language.

## Do-Not-Overclaim Rules

The following statements must not be made unless implemented, verified, and supported by evidence or contract:

- Do not claim RAM-only processing unless implemented and verified.
- Do not claim 0 ms retention.
- Do not claim memory zeroing.
- Do not claim TLS 1.3 unless verified in the deployed environment.
- Do not claim provider zero retention unless contractually verified per provider.
- Do not claim HoloEngine executes downstream business actions.
- Do not claim SOC 2 certification.
- Do not claim ISO 27001 certification.
- Do not claim ISO 42001 certification.
- Do not claim HIPAA compliance.
- Do not claim HITRUST certification.

Acceptable language at this stage:

- Target control
- Readiness workstream
- Draft architecture
- To be verified
- To be contractually confirmed
- Customer-enabled evidence-retention mode
- Metadata-only audit logging by default

## Provider And Vendor Risk Placeholders

Provider and vendor posture must be verified before buyer-facing commitments.

| Provider | Data Handling Status | DPA Status | Retention Setting Support | Enterprise Zero-Retention Eligibility | BAA/HIPAA Eligibility If Healthcare Customers Are Pursued |
| :--- | :--- | :--- | :--- | :--- | :--- |
| OpenAI | VERIFY | TBD | TBD | TBD | TBD |
| xAI | VERIFY | TBD | TBD | TBD | TBD |
| MiniMax | VERIFY | TBD | TBD | TBD | TBD |

Required next evidence:

- provider terms review
- DPA review
- subprocessor review
- data retention configuration review
- customer-region and data-residency review if required
- healthcare eligibility review if healthcare customers are pursued

## Audit Log Design

Production audit logs should be metadata-only by default.

Default metadata fields:

- timestamp
- tenant ID
- request ID
- route
- model/provider versions
- selector version/hash
- worker contract version/hash if applicable
- verdict
- latency
- token counts
- error status
- retry status
- evidence-retention mode flag

Default excluded fields:

- customer payload text
- full prompt text
- raw provider output text
- private source documents
- unredacted user conversation text

Exception mode:

A customer-enabled evidence-retention mode may store additional artifacts for regulated audit or dispute review. That mode should require explicit customer configuration, retention settings, access controls, and deletion procedures. It must not be confused with the default metadata-only audit log.

## Trust Controls Mapping

This mapping is preliminary. It is intended to guide readiness work and evidence collection.

| Framework | Draft Control Area | HoloEngine Target Control |
| :--- | :--- | :--- |
| SOC 2 Security | Access control | Authenticate callers, bind tenant/request IDs, enforce RBAC where applicable. |
| SOC 2 Security | Change management | Version selector logic, worker contracts, runtime manifests, and release changes. |
| SOC 2 Security | Monitoring | Log metadata for route, provider, selector version/hash, verdict, latency, errors, and token counts. |
| SOC 2 Security | Incident response | Define security incident process, escalation, evidence capture, customer notification, and remediation tracking. |
| SOC 2 Confidentiality | Data minimization | Send only bounded prompt content needed for review. |
| SOC 2 Confidentiality | Retention | Default metadata-only logs; customer-enabled evidence retention by explicit configuration. |
| SOC 2 Confidentiality | Vendor management | Verify provider data handling, DPAs, retention options, and subprocessors. |
| SOC 2 Privacy if applicable | Notice and purpose | Define customer-facing data handling terms and evidence-retention choices. |
| SOC 2 Privacy if applicable | Deletion | Define customer data deletion request process. |
| ISO 27001 ISMS | Asset inventory | Inventory HoloEngine components, providers, logs, secrets, datasets, and evidence stores. |
| ISO 27001 ISMS | Risk assessment | Maintain risk register for provider routing, prompt exposure, logging, retention, tenant isolation, and model governance. |
| ISO 27001 ISMS | Supplier relationships | Maintain provider/subprocessor list and vendor risk review. |
| ISO 27001 ISMS | Secure development | Dependency scanning, code review, release controls, and secrets management. |
| ISO 27001 ISMS | Cryptography | Verify encryption at rest and in transit in deployed architecture. |
| ISO 42001 / AI governance placeholder | AI system inventory | Inventory model routes, selector versions, worker contracts, evaluation lanes, and known limitations. |
| ISO 42001 / AI governance placeholder | Risk management | Track false allow, false escalate, no-select, parse failure, and provider failure classes. |
| ISO 42001 / AI governance placeholder | Human oversight | Define escalation handling and customer review responsibilities. |
| NIST AI RMF placeholder | Govern | Define roles, policies, risk ownership, and evaluation boundaries. |
| NIST AI RMF placeholder | Map | Map use cases, data flows, users, harms, and deployment context. |
| NIST AI RMF placeholder | Measure | Measure model/provider behavior, HoloGov selector behavior, and deterministic gate behavior. |
| NIST AI RMF placeholder | Manage | Track mitigations, incidents, residual risk, and release gates. |

## Open Questions And Gaps

The following items must be answered before mature enterprise trust review:

- authentication implementation
- tenant isolation
- encryption at rest
- encryption in transit
- TLS version verification
- logging storage
- log access controls
- retention and deletion policy
- vendor DPAs
- subprocessor list
- audit evidence retention mode
- customer-controlled evidence mode
- incident response
- access control and RBAC
- secrets management
- dependency and security scanning
- backup and disaster recovery
- customer data deletion request process
- provider zero-retention eligibility
- healthcare BAA/HIPAA eligibility if healthcare customers are pursued
- HoloChat conversation retention if HoloChat is deployed
- HoloBuild artifact retention if HoloBuild is deployed
- HoloBrain memory/evidence retention if HoloBrain is enabled

## Buyer-Facing Trust Outputs To Build Next

Priority trust outputs:

1. HoloEngine data-flow diagram
2. Security FAQ
3. Privacy/data-handling FAQ
4. Vendor/subprocessor list
5. Model-provider handling matrix
6. SOC 2 readiness checklist
7. ISO 27001 readiness checklist
8. AI governance controls matrix
9. Design-partner secure pilot package

## Draft Review Notes

This document should be reviewed by security, privacy, legal, engineering, and product before it is used externally. Any buyer-facing version should clearly distinguish implemented controls, planned controls, verified controls, and contract-dependent controls.
