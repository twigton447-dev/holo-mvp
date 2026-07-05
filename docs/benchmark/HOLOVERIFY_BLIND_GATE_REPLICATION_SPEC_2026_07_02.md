# HoloVerify Blind-Gate Replication Spec

Status: PRE-REGISTERED_NO_PROVIDER_SPEC

Date: 2026-07-02

## Why This Exists

The current governed-runtime HoloVerify lane can use packet truth inside deterministic gates. In particular, the runtime gate can derive the expected verdict from the sibling suffix and can route truth-conditioned repair language such as "potential overblock" or "potential underblock" into the next worker turn.

That is useful for engine hardening. It is not clean enough for a blind production error-rate claim.

The next replication must separate:

- Runtime quality control: schema, source IDs, dependency closure, consistency, no invented evidence.
- Post-hoc scoring: ALLOW/ESCALATE truth, false positives, false negatives, TP/TN.

## Core Rule

During live Holo execution, no runtime component may know the packet truth.

This includes:

- Workers.
- Gov.
- Deterministic gates.
- Final selector.
- State brief.
- Prompt metadata.
- Artifact registry.
- Repair directives.
- Normalization logic.

The answer key may be used only after the run is complete.

## Opaque Runtime Identity

Runtime packet identifiers must be opaque.

Forbidden in model-visible prompts, Gov batons, state briefs, artifact references, and runtime metadata:

- `-A` / `-B` sibling suffixes
- packet IDs that encode truth or sibling role
- target bucket labels
- hard-ALLOW / hard-ESCALATE labels
- answer-key row IDs

The runner may maintain a private post-hoc mapping from opaque runtime ID to frozen packet ID, but that mapping must not enter runtime prompts or gates.

## Runtime Gate Allowed Checks

The blind runtime gate may fail or warn on:

- malformed worker output
- missing required sections
- missing source IDs
- invented source IDs
- malformed Gov baton
- source quote/evidence shape problems
- unresolved dependency not flagged
- contradiction between answer body and chosen verdict
- action boundary not explicitly stated
- missing final recommendation
- unsafe instruction leakage
- raw prompt or answer-key leakage
- final artifact weaker than best prior artifact by blind structural criteria

## Runtime Gate Forbidden Checks

The blind runtime gate must not:

- derive expected verdict from sibling suffix
- compare worker verdict against packet truth
- emit `action_boundary_verdict_mismatch`
- emit "expected ALLOW got ESCALATE"
- emit "expected ESCALATE got ALLOW"
- tell Gov "potential overblock" because the truth is ALLOW
- tell Gov "potential underblock" because the truth is ESCALATE
- expose or consume `knew_terms`, `allow_rule`, `esc_rule`, answer-key terms, target buckets, or packet spec fields that were built from the answer key
- normalize a worker artifact by setting binding class, verdict, final answer, or critical features from suffix-conditioned expected fields
- mutate a worker artifact after the provider returns it
- invalidate a completed run solely because the final verdict is wrong
- select the final artifact using answer-key truth

## Gov Allowed Behavior

Gov may act as a control actuator, but only blind to truth.

Gov may say:

- source evidence appears insufficient
- dependency remains unresolved
- evidence cited does not support conclusion
- final answer is internally inconsistent
- worker failed schema or cited invalid source ID
- worker ignored a prior unresolved dependency
- preserve the best structurally admissible artifact by blind criteria only

Gov may not say:

- this is probably an overblock because the packet is ALLOW
- this is probably an underblock because the packet is ESCALATE
- return ALLOW if the closed boundary is present
- return ESCALATE if the open boundary is present

## Final Selector Rule

The final selector may choose between artifacts only by blind criteria:

- parse validity
- source-ID validity
- dependency coverage
- contradiction-free reasoning
- required section presence
- no leakage
- no invented evidence
- monotonic preservation of blind structural features that are not derived from truth, suffix, target bucket, or expected answer terms

The final selector must not know whether ALLOW or ESCALATE is correct.

## Scoring Rule

After the run is frozen:

1. Load the answer key.
2. Compare final verdict to packet truth.
3. Count wrong final verdicts as errors.
4. Count wrong ALLOW on ESCALATE truth as false negative.
5. Count wrong ESCALATE on ALLOW truth as false positive.
6. Do not invalidate a completed trace because it got the answer wrong.

Only non-content failures invalidate the run:

- provider transport failure after allowed retries
- malformed raw trace
- prompt/packet hash drift
- leakage
- missing required call
- wrong model roster
- parser failure where no admissible final artifact exists

## Required Falsification Tests

1. Static source scan confirms no live runtime file contains suffix-derived expected verdict logic.
2. Static source scan confirms no live runtime file contains truth-conditioned overblock/underblock repair text.
3. Prompt scan confirms no worker/Gov prompt contains expected verdict, packet truth, answer key, target bucket, or sibling truth.
4. Trace scan confirms no `action_boundary_verdict_mismatch` appears before post-hoc scoring.
5. Trace scan confirms no "expected ALLOW got ESCALATE" or "expected ESCALATE got ALLOW" appears before post-hoc scoring.
6. Injected wrong final verdict fixture completes as score error, not invalid-run repair.
7. Final selector fixture cannot choose an artifact by answer-key truth.
8. Post-hoc scorer can reproduce FP/FN/TP/TN from frozen final artifacts only.
9. Truth-invariance fixture: run prompt/gate/baton builders with truth metadata poisoned ALLOW->ESCALATE and ESCALATE->ALLOW; runtime prompts, gates, batons, and selector inputs must be byte-identical.
10. Directive-symmetry fixture: ALLOW and ESCALATE siblings with the same visible source structure must receive symmetric non-directional repair language.
11. Sibling prompt-diff fixture: sibling prompts may differ only in source payload facts, never in ID suffixes, answer labels, target buckets, or answer-derived expected terms.
12. Artifact immutability fixture: provider raw output hash must remain unchanged from provider return through post-hoc scoring.

