# HoloVerify-V Gov Rescue: Activation Dependency 022

Classification: `LIVE_GOV_V_RESCUE_COMPLETE`
Signal: `GOV_V_RESCUED_SECOND_FROZEN_CONTROL_FAILURE_AND_PASSED_GUARDRAIL`

Frozen failed control: `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` raw MiniMax M2.5 returned `ESCALATE` where local audit target is `ALLOW`.

Provider calls: 2
Tokens: 3851 input / 3197 output / 7048 total

| Call | Packet | Verdict | Binding | Admissible | Failures |
| ---: | --- | --- | --- | --- | --- |
| 1 | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ALLOW` | `EXACT_MATCH_CLOSED` | True | [] |
| 2 | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | `DEVICE_GROUP_SITE_MISMATCH` | True | [] |
