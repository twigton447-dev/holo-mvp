# HoloVerify Blindspot Atlas

Date: 2026-07-05

Callsign: HOLOATLAS SUBAGENT

Status: `PASS_NO_PROVIDER_ATLAS_V6_RERUN_UPDATED`

This foundation pass used repo-backed evidence only. No providers, Holo live runs, solo runs, judges, staging, commits, pushes, or frozen runtime evidence edits were performed.

## Scope

The Atlas is a durable learning index for HoloVerify failure terrain. It may teach Gov general policy about recurring failure classes, source-field checks, dependency closure, blocker ledgers, and scope matching. It must not teach Gov packet truth, sibling identity, answer keys, scoring maps, expected verdicts, or any benchmark-hidden label.

This is not a benchmark scorecard and does not create public claim material.

## Current Status

| Item | Status |
|---|---|
| Strict public denominator | `blind-120` only |
| Old `614` denominator | stale / historical unless re-admitted under current strict rules |
| Blind-120 score | 120/120 packets, 60 ALLOW and 60 ESCALATE |
| V5 Tier 3 FN rescue | failed-live internal evidence: 12/14 packets, 5/7 pairs |
| V6 tiny patch validation | passed internal patch validation: 4/4 packets, 2/2 pairs |
| V6 Tier 3 FN Holo rescue rerun | completed internal selected-lane repair evidence: 14/14 packets, 7/7 pairs |

## V6 Tier 3 Same-Selected-Lane Repair Evidence

| Field | Value |
|---|---|
| Classification | `V6_TIER3_FN_HOLO_RESCUE_RERUN_SELECTED_LANE_REPAIR_PASSED` |
| Run folder | `docs/benchmark/holoverify_v6_tier3_fn_holo_rescue_rerun_2026_07_05/live_runs/run_20260705T023842Z` |
| Provider calls | 70/70 |
| Provider failures | 0 |
| Route | W1 -> G1 -> W2 -> G2 -> W3 x14 |
| Packet score | 14/14 |
| Pair score | 7/7 |
| Failed packets | `[]` |
| V5 same selected lane | 12/14 packets, 5/7 pairs |
| V6 same selected lane | 14/14 packets, 7/7 pairs |

Claim boundary: this is internal selected-lane repair evidence only. It is not public benchmark evidence, not a global FNR claim, not FP precision evidence, and not general model superiority evidence. The strict public denominator remains `blind-120` only, and the old `614` remains stale / historical.

## Failure-Class Taxonomy

