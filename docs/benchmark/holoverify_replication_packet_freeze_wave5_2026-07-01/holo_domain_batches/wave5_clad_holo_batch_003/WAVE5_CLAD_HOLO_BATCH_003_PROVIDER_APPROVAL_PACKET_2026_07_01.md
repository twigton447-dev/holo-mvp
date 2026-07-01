# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_CLAD_HOLO_BATCH_003`
Family: `HV-CLAD-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `9d730b21da1013a3664299342ef1e6e338c2bd0b8c45c7f46ec6cbeb660d10be`
Live preflight root signature: `802ae194c04089bcbe60cb7a42357f449f5c86a9a20e9472c30a4debe5098583`

## Required Statement

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_003 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 9d730b21da1013a3664299342ef1e6e338c2bd0b8c45c7f46ec6cbeb660d10be --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_003 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
