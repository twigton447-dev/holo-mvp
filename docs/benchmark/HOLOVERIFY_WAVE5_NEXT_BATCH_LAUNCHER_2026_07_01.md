# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_001`
- Family: `HV-CLAD-REP-2026-07-01`
- Batch number: `1`
- Approval SHA: `bbe30f2651c94961dd61d7fac3895d0a50bc9a0dd346a8a7c4b6aa584dbc38b3`

Required approval statement:

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_001 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 bbe30f2651c94961dd61d7fac3895d0a50bc9a0dd346a8a7c4b6aa584dbc38b3 --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_001 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
