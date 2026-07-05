# HoloVerify Dot Matrix Visual Spec

Date: 2026-07-05

Callsign: HoloAtlas

Status: `PASS_NO_PROVIDER_VISUAL_SPEC_RECOMMENDATION`

This is a recommendation artifact for Taylor and HoloOps. No providers, Holo live runs, solo runs, Gov runs, judges, public site edits, staging, commits, pushes, or frozen runtime evidence edits were performed.

## Visual Spec

Each square should represent one sibling pair. A sibling pair is the right unit because the benchmark question is whether the system respects the boundary between a source-closed ALLOW and a source-open ESCALATE. Domains and failure classes should organize the grid, not replace the pair as the base unit.

Inside each square, render six solo opportunity dots:

| Row | ALLOW sibling | ESCALATE sibling |
|---|---|---|
| Solo model 1 | dot | dot |
| Solo model 2 | dot | dot |
| Solo model 3 | dot | dot |

Recommended hierarchy:

- Square: sibling pair.
- Dot: one model verdict opportunity on one sibling packet.
- Row or filter: domain.
- Badge or outline: failure class.
- Panel mode: evidence lane and denominator.

The first view should show solo models as mostly green with scattered red and amber dots across domains. The message is not that models are useless. The message is that scattered wrong-verdict dots are unacceptable at high-stakes execution boundaries.

The second view should toggle HoloVerify on. Holo-rescued solo failures may be covered with a green Holo overlay or converted to green with a visible rescue ring. Holo failures must remain red and link to failure class, patch status, rerun status, and whether the case became a regression fixture.

## Legend

| Mark | Meaning | Count rule |
|---|---|---|
| Green dot | Correct and admissible verdict. | Counts only within its explicitly selected lane. |
| Red dot | Wrong verdict. | Counts only within its explicitly selected lane. |
| Amber dot | Parse/admissibility failure. | Keep separate from semantic wrong verdicts. |
| Gray dot | Quarantined packet, packet/key defect, or excluded evidence. | Excluded from numerator and denominator. |
| Green ring over red | HoloVerify rescued a solo failure in an internal hardening lane. | Not public denominator evidence unless separately admitted. |
| Red ring or red outline | HoloVerify also failed or did not yet patch the failure class. | Link to failure class and patch/rerun state. |

Do not rely on color alone. Pair color with icon, texture, label, or accessible tooltip text.

## Domain Layout

Default layout should be domain rows with compact pair squares across each row:

1. AP / procurement
2. Legal / contracts
3. Clinical
4. Banking / finance
5. Security / IAM
6. Agentic commerce
7. Public sector
8. Infrastructure / operations

Use filters for failure class, evidence lane, verdict type, and patch status. If a domain has candidate-only or quarantined material, mark the whole row segment as candidate/quarantined instead of mixing it into public-denominator counts.

## Toggle Behavior

Use explicit modes, not one blended chart:

| Mode | What it shows | Required warning |
|---|---|---|
| Public blind-120 | Only admitted public denominator evidence. | This is the only public benchmark denominator. |
| Solo stress lane | Selected solo failure material and seam discovery. | Selected for pressure testing; not representative public denominator evidence. |
| Holo rescue / hardening | Internal HoloVerify repair and rerun evidence. | Internal hardening evidence only unless separately admitted. |
| Quarantine | Packet/key defects, invalid runs, and excluded evidence. | Excluded from scores and denominator claims. |

In Solo mode, show all six solo dots per pair. In Holo mode, keep the solo dot positions fixed and add the Holo result as an overlay so viewers can see what was rescued and what remains red. In Quarantine mode, gray out excluded pairs and suppress score aggregation.

## Failure-Class Taxonomy

Use these classes as first-pass filters and tooltip labels:

| Display label | Atlas class | Definition |
|---|---|---|
| FN false allow | `SOLO_FN_FALSE_ALLOW` | Source-open ESCALATE packet is incorrectly allowed. |
| FP overblock | `SOLO_FP_OVERBLOCK` | Source-closed ALLOW packet is incorrectly blocked. |
| Parse/admissibility | `SOLO_PARSE_ADMISSIBILITY_FAILURE` | Output cannot be scored as a clean verdict. |
| Blocker closure failure | `FALSE_BLOCKER_CLOSURE_ACCEPTED` | A claimed closure does not actually close the source-visible blocker. |
| Scope dependency non-detection | `V5_SCOPE_DEPENDENCY_NON_DETECTION` / `BLOCKER_NOT_DETECTED_BY_ANY_WORKER` | No worker or gate detects the required source-field dependency. |
| Packet/key defect quarantine | `PACKET_KEY_DEFECT` | Expected answer depends on source-invisible or defective packet/key material. |

## Tooltip Schema

Clicking a red, amber, or gray dot should open a compact evidence card:

| Field | Purpose |
|---|---|
| `dataset_mode` | `public_blind_120`, `solo_stress_lane`, `holo_rescue_internal`, or `quarantine`. |
| `denominator_status` | Included, internal-only, candidate-only, or excluded. |
| `pair_id` | Sibling-pair identifier when public-safe to show. |
| `packet_id` | Packet identifier when public-safe to show. |
| `sibling_side` | ALLOW or ESCALATE sibling. |
| `model` | Solo model name or anonymized model slot. |
| `verdict` | Model verdict emitted. |
| `truth` | Internal audit truth / expected source-visible verdict. Public views should label this as expected verdict and must not expose hidden labels. |
| `failure_class` | Atlas failure class. |
| `packet_domain` | Domain row/filter. |
| `holo_rescued` | True, false, not_run, or not_applicable. |
| `holo_result` | Holo pass/fail/admissibility status for the relevant lane. |
| `patch_version` | V4, V5, V6, or none. |
| `rerun_status` | Pending, passed, failed, partial, or not_applicable. |
| `regression_fixture` | Whether it became a regression fixture. |
| `quarantine_reason` | Packet/key defect, invalid run, provider transport failure, parse-only, or none. |
| `evidence_ref` | File-backed report, rollup, or trace-bound summary reference. |

## Claim-Boundary Warning Text

Use this warning near the chart and in exported images:

> This matrix is a failure atlas, not one blended benchmark score. The public denominator is blind-120 only. Solo stress lanes are selected to expose execution-boundary failures. Holo rescue and rerun lanes are internal hardening evidence unless separately admitted. Gray quarantined packets are excluded. Red dots do not mean AI is useless; they show scattered wrong or unusable decisions that are unacceptable at high-stakes execution boundaries.

## Implementation Notes

- Never aggregate public blind-120, solo-stress, Holo-rescue, and quarantine lanes into one score.
- Never hide unresolved Holo failures behind a green aggregate.
- Never display answer keys, sibling truth shortcuts, scoring-map contents, or prompt-visible hidden labels.
- Keep packet/key defects gray and excluded even if they are visually useful as cautionary examples.
- Promote repeated red-dot clusters into Atlas failure classes only after file-backed review.

## Source Map

- `docs/benchmark/HOLOVERIFY_BLINDSPOT_ATLAS_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_BLINDSPOT_ATLAS_2026_07_05.json`
