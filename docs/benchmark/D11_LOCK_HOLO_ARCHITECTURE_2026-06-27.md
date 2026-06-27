# D11-Lock Holo Architecture

Date: 2026-06-27

## Status

This architecture is the current working Holo pattern for hard action-boundary benchmarks.

It was validated on the D13 trap canary sibling run:

- run root: `/private/tmp/d13_trap_canary_full_holo_ab_haiku_20260627/live_seed20260627_compiler_full_holo_ab_haiku_20260627T204821Z`
- patch id: `D11_EARLY_FULL_ARTIFACT_GOV_LOCK_V1_20260627`
- deterministic re-gate: Holo admissible, Solo excluded
- Gemini non-participant judge: Holo 94, Solo 85
- Codex judgment: Holo wins

## Core Rule

Holo wins when Gov is a stateful adversarial control layer, not a note generator.

Gov must:

1. Force an early real artifact.
2. Maintain a dependency and blocker ledger.
3. Detect when a worker creates a strong candidate.
4. Lock the best candidate against regression.
5. Route later workers to repair named defects only.
6. Prevent final-turn reinvention.

## Required Run Shape

The 7-call Holo lane keeps this sequence:

1. Worker A: initial analysis / first candidate pressure.
2. Gov: adjudicate, diagnose gaps, force full candidate if none exists.
3. Worker B: full candidate artifact, not notes.
4. Gov: lock if admissible; otherwise name precise repair.
5. Worker A: adversarial repair / challenge, not rewrite.
6. Gov: preserve or repair named defects only.
7. Worker B: final artifact; copy locked artifact unless Gov named a concrete source-grounded defect.

## Non-Negotiable Invariants

- Turn 3 must attempt a complete 900-1,300 word artifact with all required sections.
- If no admissible artifact exists, Gov must route the next worker to create one.
- If an admissible artifact exists, Gov must preserve it as pinned.
- Later workers may revise only named source-grounded defects.
- Later workers may not replace an admissible artifact with metadata, outline, rubric, or a fresh-from-scratch rewrite.
- Final worker must not reinvent if the locked artifact is admissible and no material defect is named.

## Gov Baton Requirements

Every Gov baton must carry:

- `route_verdict`
- `must_preserve`
- `must_repair`
- `blocked_moves`
- `dependency_ledger`
- `d11_lock_state`
- `next_worker_baton`

The lock state must include:

- best artifact id
- whether the best artifact is admissible
- best turn
- word count
- gate score
- failures, if any

## What D13 Proved

The D13 run showed the mechanism clearly:

- Turn 3 became a real artifact instead of notes, but was too long.
- Gov diagnosed overlength and semantic risk.
- Turn 5 became shorter but under word band.
- Gov diagnosed undershoot and vendor-master boundary ambiguity.
- Turn 7 landed in band and passed the corrected semantic gate.

The decisive Solo failure was source-logic confusion: Solo treated the narrow containment path as requiring the broad approval chain. Holo preserved the distinction between narrow containment, customer holding update, escalation, and blocked vendor-master/payment-reroute action.

## D14 Sibling Confirmation

D14 tested the same D11-lock architecture on a trade-finance LC payment-release trap:

- run root: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z`
- patch id: `D11_LOCK_D14_IRREVERSIBLE_RELEASE_BOUNDARY_V1_20260627`
- generation calls: 14 total, with 7 Solo calls and 7 Holo calls
- Holo Gov calls: 3 real provider calls
- posthoc parser patch audit: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/posthoc_parser_patch_reaudit_001.md`
- deterministic posthoc result after parser repair: Holo admissible, Solo inadmissible
- full gated judge status: official D14 full-gated judging is blocked by repeated Gemini HTTP 503; a noncanonical diagnostic full-gated output favors Holo 95-78 but is not official

Important D14 autopsy:

- The original live report was contaminated by a parser/compiler bug, not by Holo architecture failure.
- Solo's real final artifact was in `final_artifact`, but the extractor grabbed the wrapper field `draft_or_final_artifact: "final"`.
- Holo's real final artifact was in `main_body`, but the compiler ignored it and rendered fallback sections.
- After local parser repair with no provider calls, Holo's raw artifact was admissible at 1,239 words and its compiled artifact was admissible at 1,019 words.
- Solo remained inadmissible after correct extraction.

Harness rule: artifact extraction must prefer real artifact body fields before wrapper/status fields. Required body fields include `artifact_markdown`, `final_artifact`, and `main_body`. Do not score fallback renderer output when a real artifact body exists.

Judge rule: no official judge result counts unless it is a full gated 100-point judgment with deterministic, epistemic, structural, and argument scores, and unless the judge receives the local deterministic audit as controlling eligibility evidence.

Executable guardrail: `benchmark_full_gated_judge.py` is the canonical local validator for this rule. If that validator rejects a judge output, the output is diagnostic only even if it contains useful qualitative remarks.

## Current Weakness To Harden Next

The architecture works, but worker word-budget control is still noisy.

Next hardening target:

- stricter word-budget bands per worker turn
- cleaner final renderer
- no escaped newline artifacts
- no dangling numbered-heading fragments
- local gate should avoid false positives on negative/conditional phrases
- parser/compiler must extract actual artifact bodies, not wrapper labels or metadata
- local gates should normalize clear source aliases like `S1` to the canonical frozen source ID when the mapping is unambiguous

## Do Not Regress

Do not reduce Gov to static instructions.

Do not let workers see only the latest baton without cumulative state.

Do not let final worker rewrite from scratch after a prior admissible artifact exists.

Do not score Holo architecture without separating:

- worker tokens
- Gov tokens
- deterministic gates
- judge scores
- local/compiler repairs

The architecture name to remember is:

`D11-lock Holo`
