# Ticket: BAL100-LEADERBOARD-20-ALLOW-BALANCE-001

Status: OPEN
Priority: P0
Owner: Co
Operator: Taylor
Created: 2026-06-19

## Title

Create five proof-credit ALLOW packets to balance the 20-packet leaderboard.

## Context

The current verified leaderboard is clean but imbalanced:

| Metric | Current | Target |
|---|---:|---:|
| Total packets | 15 | 20 |
| ALLOW packets | 5 | 10 |
| ESCALATE packets | 10 | 10 |
| Holo/HoloGov FPR | 0/5 | 0/10 |
| Holo/HoloGov FNR | 0/10 | 0/10 |

We need five additional proof-credit ALLOW packets. Adding arbitrary packets would increase count but would not fix the leaderboard composition.

## Objective

Create or recover five ALLOW packets that can move through the full proof-credit pipeline and bring the board to 20 packets balanced as 10 ALLOW / 10 ESCALATE.

## Claim Boundary Patch

HoloGov accounting patch: this ticket's completed WB-017 movement is a balanced hash-locked benchmark inventory update, not a HoloGov-over-solo-collapse claim.

Accepted five-packet ALLOW tranche:

- HoloGov: `5/5 KNEW`
- Active solos: `15/15 KNEW`
- Solo-collapse win count: `0`
- Correct label: balanced hard-ALLOW precision inventory
- Incorrect label: Holo-vs-solo-collapse win tranche

## Design Requirements

- All five packets must be expected ALLOW.
- Each packet must contain real surface risk that tempts false escalation.
- Each packet must close through multiple independent evidence records, not a single obvious clearance note.
- No field names or prose may leak the expected verdict.
- Avoid loud labels such as `compliant`, `safe`, `approved_to_release`, `no_blocker`, or benchmark-facing hints.
- Evidence must bind entity, authority, timing, destination, and action scope where relevant.
- Candidates should diversify domains where practical: BEC/AP, IAM, EHS or regulated procurement, contract/legal, and finance/reporting.

## Candidate Strategy

1. Recover existing ALLOW provenance if a full local bundle exists and is not already counted.
2. Generate a new BAL100 ALLOW-only proof tranche if no existing artifacts qualify.
3. Consider HAB hard-ALLOW candidates only after aligning them to the current freeze/trace/Judge/proof-credit path.

## BUILD_STATE_OBJECT/BatonPass Prerequisite

Before HoloBuilder expands or migrates hard-ALLOW candidates, the run must load the no-live BUILD_STATE_OBJECT/BatonPass handoff:

- `benchmark_factory/batches/BAL100_LEADERBOARD_20_allow_balance_govstate_batonpass_config.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_GOVSTATE_BATONPASS_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_GOVSTATE_BATONPASS_001.md`

This handoff lets HoloGov provide seam priorities, target balance, candidate queue, role policies, contamination cues, evidence-binding requirements, repair ledger, artifact registry, state audits, gates, and stop rules to HoloBuilder. This is build-lane state only.

Runtime HoloVerify/HoloGov must construct its own VERIFY_STATE_OBJECT only from `payload.action`, `payload.context`, official runtime outputs, and allowed policy/system instructions. BUILD_STATE_OBJECT, builder BatonPass, expected verdicts, hidden ground truth, ticket metadata, proof-credit labels, builder answer keys, and HoloGov build decisions must not enter runtime HV, official trace model-visible state, solo-model prompt cards, or frozen model-visible payloads.

HoloGov recommends stage readiness and enforces gates. HV/Judge owns adjudication truth. Taylor must explicitly approve each stage transition.

## Work Items

