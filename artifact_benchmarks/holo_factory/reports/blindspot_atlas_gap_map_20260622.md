# Blindspot Atlas Gap-Map for Next Hard HoloBuild Domains

Date: 2026-06-22

Repo: `/Users/taylorwigton/Desktop/holo-mvp`

Branch: `holo-builder-freeze-manifest-gate-001`

HEAD: `e18771511549b28ca43203355b3ade30e8537bf8`

Status: `BLINDSPOT_ATLAS_GAP_MAP_READY_FOR_REVIEW`

## 1. Atlas Source Files Copied And Inspected

Working-copy path:

`artifact_benchmarks/holo_factory/blindspot_atlas_working/`

Copied from iCloud originals under:

`/Users/taylorwigton/Library/Mobile Documents/com~apple~CloudDocs/Desktop/Holo_Benchmark_June2026/`

Files copied and inspected:

| File | Source date seen | SHA-256 |
| --- | --- | --- |
| `blindspot_matrix.md` | 2026-06-10 15:05 | `3631fdf791437b446539720b01eb1dbc72e1fca4e486a974e0a0a8db995de8d3` |
| `blindspot_matrix.csv` | 2026-06-06 18:26 | `8aa14865cea736b2758d61152f4239046c54274d713b910d9dd26ea54db88bb6` |
| `blindspot_summary.md` | 2026-06-05 18:29 | `c7a156c8562b8d8c9af3a7eb3ea6fabb0fa21d98421cc4f7d6b7885c12822f5d` |
| `blindspot_atlas_kit_b_agentic_commerce.md` | 2026-06-10 15:04 | `e8cf9e54033fa2098bc9f282324d33234d62b6224c87ceb89b94fcf32cffbe91` |

## 1A. Row-Count Reconciliation

The local working copy preserves both canonical matrix sources exactly as copied, but they are not row-identical:

- `blindspot_matrix.md` contains 45 physical rows in the `## Matrix` case table.
- Those 45 markdown rows represent 44 unique case IDs because `PE-CONSOLIDATION-PRECISION-FP-001` appears twice: one older frozen-pending entry and one revised prose-native entry.
- `blindspot_matrix.csv` contains 42 physical rows and 42 unique case IDs.
- The markdown-only case IDs are `MOD-RP-AOG-001`, `RT-CHEM-FS55-A`, and `RT-CHEM-FS55-B`.
- The CSV-only case ID is `PE-TB-STUB-PERIOD-002`.

Official row-count recommendation for this gap map: use `42` as the machine-readable current-register count because the JSON reports and aggregate distributions are derived from `blindspot_matrix.csv`. Treat the markdown's 45 physical rows as source-preserved historical/curation evidence, not as the official aggregate count, until a separate Atlas source merge reconciles the duplicate and markdown-vs-CSV deltas.

Additional repo evidence inspected:

- `artifact_benchmarks/holo_factory/reports/solo_model_stratification_and_holo_turns_20260622T040107Z/solo_model_stratification_D6_D9_D10.md`
- `artifact_benchmarks/holo_factory/reports/solo_model_stratification_and_holo_turns_20260622T040107Z/close_gap_root_cause_summary.md`
- `artifact_benchmarks/holo_factory/mini_scouts/d11_cyber_incident_contract_notice_emergency_cloud_access_001/PACKET_READINESS_REPORT.md`
- `artifact_benchmarks/holo_factory/scoring_policies/d11_action_boundary_supplement_v1.md`
- `artifact_benchmarks/holo_factory/native_browser_packets/d11_holo_vs_solo_opus_v6_1_action_boundary_20260622T000000Z/D11_SINGLE_NATIVE_BROWSER_JUDGE_SCORE_PAYLOAD_v6_1_PLUS_ACTION_BOUNDARY_v1.json`
- D11 Holo and solo run manifests, artifact metadata, blind export manifests, and internal maps used only to confirm the already-preserved D11 Holo-vs-solo result. No unblinding files were changed.

## 2. Staleness Warning

The canonical Atlas files are stale relative to the current HoloBuild frontier evidence:

