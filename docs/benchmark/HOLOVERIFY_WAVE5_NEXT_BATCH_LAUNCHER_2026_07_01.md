# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_004`
- Family: `HV-CLAD-REP-2026-07-01`
- Batch number: `4`
- Approval SHA: `cdac66ca9081ca18cdef03b914db281e5ff71633f33970acc042688419479f5d`

Required approval statement:

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_004 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 cdac66ca9081ca18cdef03b914db281e5ff71633f33970acc042688419479f5d --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_004 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
