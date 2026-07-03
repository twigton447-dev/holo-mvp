# HoloVerify Blind 120 Batch Execution Lock

Status: `NO_PROVIDER_BATCH_LOCK`
Date: 2026-07-03

## Purpose

Replace the single 600-call blind-120 execution shape with twelve pre-registered 10-packet batches.

This does not change the frozen 120-packet bank, runtime manifest, scoring map, model roster, scoring protocol, or public-claim boundary. It only changes live execution from one brittle 600-call run into twelve auditable 50-call batches.

## Reason

The first full blind-120 run failed closed at call `117_G1` because MiniMax Gov returned hidden thinking only, hit `finish_reason=length`, and emitted no visible three-line baton. That invalid run is preserved at:

`docs/benchmark/holoverify_blind_120_live_runs_2026_07_03/run_20260703T020428Z`

The failure was a runtime Gov content-contract/truncation failure. It was not a verdict failure, not a transport failure, not a scoring result, and not a solo comparison.

## Frozen Inputs

- Freeze root: `63cc81e5fd5d9dcc56e054ec5b55e5981d1a3b1d88b90e61e4cf68bb9c5c33ba`
- Runtime manifest hash: `c3a2bbe2ff2b4b4a3d2e4da0112489b3ba19d41147c5eff45cc0f36c5ca940a1`
- Scoring map hash: `b5f3c219c473aa2821540aca7cf84e5fc8d2441f977f69d9df226aad550ed166`
- Packets: `120`
- Batch count: `12`
- Batch size: `10 packets`
- Calls per batch: `50`
- Total calls if all batches complete: `600`

## Roster

- W1: `xai/grok-3-mini`
- G1: `minimax/MiniMax-M2.5-highspeed`
- W2: `openai/gpt-5.4-mini`
- G2: `minimax/MiniMax-M2.5-highspeed`
- W3: `minimax/MiniMax-M2.5-highspeed`

## Batch Registry

| Batch | Packet indices | Expected calls |
|---:|---:|---:|
| 1 | 1-10 | 50 |
| 2 | 11-20 | 50 |
| 3 | 21-30 | 50 |
| 4 | 31-40 | 50 |
| 5 | 41-50 | 50 |
| 6 | 51-60 | 50 |
| 7 | 61-70 | 50 |
| 8 | 71-80 | 50 |
| 9 | 81-90 | 50 |
| 10 | 91-100 | 50 |
| 11 | 101-110 | 50 |
| 12 | 111-120 | 50 |

## Execution Rules

1. Run only one batch after an exact provider approval sentence for that batch.
2. If a batch fails, preserve it as invalid.
3. Do not automatically rerun a failed batch.
4. Do not score failed or incomplete batches.
5. Do not run solo until Holo batch evidence is frozen and scored post-freeze.
6. Do not run judges.
7. Do not substitute models.
8. Do not alter packets, runtime payloads, scoring map, or truth labels.
9. Aggregate only clean, trace-complete, post-freeze-scored batches.
10. Invalid batches remain visible in the final lineage and are not silently discarded.

## Gov Hardening Applied Before Batch Execution

- Gov max output budget increased from `512` to `1024`.
- Gov prompt shortened to copy-only baton mode.
- Gov no longer receives verbose gate summary text in the live prompt; selected baton lines remain truth-free.
- Hidden-thinking-only Gov output still fails closed.
- Content failures are still not retried.

## Approval Sentence Generation

Use the wrapper to print the exact approval sentence for each batch:

```bash
python3 -B docs/benchmark/run_holoverify_blind_120_live_2026_07_03.py --print-approval --batch-number 1
```

Then run the approved batch:

```bash
set -a; source .env; set +a
python3 -B docs/benchmark/run_holoverify_blind_120_live_2026_07_03.py --run-live --batch-number 1 --approval-statement '<exact sentence printed above>'
```

## Claim Boundary

This batch lock does not produce any Holo result by itself. It is only an execution-control document.

No public benchmark update is allowed until:

- valid Holo batches are frozen,
- post-freeze scoring is complete,
- solo one-shots are run on the same frozen packet bank,
- comparison memo is built,
- randomized ablation subset is complete or formally deferred,
- and public claim language is reviewed.
