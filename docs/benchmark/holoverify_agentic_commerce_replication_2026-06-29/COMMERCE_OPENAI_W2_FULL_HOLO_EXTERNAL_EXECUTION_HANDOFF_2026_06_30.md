# Commerce OpenAI-W2 Full Holo External Execution Handoff

Date: 2026-06-30

Classification: `COMMERCE_OPENAI_W2_FULL_HOLO_EXTERNAL_EXECUTION_HANDOFF`

Status: `READY_FOR_AUTHORIZED_LOCAL_SHELL_EXECUTION`

## Purpose

Run the full Agentic Commerce OpenAI-W2 Holo family outside Codex because Codex cannot export frozen private benchmark prompts to external providers under the active tenant policy. This is an execution handoff, not a benchmark result.

The in-Codex live attempt was blocked before any provider call started. That is not a Commerce failure, not a Holo failure, and not a provider failure.

## Required Runtime Ancestor

```text
78164d478cc573c85ec0894c3bccf8c367623b5d
```

The current checkout must contain this commit in its ancestry. Exact `HEAD` equality is not required if later local-only handoff files are present.

## Frozen Packet Bank

- Packet freeze commit: `de22377be8175d04078ba6c70f1fd35222e9f572`
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- Family: `HV-ACOM-REP-2026-06-29`
- Family name: Agentic Commerce Order-Execution Controls

## Prior Commerce Evidence

Successful all-six canary:

```text
docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260630T031643Z
```

Canary facts:

- Provider calls: `30/30`.
- Worker calls: `18`.
- Gov calls: `12`.
- Solo calls: `0`.
- Judge calls: `0`.
- Valid pairs: `3/3`.
- Packet correctness: `6/6`.
- No leakage: `PASS`.
- Readiness assertions: `PASS`.

Latest invalid full-family attempt:

```text
docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2/run_20260630T032421Z
```

That run failed closed at `122/200` provider calls on MiniMax Gov DNS resolution:

```text
HV-ACOM-REP-013-A_G1
URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>
```

This was classified by the no-provider autopsy as a provider transport/DNS failure, not a verdict failure and not a Gov content-contract failure. The runner now includes the Commerce transport failure hardening path.

## Scope

- Commerce family only.
- `20` sibling pairs.
- `40` frozen packets.
- Expected Holo calls: `200`.
- Worker calls: `120`.
- Gov calls: `80`.
- Solo calls: `0`.
- Judge calls: `0`.
- No AP run.
- No IT run.
- No packet edits.
- No prompt edits.
- No fallback or substitution.

## Provider Roster

| Slot | Provider/model |
| --- | --- |
| W1 | `xai/grok-3-mini` |
| G1 | `minimax/MiniMax-M2.5-highspeed` |
| W2 | `openai/gpt-5.4-mini` |
| G2 | `minimax/MiniMax-M2.5-highspeed` |
| W3 | `minimax/MiniMax-M2.5-highspeed` |

Gov does not choose models. Gov routes control actions only.

## Environment Variables

Required:

- `XAI_API_KEY`
- `OPENAI_API_KEY`
- `MINIMAX_API_KEY`

Optional MiniMax endpoint overrides, only if needed in the local environment:

- `MINIMAX_CHAT_COMPLETIONS_URL`
- `MINIMAX_BASE_URL`

Do not paste provider keys into chat.

## Exact Preflight Command

Run this before live execution. It is local-only and should not call providers.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor 78164d478cc573c85ec0894c3bccf8c367623b5d "$(git rev-parse HEAD)"
python3 -B -m pytest -q docs/benchmark/test_ap_openai_w2_invalid_run_handling_2026_06_29.py docs/benchmark/test_commerce_w3_worker_failure_hardening_2026_06_29.py
python3 -B docs/benchmark/run_commerce_replication_holoverify_3dna_2026_06_29.py --preflight-openai-w2
```

The preflight must verify:

- `classification=COMMERCE_OPENAI_W2_LIVE_HOLO_PREFLIGHT`
- `status=PASS`
- `result=COMMERCE_OPENAI_W2_READY_FOR_FULL_HOLO_RUN`
- freeze root matches `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- W2 is `openai/gpt-5.4-mini`
- no Gemini active
- worker contract `compact_key_value_v1`
- Gov contract `gov_micro_baton_v2`
- MiniMax final compiler budget active
- transport policy active
- solo calls configured `0`
- judge calls configured `0`
- expected Holo calls `200`
- provider calls during preflight `0`
- judge calls during preflight `0`

