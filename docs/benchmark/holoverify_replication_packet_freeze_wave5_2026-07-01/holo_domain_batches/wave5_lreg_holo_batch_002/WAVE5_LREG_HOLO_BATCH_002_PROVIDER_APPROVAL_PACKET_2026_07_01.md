# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_LREG_HOLO_BATCH_002`
Family: `HV-LREG-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `e8578c24140b9755cd496c1c119bd900830d7eeaab9ee12c4e97a3443ee9175e`
Live preflight root signature: `a66f2b95e99ec30acc7a9b6eb6d0669ea0393ab3e08be9cee82c6ab69b232bae`

## Required Statement

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_002 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 e8578c24140b9755cd496c1c119bd900830d7eeaab9ee12c4e97a3443ee9175e --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_002 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
