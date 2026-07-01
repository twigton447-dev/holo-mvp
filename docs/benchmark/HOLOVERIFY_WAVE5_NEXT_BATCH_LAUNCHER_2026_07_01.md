# HoloVerify Wave5 Next Batch Launcher

Status: `PASS`
Provider calls by this report: `0`
Judge calls by this report: `0`

## Next Batch

- Batch: `WAVE5_SECO_HOLO_BATCH_004`
- Family: `HV-SECO-REP-2026-07-01`
- Batch number: `4`
- Approval SHA: `95eb7d649533618d5f8f85069fa3a41a9b542620ea4f44ae09595080dea698e8`

Required approval statement:

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_004 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

Command after explicit approval:

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 95eb7d649533618d5f8f85069fa3a41a9b542620ea4f44ae09595080dea698e8 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_004 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Boundary

This launcher report is no-provider. Live execution must use `--run-live` with the exact approval statement and approval SHA.
