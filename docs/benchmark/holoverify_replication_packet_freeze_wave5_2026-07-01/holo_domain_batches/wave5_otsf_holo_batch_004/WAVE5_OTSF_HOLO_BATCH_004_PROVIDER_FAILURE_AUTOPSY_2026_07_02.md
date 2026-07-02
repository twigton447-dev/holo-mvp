# Wave5 OTSF Batch004 Provider Failure Autopsy

Status: `INVALID_RUN_PROVIDER_FAILURE`

This is not a Holo verdict failure, not a Gov failure, and not a deterministic gate failure. The run failed closed because xAI returned `HTTP_429` for the required W1 worker call after the transport retry budget was exhausted.

## Run

- Batch: `WAVE5_OTSF_HOLO_BATCH_004`
- Family: `HV-OTSF-REP-2026-07-01`
- Run: `run_20260702T040420Z`
- Run path: `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_otsf_holo_batch_004/live_runs/run_20260702T040420Z`
- Classification: `WAVE5_OTSF_HOLO_BATCH_004_INVALID_OR_INCOMPLETE`
- Invalidation reason: `PROVIDER_FAILURE`
- Readiness passed: `false`

## Failure Point

- Failing turn: `HV-OTSF-REP-020-B_W1`
- Packet: `HV-OTSF-REP-020-B`
- Call kind: `worker`
- Provider: `xai`
- Model: `grok-3-mini`
- Error: `TransportFailureAfterRetries: HTTP_429`
- Transport attempts: `3`
- Transport recovered: `false`

## Accounting

- Expected provider calls: `50`
- Completed trace calls: `46`
- Worker calls completed: `28`
- Gov calls completed: `18`
- Judge calls: `0`

## Audit Notes

- No provider calls were made during this autopsy.
- No judges were run.
- No Holo rerun was started.
- No packet, prompt, truth, roster, or trace files were edited.
- No-leakage audit for the invalid run: `PASS`
- The invalid run must remain preserved and must not be counted as clean Wave5 evidence.

## Correct Next Control

Stop for autopsy before continuing. If continuing is approved, the valid move is a fresh rerun of `WAVE5_OTSF_HOLO_BATCH_004` using the same frozen packet bank, same approval packet, same model roster, and same no-fallback rules. Do not resume from call 46 and do not edit packet or prompt contents.
