# research_packet MVP Spec: VeSync Copywriter Exercise

## Purpose

`research_packet` is a pre-creative pipeline mode. It takes a real assignment brief and produces an evidence-backed packet for a later copywriter, human or model. It must not write polished ad or banner copy.

This MVP is scoped to the TurboBlaze-only version of the VeSync copywriter exercise.

## Required Inputs

The research step must accept a single JSON brief with:

- `assignment_id`: stable slug, for example `vesync_cosori_levoit_copywriter_exercise_001`.
- `assignment_summary`: what the exercise asks the copywriter to create.
- `final_copy_sections`: the exact downstream sections the creative pass must produce. For this exercise, use:
  - `recommended_product_rationale`
  - `meta_ad_copy`
  - `website_banner_copy`
  - `short_email_copy`
- `candidate_products`: product objects with `brand`, `product_name`, `known_url`, and optional `priority_hint`.
- `decision_questions`: explicit questions the packet must answer before copywriting starts.
- `brand_voice_questions`: what to inspect about tone, repeated phrasing, vocabulary, and value props.
- `meta_ad_capture_requirements`: minimum examples per brand, fields to capture, and active/inactive status.
- `website_banner_capture_requirements`: minimum first-party banners/heroes/product pages to inspect.
- `wellness_framing_constraints`: allowed, caution, and banned claim territories.
- `source_policy`: required source types, allowed third-party source classes, and reliability thresholds.
- `final_output_schema`: exact downstream JSON shape when a run requires schema-bound creative output. For the staged VeSync run this includes Meta ads, website banners, email, and `adversarial_notes`; it does not include preview text or an email CTA.
- `live_research_permission`: whether the creative generation loop may browse or recapture sources after the packet is staged. If enabled, every new factual claim must be stored as a source record before use.
- `word_count_requirements`: exact count ranges and exclusions. For this exercise, the email body target is 100-150 words, excluding subject lines and P.S.

Active candidate set for this staged exercise:

- Cosori TurboBlaze 6.0-Quart Air Fryer

Minimum decision questions:

- Which product gives the strongest copywriting runway for a short exercise?
- Which product has the clearest verified functional benefits?
- Which product has the strongest wellness/lifestyle bridge without requiring risky claims?
- Which brand voice signals are first-party confirmed versus inferred?
- What Meta ad patterns are actually visible from current or recent examples?
- What website banner patterns are visible from first-party pages?
- Which claims must be avoided, softened, or source-qualified?

## Required Source Checks

First-party sources are mandatory:

- VeSync corporate brand/family pages: confirm parent brand, brand family, and smart-home connective tissue.
- Cosori product pages and collection pages: confirm names, prices at access time, feature claims, product availability, repeated brand language, and banner/hero patterns.
- Meta Ads Library queries for Cosori: capture actual observed ad text and formats. If Meta blocks or returns no usable text, record `MISSING_PLATFORM_EVIDENCE` rather than filling with generic best practices.

Selected third-party sources are allowed only for market/context checks:

- Hands-on reviews from recognizable editorial outlets.
- Retail pages only for ratings/counts, price observations, or customer-language patterns; do not treat retail copy as brand-confirmed product fact.
- Platform documentation from Meta for format constraints, aspect ratio norms, and placement requirements.
- Competitor/category landing pages for convention mapping, if labeled as `inferred_category_pattern`.

## Reliability Scoring

Each source record receives `reliability_score` from 0 to 10:

- Authority, 0-3: first-party product page or official platform doc is 3; hands-on editorial is 2; retail/customer content is 1; unsourced blog is 0.
- Directness, 0-3: exact product or ad text is 3; same brand/category is 2; broad category advice is 1; unrelated context is 0.
- Specificity, 0-2: concrete feature, price, headline, format, or claim language is 2; general positioning is 1; vague commentary is 0.
- Recency/access, 0-1: current page captured with `accessed_at` is 1.
- Independence, 0-1: independent third-party validation is 1; first-party or syndicated/retail copy is 0.

Reliability tiers:

- `A`: 8-10, usable for verified packet facts.
- `B`: 6-7, usable with caution or as supporting evidence.
- `C`: 4-5, usable only for patterns or hypotheses.
- `D`: 0-3, appendix only unless explaining a missingness or caution note.

## Evidence Levels

Every finding must be one of:

- `first_party_confirmed_fact`: direct official source, exact product/ad/page fact.
- `repeated_brand_language`: phrase or benefit repeated across first-party surfaces or official ads.
- `inferred_category_pattern`: pattern inferred from multiple category examples, competitor pages, platform docs, or third-party reviews.
- `speculative_conclusion`: useful hypothesis that does not yet meet evidence threshold.

Do not collapse these into one generic confidence score.

## Source Metadata Schema

Every finding must carry:

- `url`
- `title`
- `source_type`
- `brand`
- `accessed_at`
- `evidence_snippet`
- `confidence`
- `reliability_score`
- `reliability_tier`
- `evidence_level`
- `used_for`

