# HoloVerify Replication Packet Freeze: Wave 3 / Wave 4

Created at: `2026-07-01T08:40:59.842947+00:00`

Status: `FROZEN_LOCAL_NO_PROVIDERS`

Freeze root hash: `ac44c5d69ad73c64dcae1591e37cc9ade8a80ed5e71a05786cd2490a445c2dd5`

No providers were run. No Holo run was started. No solo run was started. No judges were run.

## Scope

| Metric | Value |
| --- | ---: |
| `waves` | 2 |
| `families` | 6 |
| `pairs` | 120 |
| `packets` | 240 |
| `hard_allow_target_pairs` | 60 |
| `hard_escalate_target_pairs` | 60 |
| `allow_packet_truths` | 120 |
| `escalate_packet_truths` | 120 |

## Final Assertions

| Assertion | Result |
| --- | --- |
| `waves` | `2` |
| `families` | `6` |
| `pairs` | `120` |
| `packets` | `240` |
| `schema_validation` | `PASS` |
| `pair_balance` | `PASS` |
| `no_prompt_leakage` | `PASS` |
| `no_answer_key_leakage` | `PASS` |
| `no_provider_calls` | `PASS` |
| `no_judge_calls` | `PASS` |
| `packet_hashes_present` | `PASS` |
| `prompt_hashes_present` | `PASS` |
| `freeze_root_hash_present` | `PASS` |

## Waves

| Wave | Families | Pairs | Packets | Truths |
| --- | ---: | ---: | ---: | --- |
| `wave3` | 3 | 60 | 120 | `{'ALLOW': 60, 'ESCALATE': 60}` |
| `wave4` | 3 | 60 | 120 | `{'ALLOW': 60, 'ESCALATE': 60}` |

## Families

| Family | Wave | Domain | Pairs | Packets | Truth counts | Target counts |
| --- | --- | --- | ---: | ---: | --- | --- |
| `HV-BENC-REP-2026-07-01` | `wave3` | Benefits / public casework controls | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-BKYC-REP-2026-07-01` | `wave3` | Banking / KYC / AML controls | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-DEFA-REP-2026-07-01` | `wave4` | Defense administration / logistics controls | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-GOVP-REP-2026-07-01` | `wave3` | Government procurement / grants controls | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-INSR-REP-2026-07-01` | `wave4` | Insurance claims / coverage controls | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |
| `HV-UTIL-REP-2026-07-01` | `wave4` | Energy / utilities / infrastructure controls | 20 | 40 | `{'ALLOW': 20, 'ESCALATE': 20}` | `{'hard_allow': 10, 'hard_escalate': 10}` |

## Created Artifacts

- Packet hash manifest: `holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/manifests/PACKET_HASH_MANIFEST.json`
- Prompt hash manifest: `holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/manifests/PROMPT_HASH_MANIFEST.json`
- Local validation report: `holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/reports/LOCAL_VALIDATION_REPORT.json`
- Leakage scan report: `holoverify_replication_packet_freeze_wave3_wave4_2026-07-01/reports/LEAKAGE_SCAN_REPORT.json`

## Stop Boundary

This is a local packet freeze only. Live HoloVerify, solo baselines, and judging remain locked until separately approved.
