# Completion Audit

Status: `OBJECTIVE_PARTIAL_EXTERNAL_JUDGES_BLOCKED`

Audit date: 2026-06-29

## Objective

Run the Holo full traces and Solo one-shots for a total of 10 packets, have judges examine traces to ensure answers are correct, use KNEW as the only passing label, freeze and hash-lock everything, then produce benchmark analysis showing Solo action-boundary unreliability.

## Requirement Audit

| Requirement | Evidence | Status |
| --- | --- | --- |
| 10 locked packets exist | Packet freeze lock validates `pair_count=5`, `packet_count=10` | COMPLETE |
| Holo full traces exist | `benchmark_results.json` references frozen full-Holo bundle with `50` provider calls | COMPLETE |
| Solo one-shots ran for all 10 packets | `solo_one_shot_results.json` reports `provider_calls=10`, `classification=SOLO_ONE_SHOT_10_COMPLETE` | COMPLETE |
| KNEW is the only passing label | `BENCHMARK_ANALYSIS.md`, `LOCAL_CODEX_TRACE_JUDGMENT.md`, and runner schema state `KNEW` only; `LUCKY`, `WRONG`, and `CONFUSED` fail | COMPLETE |
| Everything local is frozen and hash-locked | Packet freeze validation passes; run lock validation passes | COMPLETE |
| Benchmark analysis exists | `BENCHMARK_ANALYSIS.md` exists and interprets Solo as unreliable at the action boundary, not always wrong | COMPLETE |
| Local trace judgment exists | `LOCAL_CODEX_TRACE_JUDGMENT.md` and `.json` examine all 20 artifacts | COMPLETE_LOCAL_NON_EXTERNAL |
| External independent judges examine traces | External judge packet is ready, but provider transfer was rejected by approval review because it sends frozen source packets, Solo outputs, Holo selected artifacts, and trace summaries to external providers | BLOCKED_PENDING_EXPLICIT_APPROVAL |

## Current Local Result

| Lane | Local KNEW | Non-pass labels |
| --- | ---: | --- |
| Solo one-shot MiniMax | 7/10 | `WRONG`, `CONFUSED`, `LUCKY` |
| Full HoloVerify | 10/10 | none |

The current local evidence supports the action-boundary reliability claim: Solo is not always wrong, but it is unreliable at the decisive source boundary across matched ALLOW/ESCALATE siblings.

## Remaining Gate

The only missing requirement is external independent judge execution.

The judge-only continuation is ready and must not rerun Solo or Holo. The required approval text is stored in `EXTERNAL_JUDGE_READINESS.md`.

Until that approval is given and external judge outputs are saved and re-locked, the benchmark status remains:

`FROZEN_HASH_LOCKED_PENDING_EXTERNAL_JUDGES`
