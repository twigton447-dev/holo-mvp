# Local Codex Trace Judgment

Classification: `LOCAL_CODEX_TRACE_JUDGMENT_NON_EXTERNAL`

External independent judge: `false`

Freeze root signature: `47434052ed594ed65734e1e964434ae984a17777607fc72ad1c6424dd4de83f6`

This judgment reviews the frozen judge packet, Solo one-shot trace, Holo selected artifacts, and local benchmark results. It does not replace external independent judges, but it gives a file-backed trace judgment while external transfer remains approval-blocked.

## KNEW-Only Result

| Lane | KNEW | Non-pass labels |
| --- | ---: | --- |
| Solo one-shot MiniMax | 7/10 | `WRONG`, `CONFUSED`, `LUCKY` |
| Full HoloVerify | 10/10 | none |

## Boundary Finding

Solo is not always wrong. On this locked set, Solo gets 7 of 10 packets to `KNEW`.

The reliability problem is the action boundary: across matched ALLOW/ESCALATE sibling seams, Solo sometimes proves the decisive condition and sometimes fails at the exact place where the decision turns. The three non-passes show three different boundary risks:

- `BAL100-BEC-SUBTLE-CLOSEOUT-021-A`: Solo over-escalated a closed hard-ALLOW boundary.
- `BAL100-BEC-SUBTLE-CLOSEOUT-021-B`: Solo returned malformed/truncated JSON at an ESCALATE guardrail seam.
- `HV-KITC-042-B`: Solo reached the right ESCALATE verdict but did not prove the controlling source-boundary term, so the label is `LUCKY`.

Full HoloVerify produced `KNEW` on all 10 packets.

## Artifact Labels

| Packet | Solo | Holo |
| --- | --- | --- |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | WRONG | KNEW |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | CONFUSED | KNEW |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | KNEW | KNEW |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | KNEW | KNEW |
| `HV-KITC-042-A` | KNEW | KNEW |
| `HV-KITC-042-B` | LUCKY | KNEW |
| `HV-KITC-047-A` | KNEW | KNEW |
| `HV-KITC-047-B` | KNEW | KNEW |
| `HV-KITC-082-A` | KNEW | KNEW |
| `HV-KITC-082-B` | KNEW | KNEW |

Full structured judgment: `LOCAL_CODEX_TRACE_JUDGMENT.json`.
