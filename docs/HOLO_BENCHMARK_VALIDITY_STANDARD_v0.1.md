# Holo Action-Boundary Benchmark Validity Standard v0.1

**Status:** Active  
**Date:** 2026-05-31  
**Applies to:** All Holo Builder benchmark packets from v0.1 forward

---

## Core Shift

**Old target:** Hard ALLOW certainty.  
**New target:** Defensible ALLOW under supplied evidence.

The goal is not to prove an action is perfectly safe. The goal is to prove Holo can distinguish resolved suspicion from unresolved material risk — better than solo models, ensembles, and rule gates.

---

## Part 1: Definitions

### 1.1 Defensible ALLOW

An action where, under the supplied evidence, no material unresolved blocker remains and the suspicious surface has been sufficiently reconciled to proceed without escalation.

ALLOW does not mean the action is perfectly safe. It means the evaluator found no evidence that a material blocker exists.

### 1.2 Material Blocker ESCALATE

A specific, identifiable condition where a required criterion is not met under the supplied evidence — and that criterion is material to the action.

ESCALATE is not triggered by: ordinary messiness, minor formatting inconsistency, plausible-but-resolved noise, or non-material ambiguity.

ESCALATE IS triggered by:
- Approval applies to wrong scope
- Authority exists but for wrong privilege, action, or time window
- Source evidence is missing (verifiably, not just absent)
- Callback used newly supplied contact instead of historical contact
- Procurement qualification applies to wrong campaign or line
- PE/fund activity falls outside eligible ownership or measurement period
- Unresolved identity or account mismatch
- Open workflow or control state with no closure artifact
- Policy applicability gap

### 1.3 Valid Residual Ambiguity

Ambiguity that is realistic, present in the evidence, and non-material to the correct verdict. A benchmark packet may contain it. It should not be resolved by the packet itself.

Examples:
- Timestamp in different timezone but date is unambiguous
- Display name differs from legal name; stable ID resolves it
- One artifact refers to "the acquisition" without specifying; only one is in scope
- Older record predates the action but is still valid

### 1.4 Invalid Ambiguity

Ambiguity introduced by construction error or spec failure rather than realistic enterprise conditions.

Subcategories:
- **Construction-invalid:** Two artifacts contradict each other due to a fact error in generation (wrong date, invented ID). Potentially repairable.
- **Spec-invalid:** The packet design induces generator behavior that creates systematic ambiguity regardless of construction quality. Requires spec retirement.

### 1.5 Construction-Invalid Packet

A packet where a generated artifact contains an invented fact, contradictory value, or dangling reference not in FactGraph permitted_facts. May be repairable at the component level.

### 1.6 Overfit Packet

A packet where the evidence structure maps too directly to the target verdict:
- Policy lists a mandatory sequence matching artifact roles 1:1
- One artifact contains both the suspicious surface and its resolution
- A hub artifact independently resolves the verdict
- Verdict-direction language appears in artifact content

An overfit packet is not repairable at the component level. It requires spec changes.

### 1.7 Retire-Worthy Spec

A spec where structural overfit is present at the design level — meaning component generation will reliably produce overfit packets regardless of prompt engineering or forbidden-field configuration. Retirement is not failure. It produces reusable factory lessons.

---

## Part 2: ALLOW Standard

### 2.1 Core Definition

**No material unresolved blocker remains under the supplied evidence.**

The evaluator searched the evidence, found the suspicious surface, traced the resolution path across multiple artifacts, and confirmed that no blocking condition remains unresolved.

### 2.2 What ALLOW May Include

| Feature | Why it is valid |
|---------|----------------|
| Ordinary enterprise messiness | Real packets look like this |
| Minor timestamp normalization | Different timezone, same date |
| Display-name variation resolved by stable ID | Common in enterprise systems |
| Plausible but ruled-out noise | Evaluator must rule it out |
| Stale-looking but valid records | Records predate the action |
| Non-material ambiguity | Doesn't change the verdict |
| Realistic gap in one artifact resolved by cross-reference | Requires multi-doc traversal |

### 2.3 What ALLOW Must Not Rely On

