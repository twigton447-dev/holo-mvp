# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `2`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `2`
- `completed_packets`: `20`
- `completed_pairs`: `10`
- `expected_provider_calls_for_completed_batches`: `100`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `26`
- `provider_calls_observed`: `100`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `10`
- `allow_packets`: `10`
- `completed_batches`: `2`
- `completed_correct_packets`: `20`
- `completed_packets`: `20`
- `completed_pairs`: `10`
- `escalate_correct`: `10`
- `escalate_packets`: `10`
- `expected_provider_calls_for_completed_batches`: `100`
- `guardrail_packets`: `10`
- `input_tokens`: `176387`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `26`
- `observed_provider_calls_for_completed_batches`: `100`
- `output_tokens`: `35162`
- `target_packets`: `10`
- `total_batches`: `28`
- `total_tokens`: `225498`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_MEDX_HOLO_BATCH_003`
- Family: `HV-MEDX-REP-2026-07-01`
- Approval SHA: `164cbbce07c402e214b36110865ea49217f5d4f30af3defbd0c8ca0d29b9f07b`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 164cbbce07c402e214b36110865ea49217f5d4f30af3defbd0c8ca0d29b9f07b --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_003 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
