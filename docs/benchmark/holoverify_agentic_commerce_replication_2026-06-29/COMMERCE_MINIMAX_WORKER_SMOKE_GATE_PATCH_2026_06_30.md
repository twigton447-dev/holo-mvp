# Commerce MiniMax Worker Smoke Gate Patch

Date: 2026-06-30

Classification: `COMMERCE_MINIMAX_WORKER_SMOKE_GATE_PATCH`

Status: `PATCH_REGISTERED_NO_BENCHMARK_PROVIDER_CALLS`

## Trigger

Taylor ran the non-benchmark MiniMax worker-contract smoke after MiniMax health passed. The smoke used no Commerce packet content and produced:

- Provider call OK: `True`
- Transport attempts: `1`
- Finish reason: `stop`
- Parse OK: `True`
- Visible text starts with `worker_role=FINAL_COMPILER`: `True`
- Raw text starts with `<think>`: `True`
- Deterministic fixture gate failed only on `word_band_final_answer:11`

## Root Cause

The smoke gate was over-strict in two ways:

1. It required the raw provider text to start with `worker_role=FINAL_COMPILER`, even though the registered runner strips provider thinking blocks before parsing.
2. The fixture final answer was too short for the deterministic worker gate.

The original live Batch 1 failure remains valid: that failure had `finish_reason=length` and empty visible worker text after the thinking filter. The smoke patch does not make that failure pass.

## Patch

The worker smoke now requires:

- visible stripped text starts with `worker_role=FINAL_COMPILER`
- compact worker parse passes
- deterministic fixture gate passes
- finish reason is not `length`
- transport attempts equal `1`
- transport recovered is `False`

The fixture final answer is expanded so the deterministic gate tests worker-contract readiness instead of failing on a too-short fixture sentence.

