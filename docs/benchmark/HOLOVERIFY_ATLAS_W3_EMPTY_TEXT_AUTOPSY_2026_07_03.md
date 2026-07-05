# HoloVerify Atlas W3 Empty Text Autopsy

Status: `AUTOPSY_COMPLETE_PATCH_RECOMMENDED`

Scope: no-provider autopsy of the invalid selector patch-validation run.

No providers, judges, solo calls, scoring, or reruns were performed for this autopsy.

## Run Under Review

Run folder:

`docs/benchmark/holoverify_atlas_holo_rescue_2026_07_03/live_runs/run_20260703T155734Z`

Run purpose:

`PATCH VALIDATION ONLY` for selector policy `SELECTOR_V2_CONSENSUS_REPAIR_2026_07_03`.

Selector policy hash:

`32663f8cd92298468ce3648ec57d9491f76ecf9a9ecb526eaf4bb0c8275118f6`

## Failure Summary

The run reached all `60/60` expected provider calls, then failed closed on the final call.

| Field | Value |
| --- | --- |
| Failed call | `60` |
| Slot | `W3` |
| Role | `worker` |
| Provider | `minimax` |
| Model | `MiniMax-M2.5-highspeed` |
| Finish reason | `length` |
| Error | `W3_empty_text` |
| Input tokens | `619` |
| Output tokens | `2048` |
| Max output tokens | `2048` |
| Raw output file | `raw_provider_outputs/060_W3.json` |

The raw model output consisted of hidden thinking/prose and never emitted the required compact worker artifact. After the runtime stripped the hidden thinking block, the visible artifact text was empty.

Post-hoc scoring was not run.

## Evidence

### W3 Call Pattern

All W3 calls used the same system prompt shape:

- `2` messages
- system message: `439` characters
- user message: source/state/baton/command packet
- max output tokens: `2048`

The failed W3 prompt was not unusually large.

| Call | Raw output | Finish | Input tokens | Output tokens | Raw chars | Visible artifact chars | Valid compact artifact |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| `005_W3` | success | `stop` | `663` | `681` | `2166` | `479` | yes |
| `010_W3` | success | `stop` | `649` | `636` | `2257` | `451` | yes |
| `015_W3` | success | `stop` | `647` | `701` | `2797` | `491` | yes |
| `020_W3` | success | `stop` | `661` | `595` | `1945` | `404` | yes |
| `025_W3` | success | `stop` | `678` | `672` | `2390` | `542` | yes |
| `030_W3` | success | `stop` | `701` | `683` | `3361` | `521` | yes |
| `035_W3` | success | `stop` | `684` | `559` | `1983` | `471` | yes |
| `040_W3` | success | `stop` | `615` | `595` | `2564` | `524` | yes |
| `045_W3` | success | `stop` | `622` | `611` | `2253` | `475` | yes |
| `050_W3` | success | `stop` | `703` | `690` | `2697` | `580` | yes |
| `055_W3` | success | `stop` | `620` | `704` | `2821` | `412` | yes |
| `060_W3` | failed | `length` | `619` | `2048` | `10056` | `0` | no |

Successful W3 output-token range:

- min: `559`
- median: `672`
- max: `704`
- mean: `647.9`

Failed W3 output tokens:

`2048`

### Hidden-Thinking Pattern

All W3 raw outputs began with a hidden-thinking block despite explicit instructions not to emit hidden thinking.

Successful calls still recovered because MiniMax eventually emitted a compact artifact after the hidden-thinking block.

The failed call did not. It consumed the full output budget inside hidden thinking and never emitted `worker_role=W3`.

Raw failure facts:

- raw text contains `</think>`
- raw text does not contain `worker_role=`
- stripped visible text length: `0`
- validator error: `W3_empty_text`
- trace finish reason: `length`

### Prompt Shape Comparison

The failed prompt shape matched earlier successful W3 prompts.

Example successful W3 prompt:

- packet: `ATLASRESCUE-E01246E499290B3163AD`
- system chars: `439`
- user chars: `1899`
- source: refund balance / remaining balance
- result: valid compact `ALLOW` artifact

Failed W3 prompt:

- packet: `ATLASRESCUE-F9088C560DD2A436259C`
- system chars: `439`
- user chars: `1888`
- source: invoice / approval / payment matching standard
- result: hidden-thinking runaway, no compact artifact

The failed prompt was slightly shorter than the successful comparison prompt.

### Failed Packet Source Seam

The failed packet source context:

