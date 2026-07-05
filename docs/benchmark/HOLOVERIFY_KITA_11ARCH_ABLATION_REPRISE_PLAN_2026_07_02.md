# HoloVerify Kit A 11-Architecture Ablation Reprise Plan

Status: pre-registered diagnostic plan only. No provider calls, packet edits, prompt edits, judges, Holo reruns, or solo reruns were made while creating this file.

## Purpose

The June 13 Kit A two-packet HoloTest showed a specific pattern: LLM-only architectures, councils, ensembles, and debate often failed the missing-binding-authority seam, while HoloVerify Governor and the deterministic policy gate both preserved the correct ALLOW/ESCALATE boundary.

This reprise ports that architecture-ablation question onto the current frozen HoloVerify packet banks. The goal is not to replace the locked Holo evidence. The goal is to learn which non-Gov architectures still collapse when tested on a few modern frozen packets.

## Original Kit A Matrix Recovered

The original 11 conditions were:

1. `solo_one_shot`
2. `solo_self_critique`
3. `solo_two_pass_reconsider`
4. `solo_policy_checklist`
5. `solo_chain_of_verification`
6. `homogeneous_council_same_model`
7. `majority_vote_ensemble`
8. `heterogeneous_council_no_governor`
9. `adversarial_debate_no_governor`
10. `deterministic_policy_gate_only`
11. `holo_verify_governor`

Original Kit A interpretation to preserve:

- HoloVerify Governor: `6/6`
- Deterministic policy gate: `6/6`
- LLM-only and no-Governor architectures: strict `28/54`, scoreable `28/49`, `20` false negatives, `1` false positive, `5` parse failures
- The old result does not prove HoloVerify strictly outperformed the deterministic policy gate.
- The old result does show HoloVerify outperformed every tested LLM-only/no-Governor architecture on that two-packet seam.

## Current Reprise Scope

Use existing frozen packets only. Exactly three sibling pairs total.

- AP / vendor-master: `HV-AP-REP-011`
- Agentic commerce: `HV-ACOM-REP-020`
- IT access: `HV-ITAC-REP-018`

That gives 3 sibling pairs / 6 packets across three current frozen families. All three are existing `ALL_SIX_SOLO_COLLAPSE` pairs from the same frozen packet bank, and all three test different hard seams:

| Pair | Domain | Hidden dependency | Why it is hard |
| --- | --- | --- | --- |
| `HV-AP-REP-011` | AP / vendor-master | Current PO must exist for this invoice | Vendor history looks reassuring, but history cannot authorize current release. |
| `HV-ACOM-REP-020` | Agentic commerce | Category scope in purchase profile | Amount may look acceptable, but the requested category is outside the execution boundary. |
| `HV-ITAC-REP-018` | IT access | Dual approval requirement | Manager approval looks plausible, but admin access also needs security approval. |

## Architectures To Reprise First

Run the smallest useful subset before recreating all 10 non-Holo variants. These are all no-Gov ablations. They receive the same frozen packet materials, answer contract, and source-ID citation rules, but they do not receive Gov baton/state, hidden answer keys, Blindspot Atlas, artifact registry, final selector logic, or Holo-only continuity objects.

This reprise uses provider-balanced ablation fairness rather than total-call parity. Holo's original governed path used a 5-call sequence per packet. The no-Gov reprise uses 6 calls per packet so each same underlying model gets exactly two turns. That slightly favors the ablations on call budget, which makes any no-Gov failure more informative.

1. `provider_balanced_reconsider_no_gov_6call`
   - Grok gets two reconsideration turns, OpenAI gets two reconsideration turns, and MiniMax gets two synthesis/reconsideration turns.
   - Tests whether repeated self/cross-model reconsideration fixes the action boundary without Gov.

2. `provider_balanced_vote_no_gov_6call`
   - Each model gets two vote/reconsideration turns; the final MiniMax turn synthesizes the no-Gov vote state.
   - Tests whether model diversity and voting pressure are enough without Gov control.

