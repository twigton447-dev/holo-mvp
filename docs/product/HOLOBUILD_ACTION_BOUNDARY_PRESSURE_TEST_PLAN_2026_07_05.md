# HoloBuild Action Boundary Pressure Test Plan - 2026-07-05

Status: repo-only inspection. No provider calls. No live product actions. No production behavior changes. No staging, commit, or push.

## Executive Finding

HoloBuild is the early product surface for producing high-stakes work that people may rely on. Its product job is not just drafting better prose; it is deciding whether a work product is complete, source-grounded, contradiction-free, and bounded enough to be trusted.

The repo currently contains three overlapping HoloBuild surfaces:

1. An AP/BEC benchmark packet builder under `holo_builder/` with build, lint, QA attack, freeze, and final authorization commands.
2. A newer `action_boundary` packet format inside the same builder/lint loop.
3. A staged product-style creative fixture for VeSync that inherits the HoloBuild architecture contract but explicitly says the current AP/BEC runtime should not be used for that fixture without a dedicated creative adapter.

The safe product boundary is therefore: HoloBuild may draft, critique, trace, and classify candidate work products; it must not release, publish, execute, freeze, claim benchmark proof, or authorize downstream business action without deterministic gates and explicit human approval.

## Repo Evidence

| Finding | Repo evidence |
| --- | --- |
| Product copy says HoloBuild works early on work people may rely on, such as contracts, compliance memos, finance briefs, diligence packets, procurement justifications, and payment-release analysis. | `docs/whitepaper.md:129-153` |
| HoloBuild is distinct from HoloVerify: HoloVerify asks whether an action should execute; HoloBuild asks whether AI can produce high-stakes work complete enough to rely on. | `docs/whitepaper.md:467-493` |
| Architecture contract requires lossless canonical-thread access and blocks silent summarization/truncation. | `holo_builder/ARCHITECTURE.md:6-17` |
| Architecture contract requires live research budgets, source records, missing-evidence visibility, and trace artifacts. | `holo_builder/ARCHITECTURE.md:19-57` |
| CLI exposes separate high-risk verbs: `build`, `lint`, `qa-attack`, `freeze`, and `authorize-final`. | `holo_builder/builder.py:6-39` |
| `lint` is static only and does not call an LLM. | `holo_builder/builder.py:12-13` |
| `qa-attack` is blind to target verdict, builder notes, revision history, promotion metadata, and builder identity. | `holo_builder/qa_attacker.py:1-32`, `holo_builder/qa_attacker.py:464-498` |
| `freeze` requires `CLEAN_TO_FREEZE`, hashes canonical model-visible payload, stamps `_frozen`, writes a frozen packet, and appends a ledger entry. | `holo_builder/freeze.py:1-16`, `holo_builder/freeze.py:44-89` |
| `action_boundary` lint treats `payment_hold=true` as valid scenario setup, requires `context.documents`, and blocks builder/verdict metadata from model-visible action/context. | `holo_builder/lint.py:212-291` |
| Builder convergence requires static lint, QA assessment not blocked, no active structural high categories, and Governor promotion `READY`. | `holo_builder/loop.py:1478-1597` |
| HoloBuild requires at least three providers: one fixed HoloGov plus at least two worker DNA families. | `holo_builder/loop.py:665-690` |
| Builder results record status, turns, QA deltas, fallback events, verdict drift, artifact collapse, assertion events, architecture invariant, providers, coverage, briefs, and token totals. | `holo_builder/loop.py:2440-2530` |
| Policy bridge smoke writes policy request, locked policy envelope, ingest record, policy checks, final artifact when allowed, and run manifest. | `holo_builder/policy_bridge.py:212-353` |
| Policy bridge validator fails missing manifests, missing policy requests, missing ingest records, invalid policy checks, checkpoint mismatch, input mismatch, terminal mismatch, override mutation, and invalid policy envelopes. | `holo_builder/policy_bridge.py:371-430` |
| Product dashboard is read-only by default and live runs require `HOLOBUILD_LIVE_RUNS`. | `main.py:1415`, `main.py:1731-1745`, `main.py:1933-1992` |
| Dashboard sanitizes run traces and exposes status/accounting rather than raw drafts. | `main.py:1423-1433`, `main.py:1495-1571` |
| VeSync fixture warns that current `holo_builder/` runtime is AP/BEC-shaped and should not run the creative fixture without a creative HoloBuild adapter or prompt surface. | `holo_builder/projects/vesync_cosori_levoit_copywriter_exercise_001/README.md:21-32` |
| VeSync run plan requires source classes, research budgets, source storage, lossless canonical thread, and trace artifacts. | `holo_builder/projects/vesync_cosori_levoit_copywriter_exercise_001/03_holobuild_run_plan.json:24-49`, `holo_builder/projects/vesync_cosori_levoit_copywriter_exercise_001/03_holobuild_run_plan.json:50-72` |

