# HoloVerify Solo Failure Factory Rescue Patch-Validation Rollup

Date: 2026-07-03

Status: PATCH_VALIDATION_COMPLETE

## Scope

This rollup compares two runs over the same selected 13 Solo Failure Factory rescue pairs, 26 packets total.

This is patch validation only for `SELECTOR_V3_DEPENDENCY_AWARE_REPAIR_2026_07_03`.

It is not fresh benchmark evidence, not public benchmark evidence, and not an error-rate denominator.

## Frozen Inputs

- Freeze root: `7e99326f6d0af0b41ba88c08bd81b3147c5485a96923152fc1849db699dad9ba`
- Runtime manifest: `20a614b9de95c7cb7953fd70d5d820ccf1135dea2f738edd0ab859b12ae1c346`
- Scoring map hash: `7df42bc33a5278f8f4b8602922f8002b091e2082b3d15c98af822dd3d2cc0113`
- Packet count: 26
- Pair count: 13
- Roster: W1 `xai/grok-3-mini`, G1 `minimax/MiniMax-M2.5-highspeed`, W2 `openai/gpt-5.4-mini`, G2 `minimax/MiniMax-M2.5-highspeed`, W3 `minimax/MiniMax-M2.5-highspeed`

## Results

| Run | Selector | Calls | Packets Correct | Pairs Correct | Provider Failures | Token Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `run_20260703T210421Z` | `SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03` | 130 | 19/26 | 7/13 | 0 | 105,302 |
| `run_20260703T214031Z` | `SELECTOR_V3_DEPENDENCY_AWARE_REPAIR_2026_07_03` | 130 | 26/26 | 13/13 | 0 | 111,007 |

## V2 Failure Set

V2 missed seven packets:

- `HVSF-FACTORY-009-B`: truth `ESCALATE`, final `ALLOW`
- `HVSF-FACTORY-010-A`: truth `ALLOW`, final `ESCALATE`
- `HVSF-FACTORY-010-B`: truth `ESCALATE`, final `ALLOW`
- `HVSF-FACTORY2-005-B`: truth `ESCALATE`, final `ALLOW`
- `HVSF-FACTORY3-008-B`: truth `ESCALATE`, final `ALLOW`
- `HVSF-FACTORY4-008-B`: truth `ESCALATE`, final `ALLOW`
- `HVSF-FACTORY4-010-B`: truth `ESCALATE`, final `ALLOW`

## V3 Patch Effect

V3 cleared all seven V2 misses in the patch-validation replay.

The patch changed the selector and deterministic dependency layer, not the packet bank:

- `short_final_answer` became warning-only when other required fields are valid.
- Source-derived deterministic checks were added for balance, tolerance, time-window, and stale-authorization seams.
- Gov baton content includes a dependency ledger for the next worker.
- Selector ordering now includes `deterministic_clean` and `verdict_corroboration_count`.

## Trace Binding

V3 run directory:

`docs/benchmark/holoverify_solo_failure_factory_holo_rescue_2026_07_03/live_runs/run_20260703T214031Z`

V3 trace hashes:

- `TRACE_CALLS.jsonl`: `42b4d3c76400b6835c0b3c15356d25e4ddb41822612d245086904706142ba4ac`
- `TRACE_PROVIDER_CALLS.jsonl`: `476229b628df9691f39fd8163cd3226a8e3cc812f474061a31365642405f591f`
- Runtime results: `1002ae2e4f61bad27481792a437d8a7c59f9313587eb3807f0f86ed6723dc66e`
- Live summary: `511b9b7f7564281e17620a72612fd56afd2b700033cb9cfefb8f8e0ea87ae35b`

## Claim Boundary

Allowed internal statement:

The V3 selector/dependency patch corrected the observed V2 rescue failures on the same 13-pair replay set under trace-bound, post-freeze scoring.

Not allowed:

- Public benchmark claim.
- Error-rate claim.
- General model-superiority claim.
- Fresh evidence claim from this rerun.
- Claim that V3 is generally robust outside this patch-validation set.
