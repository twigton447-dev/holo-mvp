# D1 Findings - Capital Markets

Generated: `2026-06-19T22:08:04Z`

Domain: `capital_markets_trade_shock_execution`

## Decision

D1 current-lock frontier scoring is now outside-DNA scored locally; keep D1 out of public benchmark-credit promotion until score provenance is committed and mini/order/domain replication is run.

## Bottom Line

D1 is useful now, and its current-lock frontier lane has outside-DNA final scoring on disk. It is still not a finished public benchmark claim: D1 is one domain, two solo baselines carry validity flags, and xAI judge rows show high variance that must be retested. Current D1 has `6` outside-DNA proof-credit candidate rows, of which `1` are currently primary-clean metric rows after quarantine.

## Current-Lock Quality

- Conditions: `4`
- Valid finals: `2`
- Invalid finals: `2`
- Primary-clean rows: `1`
- Primary-clean mean lift: `29.874%`
- Raw audit mean lift, all proof-credit rows: `24.457%`
- Raw audit median lift, all proof-credit rows: `27.303%`
- Quarantined rows: `5`
- Outlier rows: `2`
- Validity-adjusted primary-clean mean lift: `29.874%`
- Proof-credit final judge scores observed: `6 / 6`
- Claimable now: `false`

## Invalid Finals

| condition | provider_model | flags |
| --- | --- | --- |
| solo_anthropic | anthropic:claude-opus-4-8 | missing_required_section:risk compliance and audit controls |
| solo_google | google:gemini-3.1-pro-preview | word_count_out_of_band:3798 |

## Token And Latency

- Holo tokens: `298740`
- Mean solo tokens: `92996.0`
- Holo vs mean solo token multiple: `3.212x`
- Run total tokens: `577728`
- Run latency: `31.585` minutes

## Findings

- D1 generation is operationally real: the current HoloFactory frontier run completed all four generation conditions and produced judge packets.
- D1 current-lock final scoring now has six outside-DNA blind solo judge rows across the three final pairwise packets.
- Same-DNA frontier judge rows remain diagnostic-only and are separated from the proof-credit outside-DNA rows.
- Raw current-lock proof-credit scores show Holo lift across five of six outside-DNA judge rows, but xAI produced both a negative outlier and a high positive outlier and is quarantined from the primary clean metric pending retest.
- Validity-adjusted scoring preserves raw judge scores and applies deterministic caps only when revalidation flagged invalid finals.
- Current-lock mini proof is not present yet; older mini/error attempts are excluded from this D1 analytics board.
- For public or client-facing claims, D1 alone is still insufficient: the architecture claim needs the mini lane, order permutations, and D2-D5 replication.

## Next Actions

1. Preserve the raw outside-DNA judge artifacts and parse-failure provenance for audit.
2. Keep invalid-baseline rows, same-DNA rows, and high-variance/outlier judge-family rows out of the primary clean metric.
3. Retest quarantined rows with additional outside-DNA judges before using them in any headline.
4. Repair or rerun invalid solo baselines under the current lock.
5. Run the matched mini Holo versus mini solo lane for D1.
6. Then run order permutations and D2-D5 replication before making the architecture-level lift claim.