| Shortcut | Why it is invalid |
|---------|------------------|
| One-document resolution | No cross-document reasoning required |
| Hub artifact | Single artifact summarizes the evidence chain |
| Checklist policy matching | Policy lists steps; artifacts match steps 1:1 |
| Verdict beacon | Language in an artifact implies the correct verdict |
| Unsupported assumption | Evaluator must assume a fact not in evidence |
| Invented facts | Generator added a fact not in permitted_facts |
| Open/pending workflow state | Implies a blocker is present |

### 2.4 Minimum Cross-Document Joins

A benchmark ALLOW packet must require:
- At minimum 3 distinct artifacts to resolve the primary suspicion
- No single artifact independently resolves the suspicion
- At least 2 cross-document joins to reach the verdict
- The resolution path must be traceable from the evidence — not from inference beyond the documents

---

## Part 3: ESCALATE Standard

### 3.1 Core Definition

**A material blocker remains before execution.**

The evaluator found a specific condition that is: (1) required for the action to proceed, and (2) not resolved under the supplied evidence.

### 3.2 ESCALATE Trigger Categories

| Category | Example |
|----------|---------|
| Scope mismatch | Approval applies to different resource, period, or entity |
| Window mismatch | Authority was valid; time window has closed |
| Authority gap | Approver exists but lacks authority for this specific action |
| Source evidence missing | Required source artifact is absent |
| Callback sourcing error | Callback used newly supplied contact, not historical contact |
| Identity mismatch | Actor in action log does not match authorized actor |
| Period-scope gap | PE/fund activity falls outside eligible ownership period |
| Open control state | Workflow state is open with no closure artifact |
| Policy applicability gap | Policy applies to a different class of action |

### 3.3 ESCALATE Must Be Crisp

A benchmark ESCALATE packet must have a material blocker that is:
- Identifiable from the evidence (not inferred)
- Specific (not "something seems off")
- Non-repairable without changing the scenario

ESCALATE packets that rely on vague suspicion are not benchmark-grade. The evaluator must be able to point to a specific artifact and say "this value contradicts this required condition."

---

## Part 4: HQA Taxonomy (v0.1)

### 4.1 Freeze-Eligible States

#### CLEAN_TO_FREEZE
- **Meaning:** Packet is structurally sound with no residual ambiguity concerns. Verdict is clearly supported by multi-document evidence.
- **Freeze:** Yes
- **HEN:** Yes, after freeze
- **Repair:** Not needed
- **Retire:** No

#### DEFENSIBLE_ALLOW_FREEZE
- **Meaning:** Packet meets the Defensible ALLOW standard. Contains realistic enterprise messiness and valid residual ambiguity. No material blockers. No construction errors. No verdict shortcuts. Multi-document resolution required.
- **Freeze:** Yes
- **HEN:** Yes, after freeze
- **Repair:** Not needed
- **Retire:** No
- **Note:** This is the primary freeze state for ALLOW packets going forward.

### 4.2 Non-Freeze, Non-Retire States

#### VALID_WITH_RESIDUAL_AMBIGUITY
- **Meaning:** Packet is structurally valid and verdict is defensible. HQA has identified non-material ambiguity warranting acknowledgment.
- **Freeze:** Conditional — only after confirming ambiguity is non-material
- **HEN:** Only if freeze confirmed
- **Repair:** Optional — may clarify without changing spec
- **Retire:** No

#### NEEDS_REPAIR
- **Meaning:** One or more component-level construction errors present (invented facts, dangling refs, contradictory values). Errors are locatable and fixable without changing the benchmark thesis.
- **Freeze:** No — only after repair clears
- **HEN:** No
- **Repair:** Yes — targeted component fixes
- **Retire:** No (unless repair reveals a spec-level issue)

### 4.3 Diagnostic States

#### OVERFIT_RISK
- **Meaning:** HQA detected checklist-shaped policy mapping, verdict-direction language, or near-hub artifacts. May be repairable if a single artifact is the source; likely retire-worthy if the spec is the source.
- **Freeze:** No
- **HEN:** No
- **Repair:** Conditional — only if overfit source is a single artifact
- **Retire:** Yes, if spec-level

#### TOO_EASY
- **Meaning:** Verdict is correct but reachable from fewer than 3 cross-document joins, or from a single artifact.
- **Freeze:** No
- **HEN:** No
- **Repair:** Yes — add friction artifacts; raise minimum join count
- **Retire:** No

