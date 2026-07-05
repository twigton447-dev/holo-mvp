# HoloVerify-V Gov Rescue: Subtle Closeout 021

Classification: `LIVE_GOV_V_RESCUE_COMPLETE`
Signal: `GOV_V_RESCUED_FROZEN_CONTROL_FAILURE_AND_PASSED_GUARDRAIL`

Frozen failed control: `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` raw MiniMax M2.5 returned `ESCALATE` where local audit target is `ALLOW`.

Provider calls: 2
Tokens: 3728 input / 3640 output / 7368 total

| Call | Packet | Verdict | Binding | Admissible | Failures |
| ---: | --- | --- | --- | --- | --- |
| 1 | `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | `ALLOW` | `EXACT_MATCH_CLOSED` | True | [] |
| 2 | `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | `ESCALATE` | `HOLD_CLASS_MISMATCH` | True | [] |
