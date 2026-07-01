# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_001`
- Family: `HV-CLAD-REP-2026-07-01`
- Batch number: `1`
- Approval SHA: `fe4c710403b9158fccb4ff4611904cec3f687f66c9969a7a3dc730f3d592d307`

Required approval statement:

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_001 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 fe4c710403b9158fccb4ff4611904cec3f687f66c9969a7a3dc730f3d592d307 --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_001 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
