# HoloBuild Action Boundary Test Spec - 2026-07-05

Status: concrete gate/test specification derived from `HOLOBUILD_ACTION_BOUNDARY_PRESSURE_TEST_PLAN_2026_07_05`. No provider calls. No live product actions. No production behavior changes. No staging, commit, or push.

## Purpose

This document converts the HoloBuild action-boundary pressure-test plan into provider-free gates and test cases. The tests are intended to become deterministic unit, fixture, or validation tests before HoloBuild product pilots move beyond shadow.

The central rule is simple: HoloBuild builds and audits artifacts; it does not execute, publish, release, deploy, or authorize downstream reliance without deterministic gates and explicit human approval.

## Test Status Labels

| Label | Meaning |
| --- | --- |
| `MUST_PASS_NOW` | The repo should already support this invariant or the test should be straightforwardly fixture-backed. |
| `EXPECTED_FAIL_UNTIL_FIXED` | The pressure-test plan identified a current gap; the test should fail until code or docs are corrected. |
| `SPEC_ONLY_NEW_GATE` | New gate expected for product readiness; test may need a new validator implementation. |
| `NO_PROVIDER` | Test must use fixtures, monkeypatching, static inspection, stored traces, or pure functions only. |
| `NO_PRODUCTION_ACTION` | Test must not call deploy, publish, freeze real artifacts, live product endpoints, providers, judges, or ledger-mutating commands. |

## Fixture Contract

Every test should use local fixtures only. Recommended fixture roots:

- `tests/fixtures/holobuild/action_boundary/`
- `tests/fixtures/holobuild/product_surface/`
- `docs/product/fixtures/holobuild_action_boundary/` if the fixture is documentation-facing rather than pytest-facing.

Minimum fixture files:

- `action_boundary_allow_packet.json`: top-level `action` plus `context.documents`.
- `payment_email_packet.json`: legacy `payload.action` plus `payload.context`.
- `qa_clean_to_freeze.json`: synthetic QA result with `final_classification = CLEAN_TO_FREEZE`.
- `qa_needs_repair.json`: synthetic QA result with `final_classification = NEEDS_REPAIR`.
- `human_approval_valid.json`: approval with approver, timestamp, exact artifact hash, scope, and non-execution disclaimer.
- `human_approval_missing.json`: approval-like record missing required fields.
- `run_manifest_complete.json`: manifest with trace inventory and accounting.
- `run_manifest_incomplete.json`: manifest missing required trace/accounting fields.
- `failure_run_manifest.json`: preserved failed run with regression-packet request.

Fixtures must not contain secrets, provider credentials, live customer data, or real deploy targets.

## Gate Matrix

| Gate ID | Required by user item | Status | Summary |
| --- | --- | --- | --- |
| `HB-GATE-001` | 1 | `SPEC_ONLY_NEW_GATE` | Artifact-build vs execution boundary. |
| `HB-GATE-002` | 2 | `SPEC_ONLY_NEW_GATE` | Freeze requires explicit human approval. |
| `HB-GATE-003` | 3 | `MUST_PASS_NOW` | No autonomous deploy/release or live-run default. |
| `HB-GATE-004` | 4 | `EXPECTED_FAIL_UNTIL_FIXED` for top-level `action_boundary`; `MUST_PASS_NOW` for legacy payload packets. |
| `HB-GATE-005` | 5 | `MUST_PASS_NOW` for lint; `EXPECTED_FAIL_UNTIL_FIXED` for freeze. |
| `HB-GATE-006` | 6 | `EXPECTED_FAIL_UNTIL_FIXED` or explicit known-gap state. |
| `HB-GATE-007` | 7 | `SPEC_ONLY_NEW_GATE` | Human reliance disclosure. |
| `HB-GATE-008` | 8 | `MUST_PASS_NOW` for read-only/sanitized dashboard; `SPEC_ONLY_NEW_GATE` for full partner packet. |
| `HB-GATE-009` | 9 | `SPEC_ONLY_NEW_GATE` | Trace/accounting requirements. |
| `HB-GATE-010` | 10 | `SPEC_ONLY_NEW_GATE` | Failure preservation and regression-packet creation. |

## HB-GATE-001: Artifact-Build Vs Execution Boundary

Goal: prove HoloBuild outputs are candidate artifacts and evidence packages, not autonomous actions.

Provider-free tests:

