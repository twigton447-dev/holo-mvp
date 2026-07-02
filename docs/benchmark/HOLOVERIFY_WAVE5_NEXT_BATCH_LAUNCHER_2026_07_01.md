# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_OTSF_HOLO_BATCH_001`
- Family: `HV-OTSF-REP-2026-07-01`
- Batch number: `1`
- Approval SHA: `e147a28332e16e01a1d780039b30a6315a95df4a0345b1fbaca8d28b4258f788`

Required approval statement:

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_001 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 e147a28332e16e01a1d780039b30a6315a95df4a0345b1fbaca8d28b4258f788 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_001 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
