# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_OTSF_HOLO_BATCH_004`
Family: `HV-OTSF-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `c2950e6375a565cebaa753607aa9d3363b7b5a3565bb7678f4b5b5ab57293b07`
Live preflight root signature: `3417eb0515588b9d3f4698e9ee521c0e11512bd4a6534fd79c6b05ad3c05084e`

## Required Statement

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_004 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 c2950e6375a565cebaa753607aa9d3363b7b5a3565bb7678f4b5b5ab57293b07 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_004 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
