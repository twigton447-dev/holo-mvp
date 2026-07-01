# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `15`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `14`
- `completed_packets`: `140`
- `completed_pairs`: `70`
- `expected_provider_calls_for_completed_batches`: `700`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `14`
- `provider_calls_observed`: `750`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `70`
- `allow_packets`: `70`
- `completed_batches`: `14`
- `completed_correct_packets`: `140`
- `completed_packets`: `140`
- `completed_pairs`: `70`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `70`
- `escalate_packets`: `70`
- `expected_provider_calls_for_completed_batches`: `700`
- `guardrail_packets`: `70`
- `input_tokens`: `1220248`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `14`
- `observed_provider_calls_for_completed_batches`: `700`
- `output_tokens`: `238195`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `70`
- `total_batches`: `28`
- `total_tokens`: `1552474`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_003`
- Family: `HV-CLAD-REP-2026-07-01`
- Approval SHA: `9d730b21da1013a3664299342ef1e6e338c2bd0b8c45c7f46ec6cbeb660d10be`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 9d730b21da1013a3664299342ef1e6e338c2bd0b8c45c7f46ec6cbeb660d10be --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_003 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
