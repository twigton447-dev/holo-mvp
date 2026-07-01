# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_SECO_HOLO_BATCH_002`
Family: `HV-SECO-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `398bd98cc7b9892c8272fea8627886122c25ca573ac5eb1ab80cd330af0f1657`
Live preflight root signature: `090bd37211383f2e839c811ca0be32da2f3d2d5977f8b5743929021964ba6170`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 398bd98cc7b9892c8272fea8627886122c25ca573ac5eb1ab80cd330af0f1657 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_002 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
