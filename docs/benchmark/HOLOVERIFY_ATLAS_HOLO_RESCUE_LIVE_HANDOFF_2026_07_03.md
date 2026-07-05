# HoloVerify Atlas Holo Rescue Live Handoff

Status: `READY_FOR_EXPLICIT_PROVIDER_APPROVAL`

This handoff prepares a small Holo rescue test against six Fable-promoted seam pairs. It is directional governance evidence only, not a public error-rate claim.

## Scope

- Pairs: `6`
- Packets: `12`
- Expected provider calls: `60`
- Workers / Gov calls: `36 / 24`
- Solo calls: `0`
- Judge calls: `0`
- Scoring before trace freeze: `FORBIDDEN`
- Substitutions: `FORBIDDEN`

Promotion set:

- `HV-ATLAS-DISC-020`
- `HV-ATLAS-DISC-023`
- `HV-ATLAS-DISC-025`
- `HV-ATLAS-DISC-033`
- `HV-ATLAS-DISC-035`
- `HV-ATLAS-DISC-036`

Original `HV-ATLAS-DISC-034` is excluded. Fixed replacement `036` is included.

## Locked Hashes

- Freeze root: `d4e130d4598963b55e7cc6b708ff6b850a7e14df1a4b2d9bc2b24c3f08fbb7da`
- Runtime manifest: `0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7`
- Scoring map: `70ddcbcf5a32e4c1a75ebef563dd60c0514e3cc40eda90f5653ef80974661e19`

## Roster

- `W1`: `xai/grok-3-mini`
- `G1`: `minimax/MiniMax-M2.5-highspeed`
- `W2`: `openai/gpt-5.4-mini`
- `G2`: `minimax/MiniMax-M2.5-highspeed`
- `W3`: `minimax/MiniMax-M2.5-highspeed`

Gov does not choose models. The run lock fixes the order.

## Validation Already Run

- `py_compile`: `PASS`
- Runtime bank freeze: `PASS`
- Live preflight: `PASS`
- Runtime input leakage: `PASS`
- Prompt probe leakage: `PASS`
- Scoring map absent from live wrapper: `PASS`
- Freeze root matches hash manifest: `PASS`
- Provider calls during this prep: `0`

Preflight artifact:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/preflight_20260703T105015Z/atlas_holo_rescue_live_preflight.json`

## Exact Live Command

Run only after explicit approval:

```bash
cd /Users/taylorwigton/CascadeProjects/holo-mvp-holochat-4dna-foundation-001
set -a; source .env; set +a
python3 -B docs/benchmark/run_holoverify_atlas_holo_rescue_live_2026_07_03.py \
  --run-live \
  --approval-statement "I approve live provider execution for HOLOVERIFY_ATLAS_HOLO_RESCUE_6PAIR_RUNTIME_FIREWALL_V0 using freeze root d4e130d4598963b55e7cc6b708ff6b850a7e14df1a4b2d9bc2b24c3f08fbb7da, runtime manifest 0cd8ab98da5c6a4089279922cf644d3cbcb0820555be65d14f88b68b99f453f7, opaque packet indices 1-12 only, and exactly 60 provider calls: W1 xai/grok-3-mini x12, G1 minimax/MiniMax-M2.5-highspeed x12, W2 openai/gpt-5.4-mini x12, G2 minimax/MiniMax-M2.5-highspeed x12, W3 minimax/MiniMax-M2.5-highspeed x12. No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims."
```

## Post-Freeze Scoring

Only after the live trace freezes:

```bash
python3 -B docs/benchmark/score_holoverify_atlas_holo_rescue_posthoc_2026_07_03.py \
  --run-dir <RUN_DIR>
```

Both siblings per pair must be correct to count the pair as rescued.

## Blind-120 Hard-Seam Filter

The blind-120 solo baseline is now filtered separately:

- Total packets: `120`
- Kept hard-seam packets: `11`
- Excluded all-three-KNEW packets: `109`

Rule: keep only packets where at least one same-model solo one-shot failed. Parse/admissibility failures count as failures.

Filter artifact:

`docs/benchmark/HOLOVERIFY_BLIND_120_SOLO_FAILURE_PACKET_FILTER_2026_07_03.json`
