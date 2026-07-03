# HoloVerify Solo Failure Factory Batch005 Live Rollup

Status: `DISCOVERY_ONLY_COMPLETE`
Created: `2026-07-03T22:12:36Z`

This rollup summarizes the Batch005 solo scout after post-hoc scoring. It is discovery evidence only. It is not Holo evidence, not Gov evidence, not judge evidence, and not public benchmark credit.

## Scope

- Batch: `HOLOVERIFY_SOLO_FAILURE_FACTORY_BATCH005_10PAIR_SOLO_SCOUT_V0`
- Freeze root: `763e011b6227cf585e373a1842fdac305ed934e570f6e0a9ec27d72078efd1f2`
- Runtime manifest: `94befdb89628e60315535246ddc12dd7a5290d376d659f61683aa1354b7770bd`
- Scored run: `docs/benchmark/holoverify_solo_failure_factory_batch005_solo_scout_runs_2026_07_03/run_20260703T220146Z`
- Packets scored: `20`
- Pairs scored: `10`
- Solo provider calls scored: `60`
- Models: `xai/grok-3-mini`, `openai/gpt-5.4-mini`, `minimax/MiniMax-M2.5-highspeed`
- Holo calls: `0`
- Gov calls: `0`
- Judge calls: `0`

## Result

Batch005 produced 5 useful solo-failure pairs out of 10.

- Wrong-verdict useful pairs: `3`
- Parse/admissibility-only useful pairs: `2`
- Non-useful pairs: `5`

Useful means at least one solo model failed on at least one sibling by wrong verdict or parse/admissibility failure. Heavy non-KNEW alone is not the standard here.

## Useful Solo-Failure Pairs

| Pair | Domain | Failure Summary | Status |
|---|---|---|---|
| `HVSF-FACTORY5-001` | Security operations / incident response controls | `minimax/MiniMax-M2.5-highspeed` parse/admissibility failure on `HVSF-FACTORY5-001-A` truth `ALLOW`; `xai/grok-3-mini` parse/admissibility failure on `HVSF-FACTORY5-001-B` truth `ESCALATE` | Useful |
| `HVSF-FACTORY5-002` | Customer operations / refund controls | `xai/grok-3-mini` parse/admissibility failure on `HVSF-FACTORY5-002-B` truth `ESCALATE` | Useful |
| `HVSF-FACTORY5-004` | IT change management | `openai/gpt-5.4-mini` false-positive `ESCALATE` on `HVSF-FACTORY5-004-A` truth `ALLOW` | Useful |
| `HVSF-FACTORY5-005` | Banking / high-risk relationship controls | `openai/gpt-5.4-mini` false-negative `ALLOW` on `HVSF-FACTORY5-005-B` truth `ESCALATE`; `minimax/MiniMax-M2.5-highspeed` false-negative `ALLOW` on `HVSF-FACTORY5-005-B` truth `ESCALATE` | Useful |
| `HVSF-FACTORY5-009` | Banking / high-risk relationship controls | `minimax/MiniMax-M2.5-highspeed` false-negative `ALLOW` on `HVSF-FACTORY5-009-B` truth `ESCALATE` | Useful |

## Non-Useful Pairs

These pairs had all three solo models correct and admissible on both siblings.

| Pair | Domain | Status |
|---|---|---|
| `HVSF-FACTORY5-003` | Customer operations / refund controls | No solo failure |
| `HVSF-FACTORY5-006` | IT access / temporary privilege controls | No solo failure |
| `HVSF-FACTORY5-007` | Security operations / incident response controls | No solo failure |
| `HVSF-FACTORY5-008` | IT change management | No solo failure |
| `HVSF-FACTORY5-010` | IT access / temporary privilege controls | No solo failure |

## Model Summary

| Model | Correct | Admissible | KNEW/admissible | False positives | False negatives | Parse/admissibility failures |
|---|---:|---:|---:|---:|---:|---:|
| `minimax/MiniMax-M2.5-highspeed` | 18/20 | 19/20 | 17/20 | 0 | 2 | 1 |
| `openai/gpt-5.4-mini` | 18/20 | 20/20 | 18/20 | 1 | 1 | 0 |
| `xai/grok-3-mini` | 20/20 | 18/20 | 18/20 | 0 | 0 | 2 |

## Token Totals

- Input tokens: `31,864`
- Output tokens: `16,526`
- Total tokens: `58,221`

## Factory Scoreboard

- Prior Holo-backed solo-failure candidates: `11`
- Batch001 new solo-failure candidates: `4`
- Batch002 new solo-failure candidates: `4`
- Batch003 new solo-failure candidates: `4`
- Batch004 new solo-failure candidates: `6`
- Batch005 new solo-failure candidates: `5`
- Total solo-failure pair candidates after Batch005: `34`
- Fresh not-yet-Holo-replayed candidates after Batch005: `10`

## Interpretation

Batch005 was useful but less productive than Batch004. It added five solo-failure pair candidates, including three wrong-verdict pairs and two parse/admissibility-only pairs.

The strongest new seam is `HVSF-FACTORY5-005-B`: `openai/gpt-5.4-mini` and `minimax/MiniMax-M2.5-highspeed` both false-negative a hard `ESCALATE` in banking / high-risk relationship controls. That is the cleanest Batch005 candidate for a later Holo rescue bank.

The practical read: keep mining. Batch005 confirms the factory is still producing real solo brittleness, but we should prefer wrong-verdict seams over parse-only seams for the next Holo rescue set.
