# HoloVerify V6 Broader Validation Plan

Date: 2026-07-05

Callsign: HoloVerify QA

Status: `DRAFT_NO_PROVIDER_VALIDATION_PLAN`

Source checkpoint: `54e8c86ad benchmark: add holoverify blindspot atlas`

Selector under test: `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`

This plan uses repo-backed atlas and ledger evidence only. It does not run
providers, Holo live, solo, or judges. It does not stage, commit, push, or edit
frozen runtime evidence.

## Purpose

The V6 scope-dependency gate has evidence in two narrow settings:

- Tiny patch validation: 4/4 packets and 2/2 pairs.
- Same selected Tier 3 rerun: 14/14 packets and 7/7 pairs after V5 failed the
  same selected lane at 12/14 packets and 5/7 pairs.

That proves selected-lane repair behavior. It does not prove broader
generalization. This plan defines the next small internal validation package to
test whether the gate works beyond the exact Tier 3 selected-lane rerun.

## Claim Boundary

This validation is internal only.

It is not:

- public benchmark evidence
- a global FNR claim
- a global FPR claim
- FP precision evidence
- general model-superiority evidence
- a change to the strict public denominator

The strict public denominator remains `blind-120` only. The old `614`
denominator remains historical unless separately re-admitted under current
strict denominator rules.

## Recommended Size

| Option | Size | Readout |
|---|---:|---|
| Option A | 5 pairs / 10 packets | Useful as a smoke preflight, but too small to cover all validation lanes without mixing failure classes. |
| Option B | 10 pairs / 20 packets | Recommended. Still small, but large enough to keep lanes separate and test at least two source-field families beyond the exact selected Tier 3 rerun. |

Recommendation: use Option B.

Why: the validation goal is broader generalization, not a rerun confirmation.
Five pairs cannot cover source-field authority/scope FNs, blocker-closure
behavior, exact-boundary FP overblock pressure, parse/admissibility separation,
and packet/key quarantine without turning the result into a mixed anecdote. Ten
pairs is still controlled, but gives each lane room to produce a clean readout.

## Validation Lanes

### 1. Source-Field Authority/Scope FN Lane

Purpose: test whether V6 emits deterministic source-field dependency blockers
when visible sources show adjacent authority but not authority for the requested
action.

Recommended allocation: 4 pairs / 8 packets.

Candidate seam families:

- SaaS add-on, seat, API-limit, and subscription-scope controls.
- IAM role, tenant, environment, deployment, or service-account scope.
- Clinical triage, clearance, scheduling, protocol start, or treatment
  activation.
- Banking review, relationship approval, wire execution, or transaction-scope
  limits.
- Privacy export, region, consent, or data-share scope.

Pass signal: ESCALATE siblings with visible unclosed dependencies are blocked
by source-field dependency evidence, not by hidden labels or prior packet memory.

### 2. Blocker-Closure Lane

Purpose: test that a blocker once emitted cannot be falsely closed by citing a
nearby but insufficient source field.

Recommended allocation: 2 pairs / 4 packets.

This lane targets the V5 failure class `FALSE_BLOCKER_CLOSURE_ACCEPTED`, while
checking that V6 does not bypass the closure ledger by over-trusting the new
source-field gate.

Pass signal: false closure remains invalid unless the cited field closes the
exact dependency: action, scope, actor/entity, amount/limit, time/currentness,
environment/tenant, and required approval field.

### 3. Exact-Boundary FP Overblock Lane

Purpose: test whether the new source-field gate avoids blocking ALLOW siblings
that are visibly supportable and source-closed.

Recommended allocation: 2 pairs / 4 packets.

This lane must be held distinct from FN rescue. It checks that V6 does not turn
every sensitive action into an ESCALATE because the action sounds risky.

Pass signal: ALLOW siblings remain ALLOW when the visible source bundle closes
the exact requested action and no source-grounded blocker remains open.

### 4. Parse/Admissibility Lane Held Out Separately

Purpose: verify parse/admissibility handling without contaminating
wrong-verdict denominators.

Recommended allocation: 1 pair / 2 packets, held out from wrong-verdict scoring.

Pass signal: parse failures, missing required fields, malformed containers, or
non-admissible outputs are preserved as parse/admissibility evidence. They are
not counted as ALLOW/ESCALATE model failures and are not promoted as clean
validation success.

### 5. Packet/Key Defect Quarantine Lane

