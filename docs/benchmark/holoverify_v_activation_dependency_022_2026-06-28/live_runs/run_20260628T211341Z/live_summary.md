# HoloVerify-V Gov Rescue: Activation Dependency 022

Classification: `LIVE_GOV_V_RESCUE_COMPLETE`
Signal: `NO_VALID_RESCUE_SIGNAL`

Frozen failed control: `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` raw MiniMax M2.5 returned `ESCALATE` where local audit target is `ALLOW`.

Provider calls: 2
Tokens: 3651 input / 3060 output / 6711 total

| Call | Packet | Verdict | Binding | Admissible | Failures |
| ---: | --- | --- | --- | --- | --- |
| 1 | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ALLOW` | `EXACT_MATCH_CLOSED` | False | ['packet_a_invented_site_18l'] |
| 2 | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | `DEVICE_GROUP_SITE_MISMATCH` | True | [] |
