# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_CLAD_HOLO_BATCH_001`
Family: `HV-CLAD-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `fe4c710403b9158fccb4ff4611904cec3f687f66c9969a7a3dc730f3d592d307`
Live preflight root signature: `8b6fa631e6fd01313dd96e57d12db4b1105066911a026fe54bbf785486f4f97f`

## Required Statement

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_001 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 fe4c710403b9158fccb4ff4611904cec3f687f66c9969a7a3dc730f3d592d307 --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_001 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
