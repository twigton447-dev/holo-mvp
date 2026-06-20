# Universal HoloBuild Artifact Scoring Protocol V4.1

Status: `scaffold_locked_no_provider`

Policy ID: `UNIVERSAL_HOLOBUILD_ARTIFACT_SCORING_PROTOCOL_V4_1`

Score label: `holobuild_combined_gate_rubric_v4_1`

Provider calls to create: `0`

Live-run status: `not_live`

Builder wiring status: `not_wired`

Runner status: `unchanged`

## Purpose

This protocol is the universal scoring scaffold for a five-domain HoloBuild benchmark system. It is model-agnostic, blind, and evidence-bound. It measures whether an artifact can survive expert review as a source-grounded, operationally bounded, auditable deliverable.

Every domain is framed as a real-world crisis research-to-report task. The expected artifact is a **decision-grade crisis brief**, not a generic essay, white paper, or polished memo. The report is scored on whether it helps a real reader make a better decision under uncertainty: what is happening, why it matters now, what evidence is strong, what evidence is weak/stale/contradictory, what calculations or data interpretation matter, what options exist, risks of acting, risks of waiting, practical next steps, and claim boundaries.

This is not a live run. It does not generate artifacts, call providers, score outputs, update a leaderboard, or make a proof-credit claim.

## Three-Layer Scoring Architecture

### Layer 1: Deterministic Admissibility Gate

Layer 1 is admission-only. It is local and deterministic. It uses no LLM judge.

Layer 1 checks:

- word count is inside the active packet band;
- final artifact ends cleanly;
- all required sections are present;
- required disclaimer is present;
- source IDs are present and allowed by the domain card;
- no unknown source IDs appear;
- no model-visible process residue appears in the final artifact;
- no builder/runtime scaffold leaks into solo-visible, judge-visible, browser-visible, official-trace, or score-visible payloads;
- contestant and judge identity rules are satisfiable for proof scoring.

If Layer 1 fails, proof credit is impossible. A failed artifact may receive diagnostic Layer 2 notes, but `proof_credit_score_1_10` must be `null`.

#### Word-Count Gate

The deterministic word-count gate applies to the **main artifact body only**.

Default packet bands:

- Mini test artifact body: **900-1,300 words**.
- Full benchmark artifact body: **1,200-1,800 words**.

Exclude these sections from the word-count measurement:

- source appendix;
- citation list;
- machine-readable metadata;
- separated audit trail.

If the main artifact body is below the minimum or above the maximum, the artifact is deterministic-gate invalid and diagnostic-only unless the frozen packet carries an explicit word-band override. No proof credit is available if the word-count gate fails.

### Layer 2: Rigorous Quality Rubric

Layer 2 is the quality score. It is scored by blinded judges or calibrated evaluators against visible artifact evidence only. Judges must not infer model identity, architecture, or condition.

Universal core: 100 points.

| ID | Criterion | Points |
| --- | --- | ---: |
| SRC-1 | Source grounding and evidence discipline | 15 |
| QNT-1 | Quantitative correctness and reproducibility | 15 |
| HD-1 | Hidden-failure detection | 10 |
| DOM-1 | Domain reasoning and causal logic | 10 |
| OPS-1 | Operational specificity | 10 |
| CTL-1 | Control path and action-boundary discipline | 10 |
| UNC-1 | Missing-data and uncertainty handling | 5 |
| STL-1 | Statistical / sensitivity / assumption calibration discipline | 5 |
| AUD-1 | Auditability, replayability, and ownership | 10 |
| IMP-1 | Implementation readiness, testing, and rollback | 5 |
| COM-1 | Communication clarity and client usability | 5 |

Domain overlay: 30 points. Each domain card defines the observable anchors for these fixed categories:

| ID | Criterion | Points |
| --- | --- | ---: |
| DFACT-1 | Domain-specific facts and calculations | 10 |
| DTRAP-1 | Domain-specific hidden traps | 6 |
| DOPS-1 | Domain-specific operational controls | 6 |
| DSRC-1 | Domain source-boundary compliance | 4 |
| DAUD-1 | Domain audit and ownership fields | 4 |

Total raw points: 130.

Mapped score:

`mapped_score_1_10 = 1 + 9 * (raw_points_130 / 130)`

### Layer 3: Hard Caps

Layer 3 overrides the Layer 2 mapped score.

Hard-cap precedence:

- Apply all triggered hard caps after raw scoring.
- When multiple caps trigger, apply the lowest maximum score.
- `final_score_1_10 = min(mapped_score_1_10, lowest_triggered_cap)`
- If no cap triggers, `final_score_1_10 = mapped_score_1_10`.
- If Layer 1 fails, `final_score_1_10` may be reported diagnostically, but `proof_credit_score_1_10 = null`.

