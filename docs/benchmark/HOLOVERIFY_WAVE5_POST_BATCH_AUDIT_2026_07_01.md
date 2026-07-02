# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `21`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `20`
- `completed_packets`: `200`
- `completed_pairs`: `100`
- `expected_provider_calls_for_completed_batches`: `1000`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `8`
- `provider_calls_observed`: `1050`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `100`
- `allow_packets`: `100`
- `completed_batches`: `20`
- `completed_correct_packets`: `200`
- `completed_packets`: `200`
- `completed_pairs`: `100`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `100`
- `escalate_packets`: `100`
- `expected_provider_calls_for_completed_batches`: `1000`
- `guardrail_packets`: `100`
- `input_tokens`: `1741642`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `8`
- `observed_provider_calls_for_completed_batches`: `1000`
- `output_tokens`: `340095`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `100`
- `total_batches`: `28`
- `total_tokens`: `2217087`
- `transport_recovered_call_count`: `1`

## Next Batch

- Batch: `WAVE5_PSRC_HOLO_BATCH_001`
- Family: `HV-PSRC-REP-2026-07-01`
- Approval SHA: `bb5140f3b9c4a7fdbd59a7c057a99c6457e01f3c7f2d9ac428801353787cc6d3`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 bb5140f3b9c4a7fdbd59a7c057a99c6457e01f3c7f2d9ac428801353787cc6d3 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_001 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
