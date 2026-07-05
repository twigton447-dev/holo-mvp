# Fable HoloEngine Pressure-Test Handoff

Status: `READY_FOR_FABLE_READ_ONLY_REVIEW`

Date: `2026-07-02`

Purpose: give Fable a precise, high-leverage map of the HoloEngine ecosystem so it can pressure-test the architecture, benchmark evidence, product UX, and code quality without mutating evidence or reward-hacking metrics.

## Prime Directive

Assume the HoloVerify/HoloEngine claims may be misleading, overfit, leaky, brittle, or overclaimed. Find the strongest alternative explanations. Then design the smallest falsification tests that would distinguish true architecture improvement from model-family effects, packet leakage, evaluator bias, synthetic distribution comfort, prompt advantage, or deterministic-gate overfitting.

Fable should be ruthless, specific, and evidence-bound.

## Operating Rules

- Start read-only.
- Do not edit frozen benchmark packets, prompts, traces, lock manifests, evidence packages, or public result files.
- Do not run providers unless Taylor explicitly approves the exact scope.
- Do not optimize toward a benchmark number without an independent review gate.
- Do not hide failures, parse failures, invalid runs, provider failures, or ambiguous rows.
- Separate product hardening from benchmark evidence.
- Separate official locked evidence from diagnostic, canary, smoke, or invalid traces.
- Any code changes should be planned by Fable but implemented through Codex CLI.
- Fable may perform code review and acceptance review on Codex-produced changes.
- Fable should treat every benchmark improvement proposal as suspect until it passes a leakage/reward-hacking review.

## Current Fresh Context

The latest randomized no-Gov ablation run completed:

- Run: `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/live_runs/run_20260702T205951Z`
- Provider calls: `144/144`
- Gov calls: `0`
- Holo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- Parse failures: `2`
- Strict-admissible correct: `13/24`
- Tokens: `240,092 total`

This run is part of the Architecture Isolation Ladder, not a HoloVerify run.

## The Strategic Frame

Use this sentence as the moral center:

> HoloVerify's result is strong; the ablations are there to test what actually caused it.

Use this exact statistical language:

> On this frozen 614-packet corpus, HoloVerify observed 0 false positives and 0 false negatives. The one-sided 95% upper confidence bound is approximately 0.97% per side.

Do not convert that sentence into "zero errors" without the frozen-corpus scope and confidence bound.

## Highest-Priority Folders And Files

### 1. Current HoloChat Product Surface

Review these first for live-product behavior, routing, memory, dashboard metadata, and whether Holo feels like Holo:

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

Key questions:

- Is HoloChat using the correct current governed-shadow architecture?
- Does normal chat remain intact when shadow is off?
- Are runtime dashboard labels honest and understandable?
- Are raw prompts, secret context, HoloBrain contents, or provider error bodies hidden from the UI?
- Does the system preserve the personality/continuity Taylor expects?
- Where can a user get confused, scared, or misled?

### 2. HoloVerify Evidence And Benchmark Core

Review these to audit the claim stack, denominator math, leakage controls, and ablation logic:

- `docs/benchmark/HOLOVERIFY_STATISTICAL_APPENDIX_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_STATISTICAL_APPENDIX_2026_07_01.json`
- `docs/benchmark/compiled_holoverify_holobuild_metrics_2026_07_01/`
- `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/`
- `docs/benchmark/HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_WAVE2_WAVE3_WAVE4_COMBINED_EVIDENCE_MEMO_2026_07_01.json`
- `docs/benchmark/HOLOVERIFY_WAVE5_COMPLETED_BATCH_EVIDENCE_2026_07_01.md`
- `docs/benchmark/HOLOVERIFY_WAVE5_COMPLETED_BATCH_EVIDENCE_2026_07_01.json`
- `docs/benchmark/holoverify_20pair_3dna_2026-06-29/`
- `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/`
- `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/`
- `docs/benchmark/holoverify_it_access_replication_2026-06-30/`
- `docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29/`
- `docs/benchmark/holoverify_replication_packet_freeze_3families_wave2_2026-07-01/`
- `docs/benchmark/holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/`
- `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/`

Key questions:

