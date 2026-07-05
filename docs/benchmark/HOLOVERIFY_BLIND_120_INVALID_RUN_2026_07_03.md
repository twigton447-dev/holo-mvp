# HoloVerify Blind 120 Invalid Run Report

Status: `INVALID_RUN_PRESERVED`
Date: 2026-07-03

## Classification

`HOLOVERIFY_BLIND_120_INVALID_GOV_CONTENT_CONTRACT_FAILURE`

This is not a Holo verdict failure, not a scoring result, not a solo comparison, and not a public benchmark result.

## Run

- Run folder: `docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T020428Z`
- Wrapper commit: `d454be111addb8db64f488aab4baba148c8608c8`
- Expected provider calls: `600`
- Observed provider calls: `117`
- Trace frozen before scoring: `true`
- Post-hoc scoring run: `false`
- Solo run: `false`
- Judge run: `false`
- Substitution: `false`

## Failure

- Failing call: `117_G1`
- Slot: `G1`
- Role: `gov`
- Provider: `minimax`
- Model: `MiniMax-M2.5-highspeed`
- Error: `G1_empty_text`
- Finish reason: `length`
- Provider transport failure: `false`
- Transport recovered: `false`
- Retry attempted for content failure: `false`

## Root Cause

MiniMax returned only hidden thinking text and hit `finish_reason=length`. The runtime thinking filter stripped the hidden thinking, leaving an empty visible output. Because Gov output must be compact key=value baton text, the contract validator correctly failed closed with `G1_empty_text`.

The model appeared to understand the requested three-line baton inside hidden reasoning, but it did not emit the required visible baton before length cutoff. That makes this a Gov runtime output-contract/truncation failure.

## Accounting

- Raw provider output files: `117`
- `TRACE_PROVIDER_CALLS.jsonl` rows: `117`
- Input tokens before failure: `62,773`
- Output tokens before failure: `32,479`
- Total tokens before failure: `108,011`
- Transport recoveries: `0`

Slot counts before failure:

- `W1`: `24`
- `G1`: `24`
- `W2`: `23`
- `G2`: `23`
- `W3`: `23`

## Hashes

- `blind_canary_live_summary.json`: `e84d2674c49dac970a60126b0e63cd1f623a01d6388279bdfe0787fd5375e68a`
- `TRACE_PROVIDER_CALLS.jsonl`: `a7aca5a8e3941fd2ba88061ce67d1a951884f12a731a7780d7005507cb67fc80`

## Required Next Step

Stop. Do not score, do not run solo, do not run judges, and do not rerun automatically.

Any fresh live attempt requires a no-provider hardening patch, tests, Fable review if requested, and a new explicit provider approval sentence.
