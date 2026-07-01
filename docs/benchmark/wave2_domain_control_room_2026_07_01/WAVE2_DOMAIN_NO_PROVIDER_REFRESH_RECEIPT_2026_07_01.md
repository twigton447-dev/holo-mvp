# Wave 2 Domain No-Provider Refresh Receipt

Status: `PASS`
Package SHA-256: `074419a739d72a1161e2a8fa467d3f59c0caab3f26558cde0c2bb087155d27ee`
Generated without provider calls: `True`
Provider calls made by refresh: `0`

## Final Artifacts

| Artifact | Status | Package SHA-256 |
| --- | --- | --- |
| Control room | `PASS` | `06110e4c86904686a3ac730620e88d838a0c6221e461fdcca152700a2d7960db` |
| Completion audit | `PASS` | `8cdfad7f01405a49957c414ab47dd12226e65995f969f5a4c80e5e615a41120b` |
| Control room validation | `PASS` | `3a024d3e8d556a735ac363c49cf0d70d7c1669278df5456bb67a1a541b61291d` |
| Operator handoff | `PASS` | `b5eeaae7b9cc762195008cd8ddf115c89135f25a1375bf86c0a2646f27d289ad` |
| Preservation manifest | `PASS` | `9d7242752c609e97c899035b6f6f3881dbb8e24748e2d2ed2f414529a8a45c1c` |
| Selective staging plan | `PASS` | `73d7d01d4828f06fdc70447b8848e3f49aed7600c3aacf8185e5fa6ed696f988` |
| Statistical claim guardrail | `PASS` | `086f77cfae5273fc4835bb1be0137db558be55cc242cc2775ed1984cc2f9286c` |
| Batch004 approval packet | `READY_FOR_EXPLICIT_PROVIDER_APPROVAL` | `77eaac13e100cdec0db514ac2e0e7cf4b06bb43afe5dae6d20038a3ac5e59af5` |
| Ordering verifier | `PASS` | `0a93c2dcdc98f6df2a0ab08d82a66d0389aa56669493b5448f3dd2348b29a435` |
| Readiness | `PASS` | `5a50849c7db8c49b74b7d3eeaabf05d4a3d2292843b626bd65e2a0bd724ec017` |

## Steps

| Step | Status | Seconds |
| --- | --- | ---: |
| `compile_python_refresh_scripts` | `PASS` | `0.07` |
| `combined_evidence_batches_001_003` | `PASS` | `0.081` |
| `compile_metrics_package` | `PASS` | `0.216` |
| `build_metrics_workbook` | `PASS` | `15.161` |
| `build_domain_consolidation_ledger` | `PASS` | `0.125` |
| `verify_domain_ordering` | `PASS` | `0.05` |
| `build_completion_readiness` | `PASS` | `0.064` |
| `build_batch004_provider_approval_packet` | `PASS` | `0.047` |
| `build_control_room_pre_lock_test` | `PASS` | `0.082` |
| `test_batch004_provider_approval_gate` | `PASS` | `0.178` |
| `test_batch005_full_family_lock_fail_closed` | `PASS` | `0.235` |
| `rebuild_control_room_after_batch005_lock_test` | `PASS` | `0.08` |
| `build_statistical_claim_guardrail` | `PASS` | `0.06` |
| `build_preservation_manifest` | `PASS` | `0.148` |
| `build_selective_staging_plan` | `PASS` | `0.046` |
| `build_operator_handoff` | `PASS` | `0.048` |
| `test_domain_control_room` | `PASS` | `0.101` |
| `test_preservation_manifest` | `PASS` | `0.112` |
| `test_selective_staging_plan` | `PASS` | `0.034` |
| `test_statistical_claim_guardrail` | `PASS` | `0.064` |
| `test_operator_handoff` | `PASS` | `0.047` |
| `test_timestamp_insensitive_hashes` | `PASS` | `0.185` |
| `validate_no_provider_control_room` | `PASS` | `1.043` |
| `build_completion_audit` | `PASS` | `0.045` |
| `test_completion_audit` | `PASS` | `0.033` |

## Stop Rules

- This refresh never runs Batch 004 live provider calls.
- This refresh never approves provider calls.
- The Batch 005 run-live path is exercised only as a fail-closed lock test and must create zero live run directories.
- The control room is rebuilt after the Batch 005 lock test so final artifacts reflect the latest preflight roots.
- The operator handoff is a no-provider runbook and does not grant live execution approval.
- The selective staging plan only emits path-limited git add commands and does not stage files.
- The statistical guardrail preserves selected-target evidence separately from full-family statistical proof.
