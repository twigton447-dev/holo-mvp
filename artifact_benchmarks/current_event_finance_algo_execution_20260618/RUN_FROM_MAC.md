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
python3 build_hash_locked_lift_rollup.py
```

If preflight reports any key as `MISSING`, stop and use your existing local secret setup. Do not paste keys into chat.

## Frontier Plus xAI Baseline

Use this lane when you want every mapped frontier solo against a four-frontier HoloAgent cohort that includes Grok 4.3. Gov remains fixed to Opus for the full Holo session.

```bash
python3 run_google_frontier_e2e.py --preflight --solo-suite frontier_plus_xai_baseline --routing-config frontier4_order_a_openai_bookend
python3 run_google_frontier_e2e.py --no-provider-smoke --solo-suite frontier_plus_xai_baseline --routing-config frontier4_order_a_openai_bookend
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite frontier_plus_xai_baseline --routing-config frontier4_order_a_openai_bookend --timeout 1200
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
python3 build_hash_locked_lift_rollup.py
```

Then repeat one at a time:

```bash
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite frontier_plus_xai_baseline --routing-config frontier4_order_b_opus_bookend --timeout 1200
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
python3 build_hash_locked_lift_rollup.py

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite frontier_plus_xai_baseline --routing-config frontier4_order_c_gemini_bookend --timeout 1200
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
python3 build_hash_locked_lift_rollup.py

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite frontier_plus_xai_baseline --routing-config frontier4_order_d_grok_bookend --timeout 1200
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
python3 build_hash_locked_lift_rollup.py
```

Interpretation rule: report Grok solo, Grok middle-turn, and Grok bookend results separately. Do not claim Frontier4 route-insensitive lift until all four Frontier4 routes have run or missing routes are labeled.

## Mini Solo Baseline

Use this after the frontier baseline smoke/preflight is clean. This run tests the locked mini solos against the default Holo route selected by `--routing-config`.

```bash
python3 run_google_frontier_e2e.py --preflight --solo-suite mini_baseline
python3 run_google_frontier_e2e.py --no-provider-smoke --solo-suite mini_baseline
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config order_a_current --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
python3 build_hash_locked_lift_rollup.py
```

Mini suite solos:

- `solo_openai_mini`: `openai:gpt-4o-mini`
- `solo_anthropic_haiku`: `anthropic:claude-haiku-4-5-20251001`
- `solo_google_flash_lite`: `google:gemini-2.5-flash-lite`
- `solo_xai_grok_mini`: `xai:grok-3-mini`
- `solo_minimax_m25_highspeed`: `minimax:MiniMax-M2.5-highspeed`

## Mini-Holo All-5 Matrix

Use this lane to put minis on both sides: every locked mini solo versus all-mini Holo routes. Each route uses all five mini analysts; one model opens and closes because six turns cannot evenly divide five models. Gov is fixed to `openai:gpt-4o-mini` across this diagnostic matrix.

First run:

```bash
python3 run_google_frontier_e2e.py --preflight --solo-suite mini_baseline --routing-config mini_order_a_openai_bookend
python3 run_google_frontier_e2e.py --no-provider-smoke --solo-suite mini_baseline --routing-config mini_order_a_openai_bookend
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_order_a_openai_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
python3 build_hash_locked_lift_rollup.py
```

Then repeat one at a time:

```bash
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_order_b_haiku_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_order_c_gemini_lite_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_order_d_grok_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_order_e_minimax_bookend --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
```

Do not run these routes in parallel. Each run creates a full data trail: prompt cards, traces, condition manifests, state objects, mission packets, final selection, blind judge packets, judge scores, analysis CSVs, and intelligence chart data.

## Mini-Holo Gov Ablation

Use this after the first mini-Holo route exists. This holds the HoloAgent analyst order constant and changes only Gov. Frontier judges remain fixed across every run.

```bash
caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_gov_haiku_order_a --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_gov_gemini_lite_order_a --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_gov_grok_order_a --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest

caffeinate -dimsu python3 run_google_frontier_e2e.py --run-live --solo-suite mini_baseline --routing-config mini_gov_minimax_order_a --timeout 900
python3 inspect_google_frontier_run.py --latest
python3 analyze_google_frontier_run.py --latest
python3 build_benchmark_intelligence.py --latest
```

Interpretation rule: if lift survives Gov changes, report it as Gov-robust within this packet and cohort. Still report the best Gov, worst Gov, sensitivity range, token cost, and latency.

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

The intelligence builder writes:

- `intelligence/benchmark_intelligence.json`
- `intelligence/benchmark_intelligence.md`
- `intelligence/chart_data.csv`

The intelligence output includes deterministic insight extraction: top lift drivers, insight themes, per-solo theme heatmaps, judge-rationale evidence, token cost, and latency.

The rollup writes cross-run files into:

- `suite_rollups/hash_locked_lift_rollup.json`
- `suite_rollups/hash_locked_lift_rollup.md`
- `suite_rollups/hash_locked_lift_rollup.csv`

Use `aggregate_current_lock_matching_runs` for strict claims. Use older completed runs only as labeled diagnostics.
- `analysis/criterion_gaps.csv`
- `analysis/condition_results.csv`

The intelligence builder writes client-readable benchmark intelligence and chart data:

- `intelligence/benchmark_intelligence.json`
- `intelligence/benchmark_intelligence.md`
- `intelligence/chart_data.csv`

After it finishes, paste the inspector output or just tell Codex the run id.
