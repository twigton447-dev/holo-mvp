# AP OpenAI-W2 All-Six-Collapse Holo Canary External Execution Handoff

Date: 2026-06-29

Classification: `AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_EXTERNAL_EXECUTION_HANDOFF`

Status: `READY_FOR_AUTHORIZED_LOCAL_SHELL_EXECUTION`

## Purpose

Run HoloVerify on only the six AP pairs where the completed weak-mini solo batch showed `ALL_SIX_SOLO_COLLAPSE`.

This is the next spend-control step before a full 20-pair / 200-call AP Holo run.

Codex should not execute this live provider run from the managed environment because it exports frozen private benchmark packet/prompt content to external providers. Run it in an authorized local shell, then inspect the saved run folder.

## Required Runtime

Canary runner commit:

```text
ba13bd01aaf4747ccb0d8bd34d9df7f020cae7df
```

Underlying AP OpenAI-W2 runtime and empty-worker retry policy:

```text
ba13bd01aaf4747ccb0d8bd34d9df7f020cae7df
```

Packet freeze root:

```text
5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7
```

## Scope

- Family: AP / procurement / vendor-master controls.
- Pair count: `6`.
- Packet count: `12`.
- Expected Holo calls: `60`.
- Expected worker calls: `36`.
- Expected Gov calls: `24`.
- Solo calls: `0`.
- Judge calls: `0`.
- Commerce/IT calls: `0`.

Target pairs:

```text
HV-AP-REP-011
HV-AP-REP-012
HV-AP-REP-013
HV-AP-REP-019
HV-AP-REP-005
HV-AP-REP-010
```

These target pairs come from:

```text
docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29/solo_triage_3mini/ap_family_120call/run_20260629T183456Z
```

The solo triage lock passed and identified these exact six as `ALL_SIX_SOLO_COLLAPSE`.

## Roster

| Slot | Provider/model |
| --- | --- |
| W1 | `xai/grok-3-mini` |
| G1 | `minimax/MiniMax-M2.5-highspeed` |
| W2 | `openai/gpt-5.4-mini` |
| G2 | `minimax/MiniMax-M2.5-highspeed` |
| W3 | `minimax/MiniMax-M2.5-highspeed` |

Gov does not choose models. Gov routes control actions only.

## Required Runtime Policies

- Transport retry policy: `HOLOVERIFY_TRANSPORT_RETRY_POLICY_V1_2026_06_29`
- Empty-worker retry policy: `HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29`
- Empty-worker retry max retries: `2`

The empty-worker policy applies only when a worker call returns exactly empty text with `output_tokens=0` and a non-`length` finish reason. It does not retry malformed content, wrong verdicts, Gov baton failures, deterministic-gate failures, invented source IDs, or any non-empty parse failure.

## Required Environment Variables

- `XAI_API_KEY`
- `OPENAI_API_KEY`
- `MINIMAX_API_KEY`

Optional MiniMax endpoint overrides, only if needed locally:

- `MINIMAX_CHAT_COMPLETIONS_URL`
- `MINIMAX_BASE_URL`

Do not paste provider keys into chat.

## Exact Preflight Command

This is local-only and should not call providers.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor ba13bd01aaf4747ccb0d8bd34d9df7f020cae7df "$(git rev-parse HEAD)"
python3 -B docs/benchmark/run_ap_openai_w2_holo_all_six_collapse_canary_2026_06_29.py --preflight
```

Preflight must report:

- `status: PASS`
- `result: AP_OPENAI_W2_ALL_SIX_COLLAPSE_CANARY_READY`
- `pairs: 6`
- `packets: 12`
- `total_provider_calls: 60`
- `worker_calls: 36`
- `gov_calls: 24`
- `solo_calls: 0`
- `judge_calls: 0`
- target pairs match the AP solo triage all-six-collapse set
- no Gemini active
- W2 is `openai/gpt-5.4-mini`
- Gov is MiniMax
- worker contract is `compact_key_value_v1`
- Gov contract is `gov_micro_baton_v2`
- Gov max tokens is `1024`
- empty-worker retry policy is `HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29`
- empty-worker max retries is `2`
- provider calls during preflight: `0`

## Exact Live Canary Command

Run this only in an authorized local shell/environment.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor ba13bd01aaf4747ccb0d8bd34d9df7f020cae7df "$(git rev-parse HEAD)"
set -a; source .env; set +a
python3 -B docs/benchmark/run_ap_openai_w2_holo_all_six_collapse_canary_2026_06_29.py --run-live
```