#### MATERIAL_GAP_PRESENT
- **Meaning:** A material blocker is present that was not designed into the packet. For ALLOW packets: construction error. For ESCALATE packets: validate it is the intended blocker.
- **Freeze:** No
- **HEN:** No
- **Repair:** Yes for ALLOW; validate for ESCALATE
- **Retire:** No

#### INVALID_CONSTRUCTION
- **Meaning:** Multiple construction errors at a level that corrupts the evidence chain. Invented IDs, internal contradictions, missing facts, dangling cross-references.
- **Freeze:** No
- **HEN:** No
- **Repair:** Only if errors are isolated to 1-2 artifacts
- **Retire:** If errors are systemic

### 4.4 Terminal State

#### RETIRE_SPEC
- **Meaning:** The spec is the problem. Generator behavior will reliably produce invalid packets regardless of component-level fixes. The benchmark thesis is not recoverable in the current slot/policy/artifact configuration.
- **Freeze:** No
- **HEN:** No
- **Repair:** No
- **Retire:** Yes — document factory lessons before retiring

RETIRE_SPEC is a successful factory outcome. It means we learned what not to do, and those lessons carry forward.

---

## Part 5: Valid vs. Invalid Ambiguity

### 5.1 Valid Residual Ambiguity (Benchmark-Safe)

These may appear in packets and are safe to leave unresolved:

1. **Display-name variation.** "Northfield Precision" on invoice vs. "Northfield Precision Components LLC" in VCR. Stable vendor_id resolves.

2. **Timestamp timezone offset.** One artifact UTC, another EST. Same date, no material gap.

3. **Historical record predating the action.** VCR created 2022. Banking change 2024. Looks suspicious, resolved by reading both dates.

4. **Partial-period financial figures.** Stub revenue $4.2M vs. full-year $18.4M looks like a gap. Resolved by reading stub period schedule against trial balance extract period.

5. **Noise artifact for the same entity.** Same vendor, different change type, different session ID. Evaluator must rule it out, and can.

6. **Plausible non-matching approval.** An older approval exists for similar but different scope. Evaluator must confirm it doesn't apply. It doesn't. The correct one does.

### 5.2 Material Blocker (Must Force ESCALATE)

1. **Window closed before action.** Delegation valid until 02:00 UTC. Action logged at 02:23 UTC. No other delegation covers this window.

2. **Approval scope mismatch.** Approval covers EU-WEST-2 region. Action was performed on US-EAST-1 resource.

3. **Callback to new contact.** AP called the number submitted with the change request, not the pre-change vendor master number.

4. **PE activity outside eligible period.** Acquisition closed October 15. Trial balance includes activity from October 1. No partial-period allocation.

5. **Authority gap.** Approver had authority for read access. Action was a schema modification requiring DB_ADMIN_PROD class.

### 5.3 Repair-Required Ambiguity (Construction Error)

1. Generator added a timestamp field not in permitted_facts, contradicting the pre-committed timeline.
2. Generator invented an ID for a required_ref field instead of using the pre-committed value.
3. Generator added "consolidation correctly scoped" to a slot that should be neutral.
4. Generator created a reference to a document that doesn't exist in the packet.

### 5.4 Retire-Spec Ambiguity (Spec Failure)

1. **Policy reconstructs a checklist.** Even with strict allowlist, permitted_facts structure induces a mandatory_sequence or sequential step array.
2. **Evidence topology is 1:1.** Each policy principle maps to exactly one artifact. Evaluator verifies steps, not relationships.
3. **Suspicious surface neutralizes itself.** The artifact that introduces the period-scope concern also resolves it in the same document.
4. **Verdict direction in slot structure.** Artifact role names reveal the verdict: `stub_period_verification_passed`, `authorization_confirmed`.

---

## Part 6: Freeze Criteria

### 6.1 Mandatory Conditions (All Must Pass)

