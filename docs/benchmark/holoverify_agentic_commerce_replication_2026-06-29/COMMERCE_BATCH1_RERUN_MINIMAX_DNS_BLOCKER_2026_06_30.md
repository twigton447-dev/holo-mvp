# Commerce Batch 1 Rerun MiniMax DNS Blocker

Date: 2026-06-30

Classification: `COMMERCE_BATCH1_RERUN_MINIMAX_DNS_BLOCKER`

Status: `BLOCKED_PROVIDER_RELIABILITY`

## Summary

The Commerce Batch 1 rerun is invalid and preserved. It did not fail because of a Holo verdict, packet truth, deterministic gate, final selector, or benchmark seam. It failed because the required MiniMax Gov call could not resolve the provider endpoint after the registered transport retry budget was exhausted.

## Preserved Run

- Run: `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_20260630T223800Z`
- Classification: `COMMERCE_OPENAI_W2_BATCHED_HOLO_BATCH_INVALID_OR_INCOMPLETE`
- Readiness passed: `False`
- Provider calls completed: `27 / 70`
- Worker calls completed: `16`
- Gov calls completed: `11`
- Packet count reached: `6`
- Packet correct before stop: `5`
- Valid pairs before stop: `2`
- No leakage audit: `PASS`
- Lock validation: `PASS`

## Root Failure

- Turn: `HV-ACOM-REP-003-B_G1`
- Packet: `HV-ACOM-REP-003-B`
- Pair: `HV-ACOM-REP-003`
- Call kind: `gov`
- Provider/model: `minimax/MiniMax-M2.5-highspeed`
- Provider call OK: `False`
- Parse OK: `False`
- Error: `TransportFailureAfterRetries: DNS_RESOLUTION_ERROR`
- Transport attempts: `3`
- Transport recovered: `False`
- Transport retry policy: `HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29`

All three MiniMax attempts failed with:

`<urlopen error [Errno 8] nodename nor servname provided, or not known>`

## Interpretation

This is a provider transport blocker, not a benchmark result. The run cannot be counted as Commerce evidence, but it is useful harness evidence: the transport retry policy exhausted the bounded retry budget, failed closed, preserved the trace, and did not continue into solo, judges, fallback, or substitution.

## Next Valid Move

Do not start Batch 2 or Batch 3. Before any new Commerce batch attempt, run the non-benchmark MiniMax health check. Only run a batch if MiniMax returns a clean readiness response with no transport recovery.

