# D11-Lock Holo Score And Proof Ledger

Date: 2026-06-27

Classification: `D11_LOCK_HOLO_SCORE_AND_PROOF_LEDGER`

## Headline

D11-lock Holo has two scored A/B sibling wins and one trace-mechanics proof run.

Clean held-out Gemini judge deltas:

- D13: Holo +9
- D14: Holo +5

## Scoreboard

| case | proof type | deterministic result | argument result | winner | caveat |
|---|---|---|---|---|---|
| D11 | trace mechanics | Holo final admissible; Turn 3 and Turn 7 gate score 40; regression false | no A/B judge in trace folder | Holo trace valid | trace-only, not fresh A/B score |
| D13 | scored A/B | Holo admissible score 39 vs Solo inadmissible score 28 | Gemini 94-85; Codex 106-69 | Holo | local regate added 0 provider calls |
| D14 raw | scored A/B | Holo admissible score 48 vs Solo inadmissible score 34 | clean judge uses corrected compiled artifacts | Holo | posthoc parser repair, 0 provider calls |
| D14 compiled | scored A/B | Holo admissible score 48 vs Solo inadmissible score 38 | Gemini 95-90 | Holo | clean corrected-artifact judge |

## Two-Ledger Scoring Model

The proof standard is deterministic plus argument, not judge preference alone.

### Ledger 1: Deterministic Eligibility

The deterministic ledger decides whether an artifact is admissible for comparison. It checks source coverage, source-ID validity, required sections, word band, trap-specific semantic gates, blocked moves, and action-boundary violations.

If an artifact fails deterministic eligibility, it can still be described for autopsy, but it should not be treated as a clean quality winner.

### Ledger 2: Argument Quality

The argument ledger evaluates the surviving artifact's reasoning quality: source fidelity, trap handling, causal logic, executive usability, structure, tradeoff clarity, and whether the recommendation follows from the evidence.

Argument scores matter only after deterministic eligibility is visible. This keeps an LLM judge from laundering an artifact that is fluent but structurally or semantically inadmissible.

### Current Split Result

| case | deterministic winner | argument winner | official interpretation |
|---|---|---|---|
| D11 | Holo trace valid | not scored as A/B in trace folder | architecture proof only |
| D13 | Holo | Holo | Holo wins both ledgers |
| D14 | Holo | Holo | Holo wins both ledgers after parser repair |

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
5. Clean held-out Gemini judging preferred Holo on the argument ledger in both scored siblings: D13 by 9 points and D14 by 5 points.

## Caveats

- D11 is trace-mechanics proof only from this folder; do not count it as a fresh scored A/B without paired Solo artifacts.
- D13 local regate and D14 parser re-audit added zero provider calls, but they are posthoc local harness repairs and must be labeled that way.
- D14 prepatch 95-0 judge is superseded as official score evidence by the clean corrected-artifact judge of 95-90.
- Gemini is a single held-out judge in these siblings, not consensus. Treat it as strong directional evidence, not final multi-judge consensus.
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
- judge: `/private/tmp/d13_trap_canary_full_holo_ab_haiku_20260627/live_seed20260627_compiler_full_holo_ab_haiku_20260627T204821Z/judge_gemini_v31_dimension_only_d11_lock_001/JUDGE_RESULT_DETERMINISTIC_SCORE_ATTEMPT_001_D11_LOCK.json`
- Codex judgment: `/private/tmp/d13_trap_canary_full_holo_ab_haiku_20260627/live_seed20260627_compiler_full_holo_ab_haiku_20260627T204821Z/CODEX_JUDGMENT_D11_LOCK.json`

### D14 Trade Finance D11-Lock A/B

- trace: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/TRACE_CALLS.jsonl`
- posthoc re-audit: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/posthoc_parser_patch_reaudit_001.json`
- clean corrected judge: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/judge_gemini_d14_corrected_compiled_001/JUDGE_RESULT_D14_CORRECTED_COMPILED_GEMINI_001.json`
- old prepatch judge: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/judge_gemini_d14_d11_lock_001/JUDGE_RESULT.json`
- Holo corrected compiled artifact: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/FULL_HOLO_7_D11_LOCK_D14_HAIKU_WORKERB/compiled_final_artifact.md`
- Solo corrected compiled artifact: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/SOLO_CONTROL_7_D14/compiled_final_artifact.md`
