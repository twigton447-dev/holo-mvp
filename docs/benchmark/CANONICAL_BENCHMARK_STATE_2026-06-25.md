# Canonical Benchmark State - 2026-06-25

This note is the control checkpoint for the consolidation thread. It is not a benchmark result, score update, or authorization to start new packets.

## Git State

- Checkout: `/Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001`
- Branch: `holochat-4dna-foundation-001`
- HEAD: `c93855400da62a1b4efb5662cf71fa01456ec794`
- Git repair completed: the checkout `.git` pointer now targets the existing worktree admin dir under `/Users/taylorwigton/Desktop/holo-mvp/.git/worktrees/holo-mvp-holochat-4dna-foundation-001`.
- `git status --short --branch` now works from this checkout.
- Worktree is not clean. Existing dirt remains intentionally untouched:
  - `chat_engine.py`
  - `docs/whitepaper.md`
  - `frontend/benchmark.html`
  - `frontend/chat.html`
  - `frontend/whitepaper.html`
  - `holo_state.py`
  - `llm_adapters.py`
  - `tests/test_holochat_runtime_routing.py`
  - `tests/test_holochat_web_checked.py`
  - `docs/benchmark/APGOV_SHORT_LAYER_ISOLATION_001.md`

## Locked Architecture Profile

Source of lock: operator instruction in the consolidation thread on 2026-06-25.

- Active architecture profile: `frontier_holo_optimized_opus_gpt55_v1`
- Builder alignment: `patent_aligned_v4`
- Registry mode: `full_registry`
- Governor lane: `HoloGov-B`

This checkout does not yet expose these exact profile strings as a single discoverable runtime profile. Until that mapping is made explicit, treat the profile above as the canonical operator lock, not as proof that every runtime entrypoint has been wired to one profile constant.

## HoloBrain Memory Doctrine

- Source of truth: `holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md`
- Version: `0.1`
- Status: `locked`
- Effective date: `2026-06-25`
- Scope: HoloGov-C, HoloGov-B, and HoloGov-V use the shared HoloBrain framework with lane-specific fidelity rules.
- Locked principle: HoloGov-B and HoloGov-V are near-lossless at the reference and audit layer, not at the prompt-injection layer.
- Change rule: future modifications to the doctrine must create a new version or be explicitly approved by the operator.
- Future extraction note: HoloBrain should eventually extract structured learning from prior HoloGov-B and HoloGov-V tests as `case_experience` objects, settled decisions, failure patterns, successful resolutions, and artifact references, but not raw trace dumps by default.

## HoloBrain Maintenance Roster

- Source of truth: `holobrain/memory/HoloBrainMaintenanceRoster_v0.1.md`
- Version: `0.1`
- Status: `locked`
- Effective date: `2026-06-25`
- Governing doctrine: `holobrain/memory/HoloGov_Memory_Doctrine_v0.1.md`
- Scope: HoloScribe, HoloPrune, HoloThread, HoloSentinel, HoloScope, and HoloLedger are HoloBrain maintenance agents that may prepare memory changes but may not silently rewrite truth.
- Change rule: future modifications to the roster must create a new version or be explicitly approved by the operator.

## HoloBrain Daily Operations Policy

- Source of truth: `holobrain/operations/HoloBrain_Daily_Operations_Policy_v0.1.md`
- Version: `0.1`
- Status: `locked`
- Effective date: `2026-06-25`
- Scope: benchmark execution is governed by the locked daily operations policy.
- Operating rule: if the daily checklist is not completed, no benchmark execution may run that day.
- Change rule: future modifications to the operations policy must create a new version or be explicitly approved by the operator.

## Prepared

- HoloBuild package imports under the repo venv.
- HoloBuild CLI is reachable and exposes offline control commands including `lint`, `status`, `freeze`, and `authorize-final`.
- HoloBuild live-run dashboard controls remain guarded by tests that require live runs to be disabled by default.
- HoloVerify/Holo Engine boundary language is present in the Holo context test surface.
- Holo state and context tests pass under the repo venv.

## Actually Run In This Consolidation

- No new packets.
- No live provider calls.
- No new benchmark runs.
- No Judge, scoring, unblinding, freezing, or leaderboard movement.
- Offline checks only:
  - `./venv/bin/python -B -c "import holo_builder.builder, holo_builder.lint, holo_builder.freeze, holo_context, holo_state; print('venv_offline_imports=OK')"`
  - `./venv/bin/python -B -m holo_builder.builder lint --help`
  - `./venv/bin/python -B -m holo_builder.builder status`
  - `./venv/bin/python -B -m pytest tests/test_holobrain_dashboard.py::test_holobuild_endpoint_requires_auth tests/test_holobrain_dashboard.py::test_holobuild_live_run_endpoint_is_disabled_by_default tests/test_holo_context.py tests/test_holo_state.py`

## Offline Verification Results

- Repo venv Python: `Python 3.11.15`
- Offline imports: PASS
- HoloBuild CLI help: PASS
- HoloBuild global status probe: USAGE-ONLY, `builder status` requires a specific result path.
- Narrow pytest slice: PASS, `17 passed`, `2 warnings`

## Score-Valid

- No score-valid benchmark result was produced in this consolidation.
- The current score-valid set remains whatever was already frozen and documented before this checkpoint.
- Any prepared specs, UI controls, or passing offline tests are readiness evidence only. They are not benchmark proof.

## Blocked Or Not Yet Proven

- Worktree cleanup is not complete because pre-existing source/doc changes remain and have not been classified or staged.
- System `python3` is Python 3.9.6 and is not suitable for current code that uses `Path | None` style type hints. Use `./venv/bin/python` for checks in this checkout.
- A direct HoloBuild lint attempt on `holo_builder/specs/AP-BEC-PAYCHNG-001_spec.json` failed because `builder lint` expects a packet JSON, not a build spec. This is a command-target mismatch, not proof that HoloBuild is broken.
- A direct HoloBuild status attempt without a result path failed by usage contract because `builder status` is result-scoped. This is a command-target mismatch, not proof that HoloBuild is broken.
- The locked architecture profile is operator-canonical but not yet represented as one explicit in-repo profile constant or manifest in this checkout.
- Full HoloBuild and HoloVerify functional proof remains blocked until the operator explicitly authorizes packet/run execution.

## Stop Rule

Do not start new packets, live runs, provider calls, freezing, judging, scoring, unblinding, or benchmark expansion until:

1. The existing dirty worktree files are classified.
2. The locked profile is represented in a repo-backed profile manifest or equivalent source of truth.
3. The operator explicitly authorizes the next execution lane.
