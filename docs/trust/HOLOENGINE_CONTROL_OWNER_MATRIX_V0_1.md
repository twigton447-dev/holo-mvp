# HoloEngine Control Owner Matrix v0.1

Program: HoloEngine Trust & Assurance Program

From: HoloOps SOC / Taylor

To: HoloOps SOC and Taylor

Audience: HoloOps SOC / Taylor and future Trust, Legal, Security, Privacy, Engineering, Product, SRE, HoloGov, and HoloVerify owners

Status: Control owner matrix draft

Date: 2026-07-07

Source artifacts used:

- `docs/trust/HOLOENGINE_TRUST_EVIDENCE_BINDER_INDEX_V0_1.md`
- `docs/trust/HOLOENGINE_BUYER_CLAIM_REGISTER_V0_1.md`
- `docs/trust/HOLOENGINE_SECURITY_QUESTIONNAIRE_STARTER_PACK_V0_1.md`
- `docs/trust/HOLOENGINE_30_60_90_TRUST_SOC_READINESS_ROADMAP_V0_1.md`

## Claim Boundary

This is an internal ownership matrix for trust and SOC readiness work. It is not a SOC 2 report, SOC 2 readiness claim, SOC 2 certification claim, ISO certification claim, HIPAA readiness claim, DPA/BAA coverage claim, provider zero-retention claim, data-residency guarantee, or proof of production operating effectiveness.

Use `target_only`, `missing`, and `tbd` statuses only for unverified workstreams. Keep HoloEngine as the primary taxonomy. Keep HoloVerify benchmark/evidence controls separate from production customer mode controls.

## Status Terms

| Status | Meaning |
| :--- | :--- |
| `target_only` | The control is a target design, draft, or planned workstream. |
| `missing` | The control has not yet been implemented or evidenced in the repo-backed trust artifacts. |
| `tbd` | The control depends on provider, legal, auditor, or deployment confirmation. |

## Dependency Flag

| Flag | Meaning |
| :--- | :--- |
| `internal_only` | The workstream can move forward with internal owner action. |
| `external_dependency` | The workstream needs counsel, a provider, an auditor, or another external assessor/contracting party. |

## 30 Day Workstreams

| Control ID | Control / Workstream | Primary Owner Role | Supporting Owner Roles | Current Status | Target Evidence Artifact | Due Window | Dependency | Buyer Risk Level | Claim Gate Impact | Dependency Flag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| HCM-001 | Trust binder operationalization | Trust Lead | HoloOps SOC / Taylor, Security Lead, Legal | target_only | `docs/trust/HOLOENGINE_TRUST_EVIDENCE_BINDER_V0_2.md` | 30 days | Existing evidence binder index and roadmap | High | Centralizes evidence ownership; does not create a buyer claim by itself. | internal_only |
| HCM-002 | Buyer claim control and response gating | Trust Lead / Legal | Security Lead, Product Lead | target_only | `docs/trust/HOLOENGINE_BUYER_CLAIM_REGISTER_V0_1.md`, `docs/trust/HOLOENGINE_SECURITY_QUESTIONNAIRE_STARTER_PACK_V0_1.md` | 30 days | Current claim register and questionnaire starter pack | Critical | Prevents unsupported wording from escaping into buyer materials. | internal_only |
| HCM-003 | Deployment scope and system boundary | Trust Lead / Product Lead | Engineering Lead, HoloGov Owner | target_only | `docs/trust/HOLOENGINE_DATA_FLOW_ARCHITECTURE_V0_1.md`, `docs/trust/HOLOENGINE_DEPLOYMENT_SCOPE_WORKSHEET_V0_1.md` | 30 days | Current data-flow architecture and roadmap | High | Defines whether HoloChat, HoloBuild, and optional HoloBrain are in scope. | internal_only |
| HCM-004 | Production versus HoloVerify boundary | Trust Lead / HoloVerify Owner | Security Lead, Product Lead | target_only | `docs/trust/HOLOENGINE_DATA_FLOW_ARCHITECTURE_V0_1.md`, `docs/trust/HOLOENGINE_TRUST_EVIDENCE_BINDER_INDEX_V0_1.md` | 30 days | Existing architecture and evidence binder | Critical | Blocks benchmark/evidence artifacts from being reused as production privacy proof. | internal_only |
| HCM-005 | Access control design | Engineering Lead / Security Lead | Product Lead, SRE, Support Lead | target_only | `docs/trust/HOLOENGINE_ACCESS_CONTROL_DESIGN_PACKET_V0_1.md` | 30 days | System boundary and questionnaire controls | High | Unlocks later auth, RBAC, and tenant-isolation claims. | internal_only |
| HCM-006 | Logging design | Engineering Lead / SRE / HoloGov Owner | Security Lead, Trust Lead | target_only | `docs/trust/HOLOENGINE_METADATA_AUDIT_LOG_SCHEMA_V0_1.md` | 30 days | Data-flow architecture and questionnaire pack | High | Unlocks metadata-only logging claims only after samples exist. | internal_only |
| HCM-007 | Provider review prep | Legal / Trust Lead / Security Lead | Engineering Lead, SRE | target_only | `docs/trust/HOLOENGINE_PROVIDER_REVIEW_PACKET_V0_1.md` | 30 days | Provider data-handling matrix | High | Keeps DPA, BAA, retention, zero-retention, and residency claims blocked until evidence exists. | internal_only |
| HCM-008 | Incident response draft | Security Lead / Legal | SRE, HoloGov Owner | missing | `docs/trust/HOLOENGINE_INCIDENT_RESPONSE_PLAN_V0_1.md` | 30 days | SOC 2 gap assessment and roadmap | High | No production incident-response claim until policy and tabletop evidence exist. | internal_only |
| HCM-009 | Secure SDLC baseline | Engineering Lead / Security Lead | Trust Lead | target_only | `docs/trust/HOLOENGINE_SECURE_SDLC_AND_CHANGE_CONTROL_POLICY_V0_1.md` | 30 days | SOC 2 gap assessment and roadmap | High | Blocks secure SDLC and change-control claims until scanning and approvals exist. | internal_only |
| HCM-010 | HoloVerify evidence separation SOP | HoloVerify Owner / Trust Lead | Security Lead, Product Lead | target_only | `docs/trust/HOLOENGINE_HOLOVERIFY_EVIDENCE_SEPARATION_SOP_V0_1.md` | 30 days | Data-flow architecture, provider matrix, and roadmap | High | Keeps benchmark evidence separate from production customer-data claims. | internal_only |

