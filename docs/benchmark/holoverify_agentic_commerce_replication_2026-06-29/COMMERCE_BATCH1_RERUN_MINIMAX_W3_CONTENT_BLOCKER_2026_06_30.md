# Commerce Batch 1 Rerun MiniMax W3 Content Blocker

Date: 2026-06-30

Classification: `COMMERCE_BATCH1_RERUN_MINIMAX_W3_CONTENT_BLOCKER`

Status: `BLOCKED_MODEL_OUTPUT_CONTRACT`

## Summary

The Commerce Batch 1 rerun after the MiniMax DNS health gate is invalid and preserved. This was not a transport failure. MiniMax returned a provider response for the final compiler turn, but the response was entirely hidden-thinking text and never produced a visible compact worker artifact.

## Preserved Run

- Run: `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T230945Z`
- Classification: `COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE`
- Readiness passed: `False`
- Provider calls completed: `25 / 70`
- Worker calls completed: `15`
- Gov calls completed: `10`
- Packet count reached: `5`
- Packet correct before stop: `4`
- Valid pairs before stop: `2`
- Invalidation reason: `WORKER_CONTRACT_OR_TRUNCATION_FAILURE`

## Root Failure

- Turn: `HV-ACOM-REP-003-A_W3`
- Packet: `HV-ACOM-REP-003-A`
- Pair: `HV-ACOM-REP-003`
- Call kind: `worker`
- Worker role: `FINAL_COMPILER`
- Provider/model: `minimax/MiniMax-M2.5-highspeed`
- Provider call OK: `True`
- Transport attempts: `1`
- Transport recovered: `False`
- Finish reason: `length`
- Input tokens: `3109`
- Output tokens: `6000`
- Total tokens: `9109`
- Parse OK: `False`
- Error: `ValueError: worker_finish_reason_length_empty_text`

The raw model output started with `<think>` and ended with `</think>`. After the registered thinking filter, visible worker text was empty. The runner correctly failed closed instead of inferring a verdict from hidden reasoning.

## Interpretation

MiniMax passed basic provider health, but it did not prove readiness for the Worker 3 final-compiler contract. The next gate must test that specific contract outside the benchmark before frozen Commerce prompts are sent again.

## Patch

Add a non-benchmark MiniMax worker-contract smoke:

- harmless fixture only
- no packet text
- no benchmark prompt text
- no source IDs except `SRC-FIXTURE-CTL` and `SRC-FIXTURE-BND`
- require visible stripped output to start with `worker_role=FINAL_COMPILER`
- require compact worker parse
- require deterministic fixture gate pass
- reject `finish_reason=length`
- reject transport recovery

Do not rerun Commerce Batch 1 until both MiniMax health and MiniMax worker-contract smoke pass.
