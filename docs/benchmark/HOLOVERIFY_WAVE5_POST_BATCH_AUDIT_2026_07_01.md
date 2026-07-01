# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `6`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `6`
- `completed_packets`: `60`
- `completed_pairs`: `30`
- `expected_provider_calls_for_completed_batches`: `300`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `22`
- `provider_calls_observed`: `300`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `30`
- `allow_packets`: `30`
- `completed_batches`: `6`
- `completed_correct_packets`: `60`
- `completed_packets`: `60`
- `completed_pairs`: `30`
- `escalate_correct`: `30`
- `escalate_packets`: `30`
- `expected_provider_calls_for_completed_batches`: `300`
- `guardrail_packets`: `30`
- `input_tokens`: `524146`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `22`
- `observed_provider_calls_for_completed_batches`: `300`
- `output_tokens`: `103595`
- `target_packets`: `30`
- `total_batches`: `28`
- `total_tokens`: `667581`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_TRES_HOLO_BATCH_003`
- Family: `HV-TRES-REP-2026-07-01`
- Approval SHA: `f35427ac919c6f0beaa5378676e48f6328b7cba6ec271553c8a662d550a567ff`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 f35427ac919c6f0beaa5378676e48f6328b7cba6ec271553c8a662d550a567ff --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_003 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
