# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_PSRC_HOLO_BATCH_003`
Family: `HV-PSRC-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `5fbc27082b0f6315fd91f9282566dccdd907f70720f490533f7682d6cb1c7ab2`
Live preflight root signature: `81f2604ec68860ddc8e7e523f49eead38651387d3d328112a9b32d9537f5ac1c`

## Required Statement

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_003 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 5fbc27082b0f6315fd91f9282566dccdd907f70720f490533f7682d6cb1c7ab2 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_003 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
