# HoloVerify Architecture Story Audit

Date: 2026-07-05

Callsign: HoloArchitecture

Status: `RECOMMENDATION_ARTIFACT_NO_PROVIDER`

Audience: Taylor and HoloOps

This artifact explains, in plain English, what HoloVerify adds beyond a solo model. No providers, Holo live, solo, Gov, or judges were run. No public site files were edited.

## What HoloVerify Is

HoloVerify is a governed decision architecture for high-stakes action-boundary questions.

It is not just "a better prompt" and not just "more models voting." It is a way to force an AI system to answer a narrower question:

Can this action proceed now, using only the visible source records?

The thesis is simple: models are useful for analysis, extraction, summarization, and option generation. They are too brittle to be trusted as the final execution gate for payments, access grants, contract approvals, treatment activation, legal release, or other irreversible actions.

HoloVerify adds structure around the models: separate worker and Gov turns, source-boundary discipline, deterministic gates, blocker ledgers, frozen traces, and post-hoc scoring. The point is not that models stop being fallible. The point is that failures become visible, preserved, and patchable at the mechanism level.

## The Action Boundary

The action boundary is the exact line between "we can discuss this" and "we may execute this now."

Examples:

- Procurement: may we create, change, approve, or pay this vendor, purchase order, payment rail, or release request now?
- Legal: may we sign, release, settle, disclose, waive, or rely on this legal authority now?
- Finance: may we move money, recognize revenue, change bank details, approve an expense, or close a financial control now?
- Clinical: may we activate treatment, start a protocol, administer medication, release a result, or rely on clinical clearance now?
- Security: may we grant access, change a privileged role, disable a control, execute containment, or act on an incident now?
- Contracts: may we bind the company to this clause, renewal, amendment, order, discount, termination, or approval now?

In each case, the decision is not "does the action sound reasonable?" The decision is "do the visible source records close the exact boundary before execution?"

## Why Solo AI Is Not Enough

Solo models fail in ways that look small in a demo and dangerous in production.

- False allow / underblock: the model says "go ahead" when a required approval, scope, amount, identity, timing, or authority field is missing.
- False escalation / overblock: the model blocks a valid action because the action sounds sensitive, even though the records close the boundary.
- Parse/admissibility brittleness: the model gives an answer in the wrong shape, omits required fields, or returns prose that cannot be safely consumed by a control system.
- Inconsistent reasoning across vendors: different model families reach different answers or rely on different facts for the same packet.
- Equal verdicts for unequal reasons: two models may both say `ALLOW`, but one relied on the right source and the other guessed from tone, urgency, or adjacent authority.

That last point matters. A verdict alone is not enough. The system needs to know whether the answer came from source-grounded closure or from a plausible-sounding shortcut.

## Why 90-96% Is Not Good Enough

In a chatbot, 90-96% can feel impressive. At an action boundary, it is not enough.

If an AI gate is wrong 4-10 times per 100 high-stakes decisions, that can mean:

- Payments released to the wrong account or without the required payment-rail authority.
- Vendor-master changes approved from a plausible request instead of current source records.
- Treatment or protocol activation started from scheduling or triage evidence that does not authorize treatment.
- Contract changes treated as binding even though the required clause, signer, scope, or approval is missing.
- Privileged access granted from a ticket that names a role but not the right tenant, environment, asset, or approval.

The problem is not that a model is useless. The problem is that "usually right" is not a sufficient final gate when the cost of the miss is high and the action may be hard to reverse.

## What Changes When Holo Is Added

HoloVerify adds decision controls around the model layer.

- Structured worker/Gov turns: workers produce constrained artifacts; Gov routes the next turn and carries bounded state forward.
- Source-boundary discipline: the system keeps asking whether the visible sources close the exact requested action boundary.
- Deterministic gates: known source-field checks can fail closed before prose or majority consensus can launder the mistake.
- Blocker ledgers: once a source-grounded blocker appears, later turns must preserve it or close it with specific source fields.
- Post-hoc traceability: prompts, outputs, trace files, provider calls, and scoring are preserved so an auditor can reconstruct what happened.
- Failure preservation and patch regression: failed runs are not erased. Failure classes are named, converted into mechanism-level gates where possible, then rerun under bounded labels.

This is closer to a surgical timeout than a debate club. A skilled surgeon matters, but the safety system also requires patient identity checks, site marking, allergy checks, instrument counts, role separation, and a written record. HoloVerify treats the model as one participant inside a controlled procedure, not as the whole safety system.

## How To Describe Patching

Safe language:

We discovered failure classes, converted them into mechanism-level gates, preserved the failed evidence, and reran bounded validation lanes to check whether the mechanism repaired that class.

Unsafe shorthand:

We tuned to the test.

The distinction is important. A benchmark-tuned system memorizes answers. A mechanism-patched system learns a general control rule, such as "an add-on activation needs matching add-on authority scope" or "a prior blocker cannot disappear unless visible source fields close it."

The claim must stay bounded to the lane that was tested. A patch-validation pass can show that a particular failure class was repaired under the tested conditions. It does not prove universal safety.

## Unsafe Language

Do not say:

- HoloVerify is production-safe.
- HoloVerify is universally superior to solo models.
- HoloVerify has solved all action-boundary risk.
- HoloVerify proves global FNR or FPR reduction from internal selected lanes.
- V6 proves FP precision or broad benchmark superiority.
- The old `614` and current `blind-120` evidence can be combined into one public denominator.
- Patch-validation evidence is public benchmark evidence.

## Claim Boundary

Current safe framing:

HoloVerify is an architecture for testing whether governed, source-bound, traceable AI procedures can reduce known solo-model failure classes at high-stakes action boundaries.

Current public denominator remains `blind-120` only. The old `614` is stale / historical unless re-admitted under current rules. V6 Tier 3 and broader V6 work are internal selected-lane or internal validation evidence, not public benchmark claims, not global FNR/FPR claims, not FP precision evidence, and not general model-superiority evidence.

## Recommendation

Use this story for HoloOps and Taylor alignment before editing public pages.

The public version should keep the same spine:

1. Models are useful but brittle as final action gates.
2. The action boundary is the exact execution question.
3. Solo models fail by underblocking, overblocking, formatting badly, and reasoning inconsistently.
4. HoloVerify adds governed structure, deterministic gates, ledgers, and traceability.
5. Patching means mechanism repair under bounded claims, not answer memorization.
6. The current claim boundary remains conservative.
