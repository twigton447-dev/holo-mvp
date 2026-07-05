# HoloVerify Blind Runner V0 No-Provider Proof

Status: LOCAL_NO_PROVIDER_FIREWALL_PASS

Date: 2026-07-02

Provider calls: `0`

Judge calls: `0`

## What This Proves

The first no-provider blind HoloVerify runner prototype is registered against
Fable's T1-T7 firewall suite and passes all currently implemented checks.

This is not a live benchmark result. It is not an error-rate claim. It means the
fixture runner can build prompts, gates, artifacts, selector output, and retry
metadata without a detected answer-key channel under the current tests.

## Bound Artifacts

- Runner module: `holoverify_blind_runner_v0`
- Prompt directory: `docs/benchmark/blind_lane_fixture_prompts_2026_07_02/prompts`
- Canary manifest: `docs/benchmark/holoverify_blind_canary_manifest_2026_07_02.json`
- Spec: `docs/benchmark/HOLOVERIFY_BLIND_GATE_REPLICATION_SPEC_2026_07_02.md`

## Test Result

```text
31 passed, 0 skipped, 0 failed
```

Command:

```bash
BLIND_RUNNER_MODULE=holoverify_blind_runner_v0 \
BLIND_LANE_PROMPTS_DIR=docs/benchmark/blind_lane_fixture_prompts_2026_07_02/prompts \
python3 -B -m pytest -q -rs \
  tests/test_blind_lane_t1_id_channel.py \
  tests/test_blind_lane_t2_poisoned_spec.py \
  tests/test_blind_lane_t3_hash_chain.py \
  tests/test_blind_lane_t4_selector_sweep.py \
  tests/test_blind_lane_t5_canary_skew.py \
  tests/test_blind_lane_t6_budget_parity.py \
  tests/test_blind_lane_t7_claim_lint.py
```

## Key Checks

Prompt scan:

- Prompt files scanned: `100`
- Suffix-channel hits: `0`
- Deterministic truth-token hits: `0`

Static guard:

- Runner findings: `[]`
- Runner import-closure findings: `[]`

Canary manifest:

- Seed: `derived_from_bank_hash_no_author_seed`
- Frozen bank: `docs/benchmark/holoverify_blind_canary_bank_2026_07_02.json`
- Bank hash seed: `a686aaf1eb4bb7e7ec49a82fbae540b8bdb78a3569e4f100bdb15ac6ddb303e7`
- Pairs: `10`
- Packets: `20`
- Legacy ALLOW-side IDs: `10`
- Legacy ESCALATE-side IDs: `10`
- Bank first-turn correctness: `0.9043887147335423`
- Sample first-turn correctness: `0.9`
- One-sided binomial p-value: `0.7018792921880527`
- Skew violation: `false`
- Runtime truth sequence after opaque-ID sort: `EAEEAEEEAAAAEAEAEAEA`
- Adjacent sibling pairs in runtime order: `1`

Manifest split:

- Runtime manifest: `docs/benchmark/holoverify_blind_canary_runtime_manifest_2026_07_02.json`
- Post-hoc scoring map: `docs/benchmark/holoverify_blind_canary_scoring_map_2026_07_02.json`
- Runtime manifest SHA-256: `b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7`
- Post-hoc scoring map SHA-256: `5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b`
- Private salt source: build-time entropy via `secrets.token_hex(32)`, stored only in the post-hoc scoring map.

Live executor firewall:

- Executor surface: `holoverify_blind_runner_v0.run_blind_runtime_manifest`
- Runtime reads allowed in fixture test: runtime manifest plus opaque runtime payload files only.
- Runtime writes allowed in fixture test: output directory only.
- Expected canary calls under injected transport: `100` over `20` packets.

## Remaining Boundary

This is still not a live benchmark result. Before live calls, Fable or another
adversarial reviewer should inspect the runner, executor, prompt fixtures,
manifest, and T1-T7 output for remaining truth channels or reward-hacking paths.
