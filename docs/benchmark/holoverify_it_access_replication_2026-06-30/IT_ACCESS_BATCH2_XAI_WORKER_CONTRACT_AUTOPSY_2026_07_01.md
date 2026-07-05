# IT Access Batch 2 XAI Worker Contract Autopsy

Classification: `IT_ACCESS_BATCH2_INVALID_WORKER_CONTRACT_FAILURE`

## Preserved Run

- Run: `holo_live_runs_openai_w2_batched/batch_2/run_20260701T004011Z`
- Batch: `batch_2`
- Expected Holo calls: `70`
- Completed provider calls: `46`
- Worker calls: `28`
- Gov calls: `18`
- Solo calls: `0`
- Judge calls: `0`
- No-leakage audit: `PASS`
- Packet identity: `PASS`

## Root Failure

- Turn: `HV-ITAC-REP-012-B_W1`
- Packet: `HV-ITAC-REP-012-B`
- Pair: `HV-ITAC-REP-012`
- Role: `SOURCE_BOUNDARY_MAPPER`
- Provider/model: `xai/grok-3-mini`
- Provider call OK: `true`
- Finish reason: `stop`
- Error: `ValueError: worker_compact_missing_keys:action_boundary`

## Finding

The worker produced the correct substantive decision direction for the packet: `ESCALATE` with `SOURCE_BOUNDARY_OPEN`. It cited the controlling source IDs and identified the open dependency, but it omitted the required literal compact-contract line:

`action_boundary=...`

The parser correctly failed closed. This is not a transport failure and not a Holo verdict failure. It is a worker output contract failure that prevented the batch from completing, so the batch remains invalid/incomplete and receives no proof credit.

## Patch

The shared worker prompt builder now injects a literal `required_literal_boundary_line` and an `output_key_skeleton` into the worker answer contract. The current-turn command also repeats the exact `action_boundary=` line that must appear immediately after `binding_class=`.

The parser remains strict. Missing `action_boundary=` still fails closed; no malformed worker output is repaired or inferred from prose.

