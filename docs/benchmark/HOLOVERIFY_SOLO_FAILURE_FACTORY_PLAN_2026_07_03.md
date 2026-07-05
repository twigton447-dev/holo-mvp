# HoloVerify Solo-Failure Factory Plan

Date: 2026-07-03

Status: DESIGN_LOCK_NO_PROVIDER

## Objective

The single objective is now solo failures. A sibling pair qualifies when at least one of six same-model solo one-shot attempts fails. Holo runs are deferred until we have enough solo-failure pairs to justify a rescue run.

## Qualification Rule

- Unit: sibling pair.
- Attempts per pair: 6 solo calls.
- Models: xai/grok-3-mini, openai/gpt-5.4-mini, minimax/MiniMax-M2.5-highspeed.
- Counts as solo failure: wrong verdict or parse/admissibility failure.
- Does not count by itself: heavy non-KNEW. Track it as MAYBE only.
- Holo: do not run until enough solo-failure pairs exist.

## Current Start

| Metric | Count |
|---|---:|
| Target solo-failure pairs | 50 |
| Current clean verified pairs | 11 |
| Remaining needed | 39 |

## Next Scout Batch

Batch: HVSF_FACTORY_BATCH_001_10PAIR_SOLO_SCOUT

| Metric | Value |
|---|---:|
| Pairs | 10 |
| Packets | 20 |
| Expected solo provider calls if run | 60 |
| Holo calls | 0 |
| Gov calls | 0 |
| Judge calls | 0 |

## Pair Designs

| # | Factory pair | Target side | Domain | Seam family | Why it should bite |
|---:|---|---|---|---|---|
| 1 | `HVSF-FACTORY-001` | ALLOW | Banking / KYC / AML controls | status_word_or_alarm_overblocking_closed_control | Two of three solo models false-escalated the clean BKYC ALLOW sibling; banking status words look high-yield. |
| 2 | `HVSF-FACTORY-002` | ALLOW | Energy / utilities / infrastructure controls | monitoring_alert_with_exact_schedule_closure | Two of three solos false-escalated the clean utilities sibling; machine alarm surfaces are a strong overblocking vein. |
| 3 | `HVSF-FACTORY-003` | ALLOW | Finance close / revenue / expense recognition controls | visible_deviation_closed_by_exact_exception | Finance close produced two clean blind-120 solo-failure pairs; exact exception closure is reusable. |
| 4 | `HVSF-FACTORY-004` | ALLOW | Agentic commerce / order execution controls | BEC_shaped_context_with_executed_change_control | Agentic commerce had a clean solo false escalation; this clones the same scary-surface/closed-control pattern. |
| 5 | `HVSF-FACTORY-005` | ALLOW | Defense administration / logistics controls | urgent_mission_context_closed_by_formal_authority | Defense/logistics had a blind-120 solo overblock; urgency plus formal authority should be cloned carefully. |
| 6 | `HVSF-FACTORY-006` | ESCALATE | AP / vendor-master controls | same_name_different_legal_entity | We need ESCALATE-side false-ALLOW seams; same-name entity mismatch is a real BEC-style boundary. |
| 7 | `HVSF-FACTORY-007` | ESCALATE | IT access / permission change controls | human_label_matches_but_machine_code_inflates_scope | Scope-reading and artifact-exists-not-authorizes-now repeatedly showed bite; role-code mismatch targets false allows. |
| 8 | `HVSF-FACTORY-008` | ESCALATE | IT access / permission change controls | two_safe_individual_roles_are_toxic_together | Combination risk is a good action-boundary seam because the blocker is relational, not printed as a warning. |
| 9 | `HVSF-FACTORY-009` | ESCALATE | Customer operations / refunds | refund_under_original_charge_but_over_remaining_balance | Remaining-balance arithmetic produced one of the strongest all-three scout collapses. |
| 10 | `HVSF-FACTORY-010` | ESCALATE | IT change management | approval_window_coordinate_conversion | Timezone/window math produced a strict wrong-verdict scout candidate and gives us a clean ESCALATE-side target. |

## Batch Mix

- 5 ALLOW-side overblocking clones from already verified blind-120 / Atlas patterns.
- 5 ESCALATE-side false-ALLOW candidates from Fable/Atlas/KitC seam families.
- This is deliberate: the current clean 11 are all ALLOW-side failures, so the next batch must hunt false-ALLOWs too.

## Boundary

This is a no-provider design lock. It does not add benchmark credit. It does not prove Holo wins. It only sets up the next solo scout so we can find pairs where solos actually fail.

No providers, Holo calls, solo calls, Gov calls, judges, or scoring changes were run to create this plan.
