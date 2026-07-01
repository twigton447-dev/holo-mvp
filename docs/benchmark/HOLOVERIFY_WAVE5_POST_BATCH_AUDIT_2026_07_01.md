# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `16`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `15`
- `completed_packets`: `150`
- `completed_pairs`: `75`
- `expected_provider_calls_for_completed_batches`: `750`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `13`
- `provider_calls_observed`: `800`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `75`
- `allow_packets`: `75`
- `completed_batches`: `15`
- `completed_correct_packets`: `150`
- `completed_packets`: `150`
- `completed_pairs`: `75`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `75`
- `escalate_packets`: `75`
- `expected_provider_calls_for_completed_batches`: `750`
- `guardrail_packets`: `75`
- `input_tokens`: `1307863`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `13`
- `observed_provider_calls_for_completed_batches`: `750`
- `output_tokens`: `255833`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `75`
- `total_batches`: `28`
- `total_tokens`: `1664510`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_004`
- Family: `HV-CLAD-REP-2026-07-01`
- Approval SHA: `226e8c30d064bfa6a12fe59f08fa427b8a53b8ae6373786dbb0a9ab77957e951`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 226e8c30d064bfa6a12fe59f08fa427b8a53b8ae6373786dbb0a9ab77957e951 --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_004 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
