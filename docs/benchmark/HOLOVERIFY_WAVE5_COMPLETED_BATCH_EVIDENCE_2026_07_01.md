# HoloVerify Wave5 Completed Batch Evidence

Status: `FAIL`
Evidence state: `STOP_FOR_AUTOPSY`
Source ledger queue state: `STOP_FOR_AUTOPSY`
Source ledger builder SHA-256: `fbf47676e8de1d59fe685a7128e46523eac964eeea499187bb23f4c37d38ca03`
Collector script SHA-256: `f26a0aa65ebb1d1474311558963bcdf7ff9ad5e1266641ffbf4d3f633f84abd5`
Freeze root: `3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf`

## Claim Boundary

- `full_wave5_claim_allowed`: `False`
- `partial_claim_allowed`: `False`
- `zero_completed_batches_is_not_evidence`: `False`
- `stop_if_invalid_batch_present`: `True`
- `unrun_batches_count_as_no_evidence`: `True`

## Totals

- `total_batches`: `28`
- `completed_batches`: `27`
- `not_started_batches`: `0`
- `invalid_batches`: `1`
- `completed_pairs`: `135`
- `completed_packets`: `270`
- `completed_correct_packets`: `270`
- `expected_provider_calls_for_completed_batches`: `1350`
- `observed_provider_calls_for_completed_batches`: `1350`
- `judge_calls`: `0`
- `transport_recovered_call_count`: `3`
- `input_tokens`: `2355662`
- `output_tokens`: `460932`
- `total_tokens`: `2999965`
- `allow_packets`: `135`
- `escalate_packets`: `135`
- `allow_correct`: `135`
- `escalate_correct`: `135`
- `target_packets`: `135`
- `guardrail_packets`: `135`
- `duplicate_clean_run_batches`: `1`
- `preserved_non_counted_clean_runs`: `1`

## Checks

| Check | Value |
| --- | --- |
| `ledger_status_pass` | `True` |
| `ledger_queue_not_invalid` | `False` |
| `invalid_batches_absent` | `False` |
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
| `WAVE5_CLAD_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_002/live_runs/run_20260701T215907Z` | `50` | `10` | `10` | `5` |
| `WAVE5_CLAD_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_003/live_runs/run_20260701T225854Z` | `50` | `10` | `10` | `5` |
| `WAVE5_CLAD_HOLO_BATCH_004` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_clad_holo_batch_004/live_runs/run_20260701T231050Z` | `50` | `10` | `10` | `5` |
| `WAVE5_SECO_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_seco_holo_batch_001/live_runs/run_20260701T232237Z` | `50` | `10` | `10` | `5` |
| `WAVE5_SECO_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_seco_holo_batch_002/live_runs/run_20260701T234200Z` | `50` | `10` | `10` | `5` |
| `WAVE5_SECO_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_seco_holo_batch_003/live_runs/run_20260701T235327Z` | `50` | `10` | `10` | `5` |
| `WAVE5_SECO_HOLO_BATCH_004` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_seco_holo_batch_004/live_runs/run_20260701T235916Z` | `50` | `10` | `10` | `5` |
| `WAVE5_PSRC_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_psrc_holo_batch_001/live_runs/run_20260702T001044Z` | `50` | `10` | `10` | `5` |
| `WAVE5_PSRC_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_psrc_holo_batch_002/live_runs/run_20260702T002058Z` | `50` | `10` | `10` | `5` |
| `WAVE5_PSRC_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_psrc_holo_batch_003/live_runs/run_20260702T002818Z` | `50` | `10` | `10` | `5` |
| `WAVE5_PSRC_HOLO_BATCH_004` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_psrc_holo_batch_004/live_runs/run_20260702T003553Z` | `50` | `10` | `10` | `5` |
| `WAVE5_OTSF_HOLO_BATCH_001` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_otsf_holo_batch_001/live_runs/run_20260702T024125Z` | `50` | `10` | `10` | `5` |
| `WAVE5_OTSF_HOLO_BATCH_002` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_otsf_holo_batch_002/live_runs/run_20260702T025607Z` | `50` | `10` | `10` | `5` |
| `WAVE5_OTSF_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_otsf_holo_batch_003/live_runs/run_20260702T035651Z` | `50` | `10` | `10` | `5` |

## Duplicate Clean Runs Preserved

| Batch | Counted run | Preserved non-counted runs |
| --- | --- | --- |
| `WAVE5_LREG_HOLO_BATCH_003` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_003/live_runs/run_20260701T210956Z` | `docs/benchmark/holoverify_replication_packet_freeze_wave5_2026-07-01/holo_domain_batches/wave5_lreg_holo_batch_003/live_runs/run_20260701T210231Z` |

## Next Allowed Batch

Stop for autopsy before running another Wave5 batch.
