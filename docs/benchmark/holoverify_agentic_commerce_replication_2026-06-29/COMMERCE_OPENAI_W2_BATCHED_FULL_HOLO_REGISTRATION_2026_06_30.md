# Commerce OpenAI-W2 Batched Full-Holo Registration

Date: 2026-06-30

Classification: `COMMERCE_OPENAI_W2_BATCHED_FULL_HOLO_REGISTRATION_NO_PROVIDER`

Status: `REGISTERED_NOT_RUN`

## Purpose

Register a three-batch execution protocol for the Commerce OpenAI-W2 Holo family. The prior full-family attempts showed that a single uninterrupted `200`-call run is fragile to provider/runtime interruption. This registration preserves the same frozen packet bank, same prompts, same roster, same Gov/worker architecture, and same proof standard, while reducing blast radius by running fixed sibling-pair ranges.

This is not a new benchmark result. It is a no-provider protocol registration.

## Frozen Packet Bank

- Family: `HV-ACOM-REP-2026-06-29`
- Domain: Agentic commerce / order execution controls
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- Packet freeze commit: `de22377be8175d04078ba6c70f1fd35222e9f572`
- Packets: `40`
- Sibling pairs: `20`

## Runtime Lineage

- Current branch head at registration: `4abcb17045ca490ec3e52a5578e21028ed211961`
- Batched runner: `docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py`
- Batched runner SHA-256 at registration: `09e7819b788c4cf1be1d1b7b99bd7f0aa69c3a06b857dfdf5a9c34cc751d9482`
- Underlying Commerce wrapper: `docs/benchmark/run_commerce_replication_holoverify_3dna_2026_06_29.py`
- Underlying hardened AP runtime path: `docs/benchmark/run_ap_replication_holoverify_3dna_2026_06_29.py`

## Fixed Roster

| Slot | Provider/model |
| --- | --- |
| W1 | `xai/grok-3-mini` |
| G1 | `minimax/MiniMax-M2.5-highspeed` |
| W2 | `openai/gpt-5.4-mini` |
| G2 | `minimax/MiniMax-M2.5-highspeed` |
| W3 | `minimax/MiniMax-M2.5-highspeed` |

Gov does not choose models. Gov emits control actions only.

## Batch Plan

| Batch | Pair range | Pairs | Packets | Expected calls | Worker calls | Gov calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `batch_1` | `HV-ACOM-REP-001` to `HV-ACOM-REP-007` | 7 | 14 | 70 | 42 | 28 |
| `batch_2` | `HV-ACOM-REP-008` to `HV-ACOM-REP-014` | 7 | 14 | 70 | 42 | 28 |
| `batch_3` | `HV-ACOM-REP-015` to `HV-ACOM-REP-020` | 6 | 12 | 60 | 36 | 24 |

Total family proof requires all three batches:

- `20/20` pairs
- `40/40` packets
- `200/200` provider calls across batches
- `120` worker calls
- `80` Gov calls
- `0` solo calls
- `0` judge calls

## Proof Boundary

Acceptable public-safe wording after all three batches pass:

`Commerce completed as a lock-rooted three-batch Holo family run over the same frozen 40 packets.`

Do not describe the batched result as one uninterrupted `200`-call run.

## Stop Rules

Each batch fails closed if:

- packet identity drifts
- prompt identity drifts
- model roster changes
- fallback/substitution occurs
- provider failure remains unrecovered
- worker compact contract fails
- Gov micro-baton contract fails
- verdict/admissibility fails
- leakage audit fails
- solo or judges run

Failed batches remain preserved and are not resumed. A failed batch may only be rerun as a fresh batch attempt after autopsy and explicit approval.

## Registration Boundary

No providers, Holo live calls, solo calls, or judges were run while creating this registration.
