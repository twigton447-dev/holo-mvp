# D11-Lock Holo Score And Proof Ledger

Date: 2026-06-27

Classification: `D11_LOCK_HOLO_SCORE_AND_PROOF_LEDGER`

## Headline

D11-lock Holo has four official full-gated A/B wins, one trace-mechanics proof run, and one open regression seed.

Full gated 100-point judge deltas are required for official quality claims. Earlier narrower judge outputs remain diagnostic until superseded by a full gated judge.

Current full gated judge status:

- D10: official full gated Holo win, 95-71.
- D11_CYBER: official full gated Holo win, 96-94.
- D13: official full gated Holo win, 94-69.
- D14: official full gated Holo win, 94-69.
- D12: no official judgment; both artifacts failed deterministic word band.

## Scoreboard

| case | proof type | deterministic result | full judge result | winner | caveat |
|---|---|---|---|---|---|
| D11 | trace mechanics | Holo final admissible; Turn 3 and Turn 7 gate score 40; regression false | no A/B judge in trace folder | Holo trace valid | trace-only, not fresh A/B score |
| D10 | scored A/B | Holo admissible score 50 vs Solo inadmissible score 42 | full gated Gemini 95-71 | Holo | patched canary, not part of a single uninterrupted 45-call run |
| D11_CYBER | scored A/B | Holo admissible score 50 vs Solo admissible score 50 | full gated Gemini 96-94 | Holo | narrow margin; both artifacts cleared deterministic gate |
| D12 | regression seed | Holo inadmissible score 42 vs Solo inadmissible score 42 | no official judge; zero eligible artifacts | none | word-band control-loop failure; not a Holo or Solo win |
| D13 | scored A/B | Holo admissible score 39 vs Solo inadmissible score 28 | full gated Gemini 94-69 | Holo | local regate added 0 provider calls |
| D14 raw | scored A/B | Holo admissible score 48 vs Solo inadmissible score 34 | compiled official full gated Gemini 94-69 | Holo | raw autopsy plus parser repair, 0 provider calls |
| D14 compiled | scored A/B | Holo admissible score 48 vs Solo inadmissible score 38 | full gated Gemini 94-69 | Holo | clean corrected artifacts judged through canonical validator |

## Full Judging Rule

There can never be an official judgment without a full gated 100-point rubric that includes deterministic, epistemic, structural, and argument scoring. Any judge output missing one of those four ledgers is diagnostic only. Any judge that does not receive the local deterministic audit is also diagnostic only.

The four ledgers are:

1. Deterministic compliance: 25 points.
2. Epistemic/source reasoning: 25 points.
3. Structural/executive usability: 25 points.
4. Argument quality: 25 points.

Total score is the sum of all four ledgers. The full gated judge must report all four dimension scores separately, the 100-point total, score caps, critical failures, and the reason for the winner. The local deterministic audit controls official eligibility.

Executable guardrail: `benchmark_full_gated_judge.py` validates whether a saved judge output is official or diagnostic-only. The matching regression tests are in `tests/test_full_gated_judge_validator.py`. This prevents a narrow rubric, missing deterministic audit, noncanonical artifact schema, or ineligible winner from being counted as an official benchmark judgment.

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
| D10 | Holo | Holo | Holo | Holo | Holo wins official full gated judgment 95-71 |
| D11_CYBER | tie | tie | Holo | Holo | Holo wins official full gated judgment 96-94 |
| D12 | none | not judged | not judged | not judged | no official winner; both artifacts inadmissible |
| D13 | Holo | Holo | Holo | Holo | Holo wins official full gated judgment 94-69 |
| D14 | Holo | Holo | Holo | Holo | Holo wins official full gated judgment 94-69 |

## Token Proof

| case | total calls | solo tokens | holo worker tokens | gov tokens | holo total | gov share | provider failures |
|---|---:|---:|---:|---:|---:|---:|---|
| D11 | 7 | n/a | 49,902 | 34,904 | 84,806 | 41.16% | none |
| D10 | 15 | 58,518 | 67,775 | 42,932 | 110,707 | 38.78% | none |
| D11_CYBER + D12 | 29 | 114,625 | 118,007 | 75,478 | 193,485 | 39.01% | none |
| D13 | 14 | 52,227 | 67,175 | 46,808 | 113,983 | 41.07% | none |
| D14 | 14 | 69,956 | 80,266 | 50,909 | 131,175 | 38.81% | none |

## What Counts As Proof

These are the proof claims supported by the artifacts:

1. Gov is not static prompting in these runs. D11, D13, and D14 each contain three real Gov provider calls in the Holo lane.
2. Gov is not too lean. Gov consumed about 39-41 percent of Holo tokens in these runs.
3. The D11-lock mechanism is visible in traces: early artifact creation, local gate registry, Gov lock state, final selection, and regression prevention.
4. In D10, D13, and D14, Holo wins the deterministic ledger before quality interpretation.
5. In D11_CYBER, both artifacts clear the deterministic ledger and Holo wins narrowly on structure and argument.
6. D10, D11_CYBER, D13, and D14 have official full gated 100-point Holo wins.
7. D12 is not proof of a Holo loss; it is proof that Gov diagnosis needs deterministic actuation for hard form gates.

