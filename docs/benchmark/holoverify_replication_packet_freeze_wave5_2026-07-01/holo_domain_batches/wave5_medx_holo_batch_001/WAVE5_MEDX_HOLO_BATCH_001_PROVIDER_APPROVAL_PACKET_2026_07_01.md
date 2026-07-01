# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_MEDX_HOLO_BATCH_001`
Family: `HV-MEDX-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `57aa1ae0dc035b2c5769d29aa1f2eb14ca8a4e9ef1027fecc2ad234abab1cb24`
Live preflight root signature: `fc5652562ce075574bb46f7a873c96af936c367501d055e31718168a957776c4`

## Required Statement

`I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_001 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 57aa1ae0dc035b2c5769d29aa1f2eb14ca8a4e9ef1027fecc2ad234abab1cb24 --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_001 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