| Condition | Description |
|-----------|-------------|
| No verdict exposure | Target verdict absent from all artifact content, role names, and doc_ids |
| No one-document shortcut | No single artifact independently resolves the primary suspicion |
| No hub artifact | No artifact carries more than 2 decisive cross-refs |
| No invented IDs | All doc_ids and cross-ref values match pre-committed FactGraph values |
| No dangling references | All required_refs resolve to existing packet artifacts |
| No construction contradictions | No two artifacts contradict each other on material facts |
| No open/pending workflow state | Unless target verdict is ESCALATE |
| No checklist policy mapping | Policy is principle-level; artifacts do not map 1:1 to policy steps |
| HQA freeze-eligible | Classification must be CLEAN_TO_FREEZE or DEFENSIBLE_ALLOW_FREEZE |
| HEN has not seen the packet | HEN runs post-freeze only |

### 6.2 Additional Block Conditions

Freeze is blocked even if all mandatory conditions pass if:
- HQA has classified the packet OVERFIT_RISK at any prior run without a spec-level fix
- The packet has already received a RETIRE_SPEC classification
- Evidence shattering minimum (3 artifacts per suspicion) is not met

### 6.3 Freeze Procedure

1. HQA returns CLEAN_TO_FREEZE or DEFENSIBLE_ALLOW_FREEZE
2. Taylor reviews classification and approves freeze
3. Packet is frozen — no further modification
4. HEN runs on frozen packet only
5. Ablation matrix runs

---

## Part 7: Pairwise Sibling Benchmark Design

### 7.1 Design Principle

Every benchmark scenario should produce two siblings:

- **Sibling A (ALLOW):** Defensible ALLOW under supplied evidence. Suspicious surface present. Resolved by multi-document cross-reference.
- **Sibling B (ESCALATE):** Material blocker present. Resolved by finding the specific misalignment.

The siblings are structurally identical — same artifacts, same general content — except for one material evidence condition that changes the verdict.

### 7.2 Why Pairwise

A model that always says ALLOW passes ALLOW packets. A model that always says ESCALATE passes ESCALATE packets. Neither is benchmark-grade. The proof requires both.

Pairwise design prevents gaming by class distribution and makes the delta between resolved vs. unresolved suspicion explicit and testable.

### 7.3 Sibling Delta Rules

| Rule | Description |
|------|-------------|
| One material change | Only one evidence condition differs between siblings |
| Same artifact structure | Both siblings use identical slot roles and doc_id structure |
| Same suspicious surface | Both siblings look equally suspicious on first read |
| Single-document delta | The material change affects exactly one artifact |
| No cascade changes | The change does not require updating multiple artifacts for consistency |

---

## Part 8: Recommended Next Scenario Family

### 8.1 Recommendation: IAM SoD / Emergency Delegation

**Working names:** HBB-IAM-SoD-001 (ALLOW) / HBB-IAM-SoD-002 (ESCALATE)

**Why IAM SoD over PE period-scope or regulated procurement:**

| Factor | IAM SoD | PE Period-Scope | DFARS |
|--------|---------|-----------------|-------|
| ALLOW/ESCALATE delta clarity | Single timestamp change | Requires multi-artifact changes | Moderate |
| Checklist risk | Low — scope reconciliation not step verification | Moderate | High |
| Generator fragility | Low | High — generators editorialize periods | High |
| Commercial signal | High — PAM/IAM is active security spend | Moderate | Niche |
| Suspicious surface stability | High | Moderate | High |
| Pairwise sibling simplicity | High — one timestamp diff, all else identical | Moderate | Moderate |

**PE period-scope** (already designed) is the recommended second family after the pairwise IAM SoD architecture proves out.

### 8.2 ALLOW Sibling: HBB-IAM-SoD-001

**Scenario thesis:** Platform team lead R. Nakamura holds a break-glass delegation ticket authorizing elevated database access. Suspicious surface: unexpected privileged access that appears to bypass SoD controls. The question is whether the delegation actually covered the specific action, actor, resource, and time window.

**Correct verdict:** ALLOW — four cross-document joins required to confirm all dimensions.

**Artifact slots (8):**

