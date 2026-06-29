# AP OpenAI-W2 Provider Timeout Blocker

Date: 2026-06-29

Status: `AP_OPENAI_W2_BLOCKED_BY_PROVIDER_TIMEOUT`

## Preserved Invalid Run

- Run: `run_20260629T132430Z`
- Path: `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T132430Z`
- Stopped at: `8/200` expected Holo calls
- Failing turn: `HV-AP-REP-001-B_W2`
- Packet: `HV-AP-REP-001-B`
- Provider/model: `openai/gpt-5.4-mini`
- Error: `timeout: The read operation timed out`
- Classification: `PROVIDER_FAILURE`
- Trace hash: `524322c7b3f7a5d4369fb2c4e665870fb3270b0244e547dd432dda6bac8ca58a`
- Lock validation: `PASS`
- No-leakage audit: `PASS`
- Readiness assertions: `FAIL`

## Boundary

This blocker is a transport reliability blocker. It is not:

- a Holo verdict failure
- a Gov contract failure
- a deterministic gate failure
- a solo baseline result

Solo was not run. Judges were not run. Commerce and IT replication families were not run.

## Required Policy Before Retry

Before another 200-call AP Holo attempt, the run must be governed by `HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29`.

The policy allows bounded retry only for transport failures and forbids retry for model/content failures such as parse failure, malformed Gov baton, `finish_reason=length` incomplete output, schema/admissibility failure, and deterministic gate failure.

## Current Valid State

- The invalid run remains preserved.
- No retroactive retry may be applied.
- AP OpenAI-W2 remains blocked until a new full run is explicitly approved under the registered retry policy.

