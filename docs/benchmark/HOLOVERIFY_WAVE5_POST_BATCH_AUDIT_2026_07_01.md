# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `25`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `24`
- `completed_packets`: `240`
- `completed_pairs`: `120`
- `expected_provider_calls_for_completed_batches`: `1200`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `4`
- `provider_calls_observed`: `1250`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `120`
- `allow_packets`: `120`
- `completed_batches`: `24`
- `completed_correct_packets`: `240`
- `completed_packets`: `240`
- `completed_pairs`: `120`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `120`
- `escalate_packets`: `120`
- `expected_provider_calls_for_completed_batches`: `1200`
- `guardrail_packets`: `120`
- `input_tokens`: `2090928`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `4`
- `observed_provider_calls_for_completed_batches`: `1200`
- `output_tokens`: `409470`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `120`
- `total_batches`: `28`
- `total_tokens`: `2663047`
- `transport_recovered_call_count`: `1`

## Next Batch

- Batch: `WAVE5_OTSF_HOLO_BATCH_001`
- Family: `HV-OTSF-REP-2026-07-01`
- Approval SHA: `e147a28332e16e01a1d780039b30a6315a95df4a0345b1fbaca8d28b4258f788`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 e147a28332e16e01a1d780039b30a6315a95df4a0345b1fbaca8d28b4258f788 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_001 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
