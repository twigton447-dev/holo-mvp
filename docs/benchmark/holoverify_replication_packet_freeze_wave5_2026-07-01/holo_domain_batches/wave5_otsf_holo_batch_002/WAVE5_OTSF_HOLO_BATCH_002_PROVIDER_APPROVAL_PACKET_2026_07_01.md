# Wave5 Holo Batch Provider Approval Packet

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Batch: `WAVE5_OTSF_HOLO_BATCH_002`
Family: `HV-OTSF-REP-2026-07-01`
Approval granted by this packet: `False`
Approval packet SHA-256: `ce195d664177fed19fc531d9ac7a6ad39e6fadfdfe496842cf9069b8f4220b99`
Live preflight root signature: `e1dc6a6edfd3e52edd67ff2cd8857f06609171c12143d7cb522b4375d89228d9`

## Required Statement

`I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_002 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01.`

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
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-OTSF-REP-2026-07-01 --batch-number 2 --run-live --approval-packet-sha256 ce195d664177fed19fc531d9ac7a6ad39e6fadfdfe496842cf9069b8f4220b99 --approval-statement "I explicitly approve provider calls for WAVE5_OTSF_HOLO_BATCH_002 only, exactly as scoped in WAVE5_OTSF_HOLO_BATCH_002_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Stop Rules

- Do not run providers without exact approval statement and approval packet SHA.
- Do not edit frozen packets or prompts.
- Do not run solo or judges.
- Do not fallback or substitute models.
- If the batch fails, preserve the invalid run and stop.