## Current Boundary Assessment

HoloBuild should be treated as a governed artifact-build loop, not as an autonomous execution engine.

It may produce:

- Candidate work products.
- Critiques and repair tickets.
- Source records.
- Claim-boundary notes.
- Missing-evidence notes.
- Readiness classifications.
- Frozen evidence packages after gates.
- Design-partner replay views.

It must not independently:

- Publish a document.
- Send a message to a counterparty.
- Release a payment.
- Modify production systems.
- Update a contract, invoice, vendor master, account, or policy record.
- Convert a candidate into official benchmark proof.
- Hide missing evidence or downgrade unresolved risk into style notes.

## 1. What HoloBuild Is Supposed To Do

HoloBuild is supposed to help create high-stakes work products that are safe to rely on before an irreversible action happens.

The intended work products include contract drafts, compliance memos, finance briefs, diligence packets, procurement justifications, payment-release analyses, and product/marketing artifacts where source claims matter. For each artifact, HoloBuild should:

- Preserve the full build history and canonical context.
- Gather or ingest source evidence within declared budgets.
- Turn vague inputs into a structured candidate artifact.
- Attack the candidate for unsupported claims, missing artifacts, contradictions, tells, overfit construction, single-document reliance, and schema failures.
- Use a Governor to enforce non-negotiable constraints and decide whether repair can continue.
- Produce a final candidate only when required gates pass.
- Mark unresolved evidence gaps plainly instead of making the artifact sound ready.

For AP/BEC-style packets, HoloBuild also constructs benchmark/action-boundary cases, tests for leakage, freezes model-visible payloads, and creates evidence that can later be adjudicated blind. For broader product surfaces, the AP/BEC builder should be treated as a pattern, not as a safe generic adapter.

## 2. Risky Decisions And Actions

These decisions can become risky because they change trust state, downstream behavior, or evidence validity:

| Decision/action | Why risky | Required boundary |
| --- | --- | --- |
| Starting provider-backed build or QA turns | Sends task data to external models and can create user-visible cost, privacy, and evidence implications. | Human approval for exact scope. |
| Live web research | Can cite stale, wrong, or low-reliability sources; can exceed budget; can launder missing coverage. | Explicit research budget and source storage before use. |
| Changing `target_verdict` or `hypothesized_verdict` | Converts a build loop into answer-key drift. | Deterministic lock and failure event. |
| Provider fallback or model substitution | Changes experimental/product conditions and can undermine proof comparability. | Predeclared fallback rule; no silent substitution. |
| Marking `BUILDER_CONVERGED` | Moves a candidate toward release or freeze. | Lint, structural gates, Gov promotion, and trace completeness. |
| `builder_approval.approved_for_freeze=true` | Creates a readiness claim. | Must be advisory until deterministic gates and human review pass. |
| `freeze` | Writes immutable-ish evidence and ledger state. | `CLEAN_TO_FREEZE`, correct payload hash for the packet format, and human approval. |
| `authorize-final` | Moves toward blind adjudication or final use. | Human approval after frozen packet review. |
| Publishing/exporting final artifact | External reliance can begin. | Human signoff and partner-visible evidence packet. |
| Treating HoloBuild result as public proof | Benchmark and product evidence can blur. | Root package, lock manifest, scoring protocol, and explicit evidence label. |

