# Commerce OpenAI-W2 All-Six Canary External Execution Handoff

Date: 2026-06-29

## Purpose

Run the Commerce OpenAI-W2 Holo canary outside Codex because Codex tenant policy blocks exporting frozen benchmark packet/prompt content to external model providers.

This is not a benchmark failure and not a Commerce result. The in-Codex live attempt was blocked before any provider call started.

## Scope

- Family: `HV-ACOM-REP-2026-06-29`
- Target pairs: `HV-ACOM-REP-020`, `HV-ACOM-REP-006`, `HV-ACOM-REP-019`
- Packets: `6`
- Expected Holo calls: `30`
- Worker calls: `18`
- Gov calls: `12`
- Solo calls: `0`
- Judge calls: `0`
- No commerce full-family run
- No AP or IT run
- No packet edits
- No prompt edits
- No fallback/substitution

## Required Commits

- Packet freeze commit: `de22377be8175d04078ba6c70f1fd35222e9f572`
- Commerce W3 hardening commit: `7c6d105d`
- Commerce canary protocol commit: `2b9d4e8e89f46b5b84321d4308c12af47b32d736`

## Freeze Root

`5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Provider Roster

- W1: `xai/grok-3-mini`
- G1: `minimax/MiniMax-M2.5-highspeed`
- W2: `openai/gpt-5.4-mini`
- G2: `minimax/MiniMax-M2.5-highspeed`
- W3: `minimax/MiniMax-M2.5-highspeed`

Gov does not choose models. Gov only emits control actions.

## Environment Variables

Required:

- `XAI_API_KEY`
- `OPENAI_API_KEY`
- `MINIMAX_API_KEY`

Do not paste provider keys into chat. Run only in an authorized local shell/environment.

## Preflight Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor 2b9d4e8e89f46b5b84321d4308c12af47b32d736 "$(git rev-parse HEAD)"
python3 -B docs/benchmark/run_commerce_openai_w2_holo_all_six_collapse_canary_2026_06_29.py --preflight
```

Preflight must report:

- `status: PASS`
- `result: COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_CANARY_READY`
- `providers_called: 0`
- `target_pairs_count: true`
- `target_packets_count: true`
- `solo_triage_all_six_pairs_match: true`
- `minimax_final_compiler_worker_max_tokens: true`
- `minimax_final_compiler_budget_active: true`
- `expected_provider_calls: true`

## Live Canary Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_commerce_openai_w2_holo_all_six_collapse_canary_2026_06_29.py --run-live
```

## Post-Run Inspection Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
python3 - <<'PY'
import json
from pathlib import Path
root = Path("docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse")
runs = sorted([p for p in root.glob("run_*") if p.is_dir()])
latest = runs[-1]
summary = json.loads((latest / "canary_results.json").read_text())
print(json.dumps({
    "run_dir": str(latest),
    "classification": summary.get("classification"),
    "readiness_passed": summary.get("readiness_passed"),
    "provider_calls": summary.get("provider_calls"),
    "worker_calls": summary.get("worker_calls"),
    "gov_calls": summary.get("gov_calls"),
    "valid_pairs": summary.get("valid_pairs"),
    "packet_correct": summary.get("packet_correct"),
    "invalidation_reason": summary.get("invalidation_reason"),
    "root_failure": summary.get("root_failure"),
    "no_leakage": summary.get("no_leakage_audit", {}).get("status"),
    "readiness_assertions": summary.get("readiness_assertions"),
}, indent=2, sort_keys=True))
PY
```

## Expected Outputs

Inside:

`docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_<timestamp>/`

Expected files:

- `CANARY_PREFLIGHT.json`
- `TRACE_CALLS.jsonl`
- `canary_results.json`
- `canary_summary.md`
- `COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_NO_LEAKAGE_AUDIT.json`
- `COMMERCE_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_READINESS_ASSERTIONS.json`
- `LOCK_MANIFEST.json`
- `LOCK_VALIDATION.json`
- `prompts/`

## Pass Rules

Pass only if:

- `provider_calls=30`
- `worker_calls=18`
- `gov_calls=12`
- `solo_calls=0`
- `judge_calls=0`
- `provider_failures=[]`
- no leakage
- packet identity matches freeze
- all three worker DNA present
- Gov calls present and receive gate results
- deterministic gates present after every worker
- final selector present
- all 6 packets correct
- all 3 pairs valid

## Fail Rules

Fail closed if:

- any unrecovered transport failure occurs
- any Gov parse/content/truncation failure occurs
- any worker parse/content/truncation failure occurs
- any verdict failure occurs
- leakage occurs
- packet drift occurs
- trace is incomplete
- provider/model roster differs
- any fallback/substitution is needed

If the canary fails, preserve the failed run exactly as emitted. Do not repair, rerun, or substitute automatically.
