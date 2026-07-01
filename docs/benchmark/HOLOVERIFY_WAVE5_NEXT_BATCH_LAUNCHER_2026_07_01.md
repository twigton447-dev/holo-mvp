# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_TRES_HOLO_BATCH_003`
- Family: `HV-TRES-REP-2026-07-01`
- Batch number: `3`
- Approval SHA: `f35427ac919c6f0beaa5378676e48f6328b7cba6ec271553c8a662d550a567ff`

Required approval statement:

`I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_003 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 f35427ac919c6f0beaa5378676e48f6328b7cba6ec271553c8a662d550a567ff --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_003 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
