# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_MEDX_HOLO_BATCH_003`
Family: `HV-MEDX-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `164cbbce07c402e214b36110865ea49217f5d4f30af3defbd0c8ca0d29b9f07b`
Live preflight root signature: `d94a1ee1974f1762f4bd3c81729d6d5fc686c8b15f68a77733bb49c0a8a4d231`

## Required Statement

`I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_003 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 164cbbce07c402e214b36110865ea49217f5d4f30af3defbd0c8ca0d29b9f07b --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_003 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