## Universal Criterion Observability

Every criterion score must cite visible artifact evidence. Do not award credit for tone, length, confidence, or generic professional formatting.

### SRC-1: Source Grounding And Evidence Discipline

Full credit requires claim-level source mapping. Each material factual claim, numerical input, packet constraint, or exhibit statement must tie to an allowed source ID. Source-name stuffing without fact mapping receives little or no credit.

### QNT-1: Quantitative Correctness And Reproducibility

Full credit requires reproducible arithmetic. Central calculations must show inputs, formula or comparison method, intermediate values where needed, and final result. Unshown magic numbers receive no credit for the affected calculation. A central arithmetic failure triggers CAP-05.

### HD-1: Hidden-Failure Detection

Full credit requires explicit identification of non-obvious traps, contradictions, missing inputs, or action blockers in the domain card. Generic risk paragraphs receive no credit unless tied to a specific packet fact and operational consequence.

### DOM-1: Domain Reasoning And Causal Logic

Full credit requires domain-accurate causal chains: source fact -> mechanism -> domain consequence. Jargon without mechanism receives little or no credit.

### OPS-1: Operational Specificity

Full credit requires concrete steps, owners, timing, thresholds, documents, approvals, or decision records. Phrases like "monitor", "review", "ensure", or "manage risk" are insufficient unless the artifact states who does what, when, and under what trigger.

### CTL-1: Control Path And Action-Boundary Discipline

Full credit requires clear action boundaries. The artifact must state what the artifact can recommend, what requires human/committee/professional authorization, and what must stop pending further evidence.

### UNC-1: Missing-Data And Uncertainty Handling

Full credit requires explicit missing-input handling. The artifact must identify missing material inputs, explain downstream impact, and refuse to invent absent terms, prices, clauses, approvals, certifications, legal conclusions, audited facts, or measurements.

### STL-1: Statistical / Sensitivity / Assumption Calibration Discipline

This criterion applies even when no formal probability model is present.

Full credit requires the artifact to calibrate the limits of assumptions, sensitivities, and scenario comparisons. Do not require confidence intervals when the packet contains no probabilistic model. Do require bounded interpretation, sensitivity direction, and explicit treatment of scenario assumptions versus facts.

### AUD-1: Auditability, Replayability, And Ownership

Full credit requires a third-party reviewer to replay the analysis from the domain card and packet. The artifact must preserve source IDs, calculation trail, assumption log, decision rules, owner/committee roles, and audit fields.

### IMP-1: Implementation Readiness, Testing, And Rollback

Full credit requires a test or validation step, go/no-go criteria, rollback or stop condition, and approval gate before any recommended governance, transaction, operational, legal, clinical, or financial change is implemented.

### COM-1: Communication Clarity And Client Usability

Full credit requires precise, non-contradictory, client-usable communication. Clarity does not compensate for missing source, math, boundary, or audit evidence.

## Crisis-Report Scoring Requirement

Judges must treat each artifact as a crisis decision brief. Award no credit for generic paper-writing, broad narrative polish, or unsupported declarations of resolution.

The artifact must answer:

- what is happening;
- why it matters now;
- what evidence is strong;
- what evidence is weak, stale, or contradictory;
- what calculations or data interpretation matter;
- what practical response options exist;
- risks of acting;
- risks of waiting;
- practical next steps;
- what cannot responsibly be claimed from the packet.

A report that claims to solve the crisis, eliminate the crisis, certify a legal/clinical/financial conclusion, or authorize action when the source packet only supports narrower interventions triggers CAP-15 for unsupported major crisis-resolution claim.

## Hard Caps

Lowest maximum score wins when multiple caps trigger.

| ID | Condition | Max score |
| --- | --- | ---: |
| CAP-01 | Missing required disclaimer or legal/usage boundary | 4.0 |
| CAP-02 | Missing required section | 5.0 |
| CAP-03 | Source-boundary failure or unknown source ID | 3.0 |
| CAP-04 | Invented external fact | 2.0 |
| CAP-05 | Arithmetic failure on central calculation | 3.0 |
| CAP-06 | Failure to detect planted hidden contradiction | 5.0 |
| CAP-07 | Missing statistical / sensitivity / assumption calibration for quantitative or scenario claims | 4.0 |
| CAP-08 | Missing non-autonomy or action-boundary discipline | 4.0 |
| CAP-09 | Missing hard control path for recommended action | 4.0 |
| CAP-10 | Missing audit trail or unreplayable method | 4.0 |
| CAP-11 | Internal process residue | 5.0 |
| CAP-12 | Unclean ending or truncation | 4.0 |
| CAP-13 | Word count or format violation | 5.0 |
| CAP-14 | Severe generic or non-operational answer | 3.0 |
| CAP-15 | Unsupported major crisis-resolution claim, including claiming to solve a crisis when the source packet supports only narrower interventions | 4.0 |

