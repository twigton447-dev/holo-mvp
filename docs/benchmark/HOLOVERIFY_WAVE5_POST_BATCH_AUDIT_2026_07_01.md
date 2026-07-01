# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `1`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `1`
- `completed_packets`: `10`
- `completed_pairs`: `5`
- `expected_provider_calls_for_completed_batches`: `50`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `27`
- `provider_calls_observed`: `50`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `5`
- `allow_packets`: `5`
- `completed_batches`: `1`
- `completed_correct_packets`: `10`
- `completed_packets`: `10`
- `completed_pairs`: `5`
- `escalate_correct`: `5`
- `escalate_packets`: `5`
- `expected_provider_calls_for_completed_batches`: `50`
- `guardrail_packets`: `5`
- `input_tokens`: `88483`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `27`
- `observed_provider_calls_for_completed_batches`: `50`
- `output_tokens`: `18038`
- `target_packets`: `5`
- `total_batches`: `28`
- `total_tokens`: `113234`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_MEDX_HOLO_BATCH_002`
- Family: `HV-MEDX-REP-2026-07-01`
- Approval SHA: `83b68cbc2c3775ed28d78e4de0045768d17ef9ab3d8de8a6f92cdb295329e0b1`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 83b68cbc2c3775ed28d78e4de0045768d17ef9ab3d8de8a6f92cdb295329e0b1 --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_002 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
