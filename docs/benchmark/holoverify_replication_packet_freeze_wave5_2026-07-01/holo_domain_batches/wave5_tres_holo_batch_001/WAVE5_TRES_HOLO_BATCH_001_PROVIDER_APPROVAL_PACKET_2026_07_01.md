# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_TRES_HOLO_BATCH_001`
Family: `HV-TRES-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `a1e7f8e017b83e9281a9b8fc03aa68fcf3d08dde32a609f6ab899932f53940c5`
Live preflight root signature: `d2ac5fe9c8ef408a906488a43c1a64a3dc80092f6908869cd0dc3317c3642051`

## Required Statement

`I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_001 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 a1e7f8e017b83e9281a9b8fc03aa68fcf3d08dde32a609f6ab899932f53940c5 --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_001 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
