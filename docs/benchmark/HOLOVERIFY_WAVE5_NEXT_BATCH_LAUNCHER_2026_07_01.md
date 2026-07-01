# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_CLAD_HOLO_BATCH_003`
- Family: `HV-CLAD-REP-2026-07-01`
- Batch number: `3`
- Approval SHA: `0cb5c81ebe146853931fd3f760039c19890eaf92dfa07c9c1cdab584d3683f5f`

Required approval statement:

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_003 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 0cb5c81ebe146853931fd3f760039c19890eaf92dfa07c9c1cdab584d3683f5f --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_003 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