| Class | Definition | Evidence / status |
|---|---|---|
| `SOLO_FP_OVERBLOCK` | Solo model blocks a source-closed ALLOW packet, usually from sensitivity, warning fixation, or exact-boundary overblocking. | Solo Failure Factory counts and FP rescue candidate pool in the living seam ledger. |
| `SOLO_FN_FALSE_ALLOW` | Solo or Holo final answer allows a source-open ESCALATE packet. | V5 Tier 3 failed-live and targeted FN mining rollups. |
| `SOLO_PARSE_ADMISSIBILITY_FAILURE` | Output is unusable or non-admissible even if directionally close. Keep separate from wrong-verdict errors. | Living seam ledger separates 25 parse/admissibility-only pairs; readiness note lists parse-only pairs. |
| `PACKET_KEY_DEFECT` | Expected verdict depends on a fact not visible in runtime sources, or ALLOW/ESCALATE key is unsupported by source-visible evidence. | `HVSF-FACTORY14F-017-B` stale-cycle defect; `HVSF-FACTORY13X-002` quarantine recommended. |
| `PROVIDER_TRANSPORT_FAILURE` | Network/provider call fails before valid content is produced; must be preserved and excluded from scoring when incomplete. | V6 tiny patch-validation failed DNS/network attempt preserved separately and excluded. |
| `WORKER_PARSE_CONTRACT_FAILURE` | Worker output violates required key/value parse contract or required fields. | Runner required keys and live-wrapper parse/admissibility checks; budget and wrapper tests enforce failure handling. |
| `GOV_RUNTIME_CONTRACT_FAILURE` | Gov or governed decision path does not fail closed or does not bind the final decision to the governed receipt/path. | Governed-decision smoke tests prove fail-closed behavior for signer veto and Gov failure; HoloVerify Gov baton remains bounded state, not raw transcript memory. |
| `SELECTOR_REGRESSION` | Selector chooses from the wrong eligibility set, leaks truth markers, or lets consensus outrank hard gates. | Selector regression tests cover truth-blind verdict grid, policy identity, deterministic gates, and blocker fields. |
| `BLOCKER_DETECTED_THEN_DROPPED` | A worker surfaces a source-grounded blocker, but later turns/Gov/selector stop carrying it. | V4 patch addressed this by adding an active blocker ledger and blocker-resolution requirements. |
| `FALSE_BLOCKER_CLOSURE_ACCEPTED` | A later worker names a blocker and cites a source, but the cited source fields do not close the blocker. | V4 small-rescue autopsy exposed this on banking/payment-release fixtures; V5 tests address it. |
| `BLOCKER_NOT_DETECTED_BY_ANY_WORKER` | No worker emits the blocker, so V4/V5 blocker preservation and closure validation never activate. | V4 autopsy and Tier 3 V5 autopsy both show all-worker blocker misses. |
| `V5_SCOPE_DEPENDENCY_NON_DETECTION` | V5 has closure validation, but no source-field authority/scope dependency check emits a blocker before worker prose misses it. | Tier 3 V5 failed-live autopsy classified this as the overall failure class. |
| `V6_SCOPE_DEPENDENCY_GATE_PATCHED` | Deterministic V6 source-field gate emits authority/scope dependency blockers and blocks contradictory ALLOW artifacts. | V6 tests passed; V6 tiny patch-validation passed 4/4 packets and 2/2 pairs; V6 Tier 3 same-selected-lane rerun passed 14/14 packets and 7/7 pairs. |

## Patch Map

| Patch | Addressed failure class | Code patch | Tests | Evidence validating it | Remains unproven |
|---|---|---|---|---|---|
| V4 blocker preservation | `BLOCKER_DETECTED_THEN_DROPPED` / selector preservation regression | `holoverify_blind_runner_v0.py` active blocker ledger, worker prompt blocker ledger, selector blocker-resolution criteria | `tests/test_holoverify_blind_selector_repair_regression.py` | `docs/benchmark/HOLOVERIFY_BLOCKER_PRESERVATION_PATCH_REPORT_2026_07_04.md`; V4 small-rescue rollup/autopsy | Does not detect blockers no worker finds; does not validate semantic closure of a claimed blocker. |
| V5 blocker-closure validation | `FALSE_BLOCKER_CLOSURE_ACCEPTED` | `holoverify_blind_runner_v0.py` closure requirements, `_validate_blocker_closure`, invalid closure ledger, selector eligibility fields | `tests/test_holoverify_v5_blocker_closure_validation.py`; selector regression tests | V5 design; V5 Tier 1 patch validation pass; V5 Tier 2 replacement supplement and merged internal gate | Does not catch source-field dependencies unless a worker/gate emits a blocker; broad public FNR/FPR remains unproven. |
| V6 scope-dependency gate | `V5_SCOPE_DEPENDENCY_NON_DETECTION` and `BLOCKER_NOT_DETECTED_BY_ANY_WORKER` for implemented source-field seams | `holoverify_blind_runner_v0.py` `SELECTOR_V6_SCOPE_DEPENDENCY_GATE_2026_07_05`, `_authority_scope_dependency_checks`, deterministic dependency blockers | `tests/test_holoverify_v6_scope_dependency_gate.py`; wrapper identity tests | V6 patch report; V6 post-live audit; tiny patch validation passed 4/4 packets and 2/2 pairs; V6 Tier 3 same-selected-lane rerun passed 14/14 packets and 7/7 pairs | Broader V6 validation beyond selected source-field seams remains unproven; no public denominator credit, global FNR claim, FP precision claim, or general model-superiority claim follows from this selected lane. |

