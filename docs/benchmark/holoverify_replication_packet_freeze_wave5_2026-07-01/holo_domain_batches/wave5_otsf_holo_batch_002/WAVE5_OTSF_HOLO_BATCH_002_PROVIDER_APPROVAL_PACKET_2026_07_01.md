# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_OTSF_HOLO_BATCH_002`
Family: `HV-OTSF-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `959c8b1ab4d004b91bd1f346661d29302376baba323488c36ad2b0e362982091`
Live preflight root signature: `d9d632c75c4c28389978c45c9c580f11f14bc1a0d84baf9bb8e731d77cf95324`

## Required Statement

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_002 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 959c8b1ab4d004b91bd1f346661d29302376baba323488c36ad2b0e362982091 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_002 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