## 60 Day Workstreams

| Control ID | Control / Workstream | Primary Owner Role | Supporting Owner Roles | Current Status | Target Evidence Artifact | Due Window | Dependency | Buyer Risk Level | Claim Gate Impact | Dependency Flag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| HCM-011 | Auth / RBAC / tenant-isolation evidence | Engineering Lead / Security Lead | Trust Lead | missing | `docs/trust/HOLOENGINE_AUTH_RBAC_TENANT_ISOLATION_EVIDENCE_PACK_V0_1.md` | 60 days | Access control design | Critical | Unlocks conditional buyer answers for authentication, authorization, and tenant binding. | internal_only |
| HCM-012 | Encryption verification | SRE / Security Lead | Engineering Lead | tbd | `docs/trust/HOLOENGINE_ENCRYPTION_VERIFICATION_PACKET_V0_1.md` | 60 days | Deployment architecture and environment evidence | High | Keeps encryption-in-transit and encryption-at-rest claims conditional until verified in deployment. | internal_only |
| HCM-013 | Metadata-only log samples and log integrity | Engineering Lead / SRE / HoloGov Owner | Security Lead | missing | `docs/trust/HOLOENGINE_LOG_SAMPLES_AND_INTEGRITY_PACK_V0_1.md` | 60 days | Logging design | High | Unlocks metadata-only log claims and excluded-field assertions only if samples and tests exist. | internal_only |
| HCM-014 | Secrets management | Security Lead | Engineering Lead, SRE | missing | `docs/trust/HOLOENGINE_SECRETS_MANAGEMENT_PACKET_V0_1.md` | 60 days | Secure SDLC baseline | High | Unlocks secrets-handling claims and closes a common SOC 2 gap. | internal_only |
| HCM-015 | Vulnerability management | Security Lead | Engineering Lead, SRE | missing | `docs/trust/HOLOENGINE_VULNERABILITY_MANAGEMENT_PACKET_V0_1.md` | 60 days | Secure SDLC baseline | High | Unlocks vulnerability-program claims only after scans, SLAs, and remediation evidence exist. | internal_only |
| HCM-016 | Retention / deletion / support access / evidence-retention mode | Privacy Lead / Support Lead | Legal, SRE, Product Lead | target_only | `docs/trust/HOLOENGINE_RETENTION_DELETION_AND_SUPPORT_ACCESS_PACKET_V0_1.md` | 60 days | Privacy/legal review and access-control design | Critical | Unblocks deletion, support-access, and customer evidence-retention claims only with tested procedures. | internal_only |
| HCM-017 | Provider contract and configuration evidence | Legal / Trust Lead | Security Lead, SRE | tbd | `docs/trust/HOLOENGINE_PROVIDER_CONTRACT_AND_CONFIGURATION_EVIDENCE_BINDER_V0_1.md` | 60 days | Provider review prep | Critical | Keeps DPA, BAA, zero-retention, and residency claims blocked until contract/config proof exists. | external_dependency |
| HCM-018 | HoloGov route logs, selector hash logging, and model/provider route change control | HoloGov Owner / AI Governance Lead | Engineering Lead, Security Lead, Legal | target_only | `docs/trust/HOLOENGINE_HOLOGOV_ROUTE_LOG_AND_CHANGE_CONTROL_PACKET_V0_1.md` | 60 days | Logging design and provider review prep | High | Unlocks route-log and selector-hash claims and keeps model-change claims conditional. | internal_only |
| HCM-019 | Monitoring and alerting plus backup / DR | SRE / Operations | Security Lead, Engineering Lead | missing | `docs/trust/HOLOENGINE_MONITORING_ALERTING_AND_BACKUP_DR_PACKET_V0_1.md` | 60 days | Logging design and incident-response draft | High | Unblocks availability-related claims only after monitoring and recovery evidence exist. | internal_only |
| HCM-020 | HoloVerify benchmark integrity pack | HoloVerify Owner / Security Lead | Trust Lead, Engineering Lead | target_only | `docs/trust/HOLOENGINE_HOLOVERIFY_BENCHMARK_INTEGRITY_PACK_V0_1.md` | 60 days | HoloVerify evidence separation SOP | High | Keeps benchmark storage, scoring-map leakage, trace integrity, and failure autopsy separate from production claims. | internal_only |

