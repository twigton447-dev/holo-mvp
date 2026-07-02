# Fable Confound Review Handoff

Status: READ_ONLY_REVIEW_HANDOFF

Date: 2026-07-02

## Role Split

Codex executed the repo-local audit because this is trace and code work.

Fable should act as an adversarial reviewer, not as an evidence mutator.

## Files To Review

- `docs/benchmark/FABLE_ORACLE_INFLUENCE_CENSUS_2026_07_02.md`
- `docs/benchmark/FABLE_ORACLE_INFLUENCE_CENSUS_2026_07_02.json`
- `docs/benchmark/FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.md`
- `docs/benchmark/FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.json`
- `docs/benchmark/FABLE_RUN_FUNNEL_RECONCILIATION_2026_07_02.csv`
- `docs/benchmark/HOLOVERIFY_BLIND_GATE_REPLICATION_SPEC_2026_07_02.md`
- `docs/benchmark/HOLOVERIFY_BLIND_GATE_REPLICATION_SPEC_2026_07_02.json`
- `docs/benchmark/FABLE_BLIND_LANE_DISCONFIRMATION_BATTERY_2026_07_02.md`
- `docs/benchmark/audit_holoverify_oracle_confounds_2026_07_02.py`

## Review Questions

1. Does the audit correctly identify every truth-conditioned runtime path?
2. Are any truth-conditioned paths missed because they use different wording?
3. Does the run funnel distinguish invalid traces, complete traces, and included public evidence cleanly enough?
4. Is the blind-gate replication spec strict enough to prevent reward hacking?
5. What no-provider fixtures should be added before any live blind-gate canary?
6. Does the updated spec faithfully incorporate T1-T7 from the disconfirmation battery?

## Hard Boundaries

Fable must not:

- edit frozen evidence
- run providers
- run judges
- change packet truths
- change prompt payloads
- reclassify invalid runs as successful
- publish new public claims

Fable may:

- review code and reports
- propose patches
- identify additional confounds
- design no-provider fixtures
- recommend the minimum blind-gate replication canary
