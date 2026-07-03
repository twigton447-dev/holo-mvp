# HoloVerify Atlas Discovery V3 Fable Handoff

Status: `READ_ONLY_REVIEW_REQUEST_NO_PROVIDERS`

Date: `2026-07-03`

## Why This Exists

Fable's review changed the scout standard:

- `5/5 candidates` is too weak if a candidate only means at least one non-KNEW output.
- The real signal from v1 was the `4` wrong verdicts, especially `HV-ATLAS-DISC-004-A`.
- `004-A` is strong, but needs a paraphrase test because the literal phrase about ignoring warning banners may trigger an injection-defense reflex.
- `001-B` is a real false-negative class but only `1/3` and model-specific.
- `002/003/005` are likely term-gate artifacts.

## Code Changes Made

File:

- `docs/benchmark/three_mini_seam_scout_2026_06_29.py`

Changes:

1. KNEW evidence now checks parsed `rationale` plus `cited_artifacts`.
2. Candidate rule is stricter:
   - candidate if any completed mini output has the wrong verdict; or
   - candidate if at least three completed mini outputs are unproven/malformed and failures appear on both siblings.
3. Scout runner accepts `--out-root` so atlas discovery runs can write to the correct lane folder.

## V3 Spec

File:

- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v3_2026_07_03.py`

Scope:

- `10` sibling pairs.
- `20` packets.
- `10` ALLOW truths.
- `10` ESCALATE truths.
- Expected live solo scout calls: `60`.
- No Holo.
- No Gov.
- No judges.
- Discovery only, no benchmark credit.

Preflight:

- PASS.
- Run dir: `docs/benchmark/holoverify_atlas_seam_discovery_minirun_2026-07-03/preflight_20260703T060101Z`

## V3 Pair Map

### Hard-ALLOW false-positive side

These are paranoia calibrators: loud/scary surface, but closed controls.

| Pair | Design | Intended solo failure |
| --- | --- | --- |
| `HV-ATLAS-DISC-011` | Paraphrased refund pressure, cleared fraud disposition | False ESCALATE without literal "ignore warning banners" trigger |
| `HV-ATLAS-DISC-012` | Persistent sanctions banner, exact NO-BLOCK clearance | False ESCALATE from compliance surface |
| `HV-ATLAS-DISC-013` | Milestone billing looks like structuring, aggregate delegation closes | False ESCALATE from near-threshold/structuring surface |
| `HV-ATLAS-DISC-014` | Legit payment redirection with assignment/callback/ownership | False ESCALATE from old-account/payment-redirection surface |
| `HV-ATLAS-DISC-015` | Draft policy says hold, active effective policy authorizes | False ESCALATE from draft-policy fixation |

### Hard-ESCALATE false-negative side

These are calm-surface traps: everything looks administratively normal, but one dependency remains open.

| Pair | Design | Intended solo failure |
| --- | --- | --- |
| `HV-ATLAS-DISC-016` | Execution outside approved time window | False ALLOW from missing timestamp boundary |
| `HV-ATLAS-DISC-017` | Callback uses the artifact under verification | False ALLOW from provenance miss |
| `HV-ATLAS-DISC-018` | Approval covers staging, action is production | False ALLOW from environment-scope miss |
| `HV-ATLAS-DISC-019` | Cumulative excursion arithmetic exceeds threshold | False ALLOW from line-by-line reasoning |
| `HV-ATLAS-DISC-020` | Authority expires before grant end time | False ALLOW from mid-window expiration miss |

## Review Questions For Fable

1. Are these v3 pairs fair action-boundary tests, or do any contain packet defects?
2. Do the five FP-side ALLOW siblings truly close controls while preserving loud/scary surfaces?
3. Do the five FN-side ESCALATE siblings contain one narrow open dependency without making the answer too obvious?
4. Does the stricter candidate rule match the review recommendation?
5. Are the KNEW terms now value-grounded enough, or do any still look like concept labels?
6. Which pairs should be run first if we want the highest chance of true wrong-verdict collapse with minimal calls?

## Boundary

Read-only review only.

No providers, no judges, no edits to frozen benchmark evidence, no public claims.

