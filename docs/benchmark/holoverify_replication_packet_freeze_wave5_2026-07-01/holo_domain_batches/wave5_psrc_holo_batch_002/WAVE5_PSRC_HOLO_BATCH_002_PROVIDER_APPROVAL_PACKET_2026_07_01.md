# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_PSRC_HOLO_BATCH_002`
Family: `HV-PSRC-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `3c68a5ef8bb4b87cfe65f833b0a27985ada829223d2565eb09486863796100f5`
Live preflight root signature: `9c45d08f5a02b90397c838a26c73fd5b60311be98a8f5ba097ff9879fede69eb`

## Required Statement

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_002 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 3c68a5ef8bb4b87cfe65f833b0a27985ada829223d2565eb09486863796100f5 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_002 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
