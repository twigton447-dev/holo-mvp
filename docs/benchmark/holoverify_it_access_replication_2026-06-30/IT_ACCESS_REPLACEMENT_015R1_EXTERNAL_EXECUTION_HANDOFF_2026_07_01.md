# IT Access Replacement 015R1 External Execution Handoff

Created: 2026-07-01

## Purpose

Run the targeted IT Access replacement Holo batch outside Codex in an authorized local shell/environment.

Codex completed harmless readiness checks, but did not run the replacement batch because the live batch sends frozen benchmark packet/prompt content to external providers.

## Scope

- Domain: IT access / permission change controls
- Replacement pair: `HV-ITAC-REP-015R1`
- Replaces retired/quarantined pair: `HV-ITAC-REP-015`
- Packets: 2
- Pairs: 1
- Expected Holo calls: 10
- Solo calls: 0
- Judge calls: 0
- Commerce/AP calls: 0
- Packet edits: forbidden
- Prompt edits: forbidden

## Required Lineage

- Replacement freeze commit: `1b914293`
- Latest readiness/blocker commit before external run: `db1f8332`
- Original 3-family packet freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- Replacement freeze root: `6c61024da5f6c36c1ee5210b95efd1d7a1ed0caff60a11efe0ace1ca1e72dc4e`

## Provider Roster

- W1: `xai/grok-3-mini`
- G1: `minimax/MiniMax-M2.5-highspeed`
- W2: `openai/gpt-5.4-mini`
- G2: `minimax/MiniMax-M2.5-highspeed`
- W3: `minimax/MiniMax-M2.5-highspeed`

## Required Environment

Set provider keys in the local shell environment. Do not paste keys into chat.

Expected environment variables are the same variables used by the runner for:

- xAI
- OpenAI
- MiniMax

Use the repository `.env` only in an authorized local environment.

## Commands

Run from the repository root:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
git merge-base --is-ancestor 1b914293 "$(git rev-parse HEAD)"
git merge-base --is-ancestor db1f8332 "$(git rev-parse HEAD)"
set -a; source .env; set +a
```

Preflight:

```bash
python3 -B docs/benchmark/run_it_access_openai_w2_holo_batched_family_2026_06_30.py \
  --preflight-batch \
  --batch replacement_015r1
```

Fresh harmless readiness gates:

```bash
python3 -B docs/benchmark/run_it_access_openai_w2_holo_batched_family_2026_06_30.py --minimax-health-check

python3 -B docs/benchmark/run_it_access_openai_w2_holo_batched_family_2026_06_30.py --minimax-worker-contract-smoke
```

Targeted replacement batch:

```bash
python3 -B docs/benchmark/run_it_access_openai_w2_holo_batched_family_2026_06_30.py \
  --run-batch \
  --batch replacement_015r1 \
  --require-minimax-health \
  --require-minimax-worker-smoke
```

## Expected Outputs

The successful run should create a folder under:

`docs/benchmark/holoverify_it_access_replication_2026-06-30/holo_live_runs_openai_w2_batched/replacement_015r1/`

Expected artifacts include:

- live summary
- results JSON
- `TRACE_CALLS.jsonl`
- lock manifest
- no-leakage report
- readiness assertions

## Pass Rules

Pass only if:

- 2 packets complete
- 1 pair completes
- 10 expected Holo calls complete
- provider failures unrecovered: 0
- worker compact outputs parse
- Gov micro-batons parse
- deterministic gates present
- final selector present
- no leakage
- packet identity matches replacement freeze root
- both sibling final verdicts are correct
- solo calls: 0
- judge calls: 0

## Fail Rules

Fail closed if:

- transport failure remains unrecovered
- Gov parse/content failure occurs
- worker parse/content failure occurs
- verdict failure occurs
- leakage is detected
- packet drift is detected
- expected calls are incomplete
- solo or judge calls occur

## Reporting

If the run passes, freeze and commit only the replacement run artifacts. Preserve this handoff and all prior invalid/blocker traces.

If the run fails, preserve the failed run exactly as emitted. Do not repair, retry, or substitute inside the same run lineage.
