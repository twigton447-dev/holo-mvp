# Fable HoloEngine Single Mandate

Status: `READY_FOR_FABLE_READ_ONLY_REVIEW`

Date: `2026-07-02`

This is the single mandate to give Fable. It combines the Holo recommendation and Codex handoff into one operating brief.

## Paste This First

```text
Assume the current HoloVerify result may be partially misleading.

Your job is to find the strongest non-architectural explanations for the observed performance, inspect the codebase for mechanisms that could produce false confidence, and design the smallest decisive tests that would separate real architecture gains from confounds.

Specifically, assume the 614-packet result could be explained by one or more of:

- model-family strength rather than architecture;
- packet leakage or packet-family familiarity;
- evaluator bias or permissive admissibility;
- synthetic distribution comfort;
- hidden retries or hidden rescue paths;
- prompt asymmetry across rungs;
- state contamination or artifact carryover;
- selective reporting or packet curation effects;
- deterministic-gate overfitting;
- runtime/reporting bugs.

Start read-only.

Do not make code changes until you produce:

1. a system map;
2. a ranked confound list;
3. a falsification plan;
4. a proposed implementation plan.

All coding must be done through Codex CLI. You act as orchestrator, reviewer, and acceptance gate. Every change aimed at reducing Type I or Type II error must be independently justified against reward hacking. Any benchmark-affecting change must include a note on how it could accidentally inflate apparent performance.

Be ruthless, specific, and repo-backed. Do not write marketing copy.
```

## Goal

The goal is not "review and refactor the codebase." That is too loose.

The goal is to harden HoloEngine by testing whether its strongest evidence could be fooling us, then turning the surviving findings into controlled implementation work.

Fable should help answer:

- Is HoloVerify's apparent advantage truly architectural?
- Are the frozen packet, trace, and scoring systems trustworthy?
- Are Type I and Type II error reductions real, or artifacts of gates/prompts/evaluation?
- Are HoloChat, HoloBuild, and HoloVerify implementing the same enforcement spine where they claim to?
- What is the smallest set of tests or patches that would most improve confidence without reward hacking?

## Non-Negotiable Rules

- Start read-only.
- Do not edit frozen benchmark packets, prompts, traces, lock manifests, evidence packages, or public result files.
- Do not run providers unless Taylor explicitly approves the exact provider scope.
- Do not run judges unless Taylor explicitly approves the exact judge scope.
- Do not optimize toward benchmark numbers without independent review.
- Do not hide failures, invalid runs, parse failures, provider failures, ambiguous rows, or unfavorable comparisons.
- Separate official locked evidence from diagnostic, canary, smoke, invalid, or exploratory evidence.
- Separate product hardening from benchmark evidence.
- Do not change benchmark packets to improve metrics.
- Do not loosen gates merely to increase admissibility.
- Do not silently substitute models, prompts, packets, policies, or output contracts.
- Every benchmark-affecting change must include a reward-hacking risk note.

## Current Evidence Context

The current headline evidence should be treated as strong but not sacred:

> On this frozen 614-packet corpus, HoloVerify observed 0 false positives and 0 false negatives. The one-sided 95% upper confidence bound is approximately 0.97% per side.

Keep that exact scope attached. Do not turn it into a universal "zero errors" claim.

The current interpretive frame is:

> HoloVerify's result is strong; the ablations are there to test what actually caused it.

Fresh ablation context:

- Randomized corpus-balanced no-Gov ablation run:
  - `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/live_runs/run_20260702T205951Z`
- Provider calls: `144/144`
- Gov calls: `0`
- Holo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- Parse failures: `2`
- Strict admissible-correct no-Gov units: `13/24`
- Tokens: `158,143 input / 55,367 output / 240,092 total`

Solo ablation-series baseline status:

- Preflight is ready for `12` packets across `6` sibling pairs.
- Expected live calls: `36`
- Models:
  - `xai/grok-3-mini`
  - `openai/gpt-5.4-mini`
  - `minimax/MiniMax-M2.5-highspeed`
- Gov/Holo/judges: `0`
- Provider calls made during preflight: `0`
- Approval hash: `48e906a7c9d4527ab69aec45ae0394e6f106e3c885a05c9d6963284ed4483f4d`

## Read Folders In This Order

Do not start with the UI. Start where false certainty is born.

### 1. Evaluation And Benchmark Harness

Inspect anything defining:

- packet loading;
- frozen corpus handling;
- label adjudication;
- scoring logic;
- strict-admissible correctness;
- FPR/FNR accounting;
- result aggregation;
- report generation;
- statistical appendices;
- lock roots and hash manifests.

