# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_LREG_HOLO_BATCH_004`
Family: `HV-LREG-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `a5f2bdd590ea7a0b4f4dfaf6baec8c344e28558de2419fff30f4a41f28412620`
Live preflight root signature: `404d60277b877ea1b976af1aa2448a4c7cf0446302b3d2ec2fba182c74ffce3e`

## Required Statement

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_004 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 a5f2bdd590ea7a0b4f4dfaf6baec8c344e28558de2419fff30f4a41f28412620 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_004 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
