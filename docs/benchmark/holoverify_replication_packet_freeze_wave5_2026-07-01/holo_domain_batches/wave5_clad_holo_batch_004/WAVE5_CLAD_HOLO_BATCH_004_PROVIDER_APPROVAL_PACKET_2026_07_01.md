# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_CLAD_HOLO_BATCH_004`
Family: `HV-CLAD-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `101d29ceb98f396d8f49bb5f5593b2d3e89426638c21391a14bfe295cf875d2b`
Live preflight root signature: `293bd97b6bdb11ee6695e39049af3032c767e853f2b4afc775364fb6191c0c95`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-CLAD-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 101d29ceb98f396d8f49bb5f5593b2d3e89426638c21391a14bfe295cf875d2b --approval-statement "I explicitly approve provider calls for WAVE5_CLAD_HOLO_BATCH_004 only, exactly as scoped in WAVE5_CLAD_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
