# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_OTSF_HOLO_BATCH_004`
- Family: `HV-OTSF-REP-2026-07-01`
- Batch number: `4`
- Approval SHA: `c2950e6375a565cebaa753607aa9d3363b7b5a3565bb7678f4b5b5ab57293b07`

Required approval statement:

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_004 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 c2950e6375a565cebaa753607aa9d3363b7b5a3565bb7678f4b5b5ab57293b07 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_004 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
