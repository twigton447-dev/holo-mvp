# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_PSRC_HOLO_BATCH_004`
Family: `HV-PSRC-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `b79a323256eeb7ffa971e3d73d9d7816f80a9bd0e8687cefed782a1ff31743fe`
Live preflight root signature: `674f21e96f19f723f243cf2d37f6413003f2d4cf0261d1c536c58956483d876f`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-PSRC-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 b79a323256eeb7ffa971e3d73d9d7816f80a9bd0e8687cefed782a1ff31743fe --approval-statement "I explicitly approve provider calls for WAVE5_PSRC_HOLO_BATCH_004 only, exactly as scoped in WAVE5_PSRC_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
