# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `24`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `23`
- `completed_packets`: `230`
- `completed_pairs`: `115`
- `expected_provider_calls_for_completed_batches`: `1150`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `5`
- `provider_calls_observed`: `1200`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `115`
- `allow_packets`: `115`
- `completed_batches`: `23`
- `completed_correct_packets`: `230`
- `completed_packets`: `230`
- `completed_pairs`: `115`
- `duplicate_clean_run_batches`: `1`
- `escalate_correct`: `115`
- `escalate_packets`: `115`
- `expected_provider_calls_for_completed_batches`: `1150`
- `guardrail_packets`: `115`
- `input_tokens`: `2003552`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `5`
- `observed_provider_calls_for_completed_batches`: `1150`
- `output_tokens`: `391628`
- `preserved_non_counted_clean_runs`: `1`
- `target_packets`: `115`
- `total_batches`: `28`
- `total_tokens`: `2551108`
- `transport_recovered_call_count`: `1`

## Next Batch

- Batch: `WAVE5_PSRC_HOLO_BATCH_004`
- Family: `HV-PSRC-REP-2026-07-01`
- Approval SHA: `8ce4c1fc50f5bed1e69b20096cc2a13ccfe503c781a1d4dee36399cdf862b80d`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 8ce4c1fc50f5bed1e69b20096cc2a13ccfe503c781a1d4dee36399cdf862b80d --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_004 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
