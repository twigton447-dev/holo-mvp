# AP OpenAI-W2 Roster Variant Registration

Variant: `AP_OPENAI_W2_ROSTER_VARIANT_2026_06_29`

Classification: `PRE_REGISTERED_ROSTER_VARIANT_NO_LIVE_RUN`

This file registers a new AP/procurement roster variant. It does not run providers, Holo, solo, or judges.

## Original Lane Status

The original AP replication lane remains blocked, not failed.

- Original blocker classification: `AP_ORIGINAL_ROSTER_BLOCKED_BY_GEMINI_503`
- Required original Worker 2: `google/gemini-2.5-flash-lite`
- Failure mode: repeated provider-side HTTP `503 Service Unavailable`
- Preserved failed attempts: 3
- Fallback/substitution under original protocol: forbidden
- Evidence interpretation: no AP Holo quality signal, no comparative result, no solo authorization

## Reason for Variant

The variant exists only because the original required Worker 2 provider was unavailable during live attempts. The variant is a new pre-registered roster, not a repair of the original Gemini lane and not proof credit for the original protocol.

## Frozen Packet Bank

- Source commit: `de22377be8175d04078ba6c70f1fd35222e9f572`
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- Family: `HV-AP-REP-2026-06-29`
- Packets: 40
- Pairs: 20
- Truth balance: 20 `ALLOW`, 20 `ESCALATE`
- Packet hash validation: `PASS`
- Prompt hash validation: `PASS`

No packet edits or prompt edits are allowed for this variant.

## New Holo Roster

| Slot | Provider / Model | Role |
| --- | --- | --- |
| W1 | `xai/grok-3-mini` | Worker 1 |
| G1 | `minimax/MiniMax-M2.5-highspeed` | Gov |
| W2 | `openai/gpt-5.4-mini` | Worker 2 replacement |
| G2 | `minimax/MiniMax-M2.5-highspeed` | Gov |
| W3 | `minimax/MiniMax-M2.5-highspeed` | Worker 3 |

Preferred W2 replacement: `openai/gpt-5.4-mini`

Fallback only if unavailable in a later provider-availability check: `openai/gpt-4.1-mini`

Availability note: `openai/gpt-5.4-mini` is declared as the intended W2 model ID for this no-live registration. It has not been provider-verified in this registration because provider calls are forbidden for this step.

Do not use nicknames such as `GPT-5.3 Spark` unless an exact provider model ID is verified first.

## Protocol Delta From Original AP Lane

Same protocol as the original AP lane except Worker 2 provider/model:

- Original W2: `google/gemini-2.5-flash-lite`
- Variant W2: `openai/gpt-5.4-mini`

All other protocol boundaries remain:

- AP family only
- Same frozen AP packet bank
- No packet edits
- No prompt edits
- No answer-key leakage
- No judges
- No commerce/IT
- No fallback/substitution unless a new variant is separately registered
- Gov does not choose models
- Gov remains `minimax/MiniMax-M2.5-highspeed`

## Solo Baseline Rule

If this variant later completes a valid Holo freeze, the solo baseline must use the same three model families/models as the variant:

- `xai/grok-3-mini`
- `openai/gpt-5.4-mini`
- `minimax/MiniMax-M2.5-highspeed`

If `openai/gpt-5.4-mini` is unavailable and the variant is explicitly re-registered to use `openai/gpt-4.1-mini`, then the solo baseline must use that same replacement model.

Solo remains forbidden until a valid AP Holo freeze exists for this variant.

## Registration Validation

- Packet hashes still match freeze: `PASS`
- Prompt hashes still match freeze: `PASS`
- Model roster declared: `PASS`
- Providers called during registration: `0`
- Judges called during registration: `0`
- Live Holo runs during registration: `0`
- Live solo runs during registration: `0`

## Next Allowed Step

Before any live Holo run for this variant, perform an explicit provider availability check for the declared W2 model ID using a harmless non-benchmark prompt and no packet content.

If `openai/gpt-5.4-mini` is unavailable, do not silently substitute. Either stop, or explicitly register the fallback variant using `openai/gpt-4.1-mini`.
