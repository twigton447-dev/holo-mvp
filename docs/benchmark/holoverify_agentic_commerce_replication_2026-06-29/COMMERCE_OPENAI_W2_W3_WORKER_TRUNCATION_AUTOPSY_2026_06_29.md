# Commerce OpenAI-W2 W3 Worker Truncation Autopsy

Date: 2026-06-29

## Classification

`COMMERCE_OPENAI_W2_W3_WORKER_CONTRACT_TRUNCATION_FAILURE`

This was not a Holo verdict failure, not a deterministic gate verdict failure, and not a transport failure. The preserved Commerce run failed closed because the final MiniMax worker produced no parseable visible worker contract after exhausting the configured worker output budget.

## Preserved Invalid Run

- Run folder: `docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2/run_20260629T235436Z`
- Completed calls before stop: `45/200`
- Root failing turn: `HV-ACOM-REP-005-A_W3`
- Packet: `HV-ACOM-REP-005-A`
- Pair: `HV-ACOM-REP-005`
- Worker slot: `W3`
- Worker role: `FINAL_COMPILER`
- Provider/model: `minimax/MiniMax-M2.5-highspeed`
- Provider call OK: `true`
- Finish reason: `length`
- Parser status: `parse_ok=false`
- Error: `ValueError: worker_finish_reason_length_empty_text`
- Tokens: `2795` input / `3600` output / `6395` total
- Transport recovered: `false`

## Root Cause

The W3 final compiler call reached the generic worker output ceiling of `3600` tokens and ended with `finish_reason=length`. The visible `text` field in the trace was empty, so the worker parser correctly failed closed with `worker_finish_reason_length_empty_text`.

The preserved invalid run does not contain `raw_text` for this response. At the time of the failed run, the provider adapter stored only text after the thinking-block filter. Therefore the exact raw provider payload cannot be reconstructed from the preserved trace. The most precise supported conclusion is: MiniMax W3 consumed the full output budget and produced no parseable visible compact worker contract.

## Patch

The runner is hardened without changing packets, prompt truths, verdict rules, or parser admissibility:

- Preserve `raw_text` separately from filtered `text` for OpenAI-compatible providers.
- Preserve `raw_text` separately from filtered `text` for Gemini.
- Preserve `raw_text` separately from filtered `text` for the OpenAI Responses W2 shim.
- Add `text_stripped_by_thinking_filter` to future traces when filtering changes visible output.
- Increase MiniMax `FINAL_COMPILER` worker max tokens from the generic `3600` worker budget to `6000`.
- Keep non-final workers on the generic `3600` budget.
- Add explicit worker prompt constraints: no hidden reasoning, no analysis, no `<think>` blocks, and the first output characters must be `worker_role=`.
- Record the MiniMax final-compiler token budget in future architecture locks.

## Non-Changes

- The parser was not loosened.
- Empty visible worker output remains invalid.
- `finish_reason=length` with empty or incomplete worker output remains invalid.
- No malformed content is repaired into a valid answer.
- No content retry was added for length or parse failures.
- No packet, prompt, truth label, model roster, or evidence file was changed.
- No providers or judges were called by this patch.

## Next Valid Move

After local tests pass and this patch is committed, Commerce should use a small fresh canary before another full 200-call family run. The preserved invalid run remains an invalid provider-content/contract trace and must not be overwritten.
