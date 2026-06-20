# BAL100 Leaderboard 20 ALLOW Replacement Drafts

Status: `PASS`
Created: 2026-06-19T21:03:13Z
Mode: `no_live_replacement_draft_generation_and_static_lint`

## Scope

- Replaces failed hard-ALLOW candidates: `HAB-004`, `HAB-005`, `HAB-006`
- Replacement drafts: 3
- Live calls: none
- Freeze: none
- Judge: none
- Scorecard / leaderboard movement: none

## Drafts

| Packet | Domain | Lint | Visibility | Contamination | Hash8 | Path |
|---|---|---|---|---|---|---|
| `BAL100-HARD-ALLOW-REP-001-ALLOW` | BEC | PASS | PASS | PASS | `9706a499` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-001-ALLOW_draft_v0_1.json` |
| `BAL100-HARD-ALLOW-REP-002-ALLOW` | IAM | PASS | PASS | PASS | `999d2812` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-002-ALLOW_draft_v0_1.json` |
| `BAL100-HARD-ALLOW-REP-003-ALLOW` | AP | PASS | PASS | PASS | `c8566512` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-003-ALLOW_draft_v0_1.json` |

## Validation

- All HB lint pass: True
- All payload visibility pass: True
- All contamination audits pass: True
- All ready for freeze-manifest preflight: True
- Failures: none

## Safe Boundaries

No provider calls, freeze, official trace, Judge, QA, ablation, scorecard movement, leaderboard update, packet promotion, proof-credit status change, or push were performed.

## Next Gate

Taylor can approve freeze-manifest preflight for the three exact replacement draft paths, or approve Judge for the two strict-pass traced packets as a separate gate.
