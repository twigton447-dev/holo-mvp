# External Judge Readiness

Status: `READY_PENDING_EXPLICIT_EXTERNAL_TRANSFER_APPROVAL`

Run lock status: `FROZEN_HASH_LOCKED_PENDING_EXTERNAL_JUDGES`

Current run-lock root signature: see `RUN_LOCK_MANIFEST.json` and `RUN_LOCK_VALIDATION.json`. This value changes whenever readiness or judgment artifacts are added and the run is re-locked.

Packet freeze root signature: `47434052ed594ed65734e1e964434ae984a17777607fc72ad1c6424dd4de83f6`

## What Is Ready

The benchmark run is ready for judge-only continuation:

- Holo full traces are already frozen.
- Solo one-shot trace is already frozen.
- Judge packet is already generated.
- Local Codex trace judgment is already saved.
- KNEW-only pass rule is locked.
- No Solo rerun is required or permitted.
- No Holo rerun is required or permitted.

## Why The External Judge Step Is Blocked

The external judge packet would send the following materials to configured external judge providers:

- frozen source packets;
- Solo one-shot outputs;
- Holo selected artifacts;
- Holo trace summaries;
- local eligibility warnings;
- the KNEW-only judge schema.

That external transfer requires explicit post-risk user approval before provider calls can run.

## Approval Text

Use this exact approval if external judges should run:

`Approved: send the frozen 10-packet benchmark judge packet, including source packets, Solo outputs, Holo selected artifacts, and trace summaries, to the configured external judge providers for KNEW-only adjudication. Do not rerun Solo. Do not rerun Holo. After judges complete, re-lock the run with judge outputs included.`

## Judge-Only Command

After explicit approval, run:

```bash
set -a; source .env; set +a; python3 -B docs/benchmark/run_hard_allow_fp_5pair_solo_and_knew_judges_2026_06_28.py \
  --judge-existing-run-dir docs/benchmark/hard_allow_fp_5pair_solo_fullholo_knew_benchmark_2026-06-28/run_20260629T000225Z \
  --allow-external-judge-transfer
```

Then run:

```bash
python3 -B docs/benchmark/lock_solo_fullholo_knew_benchmark_run_2026_06_28.py
```