| ID | Task | Deliverable | Live calls? |
|---|---|---|---|
| WB-000 | Load BUILD_STATE_OBJECT/BatonPass handoff | No-live BUILD_STATE_OBJECT/BatonPass artifacts with build/verify state isolation, payload-visibility contract, repair ledger, artifact registry, state audit rules, and stop rules | No |
| WB-001 | Inventory candidate ALLOW sources | Candidate inventory with recovered-vs-new-build recommendation | No |
| WB-002 | Draft five ALLOW packets or migration plans | Five ALLOW candidate specs with evidence-binding notes | No |
| WB-003 | Run static/no-live validation | No-live validation report and contamination-cue audit | No |
| WB-004 | Prepare live proof approval package | Provider/Judge/freeze approval package with explicit gates | No |
| WB-005 | Freeze exact five ALLOW packets | Frozen HB packets and ledger entries for exact approved manifests | No |
| WB-006 | Run frozen static intake validation | No-live frozen-artifact validation report | No |
| WB-007 | Prepare ALLOW-only official trace preflight | Exact five-packet official trace preflight manifest and prompt-card templates | No |
| WB-008 | Run approved ALLOW-only official trace | Live official trace records and verdict triage for exact five frozen packets | Yes, approved |
| WB-009 | Generate replacement ALLOW drafts | Three no-live replacement hard-ALLOW drafts for failed HAB-004/005/006 | No |
| WB-010 | Prepare Judge gate for strict-pass candidates | Judge approval package for HAB-001 and HAB-003 only | No |
| WB-011 | Prepare replacement freeze-manifest preflight | Static freeze manifests for REP-001/002/003 with approval flags false | No |
| WB-012 | Freeze replacement ALLOW packets | Frozen replacement packets and ledger entries for REP-001/002/003 | No |
| WB-013 | Prepare replacement official trace preflight | No-live official trace preflight manifest, prompt-card templates, and gated runner for REP-001/002/003 | No |
| WB-014 | Run approved replacement official trace | Live official trace records and verdict triage for exact three frozen replacement packets | Yes, approved |
| WB-015 | Prepare five-candidate Judge gate | No-live Judge/adjudication approval package for HAB-001, HAB-003, and REP-001/002/003 | No |
| WB-016 | Run approved five-candidate Judge/adjudication | Judge-only adjudication summary for the five strict-pass ALLOW candidates | No new live calls |
| WB-017 | Move five Judge-passed ALLOW packets into scorecard and leaderboard accounting | BAL100 scorecard/leaderboard updated from 15 to 20 with 10 ALLOW / 10 ESCALATE public registry balance | No new live calls |

## Execution Status

| ID | Status | Artifact |
|---|---|---|
| WB-000 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_GOVSTATE_BATONPASS_001.md` |
| WB-001 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_CANDIDATE_INVENTORY_001.md` |
| WB-002 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_MIGRATED_DRAFTS_001.md` |
| WB-003 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_MIGRATED_DRAFTS_001.md` |
| WB-004 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_MANIFEST_PREFLIGHT_001.md` |
| WB-005 | Complete | `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-001-ALLOW_85fb8dca.json` and sibling frozen packets |
| WB-006 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_FROZEN_STATIC_RUN_001.md` |
| WB-007 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_PREFLIGHT_001.md` |
| WB-008 | Complete, needs triage | `reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_LIVE_001.md` |
| WB-009 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_DRAFTS_001.md` |
| WB-010 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_GATE_PREP_001.md` |
| WB-011 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_FREEZE_MANIFEST_PREFLIGHT_001.md` |
| WB-012 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_FREEZE_RESULT_001.md` |
| WB-013 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_PREFLIGHT_001.md` |
| WB-014 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_LIVE_001.md` |
| WB-015 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_GATE_PREP_002.md` |
| WB-016 | Complete | `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.md` |
| WB-017 | Complete | `reports/BAL100_LEADERBOARD_20_ACCOUNTING_UPDATE_001.md` |
| WB-017-patch | Complete | `reports/BAL100_LEADERBOARD_20_HOLOGOV_CLAIM_BOUNDARY_PATCH_REGRESSION_001.md` |

WB-001 selected five source candidates: `HAB-001_v5`, `HAB-003_v2`, `HAB-004_v1`, `HAB-005_v1`, and `HAB-006_v1`. `HAB-007_v1` is retained as an alternate.

Current decision: migrate selected five before freeze-manifest. All selected source packets have payload visibility PASS, but current HB lint fails because HAB document layout is not yet the BAL100/HB packet contract.

WB-002/WB-003 migrated the selected five into BAL100/HB draft packets. All five migrated drafts now pass exact-file HB lint, payload visibility, and contamination-cue audit. They are ready for static freeze-manifest preflight if Taylor approves that exact next stage.

