# HoloVerify Replication Packet Freeze: 3 Families Wave 2

Date: 2026-07-01T01:39:41.047559+00:00

Status: FROZEN_LOCAL_NO_PROVIDERS

Freeze root hash: `80d8106d7efe72bee44d2c05648b71814204c08e1f96934afefd3d75d242845f`

No providers were run. No judges were run. Holo was not run. Solo was not run.

## Scope

| Metric | Value |
| --- | ---: |
| `families` | 3 |
| `pairs` | 60 |
| `packets` | 120 |
| `hard_allow_target_pairs` | 30 |
| `hard_escalate_target_pairs` | 30 |
| `allow_packet_truths` | 60 |
| `escalate_packet_truths` | 60 |

## Final Assertion

| Assertion | Result |
| --- | --- |
| `families` | `3` |
| `pairs` | `60` |
| `packets` | `120` |
| `schema_validation` | `PASS` |
| `pair_balance` | `PASS` |
| `no_prompt_leakage` | `PASS` |
| `no_answer_key_leakage` | `PASS` |
| `no_provider_calls` | `PASS` |
| `no_judge_calls` | `PASS` |
| `packet_hashes_present` | `PASS` |
| `prompt_hashes_present` | `PASS` |
| `freeze_root_hash_present` | `PASS` |

## Family Summary

| Family | Pairs | Packets | Truth counts | Target counts |
| --- | ---: | ---: | --- | --- |
| `HV-HRWF-REP-2026-07-01` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-DPRV-REP-2026-07-01` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-FINC-REP-2026-07-01` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |

## Created Artifacts

- Packet hash manifest: `holoverify_replication_packet_freeze_3families_wave2_2026-07-01/manifests/PACKET_HASH_MANIFEST.json`
- Prompt hash manifest: `holoverify_replication_packet_freeze_3families_wave2_2026-07-01/manifests/PROMPT_HASH_MANIFEST.json`
- Local validation report: `holoverify_replication_packet_freeze_3families_wave2_2026-07-01/reports/LOCAL_VALIDATION_REPORT.json`
- Leakage scan report: `holoverify_replication_packet_freeze_3families_wave2_2026-07-01/reports/LEAKAGE_SCAN_REPORT.json`

## Stop Boundary

This is a local packet freeze only. Live HoloVerify, solo baselines, and judging remain locked until separately approved.
