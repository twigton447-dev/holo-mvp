# Unified Artifact Scoring Protocol v6 - Full Structural + Epistemic Rubric

Status: locked global scoring protocol for all D1-D10 HoloBuild benchmark tests after freeze.
Protocol ID: `unified_artifact_scoring_protocol_v6_structural_epistemic`.

This protocol replaces broad impression scoring and the compact v5.2 trial matrix for future all-domain scoring. It is claim-ledger first: judges must audit artifact claims against the frozen source packet before assigning final scores. The goal is to spread the top band by source-grounded expert survivability, not by style or fluency.

## Use Boundary

- Applies to D1-D10 and subsequent HoloBuild benchmark packets unless a later locked protocol supersedes it.
- Packets still carry deterministic admission gates separately.
- Word-band misses are scored through caps/ceilings unless the packet explicitly declares diagnostic-only treatment.
- Judges must not see model identity, run identity, architecture evidence, provider names, token burn, prior scores, unblinding maps, or internal audit notes.
- Do not alter this protocol after artifact generation for a run. Any scoring change requires a new protocol version and separate lock.

## Score Overview

Score each artifact on a 0-100 scale:

- Structural Score: 50 points.
- Epistemic Score: 50 points.
- Raw Score: `raw_score_0_100 = structural_score_50 + epistemic_score_50`.
- Final Score: `score_0_100 = min(raw_score_0_100, lowest_applicable_cap_or_ceiling)`.

The primary leaderboard score is `score_0_100`.

## Mandatory Pre-Score Claim Ledger

No completed claim ledger means no valid score.

For each artifact, audit 8-15 major claims. Each claim must include:

```json
{
  "claim_text": "",
  "claim_type": "factual | causal | regulatory | operational | statistical | recommendation | source-status",
  "cited_sources": [],
  "exact_source_id_quality": "exact_full_ids | abbreviated_ids | vague_reference | no_source_reference",
  "source_support_status": "supported | partially_supported | unsupported | contradicted | not_in_packet",
  "source_boundary_issue": false,
  "overclaim_issue": false,
  "stale_or_limited_evidence_issue": false,
  "missing_caveat": "",
  "severity": "none | minor | material | fatal",
  "cap_or_ceiling_trigger_if_any": ""
}
```

The ledger must include the artifact's bottom-line recommendation, core calculations, source-status claims, key operational gates, risk-of-acting claims, risk-of-waiting claims, and any claim that could change the decision.

## Structural Score - 50 Points

### 1. Task Compliance / Format Discipline - 8 pts
Required sections, requested deliverable type, body word band, and no missing mandatory elements.

### 2. Decision Architecture - 8 pts
Clear bottom-line recommendation, explains what is happening, why it matters now, and the decision leadership must make.

### 3. Operational Specificity - 10 pts
Concrete actions, owners/gates, stop/go triggers, escalation paths, conditional approvals, rollback/fallback path where relevant.

### 4. Quantitative Execution - 8 pts
Correct arithmetic, transparent calculations, no fake precision, correct interpretation of charts/tables/statistics.

### 5. Options and Tradeoff Coverage - 8 pts
Practical response options, risks of acting, risks of waiting, and no one-sided approve/block shortcut that erases material tradeoffs.

### 6. Usability / Executive Readiness - 8 pts
Leadership can act on it. Clear, scannable, decision-grade, and free of generic “monitor closely” filler.

## Epistemic Score - 50 Points

### 1. Source Fidelity - 12 pts
Exact source IDs when available, no invented sources, no loose source laundering, accurate source attribution.

### 2. Claim Support - 12 pts
Major claims are supported by frozen sources. Recommendations distinguish source facts from inference.

### 3. Uncertainty / Negative Space - 8 pts
Carries missing approvals, missing data, stale evidence, weak evidence, contradictions, and limits into the recommendation.

### 4. Overclaim Discipline - 8 pts
Does not convert incomplete screening into fraud, regional risk into legal breach, urgency into authorization, draft/advisory material into final approval, or weak commentary into decisive evidence.

### 5. Expert Survivability - 6 pts
Names avoided failure modes and would survive hostile domain review.

### 6. Auditability - 4 pts
A third party can replay the reasoning from artifact plus frozen source packet.

