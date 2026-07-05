# HoloVerify Evidence Cartographer Matrix Memo

Date: 2026-07-05
Callsign: Evidence Cartographer
Scope: file-backed evidence map only; no providers, live runs, judges, Gov, staging, commit, or push.

## What we are measuring

Three things only:

1. **Analysis:** whether a model can read the packet and return a KNEW/admissible, source-grounded result before any real-world execution.
2. **Boundary judgment:** whether the final action decision is `ALLOW` or `ESCALATE` against the frozen truth label.
3. **Seam failure:** whether at least one solo opportunity in the comparison cell failed by wrong final action or format/admissibility failure.

Repo evidence already separates these layers. The blind-120 Holo lane is `120/120` correct across `60` ALLOW and `60` ESCALATE packets. The same-model solo one-shot lane produced `346/360` KNEW/admissible calls and `14` failures affecting `11` packets. That solo result is useful for seam localization, not for a blended headline accuracy claim.

## What we are not measuring

This matrix is not a single aggregate accuracy scoreboard. It is not the public FPR/FNR denominator. It does not combine the old `614` historical/internal material with blind-120. It does not turn Solo Failure Factory, V5/V6 repair lanes, packet mining, or ablation targets into public-rate evidence. It also does not say solos are always bad; green cells stay green unless a measurable seam failure occurred.

## Matrix design

Use one cell per sibling pair when both siblings are available; otherwise use one packet cell and mark the pair as incomplete. Each pair cell contains six solo dots: `xai`, `openai`, and `minimax` on the ALLOW sibling, plus the same three models on the ESCALATE sibling. The cell also carries Holo coverage as metadata, not as a fourth measurement category and not as part of the solo-dot color.

Recommended visual rules:

| Marker | Cell content | Meaning |
| --- | --- | --- |
| Analysis | green dot | Solo returned the right verdict in admissible, source-grounded form. |
| Boundary judgment | red `W` dot | Solo final action was wrong: false ALLOW or false ESCALATE. |
| Seam failure | red `F` dot | Solo verdict may be right, but final output failed parse/source/evidence/admissibility checks. |
| Holo coverage | `H0`, `H1`, or `HX` | Holo not run, Holo covered the cell, or Holo failed/quarantined; never blend this into solo accuracy. |

Short legend: red matters because a single action-boundary miss can release or block a payment, approve the wrong procurement or vendor-master change, activate a clinical workflow without the required source closure, grant or deny security access, or mishandle legal/regulatory authority. Red means "do not hide this behind average performance."

## Red cell rule

A pair or packet cell is red only if at least one solo dot has a seam failure:

- wrong final action: `FALSE_POSITIVE_ESCALATE_ON_ALLOW` or `FALSE_NEGATIVE_ALLOW_ON_ESCALATE`;
- format/admissibility failure: parse, required-field, source, evidence, or deterministic-gate failure;
- quarantine: packet/key defect, shown separately as gray and excluded from clean claims.

Do not shade a cell red because the domain is high-risk, the prompt is hard, the old `614` stack had a result, or Holo succeeded. Red is earned only by a file-backed solo failure row.

## Six-dot rule

The six-dot pair cell is the measurable unit for seam localization: three solo models across both siblings. If exact sibling rows are missing, render no full six-dot cell. Use an incomplete packet cell instead and label the exact missing source.

For blind-120 today, the filter artifact names `11` ALLOW-side packets with at least one solo failure and validates that the other `109` packets had zero solo failures. That is enough to mark known red packet cells. It is not enough, by itself, to render every pair's six explicit dot values from raw source rows because the referenced solo score trace is absent from this checkout.

## Evidence status: what is known vs what needs extraction

Known from repo files:

- Blind-120 Holo result: `120` packets, `60/60` truth split, `120/120` correct, `0` Holo misses.
- Same-model solo one-shots: `360` calls, `346` KNEW/admissible, `14` failures, `10` false positives, `0` false negatives, `4` parse/admissibility failures.
- Blind-120 seam slice: `11/120` packets had at least one same-model solo failure; all 11 are ALLOW-side packets.
- Broader Solo Failure Factory: `210` inspected pairs, `104` pairs with at least one solo failure, `79` wrong-verdict pairs, `25` parse/admissibility-only pairs. Its own scope excludes legacy `614`, blind-120, and Atlas from those candidate totals unless explicitly in SFF rescue artifacts.

Needs extraction before a real 120-packet/six-dot matrix can be published:

- the missing all-row blind-120 solo score trace named by `HOLOVERIFY_BLIND_120_SOLO_FAILURE_PACKET_FILTER_2026_07_03.json`;
- every packet's `pair_id`, sibling side, truth, domain, opaque runtime ID, model key, solo verdict, admissibility status, error class, and source-file/hash;
- per-pair Holo coverage from the blind-120 Holo score artifact, kept separate from solo-dot outcomes.

## Claim-safe wording

Use: "On the blind-120 packet bank, HoloVerify scored `120/120`. The same three model families run alone as one-shot solo baselines produced `14` failures across `360` calls, affecting `11` packets. The matrix shows where those solo seam failures occurred."

Do not use: "overall aggregate accuracy," "public FPR/FNR from the seam matrix," "614 plus blind-120," "all solos collapsed," or "false-negative reduction from blind-120."

## Files/data needed to render the real matrix

- `docs/benchmark/HOLOVERIFY_BLIND_120_PACKET_BANK_FREEZE_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_BATCH001_012_POSTHOC_SCORE_CHECKPOINT_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_BASELINE_POSTHOC_SUMMARY_2026_07_03.json`
- `docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_FAILURE_PACKET_FILTER_2026_07_03.json`
- Missing/needs recovery: `docs/benchmark/holoverify_blind_120_solo_one_shot_runs_2026_07_03/run_20260703T045009Z/solo_one_shot_posthoc_score_trace_bound_v1.json`
- Optional internal-only seam bank, kept separate from public denominator: `docs/benchmark/HOLOVERIFY_SOLO_FAILURE_FACTORY_MASTER_SCOREBOARD_2026_07_04.json`
