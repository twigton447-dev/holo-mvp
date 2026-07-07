# HoloEngine Provider Data-Handling Matrix v0.1

Program: HoloEngine Trust & Assurance Program

Status: Provider/data-handling matrix draft

Date: 2026-07-07

Source documents:

- `docs/trust/HOLOENGINE_DATA_FLOW_ARCHITECTURE_V0_1.md`
- `docs/trust/HOLOENGINE_SOC2_READINESS_GAP_ASSESSMENT_V0_1.md`

## Purpose And Claim Boundary

This matrix documents current HoloEngine benchmark/provider route vendors and the data-handling questions that must be answered before buyer-facing commitments are made.

This is not a provider contract review. It is not a DPA, BAA, HIPAA, SOC 2, zero-retention, subprocessor, or data-residency claim. Production customer-mode handling remains a target/control design until implementation and deployment evidence are verified.

Acceptable stage language:

- provider/data-handling matrix draft
- target control
- verification workstream
- to be verified
- TBD
- contract-dependent
- customer-enabled evidence-retention mode
- benchmark/evidence mode

Do not use this artifact to claim:

- provider zero retention
- DPA coverage
- BAA coverage
- HIPAA compliance or HIPAA readiness
- SOC 2 compliance, certification, audit readiness, or operating effectiveness
- production data-handling behavior that has not been verified in the deployed environment
- data residency or regional processing guarantees

## Scope

Primary scope: HoloEngine Trust & Assurance Program.

Included vendors:

- OpenAI
- xAI
- MiniMax

These vendors are included as current benchmark/provider route vendors. The source architecture already identifies provider/vendor handling as a verification workstream covering provider terms, DPAs, subprocessors, retention settings, zero-retention eligibility, regional handling, and healthcare eligibility if healthcare customers are pursued.

## Status Terms

| Term | Meaning |
| :--- | :--- |
| `VERIFY/TBD` | Evidence or contractual confirmation may exist or may be available from the provider, but it has not been verified for HoloEngine buyer claims in this artifact. |
| `TBD` | No sufficient HoloEngine-specific evidence has been captured in this artifact. Treat as unknown until reviewed by Trust, Legal, Security, and Engineering. |
| `Target` | Intended control design, not a verified operating control. |
| `Benchmark/evidence mode` | HoloVerify or related benchmark work where frozen prompts, raw outputs, traces, manifests, scoring maps, and failure notes may be preserved for reproducibility. This is separate from production customer payload handling. |
| `Production customer mode` | Target HoloEngine production flow for bounded ALLOW/ESCALATE review requests. Default target audit logging is metadata-only unless a customer-enabled evidence-retention mode is configured. |

## Production Versus Benchmark/Evidence Boundary

| Mode | Provider-Bound Data | Retention And Evidence Treatment | Claim Boundary |
| :--- | :--- | :--- | :--- |
| Production customer mode | Target design may send minimum necessary bounded prompt content to selected providers under approved configuration. This may include customer request text, operational facts, source/evidence snippets, and role/system instructions if needed for review. | Default target audit log is metadata-only and excludes customer payload text, full prompt text, raw provider output text, private source documents, and unredacted conversation text. Customer-enabled evidence-retention mode requires explicit configuration, access controls, retention settings, and deletion procedures. | Do not claim implemented production handling, zero retention, or no customer payload exposure until deployment evidence and provider terms are verified. |
| Benchmark/evidence mode | May send frozen benchmark prompts, benchmark packets, synthetic or prepared evaluation facts, route/role instructions, and model-review prompts to benchmark/provider routes. | May intentionally preserve frozen prompts, raw provider outputs, trace files, scoring maps, runtime manifests, failure autopsies, provenance audits, and operational notes for benchmark integrity. | Do not describe benchmark evidence retention as production customer payload handling. Do not mix benchmark evidence claims into production privacy or retention claims. |

## Provider Matrix

