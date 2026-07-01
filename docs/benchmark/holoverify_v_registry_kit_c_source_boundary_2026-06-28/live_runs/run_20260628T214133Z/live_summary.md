# HoloVerify-V Kit C Registry Candidate Generation

Classification: `REGISTRY_CANDIDATE_GENERATION_COMPLETE`
Post-generation status: `diagnostic_or_repair_required`
Benchmark locked: `False`
Pre-run root signature: `f629ab33e58ab410`
Trace hash: `3c72135f69ddee82`

## Calls

Provider calls: 8 / 8
Worker calls: 0
Judge calls: 0

## Token Totals

| Lane | Input | Output | Total |
| --- | ---: | ---: | ---: |
| `solo` | 3836 | 2813 | 6649 |
| `holo` | 7453 | 6342 | 13795 |

## Rows

| Call | Lane | Pair | Packet | Verdict | Admissible | Failures |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `solo` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | `ESCALATE` | False | ['local_audit_target_expected_ALLOW'] |
| 2 | `holo` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | `ALLOW` | True | [] |
| 3 | `solo` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | `ESCALATE` | False | ['invented_or_non_doc_source:INV-OVX-2026-7021'] |
| 4 | `holo` | `HV-KITC-021` | `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | `ESCALATE` | True | [] |
| 5 | `solo` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ESCALATE` | False | ['local_audit_target_expected_ALLOW', 'packet_022a_missing_site_18p'] |
| 6 | `holo` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ALLOW` | True | [] |
| 7 | `solo` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | True | [] |
| 8 | `holo` | `HV-KITC-022` | `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | True | [] |
