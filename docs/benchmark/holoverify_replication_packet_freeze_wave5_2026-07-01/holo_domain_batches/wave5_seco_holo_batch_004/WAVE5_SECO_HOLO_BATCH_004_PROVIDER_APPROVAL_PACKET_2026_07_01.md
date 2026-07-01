# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_SECO_HOLO_BATCH_004`
Family: `HV-SECO-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `1fb3c492423abecf1678efc4495fa6936789aa7b5d4cb6b27f33b56c4af8f8d3`
Live preflight root signature: `658e7c42b20bd3d3f7bcbe9051343ad16a18f11ecefd4097db0eafb86442576d`

## Required Statement

`I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_004 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-SECO-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 1fb3c492423abecf1678efc4495fa6936789aa7b5d4cb6b27f33b56c4af8f8d3 --approval-statement "I explicitly approve provider calls for WAVE5_SECO_HOLO_BATCH_004 only, exactly as scoped in WAVE5_SECO_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
