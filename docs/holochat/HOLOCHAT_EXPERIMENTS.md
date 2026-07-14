# HoloChat Model Experiments

The experiment harness is dry-run-only unless both `--live` and `--confirm-live` are present. Dry runs never import provider SDKs, inspect credentials, or make network calls.

## Three Runners

From the repository root:

```bash
scripts/holochat_runner_economy.sh
scripts/holochat_runner_balanced.sh
scripts/holochat_runner_frontier.sh
```

Each command prints an eight-turn Condition D manifest with the exact Gov and worker sequence plus estimated cost. Add `--output /tmp/name.json` to save it.

The executable model lanes are:

- Economy: OpenAI `gpt-5.4-mini`, xAI `grok-4.3`, HoloGov `MiniMax-M2.7-highspeed`.
- Balanced: OpenAI `gpt-5.4`, xAI `grok-4.3`, HoloGov `MiniMax-M2.7-highspeed`.
- Frontier: OpenAI `gpt-5.5`, xAI `grok-4.3`, HoloGov `MiniMax-M2.7-highspeed`.

These are evaluation lanes. They do not alter canonical production routing.

Deferred ceiling test: evaluate a future Fable 5 worker against OpenAI GPT-5.6 at ultra intelligence to measure the maximum attainable worker quality. This is deliberately not part of launch routing or routine Mira QA; it requires its own explicit live budget and provider/model compatibility review.

Paid pressure runs must set `--max-estimated-cost-usd`. Before the first paid call, the live harness reserves a conservative `$0.35`; after that it projects the next cumulative total from observed worker and HoloGov turn costs, adds a 25 percent growth buffer, and stops before starting a turn when the configured ceiling would be crossed. It also stops when a completed turn has no complete cost estimate, because the cap can no longer be enforced. This is a fail-closed test estimate, not a provider billing limit; search, embedding, cache, and provider-specific charges may differ or remain outside the estimate. A capped run that stops before all requested turns is incomplete evidence and exits nonzero.

## A/B/C/D Conditions

- A: worker baseline with pre-worker HoloGov control disabled.
- B: legacy clipped history with the current control plane.
- C: current HoloGov control packet and bounded ordered history.
- D: current selective context, control packet, episodes, and reseed behavior.

Override the default condition or turn count with:

```bash
.venv312/bin/python scripts/holochat_experiment_runner.py \
  --lane frontier --condition C --rotations 8
```

## Live Gate

A live run requires provider credentials already present in the shell and both confirmation flags:

```bash
scripts/holochat_runner_frontier.sh --live --confirm-live --max-estimated-cost-usd 0.75
```

The runner forwards only the explicitly supported credential names to the child process and never prints their values. Live output must be captured and scored before comparing lanes; a dry-run cost is a planning estimate, not provider billing.

For the launch gate, run one adaptive recursive-context lap after live use is explicitly authorized. This deliberately lowers the history ceiling so the eight-turn test must exercise rolling-summary and resurfacing behavior instead of returning a vacuous short-thread pass:

```bash
RUN_ID="mira-launch-$(date +%Y%m%d-%H%M%S)"
PYTHONDONTWRITEBYTECODE=1 .venv312/bin/python scripts/holochat_live_smoke.py \
  --adaptive-script mira_recursive_context \
  --turns 8 \
  --history-message-limit 6 \
  --history-char-limit 12000 \
  --with-supabase \
  --ensure-test-capsule \
  --capsule-id "hc-${RUN_ID}" \
  --capsule-email "${RUN_ID}@holo.test" \
  --capsule-name "Mira Launch Gate" \
  --synthetic-persona mira \
  --seed-synthetic-persona \
  --fail-fast-health \
  --max-estimated-cost-usd 0.75 \
  --live-dashboard \
  --trace-jsonl "/tmp/${RUN_ID}.jsonl" \
  --transcript-md "/tmp/${RUN_ID}.md" \
  --govtrace-md "/tmp/${RUN_ID}-gov.md"
```

Do not repeat the lap to improve the score. Diagnose the first failure or unexercised dimension, patch locally, and use no-provider fixtures until the next paid run is justified.

## Comparison Record

Every completed comparison should retain:

- lane and condition
- exact worker and Gov models per turn
- Gov, worker, retry, failover, embedding, and search call costs
- provider-reported input, output, cached, and reasoning tokens where available
- worker context receipt and selected episode/source IDs
- latency, visible repair, citation status, and search outcome
- continuity, insight, empathy, challenge, factuality, hallucination, and drift scores
