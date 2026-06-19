# Domain Expansion Backlog

Status: exploratory, not frozen, not benchmark credit.
Date: 2026-06-19

## Why Expand

The finance packet proves the core shape: same packet, same turn budget, same HoloAgent loop, same solo baselines, same judge panel, and measured lift. The next benchmark layer should test whether the lift appears across many artifact types, not only finance.

The expansion goal is not to claim Holo solves every problem. The goal is to measure where governed recursive HoloAgent work produces better artifacts than solo recursive work under identical conditions.

## Candidate Expansion Tracks

### 1. Medical Diagnostic Paradoxes

Use synthetic medical cases only. No real patient data, no patient-specific advice, no treatment instructions.

What this tests:

- Differential diagnosis under contradictory signals.
- Red-flag detection.
- Premature closure resistance.
- Missing-data identification.
- Separation of observed facts, inference, uncertainty, and escalation.

Why it matters:

Solo models can sound clinically confident too early. Holo should show lift by preserving uncertainty, catching cannot-miss conditions, asking better next questions, and producing a safer reasoning packet.

### 2. Random / Adversarial Paradoxes

Use deliberately contradictory briefs where a smooth answer is usually wrong.

What this tests:

- Contradiction preservation.
- Impossibility detection.
- Tradeoff reasoning.
- Refusal of impossible requirements while still producing a useful plan.
- Auditability of assumptions.

Why it matters:

This is the purest architecture test. It strips away domain prestige and asks whether Holo is better at seeing the trap.

### 3. Experience Quality Domains

Examples: food, hotel, travel, education, college/student workflows, service operations.

What this tests:

- Whether measured lift appears in everyday, emotionally legible artifacts.
- Whether cheaper mini HoloAgent cohorts can outperform solo minis for practical users.
- Whether the value is obvious without high-stakes technical framing.

Why it matters:

People understand "better hotel experience," "better meal plan," "better student decision packet," or "better service recovery memo" immediately. These domains can make the benchmark visceral.

## Measurement Rule

Do not use a floating "better" claim. Every claim must name:

- packet ID
- hash lock
- Holo cohort
- solo cohort
- Gov model
- judge panel
- turn budget
- word band
- number of judged runs
- clean-only mean lift
- all-judge mean lift
- token and latency ratio
- invalid artifact rate

## Promotion Rule

A candidate track becomes benchmark-ready only after:

1. Scenario skeleton exists.
2. Source allowance is defined.
3. Rubric domain notes exist.
4. Deterministic validity gate exists.
5. No-provider smoke passes.
6. Live run is approved separately.
7. Rollup script can include the run without manual spreadsheet work.

## Current Candidate Skeletons

- `domain_skeletons/medical_diagnostic_paradox.json`
- `domain_skeletons/adversarial_paradox_reasoning.json`