1. `test_holobuild_packet_terminal_status_does_not_execute_action`
   - Fixture: `run_manifest_complete.json`.
   - Procedure: validate that `terminal_status` is one of `NEEDS_REPAIR`, `BLOCKED`, `SHADOW_READY`, `FROZEN_PENDING_HUMAN`, or `HUMAN_RELEASED`.
   - Pass: no status implies payment release, deploy, publish, send, account update, vendor-master update, or policy mutation.
   - Fail: manifest contains `EXECUTED`, `DEPLOYED`, `SENT`, `PAYMENT_RELEASED`, `PUBLISHED`, `AUTO_RELEASED`, or equivalent.

2. `test_holobuild_artifact_manifest_forbids_execution_targets`
   - Fixture: candidate artifact manifest.
   - Procedure: scan declared actions and destinations.
   - Pass: manifest has `artifact_kind`, `candidate_path`, `review_mode`, and `release_state`, but no callable deploy target, payment endpoint, email-send target, or production mutation target.
   - Fail: artifact includes runnable production endpoint, deployment command, direct send command, or auto-execute flag.

Required implementation shape:

```python
assert manifest["release_state"] in {"shadow_only", "candidate", "approved_for_review", "human_released"}
assert not manifest.get("autonomous_execution_allowed", False)
assert manifest.get("execution_targets", []) == []
```

## HB-GATE-002: Freeze Requires Explicit Human Approval

Goal: freeze cannot occur solely because QA says `CLEAN_TO_FREEZE`.

Provider-free tests:

1. `test_freeze_blocked_without_human_approval`
   - Fixture: `action_boundary_allow_packet.json`, `qa_clean_to_freeze.json`, no approval record.
   - Procedure: call the proposed freeze preflight validator, not the current ledger-mutating freeze command.
   - Pass: validator returns `FREEZE_BLOCKED_HUMAN_APPROVAL_REQUIRED`.
   - Fail: freeze preflight returns ready or writes a frozen artifact.

2. `test_freeze_blocked_with_incomplete_approval`
   - Fixture: `human_approval_missing.json`.
   - Required approval fields: `approved_by`, `approved_at`, `approval_scope`, `artifact_hash`, `packet_id`, `provider_scope`, `data_sharing_scope`, `non_execution_disclaimer_acknowledged`.
   - Pass: missing field blocks freeze with a specific reason.
   - Fail: incomplete approval is accepted.

3. `test_freeze_preflight_allows_valid_approval_without_writing_ledger`
   - Fixture: `human_approval_valid.json`.
   - Pass: preflight returns `FREEZE_PREFLIGHT_READY` and writes no ledger or frozen file.
   - Fail: preflight mutates `holo_builder/outputs/ledger.jsonl` or `holo_builder/outputs/frozen/`.

Required implementation shape:

```python
required = {
    "approved_by",
    "approved_at",
    "approval_scope",
    "artifact_hash",
    "packet_id",
    "provider_scope",
    "data_sharing_scope",
    "non_execution_disclaimer_acknowledged",
}
assert required <= approval.keys()
assert approval["non_execution_disclaimer_acknowledged"] is True
```

## HB-GATE-003: No Autonomous Deploy/Release

Goal: product surface cannot deploy, release, publish, send, or start live HoloBuild runs without explicit enablement and approval.

Provider-free tests:

1. `test_holobuild_live_runs_disabled_by_default`
   - Existing evidence: `/v1/holo-build/runs` returns 403 when `HOLOBUILD_LIVE_RUNS` is unset.
   - Procedure: monkeypatch env var absent; call endpoint with fake auth.
   - Pass: 403 with `HoloBuild live runs are disabled.`

2. `test_holobuild_dashboard_mode_read_only_by_default`
   - Procedure: build dashboard payload with env var unset.
   - Pass: `mode == "read_only"` and `live_runs_enabled is False`.

3. `test_no_release_keywords_in_safe_review_payload`
   - Procedure: inspect sanitized dashboard payload and product review packet.
   - Pass: no command/action named `deploy`, `publish`, `send`, `release_payment`, `update_vendor_master`, `merge`, `push`, or `execute`.
   - Fail: any autonomous release command appears in safe review mode.

## HB-GATE-004: Packet Hash And Freeze Hash Correctness

Goal: the freeze hash must cover exactly the model-visible content for the packet format.

Provider-free tests:

1. `test_payment_email_freeze_hash_uses_payload_action_context`
   - Fixture: legacy `payment_email_packet.json`.
   - Procedure: compute canonical hash of `packet.payload.action` and `packet.payload.context`.
   - Pass: computed hash equals freeze preflight hash.

