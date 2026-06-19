# D1 Findings - Capital Markets

Generated: `2026-06-19T19:45:52Z`

Domain: `capital_markets_trade_shock_execution`

## Decision

Finish current-lock final judging and validity-adjusted rollup before running D2 or making a headline lift claim.

## Bottom Line

D1 is useful now, but it is not a finished public benchmark claim yet. The strongest current-lock fact is operational: HoloFactory completed the frontier D1 generation run and produced the trace/packet structure we need. The weakest current-lock fact is scoring completeness: only `2` parsed final judge scores exist, all on `solo_anthropic`.

## Current-Lock Quality

- Conditions: `4`
- Valid finals: `2`
- Invalid finals: `2`
- Raw observed mean gap: `-0.03`
- Raw observed mean lift: `-0.146%`
- Validity-adjusted observed mean gap: `0.68`
- Validity-adjusted observed mean lift: `8.5%`
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
- D1 current-lock quality scoring is not complete: only the Anthropic solo pair has any parsed judge scores, and only two judges are present.
- The four-judge law changes the score gap: current D1 expects twelve final judge scores, not nine.
- Raw current-lock scores presently show a near tie on the Anthropic pair, but the Anthropic solo final is deterministically invalid for missing the required risk/compliance/audit section.
- Under the proposed deterministic validity cap, the existing Anthropic-pair sample flips from a raw near tie to a Holo advantage; this remains non-claimable until all pairs and judges are scored.
- Historical D1 evidence supports directional Holo lift, but it must be labeled diagnostic because it does not match the current run lock.
- For public or client-facing claims, report raw quality, validity-adjusted quality, and provider reliability as separate scores.

## Next Actions

1. Score the remaining current-lock final judge queue.
2. Regenerate this D1 evidence board after scoring.
3. Only then decide whether D1 is ready to promote from operational evidence to benchmark-credit evidence.
4. Keep D2-D5 packet generation paused until D1 final scoring is closed or explicitly accepted as partial.
