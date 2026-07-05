# D11-Lock Form Actuation Wiring

Date: 2026-06-27

Classification: `D11_LOCK_FORM_ACTUATION_WIRING`

## Purpose

This note records the local-only wiring step after the D12 regression autopsy.

The locked lesson remains:

`Gov diagnosis without deterministic actuation is insufficient for hard admissibility gates.`

## Provider-Free Actuator

The provider-free actuator lives at:

- `benchmark_form_actuator.py`

It does not judge quality and does not rewrite artifact substance. It computes:

- current word count
- allowed word band
- target word count
- minimum expansion or compression needed to enter band
- required section presence
- per-section min/target/max quotas
- blocked moves
- final-worker form instruction

## Runtime Wiring

The D10-D12 live runner copy patched for the next local test is:

- `/private/tmp/d11_lock_5packet_d10_d12_live_runner.py`

The wiring adds:

1. Import of `benchmark_form_actuator.py` from the workspace.
2. `LOCAL_FORM_ACTUATION_TURN_*.json` after every Holo worker artifact gate.
3. `deterministic_form_actuation` embedded into the next Gov baton.
4. A `DETERMINISTIC FORM ACTUATION BATON` prompt block before `FULL LATEST GOV BATON`.
5. Gov-lens fields for deterministic form defect, current words, and target words.

This preserves the Gov-sandwich order:

1. `GOV ROUTING LENS`
2. `STATE BRIEF`
3. `DETERMINISTIC FORM ACTUATION BATON`
4. `FULL LATEST GOV BATON`
5. `CURRENT TURN COMMAND`

The full latest Gov baton still remains immediately before the current turn command. The deterministic form baton is also embedded inside the full Gov baton so the final action instruction is not diluted.

## What This Is Not

This is not a provider run.

This is not a judge call.

This is not a deterministic content rescue compiler.

This is not permission to weaken local gates.

The worker must still generate the artifact. If it ignores the form actuator and misses the hard band, the lane remains fail-closed or must enter a separately logged deterministic normalization step.

## Local Verification

Local verification completed without provider calls:

- `python3 -m py_compile /private/tmp/d11_lock_5packet_d10_d12_live_runner.py benchmark_form_actuator.py`
- import-level smoke of `/private/tmp/d11_lock_5packet_d10_d12_live_runner.py`
- fake-packet prompt construction smoke proving the deterministic form baton appears before `FULL LATEST GOV BATON`, and `FULL LATEST GOV BATON` appears before `CURRENT TURN COMMAND`

