# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_SECO_HOLO_BATCH_004`
Family: `HV-SECO-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `78b8cc0be4c9b6933e7328ef795e859c5a7a153b1ed472ecdee6eb9458c3bce8`
Live preflight root signature: `a92223278aa4ead5609a2d16cfea69e3d87787c7ed2aebf99905b333f81f1fda`

## Required Statement

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_004 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Expected Calls If Approved

- `pairs`: `5`
- `packets`: `10`
- `worker_calls`: `30`
- `gov_calls`: `20`
- `total_provider_calls`: `50`
- `judge_calls`: `0`
- `solo_calls`: `0`

## Command After Explicit Approval

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 78b8cc0be4c9b6933e7328ef795e859c5a7a153b1ed472ecdee6eb9458c3bce8 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_004 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