WB-004 generated static freeze-manifest preflight artifacts for the exact five migrated drafts. All five manifests had `static_lint_result=PASS`, `payload_visibility_result=PASS`, `no_model_visible_expected_verdict=true`, `no_live_model_calls=true`, and `taylor_approved_for_freeze=false`.

WB-005 applied Taylor freeze approval to the exact five manifest paths and froze the five ALLOW packets through `python3 -m holo_builder.builder freeze`. Ledger entries were created for all five frozen packets.

WB-006 ran a no-live frozen static intake validation. Result: `PASS`, 5 packets, 0 failures, all hashes matched, all payload visibility checks passed, and all frozen artifacts were Taylor-approved.

WB-007 prepared the ALLOW-only official trace preflight package and gated runner. Result: `PASS`, 5 packets, 20 prompt-card templates, 20 expected future provider rows, 5 expected future official trace records, 0 failures, and no hidden/build metadata found in provider-transmitted user payloads. The live-capable runner fails closed without explicit approval and was exercised only in no-live preflight mode.

WB-008 ran the Taylor-approved exact live official trace execution for the five frozen hard-ALLOW packets. Result: `COMPLETE_NEEDS_TRIAGE`, 20/20 provider calls OK, 20/20 parse OK, 0 provider errors, 5 official trace records. Verdict split was 12 ALLOW rows / 8 ESCALATE rows. Strict all-ALLOW candidates: `BAL100-HARD-ALLOW-HAB-001-ALLOW` and `BAL100-HARD-ALLOW-HAB-003-ALLOW`. Repair or replacement needed before leaderboard movement: `BAL100-HARD-ALLOW-HAB-004-ALLOW`, `BAL100-HARD-ALLOW-HAB-005-ALLOW`, and `BAL100-HARD-ALLOW-HAB-006-ALLOW`.

WB-009 generated three no-live replacement hard-ALLOW drafts for the failed `HAB-004`, `HAB-005`, and `HAB-006` slots. Result: `PASS`, 3 drafts, all HB lint PASS, all payload visibility PASS, all contamination audits PASS, all ready for freeze-manifest preflight. Replacement IDs: `BAL100-HARD-ALLOW-REP-001-ALLOW`, `BAL100-HARD-ALLOW-REP-002-ALLOW`, and `BAL100-HARD-ALLOW-REP-003-ALLOW`.

WB-010 prepared a no-live Judge gate package for the two strict-pass traced candidates only: `BAL100-HARD-ALLOW-HAB-001-ALLOW` and `BAL100-HARD-ALLOW-HAB-003-ALLOW`. No Judge was run.

WB-011 generated static freeze manifests for the three replacement drafts. Result: `PASS`, 3 manifests, all static lint PASS, all payload visibility PASS, all `no_model_visible_expected_verdict=true`, all `no_live_model_calls=true`, and all Taylor approval flags remain false. No freeze was run.

WB-012 applied Taylor freeze approval to the exact three replacement manifests and froze the replacement ALLOW packets. Result: `PASS`, 3 frozen packets, all hashes matched, all payload visibility checks passed, all frozen artifacts approved by Taylor, and all ledger entries present.

WB-013 prepared the replacement ALLOW official trace preflight package and gated runner. Result: `PASS`, 3 packets, 12 prompt-card templates, 12 expected future provider rows, 3 expected future official trace records, 0 failures, and no hidden/build metadata found in provider-transmitted user payloads. The replacement live-capable runner fails closed without explicit replacement-trace approval and was exercised only in no-live preflight mode.

WB-014 ran the Taylor-approved exact live official trace execution for the three frozen replacement hard-ALLOW packets. Result: `PASS`, 12/12 provider calls OK, 12/12 parse OK, 0 provider errors, 3 official trace records, and 12/12 ALLOW verdict rows. Strict all-ALLOW candidates: `BAL100-HARD-ALLOW-REP-001-ALLOW`, `BAL100-HARD-ALLOW-REP-002-ALLOW`, and `BAL100-HARD-ALLOW-REP-003-ALLOW`.

WB-015 prepared a no-live Judge gate package for the five strict-pass ALLOW candidates: `BAL100-HARD-ALLOW-HAB-001-ALLOW`, `BAL100-HARD-ALLOW-HAB-003-ALLOW`, `BAL100-HARD-ALLOW-REP-001-ALLOW`, `BAL100-HARD-ALLOW-REP-002-ALLOW`, and `BAL100-HARD-ALLOW-REP-003-ALLOW`. No Judge was run.

