# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_PSRC_HOLO_BATCH_001`
- Family: `HV-PSRC-REP-2026-07-01`
- Batch number: `1`
- Approval SHA: `bb5140f3b9c4a7fdbd59a7c057a99c6457e01f3c7f2d9ac428801353787cc6d3`

Required approval statement:

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_001 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 bb5140f3b9c4a7fdbd59a7c057a99c6457e01f3c7f2d9ac428801353787cc6d3 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_001 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
