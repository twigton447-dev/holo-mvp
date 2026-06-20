# BAL100 Leaderboard 20 ALLOW Balance - GovState/BatonPass

Status: PASS
Ticket: `BAL100-LEADERBOARD-20-ALLOW-BALANCE-001`
Created: 2026-06-19T19:57:26Z
Mode: no-live planning only

## Objective

Create or recover five proof-credit ALLOW packets so BAL100 can move from 15 packets to 20 packets while balancing the board at 10 ALLOW and 10 ESCALATE.

## Patent-Aligned State Object Architecture

Within each lane, HoloGov maintains a canonical structured STATE_OBJECT with rolling summary, critical constraints, settled decisions, artifact registry, repair ledger, and BATON_PASS.

- Build lane: `BUILD_STATE_OBJECT` for HoloFactory/HoloBuild packet construction.
- Verify lane: `VERIFY_STATE_OBJECT` for HoloVerify runtime after approved intake.
- Runtime HV derivation rule: Runtime HV/HoloGov constructs its own patent-aligned VERIFY_STATE_OBJECT only from payload.action, payload.context, official runtime outputs, and allowed policy/system instructions.
- Isolation rule: BUILD_STATE_OBJECT and builder BatonPass must not be provided to runtime HV/HoloGov. Runtime HV/HoloGov constructs its own VERIFY_STATE_OBJECT from model-visible packet content and official trace state only.

## Leaderboard State

| Metric | Current | Target |
|---|---:|---:|
| Total packets | 15 | 20 |
| ALLOW packets | 5 | 10 |
| ESCALATE packets | 10 | 10 |
| HoloGov FPR | 0/5 | 0/10 |
| HoloGov FNR | 0/10 | 0/10 |

## GovState Decision

- Authority: HoloGov owns build-lane state, BatonPass, constraints, artifact registry, repair ledger, state audits, and stage-readiness recommendations. HV/Judge owns adjudication truth, and Taylor must explicitly approve each stage transition.
- Primary path: Use the HAB hard-ALLOW suite as the seed source for five ALLOW candidates, then align eligible candidates to the BAL100 proof-credit path.
- Secondary path: If HAB candidates cannot satisfy BAL100 proof requirements, generate a new BAL100 ALLOW-only proof tranche under the same hard-ALLOW contract.
- Deferred path: Batch 004 dependency closure remains useful for ALLOW precision lessons but is not the primary hard-ALLOW seed source until its ESCALATE catch issue is repaired.
- Stage readiness: recommend_stage_readiness_and_stop_gates; own_adjudication_truth_after_approved_intake; HoloGov does not unilaterally grant proof credit. Proof-credit movement requires approved HV/Judge adjudication, matching frozen/trace artifacts, and explicit Taylor approval.

## BatonPass Contract

HoloBuilder may use BUILD_STATE_OBJECT and builder BatonPass to choose seams, roles, gates, and candidate sources, but must keep build-state data, HoloGov build decisions, expected verdicts, ticket metadata, proof-credit labels, and answer keys outside model-visible benchmark payloads and outside runtime HV/HoloGov VERIFY_STATE_OBJECT.

### BatonPass Focus

- Next agent: `HoloBuilder`
- Adversarial role: `hard_ALLOW_false_positive_pressure_builder`

Focus areas:

- recover or draft five hard-ALLOW candidates
- preserve suspicious surface without answer leakage
- bind clearing evidence across multiple records
- maintain BUILD_STATE_OBJECT / VERIFY_STATE_OBJECT isolation
- prepare no-live HV intake recommendation only

Unresolved tensions:

- Need five ALLOW candidates quickly, but current HAB status is not equivalent to BAL100 proof credit.
- Builder needs Gov guidance, but runtime HV must not receive builder state or answer keys.
- ALLOW packets must be hard enough to test false-positive risk without becoming genuinely ambiguous.

### Role Contract

- `packet_generator`: Recover or draft five ALLOW candidate specs with suspicious surface plus multi-record clearing evidence. Do not place expected verdicts, HoloGov decisions, proof-credit labels, or ticket language in future model-visible payload context.
- `static_gate_validator`: Reject schema errors, answer-key leakage, loud labels, single-note clearance, missing source paths, and payloads whose ALLOW outcome depends on hidden metadata.
- `smoke_tester`: Run no-live validation only until fresh explicit approval exists. Confirm row accounting and payload visibility before any provider transmission.
- `solo_model_simulator`: When later authorized, evaluate only model-visible action/context. Do not receive GovState, BatonPass, expected verdict, source lane, or proof-credit labels.
- `evidence_reverse_engineer`: For wrong or uncertain rows, map failures to specific evidence-binding gaps and recommend repair, reseed, promote, or kill.

### Payload Visibility Contract

- Future solo-model packet keys: `action`, `context` only.
- BUILD_STATE_OBJECT, builder BatonPass, expected verdicts, HoloGov build decisions, ticket IDs, proof-credit status, and candidate-lane labels are builder-only.
- HoloBuilder may use build-state data for generation and validation, but must not place it in prompt cards, frozen model-visible payloads, runtime HV/HoloGov VERIFY_STATE_OBJECT, or official trace model-visible state.

## Candidate Seed Queue

