# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_TRES_HOLO_BATCH_003`
Family: `HV-TRES-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `f35427ac919c6f0beaa5378676e48f6328b7cba6ec271553c8a662d550a567ff`
Live preflight root signature: `dc6a0a7c5c55a405e97687036f75e11585c4ba37e176b5a448843e9b9d404b20`

## Required Statement

`I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_003 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 f35427ac919c6f0beaa5378676e48f6328b7cba6ec271553c8a662d550a567ff --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_003 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
