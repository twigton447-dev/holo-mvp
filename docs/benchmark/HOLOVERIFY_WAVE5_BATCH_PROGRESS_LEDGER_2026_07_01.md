# HoloVerify Wave5 Batch Progress Ledger

Status: `PASS`
Queue state: `READY_FOR_NEXT_BATCH`
Source handoff builder SHA-256: `3132939673c00f37ca367efed30b6f59df8edc89699b5c4ff26b6e60963cfbb4`
Progress builder SHA-256: `fbf47676e8de1d59fe685a7128e46523eac964eeea499187bb23f4c37d38ca03`
Freeze root: `3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf`

## Totals

- `batches`: `28`
- `completed_batches`: `4`
- `not_started_batches`: `24`
- `invalid_stop_batches`: `0`
- `complete_with_prior_invalid_batches`: `0`
- `completed_pairs`: `20`
- `completed_packets`: `40`
- `provider_calls_observed`: `200`
- `expected_provider_calls_for_completed_batches`: `200`
- `providers_called_by_ledger`: `0`
- `judges_called_by_ledger`: `0`

## Next Allowed Batch

- Batch: `WAVE5_TRES_HOLO_BATCH_001`
- Family: `HV-TRES-REP-2026-07-01`
- Approval SHA: `c8e214491cdd69ac97ec319928739146718466a54b40c3e6ed86e2ab9fed4fc0`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 c8e214491cdd69ac97ec319928739146718466a54b40c3e6ed86e2ab9fed4fc0 --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_001 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Batch State

| # | Batch | Family | Status | Runs | Provider calls observed | Latest invalidation |
| --- | --- | --- | --- | --- | --- | --- |
| `1` | `WAVE5_MEDX_HOLO_BATCH_001` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `50` | `N/A` |
| `2` | `WAVE5_MEDX_HOLO_BATCH_002` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `50` | `N/A` |
| `3` | `WAVE5_MEDX_HOLO_BATCH_003` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `50` | `N/A` |
| `4` | `WAVE5_MEDX_HOLO_BATCH_004` | `HV-MEDX-REP-2026-07-01` | `COMPLETE` | `1` | `50` | `N/A` |
| `5` | `WAVE5_TRES_HOLO_BATCH_001` | `HV-TRES-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `6` | `WAVE5_TRES_HOLO_BATCH_002` | `HV-TRES-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `7` | `WAVE5_TRES_HOLO_BATCH_003` | `HV-TRES-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `8` | `WAVE5_TRES_HOLO_BATCH_004` | `HV-TRES-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `9` | `WAVE5_LREG_HOLO_BATCH_001` | `HV-LREG-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `10` | `WAVE5_LREG_HOLO_BATCH_002` | `HV-LREG-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `11` | `WAVE5_LREG_HOLO_BATCH_003` | `HV-LREG-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `12` | `WAVE5_LREG_HOLO_BATCH_004` | `HV-LREG-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `13` | `WAVE5_CLAD_HOLO_BATCH_001` | `HV-CLAD-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `14` | `WAVE5_CLAD_HOLO_BATCH_002` | `HV-CLAD-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `15` | `WAVE5_CLAD_HOLO_BATCH_003` | `HV-CLAD-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `16` | `WAVE5_CLAD_HOLO_BATCH_004` | `HV-CLAD-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `17` | `WAVE5_SECO_HOLO_BATCH_001` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `18` | `WAVE5_SECO_HOLO_BATCH_002` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `19` | `WAVE5_SECO_HOLO_BATCH_003` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `20` | `WAVE5_SECO_HOLO_BATCH_004` | `HV-SECO-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `21` | `WAVE5_PSRC_HOLO_BATCH_001` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `22` | `WAVE5_PSRC_HOLO_BATCH_002` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `23` | `WAVE5_PSRC_HOLO_BATCH_003` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `24` | `WAVE5_PSRC_HOLO_BATCH_004` | `HV-PSRC-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `25` | `WAVE5_OTSF_HOLO_BATCH_001` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `26` | `WAVE5_OTSF_HOLO_BATCH_002` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `27` | `WAVE5_OTSF_HOLO_BATCH_003` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |
| `28` | `WAVE5_OTSF_HOLO_BATCH_004` | `HV-OTSF-REP-2026-07-01` | `NOT_STARTED` | `0` | `0` | `N/A` |

## Boundary

This ledger does not call providers. It only reads existing batch artifacts and live-run outputs.
