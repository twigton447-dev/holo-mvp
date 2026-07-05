# HoloVerify 20-Pair 3-DNA Partial Run

Classification: `INVALID_RUN_TERMINAL_CALL_FAILURE_BEFORE_COMPLETION`
Readiness passed: `False`
Provider calls: `30` / `200`
Worker calls: `18`
Gov calls: `12`
Tokens: `61828` input / `18617` output / `84561` total

## Terminal Failures

| Turn | Kind | Provider | Model | Finish | Error |
| --- | --- | --- | --- | --- | --- |
| `HV-KITC-078-A_G1` | `gov` | `minimax` | `MiniMax-M2.5-highspeed` | `stop` | `None` |
| `HV-KITC-082-B_G2` | `gov` | `minimax` | `MiniMax-M2.5-highspeed` | `length` | `JSONDecodeError: Expecting value: line 1 column 1 (char 0)` |

## Roster

- Actual distinct DNA: `google, minimax, xai`
- Roster mismatches: `0`

## Reason

Trace ended before live_results.json existed; run is not comparable or score-valid.
