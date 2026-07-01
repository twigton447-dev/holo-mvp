# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_TRES_HOLO_BATCH_003`
Family: `HV-TRES-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `d4fd39911ed8c635f9b278c64eef575dee8d5aad84160ecc79570aba8ee38a8c`
Live preflight root signature: `a28506c79af03f7eeb83771601f861d2dc122476401f27b148f87500f3eb1dfc`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-TRES-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 d4fd39911ed8c635f9b278c64eef575dee8d5aad84160ecc79570aba8ee38a8c --approval-statement "I explicitly approve provider calls for WAVE5_TRES_HOLO_BATCH_003 only, exactly as scoped in WAVE5_TRES_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
