# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `18`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `17`
- `completed_packets`: `170`
- `completed_pairs`: `85`
- `expected_provider_calls_for_completed_batches`: `850`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `11`
- `provider_calls_observed`: `900`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `85`
- `allow_packets`: `85`
- `completed_batches`: `17`
- `completed_correct_packets`: `170`
- `completed_packets`: `170`
- `completed_pairs`: `85`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `85`
- `escalate_packets`: `85`
- `expected_provider_calls_for_completed_batches`: `850`
- `guardrail_packets`: `85`
- `input_tokens`: `1482343`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `11`
- `observed_provider_calls_for_completed_batches`: `850`
- `output_tokens`: `289556`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `85`
- `total_batches`: `28`
- `total_tokens`: `1887286`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_SECO_HOLO_BATCH_002`
- Family: `HV-SECO-REP-2026-07-01`
- Approval SHA: `398bd98cc7b9892c8272fea8627886122c25ca573ac5eb1ab80cd330af0f1657`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 398bd98cc7b9892c8272fea8627886122c25ca573ac5eb1ab80cd330af0f1657 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_002 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