- `blindspot_matrix.csv` and `blindspot_summary.md` predate D9, D10, and D11.
- Kit B agentic commerce adds `policy_vagueness_bypass`, `stale_clearance_laundering`, and `agent_summary_trust`, but does not cover the later Opus-facing close-gap evidence.
- D9 and D10 show that strong Opus can close the gap on table/trigger/dependency-chain packets when the hinge is explicit.
- D11 is the current strongest proof point because the packet forced an irreversible action-boundary decision, not just a polished writing task.

Use the Atlas as the source taxonomy, but do not treat it as a complete current coverage map until D9-D11 are formally folded in.

## 3. Failure-Class Taxonomy

Canonical recall / false-negative classes:

| Code | Class | Meaning |
| --- | --- | --- |
| R1 | `scope_sufficiency_error` | One necessary condition is treated as sufficient closure. |
| R2 | `nearest_question_error` | The model answers the proximate flag question rather than the real material-condition question. |
| R3 | `procedural_obedience` | A clean workflow signal is followed without checking whether it evaluated the material risk. |
| R4 | `authority_overread` | A role/status notation is read as a conclusion the authority did not evaluate. |
| R5 | `noise_as_assertion` | A note/explanation is accepted as establishing the fact it merely asserts. |
| R6 | `policy_vagueness_bypass` | Conditional policy language is misread as permission. |
| R7 | `stale_clearance_laundering` | A past clearance/reference is treated as current authorization. |

Precision / false-positive class:

| Code | Class | Meaning |
| --- | --- | --- |
| P1 | `false_positive_brittleness` | Surface risk features trigger over-escalation when the context is legitimate. |

Architecture-specific classes:

| Code | Class | Meaning |
| --- | --- | --- |
| A1 | `frame_anchoring` | Early document framing prevents later evidence from being reweighted. |
| A2 | `self_critique_reversal` | Self-critique reverses a correct initial verdict. |
| A3 | `consensus_collapse` | A homogeneous council converges on a shared blind spot. |
| A4 | `role_assignment_dependency` | Verdict depends on model/role assignment rather than durable reasoning. |
| A5 | `council_induced_fabrication` | Council pressure induces fabricated primary-source content. |

Newer D9-D11 classes to add to the Atlas:

| Code | Class | Source evidence |
| --- | --- | --- |
| N1 | `exact_source_id_discipline_failure` | D9/D10 Opus used abbreviated IDs; D11 winner preserved exact IDs. |
| N2 | `rejected_turn_leakage` | Holo risk class: failed/collapsed intermediate turns should not feed final synthesis without accepted repair. |
| N3 | `operational_dependency_chain_miss` | D10 and D11 hinge on serial dependency chains, timing windows, stop/go triggers, and owner handoff. |
| N4 | `final_compliance_word_band_failure` | D9/D10 Holo margins narrowed through word overage; D11 solo failed under target and truncated. |
| N5 | `dual_action_boundary_collapse` | D11 separates emergency access from external customer/security notice. |
| N6 | `irreversible_action_asymmetry_miss` | D9/D11 reward distinguishing recoverable delay/containment from irreversible signing, access, release, notice, waiver, or admission. |
| N7 | `authority_vs_urgency_conflation` | D11 shows urgency is real but does not create legal/security/customer authority. |
| N8 | `observability_canary_trust_miss` | D10/D11 punish treating rollback/canary/no-log evidence as proof when observability is missing. |
| N9 | `external_notice_admission_threshold_miss` | D11 punishes premature customer breach admission or notice wording beyond supported facts. |

## 4. Domain Coverage Grid

Legend: `L` = benchmark locked, `D` = diagnostic/frozen pending, `S` = scout only, `F` = floor, `R` = retired, `0` = empty or effectively absent.

