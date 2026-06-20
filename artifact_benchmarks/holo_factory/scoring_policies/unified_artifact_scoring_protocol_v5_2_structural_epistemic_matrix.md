# Unified Artifact Scoring Protocol v5.2 - Structural + Epistemic Decision Matrix

Status: locked primary scoring candidate for trial use; not final benchmark doctrine.
Protocol ID: `unified_artifact_scoring_protocol_v5_2_structural_epistemic`.

This protocol is locked as the preferred trial metric over the broad v5.1 scoring front-end for cross-domain artifact scoring. It does not claim official benchmark proof from any manual probe. The D5 manual Gemini probe is used only as a regression fixture for math, bands, and validation behavior.

## Scoring Goal

The benchmark should distinguish polished but merely functional artifacts from artifacts that are both executive-ready and epistemically rigorous. The score is intentionally compact and inspectable:

1. Structural Executive Readiness, 18 raw points.
2. Epistemic / Insight Integrity, 15 raw points.

The primary topline score is `final_score_100`, after hard caps. The raw score is preserved as:

- `structural_raw_18`
- `epistemic_raw_15`
- `raw_total_33`
- `normalized_total_100`

Formula:

`normalized_total_100 = round((raw_total_33 / 33) * 100, 1)`

`final_score_100 = min(normalized_total_100, lowest_applicable_hard_cap)`

## Structural Executive Readiness - 18 Raw Points

Each dimension is scored from 0 to 3.

### 1. Bottom Line Up Front / BLUF

- 3: explicit, definitive recommendation in first section.
- 2: recommendation present but less direct or partially buried.
- 1: vague recommendation.
- 0: no recommendation.

### 2. Data Isolation

- 3: critical math/statistics isolated in a dedicated section, table, or distinct paragraph.
- 2: math/statistics present but buried in dense prose.
- 1: data alluded to but not calculated/interpreted.
- 0: no meaningful quantitative handling.

### 3. Option Distinctness

- 3: 3+ mutually distinct options with explicit constraints.
- 2: options present but overlapping or under-constrained.
- 1: binary yes/no only.
- 0: no meaningful alternatives.

### 4. Evidence Constraints

- 3: explicitly states what evidence does and does not prove.
- 2: mentions limitations but not sharply.
- 1: cites evidence but ignores limitations or contrary data.
- 0: no meaningful evidence-quality evaluation.

### 5. Risk Symmetry

- 3: separately addresses risk of acting and risk of waiting.
- 2: discusses both but combines or skews them.
- 1: addresses only one side.
- 0: no structured risk assessment.

### 6. Scannability

- 3: clear headings, sections, hierarchy, and executive readability.
- 2: headings present but dense.
- 1: weak structure / essay-like.
- 0: hard to scan or unstructured.

Structural subtotal: `0-18`.

## Epistemic / Insight Integrity - 15 Raw Points

Each dimension is scored from 0 to 3.

### 1. Claim-Evidence Distance

- 3: claims are strictly bounded by evidence; explicitly states what data cannot prove.
- 2: claims align with evidence but limits are mostly implied.
- 1: subtly over-extrapolates.
- 0: hallucinates, contradicts, or materially misuses sources.

### 2. Conflicting Data Handling

- 3: surfaces conflicting evidence and explains decision implications.
- 2: mentions conflicts but does not fully resolve operational impact.
- 1: ignores important weak/conflicting evidence.
- 0: suppresses or contradicts conflicting evidence.

### 3. Insight vs. Summary

- 3: synthesizes sources into operational insight.
- 2: accurate summary but limited synthesis.
- 1: surface paraphrase / low "so what".
- 0: data dump or unsupported interpretation.

### 4. Operational Reality / Execution Gap

- 3: defines dependencies, stop-rules, failure triggers, and implementation constraints.
- 2: notes operational requirements but lacks specific triggers or constraints.
- 1: assumes smooth execution.
- 0: proposes operationally impossible or unsafe action.

### 5. Source Weighting / Validity

