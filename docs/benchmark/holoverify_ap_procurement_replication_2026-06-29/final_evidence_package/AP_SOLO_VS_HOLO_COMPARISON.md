# AP Solo vs Holo Comparison

## Pair Rollup

| Pair | Solo failures | Solo attempts | Holo all correct |
| --- | ---: | ---: | --- |
| `HV-AP-REP-001` | 4 | 6 | `True` |
| `HV-AP-REP-002` | 3 | 6 | `True` |
| `HV-AP-REP-003` | 2 | 6 | `True` |
| `HV-AP-REP-004` | 2 | 6 | `True` |
| `HV-AP-REP-005` | 5 | 6 | `True` |
| `HV-AP-REP-006` | 2 | 6 | `True` |
| `HV-AP-REP-007` | 3 | 6 | `True` |
| `HV-AP-REP-008` | 2 | 6 | `True` |
| `HV-AP-REP-009` | 3 | 6 | `True` |
| `HV-AP-REP-010` | 3 | 6 | `True` |
| `HV-AP-REP-011` | 5 | 6 | `True` |
| `HV-AP-REP-012` | 4 | 6 | `True` |
| `HV-AP-REP-013` | 3 | 6 | `True` |
| `HV-AP-REP-014` | 5 | 6 | `True` |
| `HV-AP-REP-015` | 4 | 6 | `True` |
| `HV-AP-REP-016` | 3 | 6 | `True` |
| `HV-AP-REP-017` | 2 | 6 | `True` |
| `HV-AP-REP-018` | 3 | 6 | `True` |
| `HV-AP-REP-019` | 6 | 6 | `True` |
| `HV-AP-REP-020` | 3 | 6 | `True` |

## Rows

| Packet | Model | Truth | Solo | Solo admissible | Holo | Class |
| --- | --- | --- | --- | --- | --- | --- |
| `HV-AP-REP-001-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-001-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-001-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-001-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-001-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-001-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-002-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-002-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-002-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-002-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-002-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-002-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-003-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-003-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-003-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-003-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-003-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-003-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-004-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-004-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-004-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-004-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-004-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-004-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-005-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-005-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-005-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-005-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `None` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-005-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-005-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-006-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-006-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-006-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-006-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `None` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-006-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-006-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-007-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-007-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-007-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-007-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-007-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-007-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-008-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-008-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-008-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-008-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `None` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-008-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-008-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-009-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-009-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-009-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-009-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `None` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-009-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-009-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-010-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-010-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-010-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-010-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-010-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-010-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-011-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-011-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-011-A` | `xai/grok-3-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-011-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `None` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-011-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-011-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-012-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-012-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-012-A` | `xai/grok-3-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-012-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-012-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-012-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-013-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-013-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-013-A` | `xai/grok-3-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-013-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-013-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-013-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-014-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-014-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-014-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-014-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-014-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-014-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-015-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-015-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-015-A` | `xai/grok-3-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-015-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-015-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-015-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-016-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-016-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-016-A` | `xai/grok-3-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-016-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-016-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-016-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-017-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-017-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-017-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-017-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-017-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-017-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-018-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `None` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-018-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-018-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-018-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-018-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-018-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-019-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-019-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ESCALATE` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-019-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-019-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `None` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-019-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-019-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-020-A` | `minimax/MiniMax-M2.5-highspeed` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-020-A` | `openai/gpt-5.4-mini` | `ALLOW` | `ALLOW` | `True` | `ALLOW` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-020-A` | `xai/grok-3-mini` | `ALLOW` | `ALLOW` | `False` | `ALLOW` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-020-B` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `ESCALATE` | `False` | `ESCALATE` | `EXTERNAL_SOLO_RESCUE` |
| `HV-AP-REP-020-B` | `openai/gpt-5.4-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
| `HV-AP-REP-020-B` | `xai/grok-3-mini` | `ESCALATE` | `ESCALATE` | `True` | `ESCALATE` | `SOLO_CORRECT_HOLO_CORRECT` |
