# Run The Hash-Locked Finance Benchmark From Mac

This Codex sandbox cannot transmit the private benchmark packet to external providers, even with approval. Run the live step from your Mac terminal instead.

## What This Runs

Hash lock: `current_event_finance_algo_execution_google_frontier_v1`

Solos:

- `solo_openai`: `openai:gpt-5.5`
- `solo_anthropic`: `anthropic:claude-opus-4-8`
- `solo_google`: `google:gemini-3.1-pro-preview`

Holo:

1. `openai:gpt-5.5`
2. `google:gemini-3.1-pro-preview`
3. `anthropic:claude-opus-4-8`
4. `google:gemini-3.1-pro-preview`
5. `anthropic:claude-opus-4-8`
6. `openai:gpt-5.5`

Gov:

1. none
2. `google:gemini-3.1-pro-preview`
3. `openai:gpt-5.5`
4. `anthropic:claude-opus-4-8`
5. `google:gemini-3.1-pro-preview`
6. `openai:gpt-5.5`

Judges:

- OpenAI `gpt-5.5`
- Anthropic `claude-opus-4-8`
- Google `gemini-3.1-pro-preview`

## Commands

Open Terminal on the Mac and run:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp
git pull --ff-only
cd artifact_benchmarks/current_event_finance_algo_execution_20260618
python3 run_google_frontier_e2e.py --preflight
python3 run_google_frontier_e2e.py --no-provider-smoke
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --timeout 420
python3 inspect_google_frontier_run.py --latest
```

If preflight reports any key as `MISSING`, stop and use your existing local secret setup. Do not paste keys into chat.

## Expected Output

The live command writes a new folder under:

```text
/Users/taylorwigton/CascadeProjects/holo-mvp/artifact_benchmarks/current_event_finance_algo_execution_20260618/runs/
```

The inspector prints:

- run status
- run id
- condition word counts
- final artifact paths
- token and latency totals
- judge summary path
- Holo-vs-solo gap
- judge validation flags

After it finishes, paste the inspector output or just tell Codex the run id.
