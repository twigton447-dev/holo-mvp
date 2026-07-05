# HoloVerify-V Gov Rescue: Activation Dependency 022

Classification: `LIVE_GOV_V_RESCUE_COMPLETE`
Signal: `NO_VALID_RESCUE_SIGNAL`

Frozen failed control: `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` raw MiniMax M2.5 returned `ESCALATE` where local audit target is `ALLOW`.

Provider calls: 2
Tokens: 3705 input / 2883 output / 6588 total

| Call | Packet | Verdict | Binding | Admissible | Failures |
| ---: | --- | --- | --- | --- | --- |
| 1 | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ALLOW` | `EXACT_MATCH_CLOSED` | True | [] |
| 2 | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | `DEVICE_GROUP_SITE_MISMATCH` | False | ['missing_ACT-ACR-022'] |
