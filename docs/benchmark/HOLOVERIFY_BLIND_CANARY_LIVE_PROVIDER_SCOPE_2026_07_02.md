# HoloVerify Blind Canary Live Provider Scope

Status: `PRE_PROVIDER_APPROVAL_SCOPE_ONLY`

Date: 2026-07-02

Provider calls made by this scope document: `0`

Judge calls made by this scope document: `0`

## Purpose

Define the exact provider scope for the first live 20-packet HoloVerify blind
canary. This is approved by Fable only as a runtime-firewall test. It is not a
benchmark result, not an error-rate claim, and not an architecture-advantage
claim.

Live execution remains forbidden until Taylor explicitly approves this exact
scope.

## Committed Firewall Package

- Commit: `55d5877fe4cd2b4157691bdc54772e5bf09ecf04`
- Runtime manifest:
  `docs/benchmark/holoverify_blind_canary_runtime_manifest_2026_07_02.json`
- Runtime manifest SHA-256:
  `b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7`
- Post-hoc scoring map:
  `docs/benchmark/holoverify_blind_canary_scoring_map_2026_07_02.json`
- Post-hoc scoring map SHA-256:
  `5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b`
- Final read-only gate:
  `docs/benchmark/FABLE_CANARY_GATE_RECORD_2026_07_02.md`

## Scope

- Packets: `20`
- Calls per packet: `5`
- Total expected provider calls: `100`
- Solo calls: `0`
- Judge calls: `0`
- Provider retries: only transport retries allowed under existing transport
  policy; no content, parse, verdict, or schema retry.
- Runtime inputs: runtime manifest plus opaque runtime payload files only.
- Scoring map: forbidden during live execution; may be loaded only after trace
  freeze.

## Exact Roster

| Slot | Role | Provider | Model | Expected calls |
| --- | --- | --- | --- | ---: |
| `W1` | worker / source boundary mapper | `xai` | `grok-3-mini` | 20 |
| `G1` | Gov / control router | `minimax` | `MiniMax-M2.5-highspeed` | 20 |
| `W2` | worker / adversarial scope challenger | `openai` | `gpt-5.4-mini` | 20 |
| `G2` | Gov / control router | `minimax` | `MiniMax-M2.5-highspeed` | 20 |
| `W3` | worker / final compiler | `minimax` | `MiniMax-M2.5-highspeed` | 20 |

Provider totals:

- `xai`: `20`
- `openai`: `20`
- `minimax`: `60`

## Required Environment Variables

Report only `PRESENT` or `MISSING`; never print key values.

- `XAI_API_KEY`
- `OPENAI_API_KEY`
- `MINIMAX_API_KEY`
- Optional: `MINIMAX_BASE_URL` if overriding `https://api.minimax.chat/v1`

## Preflight Requirements

Before any provider call:

- Confirm `git rev-parse HEAD` equals
  `55d5877fe4cd2b4157691bdc54772e5bf09ecf04` or explicitly record a newer
  approved commit.
- Confirm runtime manifest hash equals
  `b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7`.
- Confirm post-hoc scoring map hash equals
  `5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b`.
- Confirm runtime manifest has `runtime_consumable=true`.
- Confirm runtime manifest contains only opaque runtime IDs and payload refs.
- Confirm no runtime prompt contains legacy packet IDs, `packet_truth`,
  `legacy_truth`, sibling truth, answer keys, `knew_terms`, `allow_rule`, or
  `esc_rule`.
- Confirm scoring map is not loaded by live executor before trace freeze.
- Confirm model roster exactly matches the table above.
- Confirm expected provider calls equals `100`.
- Confirm solo and judge calls are disabled.

## Stop Conditions

Stop immediately and preserve the run as invalid if any of the following occur:

- Any model substitution is needed.
- Any provider key is missing.
- Any provider call fails unrecovered.
- Runtime manifest hash mismatch.
- Runtime prompt/payload leakage is detected.
- Scoring map is accessed before trace freeze.
- Any content, parse, verdict, schema, or Gov-baton failure would require a
  retry.
- Observed call count differs from `100`.
- Any solo or judge call is attempted.

## Post-Run Handling

After the 100-call live trace completes:

1. Freeze raw trace and provider metadata.
2. Write `TRACE_CALLS.jsonl`.
3. Write `blind_canary_runtime_results.json`.
4. Only after trace freeze, load the post-hoc scoring map.
5. Produce local post-hoc scoring/audit.
6. Report this only as a blind runtime-firewall result.

Forbidden after the run unless separately approved:

- no judges
- no solo baselines
- no public benchmark claim
- no FP/FN or error-rate claim
- no architecture-advantage claim
- no rerun or repair unless the run is explicitly classified and preserved

## Exact Approval Sentence

Taylor must approve with this exact scope before any provider calls:

```text
I approve live provider execution for HOLOVERIFY_BLIND_CANARY_20PKT_RUNTIME_FIREWALL_V0 using commit 55d5877fe4cd2b4157691bdc54772e5bf09ecf04, runtime manifest b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7, and exactly 100 provider calls: W1 xai/grok-3-mini x20, G1 minimax/MiniMax-M2.5-highspeed x20, W2 openai/gpt-5.4-mini x20, G2 minimax/MiniMax-M2.5-highspeed x20, W3 minimax/MiniMax-M2.5-highspeed x20. No judges, no solo, no scoring map before trace freeze, no substitutions, no public claims.
```