## 3. What Should Be Shadow-Only

These should stay shadow-only until the design partner and operator approve a stronger mode:

- Any HoloBuild run launched from the product dashboard.
- Any provider-backed build, QA, Governor, or repair turn.
- Any live research pass.
- Any builder approval result.
- Any readiness or trust score shown to users.
- Any source-reliability classification.
- Any comparison against solo/model baselines.
- Any product-surface adapter outside AP/BEC, including the VeSync creative fixture.
- Any generated artifact that could be mistaken for legal, financial, security, procurement, compliance, HR, medical, or operational advice.
- Any freeze package before the canonical payload hash, source manifest, and QA trace validate.
- Any policy bridge result before all evidence-chain validation passes.

Shadow output may be displayed as a replay, trace, or diagnostic panel, but it should not be the visible source of truth for a real-world action.

## 4. What Should Require Human Approval

Require explicit human approval before:

- Enabling `HOLOBUILD_LIVE_RUNS`.
- Running any provider-backed HoloBuild job from UI or CLI.
- Running live web research.
- Sending task, source, or customer data to a provider.
- Using fallback providers or changing the model roster.
- Accepting a build as `BUILDER_CONVERGED`.
- Accepting a QA result as `CLEAN_TO_FREEZE`.
- Freezing an artifact.
- Authorizing final adjudication.
- Publishing, sending, submitting, or using a HoloBuild artifact externally.
- Promoting a product run into benchmark evidence.
- Using a HoloBuild output to support a payment, contract, procurement, compliance, security, hiring, or customer-facing decision.

Human approval should record approver identity, timestamp, exact artifact hash, approved scope, data-sharing scope, provider/model roster, and the irreversible action that remains forbidden or authorized.

## 5. Likely Failure Modes

| Failure mode | Impact | Existing signal | Required mitigation |
| --- | --- | --- | --- |
| Source laundering | Missing or weak evidence becomes confident artifact language. | Architecture contract says missing evidence must remain visible. | Source-before-claim gate; missing-evidence ledger; claim-to-source map. |
| Context truncation | Later turns lose earlier constraints or accepted/rejected repairs. | Architecture contract requires stop/block instead of silent truncation. | Canonical-thread completeness hash per turn. |
| Verdict drift | Builder changes target/hypothesized verdict to fit draft. | Loop has verdict-lock checks and unresolvable drift status. | Deterministic target lock and visible drift event. |
| Action-boundary metadata leak | Builder approval, verdict, or rationale appears in model-visible `action`/`context`. | `lint.py` blocks leaky action-boundary fields. | Fail closed before QA/freeze. |
| Incorrect freeze hash for top-level action-boundary packets | Legacy freeze hashes `packet.payload`, while action-boundary uses top-level `action`/`context`. | `freeze.py` canonicalizes only `packet.payload.action/context`. | Packet-format-aware hash gate before freeze. |
| Missing assertion module | Legacy loop imports `holo_builder.assert_packet`, but the module is absent in this checkout. | `importlib.util.find_spec('holo_builder.assert_packet')` returned `None`. | Restore, replace, or disable claims about assertion repair before live use. |
| Provider fallback changes the lane | Fallback can change model DNA and comparability. | Loop logs fallback events. | Predeclared fallback policy and partner-visible fallback accounting. |
| QA blind leak | QA sees target, builder notes, or filename tells. | QA code strips metadata before calls. | Test that only action/context crosses the QA boundary. |
| Overfit artifact | Candidate is purpose-built and too easy. | QA categories include overfitting, tells, single-doc reliance, verdict difficulty. | Independent QA plus single-doc reliance tests. |
| Product adapter mismatch | AP/BEC prompts run a creative/legal/compliance product task incorrectly. | VeSync README warns current runtime is AP/BEC-shaped. | Domain adapter gate before non-AP/BEC runs. |
| Dashboard overtrust | UI exposes "watch" and trace status that a partner may read as production readiness. | Dashboard is read-only by default and sanitized. | Mode labels: read-only, shadow, candidate, approved-for-review, human-released. |
| Policy bypass | Downstream stage emits or mutates artifact after policy block. | Policy bridge validates no post-checkpoint override. | Terminal release invariant and negative-path tests. |

