# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_SECO_HOLO_BATCH_002`
Family: `HV-SECO-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `bea3d98b10a83f3faaae2b07313d04be88df09aeffa55720e6fa16f635de1a63`
Live preflight root signature: `5a3c426f249da28a1d09ff0f9ace3d8be875de61492deff123f9c3b2008503fc`

## Required Statement

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_002 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 bea3d98b10a83f3faaae2b07313d04be88df09aeffa55720e6fa16f635de1a63 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_002 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