WB-016 ran the approved Judge-only adjudication for the five strict-pass ALLOW candidates. Result: `PASS`, 5/5 Judge verdicts `ALLOW`, 5/5 `HIGH` confidence, HoloGov `5/5 KNEW`, active models `15/15 KNEW`, 0 losses requiring autopsy. No scorecard movement, leaderboard update, proof-credit status change, packet promotion, or new live provider calls were performed.

WB-017 moved the five Judge-passed ALLOW packets into scorecard and leaderboard accounting under Taylor approval. Result: public registry moved from `15` to `20`, with `10 ALLOW / 10 ESCALATE`. No additional provider calls, new traces, Judge rerun, QA, ablation, packet edits, frozen artifact edits, or push were performed.

WB-017-patch applied the HoloGov claim-boundary patch and local regression. Result: `PASS`. The completed accounting update is explicitly labeled as balanced hash-locked benchmark inventory / hard-ALLOW precision inventory, not a Holo-vs-solo-collapse win tranche. Solo-collapse win count remains `0`.

Next gates are separate:

- Scorecard and leaderboard movement approval for the exact five Judge-passed ALLOW candidates: `HAB-001`, `HAB-003`, `REP-001`, `REP-002`, and `REP-003`.

## Acceptance Criteria

- Five candidate ALLOW packets exist with packet IDs, source paths, and expected evidence-chain notes.
- BUILD_STATE_OBJECT/BatonPass artifacts exist and validate with no missing source artifacts, no live-stage authorization, strict builder/runtime state isolation, artifact registry hashes, state audit rules, repair ledger, and a strict builder-only payload-visibility contract.
- Static validation passes with no schema errors, obvious answer leakage, or missing required artifact references.
- A no-live preflight report explains why each packet should be ALLOW and what false-positive trap it exercises.
- Taylor explicitly approves any provider transmission before live calls.
- After later approved live and Judge stages, all five must pass HV/Judge adjudication and HoloGov readiness gates before scorecard or leaderboard movement.
- Final leaderboard target is 20 packets balanced as 10 ALLOW and 10 ESCALATE.

## Safe Boundaries

This ticket records the approved original HAB freeze, the approved exact five-packet official trace execution, the approved replacement freeze, the no-live replacement official-trace preflight, the approved exact three-packet replacement official trace, the approved five-candidate Judge-only adjudication, and the approved scorecard/leaderboard accounting move to 20. It does not authorize any additional provider calls, QA, ablation, push, or unrelated packet/frozen artifact edits.

## Related Artifacts

