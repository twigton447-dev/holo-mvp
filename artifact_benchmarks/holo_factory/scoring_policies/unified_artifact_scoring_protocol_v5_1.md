# Unified Artifact Scoring Protocol v5.1 Candidate

Status: candidate until validated. Do not replace v5 or v4.1 yet.

## Boundary

This protocol is a candidate for cross-domain artifact scoring. It is designed for blind judging of decision-grade crisis reports against frozen task briefs and frozen source packets. It must not use artifact identity, generator identity, model identity, provider identity, run metadata, token burn, architecture evidence, or anonymization maps.

No provider calls, judging, scoring, unblinding, artifact edits, source edits, push, or benchmark proof claim are implied by this file.

## Purpose

v5.1 measures expert-survivability and risk suppression rather than generic writing quality. A fluent crisis brief can still fail if it invents sources, misstates source authority, misses negative space, mishandles contradictions, hides uncertainty, overclaims operational effect, or gives unsafe decision advice.

Any artifact may score highly if it satisfies the gates. This protocol does not encode an expected winner.

## Score Formula

Final score must be:

`min(raw_evidence_score_100, lowest_applicable_hard_cap, lowest_applicable_expert_ceiling)`

If admission fails, the artifact is diagnostic only and cannot receive proof credit or a top-band score.

## Layer 1: Admission Gate

An artifact must pass admission before normal scoring. Admission checks:

- responsive to task
- uses only frozen source packet
- no invented external sources
- no contestant identity leakage
- no architecture evidence leakage
- no provider, model, token-burn, run metadata, or benchmark-internal leakage
- required sections present
- contains a usable decision recommendation
- not empty, malformed, or substantially off-task

Admission failure result:

- diagnostic_only
- no proof credit
- no top-band score

## Layer 2: Mandatory Hard Caps

Hard caps are mandatory, not advisory. Apply the lowest applicable hard cap.

| cap_id | maximum final score |
|---|---:|
| invented_source_or_citation | 70 |
| false_source_attribution | 75 |
| material_source_misrepresentation | 75 |
| source_boundary_violation | 75 |
| central_data_stat_chart_error | 75 |
| missed_contradiction_changes_recommendation | 80 |
| unsupported_major_recommendation | 82 |
| unsafe_or_overconfident_operational_advice | 82 |
| generic_crisis_memo_low_operational_usefulness | 78 |
| failure_to_handle_uncertainty | 85 |
| severe_required_section_failure | 88 |
| reliance_critical_missing_caveat | 85 |
| stale_evidence_treated_as_current_or_decisive | 82 |
| draft_provisional_limited_source_treated_as_final_authority | 80 |
| material_negative_space_miss | 83 |
| no_clear_decision_recommendation | 83 |
| no_operational_stop_go_logic | 83 |

## Layer 3: Expert-Survivability Gates

An artifact cannot score above 83 unless all gates pass:

1. Source Fidelity Gate
2. Source-to-Claim Traceability Gate
3. Decision Logic Gate
4. Operational Specificity Gate
5. Uncertainty Gate
6. Contradiction and Negative-Space Gate
7. Risk-Suppression Gate
8. Expert Review Gate

The Risk-Suppression Gate rewards hallucination resistance, source-boundary discipline, blindspot detection, contradiction capture, stale or limited evidence handling, negative-space reasoning, overclaim suppression, and decision-safety framing.

## Layer 4: Weighted Raw Evidence Score

Use this 100-point raw score before caps and ceilings:

| category | points |
|---|---:|
| source fidelity and citation integrity | 15 |
| source-to-claim traceability | 10 |
| contradiction handling | 10 |
| uncertainty and limitation handling | 10 |
| data, stat, or chart interpretation | 8 |
| decision usefulness | 12 |
| operational actionability | 10 |
| risk suppression and blindspot avoidance | 15 |
| expert-review survivability | 10 |

## Layer 5: Ceiling Bands

- 0-69: unreliable, unsafe, fabricated, nonresponsive, or not decision-useful
- 70-82: competent-looking but not decision-grade
- 83 ceiling: maximum for artifacts that look good but fail any expert-survivability gate
- 84-89: decision-useful but not fully expert-survivable
- 90-94: expert-survivable
- 95-100: expert-ready; rare

## Layer 6: Required Top-Band Defect Audit

No artifact may score above 85 unless the judge completes all of these fields:

- why_not_100
- weakest_source_to_claim_link
- missing_or_underdeveloped_caveat
- unresolved_uncertainty
- biggest_overclaim_risk
- risk_if_leader_relied_on_it
- expert_reviewer_challenge
- needed_to_move_above_83
- needed_to_move_above_90
- needed_to_move_above_95
- material_repairs_required

No artifact may score above 90 unless at least two concrete avoided failure modes are named.

No artifact may score above 95 unless the why_not_100 audit is concrete and not generic.

## Layer 7: Pairwise Comparative Consistency

For `ARTIFACT_001` vs `ARTIFACT_003`, pairwise winners must be exact labels only:

- `ARTIFACT_001`
- `ARTIFACT_003`
- `TIE`

Pairwise dimensions:

- more_source_faithful
- more_decision_useful
- safer_to_rely_on
- better_uncertainty_handling
- better_contradiction_handling
- better_blindspot_detection
- better_hallucination_resistance
- better_overclaim_suppression
- more_operationally_actionable
- more_expert_survivable
- overall_winner

If pairwise and numeric ranking conflict, the judge must explain why.

## Layer 8: Deterministic Validator

The deterministic validator must fail if:

- final score exceeds an applicable hard cap
- final score exceeds an applicable expert ceiling
- score >83 while any expert-survivability gate is false
- score >90 without expert-review survivability rationale
- score >95 without concrete why_not_100 audit
- invented source or citation is present and final score >70
- false source attribution is present and final score >75
- material source misrepresentation is present and final score >75
- risk_suppression_gate_pass=false and final score >83
- no clear decision recommendation and final score >83
- no operational stop/go logic and final score >83
- pairwise labels are not exact artifact IDs
- raw judge text indicates a cap trigger but parsed caps are empty
- score above 85 lacks defect audit
- score above 90 lacks at least two named avoided failure modes
- source packet is missing but source-fidelity score is accepted

## Candidate Status

v5.1 remains candidate until D5 trial results are reviewed. It is not locked for D1-D5 future domains until explicitly frozen in a later lane.
