# BAL100 Leaderboard 20 ALLOW Migrated Drafts

Status: PASS
Created: 2026-06-19T20:05:47Z
Ticket: `BAL100-LEADERBOARD-20-ALLOW-BALANCE-001`
Mode: no-live migrated draft generation and static lint

## Drafts

| Candidate | Scenario ID | Domain | Lint | Visibility | Contamination | Hash8 | Draft Path |
|---|---|---|---|---|---|---|---|
| `HAB-001_v5` | `BAL100-HARD-ALLOW-HAB-001-ALLOW` | BEC | PASS | PASS | PASS | `85fb8dca` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-001-ALLOW_draft_v0_1.json` |
| `HAB-003_v2` | `BAL100-HARD-ALLOW-HAB-003-ALLOW` | IAM | PASS | PASS | PASS | `673d6c1b` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-003-ALLOW_draft_v0_1.json` |
| `HAB-004_v1` | `BAL100-HARD-ALLOW-HAB-004-ALLOW` | AP | PASS | PASS | PASS | `489e7143` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-004-ALLOW_draft_v0_1.json` |
| `HAB-005_v1` | `BAL100-HARD-ALLOW-HAB-005-ALLOW` | BEC | PASS | PASS | PASS | `7f6d94c4` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-005-ALLOW_draft_v0_1.json` |
| `HAB-006_v1` | `BAL100-HARD-ALLOW-HAB-006-ALLOW` | AP | PASS | PASS | PASS | `11f7a12b` | `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-006-ALLOW_draft_v0_1.json` |

## Validation

- Draft count: 5
- All HB lint pass: True
- All payload visibility pass: True
- All contamination audit pass: True
- All ready for freeze-manifest preflight: True
- Failures: none

## Next Step

If Taylor approves static preflight only, run freeze-manifest on these exact five draft paths and stop before freeze.

## Safe Boundaries

No provider calls, freeze, Judge, official trace, QA, ablation, scorecard movement, leaderboard update, packet promotion, proof-credit status change, or push were authorized or performed.
