# AP Solo Triage Smoke External Execution Handoff

Date: 2026-06-29

Classification: `AP_SOLO_TRIAGE_SMOKE_CODEX_PROVIDER_EXPORT_BLOCKED`

Status: `READY_FOR_AUTHORIZED_LOCAL_SHELL_EXECUTION`

## Purpose

Run the AP-only weak-mini solo smoke outside Codex because Codex cannot export frozen private benchmark packets/prompts to external providers from this environment.

This smoke determines whether the AP frozen packet family shows early solo-collapse signal before spending a 120-call AP solo batch or a 200-call AP Holo run.

## Codex Boundary Result

Codex completed the local preflight and attempted to start the 12-call AP solo smoke. The provider run was blocked before execution by tenant policy.

Codex provider calls made:

```text
0
```

This is not a benchmark failure, not a provider failure, and not evidence about AP packet difficulty.

## Required Runtime

Runner commit:

```text
66e15f3db82fa7560cd7ec42715f5c646fb1ee6b
```

Handoff commit:

```text
9144296996d8f641aaca714a2ce62c9021a92023
```

Freeze root:

```text
5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7
```

## Scope

- Family: `HV-AP-REP-2026-06-29`
- Pairs: `2`
- Packets: `4`
- Solo models per packet: `3`
- Expected provider calls: `12`
- Holo calls: `0`
- Gov calls: `0`
- Judge calls: `0`
- Commerce/IT calls: `0`

## Roster

| Slot | Provider/model |
| --- | --- |
| Solo A | `xai/grok-3-mini` |
| Solo B | `openai/gpt-4o-mini` |
| Solo C | `minimax/MiniMax-M2.5-highspeed` |

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
git merge-base --is-ancestor 9144296996d8f641aaca714a2ce62c9021a92023 "$(git rev-parse HEAD)"
python3 -B docs/benchmark/run_replication_3family_solo_triage_2026_06_29.py --preflight --family HV-AP-REP-2026-06-29 --pair-limit 2 --batch-label ap_smoke_2pair_12call
```

Preflight must report:

- `status: PASS`
- `packet_count: 4`
- `pair_count: 2`
- `expected_provider_calls: 12`
- `expected_gov_calls: 0`
- `expected_holo_calls: 0`
- `expected_judge_calls: 0`
- `provider_calls_made_by_preflight: 0`
- `judge_calls_made_by_preflight: 0`
- no prompt leakage rows
- no Gemini in triage roster
- OpenAI slot is `gpt-4o-mini`

## Exact Live Smoke Command

Run this only in an authorized local shell/environment.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor 9144296996d8f641aaca714a2ce62c9021a92023 "$(git rev-parse HEAD)"
set -a; source .env; set +a
python3 -B docs/benchmark/run_replication_3family_solo_triage_2026_06_29.py --run-live --family HV-AP-REP-2026-06-29 --pair-limit 2 --batch-label ap_smoke_2pair_12call
```

If the command exits nonzero, preserve the generated run folder. Do not rerun automatically.

## Exact Post-Run Audit Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
BATCH_LABEL=ap_smoke_2pair_12call
RUN_DIR="$(ls -td docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29/solo_triage_3mini/${BATCH_LABEL}/run_* | head -1)"
python3 - "$RUN_DIR" <<'PY'
import json
import sys
from pathlib import Path

run = Path(sys.argv[1])
summary = json.loads((run / "solo_triage_results.json").read_text())
lock = json.loads((run / "SOLO_TRIAGE_LOCK_VALIDATION.json").read_text())
report = {
    "run_dir": str(run),
    "classification": summary.get("classification"),
    "provider_calls": summary.get("provider_calls"),
    "expected_provider_calls": summary.get("expected_provider_calls"),
    "provider_failures": len(summary.get("provider_failures") or []),
    "gov_calls": summary.get("gov_calls"),
    "holo_calls": summary.get("holo_calls"),
    "judge_calls": summary.get("judge_calls"),
    "freeze_root": summary.get("freeze_root"),
    "lock_validation": lock.get("validation_status"),
    "top_holo_targets": len(summary.get("top_holo_targets") or []),
    "by_family": summary.get("by_family"),
    "by_model": summary.get("by_model"),
    "top_holo_targets_preview": (summary.get("top_holo_targets") or [])[:5],
}
print(json.dumps(report, indent=2, sort_keys=True))
PY
```

## Expected Outputs

Run folder:

```text
docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29/solo_triage_3mini/ap_smoke_2pair_12call/run_*
```

Expected files:

- `SOLO_TRIAGE_PREFLIGHT.json`
- `SOLO_TRIAGE_TRACE.jsonl`
- `solo_triage_results.json`
- `solo_triage_summary.md`
- `SOLO_TRIAGE_LOCK_MANIFEST.json`
- `SOLO_TRIAGE_LOCK_VALIDATION.json`
- `prompts/`

## Report Required After Smoke

- calls completed
- provider failures
- parse/admissibility failures
- verdict correctness by model
- any all-three-solo-fail packets
- any all-three-solo-correct packets
- hard ALLOW false-positive failures
- hard ESCALATE false-negative failures
- leakage status
- packet identity status

## Classification Rule

If AP smoke shows meaningful solo failure:

```text
AP_SOLO_TRIAGE_READY_FOR_FULL_BATCH
```

If AP smoke is mostly solo-correct:

```text
AP_SMOKE_SOLO_ROBUST_OR_PACKET_TOO_EASY
```

If the smoke is robust/easy, do not run full AP yet. Consider commerce smoke next.
