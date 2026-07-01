# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_SECO_HOLO_BATCH_003`
Family: `HV-SECO-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `279e58a9a6f76420bea21e307083a5c65f36867a0a7a96c157a6c50d2136ee04`
Live preflight root signature: `e00d41d2ad61c3c9f0f3163a95fdade4737f3772386bd6c2e2d1cb35a7fb0f18`

## Required Statement

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_003 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 279e58a9a6f76420bea21e307083a5c65f36867a0a7a96c157a6c50d2136ee04 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_003 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