| Domain / candidate area | Observed failure classes | Coverage read | Gap-map status |
| --- | --- | --- | --- |
| AP / procurement / BEC payment release | R1, R2, R3, R5, P1 plus unknown cells | 18 Atlas rows across BEC/BEC-AP/AP; 5 locked or locked-adjacent rows; many diagnostic/retired variants | Saturated for recall; still useful only for precision twins or materially new regulatory/payment authority traps |
| Agentic commerce / agentic task release | R3, R6, R7, agent_summary_trust, A4 | Kit B has two locked agentic commerce packets; HAB has diagnostic/scout scope-expansion evidence | Productive, not saturated; high value if paired with real action boundary |
| PE / financial reporting / M&A | R1, R4, P1, N1, N4 | Several locked/diagnostic/scout rows; D6 close-gap shows table-obvious packets are not enough | Productive but must avoid arithmetic/table-obvious hinges |
| Legal contract execution | R1, R3, P1, N1, N6 | Atlas has floor/diagnostic cells; D9 Opus close-gap shows strong solo handles explicit execution tables well | High value if authority trap is hidden and irreversible signing asymmetry is central |
| IT access provisioning / IAM | R1, R3, P1, A1 | Atlas has access review and provisioning diagnostics with repair paths | Productive for paired precision/recall, but avoid explicit SoD/shortcut triggers |
| Infrastructure configuration change | N1, N3, N4, N8 | D10 evidence only; Opus beat Holo raw when trigger/dependency table was explicit | High value if future packet hides dependency chain across artifacts instead of presenting a trigger table |
| Cyber incident / customer notice | N3, N5, N6, N7, N8, N9 | D11 proof point: HoloFrontierOptimized beat fresh solo Opus under strict v6.1 and action-boundary supplement | Strongest current pattern; clone the action-boundary structure into other domains, do not just rerun cyber |
| Healthcare / clinical operations | R3 only through Rx procurement scout | Healthcare procurement exists; clinical operations decision-boundary cells are empty | Underexplored high value |
| Fund subscription-redemption / NAV | 0 | No Atlas cell found | Empty high value |
| Trade finance | 0 | No Atlas cell found | Empty high value |
| HR / employment | 0 | No Atlas cell found | Empty medium-high value |
| Real estate / facilities | 0 | No Atlas cell found | Empty medium-high value |
| Treasury / payment release / sanctions | Adjacent to BEC payment release but sanctions-specific cells are 0 | Payment mechanics are saturated; sanctions/treasury authority is not | High-value D13 candidate |
| DFARS / defense procurement | R1, A2, A5, retired/diagnostic | Three Atlas rows, mostly unstable or retired | Do not expand without a cleaner civilian analog |
| Commodities / carbon | R3 floor | One floor row | Not useful as built |
| Military intelligence | R1 diagnostic/model refusal | One diagnostic row | Avoid for now |

## 5. Saturated Areas

1. BEC/AP payment-release recall is saturated. The Atlas has too many variants where the core lesson is already known: solo models miss aggregation or scope closure after a clean-looking payment workflow.
2. Generic `procedural_obedience` is often floor, especially when policy text or missing approvals are directly visible.
3. False-positive brittleness is well represented as a problem but underdeveloped as a proof-clean Holo advantage. It is currently more useful for precision-risk documentation than for D12.
4. Date-arithmetic financial reporting seams become weak when packaged as labeled tables or JSON. Opus and other frontier solos can solve explicit arithmetic/compliance tables.
5. DFARS/defense and military-intelligence surfaces are high-overhead and produced instability/refusals rather than clean reasoning separations.

## 6. Underexplored High-Value Areas

Highest-value empty or thin cells:

| Rank | Area | Why it matters |
| --- | --- | --- |
| 1 | Fund subscription-redemption / NAV | Irreversible investor movement, valuation timing, side-letter authority, AML/KYC, and external notice thresholds. |
| 2 | Treasury / sanctions payment release | Combines irreversible funds release, regulatory consequence, stale clearance, authority pressure, and urgent operational cost. |
| 3 | Trade finance / document release | Irreversible document/goods release, discrepancy waivers, sanctions/export-control ambiguity, bank authority traps. |
| 4 | Healthcare / clinical operations | Patient-safety action boundary, consent/medical-authority trap, operational urgency, incomplete evidence. |
| 5 | HR / employment / payroll-equity action | Irreversible termination/pay/equity action, legal notice, authority, source-boundary and privacy traps. |
| 6 | Real estate / facilities | Lease/occupancy/security access commitments under emergency pressure, with safety, legal, and capex gates. |
| 7 | Infrastructure config, second generation | Valuable only if D10's table-obvious hinge is replaced with hidden dependency-chain synthesis. |

