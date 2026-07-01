# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `10`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `10`
- `completed_packets`: `100`
- `completed_pairs`: `50`
- `expected_provider_calls_for_completed_batches`: `500`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `18`
- `provider_calls_observed`: `500`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `50`
- `allow_packets`: `50`
- `completed_batches`: `10`
- `completed_correct_packets`: `100`
- `completed_packets`: `100`
- `completed_pairs`: `50`
- `escalate_correct`: `50`
- `escalate_packets`: `50`
- `expected_provider_calls_for_completed_batches`: `500`
- `guardrail_packets`: `50`
- `input_tokens`: `871699`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `18`
- `observed_provider_calls_for_completed_batches`: `500`
- `output_tokens`: `169874`
- `target_packets`: `50`
- `total_batches`: `28`
- `total_tokens`: `1108745`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_LREG_HOLO_BATCH_003`
- Family: `HV-LREG-REP-2026-07-01`
- Approval SHA: `a76861940b67ecadc6737b56d680890b9c83e9b07a9d7b09ad3c41ce0e8b1189`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 a76861940b67ecadc6737b56d680890b9c83e9b07a9d7b09ad3c41ce0e8b1189 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_003 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
