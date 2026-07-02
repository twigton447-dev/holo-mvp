# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `23`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `22`
- `completed_packets`: `220`
- `completed_pairs`: `110`
- `expected_provider_calls_for_completed_batches`: `1100`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `6`
- `provider_calls_observed`: `1150`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `110`
- `allow_packets`: `110`
- `completed_batches`: `22`
- `completed_correct_packets`: `220`
- `completed_packets`: `220`
- `completed_pairs`: `110`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `110`
- `escalate_packets`: `110`
- `expected_provider_calls_for_completed_batches`: `1100`
- `guardrail_packets`: `110`
- `input_tokens`: `1915932`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `6`
- `observed_provider_calls_for_completed_batches`: `1100`
- `output_tokens`: `374415`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `110`
- `total_batches`: `28`
- `total_tokens`: `2439796`
- `transport_recovered_call_count`: `1`

## Next Batch

- Batch: `WAVE5_PSRC_HOLO_BATCH_003`
- Family: `HV-PSRC-REP-2026-07-01`
- Approval SHA: `499579865d8a1b1e44a9f13bac1c64f23e1f71496e2aecd90ac6120c8fc7eb96`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 499579865d8a1b1e44a9f13bac1c64f23e1f71496e2aecd90ac6120c8fc7eb96 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_003 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
