# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_PSRC_HOLO_BATCH_004`
Family: `HV-PSRC-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `8ce4c1fc50f5bed1e69b20096cc2a13ccfe503c781a1d4dee36399cdf862b80d`
Live preflight root signature: `deef944c3f78e2b66c1b74dce4f31c27b91bb5189bcab9db883928d28d845811`

## Required Statement

`I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_004 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 8ce4c1fc50f5bed1e69b20096cc2a13ccfe503c781a1d4dee36399cdf862b80d --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_004 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
