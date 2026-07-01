# HoloVerify Wave5 Completed Batch Evidence

Status: `PASS`
Evidence state: `PARTIAL_CLEAN_EVIDENCE`
Source ledger queue state: `READY_FOR_NEXT_BATCH`
Source ledger builder SHA-256: `fbf47676e8de1d59fe685a7128e46523eac964eeea499187bb23f4c37d38ca03`
Collector script SHA-256: `d2721c6d4e1fbdfe9f60862eea7566071008b9620d1a737c7d98843fc015a983`
Freeze root: `3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf`

## Claim Boundary

- `full_wave5_claim_allowed`: `False`
- `partial_claim_allowed`: `True`
- `zero_completed_batches_is_not_evidence`: `False`
- `stop_if_invalid_batch_present`: `False`
- `unrun_batches_count_as_no_evidence`: `True`

## Totals

- `total_batches`: `28`
- `completed_batches`: `5`
- `not_started_batches`: `23`
- `invalid_batches`: `0`
- `completed_pairs`: `25`
- `completed_packets`: `50`
- `completed_correct_packets`: `50`
- `expected_provider_calls_for_completed_batches`: `250`
- `observed_provider_calls_for_completed_batches`: `250`
- `judge_calls`: `0`
- `transport_recovered_call_count`: `0`
- `input_tokens`: `437579`
- `output_tokens`: `86284`
- `total_tokens`: `557311`
- `allow_packets`: `25`
- `escalate_packets`: `25`
- `allow_correct`: `25`
- `escalate_correct`: `25`
- `target_packets`: `25`
- `guardrail_packets`: `25`

## Checks

| Check | Value |
| --- | --- |
| `ledger_status_pass` | `True` |
| `ledger_queue_not_invalid` | `True` |
| `invalid_batches_absent` | `True` |
| `completed_results_match_completed_batches` | `True` |
| `provider_calls_match_completed_expectation` | `True` |
| `no_judge_calls` | `True` |
| `all_completed_batches_ready` | `True` |
| `all_completed_packets_correct` | `True` |

## Completed Runs

| Batch | Run | Provider calls | Packets | Correct | Valid pairs |
| --- | --- | --- | --- | --- | --- |
| `WAVE5_MEDX_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_001/live_runs/run_20260701T190553Z` | `50` | `10` | `10` | `5` |
| `WAVE5_MEDX_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_002/live_runs/run_20260701T192304Z` | `50` | `10` | `10` | `5` |
| `WAVE5_MEDX_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_003/live_runs/run_20260701T193310Z` | `50` | `10` | `10` | `5` |
| `WAVE5_MEDX_HOLO_BATCH_004` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_004/live_runs/run_20260701T194218Z` | `50` | `10` | `10` | `5` |
| `WAVE5_TRES_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_tres_holo_batch_001/live_runs/run_20260701T195657Z` | `50` | `10` | `10` | `5` |

## Next Allowed Batch

- Batch: `WAVE5_TRES_HOLO_BATCH_002`
- Family: `HV-TRES-REP-2026-07-01`
- Approval SHA: `453f3d3a322b9a0a340c2e093e9274b12ad0eb373814ac7561abae2313db563e`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 453f3d3a322b9a0a340c2e093e9274b12ad0eb373814ac7561abae2313db563e --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_002 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```
