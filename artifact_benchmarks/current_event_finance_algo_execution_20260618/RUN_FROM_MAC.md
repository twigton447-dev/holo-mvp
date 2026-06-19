# Run The Hash-Locked Finance Benchmark From Mac

This Codex sandbox cannot transmit the private benchmark packet to external providers, even with approval. Run the live step from your Mac terminal instead.

## What This Runs

Hash lock: `current_event_finance_algo_execution_google_frontier_v1`

Solos:

- `solo_openai`: `openai:gpt-5.5`
- `solo_anthropic`: `anthropic:claude-opus-4-8`
- `solo_google`: `google:gemini-3.1-pro-preview`

Solo suite: `frontier_baseline`.

The suite manifest is `solo_model_sweep.json`. Treat it as immutable after live evidence exists. If model conditions change, add a new suite id instead of editing historical conditions.

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
- xAI `grok-4.3`

Primary scoring excludes judge rows where the judge provider is the same provider as the solo model being evaluated. Excluded rows stay available as diagnostics.

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
python3 build_benchmark_intelligence.py --latest
```

If preflight reports any key as `MISSING`, stop and use your existing local secret setup. Do not paste keys into chat.

## Mini Solo Baseline

Use this after the frontier baseline smoke/preflight is clean:

```bash
python3 run_google_frontier_e2e.py --preflight --solo-suite mini_baseline
python3 run_google_frontier_e2e.py --no-provider-smoke --solo-suite mini_baseline
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config order_a_current --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
```

Mini suite solos:

- `solo_openai_mini`: `openai:gpt-4o-mini`
- `solo_anthropic_haiku`: `anthropic:claude-haiku-4-5-20251001`
- `solo_google_flash_lite`: `google:gemini-2.5-flash-lite`
- `solo_xai_grok_mini`: `xai:grok-3-mini`
- `solo_minimax_m25_highspeed`: `minimax:MiniMax-M2.5-highspeed`

## Extended Solo Sweep

This is the expensive diagnostic lane for ranking every mapped solo against the same Holo artifact. Run only after frontier and mini suites smoke cleanly:

```bash
python3 run_google_frontier_e2e.py --preflight --solo-suite extended_solo_sweep
python3 run_google_frontier_e2e.py --no-provider-smoke --solo-suite extended_solo_sweep
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite extended_solo_sweep --routing-config order_a_current --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
```

Invalid solo finals are preserved as invalid rows and skipped for final pair judging instead of killing the whole sweep. That lets the sweep finish while still showing which model failed the deterministic artifact gates.

## Order-Sensitivity Runs

Run these only after the baseline run completes cleanly:

```bash
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --routing-config order_b_opus_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --routing-config order_c_gemini_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
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

The intelligence builder writes client-readable benchmark intelligence and chart data:

- `intelligence/benchmark_intelligence.json`
- `intelligence/benchmark_intelligence.md`
- `intelligence/chart_data.csv`

After it finishes, paste the inspector output or just tell Codex the run id.
