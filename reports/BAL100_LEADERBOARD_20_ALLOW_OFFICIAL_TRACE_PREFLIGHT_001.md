# BAL100 Leaderboard 20 ALLOW Official Trace Preflight

Created: 2026-06-19T20:48:07Z

Status: `PASS`

Mode: `official_trace_preflight_no_live_no_judge_no_scorecard`

## Scope

| Packet | Hash8 | Frozen Path | Frozen Approval |
| --- | --- | --- | --- |
| BAL100-HARD-ALLOW-HAB-001-ALLOW | `85fb8dca` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-001-ALLOW_85fb8dca.json` | Taylor |
| BAL100-HARD-ALLOW-HAB-003-ALLOW | `673d6c1b` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-003-ALLOW_673d6c1b.json` | Taylor |
| BAL100-HARD-ALLOW-HAB-004-ALLOW | `489e7143` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-004-ALLOW_489e7143.json` | Taylor |
| BAL100-HARD-ALLOW-HAB-005-ALLOW | `7f6d94c4` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-005-ALLOW_7f6d94c4.json` | Taylor |
| BAL100-HARD-ALLOW-HAB-006-ALLOW | `11f7a12b` | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-006-ALLOW_11f7a12b.json` | Taylor |

## Expected Future Live Shape

- Packets: 5
- ALLOW packets: 5
- ESCALATE packets: 0
- Prompt-card templates: 20
- Active non-Gov prompt cards: 15
- HoloGov template cards: 5
- Expected future provider rows: 20
- Expected future official trace records: 5

## Approval Contract

- `BAL100_LEADERBOARD20_ALLOW_TRACE_APPROVED=I_APPROVE_OFFICIAL_TRACE_PROVIDER_TRANSMISSION`
- `BAL100_LEADERBOARD20_CODEX_ALLOW_TRACE_APPROVED=I_APPROVE_CODEX_OFFICIAL_TRACE_PROVIDER_TRANSMISSION`
- Scope: exact five frozen BAL100 hard-ALLOW packets listed in this manifest only

## Future Live Command Shape

```bash
export BAL100_LEADERBOARD20_ALLOW_TRACE_APPROVED="I_APPROVE_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
export BAL100_LEADERBOARD20_CODEX_ALLOW_TRACE_APPROVED="I_APPROVE_CODEX_OFFICIAL_TRACE_PROVIDER_TRANSMISSION"
python3 -B benchmark_factory/batches/run_BAL100_leaderboard_20_allow_official_trace.py \
  --execute-provider-calls \
  --operator Taylor \
  --allow-codex-provider-calls \
  --yes-send-frozen-payloads-to-providers \
  --out-dir scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_<timestamp>
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

Next gate: After Taylor approves the exact live official trace command, run provider execution for these five frozen packets only; Judge and leaderboard remain separate later gates.
