# BAL100 Leaderboard 20 ALLOW Replacement Official Trace Preflight

Created: 2026-06-19T21:54:05Z

Status: `PASS`

Mode: `official_trace_preflight_no_live_no_judge_no_scorecard`

## Scope

| Packet | Hash8 | Frozen Path | Frozen Approval |
| --- | --- | --- | --- |
| BAL100-HARD-ALLOW-REP-001-ALLOW | `9706a499` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-001-ALLOW_9706a499.json` | Taylor |
| BAL100-HARD-ALLOW-REP-002-ALLOW | `999d2812` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-002-ALLOW_999d2812.json` | Taylor |
| BAL100-HARD-ALLOW-REP-003-ALLOW | `c8566512` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-003-ALLOW_c8566512.json` | Taylor |

## Expected Future Live Shape

- Packets: 3
- ALLOW packets: 3
- ESCALATE packets: 0
- Prompt-card templates: 12
- Active non-Gov prompt cards: 9
- HoloGov template cards: 3
- Expected future provider rows: 12
- Expected future official trace records: 3

## Approval Contract

- `BAL100_LEADERBOARD20_REPLACEMENT_ALLOW_TRACE_APPROVED=I_APPROVE_REPLACEMENT_ALLOW_OFFICIAL_TRACE_PROVIDER_TRANSMISSION`
- `BAL100_LEADERBOARD20_CODEX_REPLACEMENT_ALLOW_TRACE_APPROVED=I_APPROVE_CODEX_REPLACEMENT_ALLOW_OFFICIAL_TRACE_PROVIDER_TRANSMISSION`
- Scope: exact three frozen replacement BAL100 hard-ALLOW packets listed in this manifest only

## Future Live Command Shape

```bash
export BAL100_LEADERBOARD20_REPLACEMENT_ALLOW_TRACE_APPROVED="I_APPROVE_REPLACEMENT_ALLOW_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
export BAL100_LEADERBOARD20_CODEX_REPLACEMENT_ALLOW_TRACE_APPROVED="I_APPROVE_CODEX_REPLACEMENT_ALLOW_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
python3 -B benchmark_factory/batches/run_BAL100_leaderboard_20_allow_replacement_official_trace.py \
  --execute-provider-calls \
  --operator Taylor \
  --allow-codex-provider-calls \
  --yes-send-frozen-payloads-to-providers \
  --out-dir scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_<timestamp>
```

## Validation

- Failure count: 0
- Exact packet count: True
- All frozen approved by Taylor: True
- All model-visible packet keys are action/context: True

## Boundaries

- No provider calls.
- No official trace records written.
- No Judge.
- No QA or ablation.
- No scorecard or leaderboard movement.
- No push.

Next gate: After Taylor approves the exact replacement live official trace command, run provider execution for these three frozen packets only; Judge and leaderboard remain separate later gates.