2. `test_action_boundary_freeze_hash_uses_top_level_action_context`
   - Fixture: top-level `action_boundary_allow_packet.json`.
   - Procedure: compute canonical hash of `packet.action` and `packet.context`.
   - Expected current status: `EXPECTED_FAIL_UNTIL_FIXED`.
   - Pass after fix: computed hash is non-empty and changes when top-level `action` or `context` changes.
   - Fail: hash is SHA-256 of empty `{action:{}, context:{}}`, ignores top-level action/context, or changes when builder-only metadata changes.

3. `test_freeze_hash_excludes_builder_metadata`
   - Fixture: same packet with modified `_builder`, `_internal`, `builder_approval`.
   - Pass: freeze hash remains unchanged when only non-model-visible metadata changes.
   - Fail: metadata changes alter model-visible payload hash.

Required canonicalization:

```json
{
  "payment_email": {
    "model_visible": "packet.payload.action + packet.payload.context"
  },
  "action_boundary": {
    "model_visible": "packet.action + packet.context"
  }
}
```

## HB-GATE-005: Top-Level Action-Boundary Packet Format Support

Goal: action-boundary packets using top-level `action` and `context.documents` are first-class citizens across lint, preflight, freeze, and review packets.

Provider-free tests:

1. `test_lint_accepts_valid_action_boundary_packet`
   - Fixture: valid `action_boundary_allow_packet.json`.
   - Procedure: call `holo_builder.lint.check`.
   - Pass: no errors.

2. `test_lint_rejects_action_boundary_metadata_leak`
   - Fixture: packet with `action.expected_verdict`, `context.documents[0].builder_approval`, or `context.documents[0].hypothesized_verdict`.
   - Pass: lint errors identify leaky model-visible field.

3. `test_action_boundary_requires_context_documents`
   - Fixture: packet with fewer than four `context.documents`.
   - Pass: lint fails with document-count error.

4. `test_action_boundary_freeze_preflight_uses_top_level_shape`
   - Fixture: valid action-boundary packet and approval.
   - Expected current status: `EXPECTED_FAIL_UNTIL_FIXED` until freeze preflight is packet-format-aware.
   - Pass after fix: freeze preflight sees top-level `action`/`context`, not `payload`.

## HB-GATE-006: Missing `holo_builder.assert_packet` Gap

Goal: the system cannot claim active assertion-repair coverage when the assertion module is absent.

Provider-free tests:

1. `test_assert_packet_module_available_or_known_gap_declared`
   - Procedure: `importlib.util.find_spec("holo_builder.assert_packet")`.
   - Current expected status: `EXPECTED_FAIL_UNTIL_FIXED` unless an explicit known-gap manifest is present.
   - Pass option A: module exists and exposes `run_assertions`.
   - Pass option B: product readiness manifest declares `assertion_gate_status = "known_gap_disabled"` and blocks live/release readiness.
   - Fail: module missing while readiness claims `assertion_gate_status = "active"`.

2. `test_no_live_readiness_when_assert_packet_missing`
   - Fixture: readiness manifest.
   - Pass: if module is missing, `live_readiness` is `BLOCKED_ASSERT_PACKET_MISSING`.
   - Fail: live readiness is `READY`, `PASS`, or `release_approved`.

Required status states:

```json
[
  "active",
  "known_gap_disabled",
  "blocked_missing_module",
  "replaced_by_equivalent_validator"
]
```

## HB-GATE-007: Human Reliance Disclosure

Goal: every review packet and design-partner display must say what the user can and cannot rely on.

Provider-free tests:

1. `test_review_packet_contains_non_execution_disclosure`
   - Fixture: design partner review packet.
   - Required text fields:
     - `mode_label`
     - `not_autonomous_execution`
     - `human_review_required_before_reliance`
     - `not_legal_financial_security_or_compliance_advice_without_review`
     - `missing_evidence_visible`
   - Pass: all fields are present and true or non-empty.

2. `test_human_reliance_disclosure_blocks_release_when_missing`
   - Fixture: packet missing disclosure.
   - Pass: release gate returns `BLOCKED_RELIANCE_DISCLOSURE_MISSING`.

3. `test_disclosure_matches_mode`
   - Procedure: compare `mode_label` and `release_state`.
   - Pass: `shadow_only` says no reliance; `approved_for_review` says human review still required; `human_released` names the approving human and exact scope.

## HB-GATE-008: Design Partner Safe Review Mode

Goal: design partners can inspect HoloBuild safely without raw provider prompts, secrets, answer keys, draft bodies, or implied release status.

Provider-free tests:

1. `test_holobuild_dashboard_sanitizes_raw_drafts`
   - Existing direction: dashboard safe run omits `draft` and `final_draft`.
   - Pass: serialized dashboard payload contains no raw draft body, no `_internal`, no builder answer key, no provider credential shape.