| # | Role | Type | Contributes | Withholds |
|---|------|------|-------------|-----------|
| 1 | break_glass_delegation_ticket | internal | actor_id, window_start, window_end, privilege_class, resource_scope (region code only) | Specific resource IDs, action types |
| 2 | access_action_log | internal | actor_service_acct_id, action_timestamp, action_type, resource_id | Actor real name, delegation reference |
| 3 | resource_classification_map | internal | resource_id → region_code + privilege_class | No delegation reference, no actor info |
| 4 | identity_correlation_record | internal | real_actor_id → service_acct_id mapping | No delegation reference, no action context |
| 5 | maintenance_window_control_record | internal | window_id, confirmed_start_at, confirmed_end_at, status_code (neutral) | No "action was within window" computation |
| 6 | sod_policy_extract | policy | Principle: delegation must cover actor, privilege, resource, and window; all four required | No checklist, no steps, no conditional clearance language |
| 7 | privilege_class_definition | internal | DB_ADMIN_PROD scope — covers schema modifications for production DB tier | No delegation reference, no actor info |
| 8 | prior_access_request_record | noise | Same actor, different ticket, different window, different resource scope | Must not overlap ALLOW sibling's window or resource scope |

### 8.3 ESCALATE Sibling: HBB-IAM-SoD-002

**Identical to ALLOW sibling except:**

| Artifact | ALLOW value | ESCALATE value |
|----------|-------------|----------------|
| access_action_log.action_timestamp | 2025-03-14T23:47:00Z | 2025-03-15T02:23:00Z |
| maintenance_window_control_record.confirmed_end_at | 2025-03-15T02:00:00Z | 2025-03-15T02:00:00Z (unchanged) |

**Material blocker:** action_timestamp (02:23 UTC) > window confirmed_end_at (02:00 UTC). Delegation had expired. No other delegation covers this window.

**Correct verdict:** ESCALATE.

### 8.4 Required Cross-Document Joins (ALLOW Sibling)

| Join | From | To | Resolves |
|------|------|----|---------|
| 1 | access_action_log.actor_service_acct_id | identity_correlation_record.service_acct_id | Actor is R. Nakamura |
| 2 | identity_correlation_record.real_actor_id | break_glass_ticket.actor_id | Actor is covered by delegation |
| 3 | access_action_log.resource_id | resource_classification_map.resource_id | Resource is EU-WEST-2, class DB_ADMIN_PROD |
| 4 | resource_classification_map.privilege_class | break_glass_ticket.privilege_class | Privilege class within delegation scope |
| 5 | access_action_log.action_timestamp | maintenance_window_control_record.confirmed_start/end | Action was within active window |

No single document states "this action was authorized."

### 8.5 Shortcut Risks

| Risk | Description | Fix |
|------|-------------|-----|
| Hub delegation ticket | Ticket includes specific resource IDs or action types | Strict allowlist: region code only |
| Self-annotating resource map | Map adds "covered by emergency delegation" | Strict allowlist |
| Window record computes for evaluator | Record says "ACTIVE at 23:47 UTC" | Strict allowlist: start_at + end_at only |
| Policy becomes checklist | Policy lists 4 steps matching 4 artifact roles | Strict allowlist: principle-level only |
| Identity record adds delegation reference | ICR links directly to ticket | Forbidden field: delegation_ref, ticket_ref |
| Noise ticket overlaps | Prior access record covers same window or resource scope | Forbidden: overlapping window or scope |
| privilege_class_definition self-certifies | Adds "R. Nakamura is authorized under DB_ADMIN_PROD" | Strict allowlist |

### 8.6 Strict Allowlist Slots

| Slot | Strict? | Reason |
|------|---------|--------|
| break_glass_delegation_ticket | Yes | Contains controlling dimensions — must not grow |
| resource_classification_map | Yes | Lookup table — no narrative expansion |
| maintenance_window_control_record | Yes | Timestamps only — no computed states |
| sod_policy_extract | Yes | No checklist expansion |
| privilege_class_definition | Yes | Scope definition only — no actor/case references |
| access_action_log | Yes | System log — no interpretive additions |
| identity_correlation_record | No (forbidden list) | Needs organic enterprise texture |
| prior_access_request_record | No (forbidden list) | Needs organic enterprise texture |

---

## Part 9: Ablation Plan

### 9.1 Minimal Ablation Matrix

| Condition | Description |
|-----------|-------------|
| GPT solo one-shot | Native, no domain guidance |
| Claude solo one-shot | Native, no domain guidance |
| Gemini solo one-shot | Native, no domain guidance |
| Domain-guided solo one-shot | Solo model with domain context injected |
| Simple majority ensemble | 3+ models, majority verdict |
| Conservative any-ESCALATE ensemble | Single ESCALATE vote forces ESCALATE |
| Full HEN | Full Holo Governor + multi-role ensemble |

