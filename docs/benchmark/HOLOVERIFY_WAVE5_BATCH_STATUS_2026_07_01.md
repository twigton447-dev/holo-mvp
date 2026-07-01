# HoloVerify Wave5 Batch Status

Status: `PASS`
Queue state: `READY_FOR_NEXT_BATCH`
Provider calls by this status check: `0`
Judge calls by this status check: `0`

## Totals

- `selected_batches`: `28`
- `run_folders`: `14`
- `completed_batches`: `13`
- `not_started_batches`: `15`
- `invalid_stop_batches`: `0`
- `in_progress_or_incomplete_batches`: `0`
- `provider_calls_observed_from_artifacts`: `700`

## Next Or Blocking Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_002`
- Family: `HV-CLAD-REP-2026-07-01`
- Status: `NOT_STARTED`
- Approval SHA: `eb988b7c83cad89ca3d709e3ca8d0e19b1a238164e8be73e9c60e3d2fc184b54`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 eb988b7c83cad89ca3d709e3ca8d0e19b1a238164e8be73e9c60e3d2fc184b54 --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_002 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Batch Rows

| Batch | Family | Status | Runs | Latest run | Provider calls observed | Invalidation |
| --- | --- | --- | --- | --- | --- | --- |
| `WAVE5_MEDX_HOLO_BATCH_001` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T190553Z` | `50` | `N/A` |
| `WAVE5_MEDX_HOLO_BATCH_002` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T192304Z` | `50` | `N/A` |
| `WAVE5_MEDX_HOLO_BATCH_003` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T193310Z` | `50` | `N/A` |
| `WAVE5_MEDX_HOLO_BATCH_004` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T194218Z` | `50` | `N/A` |
| `WAVE5_TRES_HOLO_BATCH_001` | `HV-TRES-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T195657Z` | `50` | `N/A` |
| `WAVE5_TRES_HOLO_BATCH_002` | `HV-TRES-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T200540Z` | `50` | `N/A` |
| `WAVE5_TRES_HOLO_BATCH_003` | `HV-TRES-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T201925Z` | `50` | `N/A` |
| `WAVE5_TRES_HOLO_BATCH_004` | `HV-TRES-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T203759Z` | `50` | `N/A` |
| `WAVE5_LREG_HOLO_BATCH_001` | `HV-LREG-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T204454Z` | `50` | `N/A` |
| `WAVE5_LREG_HOLO_BATCH_002` | `HV-LREG-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T205533Z` | `50` | `N/A` |
| `WAVE5_LREG_HOLO_BATCH_003` | `HV-LREG-REP-2026-07-01` | `COMPLETE` | `2` | `run_20260701T210956Z` | `50` | `N/A` |
| `WAVE5_LREG_HOLO_BATCH_004` | `HV-LREG-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T212207Z` | `50` | `N/A` |
| `WAVE5_CLAD_HOLO_BATCH_001` | `HV-CLAD-REP-2026-07-01` | `COMPLETE` | `1` | `run_20260701T214106Z` | `50` | `N/A` |
| `WAVE5_CLAD_HOLO_BATCH_002` | `HV-CLAD-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_CLAD_HOLO_BATCH_003` | `HV-CLAD-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_CLAD_HOLO_BATCH_004` | `HV-CLAD-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_SECO_HOLO_BATCH_001` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_SECO_HOLO_BATCH_002` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_SECO_HOLO_BATCH_003` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_SECO_HOLO_BATCH_004` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_PSRC_HOLO_BATCH_001` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_PSRC_HOLO_BATCH_002` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_PSRC_HOLO_BATCH_003` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_PSRC_HOLO_BATCH_004` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_OTSF_HOLO_BATCH_001` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_OTSF_HOLO_BATCH_002` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_OTSF_HOLO_BATCH_003` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |
| `WAVE5_OTSF_HOLO_BATCH_004` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `N/A` | `0` | `N/A` |

## Boundary

This status check is read-only and no-provider. It never runs Holo, solo, or judges.
