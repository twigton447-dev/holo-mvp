# Wave 2 Domain Operator Handoff

Status: `PASS`
Package SHA-256: `33a369b9c33265fd8f0189f2884d6ced69db8df3f97bcdec84b9ff17215851e3`
Generated without provider calls: `True`
Current claim: `SELECTED_TARGET_EVIDENCE_ONLY_NOT_FULL_FAMILY_STATISTICAL_PROOF`

## Current State

| Item | Value |
| --- | --- |
| All-domain live proof | `NOT_COMPLETE_PROVIDER_APPROVAL_REQUIRED` |
| Current scored pairs | `37` |
| Current scored packets | `74` |
| Current per-class n | `37` |
| Next allowed live batch | `WAVE2_HOLO_TARGET_BATCH_005` |
| Per-class n after clean Batch004 | `37` |
| Per-class n after clean Batch004+Batch005 | `60` |

## Operator Path

1. `refresh_no_provider_control_surface`

```bash
python3 -B docs/benchmark/run_wave2_domain_no_provider_refresh_2026_07_01.py
```

   Regenerates current non-live evidence, metrics, guardrails, preservation, and validation.

2. `review_and_optionally_stage_by_named_groups`
   Uses path-limited git add commands; no git add . and no git add -A.

3. `batch004_live_complete_and_promoted`

```bash
python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 4 --run-live --approval-packet-sha256 a94bb0b83c000e9ce17723526545e240323686fc21da9f9d4f95ec9590f3d5dd --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

   Approval packet SHA-256: `a94bb0b83c000e9ce17723526545e240323686fc21da9f9d4f95ec9590f3d5dd`
   Required statement: `I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

4. `promote_after_clean_batch004_live`

```bash
python3 -B docs/benchmark/build_wave2_holo_target_batch_comparison_2026_07_01.py --batch-number 4
python3 -B docs/benchmark/build_wave2_holo_target_combined_evidence_2026_07_01.py --batches 1 2 3 4
python3 -B docs/benchmark/compile_holoverify_holobuild_metrics_2026_07_01.py
node docs/benchmark/build_holoverify_holobuild_metrics_workbook_2026_07_01.mjs
python3 -B docs/benchmark/build_holoverify_domain_consolidation_ledger_2026_07_01.py
python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py
python3 -B docs/benchmark/build_wave2_domain_control_room_2026_07_01.py
python3 -B docs/benchmark/build_wave2_statistical_claim_guardrail_2026_07_01.py
```

   Promotes clean Batch004 live evidence into comparison, combined evidence, metrics, ledger, and guardrails.

5. `batch005_requires_separate_future_approval`
   Blocked by: `None`

## Checks

| Check | Result |
| --- | --- |
| `control_room_pass` | `PASS` |
| `readiness_pass` | `PASS` |
| `statistical_guardrail_pass` | `PASS` |
| `preservation_and_staging_orderly_with_unrelated_dirty_reported` | `PASS` |
| `batch004_is_only_next_live_gate` | `PASS` |
| `batch004_approval_packet_current` | `PASS` |
| `batch005_evidence_unlocked_without_approval_packet` | `PASS` |
| `provider_boundary_closed_by_handoff` | `PASS` |

## Stop Rules

- This handoff does not approve provider calls.
- Do not run Batch004 without the exact approval statement and approval packet SHA.
- Do not run Batch005 in the Batch004 approval window.
- Do not count staged Batch004 or Batch005 packets as live statistical proof.
- Do not use git add . or git add -A for this consolidation set.