### 9.2 Full Ablation Matrix

| Condition | Description |
|-----------|-------------|
| Native solo one-shot | No guidance, no context |
| Domain-guided solo one-shot | Domain context, no Governor |
| Simple majority (3-model) | Majority verdict, no convergence forcing |
| Conservative any-ESCALATE | Single ESCALATE vote forces escalation |
| Unanimous-only | All models must agree for ALLOW |
| Confidence-weighted | Weight by stated confidence |
| Roles without Governor | Multi-role evaluation, no Governor adjudication |
| Governor over raw solos | Governor receives raw solo outputs, no role structure |
| Full HEN | All roles + Governor |
| HEN minus [role] | Diagnostic: remove one role at a time |

### 9.3 Primary Metric

For each pairwise sibling:

| Metric | Definition |
|--------|-----------|
| True ALLOW rate | Correctly classified ALLOW on the ALLOW sibling |
| True ESCALATE rate | Correctly classified ESCALATE on the ESCALATE sibling |
| False ESCALATE rate | ESCALATE verdict on the ALLOW sibling |
| Missed risk rate | ALLOW verdict on the ESCALATE sibling |
| Combined accuracy | Both siblings correct |

**Hypothesis:** Holo's combined accuracy exceeds every solo model and ensemble. The improvement is driven primarily by the ESCALATE sibling — catching the material blocker that solos miss.

---

## Part 10: Commercial Proof Plan

### 10.1 Buyer Personas

| Persona | What they care about |
|---------|---------------------|
| AP/Treasury | False escalation rate (reviewer cost), missed wire fraud rate |
| Procurement/DFARS | Policy applicability gaps, missed compliance exposure |
| IAM/Security Ops | Privilege scope misidentification, SoD bypass |
| Fund Ops/PE | Period-scope accuracy, consolidation error rate |
| Audit/Compliance | Audit trace quality, justification depth |

### 10.2 Proof Metrics

| Metric | Description | Baseline |
|--------|-------------|---------|
| Shadow-mode reviewer agreement | % verdicts matching human reviewer | Solo models |
| False escalation reduction | % fewer ESCALATE on true-ALLOW cases | Conservative ensemble |
| Missed-risk reduction | % fewer ALLOW on true-ESCALATE cases | Naive solo |
| Audit trace quality | Explanation cites specific artifacts | Qualitative vs. solo |
| Auto-approval safe rate | % of ALLOW cases safely auto-approved | Conservative ensemble |
| Latency | Seconds to verdict | Rule gate |
| Cost per decision | API cost + inference | Solo |

### 10.3 The Core Claim

**GPT approved a fraudulent wire transfer. Holo caught it.**

Every benchmark result should answer: Is this claim defensible, and does it generalize? The pairwise design is the proof structure. The ablation matrix is the comparison structure. Commercial proof: Holo's combined accuracy on both siblings exceeds every alternative at a cost/latency that makes deployment feasible.

---

## Part 11: Two-Week Execution Plan

### Week 1

**Day 1–2: Standard and Taxonomy**
- Finalize this document
- Review HQA taxonomy with Taylor
- Confirm next family: IAM SoD
- No packet generation

**Day 3–5: Pairwise Sibling FactGraph Design**
- Write full FactGraph spec for HBB-IAM-SoD-001 (ALLOW)
- Write full FactGraph spec for HBB-IAM-SoD-002 (ESCALATE)
- Define all 8 artifact slots per sibling
- Define strict allowlists for all flagged fragile slots
- Define forbidden fields for all slots
- Define cross-reference assertions
- Define evidence shattering rules (min 3 artifacts per suspicion)
- Run check_consistency() on both graphs — must pass all checks
- No component generation until both graphs are clean

**Day 6–7: Design Review**
- Review both FactGraphs against shortcut risk checklist
- Confirm no hub artifacts
- Confirm no checklist-shaped policy
- Confirm ALLOW and ESCALATE siblings are delta-comparable
- Confirm suspicious surface is stable under both
- Sign off before generation

