# Inside-Holo Worker Solo Autopsy

Classification: `INSIDE_HOLO_WORKER_SOLO_AUTOPSY`

Freeze root signature: `47434052ed594ed65734e1e964434ae984a17777607fc72ad1c6424dd4de83f6`

Provider calls made now: `0`

## Question

If the same MiniMax worker calls inside Holo are treated as standalone solo final answers, do any fail the 10 locked packets?

## Answer

Yes. Standalone inside-Holo worker turns passed KNEW on `25/30` worker turns.

Packets with at least one standalone worker failure: `5/10`.

Internal failures before Holo correction, including deterministic gate failures and standalone KNEW failures: `6/30` worker turns.

Packets with at least one internal failure before Holo correction: `5/10`.

This means Holo's 10/10 final KNEW result is not explained by every MiniMax worker being individually perfect. It is explained by the full architecture: Gov, deterministic gates, state, artifact registry, pinned best, and final selection.

## By Worker Role

| Worker | Role | KNEW | Standalone KNEW failures | Internal failures before correction |
| ---: | --- | ---: | ---: | ---: |
| 1 | `SOURCE_BOUNDARY_MAPPER` | 7/10 | 3 | 3 |
| 2 | `ADVERSARIAL_SCOPE_CHALLENGER` | 8/10 | 2 | 2 |
| 3 | `FINAL_COMPILER` | 10/10 | 0 | 1 |

## By Packet

| Packet | Kind | Worker KNEW | Standalone KNEW failures | Internal failures before correction | Labels |
| --- | --- | ---: | ---: | ---: | --- |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | `hard_allow` | 2/3 | 1 | 1 | W1=KNEW/gate=PASS, W2=LUCKY/gate=FAIL, W3=KNEW/gate=PASS |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | `escalate` | 2/3 | 1 | 1 | W1=LUCKY/gate=FAIL, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `hard_allow` | 3/3 | 0 | 0 | W1=KNEW/gate=PASS, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `escalate` | 3/3 | 0 | 0 | W1=KNEW/gate=PASS, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |
| `HV-KITC-042-A` | `hard_allow` | 3/3 | 0 | 0 | W1=KNEW/gate=PASS, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |
| `HV-KITC-042-B` | `escalate` | 3/3 | 0 | 0 | W1=KNEW/gate=PASS, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |
| `HV-KITC-047-A` | `hard_allow` | 3/3 | 0 | 0 | W1=KNEW/gate=PASS, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |
| `HV-KITC-047-B` | `escalate` | 2/3 | 1 | 1 | W1=WRONG/gate=FAIL, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |
| `HV-KITC-082-A` | `hard_allow` | 2/3 | 1 | 2 | W1=KNEW/gate=PASS, W2=WRONG/gate=FAIL, W3=KNEW/gate=FAIL |
| `HV-KITC-082-B` | `escalate` | 2/3 | 1 | 1 | W1=WRONG/gate=FAIL, W2=KNEW/gate=PASS, W3=KNEW/gate=PASS |

## Interpretation

The same MiniMax substrate inside Holo can fail before HoloGov/full architecture correction when individual worker turns are treated as standalone solos or gate-checked in isolation. Holo's 10/10 final KNEW result depends on governance, gates, state, artifact selection, and repair across turns, not on every single worker call being independently perfect.
