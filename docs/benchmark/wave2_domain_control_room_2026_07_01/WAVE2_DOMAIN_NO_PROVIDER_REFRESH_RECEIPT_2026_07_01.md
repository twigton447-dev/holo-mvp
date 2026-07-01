# Wave 2 Domain No-Provider Refresh Receipt

Status: `PASS`
Package SHA-256: `29d1fc372e5bc24a608fce23614202d4acafca1853486fb6260cdf4cb5b238b3`
Generated without provider calls: `True`
Provider calls made by refresh: `0`

## Final Artifacts

| Artifact | Status | Package SHA-256 |
| --- | --- | --- |
| Control room | `PASS` | `18fb7a9a23aee8682cb10bcf98d85ca9d780178a76dc4f708ba20c4e2d945116` |
| Completion audit | `PASS` | `b97950895d9161e9c4b82cecafa0bb1ab81098a26a8a7ffb20d4789efeb612f2` |
| Control room validation | `PASS` | `241bedcce162595db3fce2760e84364ac3353eb8253dd2a8caa13dd05eb04a24` |
| Operator handoff | `PASS` | `33a369b9c33265fd8f0189f2884d6ced69db8df3f97bcdec84b9ff17215851e3` |
| Preservation manifest | `PASS` | `fb5b364a87f8479c62ab588a9323eb409d9d3373c7fe72574fcbd464990a4387` |
| Selective staging plan | `PASS` | `c0c1bab57dba1b8914e98cfa5e5bb11671207490a4a7cef0fd4c411c327d041b` |
| Statistical claim guardrail | `PASS` | `f1234a344da2aedd428a022a2a2190ba77172c6e4a7ffdf06f7c7082ec450474` |
| Batch004 approval packet | `NOT_READY` | `a94bb0b83c000e9ce17723526545e240323686fc21da9f9d4f95ec9590f3d5dd` |
| Ordering verifier | `PASS` | `091aaafaf70ca6413614a54497ddb794be58552aae608635794bbe504abcee2b` |
| Readiness | `PASS` | `f58e2474d38183addad8b2e93a6c133f4020d584488631333670cadcf10e292f` |

## Steps

| Step | Status | Seconds |
| --- | --- | ---: |
| `compile_python_refresh_scripts` | `PASS` | `0.16` |
| `combined_evidence_batches_001_004` | `PASS` | `0.162` |
| `compile_metrics_package` | `PASS` | `0.312` |
| `build_metrics_workbook` | `PASS` | `14.95` |
| `build_domain_consolidation_ledger` | `PASS` | `0.15` |
| `verify_domain_ordering` | `PASS` | `0.057` |
| `build_completion_readiness` | `PASS` | `0.07` |
| `build_control_room_pre_lock_test` | `PASS` | `0.096` |
| `test_batch004_provider_approval_gate` | `PASS` | `0.197` |
| `test_batch005_full_family_approval_lock_fail_closed` | `PASS` | `0.248` |
| `rebuild_control_room_after_batch005_lock_test` | `PASS` | `0.083` |
| `build_statistical_claim_guardrail` | `PASS` | `0.064` |
| `build_preservation_manifest` | `PASS` | `0.109` |
| `build_selective_staging_plan` | `PASS` | `0.047` |
| `build_operator_handoff` | `PASS` | `0.048` |
| `test_domain_control_room` | `PASS` | `0.094` |
| `test_preservation_manifest` | `PASS` | `0.096` |
| `test_selective_staging_plan` | `PASS` | `0.037` |
| `test_statistical_claim_guardrail` | `PASS` | `0.067` |
| `test_operator_handoff` | `PASS` | `0.051` |
| `test_timestamp_insensitive_hashes` | `PASS` | `0.196` |
| `validate_no_provider_control_room` | `PASS` | `1.193` |
| `build_completion_audit` | `PASS` | `0.05` |
| `test_completion_audit` | `PASS` | `0.037` |

## Stop Rules

- This refresh never runs Batch 004 live provider calls.
- This refresh never approves provider calls.
- The Batch 005 run-live path is exercised only as a fail-closed approval-lock test and must create zero live run directories.
- The control room is rebuilt after the Batch 005 lock test so final artifacts reflect the latest preflight roots.
- The operator handoff is a no-provider runbook and does not grant live execution approval.
- The selective staging plan only emits path-limited git add commands and does not stage files.
- The statistical guardrail preserves selected-target evidence separately from full-family statistical proof.
