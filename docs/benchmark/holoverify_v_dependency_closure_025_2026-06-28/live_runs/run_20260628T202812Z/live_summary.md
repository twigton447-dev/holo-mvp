# MiniMax Control vs HoloVerify-V Dependency Closure Diagnostic

Classification: `LIVE_DIAGNOSTIC_COMPLETE`
Signal: `CURRENT_CONTROL_SOLVED_HISTORICAL_FAILURE`

Provider calls: 4 / 4

## Token Totals

| Lane | Input | Output | Total |
| --- | ---: | ---: | ---: |
| `control` | 2174 | 2100 | 4274 |
| `gov` | 3706 | 2217 | 5923 |

## Rows

| Call | Lane | Packet | Verdict | Binding | Admissible | Failures |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `control` | `BAL100-BEC-QUIET-MISMATCH-025-B` | `ESCALATE` | `MISMATCH` | True | [] |
| 2 | `gov` | `BAL100-BEC-QUIET-MISMATCH-025-B` | `ESCALATE` | `MISMATCH` | True | [] |
| 3 | `control` | `BAL100-BEC-QUIET-MISMATCH-025-A` | `ALLOW` | `EXACT_MATCH` | True | [] |
| 4 | `gov` | `BAL100-BEC-QUIET-MISMATCH-025-A` | `ALLOW` | `EXACT_MATCH` | True | [] |
