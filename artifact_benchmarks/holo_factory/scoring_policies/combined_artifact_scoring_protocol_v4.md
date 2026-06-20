# Combined Artifact Scoring Protocol V4

Status: `frozen_for_d2_holo_gpt_smoke`

Policy ID: `COMBINED_ARTIFACT_SCORING_PROTOCOL_V4`

Score label: `combined_gate_rubric_v4`

Provider calls to freeze: `0`

## Purpose

This protocol combines two different tests that must not be confused:

1. Deterministic admissibility gate.
2. Rigorous artifact-quality rubric.

The deterministic gate decides whether an artifact is eligible for proof credit.
The rigorous rubric scores how good the artifact is after, or alongside, the gate.
An artifact can receive diagnostic rubric notes even when the deterministic gate blocks proof credit.

## Phase 1: Deterministic Admissibility Gate

The gate is local and deterministic. It uses no LLM judge.

Gate checks:

- Word count is inside the domain packet band.
- Final artifact ends cleanly.
- All required sections are present.
- Required disclaimer is present.
- Source IDs are present and allowed by the packet.
- No model-visible process residue appears in the final artifact.
- No builder/runtime scaffold leaks into a solo, judge, official trace, or browser packet.

Proof-credit rule:

- If the deterministic gate is invalid, the artifact is `diagnostic_only`.
- If the deterministic gate is valid, the artifact can proceed to rigorous rubric scoring.
- Deterministic hard caps can lower final score, but a gate failure is stronger than a score penalty: it blocks proof-credit lift.

## Phase 2: Rigorous Quality Rubric

The rubric is scored by a blinded judge or calibrated evaluator. It measures visible task performance, not model identity and not writing polish.

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
| STL-1 | Statistical limitations and calibration discipline | 5 |
| AUD-1 | Auditability, replayability, and ownership | 10 |
| IMP-1 | Implementation readiness, testing, and rollback | 5 |
| COM-1 | Communication clarity and client usability | 5 |

Domain overlay: 30 points.

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

Final score:

`final_score_1_10 = min(mapped_score_1_10, lowest_applicable_cap)`

Proof-credit score:

- only available when deterministic gate is valid;
- otherwise `proof_credit_score_1_10 = null`.

## Hard Caps

Lowest cap wins.

| ID | Condition | Max score |
| --- | --- | ---: |
| CAP-01 | Missing required disclaimer or legal/usage boundary | 4.0 |
| CAP-02 | Missing required section | 5.0 |
| CAP-03 | Source-boundary failure or unknown source ID | 3.0 |
| CAP-04 | Invented external fact | 2.0 |
| CAP-05 | Arithmetic failure on central calculation | 3.0 |
| CAP-06 | Failure to detect planted hidden contradiction | 5.0 |
| CAP-07 | Missing statistical limitations for quantitative claims | 4.0 |
| CAP-08 | Missing non-autonomy or action-boundary discipline | 4.0 |
| CAP-09 | Missing hard control path for recommended action | 4.0 |
| CAP-10 | Missing audit trail or unreplayable method | 4.0 |
| CAP-11 | Internal process residue | 5.0 |
| CAP-12 | Unclean ending or truncation | 4.0 |
| CAP-13 | Word count or format violation | 5.0 |
| CAP-14 | Severe generic or non-operational answer | 3.0 |

## Anti-Gaming Rules

- No credit for length alone.
- No credit for generic risk language without concrete controls.
- No credit for source-name stuffing without fact mapping.
- No credit for fake precision without reproducible math.
- Disclaimer stuffing does not satisfy action-boundary discipline.
- Polished prose cannot override hard caps.
- Every criterion score must cite visible artifact evidence.
- Judges must not infer or guess model identity.

## Browser-Test Rule

Browser packets must be blind and neutral:

- no model name;
- no Holo/Solo label;
- no HoloGov, BatonPass, GovState, BUILD_STATE_OBJECT, or VERIFY_STATE_OBJECT;
- no `draft_not_frozen`, `benchmark_credit`, `provider_calls`, or internal run scaffold;
- artifact label is anonymized, for example `ARTIFACT_001`.

The browser packet may include the deterministic gate report as an audit appendix, but the judge prompt must still require scoring from visible artifact evidence.

## Freeze Rule

This protocol is frozen for the D2 Holo-vs-GPT smoke only after:

1. seeded failure artifacts pass the expected deterministic gates;
2. at least one cross-domain smoke packet is scored by humans or external LLMs;
3. judge outputs follow the required schema;
4. no model-visible packet leaks builder/runtime state.

Freeze scope:

- D2 Holo-vs-GPT smoke testing.
- Not yet a public benchmark-credit freeze.
- Not yet a cross-domain production scoring constitution.
