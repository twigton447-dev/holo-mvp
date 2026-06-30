# Commerce OpenAI-W2 Batched Full-Holo External Execution Handoff

Date: 2026-06-30

Classification: `COMMERCE_OPENAI_W2_BATCHED_FULL_HOLO_EXTERNAL_EXECUTION_HANDOFF`

Status: `READY_FOR_AUTHORIZED_LOCAL_BATCH_PREFLIGHT_AFTER_MINIMAX_HEALTH_CHECK`

## Purpose

Run the Commerce OpenAI-W2 Holo family as three fixed lock-rooted batches outside Codex. Codex must not export frozen private benchmark packet/prompt content to providers. This handoff is for Taylor's authorized local shell/environment.

This is a batched full-family protocol. It is not a one-shot uninterrupted `200`-call run.

## Scope

- Commerce family only.
- Same frozen `40` packets.
- Same `20` sibling pairs.
- Same packet freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`.
- Same OpenAI-W2 Holo roster.
- No solo.
- No judges.
- No AP.
- No IT.
- No packet edits.
- No prompt edits.
- No fallback or substitution.
- MiniMax health gate required before each live batch.

## Required Environment Variables

- `XAI_API_KEY`
- `OPENAI_API_KEY`
- `MINIMAX_API_KEY`

Optional MiniMax endpoint overrides, only if needed locally:

- `MINIMAX_CHAT_COMPLETIONS_URL`
- `MINIMAX_BASE_URL`

Do not paste provider keys into chat.

## Preflight All Batches

This command is local-only and should make zero provider calls:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
PYTHONPYCACHEPREFIX=/private/tmp/holo_pycache python3 -B -m py_compile docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py
python3 -B docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py --preflight-all-batches
```

Preflight must pass for all three batches before live execution.

## MiniMax Health Gate

Before each live batch attempt, run one harmless non-benchmark MiniMax health check. This check must not include packet text, prompt text, source IDs, traps, answer keys, or any benchmark content.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py --minimax-health-check
```

Pass condition:

- response is exactly `MINIMAX_READY`
- transport attempts = `1`
- transport recovered = `False`
- no DNS, timeout, HTTP 5xx, or retry recovery

If the health check fails or requires transport recovery, stop. Do not run a Commerce batch.

After a clean health check, run the health-gated preflight for the target batch:

```bash
python3 -B docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py --preflight-batch --batch batch_1 --require-minimax-health
```

## Live Batch Commands

Run one batch at a time. If a batch fails, stop and preserve the run folder. Do not automatically continue to the next batch.

Batch 1:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py --run-batch --batch batch_1 --require-minimax-health
```

Batch 2:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py --run-batch --batch batch_2 --require-minimax-health
```

Batch 3:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py --run-batch --batch batch_3 --require-minimax-health
```

## Roll-Up Command

Run only after all three batches complete:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
python3 -B docs/benchmark/run_commerce_openai_w2_holo_batched_family_2026_06_30.py --rollup-latest
```

The roll-up passes only if the latest run for each batch is ready and the combined evidence proves:

- `20/20` pairs
- `40/40` packets
- `200/200` provider calls across batches
- `120` worker calls
- `80` Gov calls
- `0` solo calls
- `0` judge calls
- no leakage in all batches
- same freeze root in all batches
- no pair overlap
- complete pair coverage from `HV-ACOM-REP-001` through `HV-ACOM-REP-020`

## Expected Output Roots

Batch runs:

```text
docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_1/run_<timestamp>/
docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_2/run_<timestamp>/
docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2_batched/batch_3/run_<timestamp>/
```

Rollups:

```text
docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/batched_full_holo_rollups/rollup_<timestamp>/
```

## Pass/Fail Rules

Each batch passes only if:

- its expected pair range completes
- expected provider calls complete
- no unrecovered provider failures
- worker compact parses every worker turn
- Gov micro-baton parses every Gov turn
- deterministic gates run after every worker
- Gov receives gate results
- final selector is present
- all packet final verdicts are correct and admissible
- no leakage
- no solo or judges
- a recent clean MiniMax health check existed before launch

The Commerce family proof passes only if all three batches pass and the roll-up passes.

## Claim Boundary

Allowed after roll-up PASS:

`Commerce completed as a lock-rooted three-batch Holo family run over the same frozen 40 packets.`

Forbidden:

`Commerce completed as one uninterrupted 200-call run.`
