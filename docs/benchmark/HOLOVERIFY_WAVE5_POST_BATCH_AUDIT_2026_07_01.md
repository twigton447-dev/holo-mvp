# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `8`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `8`
- `completed_packets`: `80`
- `completed_pairs`: `40`
- `expected_provider_calls_for_completed_batches`: `400`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `20`
- `provider_calls_observed`: `400`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `40`
- `allow_packets`: `40`
- `completed_batches`: `8`
- `completed_correct_packets`: `80`
- `completed_packets`: `80`
- `completed_pairs`: `40`
- `escalate_correct`: `40`
- `escalate_packets`: `40`
- `expected_provider_calls_for_completed_batches`: `400`
- `guardrail_packets`: `40`
- `input_tokens`: `697186`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `20`
- `observed_provider_calls_for_completed_batches`: `400`
- `output_tokens`: `136961`
- `target_packets`: `40`
- `total_batches`: `28`
- `total_tokens`: `888140`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_LREG_HOLO_BATCH_001`
- Family: `HV-LREG-REP-2026-07-01`
- Approval SHA: `1e9186de923375b99c1b7c10db36270e0adde0a7bd903d35c1af4a8736af4e90`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 1e9186de923375b99c1b7c10db36270e0adde0a7bd903d35c1af4a8736af4e90 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_001 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
