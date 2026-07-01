# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_SECO_HOLO_BATCH_002`
- Family: `HV-SECO-REP-2026-07-01`
- Batch number: `2`
- Approval SHA: `3e9ff2cedc8961da0a8de2a87c104e08f7de5ae549e504b6e5bd0e55f29aa938`

Required approval statement:

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_002 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 3e9ff2cedc8961da0a8de2a87c104e08f7de5ae549e504b6e5bd0e55f29aa938 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_002 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
