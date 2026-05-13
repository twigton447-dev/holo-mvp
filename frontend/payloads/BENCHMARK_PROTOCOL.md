# Holo Benchmark Protocol

This document describes the public methodology used in the Holo benchmark. Full adversarial role prompts, convergence logic, Governor verdict rules, and model routing configuration are available to qualified technical reviewers under NDA.

> The public benchmark demonstrates the existence of action-boundary blind spots. It does not disclose the proprietary Governor logic, adversarial reactor configuration, model-routing rules, convergence heuristics, or private trace library used in Holo's production architecture.

---

## What the payload files contain

Each scenario JSON file contains only the case facts and artifacts that were presented to each model during evaluation: the proposed action, the email thread, vendor records, attachment summaries, domain intelligence, and organizational policies. Nothing else.

No verdict labels, answer keys, fraud classifications, or scoring rubrics are included in these files. That information was never in the model context during the benchmark and is not here now.

---

## Evaluation conditions

Every scenario runs under four conditions:

| Condition | Setup | What it tests |
|-----------|-------|---------------|
| Solo one-pass | 1 frontier model, 1 turn | Status quo baseline |
| Solo multi-pass | 1 model, multiple adversarial turns | "Just prompt it better" |
| Parallel multi-LLM | 3 frontier models, isolated, no governor | "We already use multiple LLMs" |
| Holo full architecture | 3 frontier models + deterministic governor | The isolated architectural variable |

The solo conditions use the same frontier models that run inside Holo. Same models. Same scenario. Same context. The only variable is structure.

---

## Turn protocol (high level)

- Maximum turns: 10 per condition
- Conditions may converge early when evidence is sufficient
- Models do not decide when the test is complete — convergence is detected externally
- No synthesis turn — the final verdict is computed algorithmically, not inferred from the last model output

Each turn produces a verdict (ALLOW or ESCALATE) and severity ratings across six risk categories. The written reasoning for each turn is the audit trail.

---

## Adversarial role structure

Each turn assigns a distinct adversarial role — Initial Assessment, Assumption Attacker, Edge Case Hunter, Evidence Pressure Tester, and others through turn 10. Role assignments are designed to manufacture structured disagreement and prevent any single model's reasoning from anchoring the analysis.

The exact role prompt text, role sequence logic, and model assignment rules are proprietary and not included in public materials.

---

## Holo adjudication

In the Holo condition, structurally different model families are assigned across turns. The final verdict is computed by a deterministic governor that applies fixed, auditable rules to the accumulated evidence. The governor does not summarize or synthesize — its output does not vary with model confidence, rhetorical force, or turn order.

The specific rules the governor uses are proprietary.

---

## Solo vs. Holo baseline

The solo-model baselines used the same role structure and turn budget as Holo. The only variable removed is structural independence: in solo runs, one model plays every role. In Holo runs, different model families are assigned across turns, and the final verdict is computed by a deterministic governor.

---

## Model selection and parity

The same model versions used in the solo baselines were used inside the Holo adjudication condition. The benchmark compares decision architectures, not model capability:

- Single-model baseline judgment
- Single-model adversarial scaffold
- Multi-model adversarial adjudication with deterministic governor logic

The question is not which model is smartest. The question is whether a structured action-boundary adjudication process produces a safer, more inspectable decision than relying on one model family alone.

---

## Private review

Full traces, complete adversarial role prompts, Governor configuration, model routing rules, convergence heuristics, and reproducibility materials are available to qualified technical reviewers under NDA.

Contact: hello@holoengine.ai