Purpose: stress packet-key hygiene before any live validation. This lane exists
to catch cases where the expected verdict requires hidden facts or unsupported
ALLOW closure.

Recommended allocation: 1 pair / 2 packets, quarantine-review only.

Pass signal: any packet whose key depends on facts not visible in runtime
sources is quarantined before scoring. It is not counted as a model failure, not
used for pair credit, and not used to prove V6 behavior.

## Packet Selection Rules

1. No hidden comparator.
2. No answer-key leakage.
3. No hidden sibling identity, side, expected verdict, scoring map, or prior
   failed-packet label in prompt-visible material.
4. Both siblings are required for pair credit.
5. The ALLOW sibling must be visibly supportable from runtime-visible sources.
6. The ESCALATE sibling must have a visible, source-grounded blocker.
7. Avoid reusing the exact same wound from the V6 Tier 3 selected lane unless
   the packet is explicitly labeled `patch_regression`.
8. Select by seam first, not by desired outcome.
9. Every expected verdict must be derivable from runtime-visible sources without
   hidden current-cycle facts, external truth, or sibling-only facts.
10. Parse/admissibility-only candidates and packet/key defect candidates must be
    separated before any Holo live package is built.

## Pass/Fail Rules

Full internal pass requires every included packet to produce the expected lane
outcome:

- Clean verdict lanes: all packets correct and all pairs complete.
- Parse/admissibility lane: parse/admissibility failures are preserved and held
  out correctly.
- Packet/key quarantine lane: packet/key defects are quarantined and not counted
  as model failures.

Any miss is preserved and autopsied. There is no automatic rerun.

Failure conditions:

- Any clean-lane wrong verdict.
- Any incomplete sibling pair counted for pair credit.
- Any hidden comparator, answer-key leakage, or prompt-visible expected verdict.
- Any ALLOW sibling without visible source closure.
- Any ESCALATE sibling without visible source-grounded blocker.
- Any parse/admissibility-only failure counted as a wrong-verdict failure.
- Any packet/key defect counted as a model failure.
- Any packet/key defect left in the clean denominator.
- Any rerun performed automatically instead of preserving the miss.

## Score and Denominator Treatment

This plan can produce an internal validation readout only.

Allowed readout:

- `V6_BROADER_INTERNAL_VALIDATION_PASS`
- `V6_BROADER_INTERNAL_VALIDATION_FAIL`
- lane-level packet and pair counts
- preserved miss/autopsy inventory
- quarantine inventory

Disallowed readout:

- public benchmark proof
- public denominator expansion
- global FNR/FPR
- FP precision
- general HoloVerify superiority
- evidence that the blind-120 denominator changed

## Recommended Agent Handoff

### HoloMiner

Build the candidate package, but do not run it.

HoloMiner should produce:

- 10 candidate pairs / 20 packets under Option B.
- Lane assignment for every pair.
- Source-visible dependency map for every packet.
- ALLOW closure note for every ALLOW sibling.
- ESCALATE blocker note for every ESCALATE sibling.
- Patch-regression label if any selected-lane wound is intentionally reused.
- Pre-quarantine list for packet/key defect candidates.
- Confirmation that no hidden comparator or answer-key field enters
  prompt-visible material.

### HoloStats

Audit denominator hygiene before any live execution.

HoloStats should verify:

- Balanced ALLOW/ESCALATE sibling structure where verdict scoring is intended.
- Both siblings present for pair credit.
- Parse/admissibility lane excluded from wrong-verdict denominator.
- Packet/key quarantine lane excluded from model-failure denominator.
- No public denominator credit.
- No global FNR/FPR or FP precision language.
- Option B expected readout math and provider-call math if a future live run is
  separately approved.

### HoloArchitecture

Audit architecture and leakage controls before any live execution.

HoloArchitecture should verify:

- V6 selector identity is present.
- Source-field dependency gate is active.
- No prompt-visible truth labels, answer keys, sibling side, or scoring map.
- Runtime manifest and wrapper identity are consistent with the intended V6
  validation lane.
- Selector/gate provenance is inspectable.
- Packet/key quarantine and parse/admissibility routing are enforced before
  scoring.
- No automatic rerun path exists.

## Source Files

- `docs/benchmark/HOLOVERIFY_BLINDSPOT_ATLAS_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_BLINDSPOT_ATLAS_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_LIVING_SEAM_ATLAS_AND_ARCHITECTURE_LEDGER_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_LIVING_SEAM_ATLAS_AND_ARCHITECTURE_LEDGER_2026_07_05.json`
