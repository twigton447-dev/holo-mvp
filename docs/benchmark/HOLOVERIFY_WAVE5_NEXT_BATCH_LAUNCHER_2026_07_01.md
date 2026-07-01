# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_LREG_HOLO_BATCH_001`
- Family: `HV-LREG-REP-2026-07-01`
- Batch number: `1`
- Approval SHA: `1e9186de923375b99c1b7c10db36270e0adde0a7bd903d35c1af4a8736af4e90`

Required approval statement:

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_001 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 1e9186de923375b99c1b7c10db36270e0adde0a7bd903d35c1af4a8736af4e90 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_001 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
