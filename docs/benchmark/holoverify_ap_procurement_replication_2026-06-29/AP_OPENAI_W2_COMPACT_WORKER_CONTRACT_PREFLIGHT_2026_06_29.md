# AP OpenAI-W2 Compact Worker Contract Preflight

Status: `PASS`
Current HEAD: `afdda17cf00647ae672c8bd8d6cdb300e5d7f322`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Conclusion

The AP OpenAI-W2 lane imports the shared Holo runner and reuses the compact worker contract after `configure_openai_w2_runner()` binds W2 to `openai/gpt-5.4-mini`.

## Runtime W2 Prompt Probe

- Pair: `HV-AP-REP-001`
- Packet: `HV-AP-REP-001-A`
- W2 model: `openai/gpt-5.4-mini`
- Answer contract format: `compact_key_value_v1`
- Worker contract forbids JSON/braces/quotes/markdown in the worker output.

## Assertions

| Assertion | Value |
| --- | --- |
| `head_is_worker_contract_commit` | `True` |
| `ap_imports_shared_runner` | `True` |
| `ap_openai_w2_configure_mutates_shared_worker_sequence` | `True` |
| `ap_w2_prompt_contract_is_compact_key_value` | `True` |
| `ap_w2_system_requires_compact_key_value` | `True` |
| `ap_w2_worker_output_forbids_json_braces_quotes_markdown` | `True` |
| `valid_compact_w2_output_parses` | `True` |
| `valid_compact_w2_output_gates` | `True` |
| `malformed_json_fails_closed` | `True` |
| `missing_verdict_fails_closed` | `True` |
| `invented_source_ids_fail_closed` | `True` |
| `ap_packet_hashes_match_freeze` | `True` |
| `ap_prompt_hashes_match_freeze` | `True` |
| `w2_remains_openai_gpt54_mini` | `True` |
| `transport_policy_v1_unchanged` | `True` |
| `no_providers_called` | `True` |
| `no_judges_called` | `True` |
| `invalid_run_preserved` | `True` |

## Invalid Run Preservation

- Preserved run: `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T134644Z`
- Git status: `?? docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T134644Z/`
- Raw invalid run folder remains untracked to preserve the exact emitted trace, prompts, outputs, and lock as local raw evidence. This committed preflight records that status instead of partially staging raw artifacts.
