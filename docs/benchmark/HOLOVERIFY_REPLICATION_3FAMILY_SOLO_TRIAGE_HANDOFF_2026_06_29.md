# HoloVerify 3-Family Solo Triage Handoff

Date: 2026-06-29

Classification: `HOLOVERIFY_REPLICATION_3FAMILY_SOLO_TRIAGE_HANDOFF`

Status: `READY_FOR_AUTHORIZED_LOCAL_SHELL_EXECUTION`

## Purpose

Run one-shot solo triage over all frozen replication packets before spending any full Holo calls. This answers the seam question first: which AP, agentic-commerce, and IT access sibling pairs actually create solo collapse?

This is not a Holo run and not a judge run.

## Runtime Commit

The triage runner was committed at:

```text
266ffbbb36b4ddf86254fa9fe592b651d782a3fd
```

The local shell should verify that this commit is an ancestor of the current checkout before execution.

## Frozen Packet Bank

Freeze root:

```text
5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7
```

Frozen bank:

```text
docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29
```

Scope:

- `3` families.
- `60` sibling pairs.
- `120` packets.
- `60` ALLOW truths.
- `60` ESCALATE truths.
- `30` hard-ALLOW target pairs.
- `30` hard-ESCALATE target pairs.

Families:

- `HV-AP-REP-2026-06-29`: AP / procurement / vendor-master controls.
- `HV-ACOM-REP-2026-06-29`: Agentic commerce / order execution controls.
- `HV-ITAC-REP-2026-06-29`: IT access / permission change controls.

## Solo Triage Roster

| Slot | Provider/model |
| --- | --- |
| Solo A | `xai/grok-3-mini` |
| Solo B | `openai/gpt-5.4-mini` |
| Solo C | `minimax/MiniMax-M2.5-highspeed` |

Expected calls:

```text
120 packets x 3 solo models = 360 provider calls
```

## Hard Boundaries

Forbidden:

- no Gov
- no Holo state
- no Gov baton
- no artifact registry
- no final selector
- no judges
- no commerce/IT Holo run
- no packet edits
- no prompt edits
- no fallback or substitution

The runner uses the frozen prompt files directly and performs deterministic local audit after each output only.

## Environment Variables

Required for live triage:

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
git merge-base --is-ancestor 266ffbbb36b4ddf86254fa9fe592b651d782a3fd "$(git rev-parse HEAD)"
python3 -B docs/benchmark/run_replication_3family_solo_triage_2026_06_29.py --preflight
```

Preflight must report:

- `status: PASS`
- `packet_count: 120`
- `pair_count: 60`
- `expected_provider_calls: 360`
- `expected_gov_calls: 0`
- `expected_holo_calls: 0`
- `expected_judge_calls: 0`
- `provider_calls_made_by_preflight: 0`
- `judge_calls_made_by_preflight: 0`
- no prompt leakage rows
- no Gemini in triage roster

## Exact Live Triage Command

Run this only in an authorized local shell/environment.

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor 266ffbbb36b4ddf86254fa9fe592b651d782a3fd "$(git rev-parse HEAD)"
set -a; source .env; set +a
python3 -B docs/benchmark/run_replication_3family_solo_triage_2026_06_29.py --run-live
```

If the command exits nonzero, preserve the generated run folder. Do not rerun automatically.

## Exact Post-Run Audit Command

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
RUN_DIR="$(ls -td docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29/solo_triage_3mini/run_* | head -1)"
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
    "gov_calls": summary.get("gov_calls"),
    "holo_calls": summary.get("holo_calls"),
    "judge_calls": summary.get("judge_calls"),
    "provider_failures": len(summary.get("provider_failures") or []),
    "freeze_root": summary.get("freeze_root"),
    "lock_validation": lock.get("validation_status"),
    "top_holo_targets": len(summary.get("top_holo_targets") or []),
    "by_family": summary.get("by_family"),
    "by_model": summary.get("by_model"),
}
print(json.dumps(report, indent=2, sort_keys=True))
PY
```

## Expected Outputs

Run folder:

```text
docs/benchmark/holoverify_replication_packet_freeze_3families_2026-06-29/solo_triage_3mini/run_*
```

Expected files:

- `SOLO_TRIAGE_PREFLIGHT.json`
- `SOLO_TRIAGE_TRACE.jsonl`
- `solo_triage_results.json`
- `solo_triage_summary.md`
- `SOLO_TRIAGE_LOCK_MANIFEST.json`
- `SOLO_TRIAGE_LOCK_VALIDATION.json`
- `prompts/`

## Triage Classes

Pairs are ranked into:

- `ALL_SIX_SOLO_COLLAPSE`: all six one-shots across both siblings are not KNEW/admissible.
- `STRONG_SOLO_COLLAPSE`: four or more not-KNEW outputs, or three or more wrong-verdict outputs.
- `MIXED_SEAM`: at least one solo miss but not enough for strong collapse.
- `NO_SOLO_SEAM`: all six one-shots are KNEW/admissible.
- `INVALID_PAIR_TRACE`: missing calls or provider failure before pair completion.

Holo should only be considered next for `ALL_SIX_SOLO_COLLAPSE` and `STRONG_SOLO_COLLAPSE` pairs.

## Stop Rule

After solo triage completes, stop and inspect the pair rankings. Do not start Holo until the strongest target pairs are selected from the triage output.
