# Run The Hash-Locked Finance Benchmark From Mac

This Codex sandbox cannot transmit the private benchmark packet to external providers, even with approval. Run the live step from your Mac terminal instead.

## What This Runs

Hash lock: `current_event_finance_algo_execution_google_frontier_v1`

Solos:

- `solo_openai`: `openai:gpt-5.5`
- `solo_anthropic`: `anthropic:claude-opus-4-8`
- `solo_google`: `google:gemini-3.1-pro-preview`

Holo analyst order A, current baseline:

1. `openai:gpt-5.5`
2. `google:gemini-3.1-pro-preview`
3. `anthropic:claude-opus-4-8`
4. `google:gemini-3.1-pro-preview`
5. `anthropic:claude-opus-4-8`
6. `openai:gpt-5.5`

Gov:

Fixed for the full Holo session: `anthropic:claude-opus-4-8`.

Gov is a role, not an extra model slot. Opus may also appear as analyst, solo, and judge. Analyst order can be varied with `--routing-config`, but Gov never rotates inside a run.

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
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --routing-config order_a_current --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
```

If preflight reports any key as `MISSING`, stop and use your existing local secret setup. Do not paste keys into chat.

## Order-Sensitivity Runs

Run these only after the baseline run completes cleanly:

```bash
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --routing-config order_b_opus_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --routing-config order_c_gemini_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
```

Use one run at a time. Do not run A, B, and C in parallel.

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

The analyzer writes chart/report-ready files into the live run folder:

- `analysis/analysis_summary.json`
- `analysis/analysis_summary.md`
- `analysis/scores.csv`
- `analysis/judge_rows.csv`
- `analysis/criterion_gaps.csv`
- `analysis/condition_results.csv`

After it finishes, paste the inspector output or just tell Codex the run id.