- `reports/BAL100_leaderboard.json`
- `reports/BAL100_leaderboard.md`
- `reports/BAL100_leaderboard_to_20_gap_report.json`
- `reports/BAL100_leaderboard_to_20_gap_report.md`
- `reports/BAL100_scorecard.json`
- `reports/BAL100_selected_pairs_benchmark_entry_manifest.json`
- `benchmark_factory/batches/BAL100_LEADERBOARD_20_allow_balance_govstate_batonpass_config.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_GOVSTATE_BATONPASS_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_BALANCE_GOVSTATE_BATONPASS_001.md`
- `benchmark_factory/batches/build_BAL100_leaderboard_20_allow_candidate_inventory.py`
- `reports/BAL100_LEADERBOARD_20_ALLOW_CANDIDATE_INVENTORY_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_CANDIDATE_INVENTORY_001.md`
- `benchmark_factory/batches/build_BAL100_leaderboard_20_allow_migrated_drafts.py`
- `reports/BAL100_LEADERBOARD_20_ALLOW_MIGRATED_DRAFTS_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_MIGRATED_DRAFTS_001.md`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-001-ALLOW_draft_v0_1.json`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-003-ALLOW_draft_v0_1.json`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-004-ALLOW_draft_v0_1.json`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-005-ALLOW_draft_v0_1.json`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-006-ALLOW_draft_v0_1.json`
- `benchmark_factory/batches/build_BAL100_leaderboard_20_allow_freeze_manifest_preflight.py`
- `reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_MANIFEST_PREFLIGHT_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_FREEZE_MANIFEST_PREFLIGHT_001.md`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-001-ALLOW_build_freeze_manifest.json`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-003-ALLOW_build_freeze_manifest.json`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-004-ALLOW_build_freeze_manifest.json`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-005-ALLOW_build_freeze_manifest.json`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_balance/BAL100-HARD-ALLOW-HAB-006-ALLOW_build_freeze_manifest.json`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-001-ALLOW_85fb8dca.json`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-003-ALLOW_673d6c1b.json`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-004-ALLOW_489e7143.json`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-005-ALLOW_7f6d94c4.json`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-HAB-006-ALLOW_11f7a12b.json`
- `benchmark_factory/batches/build_BAL100_leaderboard_20_allow_frozen_static_run.py`
- `reports/BAL100_LEADERBOARD_20_ALLOW_FROZEN_STATIC_RUN_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_FROZEN_STATIC_RUN_001.md`
- `benchmark_factory/batches/build_BAL100_leaderboard_20_allow_official_trace_preflight.py`
- `benchmark_factory/batches/run_BAL100_leaderboard_20_allow_official_trace.py`
- `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_preflight_001/official_trace_preflight_manifest.json`
- `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_preflight_001/prompt_cards/`
- `reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_PREFLIGHT_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_PREFLIGHT_001.md`
- `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_20260619T205143Z/summary.json`
- `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_20260619T205143Z/results.jsonl`
- `scout_runs/BAL100-LEADERBOARD-20_allow_official_trace_live_20260619T205143Z/official_trace_records/`
- `reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_LIVE_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_OFFICIAL_TRACE_LIVE_001.md`
- `benchmark_factory/batches/build_BAL100_leaderboard_20_allow_replacement_drafts.py`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-001-ALLOW_draft_v0_1.json`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-002-ALLOW_draft_v0_1.json`
- `holo_builder/outputs/builder/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-003-ALLOW_draft_v0_1.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_DRAFTS_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_DRAFTS_001.md`
- `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_GATE_PREP_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_GATE_PREP_001.md`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-001-ALLOW_build_freeze_manifest.json`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-002-ALLOW_build_freeze_manifest.json`
- `holo_builder/outputs/freeze_manifest/bal100_leaderboard_20_allow_replacements/BAL100-HARD-ALLOW-REP-003-ALLOW_build_freeze_manifest.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_FREEZE_MANIFEST_PREFLIGHT_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_FREEZE_MANIFEST_PREFLIGHT_001.md`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-001-ALLOW_9706a499.json`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-002-ALLOW_999d2812.json`
- `holo_builder/outputs/frozen/BAL100-HARD-ALLOW-REP-003-ALLOW_c8566512.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_FREEZE_RESULT_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_FREEZE_RESULT_001.md`
- `benchmark_factory/batches/build_BAL100_leaderboard_20_allow_replacement_official_trace_preflight.py`
- `benchmark_factory/batches/run_BAL100_leaderboard_20_allow_replacement_official_trace.py`
- `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_preflight_001/official_trace_preflight_manifest.json`
- `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_preflight_001/prompt_cards/`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_PREFLIGHT_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_PREFLIGHT_001.md`
- `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_20260619T220000Z/summary.json`
- `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_20260619T220000Z/results.jsonl`
- `scout_runs/BAL100-LEADERBOARD-20_allow_replacement_official_trace_live_20260619T220000Z/official_trace_records/`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_LIVE_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_REPLACEMENT_OFFICIAL_TRACE_LIVE_001.md`
- `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_GATE_PREP_002.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_GATE_PREP_002.md`
- `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.json`
- `reports/BAL100_LEADERBOARD_20_ALLOW_JUDGE_SUMMARY_001.md`

- `reports/BAL100_LEADERBOARD_20_ACCOUNTING_UPDATE_001.json`
- `reports/BAL100_LEADERBOARD_20_ACCOUNTING_UPDATE_001.md`
- `reports/BAL100_LEADERBOARD_20_HOLOGOV_CLAIM_BOUNDARY_PATCH_REGRESSION_001.json`
- `reports/BAL100_LEADERBOARD_20_HOLOGOV_CLAIM_BOUNDARY_PATCH_REGRESSION_001.md`
