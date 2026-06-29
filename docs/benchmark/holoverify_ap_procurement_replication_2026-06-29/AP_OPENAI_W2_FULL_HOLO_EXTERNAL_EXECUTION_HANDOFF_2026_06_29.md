# AP OpenAI-W2 Full Holo External Execution Handoff

Date: 2026-06-29

Classification: `AP_OPENAI_W2_FULL_HOLO_EXTERNAL_EXECUTION_HANDOFF`

Status: `READY_FOR_AUTHORIZED_LOCAL_SHELL_EXECUTION`

## Purpose

Run the full AP / procurement OpenAI-W2 Holo family outside Codex because Codex cannot export frozen private benchmark prompts to external providers under the active tenant policy. This is an execution handoff, not a benchmark result.

This refresh supersedes the stale full-family wrapper handoff and the earlier Gov-budget-only handoff. The live command now uses the repo-owned AP runtime path pinned to the successful all-six-collapse canary evidence, not `/private/tmp/run_ap_openai_w2_holo_policy_v1.py`.

## Required Runtime Ancestor

```text
e3b78f17096d48569cc9e9546d3a99b063499e1b
```

The current checkout must contain this canary-good runtime commit in its ancestry. The refreshed handoff itself may live on a later commit, so use the ancestor check below rather than requiring exact `HEAD` equality.

## Root Cause Fixed

The full AP path used the correct Gov v2 prompt and parser, but the old Gov max output budget was too small:

```text
GOV_MAX_TOKENS = 384
```

MiniMax Gov truncated after four of seven required baton lines and failed closed with:

```text
ValueError: gov_finish_reason_length_incomplete_baton
```

The AP OpenAI-W2 runtime now binds:

```text
AP_OPENAI_W2_GOV_MAX_TOKENS = 1024
RUNNER.GOV_MAX_TOKENS = AP_OPENAI_W2_GOV_MAX_TOKENS
```

The parser remains strict. Empty, malformed, or truncated Gov batons still fail closed.

## Successful All-Six Canary Lock

The full-family handoff is now pinned after the successful AP OpenAI-W2 all-six-collapse canary run:

```text
docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260629T193200Z
```

Preserved canary facts:

- Provider calls: `60/60`.
- Worker calls: `36`.
- Gov calls: `24`.
- Solo calls: `0`.
- Judge calls: `0`.
- Provider failures: `0`.
- Parse failures: `0`.
- Empty-worker recoveries needed: `0`.
- Packet correctness: `12/12`.
- Corrected valid pairs: `6/6`.
- No leakage: `PASS`.
- Lock validation: `PASS`.

The raw canary run folder remains preserved exactly as emitted. Its original generated summary used a stale canary readiness rule; commit `2e160dbe714522dd5afe4ce62f58fe7efbde8df9` documents and patches that rule prospectively without mutating the locked run. The corrected audit classifies the canary as `CANARY_COMPLETE_ALL_PACKETS_CORRECT_READINESS_RULE_MISMATCH`, which unlocks this full-family handoff.

## Scope

- AP / procurement family only.
- `20` sibling pairs.
- `40` frozen packets.
- Expected Holo calls: `200`.
- No solo baseline.
- No judges.
- No commerce or IT runs.
- No packet edits.
- No prompt edits.
- No fallback or substitution.

## Required Lineage

| Layer | Commit |
| --- | --- |
| Packet freeze | `de22377be8175d04078ba6c70f1fd35222e9f572` |
| OpenAI-W2 protocol | `50647772a80437096a943850d522bf18ca0d58e2` |
| Invalid-run hardening | `5d365d480bb574fb51f8bccb6ff6399b13303b78` |
| Transport policy | `69cdaea584f0a546a119a508da4487c27f789136` |
| Worker contract hardening | `afdda17cf00647ae672c8bd8d6cdb300e5d7f322` |
| Compact worker verification | `57e5ce6e648d2d170ec1d3ffedba4ccdf0597e91` |
| Gov placeholder fix | `4ae402f06d47f7e839de1aa4f8c2f68d88cf9a5c` |
| Successful 1-pair canary evidence | `65d9d9f2ef24a509522036342684806b1637e561` |
| Gov runtime budget patch | `ff7c269942026780a61f741514ea47ccf594b75f` |
| Empty worker output retry policy | `ba13bd01aaf4747ccb0d8bd34d9df7f020cae7df` |
| All-six canary handoff refresh | `8042c4e42dc493ba6787dfe912a52894174a026f` |
| All-six canary readiness rule fix | `2e160dbe714522dd5afe4ce62f58fe7efbde8df9` |
| Successful all-six canary evidence | `e3b78f17096d48569cc9e9546d3a99b063499e1b` |

Freeze root:

```text
5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7
```

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
git merge-base --is-ancestor e3b78f17096d48569cc9e9546d3a99b063499e1b "$(git rev-parse HEAD)"
python3 -B docs/benchmark/test_ap_full_holo_gov_runtime_path_2026_06_29.py
python3 -B docs/benchmark/run_ap_replication_holoverify_3dna_2026_06_29.py --preflight-openai-w2
```

The preflight must verify:

- Freeze root matches `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`.
- AP packet/prompt hashes match freeze.
- W2 is `openai/gpt-5.4-mini`.
- no Gemini active.
- compact worker contract `compact_key_value_v1` is active.
- Gov micro-baton contract `gov_micro_baton_v2` is active.
- Gov selected baton lines are concrete and parseable.
- no placeholder hits.
- AP Gov max tokens is `1024`.
- empty worker output retry policy is active.
- transport policy V1 is active.
- solo calls configured `0`.
- judge calls configured `0`.
- expected Holo calls `200`.
- expected packets `40`.
- expected pairs `20`.
- provider calls `0`.
- judge calls `0`.

## Exact Live Full-Holo Command

Run this only in an authorized local shell/environment. This is the patched repo-owned runtime path.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor e3b78f17096d48569cc9e9546d3a99b063499e1b "$(git rev-parse HEAD)"
set -a; source .env; set +a
python3 -B docs/benchmark/run_ap_replication_holoverify_3dna_2026_06_29.py --run-holo-openai-w2
```

If the command exits nonzero, preserve the generated run folder. Do not rerun automatically.

## Exact Post-Run Audit Command

Run this after the live command completes.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
RUN_DIR="$(ls -td docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/run_* | head -1)"
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
    "readiness_result": assertions.get("result"),
    "provider_calls": summary.get("provider_calls"),
    "worker_calls": summary.get("worker_calls"),
    "gov_calls": summary.get("gov_calls"),
    "solo_calls": summary.get("solo_calls"),
    "judge_calls": summary.get("judge_calls"),
    "root_failure": summary.get("root_failure"),
    "transport_recovered_call_count": summary.get("transport_recovered_call_count"),
    "no_leakage_status": leak.get("status"),
    "lock_validation": lock.get("validation_status"),
    "packet_identity": "PASS" if summary.get("freeze_root_hash") == "5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7" else "FAIL",
    "trace_rows": len(rows),
    "worker_rows": len(worker_rows),
    "gov_rows": len(gov_rows),
}
print(json.dumps(report, indent=2, sort_keys=True))
PY
```

## Expected Outputs

The run folder should contain:

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

Fail if:

- unrecovered transport failure.
- Gov parse/content failure.
- worker parse/content failure.
- verdict failure.
- leakage.
- packet drift.
- incomplete calls.
- solo or judge call appears.
- commerce or IT lane starts.

Stop after the full AP Holo run. If it passes, the next separate decision is whether to run the solo baseline. If it fails, preserve the run folder and do not rerun automatically.
