# Blind Canary Invalidity Audit

Run: `run_20260703T004112Z`

Classification: `INVALID_RUN_CONTENT_CONTRACT_FAILURE_W3_LENGTH_EMPTY_TEXT`

This run is preserved as invalid. Do not treat it as a Holo verdict failure, a false positive, a false negative, or a public benchmark-rate data point.

## Scope

- Packet indices: `19-20`
- Expected provider calls: `10`
- Observed provider calls: `10`
- Solo calls: `0`
- Judge calls: `0`
- Substitutions: `0`
- Trace frozen before scoring: `true`

## Failure

- Failing call: `10`
- Slot: `W3`
- Role: `worker`
- Provider: `minimax`
- Model: `MiniMax-M2.5-highspeed`
- Finish reason: `length`
- Error: `W3_empty_text`
- Max output tokens: `2048`
- Output tokens: `2048`
- Transport recovered: `false`
- Transport retry failures: `[]`

The provider returned content, but the raw output began with a hidden-thinking block and reached the output limit. The thinking-filter produced empty visible text. The worker compact contract therefore failed closed as `W3_empty_text`.

## Interpretation

This is a content/contract/truncation failure in the final compiler slot. It is not evidence that the final verdict was wrong because no valid final artifact was produced for the full batch.

The correct next engineering action is to preserve this invalid trace, audit the W3 contract/truncation behavior, and decide whether to patch the final compiler path before any fresh attempt. Do not silently rerun this batch as if it never happened.