## Fable Seven-Test Disconfirmation Battery

Failure of any test below blocks the blind-lane claim until repaired and re-swept. Passing all seven tests does not prove reliability; it licenses only this sentence:

> The blind lane, as fixtured, shows no detected truth channel.

| Test | Claim It Tries To Falsify | Executes Against | Falsification Condition | Passing Does Not Show |
| --- | --- | --- | --- | --- |
| T1 ID-channel mutual information | No runtime component receives an identifier from which truth is derivable. | All model-visible message files emitted by blind-runner fixtures, plus baseline census on existing governed-lane prompts. | Any extractable token class maps to truth deterministically or near-deterministically. | Payload content carries no truth signal. |
| T2 poisoned-spec byte-invariance | Runtime behavior is a pure function of model-visible payload and model outputs. | Fixture copies with swapped truth, sentinel `knew_terms`, and inverted `allow_rule` / `esc_rule`. | Any prompt, gate result, baton, selector decision, or trace byte differs; any sentinel appears in runtime output. | Absence of future truth channels or fields added later. |
| T3 artifact provenance hash-chain | The harness never writes into worker artifacts. | Mocked worker artifacts plus static census of governed-lane normalization metadata. | Any hash differs from raw model output, or blind runner reaches artifact-normalization functions. | Artifact truthfulness or quality. |
| T4 selector truth-swap sweep | The final selector chooses by closed-form blind criteria only. | Adversarial artifact fixtures where truth-matching artifacts are structurally weaker. | Selection changes when only truth metadata changes, declared criteria recomputation disagrees, or selection correlates with truth agreement. | Selector criteria are wise or unbiased. |
| T5 canary skew check | The canary was not chosen to be easy. | Committed sampler, published seed, frozen bank hash, and frozen governed-lane traces. | Sample is not exactly reproducible, sampler postdates difficulty artifacts, or sampled first-turn correctness exceeds bank rate beyond tolerance. | The packet bank is representative of real traffic. |
| T6 budget parity replay | The blind lane buys no accuracy through extra attempts. | Frozen governed-lane call/token distributions and blind-runner fixture replays with forced transport failures. | Blind-lane turns, retry caps, or token ceilings exceed the lane it replaces; retries are unlogged or content-triggered. | Parity with solo baselines or correctness of the shared budget. |
| T7 claim-scope lint | No rate claim is derived from the canary. | `frontend/*.html`, public briefs, evidence memos, and CI lint. | Any canary-sized ratio, percentage, or confidence bound appears publicly; any blind-lane rate lacks a lane label; canary lacks stopping rule and full-run size. | Anything about the architecture itself. |

Residual rejection grounds remain even after a clean sweep:

- Corpus curation.
- Payload-content truth signal.
- Model-family effects.
- Distribution comfort.
- Fixture fidelity.
- Run-level survivorship.

## Minimum Replication Shape

Start with a small blind-gate canary before any public claim:

- 20 packets minimum
- balanced ALLOW/ESCALATE
- seeded, pre-registered packet selection before live calls
- same frozen packet bank or a clearly pre-registered subset with opaque runtime IDs
- same model roster as the governed-runtime lane being tested
- comparable budget to the governed-runtime lane being tested
- no judges
- no provider fallback
- answer-key scoring only after trace freeze
- no rate claim from the 20-packet canary; 20/20 is only a structural proof and still leaves a large statistical upper bound

If the canary passes structurally, run a larger blind-gate family.

## Stopping Rule

The first blind-gate canary is pre-registered at exactly 20 packets:

- 10 ALLOW truths and 10 ESCALATE truths
- seeded packet selection before any live calls
- opaque runtime IDs only
- no provider fallback
- no judges
- no answer-key scoring until after trace freeze

Stop the canary immediately and preserve the run as invalid if any of these occur:

- packet or prompt hash drift
- model roster mismatch
- forbidden truth channel detected by T1 through T7
- answer-key field, sibling suffix, target bucket, or expected verdict appears in runtime prompts, gates, Gov baton, artifact registry, or final selector input
- unrecovered provider transport failure
- malformed trace or missing required call
- no admissible final artifact exists because of parse/content failure

If the canary produces a wrong final verdict, do not invalidate or repair the canary. Freeze the trace and count the wrong verdict as a scored error. A wrong `ALLOW` on `ESCALATE` truth is a false negative. A wrong `ESCALATE` on `ALLOW` truth is a false positive.

The canary can only license the structural sentence: "the blind lane, as fixtured, shows no detected truth channel." It cannot license an error-rate claim.

The first blind-gate full run is pre-registered at exactly 120 packets:

- 60 ALLOW truths and 60 ESCALATE truths
- same blind runtime firewall as the canary
- same no-fallback and no-judge policy
- same post-hoc-only scoring rule

The full run must be selected and frozen before live calls. If any runtime truth channel is detected, the full run is invalid for blind proof. If the runtime stays blind but produces wrong final verdicts, those verdicts are counted as errors in the final confusion matrix.

## Claim Boundary

Until this replication is complete, use this language:

> HoloVerify has a counted governed-runtime result across the current packet bank. The current runtime included answer-aware deterministic repair gates, so a blind-gate replication is required before reporting the result as a production error-rate bound.
