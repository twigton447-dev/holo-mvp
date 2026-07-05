# Blind Canary Invalidity Audit

Classification: `INVALID_RUN_CONTENT_CONTRACT_FAILURE_AFTER_SUCCESSFUL_TRANSPORT`

## Bottom Line

The live canary is preserved but not score-valid. Provider transport completed 100/100 calls with no provider failures, and the trace was frozen before post-hoc scoring. However, the live model outputs did not satisfy the locked worker/Gov output contracts.

This is not a valid Holo quality result. The post-hoc `0/20` row is a schema artifact: every final verdict was `UNKNOWN`, not a substantive ALLOW/ESCALATE decision.

## Key Counts

- Provider calls: `100` / `100`
- Provider failures: `0`
- Transport recovered calls: `0`
- TRACE_CALLS rows: `100`
- TRACE_PROVIDER_CALLS rows: `100`
- Worker outputs with `verification_verdict=`: `0` / `60`
- Post-hoc final verdict distribution: `{'UNKNOWN': 20}`
- Truth distribution: `{'ESCALATE': 10, 'ALLOW': 10}`

## Root Failure

The blind worker prompt said to return compact key=value output, but did not force the exact locked schema strongly enough. Workers returned keys like `boundary_closed=false`, `decision=proceed`, or other non-contract forms. Gov also returned non-contract/prose/incomplete baton text, with many `finish_reason=length` rows.

## Required Patch Before Any Rerun

- Fail closed on missing `verification_verdict`.
- Fail closed on Gov `finish_reason=length`.
- Make the live worker prompt require the exact compact schema.
- Make the live Gov prompt require compact baton only, no prose.

No rerun, public claim, or error-rate claim is licensed by this run.
