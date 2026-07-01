# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_PSRC_HOLO_BATCH_002`
Family: `HV-PSRC-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `2f4862937b1cd633d98f828667e44b3771c812a5ff786640a3c5f3e378c03a7e`
Live preflight root signature: `7bf05982dd0ad6f1337ccc6ee46dab8c8636a5e883479ee706ecdf02f91f724a`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 2f4862937b1cd633d98f828667e44b3771c812a5ff786640a3c5f3e378c03a7e --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_002 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