## 6. HoloVerify-Style Packet For HoloBuild

A HoloBuild packet should be a run-level evidence package, not just the final work product.

Minimum packet shape:

```json
{
  "packet_type": "HOLOBUILD_ACTION_BOUNDARY_PACKET",
  "packet_version": "0.1",
  "packet_id": "HB-<DOMAIN>-<YYYYMMDD>-<RUN>",
  "mode": "shadow_only | approval_required | release_approved",
  "domain": "contract | compliance | finance | diligence | procurement | payment_release | creative | other",
  "task_summary": "...",
  "input_manifest": [],
  "source_manifest": [],
  "canonical_thread": {
    "policy": "lossless",
    "turn_count": 0,
    "canonical_thread_hash": "sha256:...",
    "overflow_status": "ok | blocked_context_overflow"
  },
  "model_roster": {
    "hologov": {},
    "workers": [],
    "fallback_policy": "none | declared",
    "fallback_events": []
  },
  "artifact": {
    "candidate_path": "...",
    "candidate_hash": "sha256:...",
    "claim_source_map_path": "...",
    "missing_evidence_path": "..."
  },
  "deterministic_gates": [],
  "governor_decisions": [],
  "qa_attacker": {},
  "policy_bridge": {},
  "freeze_lock": {},
  "human_approvals": [],
  "runtime_accounting": {},
  "trace_inventory": [],
  "terminal_status": "NEEDS_REPAIR | BLOCKED | SHADOW_READY | FROZEN_PENDING_HUMAN | HUMAN_RELEASED"
}
```

Required packet files:

- `input_manifest.json`: user brief, source packet, schema, constraints, redaction state.
- `source_manifest.json`: all sources used, source class, reliability tier, accessed timestamp, evidence snippet, intended use.
- `canonical_thread.jsonl`: full turn-by-turn canonical thread or hash-linked chunks.
- `turn_inputs.jsonl`: system/user payload sent per turn, redacted where needed.
- `turn_outputs.jsonl`: model outputs, parse status, validation status.
- `governor_briefs.jsonl`: Gov constraints, repairs, promotion decisions.
- `qa_attack.json`: independent blind QA classification and repair ticket.
- `deterministic_gates.json`: schema, source, claim, boundary, policy, freeze, and redaction gates.
- `policy_checks.jsonl`: HoloBrain/HoloGov policy locks and terminal release checks.
- `final_candidate_artifact.json`: candidate work product.
- `claim_source_map.json`: every material claim mapped to source, evidence level, and allowed wording.
- `missing_evidence.json`: unresolved gaps that remain visible.
- `run_manifest.json`: terminal status, hashes, files, approvals, provider/model accounting.

The final artifact alone should never be called a HoloBuild proof packet.

## 7. Deterministic Gates

Required gates before any HoloBuild artifact can move past shadow:

