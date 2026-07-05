# HoloVerify Benchmark Story And Stress Matrix Recommendation

Date: 2026-07-05

Callsign: HoloStats

Scope: accounting and claim-safety recommendation only. No providers, Holo live, solo, Gov, or judges were run. No public site files or frozen runtime evidence were edited.

## Plain-English Scoreboard

| Lane | What It Is | Current Status | Public Use |
|---|---|---|---|
| Strict public blind denominator | Clean blind 120-packet denominator, 60 ALLOW / 60 ESCALATE | Holo `120/120`; observed FP `0/60`, observed FN `0/60` | Public-safe narrow benchmark claim |
| Stale / historical results | Older `614` framing and prior internal evidence | Historical only | Do not mix into current public denominator |
| Solo failure / stress discovery | Pairs selected because at least one solo call failed across 3 models x 2 siblings | Useful stress-test inventory | Not a natural population FPR/FNR denominator |
| Holo rescue / internal hardening | Selected failure lanes used to find, patch, and validate architecture behavior | V5 found a miss class; V6 repaired selected lane | Internal engineering evidence only |
| Future design-partner shadow evidence | Real-world or partner shadow decisions under predeclared controls | Future lane | Not public denominator unless separately admitted |
| Future red/green matrix | Visual status board for lane-specific results | Recommended | Dot color must be lane-scoped, not global truth |

## What This Benchmark Measures

The public benchmark currently measures HoloVerify performance on a frozen, balanced, blind 120-packet action-boundary denominator with trace-bound post-hoc scoring and no judge calls during scoring. Its clean public claim is narrow: Holo scored `120/120` on blind-120, with `0/60` observed false positives on ALLOW packets and `0/60` observed false negatives on ESCALATE packets. Wilson and exact upper bounds describe uncertainty around that zero-miss observation; they do not prove the true error rate is zero.

## What It Does Not Measure

The public benchmark does not measure global production reliability, natural-world FPR/FNR, model superiority over all models, or prevalence of failure classes in the wild. The Solo Failure Factory is intentionally stress-selected: pairs enter because at least one solo model failed across six solo opportunities. That makes it valid for adversarial stress testing and architecture hardening, but invalid as a natural population denominator. Internal rescue wins, V6 patch passes, and selected-lane red/green dots must not be merged into blind-120 public FPR/FNR.

## Separate Benchmark Lanes

| Lane | Selection Rule | Denominator Treatment | Good Claim |
|---|---|---|---|
| Strict public blind denominator | Frozen blind packets, balanced truth split, clean runtime controls | Public denominator | "Holo scored 120/120 on blind-120." |
| Solo failure / stress discovery | Selected for at least one solo failure across 3 models x 2 siblings | Stress inventory only | "This discovers failure seams for pressure testing." |
| Holo rescue / internal hardening | Selected from known stress/failure seams | Internal repair evidence | "Architecture patch repaired this selected lane." |
| Design-partner shadow evidence | Future real-world shadow lane under preregistered controls | Separate shadow lane | "Observed shadow evidence under these controls." |

## Recommended Public Metrics Table

Use only the strict public blind-120 denominator.

| Metric | Observed | Exact 95% Upper Bound | Wilson 95% Upper Bound | Public Label |
|---|---:|---:|---:|---|
| Holo packets correct | `120/120` | n/a | n/a | Public-safe |
| ALLOW false positives | `0/60` | `4.870%` | `6.017%` | Public-safe |
| ESCALATE false negatives | `0/60` | `4.870%` | `6.017%` | Public-safe |
| Overall packet misses | `0/120` | `2.466%` | `3.102%` | Public-safe |

Exact bound is one-sided Clopper-Pearson for zero observed misses. Wilson bound uses the 95% Wilson score upper bound used in the Phase 1 roadmap.

## Public Milestones

| Milestone | Clean Balanced Packets | Add From Blind-120 | Wilson 95% Meaning If Zero Misses Continue |
|---|---:|---:|---|
| Current | `60/60 = 120` | 0 | Overall `3.102%`; side-specific `6.017%` |
| Small public checkpoint | `75/75 = 150` | +30 total | Overall `2.497%`; side-specific `4.872%` |
| Recommended next clean milestone | `150/150 = 300` | +180 total | Overall `1.264%`; side-specific `2.497%` |
| Phase 1 target | `381/381 = 762` | +642 total | Side-specific `0.998%`; overall `0.502%` |

Recommendation: use `150/150 = 300` as the next meaningful public-facing milestone if the goal is a better side-specific story. Use `75/75 = 150` only as a near-term progress checkpoint, not as the main Phase 1 proof point.

## Red/Green Matrix Labeling Scheme

| Dot | Label | Meaning | Denominator Effect |
|---|---|---|---|
| Green | `PASS_IN_LANE` | Passed the predeclared lane rule with valid controls | Counts only inside that lane |
| Red | `FAIL_IN_LANE` | Failed the predeclared lane rule with valid controls | Counts only inside that lane |
| Yellow | `QUARANTINE_OR_HELD_OUT` | Packet/key defect, parse/admissibility, or transport/control issue | Excluded from wrong-verdict denominator |
| Gray | `NOT_RUN_OR_PREFLIGHT_ONLY` | Built or planned but no valid live/scored run | No denominator credit |

Recommended matrix columns:

| Column | Values |
|---|---|
| Lane | `PUBLIC_BLIND`, `SOLO_STRESS`, `INTERNAL_RESCUE`, `SHADOW_PARTNER` |
| Selection type | `blind`, `stress-selected`, `known-failure`, `shadow-real-world` |
| Result dot | `green`, `red`, `yellow`, `gray` |
| Packet count | Count only the packets eligible for that lane |
| Pair count | Count only complete eligible pairs |
| Claim class | `public denominator`, `internal stress`, `internal hardening`, `shadow evidence` |
| Public copy allowed | `yes`, `limited`, `no` |

## Forbidden Language

- Do not claim global FPR/FNR from selected solo-failure cases.
- Do not claim "Holo beats all models."
- Do not mix blind-120 with old `614`.
- Do not claim stress-selected packets represent natural-world prevalence.
- Do not treat internal rescue wins as public denominator evidence.
- Do not count parse/admissibility held-out or packet-key quarantine lanes as wrong-verdict denominators.
- Do not call red/green stress matrix totals a public reliability rate unless the lane was predeclared as a public denominator.

## Source Map

- `docs/benchmark/HOLOVERIFY_LIVING_SEAM_ATLAS_AND_ARCHITECTURE_LEDGER_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_BATCH001_012_POSTHOC_SCORE_CHECKPOINT_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_MASTER_SCOREBOARD_2026_07_04.json`
- `docs/benchmark/HOLOVERIFY_V6_BROADER_VALIDATION_PLAN_2026_07_05.json`
