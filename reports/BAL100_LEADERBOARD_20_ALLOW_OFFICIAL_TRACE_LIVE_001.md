# BAL100 Leaderboard 20 ALLOW Official Trace Live Result

Status: `COMPLETE_NEEDS_TRIAGE`
Created: 2026-06-19T20:56:00Z
Run directory: `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_20260619T205143Z`

## Scope

- Packets: 5 frozen hard-ALLOW packets
- Provider rows: 20/20 completed
- Parse: 20/20 OK
- Provider errors: 0
- Official trace records: 5
- Prompt cards: 20

## Boundaries

- Official trace: true
- Judge: false
- QA/ablation: false
- Freeze: false
- Benchmark credit: false
- Scorecard movement: false
- Leaderboard movement: false
- Proof credit remains unchanged: true

## Verdict Summary

| Metric | Count |
|---|---:|
| Total ALLOW verdict rows | 12 |
| Total ESCALATE verdict rows | 8 |
| Active non-Gov ALLOW rows | 10 |
| Active non-Gov ESCALATE rows | 5 |
| HoloGov ALLOW rows | 2 |
| HoloGov ESCALATE rows | 3 |
| Strict all-ALLOW packet candidates | 2 |
| Packets needing repair or replacement | 3 |

## Packet Results

| Packet | Hash8 | Verdict Rows | HoloGov | Status |
|---|---|---:|---|---|
| `BAL100-HARD-ALLOW-HAB-001-ALLOW` | `85fb8dca` | 4 ALLOW / 0 ESCALATE | ALLOW | STRICT_PASS_CANDIDATE |
| `BAL100-HARD-ALLOW-HAB-003-ALLOW` | `673d6c1b` | 4 ALLOW / 0 ESCALATE | ALLOW | STRICT_PASS_CANDIDATE |
| `BAL100-HARD-ALLOW-HAB-004-ALLOW` | `489e7143` | 1 ALLOW / 3 ESCALATE | ESCALATE | REPAIR_OR_REPLACE_BEFORE_LEADERBOARD |
| `BAL100-HARD-ALLOW-HAB-005-ALLOW` | `7f6d94c4` | 1 ALLOW / 3 ESCALATE | ESCALATE | REPAIR_OR_REPLACE_BEFORE_LEADERBOARD |
| `BAL100-HARD-ALLOW-HAB-006-ALLOW` | `11f7a12b` | 2 ALLOW / 2 ESCALATE | ESCALATE | REPAIR_OR_REPLACE_BEFORE_LEADERBOARD |

## Failure Themes

- `HAB-004`: false escalations centered on variance threshold / invoice amount variance.
- `HAB-005`: false escalations centered on banking detail change and dormant vendor reactivation justification.
- `HAB-006`: false escalations centered on missing VP Finance review.

## Recommendation

Do not move all five packets to scorecard or leaderboard. `HAB-001` and `HAB-003` are strict-pass candidates for a later Judge gate if Taylor approves that exact next stage. `HAB-004`, `HAB-005`, and `HAB-006` should be repaired or replaced before leaderboard movement.

Next approval required: explicit Taylor approval for any Judge, scorecard update, leaderboard update, repair live call, or push.
