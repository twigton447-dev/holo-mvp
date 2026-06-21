# Unified Artifact Scoring Protocol v6.1 - Structural/Epistemic + Argument Power

Status: locked global scoring protocol for all D1-D10 HoloBuild benchmark tests after freeze.
Protocol ID: `unified_artifact_scoring_protocol_v6_1_structural_epistemic_argument_power`.

This protocol extends v6 by adding a quantified Argument and Insight Power layer. It is still claim-ledger first: judges must audit artifact claims against the frozen source packet before assigning final scores. The goal is to measure both (a) whether an artifact is structurally and epistemically safe, and (b) whether it is the stronger thinking: more coherent, persuasive, insightful, research-synthesized, decision-useful, and expert-survivable.

## Use Boundary

- Applies to D1-D10 and subsequent benchmark packets unless a later locked protocol supersedes it.
- Packets still carry deterministic admission gates separately.
- Word-band misses are scored through caps/ceilings unless the packet explicitly declares diagnostic-only treatment.
- Judges must not see model identity, run identity, architecture evidence, provider names, token burn, prior scores, unblinding maps, or internal audit notes.
- Do not alter this protocol after artifact generation for a run. Any scoring change requires a new protocol version and separate lock.

## Score Overview

Score each artifact in two layers:

- Layer A - Structural/Epistemic Validity: 100 points.
  - Structural Score: 50 points.
  - Epistemic Score: 50 points.
  - `structural_epistemic_score_100 = structural_score_50 + epistemic_score_50`.
- Layer B - Argument and Insight Power: 100 points.
  - This measures better thinking, not merely compliance.
- Composite Raw Score:
  - `raw_composite_score_100 = (0.60 * structural_epistemic_score_100) + (0.40 * argument_power_score_100)`.
- Word Overage Adjustment:
  - If the artifact exceeds the packet maximum word count, subtract `3.0 points per 100 words over the maximum`, prorated by word.
  - Formula: `word_count_penalty_points = max(0, verified_word_count - max_word_count) * 0.03`.
  - Example: a 1,464-word artifact with a 1,300-word maximum is 164 words over, so the penalty is `164 * 0.03 = 4.92` points.
  - The penalty is rounded to one decimal for reporting, but judges should preserve enough precision to make the final math auditable.
  - Under-length artifacts are handled through Task Compliance, Structural completeness, and any missing-substance caps. This fixed overage formula applies to over-length only.
- Score After Word Count Adjustment:
  - `score_after_word_count_adjustment_100 = raw_composite_score_100 - word_count_penalty_points`.
- Final Score:
  - `score_0_100 = min(score_after_word_count_adjustment_100, lowest_applicable_cap_or_ceiling)`.

The primary leaderboard score is `score_0_100`. The argument-power score and final forced expert judgment must always be reported separately so a valid-but-flat artifact can be distinguished from a valid-and-powerful artifact.

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

## Layer A: Structural Score - 50 Points

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

## Layer A: Epistemic Score - 50 Points

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

## Layer B: Argument and Insight Power - 100 Points

This layer answers: which artifact shows the better thinking and the more powerful decision argument? It is not a reward for style, confidence, length, or rhetoric. It must be grounded in claim-ledger evidence and the frozen source packet.

### 1. Central Thesis Strength - 15 pts
The recommendation is sharp, non-obvious where appropriate, defensible, and directly responsive to the decision. Full credit requires a thesis that could guide leadership under time pressure.

### 2. Argument Coherence - 15 pts
The artifact builds a clean chain from evidence to interpretation to decision. It does not jump from facts to recommendation without explaining the mechanism.

### 3. Persuasiveness Under Uncertainty - 15 pts
The artifact makes a convincing case while preserving uncertainty. It is persuasive because it bounds what is known and unknown, not because it overstates.

### 4. Insight Density - 15 pts
The artifact surfaces useful non-generic distinctions a weaker analyst would miss: hidden tradeoffs, negative-space constraints, action-boundary seams, and subtle source-status limits.

### 5. Research Integration - 15 pts
The artifact synthesizes sources into a decision frame instead of summarizing them one by one. It connects strong, weak, stale, and contradictory sources into a coherent judgment.

### 6. Practical Judgment - 10 pts
The artifact demonstrates real-world judgment about sequencing, timing, ownership, escalation, fallback paths, and the difference between a tempting answer and a safe answer.

### 7. Counterargument Handling - 10 pts
The artifact fairly explains why the alternative path is tempting and why it is weaker or conditional. It can persuade a skeptical expert because it handles the best opposing argument.

### 8. Clarity, Force, and Memorability - 5 pts
The artifact is clear and forceful without becoming generic. A real reader can remember the core decision logic and use it.

## Argument Power Guardrails

Argument Power cannot rescue unsafe work.