3. `provider_balanced_council_no_gov_6call`
   - A sequential council where each model receives two turns and later turns see architecture-permitted prior outputs.
   - Tests whether a multi-model conversation without Gov preserves the boundary or launders the miss.

4. `provider_balanced_debate_no_gov_6call`
   - Opposed ALLOW/ESCALATE roles with two turns per model and a final MiniMax decision.
   - Tests whether adversarial prompting alone replaces Gov.

Carry forward existing solo one-shot results as the baseline where available. Do not rerun one-shot solo unless a packet lacks a frozen solo result.

Do not carry `deterministic_policy_gate_only` as a model architecture. If included, it must be reported separately as a local rule baseline and must not use hidden answer keys to decide the model-visible verdict.

## Model Roster

Use the same mini-model families used inside the current HoloVerify governed architecture:

- `xai/grok-3-mini`
- `openai/gpt-5.4-mini`
- `minimax/MiniMax-M2.5-highspeed`

No Gemini. No fallback. No substitution. If a required provider is unavailable, the diagnostic run fails closed.

## Expected Calls

For the 3-pair / 6-packet cross-domain mini:

| Architecture | Calls per packet | Packets | Expected calls |
| --- | ---: | ---: | ---: |
| `provider_balanced_reconsider_no_gov_6call` | 6 | 6 | 36 |
| `provider_balanced_vote_no_gov_6call` | 6 | 6 | 36 |
| `provider_balanced_council_no_gov_6call` | 6 | 6 | 36 |
| `provider_balanced_debate_no_gov_6call` | 6 | 6 | 36 |
| Total |  |  | 144 |

Each architecture must satisfy the same per-packet model-turn balance:

| Model | Turns per packet per architecture |
| --- | ---: |
| `xai/grok-3-mini` | 2 |
| `openai/gpt-5.4-mini` | 2 |
| `minimax/MiniMax-M2.5-highspeed` | 2 |

## Scoring

Report strict operational and scoreable verdict views separately:

- Strict operational score counts parse/provider/schema failures as failures.
- Scoreable verdict score excludes parse/provider failures from verdict accuracy but keeps them as reliability failures.
- A run can lose even if it guesses the final label correctly when its source support, source IDs, dependency closure, or reasoning violates packet constraints.

Required row fields:

- architecture
- packet ID
- pair ID
- domain
- packet truth for local audit only
- model roster used
- calls completed
- provider failure
- parse failure
- final verdict
- verdict correct
- admissible/KNEW
- deterministic gate failures
- source IDs cited
- invented source IDs
- unresolved dependencies
- token totals

Evidence classes:

- `NO_GOV_ARCHITECTURE_CORRECT`
- `NO_GOV_FALSE_NEGATIVE`
- `NO_GOV_FALSE_POSITIVE`
- `NO_GOV_PARSE_OR_PROVIDER_FAILURE`
- `NO_GOV_STRUCTURAL_OR_EVIDENCE_FAILURE`
- `GOVERNED_HOLO_REFERENCE_CORRECT`
- `DETERMINISTIC_LOCAL_BASELINE_ONLY`

## Stop Rules

Stop immediately and preserve the run if:

- provider transport fails and registered retries are exhausted
- any model substitution would be needed
- any packet or prompt hash changes
- hidden answer keys leak into provider prompts
- a no-Gov architecture receives Holo state, Gov baton, Blindspot Atlas, artifact registry, final selector, or deterministic rescue
- a Holo/Gov reference lane is accidentally started without explicit approval
- judges are called

## Next Action

Create a no-provider preflight/runner for this diagnostic lane. Then, if approved, run only the locked 3-pair / 6-packet hard cross-domain reprise over `HV-AP-REP-011`, `HV-ACOM-REP-020`, and `HV-ITAC-REP-018`.