2. `test_safe_review_mode_includes_trace_summary_not_raw_trace`
   - Fixture: full run trace and safe review projection.
   - Pass: safe projection includes turn numbers, providers, model ids, token counts, elapsed ms, status, high-risk categories, and redacted findings; excludes raw prompt bodies and final candidate body unless explicitly approved for review.

3. `test_safe_review_mode_labels_shadow_state`
   - Pass: packet includes one of `read_only`, `shadow_only`, `candidate`, `approved_for_review`, `human_released`.
   - Fail: label says or implies `production_ready`, `autonomous_ready`, or `released` without human approval.

## HB-GATE-009: Trace And Accounting Requirements

Goal: every HoloBuild packet must have enough trace material to audit the run.

Provider-free tests:

1. `test_run_manifest_has_required_trace_inventory`
   - Required files:
     - `input_manifest.json`
     - `source_manifest.json`
     - `canonical_thread.jsonl`
     - `turn_inputs.jsonl`
     - `turn_outputs.jsonl`
     - `governor_briefs.jsonl`
     - `qa_attack.json`
     - `deterministic_gates.json`
     - `policy_checks.jsonl`
     - `final_candidate_artifact.json`
     - `claim_source_map.json`
     - `missing_evidence.json`
     - `run_manifest.json`
   - Pass: manifest lists every file with path, sha256, required flag, and visibility classification.

2. `test_runtime_accounting_complete`
   - Required fields:
     - `run_id`
     - `branch_commit`
     - `mode`
     - `domain`
     - `adapter`
     - `risk_class`
     - `provider_model_ids_per_turn`
     - `hologov_provider`
     - `worker_pool`
     - `input_tokens`
     - `output_tokens`
     - `elapsed_ms`
     - `retry_count`
     - `fallback_events`
     - `parse_errors`
     - `canonical_thread_hash_before_after_each_turn`
     - `source_budget_used`
     - `material_claim_count`
     - `sourced_claim_count`
     - `missing_evidence_count`
     - `gate_results`
     - `human_approvals`
     - `release_state`
   - Pass: fields are present; numeric counts are integers; fallback and parse errors are explicit lists, even when empty.

3. `test_trace_inventory_hashes_match_files`
   - Procedure: recompute sha256 for every required trace file.
   - Pass: all hashes match.
   - Fail: missing file, hash mismatch, or unclassified visibility.

## HB-GATE-010: Failure Preservation And Regression-Packet Creation

Goal: failures become durable evidence and regression work, not deleted noise.

Provider-free tests:

1. `test_failed_run_preserves_failure_artifacts`
   - Fixture: failed run directory.
   - Required preserved files:
     - `run_manifest.json`
     - `failure_summary.json`
     - `deterministic_gates.json`
     - relevant trace snippets or redacted trace hashes
     - `regression_packet_request.json`
   - Pass: failure is marked `proof_credit = false`, `release_state = blocked`, and all failure reasons are explicit.

2. `test_regression_packet_created_for_gate_failure`
   - Procedure: feed a failed gate result into proposed regression-packet builder.
   - Pass: output includes `regression_id`, `source_failure_id`, `gate_id`, `minimal_repro_fixture`, `expected_failure_reason`, `owner`, and `promotion_blocked_until`.

3. `test_failure_preservation_does_not_freeze_or_judge`
   - Pass: failure preservation does not call providers, does not freeze, does not judge, does not update leaderboard/benchmark credit, and does not write to production release locations.

4. `test_failure_cannot_be_overwritten_by_later_success`
   - Fixture: failed run followed by repaired run.
   - Pass: repaired run links back to failure id; original failure remains intact and visible.

Required regression packet shape:

```json
{
  "regression_id": "HB-REG-<GATE>-<YYYYMMDD>-<NNN>",
  "source_failure_id": "string",
  "gate_id": "HB-GATE-004",
  "minimal_repro_fixture": "path",
  "expected_failure_reason": "string",
  "proof_credit": false,
  "release_state": "blocked",
  "promotion_blocked_until": "test_passes_and_human_review",
  "created_from_failed_run": true
}
```

## Concrete Test Inventory

