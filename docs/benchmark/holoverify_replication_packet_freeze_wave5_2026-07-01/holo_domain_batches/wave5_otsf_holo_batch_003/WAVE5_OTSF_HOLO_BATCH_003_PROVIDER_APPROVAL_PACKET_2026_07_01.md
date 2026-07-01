# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_OTSF_HOLO_BATCH_003`
Family: `HV-OTSF-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `d271ce89608d8beada106c7596457c95174978c3c2e147e242ce40b3db363291`
Live preflight root signature: `504022e9d66e9bc1bc6f934ebcbf08f7e75ca33b3113e1f483e72e9e356620a1`

## Required Statement

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_003 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 3 --run-live --approval-packet-sha256 d271ce89608d8beada106c7596457c95174978c3c2e147e242ce40b3db363291 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_003 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_003_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