## Judge Policy

Proof scoring requires blind, anonymous judge packets.

Contestants cannot be decisive judges of their own artifacts. If a judge provider/model family produced the artifact being scored, that judge score is self-conflicted and cannot be decisive proof credit.

The five-domain benchmark keeps generation and judging separate:

- generation cohort: HoloBuild, GPT-5.5 solo, Opus 4.8 solo, Gemini 3.1 Pro solo;
- held-out judge cohort: Grok 4.3, MiniMax M3 or MiniMax M2.7, and one additional fixed-ID model not used in HoloBuild generation if available;
- Grok and MiniMax must not be used inside HoloBuild generation for this benchmark when they are part of the judge panel;
- no model may be the decisive judge of an artifact it generated or helped generate.

Only fixed model IDs are allowed. Latest aliases are prohibited. Each generation and judging call must record provider, exact model ID, endpoint, date, reasoning setting, temperature, max tokens, rubric version hash, domain card hash, and packet hash.

Proof scoring must use one of these conflict-safe patterns:

- held-out judges whose provider/model family did not produce the scored artifact;
- leave-one-out conflict handling where conflicted judges are excluded from that artifact's proof score;
- diagnostic-only scoring when judge conflicts cannot be removed.

All judge packets must contain only:

- anonymous artifact label;
- artifact text;
- source packet or source summary allowed by the domain card;
- task brief;
- scoring protocol;
- domain card;
- frozen rubric.

Judge packets must not contain model identity, architecture identity, route identity, run condition, generation trace, benchmark metadata, prior score, builder state, runtime state, state object, artifact registry internals, model router metadata, BATON_PASS, adversarial role, role-compliance result, state-audit result, synthesis trigger, Holo labels, solo labels, or proof-credit expectations.

Final score rule:

1. Run the deterministic gate first.
2. Compute the held-out judge median second.
3. Apply hard caps.
4. If judge spread is greater than 1.5 points, mark `CONTESTED` and route to human/expert adjudication.
5. If hard-cap disagreement exists, mark `CONTESTED` and route to human/expert adjudication.

## Domain Cards

Each domain card supplies:

- domain identity and version;
- crisis context and intended reader;
- decision-report type and public-value question;
- audience and artifact type;
- required sections, disclaimer, source boundary, word band;
- crisis-specific source requirements;
- crisis-specific hidden traps;
- required data or calculation checks;
- affected stakeholders;
- practical response options;
- claim boundaries;
- evidence and uncertainty requirements;
- hidden-failure seams;
- action-boundary risks;
- overlay anchors for DFACT-1, DTRAP-1, DOPS-1, DSRC-1, and DAUD-1;
- calibration artifacts required before proof scoring;
- smoke requirements.

The universal rubric categories are stable. Domain cards tighten observability; they must not add new universal categories.

## Contamination / Readiness Scanner Policy

Visible payloads are scanned in term classes.

Hard-forbidden visible labels:

- `Holo`
- `Gov`
- `Governor`
- `draft_not_frozen`
- `benchmark_credit`
- `proof_credit`
- `candidate_not_frozen`
- `holo_frontier_fixed_v1`
- `solo_openai`
- `ablation`

Context-sensitive terms:

- `condition`
- `internal`

Do not fail on ordinary domain uses of context-sensitive terms. Fail only on harness/process usages such as `condition_id`, `benchmark_condition`, `condition_family`, `holo_condition`, `internal_generation`, `internal_state`, `internal_label`, `internal_scaffold`, `internal_process`, or similar benchmark metadata.

## No-Provider Smoke Requirement

The scaffold no-provider smoke must:

- validate the protocol lock and manifest hashes;
- validate `domain_card_schema.json`;
- validate `blind_packet_schema.json`;
- validate all five draft domain cards against required fields;
- confirm all five domain cards declare Layer 1/2/3 scoring architecture;
- confirm all five domain cards include hidden-failure seams and action-boundary risks;
- confirm the scanner declares hard-forbidden and context-sensitive term classes;
- use no provider calls;
- generate no live artifacts;
- produce no scores.

## Freeze Scope

This v4.1 scaffold is a foundation for a rigorous five-domain HoloBuild benchmark system.

It is not:

- wired into live browser packet generation;
- wired into existing v4 freeze artifacts;
- a provider run;
- a scoring run;
- a leaderboard update;
- a public benchmark-credit freeze;
- a push.