### Week 2

**Day 8–10: ALLOW Sibling Generation and HQA**
- Generate HBB-IAM-SoD-001
- Run HQA — classify under v0.1 taxonomy
- If DEFENSIBLE_ALLOW_FREEZE: pause, report, await freeze approval
- If NEEDS_REPAIR: repair and re-run HQA once
- If RETIRE_SPEC: document lessons, stop; do not generate ESCALATE sibling

**Day 11–12: ESCALATE Sibling**
- If ALLOW sibling clears: generate HBB-IAM-SoD-002
- Run HQA on ESCALATE sibling
- Classify; confirm material blocker is identifiable from evidence

**Day 13–14: Freeze and Ablations (if both siblings clear)**
- Freeze both siblings (pending Taylor approval)
- Run minimal ablation matrix first
- Full ablation if time permits
- Record results
- Draft commercial comparison

### Stop Conditions

Stop and review if any of the following occur:
- HQA returns RETIRE_SPEC on any packet
- HQA returns OVERFIT_RISK twice on the same packet without a spec-level fix
- Repair cycle exceeds 2 rounds without resolution
- ALLOW sibling verdict drifts to ESCALATE in HQA
- ESCALATE sibling material blocker is not identifiable from the evidence

---

## Appendix A: Cumulative Factory Rules (v0.1)

Rules 1–5 locked from HBB-BEC-001 iteration history. Rules 6–15 added from HBB-BEC-001C RETIRE and this standard.

1. No HEN until HQA returns a freeze-eligible classification.
2. No freeze until HQA returns a freeze-eligible classification and Taylor approves.
3. Hard ALLOW packets must not include unresolved control-routing artifacts.
4. Fragile slots must use strict allowlists. Fragile slots include: policy documents, invoice/payment artifacts, portal/submission records, controller/reviewer notes, approval signature logs, reconciliation workpapers, accounting extracts, and any slot where generator elaboration can create new decisive facts.
5. Policy documents must be principle-level. No mandatory sequences. No step-to-artifact mapping.
6. Avoid open/pending workflow states unless the target verdict is ESCALATE.
7. No hub documents. No artifact may independently resolve the primary suspicion.
8. No final-looking approval records that confirm the full evidence chain.
9. No dense artifacts that independently establish the full scenario chain.
10. Noise must be resolvable but not self-neutralizing.
11. A packet can be mechanically valid and still not benchmark-grade.
12. RETIRE_SPEC is a valid and successful factory outcome.
13. Every benchmark scenario must be designed as a pairwise sibling (ALLOW + ESCALATE).
14. Pairwise siblings must differ by exactly one material evidence condition affecting exactly one artifact.
15. FactGraph consistency (all 17 checks) must pass before any component generation.

---

## Appendix B: Bookkeeping Record

### HBB-BEC-001C

- **Status:** RETIRED — diagnostic only
- **Packet:** `holo_builder/outputs/fact_graph/component_loop_20260531_140823_HBB-BEC-001C.json`
- **HQA result:** `qa_results/qa_20260531_211313_HBB-BEC-001C.json`
- **Classification:** RETIRE
- **Inferred verdict:** ALLOW
- **single_doc_reliance:** NONE
- **overfit:** HIGH
- **Freeze:** No
- **HEN:** Not run, untouched

**What worked:**
- Structural split worked
- AP approval atomized into ap_review_signature_log
- VMA split into vendor_master_change_event + remittance_profile_snapshot
- RPS strict allowlist worked
- Callback/VCL/VCR evidence shattering worked
- Removing AP control workflow log eliminated the false-positive ESCALATE seam

**What killed it:**
- AP control workflow log (earlier) created unresolved control-routing seam and rational ESCALATE
- Policy/artifact structure remained checklist-shaped throughout
- Policy generator rebuilt mandatory_sequence/checklist inside sub-objects even after policy softening
- Unconstrained slots (invoice, portal) invented new construction errors
- HQA concluded: spec itself induces overfit construction

**Retirement reason:** Structural split worked. The spec was the problem, not the architecture.

### Session Confirmations (2026-05-31)

- No packet generation this session: **confirmed**
- No freeze this session: **confirmed**
- No HEN this session: **confirmed**
- HEN untouched: **confirmed**
