# HoloVerify Blind Runner V0 - Fable Third Block Repair Report

Status: LOCAL_NO_PROVIDER_REPAIR_COMPLETE

Date: 2026-07-02

Provider calls: `0`

Judge calls: `0`

## Scope

This report addresses Fable's third `BLOCK_CANARY` review. No live canary was
run. No providers, judges, or frozen benchmark scoring calls were used.

## Repairs

| Blocker | Status | Repair |
| --- | --- | --- |
| B1 public "private" salt | repaired | `build_blind_canary_manifest_2026_07_02.py` now generates the runtime salt with `secrets.token_hex(32)`. The salt is stored only in the post-hoc scoring map. The runtime manifest receives no salt, bank hash, seed material, truth, legacy IDs, or scoring rows. |
| B2 no live execution harness | repaired | `holoverify_blind_runner_v0.run_blind_runtime_manifest` now loads the runtime manifest, loads opaque runtime payloads, calls injected transport for W1/G1/W2/G2/W3, and writes trace/results. T5 includes a filesystem-isolation shim that fails on any read outside the runtime manifest and opaque payload files, and any write outside the output directory. |
| B3 missing import-closure scan | repaired | `blind_lane_suite.static_guards` now follows repo-local imports from the registered runner and scans the full import closure for truth reachability. T2 fails if the registered runner or its local imports touch truth fields, sibling-suffix verdict derivation, or known answer-conditioned repair paths. |

## Regenerated Package

- Audit manifest: `docs/benchmark/holoverify_blind_canary_manifest_2026_07_02.json`
- Runtime manifest: `docs/benchmark/holoverify_blind_canary_runtime_manifest_2026_07_02.json`
- Post-hoc scoring map: `docs/benchmark/holoverify_blind_canary_scoring_map_2026_07_02.json`
- Runtime payload dir: `docs/benchmark/holoverify_blind_canary_runtime_payloads_2026_07_02/`
- Prompt fixtures: `docs/benchmark/blind_lane_fixture_prompts_2026_07_02/prompts/`

Hashes:

- Audit manifest SHA-256: `fa6a32cde377ca4d32387fae697b9a11b07fb977de4ff95572ee306c3147adcb`
- Runtime manifest SHA-256: `b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7`
- Post-hoc scoring map SHA-256: `5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b`

Runtime ordering:

- Truth sequence after opaque-ID sort: `EAEEAEEEAAAAEAEAEAEA`
- Adjacent sibling pairs in runtime order: `1`

## Validation

Py compile: PASS

Firewall suite:

```text
31 passed in 1.04s
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

New checks added:

- Public bank-hash salt recipe cannot reconstruct the private runtime salt.
- Registered runner import closure has no detected truth reachability.
- Runtime executor can read only the runtime manifest and opaque runtime payload files.
- Runtime executor can write only to the output directory.
- Runtime executor produces the expected `100` transport calls over `20` canary packets under injected transport.

## Boundary

This repair does not produce benchmark evidence. It only repairs the no-provider
blind firewall and prepares the package for another read-only adversarial review.

No live canary should run until the current package receives an explicit
`PASS_TO_CANARY`.
