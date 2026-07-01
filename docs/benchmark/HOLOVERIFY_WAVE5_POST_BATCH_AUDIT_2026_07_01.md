# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `14`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `13`
- `completed_packets`: `130`
- `completed_pairs`: `65`
- `expected_provider_calls_for_completed_batches`: `650`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `15`
- `provider_calls_observed`: `700`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `65`
- `allow_packets`: `65`
- `completed_batches`: `13`
- `completed_correct_packets`: `130`
- `completed_packets`: `130`
- `completed_pairs`: `65`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `65`
- `escalate_packets`: `65`
- `expected_provider_calls_for_completed_batches`: `650`
- `guardrail_packets`: `65`
- `input_tokens`: `1132740`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `15`
- `observed_provider_calls_for_completed_batches`: `650`
- `output_tokens`: `220917`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `65`
- `total_batches`: `28`
- `total_tokens`: `1440773`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_002`
- Family: `HV-CLAD-REP-2026-07-01`
- Approval SHA: `96fca2cc0bd42c7df9e444da48711c28737db1b9a5c2dad90d24e20e9a9ab5ad`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 96fca2cc0bd42c7df9e444da48711c28737db1b9a5c2dad90d24e20e9a9ab5ad --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_002 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