## 90 Day Workstreams

| Control ID | Control / Workstream | Primary Owner Role | Supporting Owner Roles | Current Status | Target Evidence Artifact | Due Window | Dependency | Buyer Risk Level | Claim Gate Impact | Dependency Flag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| HCM-021 | Control readiness review | Trust Lead / Security Lead | Legal, Product Lead, SRE | target_only | `docs/trust/HOLOENGINE_CONTROL_READINESS_REVIEW_MEMO_V0_1.md` | 90 days | 30- and 60-day evidence packs | High | Determines which controls can move from target_only to conditional_tbd. | internal_only |
| HCM-022 | Auditor scoping packet | Trust Lead / Security Lead | Legal, SRE | tbd | `docs/trust/HOLOENGINE_SOC2_AUDITOR_SCOPING_PACKET_V0_1.md` | 90 days | Control readiness review | Critical | Prepares, but does not itself confer, a SOC 2 audit-readiness claim. | external_dependency |
| HCM-023 | SOC 2 Type I decision | HoloOps SOC / Taylor / Legal | Trust Lead, Security Lead | tbd | `docs/trust/HOLOENGINE_SOC2_TYPE_I_GO_NO_GO_DECISION_RECORD_V0_1.md` | 90 days | Auditor scoping packet and budget | Critical | Opens or closes the Type I pursuit path; no external claim by itself. | external_dependency |
| HCM-024 | SOC 2 Type II planning | Trust Lead / Security Lead / SRE | Legal | tbd | `docs/trust/HOLOENGINE_SOC2_TYPE_II_READINESS_PLAN_V0_1.md` | 90 days | Stable controls and Type I decision | High | Sets up an observation-period path only if Type I is credible. | external_dependency |
| HCM-025 | Buyer trust packet v0.2 / questionnaire refresh | Trust Lead / Legal | Product Lead, Security Lead | target_only | `docs/trust/HOLOENGINE_DESIGN_PARTNER_TRUST_PACKET_V0_2.md`, `docs/trust/HOLOENGINE_SECURITY_QUESTIONNAIRE_STARTER_PACK_V0_2.md` | 90 days | Control readiness review and claim gates | High | Updates buyer-facing language only with verified evidence and preserved caveats. | internal_only |
| HCM-026 | Privacy / legal package | Legal / Privacy Lead | Trust Lead, Product Lead | tbd | `docs/trust/HOLOENGINE_PRIVACY_LEGAL_REVIEW_PACKET_V0_1.md` | 90 days | Provider evidence and data map | Critical | Unblocks privacy, DPA, and customer-data terms review without making a DPA/BAA claim. | external_dependency |
| HCM-027 | ISO 27001 / ISO 42001 decision | Trust Lead / Legal / Security Lead | Product Lead | tbd | `docs/trust/HOLOENGINE_ISO_DECISION_MEMO_V0_1.md` | 90 days | SOC control maturity and budget | Medium | Decides whether ISO work begins; it is not a certification claim. | internal_only |
| HCM-028 | HIPAA / BAA go/no-go | Legal / Privacy Lead / Product Lead | Trust Lead, Security Lead | tbd | `docs/trust/HOLOENGINE_HIPAA_BAA_GO_NO_GO_MEMO_V0_1.md` | 90 days | Buyer pipeline and provider evidence | Critical | Keeps healthcare claims blocked until counsel and provider evidence are real. | external_dependency |
| HCM-029 | Provider zero-retention review | Legal / Security Lead / AI Governance Lead | Trust Lead | tbd | `docs/trust/HOLOENGINE_PROVIDER_ZERO_RETENTION_REVIEW_MEMO_V0_1.md` | 90 days | Provider contract and configuration evidence | Critical | Keeps zero-retention claims blocked until provider-specific proof exists. | external_dependency |
| HCM-030 | External assessment budget | HoloOps SOC / Taylor | Trust Lead, Legal, Security Lead | target_only | `docs/trust/HOLOENGINE_90_DAY_EXTERNAL_SPEND_PLAN_V0_1.md` | 90 days | Control readiness review and buyer pressure | Medium | Selects which external lane opens next; it does not itself create a trust claim. | internal_only |

## Working Rules

1. Use the owner roles exactly as written here when assigning work.
2. Treat `target_only` as design work, not as operating evidence.
3. Treat `missing` as a real gap that needs a due date and an artifact.
4. Treat `tbd` as a workstream that depends on provider, legal, auditor, or deployment confirmation.
5. Keep HoloVerify evidence separated from production customer-mode evidence in both storage and claim language.