## Hard Caps / Ceilings

Apply the lowest applicable cap/ceiling.

- `missing_claim_ledger`: invalid score.
- `invented_source_or_fabricated_external_fact`: max 60, or max 50 if material/fatal.
- `material_source_misattribution`: max 75.
- `source_status_error`: max 80, or max 75 if material.
- `unsupported_major_recommendation_claim`: max 82.
- `material_negative_space_miss`: max 83.
- `generic_operational_advice_without_executable_gates`: max 84.
- `material_risk_of_acting_or_waiting_omission`: max 86.
- `word_count_slight_miss`: max 88.
- `word_count_major_miss`: max 82.
- `word_count_extreme_miss`: diagnostic-only unless packet override exists.
- `abbreviated_source_ids_when_exact_ids_expected`: max 90.
- `score_above_85_requires_two_avoided_failure_modes`: score above 85 invalid unless satisfied.
- `score_above_90_requires_three_avoided_failure_modes`: score above 90 invalid unless satisfied.
- `score_above_90_requires_no_material_source_support_defects`: score above 90 invalid if any material source-support defect exists.
- `score_above_95_requires_near_perfect_source_fidelity`: score above 95 invalid with applied caps, material defects, unsupported major claims, source laundering, or missing concrete defect audit.

## Top-Band Meaning

- 96-100: Expert-grade, nearly clean, audit-ready.
- 90-95: Strong expert-survivable artifact with only minor defects.
- 84-89: Good artifact, but has meaningful structural or epistemic weaknesses.
- 75-83: Useful but not expert-survivable without revision.
- Below 75: Materially unreliable, generic, unsupported, or unsafe.

Perfect or near-perfect scores are intentionally rare. A polished artifact with a word-band miss, abbreviated citations, weak source weighting, or missing negative-space limitation should usually land below 90.

## Required Final JSON

```json
{
  "protocol_id": "unified_artifact_scoring_protocol_v6_structural_epistemic",
  "artifact_scores": [
    {
      "artifact_label": "ARTIFACT_001",
      "verified_word_count": null,
      "word_band_pass": null,
      "structural_score_50": null,
      "epistemic_score_50": null,
      "raw_score_0_100": null,
      "score_0_100": null,
      "claim_ledger": [],
      "caps_or_ceilings_applied": [],
      "invented_or_false_source_attributions": [],
      "unsupported_major_claims": [],
      "source_laundering_findings": [],
      "negative_space_misses": [],
      "tempting_but_rejected_claims": [],
      "avoided_failure_modes": [],
      "major_strengths": [],
      "major_defects": [],
      "would_survive_expert_review": null,
      "rationale": ""
    }
  ],
  "forced_rank_order_best_to_worst": [],
  "pairwise_winners": {},
  "dimension_rankings": {
    "structural_quality": [],
    "source_fidelity": [],
    "claim_discipline": [],
    "operational_usefulness": [],
    "uncertainty_handling": [],
    "expert_survivability": []
  },
  "score_spread_explanation": ""
}
```

## Validator Requirements

The validator must fail if:

- `protocol_id` is wrong.
- claim ledger has fewer than 8 or more than 15 claims.
- required claim fields are missing or use invalid enums.
- structural + epistemic math is wrong.
- final score exceeds raw score.
- final score exceeds the lowest applicable cap/ceiling.
- word-band fail scores above 88 unless an explicit lower/diagnostic cap is absent and packet override is recorded.
- abbreviated source IDs appear in the ledger and final score exceeds 90.
- any invented/false source attribution scores above 60.
- unsupported material recommendation claim scores above 82.
- material negative-space miss scores above 83.
- nonempty source laundering findings score above 85.
- score above 85 has fewer than 2 avoided failure modes.
- score above 90 has fewer than 3 avoided failure modes.
- score above 90 has material source-support defects.
- score above 95 has applied caps/ceilings or material defects.
- pairwise winners do not use exact artifact labels or include all-equal/tie without ledger-grounded evidence.

## Active Lock Doctrine

This v6 protocol is the active scoring lock for all benchmark tests after its freeze timestamp. Older v4/v5/v5.1/v5.2 protocols remain historical and may be used only for regression/autopsy unless explicitly selected with a separate run label.