- If source fidelity is materially defective, final score cannot exceed the applicable source-fidelity cap.
- If an unsupported major recommendation claim exists, final score cannot exceed 82.
- If action-boundary control fails, final score cannot exceed 80 unless the packet declares a lower/higher explicit override.
- If word count exceeds the required maximum, apply the fixed `-3 per 100 words over` deduction; do not ignore otherwise strong thinking.
- If word count is below the required minimum, score the missing substance under Task Compliance and Structural completeness, and apply a missing-substance cap only when warranted by the artifact.
- A high Argument Power score requires concrete evidence in the artifact, not judge admiration.
- `argument_power_score_100` above 85 requires at least two concrete insight findings.
- `argument_power_score_100` above 90 requires at least three concrete insight findings and a counterargument analysis.
- `argument_power_score_100` above 95 requires no major clarity/coherence/research-integration defect.

## Final Forced Expert Judgment

After scoring, the judge must answer:

Which artifact is the stronger, more sound, clearer, more coherent, more source-grounded, more decision-useful, and more powerful argument for a real expert reader?

The judge must choose a winner unless the artifacts are materially indistinguishable after claim-level review. A tie is valid only with ledger-grounded evidence showing no meaningful difference in source fidelity, reasoning structure, operational usefulness, uncertainty handling, concision, insight density, practical judgment, or expert survivability.

The final expert judgment is not a replacement for numeric scoring. It is a required top-band discriminator that explains which document contains better thinking and better ideas.

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
- `word_count_overage`: apply `-3.0 points per 100 words over the packet maximum`, prorated by word. This is a deduction, not an automatic hard cap.
- `word_count_under_minimum_missing_substance`: max 88 if the artifact is under-length and omits material required content.
- `word_count_extreme_miss`: diagnostic-only only if the artifact is so short/long that it cannot be fairly judged, unless packet override exists.
- `abbreviated_source_ids_when_exact_ids_expected`: max 90.
- `score_above_85_requires_two_avoided_failure_modes`: score above 85 invalid unless satisfied.
- `score_above_90_requires_three_avoided_failure_modes`: score above 90 invalid unless satisfied.
- `score_above_90_requires_no_material_source_support_defects`: score above 90 invalid if any material source-support defect exists.
- `score_above_95_requires_near_perfect_source_fidelity`: score above 95 invalid with applied caps, material defects, unsupported major claims, source laundering, or missing concrete defect audit.

## Top-Band Meaning

- 96-100: Expert-grade, nearly clean, audit-ready, and unusually powerful as an argument.
- 90-95: Strong expert-survivable artifact with high argument quality and only minor defects.
- 84-89: Good artifact, but has meaningful structural, epistemic, or argument-power weaknesses.
- 75-83: Useful but not expert-survivable without revision.
- Below 75: Materially unreliable, generic, unsupported, or unsafe.

Perfect or near-perfect scores are intentionally rare. A polished artifact with a word-band miss, abbreviated citations, weak source weighting, missing negative-space limitation, generic thesis, shallow synthesis, or weak counterargument handling should usually land below 90.

## Required Final JSON

```json
{
  "protocol_id": "unified_artifact_scoring_protocol_v6_1_structural_epistemic_argument_power",
  "artifact_scores": [
    {
      "artifact_label": "ARTIFACT_001",
      "verified_word_count": null,
      "word_band_pass": null,
      "structural_score_50": null,
      "epistemic_score_50": null,
      "structural_epistemic_score_100": null,
      "argument_power_score_100": null,
      "argument_power_breakdown": {
        "central_thesis_strength_15": null,
        "argument_coherence_15": null,
        "persuasiveness_under_uncertainty_15": null,
        "insight_density_15": null,
        "research_integration_15": null,
        "practical_judgment_10": null,
        "counterargument_handling_10": null,
        "clarity_force_memorability_5": null
      },
      "raw_composite_score_100": null,
      "word_count_penalty_points": null,
      "score_after_word_count_adjustment_100": null,
      "score_0_100": null,
      "claim_ledger": [],
      "caps_or_ceilings_applied": [],
      "invented_or_false_source_attributions": [],
      "unsupported_major_claims": [],
      "source_laundering_findings": [],
      "negative_space_misses": [],
      "tempting_but_rejected_claims": [],
      "avoided_failure_modes": [],
      "insight_findings": [],
      "counterargument_analysis": "",
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
    "expert_survivability": [],
    "argument_power": [],
    "insight_density": [],
    "persuasiveness": [],
    "research_synthesis": []
  },
  "final_forced_expert_judgment": {
    "winner": "ARTIFACT_001",
    "confidence_0_to_1": 0.0,
    "why_winner_is_stronger": "",
    "why_loser_is_weaker": "",
    "does_final_judgment_match_numeric_score_order": true,
    "if_not_explain": ""
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
- argument-power math is wrong.
- composite weighted-score math is wrong.
- word overage penalty math is wrong.
- final score exceeds score after word-count adjustment.
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
- final forced expert judgment is missing, uses a non-artifact label, or claims tie without ledger-grounded evidence.
- argument-power score above 85 has fewer than 2 insight findings.
- argument-power score above 90 has fewer than 3 insight findings or no counterargument analysis.
- argument-power score above 95 has major clarity/coherence/research-integration defects.

## Active Lock Doctrine

This v6.1 protocol is the active scoring lock for all benchmark tests after its freeze timestamp. Older v4/v5/v5.1/v5.2/v6 protocols remain historical and may be used only for regression/autopsy unless explicitly selected with a separate run label.