Current preflight root signature:

```text
a2d1ac9d0cbd91b2f6c4b7b57f023daad031a1ed8580a75cdbe8016fe265c7d1
```

## Exact Live Full-Holo Command

Run this only in an authorized local shell/environment.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor 78164d478cc573c85ec0894c3bccf8c367623b5d "$(git rev-parse HEAD)"
set -a; source .env; set +a
python3 -B docs/benchmark/run_commerce_replication_holoverify_3dna_2026_06_29.py --run-holo-openai-w2
```

If the command exits nonzero, preserve the generated run folder. Do not rerun automatically.

## Exact Post-Run Audit Command

Run this after the live command completes.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
RUN_DIR="$(ls -td docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2/run_* | head -1)"
python3 - "$RUN_DIR" <<'PY'
import json
import sys
from pathlib import Path

run = Path(sys.argv[1])
summary = json.loads((run / "live_results.json").read_text())
assertions = json.loads((run / "AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS.json").read_text())
lock = json.loads((run / "LOCK_VALIDATION.json").read_text())
leak = json.loads((run / "AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT.json").read_text())
rows = [json.loads(line) for line in (run / "TRACE_CALLS.jsonl").read_text().splitlines() if line.strip()]
worker_rows = [row for row in rows if row.get("call_kind") == "worker"]
gov_rows = [row for row in rows if row.get("call_kind") == "gov"]
report = {
    "run_dir": str(run),
    "classification": summary.get("classification"),
    "readiness_passed": summary.get("readiness_passed"),
    "provider_calls": summary.get("provider_calls"),
    "worker_calls": summary.get("worker_calls"),
    "gov_calls": summary.get("gov_calls"),
    "solo_calls": summary.get("solo_calls"),
    "judge_calls": summary.get("judge_calls"),
    "root_failure": summary.get("root_failure"),
    "transport_recovered_call_count": summary.get("transport_recovered_call_count"),
    "no_leakage_status": leak.get("status"),
    "lock_validation": lock.get("validation_status"),
    "readiness_result": assertions.get("result"),
    "trace_rows": len(rows),
    "worker_rows": len(worker_rows),
    "gov_rows": len(gov_rows),
}
print(json.dumps(report, indent=2, sort_keys=True))
PY
```

The inherited AP filenames in the run folder are expected because Commerce reuses the hardened AP OpenAI-W2 runtime path with Commerce packet binding.

## Expected Outputs

Inside:

```text
docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2/run_<timestamp>/
```

Expected files:

- `live_summary.md`
- `live_results.json`
- `TRACE_CALLS.jsonl`
- `LOCK_MANIFEST.json`
- `LOCK_VALIDATION.json`
- `AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT.md`
- `AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT.json`
- `AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS.md`
- `AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS.json`
- `prompts/`
- `artifacts/`

## Pass Rules

Pass only if:

- `40` packets complete.
- `20` pairs complete.
- expected `200` Holo calls complete.
- no unrecovered provider failures.
- Gov v2 parses every Gov turn.
- worker compact parses every worker turn.
- no leakage.
- packet identity matches freeze.
- final verdicts correct.
- solo calls `0`.
- judge calls `0`.

## Fail Rules

Fail closed if:

- unrecovered transport failure.
- Gov parse/content/truncation failure.
- worker parse/content/truncation failure.
- verdict failure.
- leakage.
- packet drift.
- incomplete calls.
- roster mismatch.
- fallback or substitution needed.

If the full-family run fails, preserve the failed run exactly as emitted. Do not repair, rerun, or substitute automatically.