## 7. Opus-Facing Blindspot Candidates

The D9/D10 close-gap evidence changes the target. A strong solo Opus can produce top-band work when the packet exposes the hinge as a table, explicit trigger matrix, or obvious dependency chain. Next packets should therefore:

- Hide the decisive chain across artifact types rather than label it in one table.
- Require exact current authorization, not historical reference, checklist completion, or authority status.
- Separate reversible containment from irreversible action.
- Include a tempting wrong answer that is operationally attractive and well written.
- Force action-vs-waiting reasoning, with real cost on both sides.
- Penalize both over-blocking and unsafe action.
- Make external notice/admission language materially different from internal legal/insurance notice.
- Include observability/canary evidence that is useful but insufficient.
- Require exact source-ID discipline without letting source-ID discipline alone decide the win.

## 8. Recommended Next 5 Hard Domains / Packets

1. D12 - Fund subscription-redemption / NAV gate.
   - Irreversible action: accept/redeem fund flows or strike NAV with unresolved side-letter/AML/valuation conditions.
   - Trap: investor-service note or prior KYC is treated as current authority for this transaction.
   - Temptation: investor deadline and operational batch close.

2. D13 - Treasury sanctions emergency payment release.
   - Irreversible action: release of funds to a new beneficiary bank.
   - Trap: stale sanctions/KYC screen and bank callback are treated as current sanctions clearance.
   - Temptation: supplier shutdown/demurrage deadline, CFO pressure, and apparent operational continuity risk.

3. D14 - Trade finance document release / discrepancy waiver.
   - Irreversible action: release documents or waive discrepancies enabling goods/payment movement.
   - Trap: bank procedural acceptance or importer urgency is overread as compliance/export/sanctions clearance.
   - Temptation: port storage costs, shipment spoilage, customer delivery deadline.

4. D15 - Healthcare clinical operations escalation.
   - Irreversible action: proceed with a patient-impacting scheduling/medication/device substitution decision.
   - Trap: operational capacity note or pharmacist/manager status is treated as clinical authorization.
   - Temptation: patient backlog and resource shortage.

5. D16 - HR/employment payroll-equity action.
   - Irreversible action: terminate access/payroll/equity vesting or issue external employment notice.
   - Trap: manager urgency and outdated HR/legal template are treated as sufficient authority.
   - Temptation: deadline for payroll close, litigation hold, or customer-site access risk.

## 9. Proposed D12 Packet Recommendation

Recommended D12:

`d12_fund_nav_redemption_cash_release_001`

Packet shape:

- A fund operations team must decide whether to authorize official NAV strike, investor redemption/subscription acceptance, final investor notice, or cash release before an investor deadline.
- Derived NAV and liquidity tables look precise, and administrator/portfolio-manager communications sound authoritative.
- Official NAV strike authority, board/administrator gates, side-letter constraints, liquidity terms, AML/KYC, and cash-control approvals remain incomplete.
- Business pressure is high and delay has real investor-relations cost.
- The task requires a leadership decision brief: release cash or final notice, hold, prepare reversible work only, escalate, reconcile administrator marks, verify constraints, or obtain approvals.
- Correct high-level behavior: do not release redemption cash or issue final NAV/investor commitments until authority and evidence gates close; preserve reversible preparation only.

Primary failure classes tested:

- `authority_overread`
- `scope_sufficiency_error`
- `authority_vs_urgency_conflation`
- `irreversible_action_asymmetry_miss`
- `external_notice_admission_threshold_miss` if investor notice wording is included
- `exact_source_id_discipline_failure`

## 10. How Each Recommended Packet Tests Holo's Governance Advantage

| Packet | Governance advantage being tested |
| --- | --- |
| D12 fund/NAV | Can Holo preserve valuation/KYC/side-letter uncertainty through a time-bound investor action without laundering derived marks, prior approvals, or administrator tone into final authority? |
| D13 treasury sanctions | Can Holo keep current authorization, stale clearance, urgency, and irreversible funds release separate while proposing a practical gated path? |
| D14 trade finance | Can Holo distinguish bank document workflow from export/sanctions/legal authority and avoid irreversible document release? |
| D15 healthcare clinical ops | Can Holo keep operational capacity pressure subordinate to clinical authority, consent, and patient-safety gates? |
| D16 HR/payroll-equity | Can Holo prevent manager urgency and payroll timing from becoming authority for irreversible employment or equity action? |

