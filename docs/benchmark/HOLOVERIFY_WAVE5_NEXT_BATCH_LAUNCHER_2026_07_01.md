# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_LREG_HOLO_BATCH_003`
- Family: `HV-LREG-REP-2026-07-01`
- Batch number: `3`
- Approval SHA: `a76861940b67ecadc6737b56d680890b9c83e9b07a9d7b09ad3c41ce0e8b1189`

Required approval statement:

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_003 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 a76861940b67ecadc6737b56d680890b9c83e9b07a9d7b09ad3c41ce0e8b1189 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_003 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
