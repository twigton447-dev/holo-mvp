# HoloVerify Wave5 Post-Batch Audit

Status: `PASS`
Post-batch state: `READY_FOR_NEXT_BATCH`
Provider calls by this audit: `0`
Judge calls by this audit: `0`
Wave5 live run folders: `9`

## Recommended Action

Run exactly the next allowed batch if provider calls are explicitly approved.

## Totals

### Progress Ledger

- `batches`: `28`
- `complete_with_prior_invalid_batches`: `0`
- `completed_batches`: `9`
- `completed_packets`: `90`
- `completed_pairs`: `45`
- `expected_provider_calls_for_completed_batches`: `450`
- `invalid_stop_batches`: `0`
- `judges_called_by_ledger`: `0`
- `not_started_batches`: `19`
- `provider_calls_observed`: `450`
- `providers_called_by_ledger`: `0`

### Completed Evidence

- `allow_correct`: `45`
- `allow_packets`: `45`
- `completed_batches`: `9`
- `completed_correct_packets`: `90`
- `completed_packets`: `90`
- `completed_pairs`: `45`
- `escalate_correct`: `45`
- `escalate_packets`: `45`
- `expected_provider_calls_for_completed_batches`: `450`
- `guardrail_packets`: `45`
- `input_tokens`: `784082`
- `invalid_batches`: `0`
- `judge_calls`: `0`
- `not_started_batches`: `19`
- `observed_provider_calls_for_completed_batches`: `450`
- `output_tokens`: `152935`
- `target_packets`: `45`
- `total_batches`: `28`
- `total_tokens`: `997673`
- `transport_recovered_call_count`: `0`

## Next Batch

- Batch: `WAVE5_LREG_HOLO_BATCH_002`
- Family: `HV-LREG-REP-2026-07-01`
- Approval SHA: `53f3c3f4d6d195ac54f57eb17e7f20564a6e1355ec1d05a87ba952615bc2979c`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 53f3c3f4d6d195ac54f57eb17e7f20564a6e1355ec1d05a87ba952615bc2979c --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_002 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Checks

| Check | Value |
| --- | --- |
| `progress_ledger_pass` | `True` |
| `completed_batch_evidence_pass` | `True` |
| `provider_calls_by_post_batch_audit` | `True` |
| `judge_calls_by_post_batch_audit` | `True` |
| `evidence_not_ahead_of_ledger` | `True` |
