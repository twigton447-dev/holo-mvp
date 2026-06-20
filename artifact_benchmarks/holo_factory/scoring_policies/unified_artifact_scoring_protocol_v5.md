# Unified Artifact Scoring Protocol v5 Candidate

Status: candidate until validated. Do not replace v4.1 yet.

## Boundary

No providers, judging, scoring, unblinding, artifact edits, source-packet edits, or push are implied by this protocol file. This file defines a candidate scoring method only.

Do not tune this protocol to favor any artifact. Do not use system identity. Do not use the anonymization map. Score only blind artifact content against the task brief, source packet, domain card, and this protocol.

## Problem

The previous broad numeric scoring pass ceilinged out and gave the three strong D5 artifacts effectively the same score. The secondary blind discrimination pass separated them, but that creates two separate scoring layers.

## Goal

Create one consistent scoring method that both:

1. Brings the floor down when an artifact is flawed, generic, invalid, overclaims, misses sources, or fails the task.
2. Separates the top end when all artifacts are strong but one is materially better.

## Core Doctrine

HoloBuild value lives in the 85-100 quality band. Frontier solos can often produce competent work. The scorer must punish real failures below 85, but also distinguish good, strong, expert-grade, and exceptional artifacts above 85.

No top-band score is allowed without a concrete defect audit.

## Layer 1: Deterministic Admission Gate

Checks:

- artifact body exists
- word count valid
- required sections present
- source packet used
- no invented source IDs
- no forbidden leakage
- no process residue
- no missing artifact text

If Layer 1 fails:

- diagnostic_only
- no proof credit
- no top-band score

## Layer 2: Hard Caps

Hard caps override the raw score. Use the lowest applicable cap.

| Hard Cap | Maximum Score |
|---|---:|
| invented source or invented citation | 70 |
| material source misrepresentation | 75 |
| central data/stat/chart error | 75 |
| missed contradiction that changes the recommendation | 80 |
| unsupported major recommendation | 82 |
| unsafe or overconfident operational advice | 82 |
| generic crisis memo / low operational usefulness | 78 |
| source-boundary violation, including treating FDA draft/advisory/press material as final approval | 75 |
| failure to handle uncertainty | 85 |
| severe format or required-section failure | 88 |

## Layer 3: 100-Point Evidence Score

| Category | Points |
|---|---:|
| source fidelity | 15 |
| source-to-claim traceability | 10 |
| contradiction handling | 10 |
| uncertainty and limitations | 10 |
| data/stat/chart interpretation | 10 |
| decision usefulness | 15 |
| operational actionability | 10 |
| overclaim discipline | 10 |
| expert-review survivability | 10 |

## Layer 4: Top-Band Differentiator Baked Into Final Score

This is not a separate ranking layer. It must affect final_score_100.

Scores above 85 require a top-band defect audit.

Top-band thresholds:

- Above 85 requires artifact to be clearly usable and source-grounded.
- Above 90 requires no material source misuse and decision-useful guidance.
- Above 93 requires strong contradiction handling, uncertainty handling, and operational risk handling.
- Above 95 requires expert-survivability with only minor edits.
- Above 98 requires no material defect found after explicit top-band audit.

Every score above 85 must answer:

- what keeps this from 100?
- weakest source-to-claim link
- most important missing caveat
- most important unresolved uncertainty
- biggest overclaim risk
- biggest risk if a healthcare leader relied on it
- what an expert reviewer would challenge first
- what would move it from 90 to 95?
- what would move it from 95 to 98?

If a judge cannot name concrete defects, it cannot award a top-band score.

## Layer 5: Forced Comparative Consistency

When scoring multiple artifacts from the same packet, the judge must:

- assign final_score_100 to each artifact
- assign forced_rank_order_best_to_worst
- identify pairwise winners
- explain why each lower-ranked artifact lost
- ensure scores and rankings are consistent

No ties unless explicitly marked CONTESTED with reason.

## Required Judge Output JSON

```json
{
  "artifact_scores": [
    {
      "artifact_label": "ARTIFACT_001",
      "deterministic_gate": "pass|fail",
      "hard_caps": [],
      "raw_evidence_score_100": 0,
      "final_score_100": 0,
      "final_score_10": 0,
      "score_band": "below_proof|85_90_usable|90_93_strong|93_95_expert_grade|95_98_expert_survivable|98_100_exceptional",
      "forced_rank_position": 0,
      "source_fidelity_findings": [],
      "source_to_claim_findings": [],
      "contradiction_findings": [],
      "uncertainty_findings": [],
      "decision_usefulness_findings": [],
      "operational_actionability_findings": [],
      "top_band_defect_audit": {
        "what_keeps_it_from_100": "",
        "weakest_source_to_claim_link": "",
        "missing_caveat": "",
        "unresolved_uncertainty": "",
        "biggest_overclaim_risk": "",
        "risk_if_leader_relied_on_it": "",
        "expert_reviewer_challenge": "",
        "needed_to_move_90_to_95": "",
        "needed_to_move_95_to_98": ""
      },
      "invented_sources": [],
      "source_misrepresentations": [],
      "unsupported_claims": [],
      "would_survive_expert_review": true,
      "confidence": 0
    }
  ],
  "forced_rank_order_best_to_worst": [],
  "pairwise_winners": {
    "ARTIFACT_001_vs_ARTIFACT_002": "",
    "ARTIFACT_001_vs_ARTIFACT_003": "",
    "ARTIFACT_002_vs_ARTIFACT_003": ""
  },
  "best_artifact_label": "",
  "worst_artifact_label": "",
  "ranking_score_consistency_check": "",
  "overall_rationale": ""
}
```
