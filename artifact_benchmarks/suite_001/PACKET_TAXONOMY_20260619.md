# Holo Packet Taxonomy

Status: planning, not frozen, not benchmark credit.
Date: 2026-06-19

## Why This Exists

HoloBuild and HoloVerify overlap, but they should not be confused.

HoloBuild asks whether governed HoloAgents can create, improve, or repair better artifacts than solo models under identical conditions.

HoloVerify asks whether governed HoloAgents can check facts, boundaries, authority, policy, evidence, and action safety better than solo models under identical conditions.

The bridge is discrepancy work: inspect something trusted, find what is wrong or missing, and repair it without hallucinating or hindsight laundering.

## The Two Worlds

### HoloBuild World

Core verb: build.

Typical outputs:

- report
- memo
- deck
- legal ruling
- bench memo
- strategy packet
- clinical reasoning packet
- service design
- student plan
- product plan

Proof question:

Can Holo produce a materially better artifact than solo models from the same brief, source pack, turn budget, word band, and judging rubric?

### HoloVerify World

Core verb: verify.

Typical outputs:

- boundary decision
- source-grounding audit
- hallucination check
- authority check
- policy/action allow-or-block decision
- contradiction report
- safety gate
- evidence ledger

Proof question:

Can Holo prevent unsupported claims, unsafe actions, boundary violations, false positives, and false negatives better than solo models?

### Overlap World

Core verbs: dissect, compare, repair.

Typical outputs:

- discrepancy report
- postmortem
- premortem
- best-existing-artifact improvement
- ruling critique
- guideline gap analysis
- incident-plan failure analysis
- policy contradiction map

Proof question:

Can Holo inspect an already trusted artifact and find material discrepancies that solo models miss, while staying grounded and bounded?

## Packet Families

### 1. Blank-Slate Build Packet

Start state:

- brief
- source pack
- rubric
- no strong baseline artifact

Task:

Create the best possible artifact from scratch.

Best for:

- finance strategy report
- data-center strategy report
- cyber incident packet
- vendor risk memo
- hotel experience plan
- student decision packet

Primary metric:

Holo final score minus solo final score.

Risk:

Judges may reward polish over real insight unless the rubric heavily scores hidden failures and implementability.

### 2. Best-Existing-Artifact Improvement Packet

Start state:

- brief
- source pack
- strong baseline artifact

Task:

Improve an already good artifact.

Best for:

- legal memo revision
- board deck improvement
- clinical governance report improvement
- investment thesis repair
- service design refinement

Primary metric:

Holo-improved artifact minus solo-improved artifact, plus both versus baseline.

Why it matters:

This matches real client work. People usually have something already. Holo must find hidden weaknesses in good work, not merely beat a weak first draft.

### 3. Discrepancy Discovery Packet

Start state:

- predefined artifact people would be tempted to trust
- authority/source pack
- finding schema

Task:

Find discrepancies, contradictions, unsupported claims, missing assumptions, missing gates, or unhandled edge cases.

Best for:

- legal ruling versus precedent pack
- medical pathway versus guideline pack
- finance policy versus regulatory/market constraints
- cyber plan versus NIST/CISA/SEC obligations
- vendor claims versus contract and audit rights
- public report versus cited sources

Primary metric:

Material true discrepancies found minus false positives.

Why it matters:

This is the trust/insurance story. Holo finds what already-good work missed.

### 4. Known-Outcome Retrospective Packet

Start state:

- pre-event information only
- artifact or decision from before the outcome
- later known outcome kept out of generation context
- hidden answer key available only for evaluation

Task:

Identify failure modes that later became real, without hindsight.

Best for:

- public forecast failures
- court rulings later reversed or heavily criticized
- cyber incidents with postmortems
- medical safety failures in public case studies
- financial strategy failures
- product launch misses

Primary metric:

Did the model find the real failure mode from pre-event evidence, rank it correctly, and recommend a realistic repair?

Why it matters:

This is the strongest reality-grounded benchmark. It tests whether Holo can see the crack before history exposes it.

### 5. Competition / Court Packet

Start state:

- frozen fact pattern
- authority pack
- role rules
- output format

Task:

Run adversarial argument, counterargument, clerk analysis, majority/dissent, or final ruling.

Best for:

- moot Supreme Court opinions
- appellate bench memos
- legal debates
- policy debates
- strategy competitions
- product launch committee debates

Primary metric:

Reasoning quality, counterargument strength, precedent/source handling, administrability, and final decision clarity.

Boundary:

Not legal advice, not real-case adjudication, not a replacement for counsel or courts.

### 6. Medical Diagnostic Paradox Packet

Start state:

- synthetic case only
- guideline/source pack
- contradiction ledger
- red-flag/cannot-miss checklist

Task:

Produce a diagnostic reasoning and safety packet, not a diagnosis or treatment plan.

Best for:

- differential reasoning
- diagnostic error prevention
- red-flag detection
- missing-data analysis
- premature closure resistance

Primary metric:

Cannot-miss conditions preserved, contradictions identified, uncertainty stated, unsafe closure avoided.

Boundary:

No real patient data. No medical advice. No treatment instructions. Clinician authority remains explicit.

### 7. Experience Quality Packet

Start state:

- user/customer objective
- constraints
- source/context pack
- evaluation rubric

Task:

Design a better experience, plan, or recommendation artifact.

Best for:

- hotel stay recovery
- food/menu/restaurant operations
- travel plan
- college/student planning
- creator workflow
- service blueprint

Primary metric:

Quality lift, user usefulness, constraint fit, specificity, and implementation realism.

Why it matters:

This makes the value visceral. A measured lift in ordinary life is easier for people to feel than a technical governance result.

## Recommended Execution Order

1. Finance blank-slate build packet under current lock.
2. Finance best-existing-artifact improvement packet.
3. Finance discrepancy discovery packet.
4. Adversarial paradox packet.
5. Medical diagnostic paradox packet with synthetic data only.
6. Legal competition/court packet.
7. Experience quality packet for food/hotel/student workflows.

## Claim Discipline

Never say "Holo is X% better" without naming:

- packet family
- packet ID
- hash lock
- Holo cohort
- solo cohort
- Gov model
- judge panel
- turn budget
- source policy
- clean-only mean lift
- all-judge mean lift
- token ratio
- latency ratio
- invalid artifact rate

## The Simple Story

HoloBuild makes better things.

HoloVerify checks whether things are true, safe, and allowed.

Discrepancy packets prove the bridge: Holo can inspect trusted work, find what it missed, and repair it under evidence control.

