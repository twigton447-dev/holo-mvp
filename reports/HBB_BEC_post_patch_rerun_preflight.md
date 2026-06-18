# HBB-BEC Post-Patch 4DNA Rerun Preflight

Date: `2026-06-18`
Scope: `HBB-BEC-001` and `HBB-BEC-002-HARD`
Status: `completed_runner_available_pending_explicit_live_approval`

This update adds the committed gated post-patch runner only. It did not run provider calls, create traces, run Judge, run QA or ablation, freeze anything, edit packet drafts, edit frozen artifacts, change proof-credit counts, or push.

## Gate

| Check | Result |
|---|---|
| Repo | `/Users/taylorwigton/CascadeProjects/holo-mvp` |
| Branch | `holo-builder-freeze-manifest-gate-001` |
| Start status | Clean |
| Mandate | `docs/HOLO_ACTIVE_MANDATE.md` re-read |

## Summary

The frozen artifact side remains ready: all four frozen HBB packets exist, their computed payload hashes match `_frozen.hash`, and the preflight-approved ledger/hash records match. Original trace directories, Judge reports, autopsies, and regression tests exist.

The previous blocker is now closed at the runner level: `benchmark_factory/batches/run_HBB_BEC_post_patch_4dna_rerun.py` provides a fail-closed no-live default and an explicit Taylor-approved provider-execution path. Live execution was not run in this task.

## Runner Contract

- Runner path: `benchmark_factory/batches/run_HBB_BEC_post_patch_4dna_rerun.py`
- Default behavior: no-live prompt-card and rerun-plan generation only.
- Live execution requires `--execute-provider-calls`, `--operator Taylor`, `--yes-send-frozen-payloads-to-providers`, and `HBB_BEC_POST_PATCH_RERUN_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION`.
- Taylor-local execution also requires `--i-am-taylor-local`.
- Codex/Co execution also requires `--allow-codex-provider-calls` and `HBB_BEC_CODEX_POST_PATCH_RERUN_APPROVED=I_APPROVE_CODEX_PROVIDER_TRANSMISSION`.
- Output directory: `scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun`
- Expected row/call count: 16 = 4 frozen packets x 4 active 4DNA calls.
- Output records are marked `post_patch_rerun=true`, `original_trace=false`, `official_trace=false`, `judge=false`, `freeze=false`, and `benchmark_credit=false`.
- The runner refuses to overwrite an existing live output directory.

No-live command:

```bash
python3 -B benchmark_factory/batches/run_HBB_BEC_post_patch_4dna_rerun.py --out-dir scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun
```

Taylor-approved live command:

```bash
HBB_BEC_POST_PATCH_RERUN_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION python3 -B benchmark_factory/batches/run_HBB_BEC_post_patch_4dna_rerun.py --execute-provider-calls --operator Taylor --i-am-taylor-local --yes-send-frozen-payloads-to-providers --timeout 90 --out-dir scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun
```

Codex/Co-approved live command, if explicitly approved later:

```bash
HBB_BEC_POST_PATCH_RERUN_APPROVED=I_APPROVE_PROVIDER_TRANSMISSION HBB_BEC_CODEX_POST_PATCH_RERUN_APPROVED=I_APPROVE_CODEX_PROVIDER_TRANSMISSION python3 -B benchmark_factory/batches/run_HBB_BEC_post_patch_4dna_rerun.py --execute-provider-calls --operator Taylor --allow-codex-provider-calls --yes-send-frozen-payloads-to-providers --timeout 90 --out-dir scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun
```

## Family Preflight

| family_id | frozen_packet_ids | hash_verification_status | original_trace_pointer | judge_pointer | autopsy_pointer | rerun_needed | rerun_blocked | proof_credit_possible_if_clean |
|---|---|---|---|---|---|---|---|---|
| `HBB-BEC-001` | `HBB-BEC-001`; `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL` | PASS: computed payload hashes match _frozen.hash and holo_builder/outputs/ledger.jsonl rows for both siblings. | `traces/HBB-BEC-001_pair_4dna_seed447/` | `reports/HBB_BEC_001_pair_4dna_seed447_judge_summary.json` | `reports/HBB_BEC_001_seed447_hologov_loss_autopsy.json` | yes | no | yes |
| `HBB-BEC-002-HARD` | `HBB-BEC-002-HARD-ALLOW`; `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL` | PASS: computed payload hashes match _frozen.hash and holo_builder/outputs/ledger.jsonl rows for both siblings. | `traces/HBB-BEC-002_hard_pair_4dna_seed447/` | `reports/HBB_BEC_002_hard_pair_4dna_seed447_judge_summary.json` | `reports/HBB_BEC_002_seed447_hologov_loss_autopsy.json` | yes | no | yes |