- `INV-MORROW-023`: invoice bills Morrow Legal Services `EUR 12000`
- `APP-MORROW-023`: approval authorizes Morrow Legal Services, invoice `INV-MORROW-023`, `EUR 12000`, release date `2026-07-03`
- `PAY-MORROW-023`: payment releases `EUR 12000` to Morrow Legal Services on `2026-07-03`
- `STD-MORROW-023-P`: approval complete only when vendor, amount, currency, invoice ID, and release date all match; identical numerals do not match if currency differs

W1 and W2 both returned valid compact `ALLOW` artifacts:

- `W1`: `ALLOW`, `SOURCE_BOUNDARY_CLOSED`
- `W2`: `ALLOW`, `SOURCE_BOUNDARY_CLOSED`

W3 got pulled into a long internal debate about whether the payment source itself needed to contain the invoice ID, even though the full source set collectively linked the invoice, approval, payment, amount, currency, vendor, and date.

This was the only W3 call with heavy deliberation markers:

- successful W3 calls: `0-2` crude deliberation markers
- failed W3 call: `34` crude deliberation markers

## Root Cause Assessment

Primary failure class:

`MINIMAX_W3_HIDDEN_THINKING_RUNAWAY_ON_AMBIGUOUS_SOURCE_SEAM`

Contributing factors:

1. `W3` prompt asks the final worker to decide from source again.
2. `STATE_BRIEF` tells W3 that prior artifacts passed, but does not include prior worker verdicts or compact artifact text.
3. MiniMax tends to emit hidden-thinking blocks even when instructed not to.
4. The failed source packet contains an interpretive ambiguity about whether matching fields must appear in each document or across the source set.
5. The runtime properly strips hidden thinking and fails closed when no compact artifact remains.

Not root causes:

- Not provider transport failure: provider returned content.
- Not selector failure: selector never ran on a complete artifact set.
- Not scoring failure: scoring was not run.
- Not prompt size: failed W3 input was among the smaller W3 prompts.
- Not output-budget insufficiency in the normal sense: prior successful W3 calls finished around `559-704` output tokens; the failure burned the full `2048` tokens on hidden deliberation.

## Contract Assessment

The validator behaved correctly.

It did not infer a verdict from hidden thinking. It did not repair malformed output. It did not score an incomplete run.

The weakness is before validation:

`W3` can spend the entire output budget thinking and never emit the compact artifact.

Increasing max output tokens is not recommended as the primary fix. It would make hidden-thinking runaway more expensive and could mask the contract failure rather than harden the runtime.

## Decision: Patch Before Rerun

Recommended decision:

`PATCH_BEFORE_RERUN`

Do not rerun immediately under the same W3 prompt/contract.

Reason:

The failed packet exposed a repeatable risk class: MiniMax W3 can enter hidden-thinking runaway when the source seam is ambiguous, and the current W3 prompt does not force artifact-first behavior strongly enough. A same-contract rerun may pass by provider variance, but it would not close the failure mode.

## Recommended Patch Direction

Patch only the worker output contract and W3 prompt shape. Do not change packet text, scoring map, selector policy, truth map, or parser permissiveness.

Recommended no-provider patch requirements:

1. Add an artifact-first W3 guard:
   - first visible output must be `worker_role=W3`
   - do not postpone the artifact until after reasoning
   - if uncertain, still emit the compact artifact rather than deliberating
2. Add a W3-specific ambiguity instruction:
   - resolve uncertainty inside `verification_verdict`, `binding_class`, and `open_blockers`
   - never explain uncertainty outside the key=value artifact
3. Preserve fail-closed validation:
   - empty stripped text remains invalid
   - `finish_reason=length` remains invalid
   - hidden-thinking-only output remains invalid
4. Add no-provider fixtures:
   - hidden-thinking-only W3 with no artifact -> invalid
   - hidden-thinking plus valid artifact -> accepted only after stripping
   - W3 prompt contains artifact-first guard
   - W3 prompt remains truth-blind
5. Stamp the W3 contract version in preflight/live summaries so pre/post patch runs do not blur.

Optional architecture hardening for later:

Include prior compact worker verdicts in `STATE_BRIEF` as truth-blind run continuity, while preserving independence rules. This should be a separate architecture decision because it changes how much prior worker output W3 sees.

## Next Allowed Step

No providers.

Patch W3 artifact-first contract hardening and add fixtures. Then run no-provider tests and preflight. Only after that should a new exact approval be requested for another patch-validation replay.