Start here:

- `docs/benchmark/HOLOVERIFY_STATISTICAL_APPENDIX_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_STATISTICAL_APPENDIX_2026_07_01.json`
- `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/`
- `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/`
- `docs/benchmark/HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_WAVE5_COMPLETED_BATCH_EVIDENCE_2026_07_01.md`
- `docs/benchmark/holoverify_20pair_3dna_2026-06-29/`
- `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/`
- `docs/benchmark/holoverify_it_access_replication_2026-06-30/`
- `docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29/`
- `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/`
- `docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/`
- `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/`

Primary questions:

- Does the `614` denominator reconcile from packet-level evidence?
- Are `ALLOW` and `ESCALATE` denominators both `307`?
- Are FPR/FNR definitions correct?
- Are score-valid, diagnostic, invalid, and public evidence lanes separated?
- Are prompt hashes and generated provider-prompt hashes frozen for every ablation rung?
- Could the aggregation logic make the system look cleaner than it is?

### 2. Governor / Decision Logic

Inspect anything implementing:

- Gov logic;
- action-boundary decisions;
- escalation rules;
- deterministic gates;
- monotonic preservation;
- best-artifact preservation;
- final selector behavior;
- trace/accounting logic.

Start here:

- `holo_architecture_invariants.py`
- `hologov_v_signer.py`
- `hologov_v_signer_service.py`
- `benchmark_form_actuator.py`
- `benchmark_dynamic_gov_router.py`
- `benchmark_full_gated_judge.py`
- `benchmark_proof.py`
- `benchmark_telemetry.py`
- `docs/benchmark/run_ap_replication_holoverify_3dna_2026_06_29.py`
- `docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py`
- `docs/benchmark/run_kita_11arch_ablation_reprise_2026_07_02.py`
- `docs/benchmark/run_kita_randomized_corpus_balanced_ablation_2026_07_02.py`
- `docs/benchmark/run_kita_ablation_series_solo_one_shot_2026_07_02.py`
- `tests/test_holo_surface_architecture_invariants.py`
- `tests/test_holoverify_governed_decision_smoke.py`
- `tests/test_benchmark_form_actuator.py`
- `tests/test_kita_11arch_ablation_reprise.py`
- `tests/test_kita_randomized_corpus_balanced_ablation.py`

Primary questions:

- Can Gov ever call something ready when gates fail?
- Is the actuator actually binding, or merely advisory?
- Is the final selector monotonic and auditable?
- Are content failures and malformed Gov batons fail-closed?
- Are transport retries limited to transport failures only?
- Are Gov tokens and worker tokens separately accounted?

### 3. Prompt / Policy / Packet Orchestration Layer

Inspect anything controlling:

- rung-specific prompts;
- role prompts;
- no-Gov versus Gov execution differences;
- packet freezing/versioning;
- state injection;
- memory/context injection;
- artifact passing between turns;
- model routing and call budgets.

Primary questions:

- Are comparisons fair, or is one rung getting a better prompt?
- Does any solo/no-Gov condition accidentally receive Holo-only help?
- Does any Holo condition receive hidden answer-key leakage?
- Are model rosters and call counts bound by run lock?
- Is Gov forbidden from choosing models where the protocol says routing is fixed?

### 4. Runtime / Failover / Model Orchestration

Inspect anything involving:

- provider routing;
- retries;
- failover;
- hidden second chances;
- model selection;
- timeout handling;
- partial result recovery.

Primary questions:

- Could runtime behavior quietly rescue bad turns?
- Are invalid traces preserved?
- Are retries logged as retries?
- Are provider failures separated from verdict failures?
- Are parse/content failures correctly non-retryable?

### 5. Logging / Observability / Trace Surfaces

Inspect anything recording:

- raw decisions;
- intermediate artifacts;
- rejected outputs;
- retries;
- hidden corrections;
- state transitions;
- benchmark traces;
- token accounting.

Primary questions:

- Can an outside reviewer reconstruct what happened?
- Are raw failed outputs preserved?
- Do summaries match traces?
- Are immutable traces useful for auditors, regulators, compliance, and insurance?

### 6. HoloChat Product Surface

Only after engine truth:

