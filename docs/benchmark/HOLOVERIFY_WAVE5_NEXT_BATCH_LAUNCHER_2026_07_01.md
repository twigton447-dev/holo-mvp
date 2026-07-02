# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_PSRC_HOLO_BATCH_003`
- Family: `HV-PSRC-REP-2026-07-01`
- Batch number: `3`
- Approval SHA: `499579865d8a1b1e44a9f13bac1c64f23e1f71496e2aecd90ac6120c8fc7eb96`

Required approval statement:

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_003 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 499579865d8a1b1e44a9f13bac1c64f23e1f71496e2aecd90ac6120c8fc7eb96 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_003 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
