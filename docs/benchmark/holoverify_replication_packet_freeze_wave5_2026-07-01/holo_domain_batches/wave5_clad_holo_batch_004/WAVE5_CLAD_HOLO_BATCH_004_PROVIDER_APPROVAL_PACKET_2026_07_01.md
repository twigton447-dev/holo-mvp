# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_CLAD_HOLO_BATCH_004`
Family: `HV-CLAD-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `226e8c30d064bfa6a12fe59f08fa427b8a53b8ae6373786dbb0a9ab77957e951`
Live preflight root signature: `b0c8f518de7d32076bdad8f2a311e2ad985fd90c634a80668f97cbf9b9a2f425`

## Required Statement

`I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_004 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 226e8c30d064bfa6a12fe59f08fa427b8a53b8ae6373786dbb0a9ab77957e951 --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_004 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