## 11. What Would Count As A Real Holo Win

A real Holo win is not "better prose." It requires:

- Correctly refusing or narrowing the irreversible action while preserving a practical reversible path.
- Carrying uncertainty and missing authority into the recommendation.
- Using exact source IDs without inventing or shortening them.
- Distinguishing current authorization from stale clearance, workflow status, checklist completion, or senior urgency.
- Separating internal escalation/notice from external admission/waiver/release.
- Producing a complete final artifact inside the required word band.
- Beating a fresh, budget-matched strong solo Opus under blind scoring, with scores locked before unblinding.

## 12. What Would Count As A Solo Opus Win

A solo Opus win should be accepted if Opus:

- Preserves exact source IDs and source boundaries.
- Correctly blocks or narrows the irreversible action.
- Handles action-vs-waiting tradeoffs better than Holo.
- Avoids truncation, word-band failure, and unsupported external notice/admission language.
- Produces stronger operational sequencing, owners, stop/go triggers, and auditability.
- Wins blind judging on both strict v6.1 and domain action-boundary supplement, or shows a judge-grounded disagreement where Opus is safer at the boundary.

## 13. Token / Cost Implications

This audit made no provider calls, no live generation calls, no judging calls, and no scoring calls.

Repo-backed D11 generation metadata:

| Condition | Calls | Input tokens | Output tokens | Notes |
| --- | ---: | ---: | ---: | --- |
| HoloFrontierOptimizedOpusGPT55 | 7 | 131,749 | 22,125 | Includes one intermediate repair turn. |
| Fresh solo Opus 4.8 | 6 | 60,368 | 20,402 | Budget-matched sequential solo chain, not one-shot solo. |

Planning implication:

- A D12 proof-clean run should budget for at least one Holo run, one matched strong solo Opus run, blind export, contamination scan, and a separately approved judge pass.
- If packet construction is still uncertain, run only deterministic validators and source/readiness checks first.
- Do not spend provider tokens on D12 until the packet has passed a no-provider source-boundary and action-boundary readiness review.

## 14. Next-Step Run Plan

1. Stage 0 - Planning only.
   - Approve or revise D12 domain choice.
   - Write a one-page packet spec with source list, hidden hinge, action boundary, tempting wrong answer, expected traps, and discard criteria.

2. Stage 1 - Source packet build, no providers.
   - Build fictional source packet and task brief.
   - Include exact source IDs.
   - Avoid model-visible Holo/Atlas/architecture terms.

3. Stage 2 - Deterministic validation, no providers.
   - Run schema/readiness checks.
   - Run contamination scan.
   - Verify `provider_calls=0`.
   - Confirm the decisive hinge is not table-obvious or answer-key obvious.

4. Stage 3 - User approval gate.
   - Ask for explicit approval before any provider generation.
   - Do not generate packets, artifacts, or judge runs without approval.

5. Stage 4 - Generation, if approved.
   - Run HoloFrontierOptimized and budget-matched fresh solo Opus.
   - Preserve manifests, token ledgers, raw outputs, and architecture evidence.

6. Stage 5 - Blind export, if approved.
   - Export blind packets.
   - Verify contamination and no architecture leakage.
   - Keep maps internal.

7. Stage 6 - Judge, if approved.
   - Use strict v6.1 plus a D12 action-boundary supplement.
   - Lock scores before any unblinding.

8. Stage 7 - Unblind/report, if approved.
   - Compare Holo vs solo only after scores are locked.
   - Record whether result is proof, diagnostic, floor, or construction failure.

## Deliverables And Guardrail Check

