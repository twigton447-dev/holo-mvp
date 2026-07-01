# HoloVerify Wave5 Completed Batch Evidence

Status: `PASS`
Evidence state: `NO_COMPLETED_BATCHES_YET`
Source ledger queue state: `READY_FOR_NEXT_BATCH`
Source ledger builder SHA-256: `fbf47676e8de1d59fe685a7128e46523eac964eeea499187bb23f4c37d38ca03`
Collector script SHA-256: `d2721c6d4e1fbdfe9f60862eea7566071008b9620d1a737c7d98843fc015a983`
Freeze root: `3690788df10f817e153113d3eb15f850bb5de2a1a6256253ad8f3031a26238cf`

## Claim Boundary

- `full_wave5_claim_allowed`: `False`
- `partial_claim_allowed`: `False`
- `zero_completed_batches_is_not_evidence`: `True`
- `stop_if_invalid_batch_present`: `False`
- `unrun_batches_count_as_no_evidence`: `True`

## Totals

- `total_batches`: `28`
- `completed_batches`: `0`
- `not_started_batches`: `28`
- `invalid_batches`: `0`
- `completed_pairs`: `0`
- `completed_packets`: `0`
- `completed_correct_packets`: `0`
- `expected_provider_calls_for_completed_batches`: `0`
- `observed_provider_calls_for_completed_batches`: `0`
- `judge_calls`: `0`
- `transport_recovered_call_count`: `0`
- `input_tokens`: `0`
- `output_tokens`: `0`
- `total_tokens`: `0`
- `allow_packets`: `0`
- `escalate_packets`: `0`
- `allow_correct`: `0`
- `escalate_correct`: `0`
- `target_packets`: `0`
- `guardrail_packets`: `0`

## Checks

| Check | Value |
| --- | --- |
| `ledger_status_pass` | `True` |
| `ledger_queue_not_invalid` | `True` |
| `invalid_batches_absent` | `True` |
| `completed_results_match_completed_batches` | `True` |
| `provider_calls_match_completed_expectation` | `True` |
| `no_judge_calls` | `True` |
| `all_completed_batches_ready` | `True` |
| `all_completed_packets_correct` | `True` |

## Completed Runs

No Wave5 live batch has completed yet. This file is readiness scaffolding, not benchmark evidence.

## Next Allowed Batch

- Batch: `WAVE5_MEDX_HOLO_BATCH_001`
- Family: `HV-MEDX-REP-2026-07-01`
- Approval SHA: `4aabf9937d7aa629ed4da512d924b99fdafc8b8a4e437df47e7fd80deff8bbc0`

```bash
python3 -B docs/benchmark/run_wave5_holo_domain_batch_2026_07_01.py --family HV-MEDX-REP-2026-07-01 --batch-number 1 --run-live --approval-packet-sha256 4aabf9937d7aa629ed4da512d924b99fdafc8b8a4e437df47e7fd80deff8bbc0 --approval-statement "I explicitly approve provider calls for WAVE5_MEDX_HOLO_BATCH_001 only, exactly as scoped in WAVE5_MEDX_HOLO_BATCH_001_PROVIDER_APPROVAL_PACKET_2026_07_01."
```
