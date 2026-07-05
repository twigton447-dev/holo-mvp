# AP OpenAI-W2 Canary Success

Date: 2026-06-29

Classification: `AP_OPENAI_W2_CANARY_READY_FOR_FULL_FAMILY_RUN`

Status: `PASS`

## Scope

- Run folder: `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_20260629T164305Z`
- Family: AP / procurement / vendor-master controls
- Pair: `HV-AP-REP-001`
- Packets: `2`
- Siblings: `A`, `B`
- Expected Holo calls: `10`
- Solo calls: `0`
- Judge calls: `0`
- Commerce/IT calls: `0`

## Lineage

- Packet freeze commit: `de22377be8175d04078ba6c70f1fd35222e9f572`
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- Gov placeholder fix commit: `4ae402f06d47f7e839de1aa4f8c2f68d88cf9a5c`
- External handoff commit / canary run HEAD: `abf76131199123d62773a3417a5c98a79e25ffe8`

The external canary was run outside Codex in an authorized local environment. Codex ingestion performed no provider calls.

## Runtime Summary

| Metric | Value |
| --- | --- |
| Readiness passed | `true` |
| Classification | `AP_OPENAI_W2_CANARY_READY_FOR_FULL_FAMILY_RUN` |
| Provider calls | `10 / 10` |
| Trace rows | `10` |
| Worker calls | `6` |
| Gov calls | `4` |
| Solo calls | `0` |
| Judge calls | `0` |
| Provider failures | `0` |
| Terminal failures | `0` |
| Transport recovered calls | `0` |
| Root failure | `null` |
| Lock validation | `PASS` |
| No-leakage audit | `PASS` |
| Total tokens | `20310` |

Token accounting:

- Input tokens: `15786`
- Output tokens: `3578`
- Total tokens: `20310`

## Packet Results

| Packet | Expected | Final verdict | Final admissible | Final correct | Final selector |
| --- | --- | --- | --- | --- | --- |
| `HV-AP-REP-001-A` | `ALLOW` | `ALLOW` | `true` | `true` | `FINAL_ARTIFACT_ADMISSIBLE` |
| `HV-AP-REP-001-B` | `ESCALATE` | `ESCALATE` | `true` | `true` | `FINAL_ARTIFACT_ADMISSIBLE` |

## Readiness Assertions

| Assertion | Result |
| --- | --- |
| `holo_packets` | `PASS` |
| `holo_pairs` | `PASS` |
| `holo_calls` | `PASS` |
| `unrecovered_provider_failures` | `PASS` |
| `gov_v2_parsed_every_gov_turn` | `PASS` |
| `worker_compact_parsed_every_worker_turn` | `PASS` |
| `no_leakage` | `PASS` |
| `packet_identity_matches_freeze` | `PASS` |
| `both_sibling_final_verdicts_correct` | `PASS` |
| `final_selector_present` | `PASS` |
| `no_solo` | `PASS` |
| `no_judges` | `PASS` |

## Interpretation

The AP OpenAI-W2 one-pair canary passed. The run completed the expected 10-call Holo sequence across both siblings, with Gov v2 parsing on all Gov turns, compact worker parsing on all worker turns, no unrecovered provider failures, no leakage, no solo calls, no judge calls, and both sibling final verdicts correct.

AP is ready for a fresh full 20-pair Holo run, subject to explicit approval. Do not start full AP from this summary alone.
