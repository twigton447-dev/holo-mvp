# Blind Canary Gov Copy Contract Patch

Status: `READY_FOR_PACKET_INDEX_3_RERUN`

## Reason

Packet index 3 failed closed in `run_20260703T000924Z` because MiniMax Gov slot `G2` emitted hidden thinking, reached `finish_reason=length`, and produced no parseable compact Gov baton after filtering.

This was a content/contract failure, not a verdict failure and not a transport failure.

## Patch

- Replaced the broad blind Gov prompt with a compact copy contract.
- Gov now receives truth-free selected baton lines derived only from blind structural gate status.
- Gov is instructed to copy exactly three lines:
  - `route_verdict`
  - `repair_target`
  - `blocked_move`
- Gov prompt no longer contains the literal verdict words `ALLOW` or `ESCALATE`.
- Gov calls now use `GOV_MAX_OUTPUT_TOKENS=512`.
- Unclosed `<think>` / `<thinking>` blocks strip to empty text and fail closed.
- Slot validation now requires Gov prompts to contain `SELECTED_GOV_BATON_LINES`.

## Validation

Local only. No providers, solo, or judges were run.

- `py_compile`: PASS with `PYTHONPYCACHEPREFIX=/tmp/codex_pycache`
- Blind canary wrapper + Fable blind-lane tests: `34 passed, 12 skipped`
- Packet-index-3 preflight: PASS
- Generated packet-index-3 G2 prompt contains:
  - `SELECTED_GOV_BATON_LINES`
  - `route_verdict=CONTINUE`
  - `repair_target=preserve source-grounded reasoning`
  - `blocked_move=do not invent source IDs`
- Generated packet-index-3 G2 prompt does not contain:
  - `ALLOW`
  - `ESCALATE`
  - `packet_truth`

## Claim Boundary

This patch prepares the blind runtime-firewall lane for another one-packet canary attempt. It does not create a score-valid benchmark result and does not support any public FP/FN or error-rate claim.
