# AP OpenAI-W2 Full Holo External Execution Handoff

Date: 2026-06-29

Classification: `AP_OPENAI_W2_FULL_HOLO_EXTERNAL_EXECUTION_HANDOFF`

Status: `READY_FOR_AUTHORIZED_LOCAL_SHELL_EXECUTION`

## Purpose

Run the full AP / procurement OpenAI-W2 Holo family outside Codex because Codex cannot export frozen private benchmark prompts to external providers under the active tenant policy. This is an execution handoff, not a benchmark result.

The 1-pair AP OpenAI-W2 canary passed and was committed as:

```text
65d9d9f2ef24a509522036342684806b1637e561
```

Canary run:

```text
docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2/run_20260629T164305Z
```

Canary status:

```text
AP_OPENAI_W2_CANARY_READY_FOR_FULL_FAMILY_RUN
```

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

The external full-family wrapper is:

```text
/private/tmp/run_ap_openai_w2_holo_policy_v1.py
```

The wrapper writes a fresh timestamped run folder under:

```text
docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_live_runs_openai_w2/
```

The commands below intentionally pin the wrapper's expected execution HEAD in memory to the successful canary evidence commit `65d9d9f2ef24a509522036342684806b1637e561`. Do not run from a different HEAD unless a new handoff is registered.

## Required Lineage

| Layer | Commit |
| --- | --- |
| Packet freeze | `de22377` |
| OpenAI-W2 protocol | `5064777` |
| Invalid-run hardening | `5d365d` |
| Transport policy | `69cdaea` |
| Worker contract hardening | `afdda17` |
| Compact worker verification | `57e5ce6` |
| Gov v2 | `51e4fcf` |
| Gov placeholder fix | `4ae402f` |
| External canary handoff | `abf7613` |
| Successful canary evidence | `65d9d9f` |

Required execution HEAD:

```text
65d9d9f2ef24a509522036342684806b1637e561
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

Run this before the live full-family run. It performs local checks only and should not call providers.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 - <<'PY'
import importlib.util
import json
from pathlib import Path

EXPECTED_HEAD = "65d9d9f2ef24a509522036342684806b1637e561"
LINEAGE = {
    "packet_freeze": "de22377be8175d04078ba6c70f1fd35222e9f572",
    "openai_w2_protocol": "50647772a80437096a943850d522bf18ca0d58e2",
    "invalid_run_hardening": "5d365d480bb574fb51f8bccb6ff6399b13303b78",
    "transport_policy": "69cdaea584f0a546a119a508da4487c27f789136",
    "worker_contract_hardening": "afdda17cf00647ae672c8bd8d6cdb300e5d7f322",
    "compact_worker_verification": "57e5ce6e648d2d170ec1d3ffedba4ccdf0597e91",
    "gov_v2": "51e4fcf",
    "gov_placeholder_fix": "4ae402f06d47f7e839de1aa4f8c2f68d88cf9a5c",
    "external_canary_handoff": "abf76131199123d62773a3417a5c98a79e25ffe8",
    "successful_canary_evidence": EXPECTED_HEAD,
}

p = Path("/private/tmp/run_ap_openai_w2_holo_policy_v1.py")
if not p.exists():
    raise SystemExit(f"missing external wrapper: {p}")
spec = importlib.util.spec_from_file_location("ap_openai_w2_full_handoff", p)
m = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)
m.EXPECTED_HEAD = EXPECTED_HEAD
m.LINEAGE_COMMITS.update(LINEAGE)
manifest = m.validate_pre_live()
print(json.dumps({
    "preflight": "PASS",
    "execution_head": EXPECTED_HEAD,
    "current_head": m.AP.current_head(),
    "freeze_root": manifest["freeze_root"],
    "result": manifest["result"],
    "w2_model": manifest["runner_binding"]["actual_w2_model"],
    "w2_provider": manifest["runner_binding"]["actual_w2_provider"],
    "expected_counts": manifest["expected_counts"],
    "pre_live_contract_assertions": manifest["pre_live_contract_assertions"],
    "providers_called": manifest["providers_called"],
    "lineage_commits": manifest["lineage_commits"],
}, indent=2, sort_keys=True))
PY
```

Expected preflight highlights:

- `preflight: PASS`
- `current_head: 65d9d9f2ef24a509522036342684806b1637e561`
- `freeze_root: 5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- `result: AP_OPENAI_W2_READY_FOR_FULL_HOLO_RUN`
- `w2_provider: openai`
- `w2_model: gpt-5.4-mini`
- `expected_counts.holo_calls: 200`
- `expected_counts.solo_calls: 0`
- `expected_counts.judge_calls: 0`
- `providers_called: 0`

## Exact Live Full-Holo Command

Run this only in an authorized local shell/environment.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 - <<'PY'
import importlib.util
from pathlib import Path

EXPECTED_HEAD = "65d9d9f2ef24a509522036342684806b1637e561"
LINEAGE = {
    "packet_freeze": "de22377be8175d04078ba6c70f1fd35222e9f572",
    "openai_w2_protocol": "50647772a80437096a943850d522bf18ca0d58e2",
    "invalid_run_hardening": "5d365d480bb574fb51f8bccb6ff6399b13303b78",
    "transport_policy": "69cdaea584f0a546a119a508da4487c27f789136",
    "worker_contract_hardening": "afdda17cf00647ae672c8bd8d6cdb300e5d7f322",
    "compact_worker_verification": "57e5ce6e648d2d170ec1d3ffedba4ccdf0597e91",
    "gov_v2": "51e4fcf",
    "gov_placeholder_fix": "4ae402f06d47f7e839de1aa4f8c2f68d88cf9a5c",
    "external_canary_handoff": "abf76131199123d62773a3417a5c98a79e25ffe8",
    "successful_canary_evidence": EXPECTED_HEAD,
}

p = Path("/private/tmp/run_ap_openai_w2_holo_policy_v1.py")
if not p.exists():
    raise SystemExit(f"missing external wrapper: {p}")
spec = importlib.util.spec_from_file_location("ap_openai_w2_full_live", p)
m = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(m)
m.EXPECTED_HEAD = EXPECTED_HEAD
m.LINEAGE_COMMITS.update(LINEAGE)
raise SystemExit(m.main())
PY
```

If the command exits nonzero, preserve the generated run folder. Do not rerun automatically.

## Exact Post-Run Audit Command

Run this after the full-Holo command completes.

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
    "expected_provider_calls": summary.get("expected_provider_calls"),
    "packet_count": summary.get("packet_count"),
    "valid_pairs": summary.get("valid_pairs"),
    "worker_calls": summary.get("worker_calls"),
    "gov_calls": summary.get("gov_calls"),
    "solo_calls": summary.get("solo_calls"),
    "judge_calls": summary.get("judge_calls"),
    "provider_failures": len(summary.get("provider_failures") or []),
    "transport_recovered_call_count": summary.get("transport_recovered_call_count"),
    "root_failure": summary.get("root_failure"),
    "lock_validation": lock.get("validation_status"),
    "lock_root_signature": lock.get("root_signature"),
    "leakage_status": leak.get("status"),
    "trace_rows": len(rows),
    "worker_rows": len(worker_rows),
    "gov_rows": len(gov_rows),
    "assertions": assertions,
}
print(json.dumps(report, indent=2, sort_keys=True))
failures = []
if summary.get("provider_calls") != 200:
    failures.append("provider_calls_not_200")
if len(rows) != 200:
    failures.append("trace_rows_not_200")
if summary.get("packet_count") != 40:
    failures.append("packet_count_not_40")
if summary.get("valid_pairs") != 20:
    failures.append("valid_pairs_not_20")
if summary.get("solo_calls") != 0:
    failures.append("solo_calls_not_0")
if summary.get("judge_calls") != 0:
    failures.append("judge_calls_not_0")
if summary.get("provider_failures"):
    failures.append("provider_failures_present")
if leak.get("status") != "PASS":
    failures.append("leakage_not_pass")
if lock.get("validation_status") != "PASS":
    failures.append("lock_not_pass")
if assertions.get("result") != "AP_OPENAI_W2_HOLO_FROZEN_READY_FOR_SOLO_BASELINE":
    failures.append("readiness_result_not_ready_for_solo")
for key, value in assertions.items():
    if key not in {"classification", "result"} and value != "PASS":
        failures.append(f"assertion_failed:{key}")
if failures:
    raise SystemExit("POST_RUN_AUDIT_FAIL:" + ",".join(failures))
PY
```

## Expected Outputs

The full-Holo run folder should contain:

- `live_summary.md`
- `live_results.json`
- `TRACE_CALLS.jsonl`
- `LOCK_MANIFEST.json`
- `LOCK_VALIDATION.json`
- `AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT.md`
- `AP_OPENAI_W2_HOLO_NO_LEAKAGE_AUDIT.json`
- `AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS.md`
- `AP_OPENAI_W2_HOLO_READINESS_ASSERTIONS.json`
- prompt refs under `prompts/`
- worker and Gov artifacts under `artifacts/`

## Pass Rules

Pass only if all of the following are true:

- `40` packets complete.
- `20` pairs complete.
- Expected `200` Holo calls complete.
- No unrecovered provider failures.
- Gov v2 parses on every Gov turn.
- Worker compact parses on every worker turn.
- No leakage.
- Packet identity matches freeze.
- Final verdicts are correct.
- Solo calls are `0`.
- Judge calls are `0`.

If pass, classify:

```text
AP_OPENAI_W2_FULL_HOLO_FROZEN_READY_FOR_SOLO_BASELINE
```

Then stop before solo baseline.

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
- Any commerce or IT lane starts.

Do not repair silently. Do not rerun automatically.

## Safety Note

Do not paste provider keys into chat. Run only in an authorized local shell/environment where exporting the frozen AP full-family packet/prompt content to xAI, OpenAI, and MiniMax is permitted.

Codex must not execute this live handoff because it would export frozen private benchmark prompts to external providers.
