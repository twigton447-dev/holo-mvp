# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_OTSF_HOLO_BATCH_001`
Family: `HV-OTSF-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `260a9fbaeee1d6461c21ce04ad3f5e35011a9763a338812f5cce9a704e3fa320`
Live preflight root signature: `7fdb46ef44411e752140b3796f0728a8c30489405e8e74db39c2805e1ed86b5d`

## Required Statement

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_001 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 260a9fbaeee1d6461c21ce04ad3f5e35011a9763a338812f5cce9a704e3fa320 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_001 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
