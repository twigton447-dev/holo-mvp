# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `28`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `27`
- `completed_packets`: `270`
- `completed_pairs`: `135`
- `expected_provider_calls_for_completed_batches`: `1350`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `1`
- `provider_calls_observed`: `1400`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `135`
- `allow_packets`: `135`
- `completed_batches`: `27`
- `completed_correct_packets`: `270`
- `completed_packets`: `270`
- `completed_pairs`: `135`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `135`
- `escalate_packets`: `135`
- `expected_provider_calls_for_completed_batches`: `1350`
- `guardrail_packets`: `135`
- `input_tokens`: `2355662`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `1`
- `observed_provider_calls_for_completed_batches`: `1350`
- `output_tokens`: `460932`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `135`
- `total_batches`: `28`
- `total_tokens`: `2999965`
- `transport_recovered_call_count`: `3`

## Next Batch

- Batch: `WAVE5_OTSF_HOLO_BATCH_004`
- Family: `HV-OTSF-REP-2026-07-01`
- Approval SHA: `c2950e6375a565cebaa753607aa9d3363b7b5a3565bb7678f4b5b5ab57293b07`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 c2950e6375a565cebaa753607aa9d3363b7b5a3565bb7678f4b5b5ab57293b07 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_004 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