## Seam Map

| Seam | Productive failure pressure | Evidence domains | Current readout |
|---|---|---|---|
| authority/scope mismatch | Nearby authority exists but does not close the requested action scope. | Agentic commerce add-on activation, clinical protocol start, IAM, SaaS, banking/payment release. | Productive and now partially patched by V6 for add-on activation and protocol start fixtures. |
| blocker closure vs blocker detection | A blocker can be preserved only after it exists; false closure and non-detection are different failures. | V4/V5/V6 rescue lanes. | Core Atlas distinction; V5 patches closure, V6 starts detection. |
| exact-boundary overblock | Model blocks ALLOW because action sounds sensitive, despite exact source closure. | FP_OVERBLOCK candidates, exact-boundary top-10 rollups. | Keep separate from FN rescue; useful for FP precision validation. |
| payment rail vs invoice approval | Approval of invoice/vendor/relationship is mistaken for payment rail execution authority. | AP vendor master, AP payment, trade finance. | Productive; packet/key hygiene matters because hidden approval requirements must be source-visible. |
| SaaS add-on / seat / API-limit scope | Renewal, admin, or seat approval confused with add-on activation or API-limit change. | Agentic commerce subscription controls, SaaS seat expansion, SaaS API-limit controls. | Productive; V6 add-on activation gate is first deterministic patch. |
| IAM role/tenant/deployment scope | Role, tenant, production/deployment, or service-account scopes get collapsed. | IAM controls, IT access, service-account deployment, payment-template permissions. | Evidence present in solo mining and packet freeze surfaces; needs deterministic rule expansion. |
| clinical triage vs treatment activation | Scheduling/triage/clearance confused with protocol start or medication/treatment activation. | Clinical treatment activation and protocol start. | Productive; V6 protocol-start gate is first deterministic patch. |
| banking review vs wire execution | KYC/relationship/review controls mistaken for transaction or wire execution approval. | Banking relationship, banking wire execution, treasury controls. | Productive; V5 closure validation covers transaction type and amount limit when blocker exists. |
| privacy export scope | Data-share/export region or consent scope confused with exact release authority. | Privacy/data-share, DPRV Wave 2. | Evidence present; not yet patched as a named deterministic V6 family. |
| agentic commerce add-on/subscription/refund controls | Subscription, refund, add-on, cap, or order-state controls over-credit adjacent records. | Agentic commerce, refund controls, subscription controls. | Productive; split FN rescue from FP overblock and parse-only failures. |

## Domain Map

| Domain | Evidence status | Source-backed notes |
|---|---|---|
| AP / procurement | Present | Vendor-master/payment controls, AP payment destination, procurement release, payment rail vs invoice approval seams. |
| Agentic commerce | Present | Order execution, subscription, add-on activation, refund controls; V6 add-on fixture lives here. |
| IT / IAM / access | Present | IT access replication, IAM controls, service-account deployment, payment-template permissions. |
| Banking / payments / treasury | Present | Banking relationship, trade-finance payment release, wire execution, treasury controls. |
| SaaS subscription controls | Present | Seat expansion, API-limit, admin delegation, subscription scope. |
| Clinical / treatment activation | Present | Kit C, clinical treatment activation, medication activation, protocol start; V6 protocol-start fixture lives here. |
| Privacy / data export | Present | DPRV/data privacy, privacy data-share/export scope. |
| Security operations | Present | Security operations and containment/incident-response candidate surfaces. |
| Public sector | Limited / candidate-only in evidence read | Public-sector emergency procurement appears in parse/admissibility candidate material; not current strict public denominator evidence. |
| Other found | Present | HR/workforce, finance close, legal, insurance, logistics, utility/OT safety, tax/withholding, grant-funded AP. |

## Gov-Safe Learning Boundary

Gov may use:

- General failure-class policy such as false closure, blocker non-detection, packet-key defect, parse failure, and provider transport failure.
- Source-field checks derived only from model-visible runtime source text.
- Required dependency closure rules: exact action, scope, actor/entity, amount/limit, time/currentness, environment/tenant, and required approval fields.
- Active blocker ledgers, invalid closure ledgers, deterministic dependency ledgers, and closure-validation failures.
- Scope matching rules that can be stated without packet truth or answer keys.