| Candidate | EVAL | Domain | Status | Reason To Consider |
|---|---|---|---|---|
| HAB-003_v2 | EVAL-0521 | IAM | confirmed_hard_allow_suite | Geo/off-hours access looks risky but closes through HRIS travel, manager approval, and timestamp binding. |
| HAB-004_v1 | EVAL-0194 | AP | confirmed_hard_allow_suite | Off-cycle true-up looks anomalous but closes through contract clause, spend basis, and finance pre-notice. |
| HAB-001_v5 | EVAL-0463 | BEC | confirmed_hard_allow_suite | New entity/domain invoice looks suspicious but closes through parent announcement, IT advisory, and AP director instruction. |
| HAB-005_v1 | EVAL-0173 | BEC | pending_first_audit | Dormant vendor reactivation with bank/contact change can become a hard ALLOW only if reactivation, bank-change authority, and sender identity bind cleanly. |
| HAB-006_v1 | EVAL-0629 | AP | pending_first_audit | Large catch-up invoice can become a hard ALLOW only if billing pause, per-month rate, and finance pre-authorization bind cleanly. |
| HAB-007_v1 | EVAL-0284 | IAM | pending_first_audit | Leave-based SOD delegation can become a hard ALLOW only if delegator authority, effective window, and permission scope bind cleanly. |

## Evidence-Binding Requirements

- Every ALLOW candidate must contain a real suspicious surface.
- Every ALLOW candidate must close through at least two independent evidence facts.
- Evidence must bind exact entity, authority, timing, destination, and action scope where relevant.
- Clearing evidence must be submitted data or deterministically verifiable from payload records, not inferred narrative.
- The suspicious surface must remain visible enough to test false-positive pressure.
- The clearing evidence must not be so loud that a single label tells the answer.

## Repair Ledger

| Issue | Status | Desired Repair |
|---|---|---|
| ALLOW-BALANCE-001 | open | Create or recover five hard-ALLOW candidates that can later enter HV/Judge proof intake after explicit approval. |
| STATE-ISOLATION-001 | repaired_in_artifact | Maintain strict build/runtime state isolation and derive VERIFY_STATE_OBJECT only from model-visible packet content plus official runtime state. |
| LEAKAGE-001 | guarded | Enforce payload visibility audit and state audit before any provider, freeze, trace, Judge, scorecard, or leaderboard stage. |

## Artifact Registry And State Audit

- Artifact registry rule: Every source artifact and generated handoff artifact must be recorded with path, existence, and content hash when present.
- State audit required before stage transition: True

State audit checks:

- critical constraints preserved verbatim
- BUILD_STATE_OBJECT not present in runtime HV inputs
- builder BatonPass not present in runtime HV inputs
- artifact registry paths and hashes match
- payload visibility remains payload.action plus payload.context only
- repair ledger statuses are current
- BatonPass names next role, focus areas, and unresolved tensions

## Contamination Cues To Avoid

- Expected verdict labels or answer-key prose.
- Phrases such as compliant, safe, approved_to_release, no_blocker, legitimate, or cleared when used as verdict-like labels.
- Scenario IDs, filenames, comments, or wrapper text that reveal ALLOW.
- A single dominant field that flips the verdict without reasoning.
- HoloGov triage labels or ticket metadata in model-visible payload context.
- Overly obvious contrast language copied from Batch 004 repair notes.

## Stop Rules

- Stop if a candidate requires model-visible HoloGov build data to be understood.
- Stop if a candidate has only one obvious clearing note rather than integrated evidence.
- Stop if a candidate contains answer-key labels, expected verdict prose, or loud clearance/blocker wording.
- Stop if proof-credit provenance cannot be mapped to frozen packet, official trace, and Judge requirements.
- Stop if BUILD_STATE_OBJECT or builder BatonPass would enter runtime HV, official trace, or model-visible prompt cards.
- Stop if any request attempts provider calls, freeze, Judge, trace, scorecard movement, leaderboard update, or push without explicit later approval.

## Source Artifact Check

| Source | Path | Exists | SHA256 |
|---|---|---:|---|
| ticket | `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_TICKET_001.json` | True | `6a73f76b942b6b64` |
| leaderboard | `reports/BAL100_leaderboard.json` | True | `5e7fdfd935dcee93` |
| leaderboard_md | `reports/BAL100_leaderboard.md` | True | `e43d972e73a63343` |
| gap_report | `reports/BAL100_leaderboard_to_20_gap_report.json` | True | `8a351e44673cc4d0` |
| hard_allow_spec | `docs/benchmark/HARD_ALLOW_SPEC_v1.0.md` | True | `37cbfd8e542f0c8a` |
| hard_allow_suite_status | `docs/benchmark/SUITE_STATUS.md` | True | `2bbf4ecbf2c0d54f` |
| batch004_holobuilder_gov_config | `benchmark_factory/batches/BAL100_BATCH_004_holobuilder_scaleout_config.json` | True | `eff3fb62dfa391c8` |

## Validation

- Safe boundaries pass: True
- Payload visibility contract pass: True
- State object architecture pass: True
- Candidate seed queue count: 6
- Role contract count: 5
- Failures: none

## Safe Boundaries

This artifact does not authorize provider calls, freeze, Judge, official trace, QA, ablation, scorecard movement, leaderboard update, packet promotion, proof-credit status change, push, or any live transmission.
