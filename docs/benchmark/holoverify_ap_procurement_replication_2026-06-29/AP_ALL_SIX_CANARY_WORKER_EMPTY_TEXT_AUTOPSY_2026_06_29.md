# AP All-Six-Collapse Canary Worker Empty Text Autopsy

Date: 2026-06-29

Run folder: `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260629T191023Z`

Classification: `AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_INVALID_OR_INCOMPLETE`

## Finding

The AP OpenAI-W2 all-six-collapse Holo canary stopped fail-closed at `26/60` expected provider calls because Worker 1 returned exactly empty text on packet `HV-AP-REP-013-B`.

This was not a Holo verdict failure, not a Gov baton failure, and not a transport failure under the registered transport retry policy.

## Failing Turn

- Turn: `HV-AP-REP-013-B_W1`
- Pair: `HV-AP-REP-013`
- Packet: `HV-AP-REP-013-B`
- Sibling: `B`
- Call kind: `worker`
- Worker index: `1`
- Worker role: `SOURCE_BOUNDARY_MAPPER`
- Provider: `xai`
- Model: `grok-3-mini`
- Provider call OK: `true`
- Parse OK: `false`
- Admissible: `false`
- Finish reason: `""`
- Text: `""`
- Input tokens: `1678`
- Output tokens: `0`
- Total tokens: `1704`
- Error: `ValueError: worker_empty_text`
- Transport attempt count: `1`
- Transport recovered: `false`
- Transport retry failures: `[]`

## Preserved Run State

- Provider calls completed: `26/60`
- Worker calls completed: `16/36`
- Gov calls completed: `10/24`
- Solo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- No leakage: `PASS`
- Lock validation: `PASS`
- Benchmark laws: `PASS`

## Root Cause Classification

Root cause: `WORKER_EXACT_EMPTY_TEXT_ZERO_OUTPUT_TOKENS`

The provider returned a response object with no worker text and zero output tokens. Because the transport call returned successfully, the transport retry policy did not apply. Because no worker content existed, the worker compact parser correctly failed closed with `worker_empty_text`.

## Protocol Decision

The preserved invalid run remains invalid and must not be repaired retroactively.

A prospective, narrow retry policy is registered as `HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29`. It permits bounded retry only for exact-empty worker responses with `0` output tokens, using the identical packet, prompt, model, provider, settings, role, turn lineage, and max token budget.

Malformed content, markdown-wrapped content, wrong verdicts, Gov failures, deterministic gate failures, and schema/admissibility failures remain non-retryable.