Allowed `source_type` values:

- `first_party_product_page`
- `first_party_collection_or_homepage`
- `first_party_corporate_page`
- `platform_ad_library`
- `platform_documentation`
- `third_party_editorial_review`
- `retail_marketplace`
- `competitor_category_reference`

## Strong Evidence vs Fluff

Strong evidence:

- Exact official product facts, such as product name, price at access time, capacity, app compatibility, functions, coating/material language, filter mode, or smart-control language.
- Actual Meta Ads Library observations with page name, ad status, primary text, headline, description if visible, CTA, format, destination, and capture date.
- Repeated official phrasing appearing on at least two first-party surfaces or one first-party surface plus one official ad.
- Category conventions supported by at least three observed examples, with examples listed.
- Third-party review findings based on hands-on testing, clearly marked as third-party validation rather than brand fact.

Fluff:

- Unsourced statements such as "consumers want wellness" or "families care about convenience."
- Generic best-practice claims standing in for actual Meta ad observations.
- Feature claims copied from retail listings when first-party pages do not confirm them.
- "Premium," "healthy," "clean," "best," or "medical-grade" language without source-backed definition.
- Category cliches that are named but not evidenced by examples.

## Meta Ad Evidence Requirements

Minimum viable Meta evidence requires:

- Five usable Cosori ad examples, or an explicit `MISSING_PLATFORM_EVIDENCE` record explaining why not.
- For each ad: `brand`, `page_name`, `library_id` if visible, `status`, `start_date` if visible, `format`, `primary_text`, `headline`, `description`, `cta`, `destination_url`, `screenshot_path` if captured, `accessed_at`.
- Pattern extraction must quote short fragments only, then normalize into patterns such as:
  - benefit-led headline
  - offer-led headline
  - problem/solution opener
  - feature stack
  - seasonal/lifestyle hook
  - review/social-proof hook

If the packet only uses Meta format docs and no actual ad examples, the Meta section must be labeled `platform_constraints_only`, not `ad_convention_observations`.

## Website Banner Evidence Requirements

Minimum viable banner evidence requires:

- At least three first-party Cosori page captures.
- For each capture: hero headline, subhead, CTA text, product visibility, image/product context, promo/price presence, and claim type.
- Pattern extraction must separate:
  - exact observed first-party banner language
  - repeated brand language
  - inferred banner convention

## Wellness Framing Constraints

Allowed:

- Convenience, speed, freshness, everyday routines, home comfort, cooking confidence, pet-home fit, smart control, cleaning/maintenance ease.

Caution:

- Healthier cooking, clean air, allergy, smoke, dander, toxin, PFAS, HEPA, medical comfort, energy efficiency. Use only when source-backed and phrase as functional support, not health outcome.

Banned unless explicitly legal-approved in the source:

- Disease prevention, allergy relief, asthma relief, toxin-free home, medical-grade purification, guaranteed weight loss or nutrition outcomes, universally safe/non-toxic claims beyond exact official wording.

## Packet Structure

The final research packet must include:

- `assignment_summary`: compressed restatement of the brief and downstream deliverables.
- `decision_questions`: each question answered with evidence status.
- `recommended_product`: one product recommendation plus why, with evidence levels named.
- `product_lanes`: separate product targets only when explicitly requested. The active staged VeSync run is TurboBlaze-only.
- `product_comparison_snapshot`: compact table comparing candidates.
- `brand_voice_analysis`: official phrasing, repeated language, tonal constraints, and risky copy territories.
- `feature_functionality_inventory`: features separated by source confidence.
- `wellness_lifestyle_bridge_opportunities`: usable territories and claim boundaries.
- `meta_ad_convention_observations`: actual ad patterns, or `platform_constraints_only` if ad examples are unavailable.
- `website_banner_convention_observations`: first-party hero/banner patterns.
- `short_email_convention_observations`: subject-line, body, and P.S. conventions for short ecommerce introductions. Preview text and email CTA may be researched as optional conventions but must not appear in schema-bound output unless the schema includes them.
- `claim_caution_notes`: claims to avoid, soften, or source-qualify.
- `messaging_opportunities`: copy territories, not polished lines.
- `word_count_rules`: exact count requirements for the later creative pass.
- `source_appendix`: full source metadata and finding IDs.

The packet must also save intermediate artifacts:

- `00_input_brief.json`
- `01_source_plan.json`
- `02_source_records.json`
- `03_findings.json`
- `04_reliability_scores.json`
- `05_evidence_level_map.json`
- `research_packet.json`
- `research_packet.md`

## Done Definition

The MVP research packet is complete when:

- Every recommendation points to at least one finding ID.
- Every finding has full source metadata.
- The packet contains at least one entry for each evidence level, even if speculative entries are explicitly rejected from creative use.
- Meta evidence is either actual observed ad examples or explicitly marked missing.
- Wellness and product claims are separated into allowed, caution, and banned territories.
- A later copywriter can draft the three requested creative sections without visiting source URLs, while still seeing what is verified versus inferred.
