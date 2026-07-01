# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `3`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `3`
- `completed_packets`: `30`
- `completed_pairs`: `15`
- `expected_provider_calls_for_completed_batches`: `150`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `25`
- `provider_calls_observed`: `150`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `15`
- `allow_packets`: `15`
- `completed_batches`: `3`
- `completed_correct_packets`: `30`
- `completed_packets`: `30`
- `completed_pairs`: `15`
- `escalate_correct`: `15`
- `escalate_packets`: `15`
- `expected_provider_calls_for_completed_batches`: `150`
- `guardrail_packets`: `15`
- `input_tokens`: `263633`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `25`
- `observed_provider_calls_for_completed_batches`: `150`
- `output_tokens`: `52074`
- `target_packets`: `15`
- `total_batches`: `28`
- `total_tokens`: `337167`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_MEDX_HOLO_BATCH_004`
- Family: `HV-MEDX-REP-2026-07-01`
- Approval SHA: `7fb34b48ae48831fb18451b6211a3ef5f420822a24908659139abe5f63e6ac2d`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 7fb34b48ae48831fb18451b6211a3ef5f420822a24908659139abe5f63e6ac2d --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_004 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
