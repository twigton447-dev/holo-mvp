# HoloVerify Replication Packet Freeze: 3 Families

Date: 2026-06-29T10:37:33.485728+00:00

Status: FROZEN_LOCAL_NO_PROVIDERS

Freeze root hash: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

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
| `HV-AP-REP-2026-06-29` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-ACOM-REP-2026-06-29` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-ITAC-REP-2026-06-29` | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |

## Created Artifacts

- Packet hash manifest: `holoverify_replication_packet_freeze_3families_2026-06-29/manifests/PACKET_HASH_MANIFEST.json`
- Prompt hash manifest: `holoverify_replication_packet_freeze_3families_2026-06-29/manifests/PROMPT_HASH_MANIFEST.json`
- Local validation report: `holoverify_replication_packet_freeze_3families_2026-06-29/reports/LOCAL_VALIDATION_REPORT.json`
- Leakage scan report: `holoverify_replication_packet_freeze_3families_2026-06-29/reports/LEAKAGE_SCAN_REPORT.json`

## Stop Boundary

This is a local packet freeze only. Live HoloVerify, solo baselines, and judging remain locked until separately approved.
