# D13/D14 Hardened V4 Sibling Freeze

Date: 2026-06-27

Classification: `D13_D14_SIBLING_HARDENED_V4_FREEZE_VALIDATED`

Validation: `FREEZE_VALIDATION_PASS`

Live sibling run status: `NOT_RUN`

## Boundary Decision

Solo hardening is removed.

`SOLO_CONTROL_7` uses `solo_neutral_format_only`. It may receive JSON/markdown body coercion, required section rendering, heading-noise normalization, and overlength trimming only. It must not receive fallback section content, source coverage repair, D13 expansion sentences, GO/STOP normalization, Gov lens, Gov baton, Gov state, Gov ledger, or dependency repair from Gov.

`FULL_HOLO_7_COMPILER_HAIKU_WORKERB` keeps `holo_full_hardened`. It must receive renderer cleanup, source coverage repair when needed, D13 expansions when needed, section 9 GO/STOP normalization when missing, and Gov-preserved dependency visibility.

This restores the intended comparison boundary:

- Solo = strong repeated model plus neutral formatting.
- Holo = multi-worker Gov-orchestrated system plus full hardened compiler.

## Strict V4 Judge Protocol

The next sibling uses split-ledger judging:

- Deterministic ledger: local only, 40 points.
- Structural ledger: local only, 30 points.
- Argument ledger: blind dimension-only LLM judge, 30 points.
- Gov ledger: trace-derived diagnostic ledger, separately reported.

The harness computes totals, winner, and margin. The LLM judge may not compute official totals, choose the winner, see architecture labels, see token counts, or see local deterministic audit material.

## Gov Ledger Requirement

The V4 judge harness must emit `GOV_LEDGER.json` from `TRACE_CALLS.jsonl`.

Required Gov ledger fields include Gov call count, worker call count, Gov input/output/total tokens, Holo worker input/output/total tokens, Gov share of Holo tokens, route verdicts, Gov context requests, one-sentence diagnoses, and failure modes.

This is required so Gov contribution is measured as real orchestration work rather than inferred from artifact quality.

## Current D13 Trace Token Delta

From the completed D13 trace:

- Solo calls: 7.
- Solo tokens: 36,072 input / 26,978 output / 63,050 total.
- Holo calls: 7 total, with 4 worker calls and 3 Gov calls.
- Holo worker tokens: 59,941 input / 8,417 output / 68,358 total.
- Holo Gov tokens: 35,729 input / 8,884 output / 44,613 total.
- Holo total tokens: 95,670 input / 17,301 output / 112,971 total.
- Holo minus Solo: +49,921 total tokens.
- Holo/Solo total multiplier: 1.7918x.
- Gov share of Holo tokens: 39.4907%.

## Frozen Harness Paths

- Freeze root: `/private/tmp/d13_sibling_hardened_v4_freeze_20260627`
- Architecture lock: `/private/tmp/d13_sibling_hardened_v4_freeze_20260627/ARCHITECTURE_LOCK.json`
- Judge protocol: `/private/tmp/d13_sibling_hardened_v4_freeze_20260627/JUDGE_PROTOCOL_V4_STRICT.md`
- Validator: `/private/tmp/d13_sibling_hardened_v4_freeze_20260627/validate_freeze.py`
- V4 judge harness: `/private/tmp/run_d13_v4_split_ledger_judge.py`
- D13 runner: `/private/tmp/run_d13_trap_canary_full_holo_ab_haiku.py`
- Base compiler: `/private/tmp/run_compiler_full_holo_ab_haiku.py`

## Patch IDs

- `SECTION_BODY_HEADING_NOISE_NORMALIZATION_V1_20260627`
- `D13_SECTION9_GOSTOP_NORMALIZATION_V1_20260627`
- `SOLO_NEUTRAL_FORMAT_ONLY_COMPILER_V1_20260627`
- `HOLO_FULL_HARDENED_COMPILER_V1_20260627`

## Next Run Rule

The next live run should be a fresh sibling packet only:

- fresh Solo
- fresh Holo
- same frozen architecture lock
- strict V4 split-ledger judge
- no post-hoc patching of scored artifacts

A single sibling result is signal only. A durable 15% Holo advantage claim requires a hard packet suite, ideally 5-10 sibling packets.
