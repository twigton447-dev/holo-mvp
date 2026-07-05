# VeSync HoloBuild vs Solo Comparison Protocol

## Purpose

Test whether a HoloBuild creative loop using Claude Opus 4.8 plus Grok 4.3, with Grok 4.3 permanently serving as HoloGov, improves a real copywriting assignment for Cosori TurboBlaze Air Fryer more reliably than solo Opus controls, with live research allowed equally across lanes.

## Conditions

1. `holo_build_creative_dynamic_convergence_v1`
   - Dynamic turn count with hard cap of 10 turns.
   - Active model pool: Claude Opus 4.8 and Grok 4.3.
   - Active model rotation is randomized constrained with no consecutive active-model repeats.
   - HoloGov remains Grok 4.3 for every turn and every session.
   - Role-separated builder and attacker surfaces.
   - Lossless canonical thread: each later HB turn sees the complete prior HB prompts, outputs, critiques, governor briefs, live source records, rejected options, and current candidate artifact.
   - Early convergence is allowed only when both the active model and Grok 4.3 HoloGov judge that no further meaningful improvement is possible.
   - Live research allowed during generation.
   - Product focus: Cosori TurboBlaze Air Fryer only.

2. `solo_claude_opus_4_8_single_shot_v0`
   - One call.
   - Same visible packet.
   - Same live-research permission.
   - Same TurboBlaze-only product focus.
   - Same output contract.

3. `solo_claude_opus_4_8_multi_shot_v0`
   - Up to 10 calls.
   - Same model and same visible packet.
   - Same live-research permission.
   - Same TurboBlaze-only product focus.
   - Self-revision allowed, but no role-separated HoloBuild state or independent attacker/governor role.

Model availability for Claude Opus 4.8 and Grok 4.3 is not verified by this staging step. If either model is unavailable in live execution, the run must block rather than silently substituting another model.

## Inputs Shared By All Conditions

- `00_input_brief.json`
- `01_research_packet_seed.json`
- `02_initial_draft.md`
- `02_initial_draft.json`
- `05_output_schema.json`
- `06_product_lane_strategy.json`

All conditions must see the same research packet, the same initial draft, the same TurboBlaze-only product focus, and the same live-research permission. Any new web evidence found during generation must be stored with source metadata.

## HoloBuild Canonical Thread

The HoloBuild lane is lossless across turns. Each subsequent HB call must receive the entire canonical thread before it, including the initial visible packet, every prior prompt, every prior model output, attacker findings, HoloGov briefs, accepted and rejected copy variants, live source records, missing-evidence notes, claim-boundary warnings, and the current candidate artifact.

Do not substitute a compressed summary for prior turns. A navigation index may be added, but prior canonical content must remain available verbatim. If the full canonical thread cannot fit in the target model context, stop the run and mark it blocked rather than dropping earlier turns.

## HoloGov

HoloGov is Grok 4.3 for this run. This is an overriding invariant. The active model may rotate between Claude Opus 4.8 and Grok 4.3, but HoloGov does not rotate away from Grok 4.3.

## Convergence

Each turn must treat the prior candidate as improvable. The run terminates early only if both the active model and Grok 4.3 HoloGov judge that no further meaningful improvement is possible. If either one sees meaningful improvement potential, the run continues until the hard cap of 10 turns.

## Live Research Budget

Live research is allowed but capped equally for every lane:

- Maximum 20 seconds of web research per turn.
- Maximum 120 seconds of total web research per lane.
- Maximum 8 search queries per lane.
- Maximum 12 opened pages per lane.
- Maximum 20 seconds per turn attempting to capture usable Cosori Meta Ads Library examples.
- Stop once the required source classes are satisfied and two consecutive searches produce no new material claim.
- If the budget expires or Meta examples are unavailable, proceed from the staged packet and record the gap in `adversarial_notes.missing_evidence`.

## Required Output

Each condition must generate one strict JSON artifact matching `05_output_schema.json` and contain:

- `assignment_id`
- `product`
- `section_1_meta_ads.ad1` and `section_1_meta_ads.ad2`, each with `on_image_text`, `primary_text`, `headline`, `description`, and `cta`.
- `section_2_website_banners.banner1`, `banner2`, and `banner3`, each with `header`, `subhead`, and `cta`.
- `section_3_email` with `subject_line_1`, `subject_line_2`, `body`, and `ps`.
- `adversarial_notes` with `wellness_linkage_issues`, `rule_violations`, `tone_drift`, and `missing_evidence`.

The generated artifact must not contain a research brief, source appendix, explanation, markdown wrapper, preview text, or email CTA unless the schema is explicitly revised.

Email body word count must be 100-150 words, excluding subject lines and P.S.

## Rubric

Score each artifact 1-5 on:

- Assignment completeness: all requested fields present.
- Schema compliance: valid JSON, exact top-level shape, no extra narrative wrapper.
- Evidence faithfulness: product claims stay within packet evidence.
- Claim safety: avoids medical, diet, allergy, guilt-free, and guaranteed-health language.
- Brand fit: Cosori voice feels food-first, capable, practical, and appetizing.
- Wellness bridge: links features to home routines or home environment improvements, and explicitly explains how the functionality contributes to a better lifestyle.
- Healthier-lifestyle strategy: for TurboBlaze, frames less-oil home cooking and routine-building as contributing to a healthier, wellness-forward lifestyle without promising health outcomes.
- Channel fit: Meta ads, website banners, and email feel native to their channels.
- Creative lift: improves materially over the initial draft rather than lightly paraphrasing it.
- Concision and polish: copy is sharp, readable, and not a feature dump.

Suggested weighting:

- Claim safety: 20%
- Evidence faithfulness: 20%
- Channel fit: 20%
- Creative lift: 15%
- Brand fit: 10%
- Wellness bridge: 10%
- Assignment completeness: 5%
- Schema compliance: mechanical gate before scoring

## Blind Evaluation

Before judging, label outputs as `ARTIFACT_A`, `ARTIFACT_B`, and `ARTIFACT_C`. Keep a private anonymization map outside the judge-visible packet.

Judge packet should include:

- Assignment brief.
- Research packet seed.
- Initial draft.
- Three anonymized artifacts.
- Rubric.
- Required ranking with no ties.
- Per-section rationale.
- Claim-safety defect log.

## My Read On This Test

This is a good HoloBuild test because the task is not just "write prettier copy." The winning artifact has to preserve evidence boundaries, interpret claim risk, translate functional features into lifestyle framing, and make three different channel formats work together. That gives HoloBuild real room to show value through attacker turns and convergence.

The important control is the multi-shot solo lane. Without it, a HoloBuild win could be dismissed as "iteration beat one-shot." With both solo single-shot and solo multi-shot, the comparison can separate iteration benefit from governed-role benefit.

The main risk is evidence asymmetry. If the HoloBuild lane sees richer hidden notes than the solo lanes, the test gets muddy. Keep the visible packet identical and apply the same live-research permission and source-storage rule to every lane.

The current staged packet is strong enough for a creative run, but it should not be used to claim observed Meta ad conventions. Meta Ads Library examples were not captured into the seed packet, so ad-pattern language must be treated as channel best practice rather than brand-specific paid-media evidence.
