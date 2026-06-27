# D11-Lock Holo Score And Proof Ledger

Date: 2026-06-27

Classification: `D11_LOCK_HOLO_SCORE_AND_PROOF_LEDGER`

## Headline

D11-lock Holo has two scored A/B sibling wins and one trace-mechanics proof run.

Full gated 100-point judge deltas are required for official quality claims. Earlier narrower judge outputs remain diagnostic until superseded by a full gated judge.

Current full gated judge status:

- D13: official full gated Holo win, 94-69.
- D14: official full gated judge blocked by repeated Gemini HTTP 503. Diagnostic noncanonical full-gated output favors Holo 95-78, but it is not official.

## Scoreboard

| case | proof type | deterministic result | full judge result | winner | caveat |
|---|---|---|---|---|---|
| D11 | trace mechanics | Holo final admissible; Turn 3 and Turn 7 gate score 40; regression false | no A/B judge in trace folder | Holo trace valid | trace-only, not fresh A/B score |
| D13 | scored A/B | Holo admissible score 39 vs Solo inadmissible score 28 | full gated Gemini 94-69 | Holo | local regate added 0 provider calls |
| D14 raw | scored A/B | Holo admissible score 48 vs Solo inadmissible score 34 | official full gated blocked; diagnostic noncanonical 95-78 | Holo deterministic | posthoc parser repair, 0 provider calls |
| D14 compiled | scored A/B | Holo admissible score 48 vs Solo inadmissible score 38 | official full gated blocked; diagnostic noncanonical 95-78 | Holo deterministic | clean corrected artifacts available |

## Full Judging Rule

There can never be an official judgment without a full gated 100-point rubric that includes deterministic, epistemic, structural, and argument scoring. Any judge output missing one of those four ledgers is diagnostic only. Any judge that does not receive the local deterministic audit is also diagnostic only.

The four ledgers are:

1. Deterministic compliance: 25 points.
2. Epistemic/source reasoning: 25 points.
3. Structural/executive usability: 25 points.
4. Argument quality: 25 points.

Total score is the sum of all four ledgers. The full gated judge must report all four dimension scores separately, the 100-point total, score caps, critical failures, and the reason for the winner. The local deterministic audit controls official eligibility.

### Ledger 1: Deterministic Compliance

Deterministic compliance checks source coverage, source-ID validity, required sections, word band, trap-specific semantic gates, blocked moves, and action-boundary violations.

If an artifact fails deterministic compliance, it can still be described for autopsy, but it should not be treated as a clean quality winner.

### Ledger 2: Epistemic / Source Reasoning

Epistemic scoring checks evidence hierarchy, uncertainty handling, missing dependencies, stale or weak source treatment, conflict handling, and overclaim prevention.

### Ledger 3: Structural / Executive Usability

Structural scoring checks whether the artifact is usable as a decision brief: required sections, readable organization, bottom-line clarity, stop/go triggers, sequencing, and concise formatting.

### Ledger 4: Argument Quality

Argument scoring evaluates whether the recommendation follows from the evidence, handles counterarguments and traps, preserves causal logic, balances risks, and makes the action boundary explicit.

Argument scores matter only after deterministic compliance is visible. This keeps an LLM judge from laundering an artifact that is fluent but structurally or semantically inadmissible.

### Current Split Result

| case | deterministic winner | epistemic winner | structural winner | argument winner | official interpretation |
|---|---|---|---|---|---|
| D11 | Holo trace valid | not scored as A/B | not scored as A/B | not scored as A/B | architecture proof only |
| D13 | Holo | Holo | Holo | Holo | Holo wins official full gated judgment 94-69 |
| D14 | Holo | diagnostic Holo | diagnostic Holo | diagnostic Holo | Holo deterministic win; official full gated judgment blocked by provider 503 |

## Token Proof

| case | total calls | solo tokens | holo worker tokens | gov tokens | holo total | gov share | provider failures |
|---|---:|---:|---:|---:|---:|---:|---|
| D11 | 7 | n/a | 49,902 | 34,904 | 84,806 | 41.16% | none |
| D13 | 14 | 52,227 | 67,175 | 46,808 | 113,983 | 41.07% | none |
| D14 | 14 | 69,956 | 80,266 | 50,909 | 131,175 | 38.81% | none |

## What Counts As Proof

These are the proof claims supported by the artifacts:

