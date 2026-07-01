# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_MEDX_HOLO_BATCH_002`
Family: `HV-MEDX-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `bdb43e3867f0664aeb89a769c432e21bb848e17e28ecd373e7370ac6dd43d1b1`
Live preflight root signature: `408aaa8e81af085c0f231e8ec8e87f578ae0f205ea5eea07dfe085ea15ff1d4e`

## Required Statement

`I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_002 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 bdb43e3867f0664aeb89a769c432e21bb848e17e28ecd373e7370ac6dd43d1b1 --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_002 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
