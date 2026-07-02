# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_PSRC_HOLO_BATCH_002`
- Family: `HV-PSRC-REP-2026-07-01`
- Batch number: `2`
- Approval SHA: `3c68a5ef8bb4b87cfe65f833b0a27985ada829223d2565eb09486863796100f5`

Required approval statement:

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_002 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 3c68a5ef8bb4b87cfe65f833b0a27985ada829223d2565eb09486863796100f5 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_002 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