- Does the `614` denominator reconcile from packet-level evidence?
- Are `ALLOW` and `ESCALATE` denominators both `307`?
- Are FPR/FNR definitions clear and defensible?
- Are invalid, diagnostic, and official evidence lanes separated?
- Is the Architecture Isolation Ladder valid, or does any rung receive a prompt advantage?
- Are prompt hashes and generated provider-prompt hashes frozen for every rung?
- Are the ablations proving architecture, or merely showing prompt/style fragility?

### 3. HoloVerify/HoloGov Runtime And Enforcement

Review these for actual enforcement mechanisms:

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
- `docs/benchmark/build_randomized_corpus_balanced_ablation_sample_2026_07_02.py`
- `tests/test_holo_surface_architecture_invariants.py`
- `tests/test_holoverify_governed_decision_smoke.py`
- `tests/test_benchmark_form_actuator.py`
- `tests/test_kita_11arch_ablation_reprise.py`
- `tests/test_kita_randomized_corpus_balanced_ablation.py`

Key questions:

- Where exactly are deterministic gates enforced?
- Can Gov call something ready when gates fail?
- Is the final selector monotonic and auditable?
- Are transport retries limited to transport failures only?
- Are content failures, parse failures, verdict failures, and malformed Gov batons fail-closed?
- Does any benchmark runner silently fallback, repair, or substitute models?

### 4. HoloBuild

Review HoloBuild as the second major governed architecture:

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

Key questions:

- Does HoloBuild have the same enforcement spine as HoloVerify where appropriate?
- Are Gov calls real API calls, static prompts, or local deterministic transforms?
- Are traces token-accounted separately for Gov and workers?
- Are final artifacts selected by a trustworthy mechanism or merely last-turn recency?

### 5. Public Benchmark / Whitepaper Surface

Review public narrative and claim hygiene:

- `frontend/benchmark.html`
- `frontend/benchmark-v2.html`
- `frontend/benchmark-v3.html`
- `docs/benchmark/BENCHMARK_PAGE_V7_52_DRAFT_2026_07_01.md`
- `docs/benchmark_summary.md`
- `KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF_2026_06_29.md`
- `KIT_C_HOLOVERIFY_PUBLIC_EVIDENCE_BRIEF_2026_06_29.json`

Key questions:

- Is the public copy Paul Graham understandable?
- Does it explain frozen/hash-locked packets clearly?
- Does it explain immutable traces as audit/insurance/compliance value?
- Does it explain enterprise policies and SOP integration without sounding magic?
- Does it avoid universal superiority claims?
- Does it make limitations obvious without weakening the central result?

## Files/Folders To Avoid Or Treat Carefully

- `.env`
- `.env.*`
- `venv/`
- `__pycache__/`
- `.pytest_cache/`
- raw provider keys or local secrets
- frozen packet or prompt files unless read-only
- lock manifests unless read-only
- evidence packages unless read-only

## Fable Mission 1: Misleading-Result Pressure Test

Prompt:

```text
Assume the HoloVerify result is misleading or untrue. Give me the strongest alternative explanations for a 614-packet frozen action-boundary benchmark with 0 observed false positives and 0 observed false negatives. Then design the smallest set of falsification tests that would distinguish true architecture improvement from model-family effects, packet leakage, evaluator bias, prompt advantage, deterministic-gate overfitting, synthetic distribution comfort, or reporting selection effects.

Rules:
- Be ruthless and specific.
- Use repo-backed evidence only.
- Separate official evidence from diagnostic or invalid runs.
- Do not propose changing benchmark packets to improve metrics.
- Do not reward-hack the benchmark.
- Every proposed falsification test must name: exact files to inspect, expected artifact outputs, pass/fail condition, and what conclusion would change.
```

Deliverable:

- `FABLE_HOLOVERIFY_MISLEADING_RESULT_PRESSURE_TEST.md`
- Include top 10 alternative explanations.
- Include smallest falsification test suite.
- Include "what would make me stop claiming architecture advantage."

## Fable Mission 2: Architecture Isolation Ladder Review

Prompt:

```text
Review the Architecture Isolation Ladder strategy and current ablation artifacts. Determine whether the ladder fairly isolates solo one-shot, no-Gov multi-call architectures, and Full HoloVerify.

Focus on:
- whether each rung receives frozen/versioned prompts;
- whether model rosters are identical where claimed;
- whether call budgets are comparable or clearly disclosed;
- whether no-Gov architectures are disadvantaged by prompt shape;
- whether the decision criterion is too weak, too strong, or gameable;
- whether the one-glance matrix would make the result legible.

Return a red-team report, not marketing copy.
```