| Provider | Current Route Role | Data Sent In Production Customer Mode | Customer Payload Text Sent? | Data Sent In Benchmark/Evidence Mode |
| :--- | :--- | :--- | :--- | :--- |
| OpenAI | Current benchmark/provider route vendor. May be selected by target HoloEngine provider routing only under approved provider/vendor terms. | `VERIFY/TBD`. Target design may send minimum necessary bounded prompt content needed for ALLOW/ESCALATE review: role/system instructions, customer request or extracted operational facts, source/evidence snippets, action-boundary facts, and route metadata required for the provider call. | `VERIFY/TBD`. If OpenAI is selected for a production provider route, customer payload text or extracted facts may be sent when needed for model review. Default target audit logs exclude payload text, but deployed behavior must be verified. | Frozen benchmark prompts, benchmark packet text, role/route instructions, benchmark evidence facts, raw model outputs, trace metadata, model/provider identifiers, token/latency/error metadata, and failure-analysis artifacts may be used or preserved. Production customer payload text should not be present in benchmark mode. |
| xAI | Current benchmark/provider route vendor. May be selected by target HoloEngine provider routing only under approved provider/vendor terms. | `VERIFY/TBD`. Target design may send minimum necessary bounded prompt content needed for ALLOW/ESCALATE review: role/system instructions, customer request or extracted operational facts, source/evidence snippets, action-boundary facts, and route metadata required for the provider call. | `VERIFY/TBD`. If xAI is selected for a production provider route, customer payload text or extracted facts may be sent when needed for model review. Default target audit logs exclude payload text, but deployed behavior must be verified. | Frozen benchmark prompts, benchmark packet text, role/route instructions, benchmark evidence facts, raw model outputs, trace metadata, model/provider identifiers, token/latency/error metadata, and failure-analysis artifacts may be used or preserved. Production customer payload text should not be present in benchmark mode. |
| MiniMax | Current benchmark/provider route vendor. May be selected by target HoloEngine provider routing only under approved provider/vendor terms. | `VERIFY/TBD`. Target design may send minimum necessary bounded prompt content needed for ALLOW/ESCALATE review: role/system instructions, customer request or extracted operational facts, source/evidence snippets, action-boundary facts, and route metadata required for the provider call. | `VERIFY/TBD`. If MiniMax is selected for a production provider route, customer payload text or extracted facts may be sent when needed for model review. Default target audit logs exclude payload text, but deployed behavior must be verified. | Frozen benchmark prompts, benchmark packet text, role/route instructions, benchmark evidence facts, raw model outputs, trace metadata, model/provider identifiers, token/latency/error metadata, and failure-analysis artifacts may be used or preserved. Production customer payload text should not be present in benchmark mode. |

## Provider Contract And Readiness Status

| Provider | Retention Setting Status | DPA Status | Subprocessor Status | Zero-Retention Eligibility | BAA/HIPAA Eligibility | Regional/Data Residency Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| OpenAI | `VERIFY/TBD` | `TBD` | `TBD` | `VERIFY/TBD` | `TBD` | `TBD` |
| xAI | `VERIFY/TBD` | `TBD` | `TBD` | `VERIFY/TBD` | `TBD` | `TBD` |
| MiniMax | `VERIFY/TBD` | `TBD` | `TBD` | `VERIFY/TBD` | `TBD` | `TBD` |

## Shared Data Classes

### Potentially Provider-Bound In Production Customer Mode

These are target design data classes and must be verified in deployment before buyer claims:

- role/system instructions for the selected HoloEngine route
- bounded customer request text or extracted facts needed for review
- operational facts, evidence references, or source snippets needed for ALLOW/ESCALATE evaluation
- action-boundary facts and governance instructions
- route, provider, model, retry, latency, token, and error metadata
- tenant/request identifiers only where required for routing or audit, and only under approved design

### Excluded From Default Production Audit Logs

The source architecture targets metadata-only audit logging by default. Default excluded fields:

- customer payload text
- full prompt text
- raw provider output text
- private source documents
- unredacted user conversation text

### Potentially Preserved In Benchmark/Evidence Mode

Benchmark/evidence mode may intentionally preserve:

- frozen prompts
- benchmark packet text
- raw provider outputs
- trace files
- scoring maps
- runtime manifests
- model/provider route metadata
- failure autopsies
- provenance audits
- operational notes for invalid or blocked runs

Scoring maps and answer keys must remain benchmark evidence artifacts. They must not be treated as provider prompt content unless a separate, explicit, non-production evaluation design approves that exposure.

## Risks And Mitigations

