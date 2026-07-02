# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `26`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `25`
- `completed_packets`: `250`
- `completed_pairs`: `125`
- `expected_provider_calls_for_completed_batches`: `1250`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `3`
- `provider_calls_observed`: `1300`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `125`
- `allow_packets`: `125`
- `completed_batches`: `25`
- `completed_correct_packets`: `250`
- `completed_packets`: `250`
- `completed_pairs`: `125`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `125`
- `escalate_packets`: `125`
- `expected_provider_calls_for_completed_batches`: `1250`
- `guardrail_packets`: `125`
- `input_tokens`: `2180083`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `3`
- `observed_provider_calls_for_completed_batches`: `1250`
- `output_tokens`: `426855`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `125`
- `total_batches`: `28`
- `total_tokens`: `2776575`
- `transport_recovered_call_count`: `1`

## Next Batch

- Batch: `WAVE5_OTSF_HOLO_BATCH_002`
- Family: `HV-OTSF-REP-2026-07-01`
- Approval SHA: `959c8b1ab4d004b91bd1f346661d29302376baba323488c36ad2b0e362982091`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 959c8b1ab4d004b91bd1f346661d29302376baba323488c36ad2b0e362982091 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_002 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
