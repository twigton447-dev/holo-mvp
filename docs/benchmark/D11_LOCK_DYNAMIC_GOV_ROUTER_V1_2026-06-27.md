# D11-Lock Dynamic Gov Router V1

Date: 2026-06-27

Classification: `D11_LOCK_DYNAMIC_GOV_ROUTER_V1`

## Core Lock

Gov does not choose models.

Gov chooses control actions.

The model roster, model order, randomization seed, and fallback policy belong to the run lock. Gov may not select, substitute, rank, prefer, or avoid a model. This prevents Gov from introducing model-selection bias while preserving Gov's role as the stateful adversarial control layer.

## Purpose

This architecture hardens D11-lock Holo from a fixed 7-turn benchmark loop into a commercial-grade control router.

The benchmark loop proved the value of stateful adversarial governance. The product loop must also optimize:

- correctness
- token burn
- latency
- auditability
- fail-closed behavior

Dynamic routing is how Gov reduces wasted turns without weakening the hard gates.

## Allowed Gov Control Actions

Gov may emit exactly one control action per baton:

- `CONTINUE`: continue the locked sequence because useful work remains.
- `REPAIR`: repair named deterministic, epistemic, structural, or argument defects.
- `TARGETED_HUNTER`: direct the next locked worker to attack a specific vulnerability.
- `PRESERVE_LOCKED`: preserve the pinned best artifact and block reinvention.
- `EARLY_EXIT_TO_FINAL_COMPILER`: stop the loop early because the artifact is already admissible and stable.
- `FINAL_COMPILER`: route to final compiler under the run lock.
- `FAIL_CLOSED`: stop because a blocker, provider failure, prompt violation, or integrity failure makes the lane invalid.

Gov may not emit a model name as a route verdict.

## Forbidden Gov Actions

Gov may not:

- choose the next model
- choose the next provider
- substitute a model
- choose a fallback model
- route away from a model because of preference
- route toward a model because of preference
- hide model availability failures
- convert a randomized/locked model order into a Gov-selected order

Any Gov payload containing `model`, `selected_model`, `worker_model`, `provider`, `selected_provider`, `model_choice`, or equivalent model-selection fields is invalid under this lock.

## Required Gov Control Object

Every Dynamic Gov Router control object must contain:

```json
{
  "gov_mode": "CONTROL_ROUTER",
  "route_verdict": "CONTINUE | REPAIR | TARGETED_HUNTER | PRESERVE_LOCKED | EARLY_EXIT_TO_FINAL_COMPILER | FINAL_COMPILER | FAIL_CLOSED",
  "burn_decision": {
    "continue_turns": true,
    "reason": "...",
    "estimated_value_of_next_turn": "LOW | MEDIUM | HIGH"
  },
  "targeted_hunter": {},
  "delta_ledger": [],
  "deterministic_form_actuation": {},
  "open_blockers": [],
  "final_compiler_allowed": false
}
```

## Dynamic Early Exit

Gov may trigger early exit only when the local evidence is clean.

Required early-exit evidence:

- deterministic gate passed
- required sections present
- source IDs valid
- semantic trap gates passed
- no open blockers
- no high or critical drift in the Delta Ledger
- final compiler allowed
- next turn estimated value is low

This is a burn-optimization move, not a quality shortcut.

## Targeted Hunter Deployment

Gov should stop sending generic adversarial prompts when the weakness is known.

For `TARGETED_HUNTER`, Gov must specify:

- `hunter_target`: the exact section, claim, action, calculation, or boundary to attack
- `attack_question`: the adversarial question the worker must answer
- `must_not_discuss`: topics that would waste the Hunter turn
- `success_condition`: what counts as a successful Hunter output

Example:

```json
{
  "route_verdict": "TARGETED_HUNTER",
  "targeted_hunter": {
    "hunter_target": "Section 4 vendor-master exception",
    "attack_question": "Does this section turn a narrow exception into broad approval authority?",
    "must_not_discuss": ["style", "general summary", "already-settled sections"],
    "success_condition": "Either identify a source-grounded defect or certify no defect found."
  }
}
```

## Semantic Drift Detection

Gov must maintain a Delta Ledger for narrative and action-boundary drift.

This is required because the failure mode is often gradual mutation:

- `holding notice` becomes `customer notice`
- `customer notice` becomes `exposure language`
- `exposure language` becomes `breach admission`

Delta Ledger entries must include:

- `claim_or_action`
- `prior_position`
- `current_position`
- `drift_class`
- `severity`
- `required_repair`

High or critical drift blocks early exit and final compiler routing until repaired or fail-closed.

## Relationship To Form Actuation

Dynamic Gov Router V1 sits above deterministic form actuation.

The form actuator computes mechanical defects:

- word count
- word-band status
- section presence
- exact expansion/compression
- section quotas

Gov decides the control action:

- send the worker to repair form
- preserve a locked admissible artifact
- deploy Hunter against a non-form defect
- fail closed
- early-exit to compiler

Gov still does not rewrite the artifact and still does not choose the model.

## Executable Guardrail

The local validator is:

- `benchmark_dynamic_gov_router.py`

The tests are:

- `tests/test_dynamic_gov_router_validator.py`

The validator rejects:

- missing control-router fields
- invalid route verdicts
- any Gov-side model/provider selection
- targeted Hunter routes without a specific attack contract
- final compiler routes with open blockers
- final compiler routes with high or critical semantic drift
- final compiler allowance when high or critical drift is unresolved

## Current Architecture Name

Use this name for the next sibling lock:

`D11_LOCK_DYNAMIC_GOV_ROUTER_V1`

Short form:

`Dynamic Gov Router V1`

Non-negotiable invariant:

`Gov does not choose models. Gov chooses control actions.`