1. **Mode Gate:** run mode is one of `read_only`, `shadow_only`, `approval_required`, or `release_approved`; default is `read_only`.
2. **Spec Gate:** spec has domain, task, output schema, risk class, data-sharing scope, target packet format, and stop rules.
3. **Adapter Gate:** domain adapter matches the task; AP/BEC builder cannot run creative/legal/compliance products without the right adapter.
4. **Provider Scope Gate:** provider calls are disabled unless exact provider/model roster and data-sharing scope are approved.
5. **Roster Gate:** at least one fixed HoloGov and at least two worker model families for full HoloBuild claims.
6. **Fallback Gate:** fallback is either disabled or explicitly declared; any fallback changes evidence label.
7. **Canonical Thread Gate:** every turn after turn 1 proves prior content was available or blocks on overflow.
8. **Source-Before-Claim Gate:** material claims require a stored source record before appearing in the candidate.
9. **Missing-Evidence Gate:** unresolved evidence gaps must appear in artifact notes or block release.
10. **Schema Gate:** final candidate matches output schema exactly.
11. **Action-Boundary Metadata Gate:** model-visible `action`/`context` cannot contain verdict, builder approval, rationale, or answer-key metadata.
12. **Target-Lock Gate:** target verdict or hypothesized verdict cannot drift.
13. **Contradiction Gate:** dates, IDs, amounts, contact records, permissions, and policy requirements cannot conflict.
14. **Single-Document Reliance Gate:** no single document can independently resolve the artifact's critical conclusion.
15. **Overfit/Tell Gate:** document titles, fields, or phrasing cannot telegraph the answer.
16. **QA Gate:** independent blind QA must produce `CLEAN_TO_FREEZE` before freeze; otherwise return to repair or retire.
17. **Policy Gate:** release behavior must be caused by locked policy; absent/tampered/mismatched policy fails closed.
18. **Freeze Hash Gate:** payload hash must cover the actual model-visible content for the packet format.
19. **Trace Inventory Gate:** required trace files exist and hash-match the manifest.
20. **Human Approval Gate:** freeze, final adjudication, publication, and downstream reliance require explicit approval.

Known gate gap: the legacy assertion-repair import is absent in this checkout. Do not claim that assertion gate is active until `holo_builder.assert_packet` exists or an equivalent deterministic validator replaces it.

## 8. Runtime Trace And Accounting

Every run should account for:

- Run id, branch/commit, mode, domain, adapter, risk class.
- Provider/model ids per turn.
- HoloGov provider and worker pool.
- System prompt hash, user prompt hash, input hash, output hash.
- Input/output tokens, elapsed ms, retry count, fallback events, parse errors.
- Canonical thread hash before and after each turn.
- Source records captured and source budget used.
- Material claim count, sourced claim count, missing-evidence count.
- QA classifications, category severities, repair ticket, convergence state.
- Gov briefs, promotion decisions, policy checkpoints, terminal status.
- Deterministic gate results with pass/fail reasons.
- Human approvals and exact scope.
- Final candidate hash, freeze hash, ledger entry, release state.

The design-partner replay should show enough to trust the process without leaking raw provider prompts, secrets, private customer data, or builder answer keys.

## 9. What Design Partners Need Before Trusting It

Design partners need to see:

- Clear mode labels: `read-only`, `shadow`, `candidate`, `approved for review`, `human released`.
- A plain statement that HoloBuild does not execute actions or publish artifacts autonomously.
- Side-by-side final artifact plus claim-source map.
- Missing-evidence notes that remain visible instead of being polished away.
- A replay of Builder, QA, and Gov handoff sequence.
- Deterministic gate report with failures as first-class outcomes.
- Source reliability tiers and source budget accounting.
- Provider/model roster, fallback events, and token/cost accounting.
- Negative examples where HoloBuild blocks itself.
- Human approval log before any freeze, release, or downstream reliance.
- Data-handling scope: what went to which provider and what was redacted.
- Evidence labels that distinguish product demo, shadow trace, frozen benchmark proof, and public root-signature package.
- External scoring or review protocol when performance claims are made.

## Acceptance Criteria For This Plan

Before HoloBuild product-surface pilots move beyond shadow:

- `HOLOBUILD_LIVE_RUNS` remains off by default.
- Non-AP/BEC domains have explicit adapters and fixture tests.
- Action-boundary freeze hashing is packet-format-aware.
- Missing `assert_packet` gate is resolved or removed from readiness claims.
- Product dashboard labels cannot be mistaken for production authorization.
- HoloBuild packet generator emits the run-level evidence package above.
- Deterministic gates can be run provider-free against stored traces.
- Human approval is required for freeze, final adjudication, publication, and downstream reliance.

