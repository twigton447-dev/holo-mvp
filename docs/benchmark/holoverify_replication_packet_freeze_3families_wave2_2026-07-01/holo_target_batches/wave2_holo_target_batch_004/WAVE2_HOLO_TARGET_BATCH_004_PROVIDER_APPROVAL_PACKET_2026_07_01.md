# Wave 2 Batch 004 Provider Approval Packet

Classification: `WAVE2_BATCH004_PROVIDER_APPROVAL_PACKET_NO_PROVIDER_2026_07_01`
Package SHA-256: `77eaac13e100cdec0db514ac2e0e7cf4b06bb43afe5dae6d20038a3ac5e59af5`
Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`
Generated without provider calls: `True`
Approval granted by this packet: `False`

## Required Approval Statement

`I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01.`

## Scope

| Item | Value |
| --- | ---: |
| Pairs | `10` |
| Packets | `20` |
| Worker calls | `60` |
| Gov calls | `40` |
| Total provider calls | `100` |
| Solo calls | `0` |
| Judge calls | `0` |

## Run Command After Approval

```bash
python3 -B docs/benchmark/run_wave2_holo_target_batch_2026_07_01.py --batch-number 4 --run-live --approval-packet-sha256 77eaac13e100cdec0db514ac2e0e7cf4b06bb43afe5dae6d20038a3ac5e59af5 --approval-statement "I explicitly approve provider calls for WAVE2_HOLO_TARGET_BATCH_004 only, exactly as scoped in WAVE2_HOLO_TARGET_BATCH_004_PROVIDER_APPROVAL_PACKET_2026_07_01."
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
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-005` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-DPRV-REP-005-A, HV-DPRV-REP-005-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-007` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-DPRV-REP-007-A, HV-DPRV-REP-007-B` |
| `HV-DPRV-REP-2026-07-01` | `HV-DPRV-REP-008` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-DPRV-REP-008-A, HV-DPRV-REP-008-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-002` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-FINC-REP-002-A, HV-FINC-REP-002-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-016` | `STRONG_SOLO_COLLAPSE` | `9` | `HV-FINC-REP-016-A, HV-FINC-REP-016-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-017` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-FINC-REP-017-A, HV-FINC-REP-017-B` |
| `HV-FINC-REP-2026-07-01` | `HV-FINC-REP-020` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-FINC-REP-020-A, HV-FINC-REP-020-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-006` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-HRWF-REP-006-A, HV-HRWF-REP-006-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-007` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-HRWF-REP-007-A, HV-HRWF-REP-007-B` |
| `HV-HRWF-REP-2026-07-01` | `HV-HRWF-REP-010` | `STRONG_SOLO_COLLAPSE` | `8` | `HV-HRWF-REP-010-A, HV-HRWF-REP-010-B` |

## Pre-Run Verifiers

| Command | Status | Package SHA-256 |
| --- | --- | --- |
| `python3 -B docs/benchmark/verify_wave2_domain_ordering_2026_07_01.py` | `PASS` | `0a93c2dcdc98f6df2a0ab08d82a66d0389aa56669493b5448f3dd2348b29a435` |
| `python3 -B docs/benchmark/build_wave2_domain_completion_readiness_2026_07_01.py` | `PASS` | `5a50849c7db8c49b74b7d3eeaabf05d4a3d2292843b626bd65e2a0bd724ec017` |

## Checks

| Check | Result |
| --- | --- |
| `batch_id_is_004` | `PASS` |
| `registration_status_preflight_pass` | `PASS` |
| `live_preflight_pass` | `PASS` |
| `live_preflight_requires_approval_statement` | `PASS` |
| `live_preflight_approval_statement_hash_matches` | `PASS` |
| `ordering_verification_pass` | `PASS` |
| `readiness_pass` | `PASS` |
| `readiness_all_checks_passed` | `PASS` |
| `readiness_batch004_true_batch005_false` | `PASS` |
| `expected_provider_calls_100` | `PASS` |
| `expected_solo_calls_0` | `PASS` |
| `expected_judge_calls_0` | `PASS` |
| `no_provider_calls_made` | `PASS` |
| `no_live_started` | `PASS` |
| `no_fallback_policy_declared` | `PASS` |
| `gov_cannot_choose_models` | `PASS` |
| `run_command_batch004_only` | `PASS` |
| `run_command_requires_approval_packet_sha256` | `PASS` |
| `run_command_carries_exact_approval_statement` | `PASS` |

## Stop Rules

- Do not run this command without the exact explicit approval statement.
- Run Batch 004 only; do not run Batch 005 in the same approval window.
- Do not run solo or judge lanes before, during, or after this command unless separately approved.
- Abort if either no-provider verifier fails immediately before live execution.
- Abort if packet, prompt, model-visible payload, or manifest hashes differ from preflight.
- No fallback or model substitution is allowed; provider failure invalidates the run.
- Gov may choose control actions only; Gov may not choose or alter models.