- 3: clearly distinguishes strong, weak, stale, draft, secondary, preprint, regulatory, or provisional evidence.
- 2: mostly weights sources correctly but not explicitly enough.
- 1: over-relies on weak evidence or flattens source quality.
- 0: fails to evaluate source quality or uses unsupported assumptions.

Epistemic subtotal: `0-15`.

## Score Bands

- `95-100`: Executive-ready / highly rigorous.
- `90-94.9`: Strong / expert-survivable with minor edits.
- `83-89.9`: Functional / needs revision.
- `70-82.9`: Draft quality / research summary.
- `<70`: Rejected / not decision-grade.

Band doctrine: a mid-80s score is not bad. It means the artifact is accurate and useful, but not yet executive-ready or fully expert-survivable. This is the intended separation: strong solo outputs may land in the 83-89 range, while artifacts that clear both structure and epistemic integrity can reach 95+.

## Mandatory Hard Caps

Hard caps override the normalized score. If multiple caps apply, use the lowest maximum score.

- `invented_source_or_citation`: max 70.
- `false_source_attribution`: max 75.
- `material_source_misrepresentation`: max 75.
- `source_boundary_violation`: max 75.
- `central_data_stat_chart_error`: max 75.
- `missed_contradiction_changing_recommendation`: max 80.
- `unsupported_major_recommendation`: max 82.
- `unsafe_or_overconfident_operational_advice`: max 82.
- `generic_crisis_memo_low_operational_usefulness`: max 78.
- `failure_to_handle_uncertainty`: max 85.
- `severe_required_section_failure`: max 88.
- `reliance_critical_missing_caveat`: max 85.
- `stale_evidence_treated_as_current_decisive`: max 82.
- `draft_provisional_limited_source_treated_as_final_authority`: max 80.
- `material_negative_space_miss`: max 83.
- `no_clear_decision_recommendation`: max 83.
- `no_operational_stop_go_logic`: max 83.

## Required JSON Output Shape

For each artifact score row:

- `artifact_id`
- `structural_scores`
  - `bluf`
  - `data_isolation`
  - `option_distinctness`
  - `evidence_constraints`
  - `risk_symmetry`
  - `scannability`
- `structural_raw_18`
- `epistemic_scores`
  - `claim_evidence_distance`
  - `conflicting_data_handling`
  - `insight_vs_summary`
  - `operational_reality_gap`
  - `source_weighting_validity`
- `epistemic_raw_15`
- `raw_total_33`
- `normalized_total_100`
- `applicable_hard_caps`
- `final_score_100`
- `band`
- `dimension_justifications`
- `strongest_dimensions`
- `weakest_dimensions`
- `required_repairs_to_next_band`
- `expert_reviewer_challenge`
- `decision_reliance_risk`

A complete scoring payload may wrap rows under `artifact_scores` with `protocol_id`.

## Validator Requirements

Fail validation if:

- any dimension score is not 0, 1, 2, or 3;
- structural subtotal math is wrong;
- epistemic subtotal math is wrong;
- raw total math is wrong;
- normalized score math is wrong;
- final score exceeds an applicable hard cap;
- score is 95+ but any structural dimension is below 3;
- score is 95+ but any epistemic dimension is below 3;
- score is 90+ but claim-evidence distance is below 3;
- score is 90+ but source weighting is below 3;
- score is 90+ but operational reality gap is below 3;
- score is above 83 with no clear decision recommendation;
- score is above 83 with no stop/go or failure-trigger logic;
- invented source/citation is present and final score exceeds 70;
- false source attribution is present and final score exceeds 75;
- material source misrepresentation is present and final score exceeds 75.

## D5 Manual Regression Fixture

This fixture tests math, bands, and validation only. It is not official proof.

- `ARTIFACT_001`: Structural `18/18`, Epistemic `15/15`, Raw `33/33`, Normalized `100.0`, Band `Executive-ready / highly rigorous`.
- `ARTIFACT_003`: Structural `16/18`, Epistemic `12/15`, Raw `28/33`, Normalized `84.8`, Band `Functional / needs revision`.
