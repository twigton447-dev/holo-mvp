# HoloVerify Gemini Wave 1 Matrix Visual Brief

Date: 2026-07-06

Callsign: HoloStats

Scope: Gemini-ready visual matrix data package for Wave 1 stress-matrix evidence. This package was created from repo-backed artifacts only. No providers, Holo live, solo, Gov live, or judges were run.

## Summary Totals

| Metric | Value |
|---|---:|
| Pairs | 20 |
| Packets | 40 |
| Solo calls | 120 |
| Green dots | 90 |
| Red dots | 30 |
| False positives | 23 |
| False negatives | 0 |
| Parse/admissibility failures | 7 |
| Pairs with at least one red | 16/20 |
| Wrong-verdict pairs | 13 |
| Parse-only holdouts | 3 |

## Domain Breakdown

| Domain | Pairs | Calls | Green | Red | FP | FN | Parse/admissibility |
|---|---:|---:|---:|---:|---:|---:|---:|
| Banking, KYC & Risk | 3 | 18 | 14 | 4 | 3 | 0 | 1 |
| Clinical & Regulated Activation | 1 | 6 | 5 | 1 | 1 | 0 | 0 |
| Legal, Privacy & Regulatory | 5 | 30 | 23 | 7 | 7 | 0 | 0 |
| Operations, Insurance & Industrial | 4 | 24 | 18 | 6 | 4 | 0 | 2 |
| Public Sector, Benefits & Grants | 7 | 42 | 30 | 12 | 8 | 0 | 4 |

## Dot Matrix Legend

- Green: KNEW/admissible solo answer.
- Red: failed solo attempt, either wrong verdict or parse/admissibility failure.
- ALLOW row order: xAI, OpenAI, MiniMax.
- ESCALATE row order: xAI, OpenAI, MiniMax.

## Actual Wave 1 Pair Matrix

| Pair | Domain | ALLOW dots | ESCALATE dots | Red count |
|---|---|---|---|---:|
| HVSM-W1-001 | Public Sector, Benefits & Grants | G R G | G G G | 1 |
| HVSM-W1-002 | Public Sector, Benefits & Grants | G R R | G G G | 2 |
| HVSM-W1-003 | Public Sector, Benefits & Grants | G R G | G G G | 1 |
| HVSM-W1-004 | Public Sector, Benefits & Grants | G R G | G G G | 1 |
| HVSM-W1-005 | Public Sector, Benefits & Grants | R R R | G G G | 3 |
| HVSM-W1-006 | Public Sector, Benefits & Grants | G G R | G G G | 1 |
| HVSM-W1-007 | Public Sector, Benefits & Grants | R R R | G G G | 3 |
| HVSM-W1-008 | Legal, Privacy & Regulatory | G R G | G G G | 1 |
| HVSM-W1-009 | Legal, Privacy & Regulatory | R G R | G G G | 2 |
| HVSM-W1-010 | Legal, Privacy & Regulatory | G G G | G G G | 0 |
| HVSM-W1-011 | Legal, Privacy & Regulatory | R R R | G G G | 3 |
| HVSM-W1-012 | Legal, Privacy & Regulatory | G G R | G G G | 1 |
| HVSM-W1-013 | Operations, Insurance & Industrial | R R R | G G G | 3 |
| HVSM-W1-014 | Operations, Insurance & Industrial | R R R | G G G | 3 |
| HVSM-W1-015 | Operations, Insurance & Industrial | G G G | G G G | 0 |
| HVSM-W1-016 | Operations, Insurance & Industrial | G G G | G G G | 0 |
| HVSM-W1-017 | Banking, KYC & Risk | G G G | G G G | 0 |
| HVSM-W1-018 | Banking, KYC & Risk | G G R | G G G | 1 |
| HVSM-W1-019 | Banking, KYC & Risk | R R R | G G G | 3 |
| HVSM-W1-020 | Clinical & Regulated Activation | G R G | G G G | 1 |

## Top 5 Holo Rescue Subset

Selected pairs: `HVSM-W1-005`, `HVSM-W1-009`, `HVSM-W1-011`, `HVSM-W1-013`, `HVSM-W1-019`.

Actual Holo result: 7/10 packets correct and 2/5 pairs correct. Failed ALLOW packets: `HVSM-W1-009-A`, `HVSM-W1-011-A`, `HVSM-W1-019-A`.

This is failed internal evidence, not a Holo win.

## V7 Status

V7 is hardened and committed. The tiny preflight is ready with expected 30 calls. Live validation was blocked by policy before provider calls, so actual calls were 0 and no V7 live result exists.

## Gemini Visual Instructions

1. First frame: render the actual solo matrix with the red/green dots in the JSON package.
2. Zoom into a 6-dot pair block to show ALLOW x3 and ESCALATE x3.
3. Use a red-to-green coverage sweep only as a transition concept.
4. Label that transition exactly: `coverage concept / intended Holo repair state`.
5. Keep the actual Holo Top 5 failed result visually separate from the concept animation.

## Claim Boundary

- Internal stress-matrix evidence only.
- Public denominator remains blind-120 only.
- No global FPR/FNR claim.
- No production-rate claim.
- No Holo win claim from Wave 1 Top 5.
- No V7 live result exists.

## Source Artifacts

- `docs/benchmark/HOLOVERIFY_STRESS_MATRIX_EXPANSION_WAVE1_SOLO_ROLLUP_2026_07_05.json`
- `docs/benchmark/holoverify_stress_matrix_expansion_wave1_solo_scout_runs_2026_07_05/run_20260705T215904Z/stress_matrix_wave1_solo_posthoc_score.json`
- `docs/benchmark/HOLOVERIFY_LIVING_SEAM_ATLAS_AND_ARCHITECTURE_LEDGER_2026_07_05.json`
- `docs/benchmark/stress_matrix_mockup_2026_07_05/wave1_red_to_green_transition.html`
