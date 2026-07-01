# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_LREG_HOLO_BATCH_001`
Family: `HV-LREG-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `1e9186de923375b99c1b7c10db36270e0adde0a7bd903d35c1af4a8736af4e90`
Live preflight root signature: `e8c6d27628c79fa51f04f2b67fb02ad99d58dfdc0557fd12ba4130a3ec6cc738`

## Required Statement

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_001 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 1e9186de923375b99c1b7c10db36270e0adde0a7bd903d35c1af4a8736af4e90 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_001 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