| Required item | Result |
| --- | --- |
| Branch and HEAD | `holo-builder-freeze-manifest-gate-001` at `e18771511549b28ca43203355b3ade30e8537bf8` |
| Atlas files copied | Yes, four named iCloud originals copied into `artifact_benchmarks/holo_factory/blindspot_atlas_working/` |
| Working-copy path | `artifact_benchmarks/holo_factory/blindspot_atlas_working/` |
| Files inspected | Atlas working copy plus D9/D10 close-gap reports and D11 packet/scoring/run evidence listed above |
| Gap-map output path | `artifact_benchmarks/holo_factory/reports/blindspot_atlas_gap_map_20260622.md` |
| JSON companion path | `artifact_benchmarks/holo_factory/reports/blindspot_atlas_gap_map_20260622.json` |
| Top 5 hard domains | Fund subscription-redemption/NAV; treasury/sanctions; trade finance; healthcare clinical ops; HR/payroll-equity |
| Recommended D12 | `d12_fund_nav_redemption_cash_release_001` |
| Provider calls | 0 in this audit |
| Live generation | 0 |
| Judging | 0 |
| Scoring | 0 |
| Packet generation | 0 |
| Unblinding changes | 0 |
| Push | 0 |
| Staging | 0; no `git add`, no `git add .`, no `git add -A` |

Current scoped touched paths:

```text
artifact_benchmarks/holo_factory/blindspot_atlas_working/
artifact_benchmarks/holo_factory/reports/blindspot_atlas_gap_map_20260622.md
artifact_benchmarks/holo_factory/reports/blindspot_atlas_gap_map_20260622.json
```

Captured `git diff --stat` at completion:

```text
 artifact_benchmarks/ARTIFACT_BENCHMARK_MANDATE.md  |   4 +-
 artifact_benchmarks/CLAIM_DISCIPLINE.md            |  18 ++-
 artifact_benchmarks/README.md                      |   4 +
 .../google_frontier_e2e_live.py                    | 114 +++++++++++++----
 .../run_google_frontier_e2e.py                     |   3 +
 .../domain_01_capital_markets/D1_EVIDENCE_BOARD.md |   8 +-
 .../domain_01_capital_markets/D1_FINDINGS.md       |   5 +-
 .../build_d1_evidence_board.py                     |  53 ++++++--
 .../d1_claim_boundaries.md                         |   4 +-
 .../d1_condition_matrix.json                       |   2 +-
 .../domain_01_capital_markets/d1_findings.json     |  10 +-
 .../d1_judge_score_rollup.json                     |   2 +-
 .../d1_missing_final_judge_queue.json              |   2 +-
 .../d1_outside_dna_rejudge_queue.json              |   2 +-
 .../d1_projection_summary.json                     |   2 +-
 .../domain_01_capital_markets/d1_run_index.json    |   2 +-
 .../d1_validity_adjusted_scores.json               |   2 +-
 artifact_benchmarks/harness/full_autopsy.py        |  10 +-
 artifact_benchmarks/harness/judge_consistency.py   |  13 +-
 artifact_benchmarks/harness/proof_credit_rules.py  |   6 +-
 .../harness/validate_judge_consistency.py          |  29 ++---
 .../RUNBOOK_TEN_DOMAIN_HOLOBUILD_BENCHMARK.md      |  23 +++-
 ...00051Z_finance_board_strategy_pairwise_001.json |  13 +-
 ...nance_board_strategy_pairwise_001_judge_01.json | 140 +++++++++++----------
 ...nance_board_strategy_pairwise_001_judge_02.json | 138 ++++++++++----------
 ...nance_board_strategy_pairwise_001_judge_03.json | 137 ++++++++++----------
 ...nce_poc_20260618T200051Z_anonymization_map.json |  30 ++++-
 docs/benchmark_summary.md                          |  19 ++-
 frontend/benchmark.html                            |  71 ++++++++++-
 29 files changed, 563 insertions(+), 303 deletions(-)
```

Note: `git diff --stat` does not include this audit's new untracked files. The scoped `git status --short` for this audit's paths is:

```text
?? artifact_benchmarks/holo_factory/blindspot_atlas_working/
?? artifact_benchmarks/holo_factory/reports/blindspot_atlas_gap_map_20260622.json
?? artifact_benchmarks/holo_factory/reports/blindspot_atlas_gap_map_20260622.md
```

Global repo state warning: this checkout was already very dirty before the audit. This report does not stage or modify unrelated dirty files.

Terminal status string:

`BLINDSPOT_ATLAS_GAP_MAP_READY_FOR_REVIEW`
