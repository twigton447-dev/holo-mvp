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

- Economy: OpenAI `gpt-5.4-mini`, xAI `grok-4.3`, Gov `gpt-5.4-mini`.
- Balanced: OpenAI `gpt-5.4`, xAI `grok-4.3`, Gov `gpt-5.4`.
- Frontier: OpenAI `gpt-5.5`, xAI `grok-4.5`, Gov `gpt-5.5`.

These are evaluation lanes. They do not alter canonical production routing.

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
scripts/holochat_runner_frontier.sh --live --confirm-live
```

The runner forwards only the explicitly supported credential names to the child process and never prints their values. Live output must be captured and scored before comparing lanes; a dry-run cost is a planning estimate, not provider billing.

## Comparison Record

Every completed comparison should retain:

- lane and condition
- exact worker and Gov models per turn
- Gov, worker, retry, failover, embedding, and search call costs
- provider-reported input, output, cached, and reasoning tokens where available
- worker context receipt and selected episode/source IDs
- latency, visible repair, citation status, and search outcome
- continuity, insight, empathy, challenge, factuality, hallucination, and drift scores
