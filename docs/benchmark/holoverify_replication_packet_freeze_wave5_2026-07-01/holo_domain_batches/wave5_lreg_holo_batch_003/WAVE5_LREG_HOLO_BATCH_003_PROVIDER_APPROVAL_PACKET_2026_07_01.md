# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_LREG_HOLO_BATCH_003`
Family: `HV-LREG-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `a76861940b67ecadc6737b56d680890b9c83e9b07a9d7b09ad3c41ce0e8b1189`
Live preflight root signature: `2ffa34961d5ac2de466b7c5eaf8543fed38620b3e88d9658bb5aa3ca7acfa1db`

## Required Statement

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_003 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 a76861940b67ecadc6737b56d680890b9c83e9b07a9d7b09ad3c41ce0e8b1189 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_003 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