Primary files:

- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/ARCHITECTURE_ISOLATION_LADDER_STRATEGY_LOCK_2026_07_02.md`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/randomized_corpus_balanced_sample_20260702/`
- `docs/benchmark/kita_11arch_ablation_reprise_2026-07-02/cross_domain_3pair_hard_modelmix_rerun_20260702/`

Deliverable:

- `FABLE_ARCHITECTURE_ISOLATION_LADDER_REVIEW.md`

## Fable Mission 3: HoloChat Product/UX Walkthrough

Prompt:

```text
Walk through the major HoloChat user paths using browser control where available. Identify where users can get confused, where the runtime dashboard labels are unclear, and where the product fails to feel like a coherent Holo intelligence rather than a generic chatbot.

Do not change code. Produce a UX confusion report with exact screens, user expectations, observed behavior, severity, and recommended fixes.
```

Deliverable:

- `FABLE_HOLOCHAT_UX_CONFUSION_REPORT.md`

## Fable Mission 4: Codebase Review Since Fable Ban Date

The exact Fable ban date must be provided by Taylor before this mission is final. Use placeholder:

`FABLE_BAN_DATE=<Taylor to fill in>`

Prompt:

```text
Review all code changed after FABLE_BAN_DATE. Look for bugs, dead code, brittle abstractions, missing tests, confusing state boundaries, leaky benchmark logic, provider failure hazards, and opportunities to simplify.

Do not refactor directly. Produce a ranked review:
- P0 correctness/security issues
- P1 benchmark/evidence integrity issues
- P2 product UX/runtime clarity issues
- P3 cleanup/refactor opportunities

For every proposed code change, include exact file paths, acceptance tests, and whether Codex CLI should implement it.
```

Deliverable:

- `FABLE_POST_BAN_CODE_REVIEW.md`

## Fable Mission 5: Automation And Business Ideation

This is useful but lower priority than evidence/product hardening.

Prompt:

```text
Given Taylor's current HoloEngine assets, benchmark evidence, HoloChat product, HoloVerify architecture, and available AI-agent workflows, identify practical automations and small business experiments that could generate first-dollar revenue without distracting from the core HoloEngine proof.

Do not invent facts. Tie each idea to existing assets in the repo or public Holo materials. Rank by fastest path to revenue, implementation difficulty, credibility, and strategic alignment.
```

Deliverable:

- `FABLE_FIRST_DOLLAR_AND_AUTOMATION_IDEAS.md`

## Two-Day Fable Operating Plan

### Day 1 Morning: Read-Only Reality Map

1. Read this handoff.
2. Inspect priority folders.
3. Produce a one-page architecture map.
4. Identify the 10 highest-risk claims or code paths.

### Day 1 Afternoon: Adversarial Benchmark Review

1. Run Mission 1.
2. Run Mission 2.
3. Produce falsification test proposals.
4. Do not mutate evidence.

### Day 1 Evening: Codex Review Loop

1. Fable writes a plan.
2. Fable asks Codex GPT-5.5 xhigh via CLI for three adversarial reviews of the plan.
3. Fable revises the plan after each review.
4. No coding begins until the plan has a pass/fail acceptance checklist.

### Day 2 Morning: Product And UX Review

1. Run HoloChat UX walkthrough.
2. Review runtime dashboard labels.
3. Identify onboarding confusion and trust gaps.
4. Propose fixes.

### Day 2 Afternoon: Implementation Orchestration

1. Fable selects 1-3 highest-leverage changes.
2. Codex CLI implements.
3. Fable performs acceptance review.
4. Independent agent or Taylor approves benchmark-affecting changes before merge.

## Independent Approval Gate

Any change that could improve measured Type I or Type II error must pass this gate:

- Identify whether it changes model prompt, packet content, deterministic gate, parser, final selector, scoring, sample selection, or public claim language.
- Prove it does not edit frozen benchmark evidence.
- Prove it does not use answer-key leakage.
- Prove it does not reward-hack the benchmark.
- Run a before/after regression on locked packets.
- Get independent review before counting new results.

## Recommended First Question For Fable

```text
Before touching code, tell me the five most likely ways this HoloEngine evidence stack could be fooling us, and exactly where in the repo you would look to confirm or falsify each one.
```

