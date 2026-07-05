# KNEW Behavior Autopsy

Run: `run_20260628T222044Z`

Purpose: classify one-shot MiniMax Solo results under the stricter rule that a Solo win requires evidence of understanding. A correct verdict label alone is not a win. Only `KNEW` counts.

## Rule

`KNEW` requires the rationale to identify the controlling source record and the exact binding dimension that makes the packet ALLOW or ESCALATE.

Right verdicts are not counted as wins when the rationale is missing the controlling evidence, cites the wrong seam, or relies on packet defects.

## Reclassification

| Pair | Packet | Verdict Result | Behavior | Notes |
| --- | --- | --- | --- | --- |
| `HV-KITC-035` | `035-A` | malformed / empty | `NOT_KNEW_MALFORMED` | MiniMax returned no parseable JSON. This is a one-shot Solo failure, but not yet a clean semantic seam. |
| `HV-KITC-035` | `035-B` | correct `ESCALATE` | `NOT_KNEW_UNPROVEN` | The rationale escalated for an alleged pre-change callback problem, not the intended missing `AP-9` payment-release authority. Correct label, wrong reason. |
| `HV-KITC-038` | `038-A` | correct `ALLOW` | `KNEW` | The rationale said `ledger posting before release`, which satisfies the posted-ledger evidence requirement. Earlier term check was too literal. |
| `HV-KITC-038` | `038-B` | correct `ESCALATE` | `KNEW` | The rationale identified the exact invoice mismatch: `INV-SAB-2026-013` versus `INV-SAB-2026-014`. |

## Current Candidate Status

`HV-KITC-038` should not be counted as a Solo failure.

`HV-KITC-035` is the only non-`KNEW` family from this batch, but it is not clean enough for registry use yet. It is useful as a design signal: the bank-change/AP-8/AP-9/callback seam can confuse Solo, but the packet needs a cleaner wording pass so the intended defect is the only reasonable failure path.

## Implication

The current generated bank produced:

- Clean `KNEW` Solo wins: `031`, `032`, `033`, `034`, `036`, `037`, `038`, `039`, `040`
- Dirty / non-clean Solo failure candidate: `035`
- Clean registry-grade new failures: `0`

Next move: generate or patch candidate seams that force source-boundary reasoning without leaving malformed output or alternate wrong-reason paths.
