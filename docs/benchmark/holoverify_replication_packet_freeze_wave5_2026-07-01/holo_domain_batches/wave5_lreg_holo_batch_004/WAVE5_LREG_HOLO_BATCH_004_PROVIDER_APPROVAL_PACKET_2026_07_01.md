# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_LREG_HOLO_BATCH_004`
Family: `HV-LREG-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `72c594069a80c601b15c3525700a57d22b2953081748d0aecb52596e0e3b9fb5`
Live preflight root signature: `029fceaa1dbc47e645d4dad48ce686839511675119a3d70b00414cafdb419998`

## Required Statement

`I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_004 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-LREG-REP-2026-07-01 --batch-number 4 --run-live --approval-packet-sha256 72c594069a80c601b15c3525700a57d22b2953081748d0aecb52596e0e3b9fb5 --approval-statement "I explicitly approve provider calls for WAVE5_LREG_HOLO_BATCH_004 only, exactly as scoped in WAVE5_LREG_HOLO_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
