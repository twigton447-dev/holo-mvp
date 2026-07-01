# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_SECO_HOLO_BATCH_001`
- Family: `HV-SECO-REP-2026-07-01`
- Batch number: `1`
- Approval SHA: `7b544fc5442eec7dafaa5cd9e4238bccc84b48ad4ccaa658220af567b73b12ab`

Required approval statement:

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_001 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 7b544fc5442eec7dafaa5cd9e4238bccc84b48ad4ccaa658220af567b73b12ab --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_001 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