## Caveats

- D11 is trace-mechanics proof only from this folder; do not count it as a fresh scored A/B without paired Solo artifacts.
- D13 local regate and D14 parser re-audit added zero provider calls, but they are posthoc local harness repairs and must be labeled that way.
- D14 prepatch 95-0 judge is superseded as official score evidence by later full-gated attempts.
- D14 diagnostic noncanonical full-gated output favored Holo 95-78, but the local validator rejected it as official because the judge did not return the canonical schema. It is superseded by the later schema-backed official 94-69 result.
- D10 was a patched canary after an invalid prepatch attempt. It is official for D10, but the D10-D12 set should be disclosed as split across a D10 canary and a D11-D12 continuation, not as one uninterrupted 45-call suite.
- D12 produced no official winner because both artifacts failed word band. The Holo trace shows Gov repeatedly diagnosed the defect correctly, but the worker oscillated under/over the band.
- Gemini is a single held-out judge in these siblings, not consensus. Treat it as strong directional evidence unless paired with additional held-out judges.
- Any judge that does not report deterministic, epistemic, structural, and argument scores out of 100 is diagnostic only.
- Any judge that does not receive the local deterministic audit is diagnostic only.
- The next proof upgrade is a locked parser in the canonical runner plus a 5- or 10-packet sibling suite with deterministic-first scoring and two held-out judges.
- Before rerunning D12, add deterministic actuation for word-band control rather than weakening the gate.

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

### D10-D12 Mini-Suite And D12 Regression

- autopsy: `docs/benchmark/D11_LOCK_D10_D12_AUTOPSY_2026-06-27.md`
- D10 canary run: `/private/tmp/d11_lock_5packet_suite_live_20260627/d11_lock_5packet_d10_d12_live_20260627T231320Z`
- D10 official judge: `/private/tmp/d11_lock_5packet_suite_live_20260627/d11_lock_5packet_d10_d12_live_20260627T231320Z/D10_INFRASTRUCTURE_CONFIGURATION_CHANGE/judge_gemini_full_gated_100pt_001/JUDGE_RESULT_FULL_GATED_100PT.json`
- D11-D12 continuation run: `/private/tmp/d11_lock_5packet_suite_live_20260627/d11_lock_5packet_d10_d12_live_20260627T232331Z`
- D11_CYBER official judge: `/private/tmp/d11_lock_5packet_suite_live_20260627/d11_lock_5packet_d10_d12_live_20260627T232331Z/D11_CYBER_INCIDENT_CONTRACT_NOTICE_EMERGENCY_CLOUD_ACCESS/judge_gemini_full_gated_100pt_001/JUDGE_RESULT_FULL_GATED_100PT.json`
- D12 local deterministic audit: `/private/tmp/d11_lock_5packet_suite_live_20260627/d11_lock_5packet_d10_d12_live_20260627T232331Z/D12_FUND_NAV_REDEMPTION_CASH_RELEASE/local_deterministic_audit.json`

### D14 Trade Finance D11-Lock A/B

- trace: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/TRACE_CALLS.jsonl`
- posthoc re-audit: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/posthoc_parser_patch_reaudit_001.json`
- full gated judge summary: `/private/tmp/d11_lock_full_gated_100pt_judges_20260627/FULL_GATED_100PT_JUDGE_SUMMARY.json`
- official full gated judge: `/private/tmp/d11_lock_full_gated_100pt_judges_20260627/D14_FULL_GATED_100PT_GEMINI_001/JUDGE_RESULT_FULL_GATED_100PT.json`
- official full gated validation: `/private/tmp/d11_lock_full_gated_100pt_judges_20260627/D14_FULL_GATED_100PT_GEMINI_001/CANONICAL_VALIDATION.json`
- diagnostic noncanonical full-gated judge: `/private/tmp/d11_lock_full_gated_100pt_judges_20260627/D14_FULL_GATED_100PT_GEMINI_PLAINJSON_001/JUDGE_RESULT_FULL_GATED_100PT.json`
- clean corrected judge: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/judge_gemini_d14_corrected_compiled_001/JUDGE_RESULT_D14_CORRECTED_COMPILED_GEMINI_001.json`
- old prepatch judge: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/judge_gemini_d14_d11_lock_001/JUDGE_RESULT.json`
- Holo corrected compiled artifact: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/FULL_HOLO_7_D11_LOCK_D14_HAIKU_WORKERB/compiled_final_artifact.md`
- Solo corrected compiled artifact: `/private/tmp/d14_d11_lock_full_holo_ab_haiku_20260627/live_d14_d11_lock_20260627T213134Z/posthoc_parser_patch_reaudit_001/SOLO_CONTROL_7_D14/compiled_final_artifact.md`
