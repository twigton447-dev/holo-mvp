# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_PSRC_HOLO_BATCH_003`
Family: `HV-PSRC-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `499579865d8a1b1e44a9f13bac1c64f23e1f71496e2aecd90ac6120c8fc7eb96`
Live preflight root signature: `7960dc6c8f44f79d38004c65acf7120314bc188b032df61fa8978e89a127efbe`

## Required Statement

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_003 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 499579865d8a1b1e44a9f13bac1c64f23e1f71496e2aecd90ac6120c8fc7eb96 --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_003 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