Gov must not use:

- Packet truth.
- Sibling ID or sibling side.
- Answer keys or expected verdict labels.
- Scoring map contents.
- Prior failed packet expected verdict.
- Hidden benchmark labels, hidden family tags, or hidden scoring fields.
- Any benchmark-specific packet identity as a decision shortcut.
- Old public-denominator status as proof of a new packet.

Preserved audit areas for this Atlas patch:

- No packet answer keys are included.
- No scoring-map contents are included.
- No sibling truth shortcuts are introduced.
- No prompt-visible hidden labels are introduced.
- The Gov-safe learning boundary remains explicit.

## Recommendations

1. Choose new packets by seam, not by desired outcome. Build balanced ALLOW/ESCALATE siblings only after the source-visible control rule is explicit.
2. Require packet/key hygiene before live use: every expected verdict must be derivable from runtime-visible sources without sibling facts, hidden current-cycle facts, or external truth.
3. Treat a failure class as patched only after no-provider tests cover negative and matching-positive fixtures, runtime wrapper identity is updated, and a live patch-validation or rescue lane passes under trace-bound scoring.
4. Treat a failure class as partially patched when it is only covered by narrow deterministic families, tiny validation, or selected repair evidence.
5. Promote to product Gov policy only source-visible rules that generalize: source-field authority/scope matching, required dependency closure, active blocker preservation, deterministic closure validation, packet/key quarantine, parse fail-closed behavior, and provider transport exclusion.

## Source Map

- `docs/benchmark/HOLOVERIFY_LIVING_SEAM_ATLAS_AND_ARCHITECTURE_LEDGER_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_BLOCKER_PRESERVATION_PATCH_REPORT_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_V4_SMALL_RESCUE_FAILURE_AUTOPSY_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_V5_BLOCKER_CLOSURE_VALIDATION_DESIGN_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_PACKET_DEFECT_REVIEW_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_V5_TIER2_FN_RESCUE_LIVE_ROLLUP_2026_07_04.md`
- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_LIVE_ROLLUP_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_ACCOUNTING_CORRECTION_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_TIER3_FN_HOLO_RESCUE_FAILURE_AUTOPSY_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_PATCH_REPORT_2026_07_05.md`
- `docs/benchmark/HOLOVERIFY_V6_SCOPE_DEPENDENCY_GATE_TINY_PATCH_VALIDATION_POSTLIVE_ARCHITECTURE_AUDIT_2026_07_05.json`
- `docs/benchmark/HOLOVERIFY_V6_TIER3_FN_HOLO_RESCUE_RERUN_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- `docs/benchmark/holoverify_v6_tier3_fn_holo_rescue_rerun_2026_07_05/live_runs/run_20260705T023842Z/v6_tier3_fn_holo_rescue_rerun_live_summary.json`
- `docs/benchmark/holoverify_v6_tier3_fn_holo_rescue_rerun_2026_07_05/live_runs/run_20260705T023842Z/v6_tier3_fn_holo_rescue_rerun_posthoc_score_trace_bound_v1.json`
- `docs/benchmark/HOLOVERIFY_CONTEXT_PRESERVATION_AUDIT_2026_07_05.md`
- `docs/benchmark/holoverify_domain_consolidation_ledger_2026_07_01/HOLOVERIFY_DOMAIN_CONSOLIDATION_LEDGER_2026_07_01.md`
- `holoverify_blind_runner_v0.py`
- `tests/test_holoverify_blind_selector_repair_regression.py`
- `tests/test_holoverify_v5_blocker_closure_validation.py`
- `tests/test_holoverify_v6_scope_dependency_gate.py`
- `tests/test_holoverify_blind_120_live_wrapper.py`
- `tests/test_blind_lane_t6_budget_parity.py`
- `tests/test_holoverify_governed_decision_smoke.py`