1. Gov is not static prompting in these runs. D11, D13, and D14 each contain three real Gov provider calls in the Holo lane.
2. Gov is not too lean. Gov consumed about 39-41 percent of Holo tokens in these runs.
3. The D11-lock mechanism is visible in traces: early artifact creation, local gate registry, Gov lock state, final selection, and regression prevention.
4. In D13 and D14, Holo wins the deterministic ledger before quality interpretation.
5. D13 has an official full gated 100-point Holo win. D14 has deterministic Holo win plus diagnostic full-gated support, but official D14 full-gated judging is blocked by provider 503 until rerun succeeds.

## Caveats

- D11 is trace-mechanics proof only from this folder; do not count it as a fresh scored A/B without paired Solo artifacts.
- D13 local regate and D14 parser re-audit added zero provider calls, but they are posthoc local harness repairs and must be labeled that way.
- D14 prepatch 95-0 judge is superseded as official score evidence by later full-gated attempts.
- D14 diagnostic noncanonical full-gated output favored Holo 95-78, but the local validator rejected it as official because the judge did not return the canonical schema.
- Gemini is a single held-out judge in these siblings, not consensus. Treat it as strong directional evidence unless paired with additional held-out judges.
- Any judge that does not report deterministic, epistemic, structural, and argument scores out of 100 is diagnostic only.
- Any judge that does not receive the local deterministic audit is diagnostic only.
- The next proof upgrade is a locked parser in the canonical runner plus a 5- or 10-packet sibling suite with deterministic-first scoring and two held-out judges.

## Key Artifacts

### D11 Full Holo Trace Proof

- trace: `/private/tmp/d11_full_holo_traces_only_20260627/TRACE_CALLS.jsonl`
- final selection: `/private/tmp/d11_full_holo_traces_only_20260627/FINAL_SELECTION.json`
- registry: `/private/tmp/d11_full_holo_traces_only_20260627/FINAL_FULL_HOLO_REGISTRY.json`
- readme: `/private/tmp/d11_full_holo_traces_only_20260627/README.md`

### D13 Trap Canary D11-Lock A/B

- trace: `/private/tmp/d13_trap_canary_full_holo_ab_haiku_20260627/live_seed20260627_compiler_full_holo_ab_haiku_20260627T204821Z/TRACE_CALLS.jsonl`
- local regate: `/private/tmp/d13_trap_canary_full_holo_ab_haiku_20260627/live_seed20260627_compiler_full_holo_ab_haiku_20260627T204821Z/local_regate_after_d11_lock_gate_patch.json`
- official full gated judge: `/private/tmp/d11_lock_full_gated_100pt_judges_20260627/D13_FULL_GATED_100PT_GEMINI_001/JUDGE_RESULT_FULL_GATED_100PT.json`
- judge: `/private/tmp/d13_trap_canary_full_holo_ab_haiku_20260627/live_seed20260627_compiler_full_holo_ab_haiku_20260627T204821Z/judge_gemini_v31_dimension_only_d11_lock_001/JUDGE_RESULT_DETERMINISTIC_SCORE_ATTEMPT_001_D11_LOCK.json`
- Codex judgment: `/private/tmp/d13_trap_canary_full_holo_ab_haiku_20260627/live_seed20260627_compiler_full_holo_ab_haiku_20260627T204821Z/CODEX_JUDGMENT_D11_LOCK.json`

### D14 Trade Finance D11-Lock A/B

- trace: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/TRACE_CALLS.jsonl`
- posthoc re-audit: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/posthoc_parser_patch_reaudit_001.json`
- full gated judge summary: `/private/tmp/d11_lock_full_gated_100pt_judges_20260627/FULL_GATED_100PT_JUDGE_SUMMARY.json`
- diagnostic noncanonical full-gated judge: `/private/tmp/d11_lock_full_gated_100pt_judges_20260627/D14_FULL_GATED_100PT_GEMINI_PLAINJSON_001/JUDGE_RESULT_FULL_GATED_100PT.json`
- clean corrected judge: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/judge_gemini_d14_corrected_compiled_001/JUDGE_RESULT_D14_CORRECTED_COMPILED_GEMINI_001.json`
- old prepatch judge: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/judge_gemini_d14_d11_lock_001/JUDGE_RESULT.json`
- Holo corrected compiled artifact: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/FULL_HOLO_7_D11_LOCK_D14_HAIKU_WORKERB/compiled_final_artifact.md`
- Solo corrected compiled artifact: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/SOLO_CONTROL_7_D14/compiled_final_artifact.md`