| Test ID | Test name | Gate | Status |
| --- | --- | --- | --- |
| `HB-ABT-001` | `test_holobuild_packet_terminal_status_does_not_execute_action` | `HB-GATE-001` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-002` | `test_holobuild_artifact_manifest_forbids_execution_targets` | `HB-GATE-001` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-003` | `test_freeze_blocked_without_human_approval` | `HB-GATE-002` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-004` | `test_freeze_blocked_with_incomplete_approval` | `HB-GATE-002` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-005` | `test_freeze_preflight_allows_valid_approval_without_writing_ledger` | `HB-GATE-002` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-006` | `test_holobuild_live_runs_disabled_by_default` | `HB-GATE-003` | `MUST_PASS_NOW` |
| `HB-ABT-007` | `test_holobuild_dashboard_mode_read_only_by_default` | `HB-GATE-003` | `MUST_PASS_NOW` |
| `HB-ABT-008` | `test_no_release_keywords_in_safe_review_payload` | `HB-GATE-003` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-009` | `test_payment_email_freeze_hash_uses_payload_action_context` | `HB-GATE-004` | `MUST_PASS_NOW` |
| `HB-ABT-010` | `test_action_boundary_freeze_hash_uses_top_level_action_context` | `HB-GATE-004` | `EXPECTED_FAIL_UNTIL_FIXED` |
| `HB-ABT-011` | `test_freeze_hash_excludes_builder_metadata` | `HB-GATE-004` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-012` | `test_lint_accepts_valid_action_boundary_packet` | `HB-GATE-005` | `MUST_PASS_NOW` |
| `HB-ABT-013` | `test_lint_rejects_action_boundary_metadata_leak` | `HB-GATE-005` | `MUST_PASS_NOW` |
| `HB-ABT-014` | `test_action_boundary_requires_context_documents` | `HB-GATE-005` | `MUST_PASS_NOW` |
| `HB-ABT-015` | `test_action_boundary_freeze_preflight_uses_top_level_shape` | `HB-GATE-005` | `EXPECTED_FAIL_UNTIL_FIXED` |
| `HB-ABT-016` | `test_assert_packet_module_available_or_known_gap_declared` | `HB-GATE-006` | `EXPECTED_FAIL_UNTIL_FIXED` |
| `HB-ABT-017` | `test_no_live_readiness_when_assert_packet_missing` | `HB-GATE-006` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-018` | `test_review_packet_contains_non_execution_disclosure` | `HB-GATE-007` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-019` | `test_human_reliance_disclosure_blocks_release_when_missing` | `HB-GATE-007` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-020` | `test_disclosure_matches_mode` | `HB-GATE-007` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-021` | `test_holobuild_dashboard_sanitizes_raw_drafts` | `HB-GATE-008` | `MUST_PASS_NOW` |
| `HB-ABT-022` | `test_safe_review_mode_includes_trace_summary_not_raw_trace` | `HB-GATE-008` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-023` | `test_safe_review_mode_labels_shadow_state` | `HB-GATE-008` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-024` | `test_run_manifest_has_required_trace_inventory` | `HB-GATE-009` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-025` | `test_runtime_accounting_complete` | `HB-GATE-009` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-026` | `test_trace_inventory_hashes_match_files` | `HB-GATE-009` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-027` | `test_failed_run_preserves_failure_artifacts` | `HB-GATE-010` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-028` | `test_regression_packet_created_for_gate_failure` | `HB-GATE-010` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-029` | `test_failure_preservation_does_not_freeze_or_judge` | `HB-GATE-010` | `SPEC_ONLY_NEW_GATE` |
| `HB-ABT-030` | `test_failure_cannot_be_overwritten_by_later_success` | `HB-GATE-010` | `SPEC_ONLY_NEW_GATE` |

## Non-Execution Rules For Implementing These Tests

- Use fixture JSON and monkeypatched functions only.
- Do not call `run_builder`, `run_qa_attack`, provider adapters, live web research, judges, deploy commands, or push commands.
- Do not run `holo_builder/builder.py freeze` in tests unless it is redirected to a temporary directory and cannot touch the real ledger.
- Prefer a pure `freeze_preflight` validator before allowing any ledger-mutating freeze path.
- Any test that intentionally models failure must set `proof_credit = false`.
- Any test that creates a regression packet must write it to a test temp directory, not product or benchmark ledgers.

## Promotion Criteria

HoloBuild cannot move beyond shadow until:

1. All `MUST_PASS_NOW` tests pass provider-free.
2. `EXPECTED_FAIL_UNTIL_FIXED` tests either pass after fixes or are explicitly blocked in readiness output.
3. Freeze preflight requires human approval and is packet-format-aware.
4. Missing `assert_packet` is resolved or the assertion gate is truthfully disabled and blocks live readiness.
5. Safe review mode shows trace/accounting and disclosure without raw secrets, answer keys, or implied release authority.
6. Failure preservation produces regression packets and never grants proof credit by itself.

