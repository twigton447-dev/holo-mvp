# Wave 2 Batch 005 Provider Approval Packet

Classification: `WAVE2_BATCH005_PROVIDER_APPROVAL_PACKET_NO_PROVIDER_2026_07_01`
Package SHA-256: `350982865614742252da0f191895884d5521c98d74fff079b62c1a339688f3a0`
Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Generated without provider calls: `True`
Approval granted by this packet: `False`

## Required Approval Statement

`I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_005 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Scope

| Item | Value |
| --- | ---: |
| Selection mode | `full-family-remainder` |
| Pairs | `23` |
| Packets | `46` |
| Worker calls | `138` |
| Gov calls | `92` |
| Total provider calls | `230` |
| Solo calls | `0` |
| Judge calls | `0` |

## Run Command After Approval

```bash
python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 5 --run-live --approval-packet-sha256 350982865614742252da0f191895884d5521c98d74fff079b62c1a339688f3a0 --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_005 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_005_PROVIDER_APPROVAL_PACKET_2026_07_01."
```

## Model Roster

| Slot | Provider | Model | Role |
| --- | --- | --- | --- |
| `W1` | `xai` | `grok-3-mini` | `SOURCE_BOUNDARY_MAPPER` |
| `W2` | `openai` | `gpt-5.4-mini` | `ADVERSARIAL_SCOPE_CHALLENGER` |
| `W3` | `minimax` | `MiniMax-M2.5-highspeed` | `FINAL_COMPILER` |
| `G1` | `minimax` | `MiniMax-M2.5-highspeed` | Gov |
| `G2` | `minimax` | `MiniMax-M2.5-highspeed` | Gov |

## Selected Pairs

| Family | Pair | Class | Priority | Packets |
| --- | --- | --- | ---: | --- |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-002` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-002-A, HV-DPRV-REP-002-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-003` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-003-A, HV-DPRV-REP-003-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-004` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-004-A, HV-DPRV-REP-004-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-006` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-006-A, HV-DPRV-REP-006-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-010` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-010-A, HV-DPRV-REP-010-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-011` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-011-A, HV-DPRV-REP-011-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-016` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-016-A, HV-DPRV-REP-016-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-017` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-DPRV-REP-017-A, HV-DPRV-REP-017-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-005` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-FINC-REP-005-A, HV-FINC-REP-005-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-008` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-FINC-REP-008-A, HV-FINC-REP-008-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-014` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-FINC-REP-014-A, HV-FINC-REP-014-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-018` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-FINC-REP-018-A, HV-FINC-REP-018-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-002` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-002-A, HV-HRWF-REP-002-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-003` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-003-A, HV-HRWF-REP-003-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-004` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-004-A, HV-HRWF-REP-004-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-005` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-005-A, HV-HRWF-REP-005-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-008` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-008-A, HV-HRWF-REP-008-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-009` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-009-A, HV-HRWF-REP-009-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-011` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-011-A, HV-HRWF-REP-011-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-013` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-013-A, HV-HRWF-REP-013-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-014` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-014-A, HV-HRWF-REP-014-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-015` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-015-A, HV-HRWF-REP-015-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-016` | `NON_TARGET_FULL_FAMILY_COMPLETION` | `None` | `HV-HRWF-REP-016-A, HV-HRWF-REP-016-B` |

## Pre-Run Verifiers

| Command | Status | Package SHA-256 |
| --- | --- | --- |
| `python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py` | `PASS` | `091aaafaf70ca6413614a54497ddb794be58552aae608635794bbe504abcee2b` |
| `python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py` | `PASS` | `f58e2474d38183addad8b2e93a6c133f4020d584488631333670cadcf10e292f` |

## Checks

| Check | Result |
| --- | --- |
| `batch_id_is_005` | `PASS` |
| `selection_mode_full_family_remainder` | `PASS` |
| `registration_status_preflight_pass` | `PASS` |
| `live_preflight_pass` | `PASS` |
| `live_execution_gate_pass` | `PASS` |
| `live_preflight_requires_approval_statement` | `PASS` |
| `live_preflight_approval_statement_hash_matches` | `PASS` |
| `ordering_verification_pass` | `PASS` |
| `readiness_pass` | `PASS` |
| `readiness_all_checks_passed` | `PASS` |
| `readiness_batch005_true` | `PASS` |
| `combined_memo_has_37_valid_pairs` | `PASS` |
| `combined_memo_has_74_correct_packets` | `PASS` |
| `batch004_comparison_has_10_valid_pairs` | `PASS` |
| `expected_provider_calls_230` | `PASS` |
| `expected_solo_calls_0` | `PASS` |
| `expected_judge_calls_0` | `PASS` |
| `no_provider_calls_made` | `PASS` |
| `no_live_started` | `PASS` |
| `no_fallback_policy_declared` | `PASS` |
| `gov_cannot_choose_models` | `PASS` |
| `run_command_batch005_only` | `PASS` |
| `run_command_requires_approval_packet_sha256` | `PASS` |
| `run_command_carries_exact_approval_statement` | `PASS` |

## Stop Rules

- Do not run this command without the exact explicit approval statement.
- Run Batch 005 only; do not rerun Batch 001-004 in the same approval window.
- Do not run solo or judge lanes before, during, or after this command unless separately approved.
- Abort if either no-provider verifier fails immediately before live execution.
- Abort if packet, prompt, model-visible payload, or manifest hashes differ from preflight.
- No fallback or model substitution is allowed; provider failure invalidates the run.
- Gov may choose control actions only; Gov may not choose or alter models.
