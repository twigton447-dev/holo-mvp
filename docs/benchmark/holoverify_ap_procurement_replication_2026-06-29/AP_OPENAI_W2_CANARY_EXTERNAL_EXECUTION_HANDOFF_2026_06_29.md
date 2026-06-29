# AP OpenAI-W2 Canary External Execution Handoff

Date: 2026-06-29

Classification: `AP_OPENAI_W2_CANARY_EXTERNAL_EXECUTION_HANDOFF`

Status: `READY_FOR_AUTHORIZED_LOCAL_SHELL_EXECUTION`

## Purpose

Run one AP OpenAI-W2 Holo canary pair outside Codex because Codex cannot export frozen benchmark prompts to external providers under the active tenant policy. This is an execution handoff, not a benchmark result.

Current Codex state:

- Local preflight passed.
- Gov placeholder fix is active at `4ae402f06d47f7e839de1aa4f8c2f68d88cf9a5c`.
- Freeze root matched.
- No Gemini is active in the AP OpenAI-W2 canary runner.
- No provider calls were made inside Codex for the second canary.
- No live canary was started inside Codex.

## Scope

- One AP pair only: `HV-AP-REP-001`.
- Both siblings included: `A` and `B`.
- Expected Holo calls: `10`.
- No full AP run.
- No solo run.
- No judges.
- No commerce or IT runs.
- No packet edits.
- No prompt edits.

The local wrapper is:

```text
/private/tmp/run_ap_openai_w2_one_pair_canary.py
```

The wrapper writes a fresh timestamped run folder under:

```text
docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/
```

## Required Lineage

| Layer | Commit |
| --- | --- |
| Packet freeze | `de22377` |
| OpenAI-W2 protocol | `5064777` |
| Invalid-run hardening | `5d365d` |
| Transport policy | `69cdaea` |
| Worker contract hardening | `afdda17` |
| Compact worker verification | `57e5ce6` |
| Gov placeholder fix | `4ae402f` |

Required current HEAD for this handoff:

```text
4ae402f06d47f7e839de1aa4f8c2f68d88cf9a5c
```

## Freeze Root

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

No Gemini should appear in the active canary runner.

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

Run this before the live canary. It performs local checks only and should not call providers.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 - <<'PY'
import importlib.util
import json

p = "/private/tmp/run_ap_openai_w2_one_pair_canary.py"
spec = importlib.util.spec_from_file_location("canary", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
freeze, pairs, canary_pairs, checks = m.preflight()
print(json.dumps({
    "head_matches_gov_placeholder_fix": checks["head_matches_gov_v2_commit"],
    "freeze_root": freeze["summary"].get("freeze_root_hash"),
    "pair_count": len(pairs),
    "canary_pair_id": canary_pairs[0]["pair_id"],
    "w2_model": checks["w2_model"],
    "no_gemini_active": checks["no_gemini_active"],
    "worker_contract_format": checks["worker_contract_format"],
    "gov_contract_format": checks["gov_contract_format"],
    "gov_prompt_placeholder_hits": checks["gov_prompt_placeholder_hits"],
    "gov_prompt_selected_baton_lines": checks["gov_prompt_selected_baton_lines"],
    "transport_max_retries": checks["transport_max_retries"],
    "openai_timeout_seconds": checks["openai_timeout_seconds"],
    "missing_provider_env": checks["missing_provider_env"],
}, indent=2, sort_keys=True))
PY
```

Expected preflight highlights:

- `head_matches_gov_placeholder_fix: true`
- `freeze_root: 5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- `canary_pair_id: HV-AP-REP-001`
- `w2_model: gpt-5.4-mini`
- `no_gemini_active: true`
- `worker_contract_format: compact_key_value_v1`
- `gov_contract_format: gov_micro_baton_v2`
- `gov_prompt_placeholder_hits: []`
- `missing_provider_env: []`

## Exact Live Canary Command

Run this only in an authorized local shell/environment.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B /private/tmp/run_ap_openai_w2_one_pair_canary.py
```

If the command exits nonzero, preserve the generated run folder. Do not rerun automatically.

## Exact Post-Run Audit Command

Run this after the canary command completes.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
RUN_DIR="$(ls -td docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_* | head -1)"
python3 - "$RUN_DIR" <<'PY'
import json
import sys
from pathlib import Path

run = Path(sys.argv[1])
summary = json.loads((run / "canary_results.json").read_text())
lock = json.loads((run / "LOCK_VALIDATION.json").read_text())
leak = json.loads((run / "AP_OPENAI_W2_CANARY_NO_LEAKAGE_AUDIT.json").read_text())
rows = [json.loads(line) for line in (run / "TRACE_CALLS.jsonl").read_text().splitlines() if line.strip()]
report = {
    "run_dir": str(run),
    "classification": summary.get("classification"),
    "readiness_passed": summary.get("readiness_passed"),
    "failure_class": summary.get("failure_class"),
    "provider_calls": summary.get("provider_calls"),
    "expected_provider_calls": summary.get("expected_provider_calls"),
    "worker_calls": summary.get("worker_calls"),
    "gov_calls": summary.get("gov_calls"),
    "solo_calls": summary.get("solo_calls"),
    "judge_calls": summary.get("judge_calls"),
    "provider_failures": len(summary.get("provider_failures") or []),
    "terminal_failures": len(summary.get("terminal_failures") or []),
    "root_failure": summary.get("root_failure"),
    "readiness_assertions": summary.get("readiness_assertions"),
    "lock_validation": lock.get("validation_status"),
    "lock_root_signature": lock.get("root_signature"),
    "leakage_status": leak.get("status"),
    "trace_rows": len(rows),
}
print(json.dumps(report, indent=2, sort_keys=True))
if not summary.get("readiness_passed"):
    raise SystemExit(2)
PY
```

## Expected Outputs

The canary run folder should contain:

- `canary_summary.md`
- `canary_results.json`
- `TRACE_CALLS.jsonl`
- `LOCK_MANIFEST.json`
- `LOCK_VALIDATION.json`
- `AP_OPENAI_W2_CANARY_NO_LEAKAGE_AUDIT.md`
- `AP_OPENAI_W2_CANARY_NO_LEAKAGE_AUDIT.json`
- `AP_OPENAI_W2_CANARY_READINESS_ASSERTIONS.json`
- `CANARY_PRE_RUN_MANIFEST.json`
- prompt refs under `prompts/`
- worker artifacts under `artifacts/`

## Pass Rules

Pass only if all of the following are true:

- `2` packets complete.
- `1` pair complete.
- Expected `10` Holo calls complete.
- No unrecovered provider failures.
- Gov v2 parses on every Gov turn.
- Worker compact parses on every worker turn.
- No leakage.
- Packet identity matches freeze.
- Both sibling final verdicts are correct.
- Final selector is present.
- Solo calls are `0`.
- Judge calls are `0`.

If pass, classify:

```text
AP_OPENAI_W2_CANARY_READY_FOR_FULL_FAMILY_RUN
```

Stop before full AP.

## Fail Rules

Fail and preserve the generated run folder if any of the following occurs:

- Unrecovered transport failure.
- Gov parse/content failure.
- Worker parse/content failure.
- Verdict failure.
- Leakage.
- Packet drift.
- Incomplete calls.
- Solo or judge call appears.

Do not repair silently. Do not rerun automatically.

## Safety Note

Do not paste provider keys into chat. Run only in an authorized local shell/environment where exporting the frozen AP canary packet/prompt content to xAI, OpenAI, and MiniMax is permitted.