If the command exits nonzero, preserve the generated run folder. Do not rerun automatically.

## Exact Post-Run Audit Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
RUN_DIR="$(ls -td docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_* | head -1)"
python3 - "$RUN_DIR" <<'PY'
import json
import sys
from pathlib import Path

run = Path(sys.argv[1])
summary = json.loads((run / "canary_results.json").read_text())
lock = json.loads((run / "LOCK_VALIDATION.json").read_text())
rows = [json.loads(line) for line in (run / "TRACE_CALLS.jsonl").read_text().splitlines() if line.strip()]
empty_worker_recovered = sum(1 for row in rows if row.get("empty_worker_output_recovered") is True)
empty_worker_attempts = sum((row.get("empty_worker_output_attempt_count") or 0) for row in rows)
report = {
    "run_dir": str(run),
    "classification": summary.get("classification"),
    "readiness_passed": summary.get("readiness_passed"),
    "provider_calls": summary.get("provider_calls"),
    "expected_provider_calls": summary.get("expected_provider_calls"),
    "worker_calls": summary.get("worker_calls"),
    "gov_calls": summary.get("gov_calls"),
    "solo_calls": summary.get("solo_calls"),
    "judge_calls": summary.get("judge_calls"),
    "provider_failures": len(summary.get("provider_failures") or []),
    "terminal_failures": len(summary.get("terminal_failures") or []),
    "root_failure": summary.get("root_failure"),
    "lock_validation": lock.get("validation_status"),
    "no_leakage_status": (summary.get("no_leakage_audit") or {}).get("status"),
    "trace_rows": len(rows),
    "empty_worker_output_recovered_count": empty_worker_recovered,
    "empty_worker_output_attempt_total": empty_worker_attempts,
    "target_pair_ids": summary.get("target_pair_ids"),
    "packet_correct": summary.get("packet_correct"),
    "valid_pairs": summary.get("valid_pairs"),
    "readiness_assertions": summary.get("readiness_assertions"),
}
print(json.dumps(report, indent=2, sort_keys=True))
PY
```

## Expected Outputs

Run folder:

```text
docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_*
```

Expected files:

- `CANARY_PREFLIGHT.json`
- `TRACE_CALLS.jsonl`
- `canary_results.json`
- `canary_summary.md`
- `LOCK_MANIFEST.json`
- `LOCK_VALIDATION.json`
- `AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_NO_LEAKAGE_AUDIT.json`
- `AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_READINESS_ASSERTIONS.json`
- `prompts/`
- `artifacts/`

## Pass Rules

Pass only if:

- `12` packets complete.
- `6` pairs complete.
- `60` Holo calls complete.
- `36` worker calls complete.
- `24` Gov calls complete.
- no unrecovered provider failures.
- no terminal parse/content failures.
- recovered exact-empty worker attempts are allowed only if logged under `HOLOVERIFY_EMPTY_WORKER_OUTPUT_RETRY_POLICY_V1_2026_06_29`.
- Gov v2 parses every Gov turn.
- worker compact parses every worker turn.
- no leakage.
- packet identity matches freeze.
- all final verdicts correct and admissible.
- final selector present.
- solo calls `0`.
- judge calls `0`.

If this canary passes, the next valid move is the full AP OpenAI-W2 20-pair Holo family run.
