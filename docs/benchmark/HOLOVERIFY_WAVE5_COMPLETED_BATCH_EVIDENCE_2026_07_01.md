# HoloVerify Wave5 Completed Batch Evidence

Status: `PASS`
Evidence state: `PARTIAL_CLEAN_EVIDENCE`
Source ledger queue state: `READY_FOR_NEXT_BATCH`
Source ledger builder SHA-256: `fbf47676e8de1d59fe685a7128e46523eac964eeea499187bb23f4c37d38ca03`
Collector script SHA-256: `f26a0aa65ebb1d1474311558963bcdf7ff9ad5e1266641ffbf4d3f633f84abd5`
Freeze root: `3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf`

## Claim Boundary

- `full_wave5_claim_allowed`: `False`
- `partial_claim_allowed`: `True`
- `zero_completed_batches_is_not_evidence`: `False`
- `stop_if_invalid_batch_present`: `False`
- `unrun_batches_count_as_no_evidence`: `True`

## Totals

- `total_batches`: `28`
- `completed_batches`: `13`
- `not_started_batches`: `15`
- `invalid_batches`: `0`
- `completed_pairs`: `65`
- `completed_packets`: `130`
- `completed_correct_packets`: `130`
- `expected_provider_calls_for_completed_batches`: `650`
- `observed_provider_calls_for_completed_batches`: `650`
- `judge_calls`: `0`
- `transport_recovered_call_count`: `0`
- `input_tokens`: `1132740`
- `output_tokens`: `220917`
- `total_tokens`: `1440773`
- `allow_packets`: `65`
- `escalate_packets`: `65`
- `allow_correct`: `65`
- `escalate_correct`: `65`
- `target_packets`: `65`
- `guardrail_packets`: `65`
- `duplicate_clean_run_batches`: `1`
- `preserved_non_counted_clean_runs`: `1`

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
| `duplicate_clean_runs_preserved_and_not_counted` | `True` |

## Completed Runs

| Batch | Run | Provider calls | Packets | Correct | Valid pairs |
| --- | --- | --- | --- | --- | --- |
| `WAVE5_MEDX_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_001/live_runs/run_20260701T190553Z` | `50` | `10` | `10` | `5` |
| `WAVE5_MEDX_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_002/live_runs/run_20260701T192304Z` | `50` | `10` | `10` | `5` |
| `WAVE5_MEDX_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_003/live_runs/run_20260701T193310Z` | `50` | `10` | `10` | `5` |
| `WAVE5_MEDX_HOLO_BATCH_004` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_medx_holo_batch_004/live_runs/run_20260701T194218Z` | `50` | `10` | `10` | `5` |
| `WAVE5_TRES_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_tres_holo_batch_001/live_runs/run_20260701T195657Z` | `50` | `10` | `10` | `5` |
| `WAVE5_TRES_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_tres_holo_batch_002/live_runs/run_20260701T200540Z` | `50` | `10` | `10` | `5` |
| `WAVE5_TRES_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_tres_holo_batch_003/live_runs/run_20260701T201925Z` | `50` | `10` | `10` | `5` |
| `WAVE5_TRES_HOLO_BATCH_004` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_tres_holo_batch_004/live_runs/run_20260701T203759Z` | `50` | `10` | `10` | `5` |
| `WAVE5_LREG_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_001/live_runs/run_20260701T204454Z` | `50` | `10` | `10` | `5` |
| `WAVE5_LREG_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_002/live_runs/run_20260701T205533Z` | `50` | `10` | `10` | `5` |
| `WAVE5_LREG_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_003/live_runs/run_20260701T210956Z` | `50` | `10` | `10` | `5` |
| `WAVE5_LREG_HOLO_BATCH_004` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_004/live_runs/run_20260701T212207Z` | `50` | `10` | `10` | `5` |
| `WAVE5_CLAD_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_001/live_runs/run_20260701T214106Z` | `50` | `10` | `10` | `5` |

## Duplicate Clean Runs Preserved

| Batch | Counted run | Preserved non-counted runs |
| --- | --- | --- |
| `WAVE5_LREG_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_003/live_runs/run_20260701T210956Z` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_003/live_runs/run_20260701T210231Z` |

## Next Allowed Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_002`
- Family: `HV-CLAD-REP-2026-07-01`
- Approval SHA: `96fca2cc0bd42c7df9e444da48711c28737db1b9a5c2dad90d24e20e9a9ab5ad`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 96fca2cc0bd42c7df9e444da48711c28737db1b9a5c2dad90d24e20e9a9ab5ad --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_002 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```
