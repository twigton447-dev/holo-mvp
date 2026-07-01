# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_TRES_HOLO_BATCH_004`
Family: `HV-TRES-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `6168eb3221408da059d52c4d2c5e36416b73c117aaff82c634bb1aa507f6b069`
Live preflight root signature: `dc73f86283a730b2093fa6f6f583ebf787d3c8457f2dbd45255bd4688e79d7eb`

## Required Statement

`I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_004 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 6168eb3221408da059d52c4d2c5e36416b73c117aaff82c634bb1aa507f6b069 --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_004 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
