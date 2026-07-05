# AP OpenAI-W2 Holo Invalid Run Report

Date: 2026-06-29

Run folder:

`docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T114551Z`

## Classification

`INVALID_RUN_GOV_PARSE_FAILURE_BEFORE_FULL_HOLO_FREEZE`

This run is not a valid frozen AP Holo result and is not ready for solo baseline.

## Root Failure

The run stopped on Holo call 167 of expected 200.

Failing turn:

- turn_id: `HV-AP-REP-017-B_G1`
- packet_id: `HV-AP-REP-017-B`
- pair_id: `HV-AP-REP-017`
- call_kind: `gov`
- gov_index: `1`
- provider: `minimax`
- model: `MiniMax-M2.5-highspeed`
- provider_call_ok: `true`
- parse_ok: `false`
- finish_reason: `length`
- error: `ValueError: gov_micro_key_value_parse_failed`
- text: empty

The provider transport did not fail. The Gov call returned a response metadata record, but the output was truncated/empty and failed the required Gov micro-parser contract.

## Trace Status At Stop

- trace rows: 167 / 200 expected
- worker calls logged: 100
- Gov calls logged: 67
- packets seen: 34 / 40
- pairs seen: 17 / 20
- provider_call_ok false: 0
- parse_ok false: 1
- last turn: `HV-AP-REP-017-B_G1`

## Token Accounting Through Failure

Total through invalidation:

- input_tokens: 241,716
- output_tokens: 73,470
- total_tokens: 335,577

By call kind:

| call_kind | calls | input_tokens | output_tokens | total_tokens |
|---|---:|---:|---:|---:|
| worker | 100 | 230,208 | 50,234 | 300,833 |
| gov | 67 | 11,508 | 23,236 | 34,744 |

By model:

| model | calls | input_tokens | output_tokens | total_tokens |
|---|---:|---:|---:|---:|
| xai/grok-3-mini | 34 | 52,187 | 9,121 | 81,699 |
| openai/gpt-5.4-mini | 33 | 80,273 | 11,081 | 91,354 |
| minimax/MiniMax-M2.5-highspeed | 100 | 109,256 | 53,268 | 162,524 |

## Secondary Reporting Defect

After the failing Gov row was preserved, the local wrapper attempted to call `holo_summary(...)` and hit:

`KeyError: 'architecture_lock'`

This is a post-failure reporting defect in the summary path for the OpenAI-W2 variant manifest shape. It is not the benchmark invalidation root cause.

## Actions Not Taken

- no automatic rerun
- no silent repair
- no fallback/substitution
- no solo baseline
- no judges
- no commerce run
- no IT run

## Required Next Decision

This lane needs an explicit next instruction before any further provider calls. A valid next step would be a no-provider runner/reporting patch or a separately approved fresh full AP Holo attempt after the Gov parse/truncation condition is addressed.