| Risk | Current Status | Mitigation / Control Workstream |
| :--- | :--- | :--- |
| Provider retention settings are not verified for HoloEngine claims. | `VERIFY/TBD` for all listed providers. | Complete provider-specific retention review, document configuration options, capture contract evidence, and map route behavior to approved settings before buyer commitments. |
| DPA coverage is not confirmed. | `TBD` for all listed providers. | Legal/Trust review of provider terms and DPAs; store signed or accepted DPA evidence in the trust binder. |
| Subprocessor lists are not confirmed. | `TBD` for all listed providers. | Build provider/subprocessor inventory, review provider subprocessor pages or contract exhibits, and create an update cadence. |
| Zero-retention eligibility could be overstated. | `VERIFY/TBD` for all listed providers. | Treat zero retention as unavailable for claims until contractually verified per provider and mapped to the actual HoloEngine route/account/configuration. |
| BAA/HIPAA eligibility could be overstated. | `TBD` for all listed providers. | Do not pursue healthcare claims until BAA availability, HIPAA scope, product handling, access controls, audit controls, and legal review are complete. |
| Regional/data residency requirements may not match provider processing. | `TBD` for all listed providers. | Define customer region requirements, verify provider regional processing/storage options, and add route-level restrictions where required. |
| Production customer payloads could be sent to providers without explicit approval or minimization. | Target control only. | Require provider route approval, data-sharing scope, prompt minimization, redaction tests, and audit metadata showing provider/model/route and evidence-retention mode. |
| Benchmark evidence could be confused with production customer data handling. | Known separation requirement. | Keep HoloVerify evidence in separate storage, access control, retention policy, and claim language. Do not use benchmark retention behavior as production privacy evidence. |
| Raw prompts or raw provider outputs could be over-retained in production. | Target control only. | Default to metadata-only audit logs; require customer-enabled evidence-retention mode for payload artifacts; define retention, deletion, support access, and export controls. |
| Scoring maps or benchmark answer keys could leak into provider prompts. | Partial benchmark discipline. | Access-control scoring maps, exclude scoring maps from provider prompts, and add prompt-leakage tests before production or benchmark expansion. |
| Provider fallback or model-route changes could alter data-sharing scope. | Target control only. | Treat provider/model roster changes as change-managed events requiring approval, data-sharing review, and buyer-impact review if applicable. |

## Buyer-Safe Language

The following language is safe for draft buyer review if it remains paired with the claim boundary:

- HoloEngine has a draft provider/data-handling matrix for enterprise trust review.
- The matrix separates target production customer-mode handling from benchmark/evidence mode.
- In target production mode, HoloEngine is designed to minimize provider-bound content to the prompt content needed for ALLOW/ESCALATE review.
- Default production audit logging is a metadata-only target; customer payload text and raw provider outputs are excluded by default in the target design.
- Customer-enabled evidence retention is a separate mode that requires explicit configuration, retention settings, access controls, and deletion procedures.
- Provider retention settings, DPAs, subprocessors, zero-retention eligibility, BAA/HIPAA eligibility, and regional/data-residency posture are verification workstreams.
- HoloVerify benchmark evidence is separate from production customer payload handling.

## Must-Not-Claim Language

Do not claim any of the following unless supported by current provider-specific contracts, deployment evidence, and legal/security review:

- OpenAI, xAI, or MiniMax provide zero retention for HoloEngine data.
- HoloEngine has DPA coverage with OpenAI, xAI, or MiniMax.
- HoloEngine has BAA coverage with OpenAI, xAI, or MiniMax.
- HoloEngine is HIPAA compliant or HIPAA ready.
- HoloEngine is SOC 2 compliant, SOC 2 certified, SOC 2 ready, or auditor validated.
- HoloEngine production customer payloads are never sent to providers.
- HoloEngine production customer payloads are never stored.
- HoloEngine default audit logs, provider payloads, evidence-retention mode, backups, and support workflows have been verified end to end.
- HoloEngine can guarantee customer regional processing or data residency.
- Benchmark/evidence retention controls are equivalent to production customer data handling.

## Evidence To Collect Next

1. Provider terms review for OpenAI, xAI, and MiniMax.
2. DPA review and evidence capture for each provider.
3. Subprocessor inventory and update cadence for each provider.
4. Provider retention setting review, including route/account/configuration evidence.
5. Zero-retention eligibility review for each provider, if available.
6. BAA/HIPAA eligibility review before any healthcare positioning.
7. Regional/data-residency review for customer deployment scenarios.
8. Production prompt-minimization evidence and redaction tests.
9. Production metadata-only audit-log samples.
10. Customer-enabled evidence-retention configuration, retention, deletion, and support-access controls.
11. Benchmark/evidence storage, access-control, and retention separation proof.
12. Provider/model route change-control procedure.

## Draft Review Notes

This artifact should be reviewed by Trust, Legal, Security, Privacy, Engineering, Product, and HoloGov owners before external use. Any buyer-facing version must preserve the distinction between target controls, verified controls, contract-dependent controls, and TBD items.
