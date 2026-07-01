# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `7`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `7`
- `completed_packets`: `70`
- `completed_pairs`: `35`
- `expected_provider_calls_for_completed_batches`: `350`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `21`
- `provider_calls_observed`: `350`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `35`
- `allow_packets`: `35`
- `completed_batches`: `7`
- `completed_correct_packets`: `70`
- `completed_packets`: `70`
- `completed_pairs`: `35`
- `escalate_correct`: `35`
- `escalate_packets`: `35`
- `expected_provider_calls_for_completed_batches`: `350`
- `guardrail_packets`: `35`
- `input_tokens`: `611124`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `21`
- `observed_provider_calls_for_completed_batches`: `350`
- `output_tokens`: `120486`
- `target_packets`: `35`
- `total_batches`: `28`
- `total_tokens`: `778496`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_TRES_HOLO_BATCH_004`
- Family: `HV-TRES-REP-2026-07-01`
- Approval SHA: `8e1e796543a36a4334b45a2dd9787ab2087a669901c1a92263bf3157cf52f594`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 8e1e796543a36a4334b45a2dd9787ab2087a669901c1a92263bf3157cf52f594 --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_004 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
