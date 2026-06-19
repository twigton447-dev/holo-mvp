# D1 Findings - Capital Markets

Generated: `2026-06-19T21:41:42Z`

Domain: `capital_markets_trade_shock_execution`

## Decision

D1 current-lock frontier scoring is now outside-DNA scored locally; keep D1 out of public benchmark-credit promotion until score provenance is committed and mini/order/domain replication is run.

## Bottom Line

D1 is useful now, and its current-lock frontier lane has outside-DNA final scoring on disk. It is still not a finished public benchmark claim: D1 is one domain and the broader architecture proof still needs matched mini results, order permutations, and D2-D5 replication. Current D1 has `6` outside-DNA proof-credit candidate rows and `2` same-DNA diagnostic rows.

## Current-Lock Quality

- Conditions: `4`
- Valid finals: `2`
- Invalid finals: `2`
- Raw observed mean gap: `1.095`
- Raw observed mean lift: `18.306%`
- Validity-adjusted observed mean gap: `1.37`
- Validity-adjusted observed mean lift: `21.489%`
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
- Raw current-lock proof-credit scores show Holo lift across five of six outside-DNA judge rows, with one negative Anthropic-pair xAI row.
- Validity-adjusted scoring preserves raw judge scores and applies deterministic caps only when revalidation flagged invalid finals.
- Historical D1 evidence supports directional Holo lift, but it must be labeled diagnostic because it does not match the current run lock.
- For public or client-facing claims, D1 alone is still insufficient: the architecture claim needs the mini lane, order permutations, and D2-D5 replication.

## Next Actions

1. Commit the D1 proof-credit scoring board and boundary-accounting patch.
2. Preserve the raw outside-DNA judge artifacts and parse-failure provenance for audit.
3. Keep same-DNA frontier judge rows diagnostic-only even if additional legacy-panel scores are added.
4. Run the matched mini Holo versus mini solo lane for D1.
5. Then run order permutations and D2-D5 replication before making the architecture-level lift claim.
