# HoloVerify Atlas Held V5 Exploratory Result

Status: `EXPLORATORY_RUN_COMPLETE`

Created: `2026-07-03T16:48:45Z`

## Scope

This run is fresh exploratory signal only. It is not patch validation, not benchmark evidence, and not a public denominator.

- Lane: `HOLOVERIFY_ATLAS_HELD_V5_EXPLORATORY_3PAIR_RUNTIME_FIREWALL_V0`
- Freeze root: `039a699f9d8c1314472e0e04cae67a8b794ad085cef98bccfd9c42d843efe069`
- Runtime manifest: `b158cb6ed1eecb4bf2d84a7137b124e8cd6e9787713fdaa5105f3679ef889197`
- Run directory: `docs/benchmark/holoverify_atlas_held_v5_exploratory_2026_07_03/live_runs/run_20260703T164532Z`
- Provider calls: `30/30`
- Workers / Gov calls: `18 / 12`
- Judges: `0`
- Solo calls: `0`
- Substitutions: `0`
- Scoring map before trace freeze: `false`

## Result

- Packets correct: `6/6`
- Sibling pairs both correct: `3/3`
- Incorrect packets: `0`
- Runtime firewall: `PASS`

| Pair | Source design | Seam class | A verdict | B verdict | Pair result |
| --- | --- | --- | --- | --- | --- |
| `HV-ATLAS-HELDV5-011` | `V5-11` | Business-day holiday count | `ALLOW` | `ESCALATE` | `PASS` |
| `HV-ATLAS-HELDV5-012` | `V5-12` | Toxic role combination | `ALLOW` | `ESCALATE` | `PASS` |
| `HV-ATLAS-HELDV5-014` | `V5-14` | Composite qty x unit x FX | `ALLOW` | `ESCALATE` | `PASS` |

## Token Totals

- Input tokens: `13,699`
- Output tokens: `8,480`
- Total tokens: `26,525`

By slot:

| Slot | Input | Output | Total |
| --- | ---: | ---: | ---: |
| `W1` | `4,079` | `627` | `9,052` |
| `G1` | `748` | `1,643` | `2,391` |
| `W2` | `3,543` | `731` | `4,274` |
| `G2` | `748` | `1,478` | `2,226` |
| `W3` | `4,581` | `4,001` | `8,582` |

## Trace Binding

- `TRACE_CALLS.jsonl`: `57eba7badef4e2a51ef5386b1feca2874a4fbbf39d19a5acc034f00a37cdd56a`
- `TRACE_PROVIDER_CALLS.jsonl`: `69aaa3b9cae200f21c380fa653d7bcfdc1afab1b86aa033bbc611e5f8c81ec17`
- Runtime results: `7c3203cad014e729d3b3c2a4a11d758d8caed7236264292ebdacc43d9a246f06`
- Live summary: `d4d2d444299eedf91cbe076df4c20558def5f99670faa861c99e031a2f12bdd5`
- Scoring map: `e0d4c785a98fd4387e1d5c20ea7b758ff6ac2518ac1e18ce4ef8a191bc289d10`

## Allowed Language

HoloVerify completed the held V5 exploratory three-pair hop-depth lane. The run completed 30/30 provider calls and scored 6/6 after trace freeze.

## Forbidden Language

Do not describe this as:

- benchmark evidence;
- a public error-rate result;
- an addition to the public denominator;
- proof of general robustness;
- part of the selector/W3 patch-validation result.
