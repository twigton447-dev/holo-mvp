# HoloVerify Solo Failure Factory Batch 001 Packet Freeze

Status: `FROZEN_NO_PROVIDER_SOLO_SCOUT_BANK`

Created: `2026-07-03T19:02:35.913484+00:00`

Provider / Solo / Holo / Gov / Judge calls made by this freeze: `0 / 0 / 0 / 0 / 0`

Freeze root: `442dc91bfa71c7a43be0aed5276ee42c6bc495f535601e7a199fac732f82ccf1`

## Scope

- Pairs: `10`
- Packets: `20`
- Truth counts: `{'ALLOW': 10, 'ESCALATE': 10}`
- Target failure side counts: `{'ALLOW': 5, 'ESCALATE': 5}`
- Expected solo provider calls if approved later: `60`

This bank is for solo-failure discovery only. It does not approve provider execution, Holo execution, scoring claims, or public claims.

## Validation

- `plan_json_parse`: `True`
- `pair_count_10`: `True`
- `packet_count_20`: `True`
- `truth_balance`: `True`
- `target_failure_side_balance`: `True`
- `runtime_leakage_clean`: `True`
- `runtime_ids_unique`: `True`
- `runtime_manifest_separate_from_scoring_map`: `True`
- `provider_calls_zero`: `True`
- `solo_calls_zero`: `True`
- `holo_calls_zero`: `True`
- `gov_calls_zero`: `True`
- `judge_calls_zero`: `True`

## Selected Rows

| Legacy packet | Truth | Target side | Opaque runtime ID | Seam family |
| --- | --- | --- | --- | --- |
| `HVSF-FACTORY-001-A` | `ALLOW` | `ALLOW` | `HVSF001-9FAF36C613E8283CBF5F` | status_word_or_alarm_overblocking_closed_control |
| `HVSF-FACTORY-001-B` | `ESCALATE` | `ALLOW` | `HVSF001-8596CEE21A2C5BFA3D98` | status_word_or_alarm_overblocking_closed_control |
| `HVSF-FACTORY-002-A` | `ALLOW` | `ALLOW` | `HVSF001-273A8C3381B29879B573` | monitoring_alert_with_exact_schedule_closure |
| `HVSF-FACTORY-002-B` | `ESCALATE` | `ALLOW` | `HVSF001-FBEB32CDE7287BEAC571` | monitoring_alert_with_exact_schedule_closure |
| `HVSF-FACTORY-003-A` | `ALLOW` | `ALLOW` | `HVSF001-997E3AE13741248B5D84` | visible_deviation_closed_by_exact_exception |
| `HVSF-FACTORY-003-B` | `ESCALATE` | `ALLOW` | `HVSF001-1D559EFD13870CEE6B3E` | visible_deviation_closed_by_exact_exception |
| `HVSF-FACTORY-004-A` | `ALLOW` | `ALLOW` | `HVSF001-07C2ABDF098D94234998` | BEC_shaped_context_with_executed_change_control |
| `HVSF-FACTORY-004-B` | `ESCALATE` | `ALLOW` | `HVSF001-9CDDD01598036DFD70B3` | BEC_shaped_context_with_executed_change_control |
| `HVSF-FACTORY-005-A` | `ALLOW` | `ALLOW` | `HVSF001-414B013F2D8620AE615E` | urgent_mission_context_closed_by_formal_authority |
| `HVSF-FACTORY-005-B` | `ESCALATE` | `ALLOW` | `HVSF001-30708016988EA836CE36` | urgent_mission_context_closed_by_formal_authority |
| `HVSF-FACTORY-006-A` | `ALLOW` | `ESCALATE` | `HVSF001-7391B7095F46F708F787` | same_name_different_legal_entity |
| `HVSF-FACTORY-006-B` | `ESCALATE` | `ESCALATE` | `HVSF001-B9F0FF6CADD15516FE25` | same_name_different_legal_entity |
| `HVSF-FACTORY-007-A` | `ALLOW` | `ESCALATE` | `HVSF001-BB7420EE309282BF71E8` | human_label_matches_but_machine_code_inflates_scope |
| `HVSF-FACTORY-007-B` | `ESCALATE` | `ESCALATE` | `HVSF001-F5B9354574E859F59E1A` | human_label_matches_but_machine_code_inflates_scope |
| `HVSF-FACTORY-008-A` | `ALLOW` | `ESCALATE` | `HVSF001-EED69275B47B9F36EBC8` | two_safe_individual_roles_are_toxic_together |
| `HVSF-FACTORY-008-B` | `ESCALATE` | `ESCALATE` | `HVSF001-AF31197420ED5152353D` | two_safe_individual_roles_are_toxic_together |
| `HVSF-FACTORY-009-A` | `ALLOW` | `ESCALATE` | `HVSF001-3B8B749A710CACC78F9B` | refund_under_original_charge_but_over_remaining_balance |
| `HVSF-FACTORY-009-B` | `ESCALATE` | `ESCALATE` | `HVSF001-7535FFAD6097863E03A7` | refund_under_original_charge_but_over_remaining_balance |
| `HVSF-FACTORY-010-A` | `ALLOW` | `ESCALATE` | `HVSF001-1C781453C2F4B97A783C` | approval_window_coordinate_conversion |
| `HVSF-FACTORY-010-B` | `ESCALATE` | `ESCALATE` | `HVSF001-A0BF513B7A9F30EDE2DC` | approval_window_coordinate_conversion |
