# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_SECO_HOLO_BATCH_001`
Family: `HV-SECO-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `7e290524efd6c408eeff0a3886f8c399c344cf5dd1a24ef2c08ec21ab3285a3b`
Live preflight root signature: `91bd2acef55f75caedfb4ec05f182ad77934eab675226522aea4bef3c182e7d5`

## Required Statement

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_001 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 7e290524efd6c408eeff0a3886f8c399c344cf5dd1a24ef2c08ec21ab3285a3b --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_001 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