- `main.py`
- `chat_engine.py`
- `holo_governed_shadow.py`
- `holo_state.py`
- `holo_context.py`
- `holo_router.py`
- `holo_trace.py`
- `holo_release.py`
- `holobrain/`
- `holo_profiles/`
- `frontend/`
- `tests/test_holochat_governed_shadow.py`
- `tests/test_holochat_runtime_routing.py`
- `tests/test_holochat_shadow.py`
- `tests/test_holochat_web_checked.py`
- `tests/test_holo_state.py`
- `tests/test_holo_context.py`
- `tests/test_holo_router.py`

Primary questions:

- Is HoloChat using the correct governed-shadow architecture?
- Does normal chat remain intact when shadow is off?
- Are runtime labels honest?
- Is raw memory or hidden prompt content exposed?
- Does Holo still feel wise, balanced, clever, and coherent?
- Where can users get confused?

### 7. HoloBuild

Review after HoloVerify/HoloChat:

- `holo_builder/`
- `holo_builder/ARCHITECTURE.md`
- `holo_builder/builder.py`
- `holo_builder/loop.py`
- `holo_builder/freeze.py`
- `holo_builder/lint.py`
- `holo_builder/policy_bridge.py`
- `holo_builder/qa_attacker.py`
- `holo_builder/projects/vesync_cosori_levoit_copywriter_exercise_001/`
- `tests/test_holobuild_policy_bridge_smoke.py`

Primary questions:

- Does HoloBuild share the enforcement spine where appropriate?
- Are Gov calls real model calls or static prompts?
- Are worker/Gov token costs separately counted?
- Is final output last-turn recency or selected best artifact?

### 8. Public Benchmark / Whitepaper Surface

Review public claim hygiene last:

- `frontend/benchmark.html`
- `frontend/benchmark-v2.html`
- `frontend/benchmark-v3.html`
- `docs/benchmark/BENCHMARK_PAGE_V7_52_DRAFT_2026_07_01.md`
- `docs/benchmark_summary.md`
- `KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF_2026_06_29.md`
- `KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF_2026_06_29.json`

Primary questions:

- Is the public copy understandable to a smart non-specialist?
- Does it explain frozen/hash-locked packets clearly?
- Does it explain immutable traces as audit/compliance/insurance value?
- Does it explain enterprise policies and SOPs concretely?
- Does it avoid universal superiority claims?
- Are limitations clear without undercutting the result?

## Required Phase Sequence

### Phase 1: Read-Only Adversarial Audit

Produce:

- system map;
- ranked risk register;
- confound hypotheses;
- code smells tied to benchmark credibility;
- missing instrumentation list.

No edits.

### Phase 2: Falsification Plan

Propose the smallest decisive test battery for:

- architecture versus model-family effects;
- packet leakage;
- evaluator bias;
- synthetic distribution comfort;
- hidden runtime rescue;
- prompt asymmetry;
- state contamination;
- selective reporting.

Each test must name:

- exact files to inspect or create;
- exact artifacts produced;
- pass/fail condition;
- what conclusion would change.

### Phase 3: Three-Round Adversarial Review

Before implementation, run the plan through Codex GPT-5.5 xhigh via CLI if available.

Ask Codex:

1. What confounds still remain?
2. Where could this plan reward-hack itself?
3. What result would look good but prove little?

Fable must revise after each review.

### Phase 4: Controlled Implementation

Only after the above may Fable orchestrate Codex CLI to:

- add missing instrumentation;
- harden trace integrity;
- fix benchmark fairness issues;
- tighten acceptance tests;
- implement approved refactors.

Fable reviews every patch for:

- correctness;
- benchmark contamination risk;
- acceptance coverage;
- unintended metric inflation.

### Phase 5: UX And Workflow Audit

After engine hardening:

- use browser control to walk through major HoloChat paths;
- write confusion report;
- rank friction;
- propose highest-leverage UX fixes.

### Phase 6: Optional Opportunity Work

Only if time remains:

- automation checklist;
- simple business ideas;
- X-post analysis;
- SaaS ideation;
- useful Fable workflow research.

## Files To Avoid Or Treat Carefully

- `.env`
- `.env.*`
- `venv/`
- `__pycache__/`
- `.pytest_cache/`
- raw provider keys or local secrets
- frozen packet or prompt files except read-only
- lock manifests except read-only
- evidence packages except read-only

## First Deliverable

Fable's first deliverable should be:

`FABLE_READ_ONLY_SYSTEM_MAP_AND_CONFOUND_REGISTER.md`

It must include:

- the five most likely ways the evidence stack could be fooling us;
- where in the repo each risk would be confirmed or falsified;
- the smallest falsification test for each;
- whether the risk threatens public claims, internal engineering confidence, or product reliability;
- whether code changes are needed, or only clearer evidence/reporting.