## Frozen Artifacts

| Packet | Frozen path | Payload hash |
|---|---|---|
| `HBB-BEC-001` | `holo_builder/outputs/frozen/HBB-BEC-001_8181d83c.json` | `8181d83ceb7f36f97160f078a4d4d35bdced5555fba5478c55bd3d954f40c4f1` |
| `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL` | `holo_builder/outputs/frozen/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc.json` | `807468fcba476a97ef92cf4058af0767c73a66a450bda37c60c6bfaa8be5e883` |
| `HBB-BEC-002-HARD-ALLOW` | `holo_builder/outputs/frozen/HBB-BEC-002-HARD-ALLOW_f7986fa2.json` | `f7986fa2d852183033f1596780f9a763da803f61490af0b18d439d73ba5810d5` |
| `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL` | `holo_builder/outputs/frozen/HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL_0151f5e6.json` | `0151f5e643eb27d56d879b6b12b66ae9bcbebd962e2ce7a014c51e17ee68b4cf` |

## Provider Roster

Seed `447` preserves the original HBB 4DNA mini roster shape:

- `HBB-BEC-001_pair_4dna_seed447_post_patch`: HoloGov `openai:gpt-4o-mini`; active non-Gov `xai:grok-3-mini, google:gemini-2.5-flash-lite, minimax:MiniMax-Text-01`; excluded `anthropic:claude-haiku-4-5-20251001`.
- `HBB-BEC-002_hard_pair_4dna_seed447_post_patch`: HoloGov `openai:gpt-4o-mini`; active non-Gov `xai:grok-3-mini, google:gemini-2.5-flash-lite, minimax:MiniMax-Text-01`; excluded `anthropic:claude-haiku-4-5-20251001`.

## Expected Outputs

- `scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/rerun_plan.json`
- `scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/prompt_cards/`
- `scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/results.jsonl`
- `scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/summary.json`
- `scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun/post_patch_rerun_records/`

These are post-patch rerun outputs, not original trace directories. The runner does not update scorecard or proof-credit automatically.

## Stop Conditions

- Any selected packet path or payload hash differs from the preflight-approved HBB records.
- Any family outside HBB-BEC-001 or HBB-BEC-002-HARD is selected.
- Any frozen packet fails the build_freeze_manifest hash and payload-visibility contract.
- Seed447 roster differs from OpenAI HoloGov plus xAI/Gemini/MiniMax active non-Gov and Anthropic excluded.
- Provider execution requested without explicit HBB post-patch approval gates.
- Output directory already exists for live execution.
- Expected row count differs from 4 frozen packets x 4 active 4DNA calls = 16.

## Patch And Regression

Patch pointer:

- `llm_adapters.py`
- `reports/HBB_BEC_001_seed447_hologov_loss_autopsy.json`
- `reports/HBB_BEC_002_seed447_hologov_loss_autopsy.json`

Regression test pointers:

- `test_hbb_bec_post_patch_rerun_runner.py`
- `test_hbb_bec_hologov_trigger_completion_regression.py`
- `test_holo_builder_frozen_4dna_runner.py`
- `test_holo_builder_freeze_ledger_accounting.py`
- `test_balanced_100_packet_factory_manifest.py`

Regression result:

```bash
python3 -m pytest test_hbb_bec_post_patch_rerun_runner.py test_hbb_bec_hologov_trigger_completion_regression.py test_holo_builder_frozen_4dna_runner.py test_holo_builder_freeze_ledger_accounting.py test_balanced_100_packet_factory_manifest.py
```

Result: `PASS: 35 passed.`

## Validation

- `py_compile`: PASS
- Runner no-live smoke: PASS
- Attempted live execution without approval: failed closed
- Relevant regression tests: PASS
- Live calls: not run
- Judge, QA/ablation, freeze: not run
- Packet drafts/frozen artifacts: not edited
- Proof-credit: unchanged

## Proof Credit

Proof-credit remains unchanged:

- Current proof-credit-ready families: `BEC-PAIR-009`, `BEC-PAIR-010`
- Current proof-credit count: 2 pair families / 4 packets
- HBB-BEC-001 and HBB-BEC-002-HARD remain non-credit until clean post-patch 4DNA rerun and Judge evidence exists.
- If both post-patch reruns and Judge review are clean in a future approved lane, proof-credit could expand to 4 pair families / 8 packets.
