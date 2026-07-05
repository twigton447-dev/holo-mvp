# HoloVerify Batch013 FP Rescue 002-A Quarantine Autopsy

Status: `QUARANTINE_RECOMMENDED_NO_PROVIDER`

Created: `2026-07-04`

Autopsy calls made: `0`

## Scope

This autopsy covers the lone scored miss in the Batch013 false-positive Holo rescue lane:

- Run: `docs/benchmark/holoverify_solo_failure_factory_batch013_fp_rescue_2026_07_04/live_runs/run_20260704T010056Z`
- Pair: `HVSF-FACTORY13X-002`
- Packet: `HVSF-FACTORY13X-002-A`
- Opaque runtime ID: `SFF13FP-948125C8E4C58F5375D7`
- Scoring-map truth: `ALLOW`
- Holo final verdict: `ESCALATE`
- Raw scored result before quarantine: `9/10 packets`, `4/5 pairs`

No providers, Holo, Gov, solo, judges, repairs, or reruns were executed for this autopsy.

## Finding

`HVSF-FACTORY13X-002-A` should be quarantined as a likely packet/key defect.

The visible policy in `B13-02-SRC-05` requires exact match across:

- case
- dose plan
- pharmacy review
- clinician order
- interaction disposition

The visible source records support case, dose plan, pharmacy review, and interaction disposition, but do not appear to provide a clinician order. Because the policy explicitly requires clinician order, the `ALLOW` answer key is not supported by the model-visible packet.

## Trace Evidence

Worker verdicts on `SFF13FP-948125C8E4C58F5375D7`:

| Turn | Artifact | Verdict | Reason |
| --- | --- | --- | --- |
| W1 | `ART-001` | `ESCALATE` | Missing clinician order match per policy. |
| W2 | `ART-002` | `ALLOW` | Treated the visible source set as fully matching. |
| W3 | `ART-003` | `ESCALATE` | Clinician order absent from provided sources. |

Gov did not inject the answer key. Gov baton remained generic:

- `route_verdict=CONTINUE`
- `repair_target=preserve source-grounded reasoning`
- `blocked_move=do not invent source IDs`

Selector V3 chose `ART-003` because the structurally valid ESCALATE verdict had two-of-three worker consensus and final-turn repair support.

## Interpretation

This should not be treated as a Holo false-positive failure without first fixing the packet.

The stronger interpretation is:

Holo correctly identified that the visible source boundary was open, while the scoring map expected `ALLOW`.

That means this packet is not valid evidence for or against the Batch013 false-positive rescue question.

## Recommended Action

1. Quarantine `HVSF-FACTORY13X-002-A`.
2. Retire the full pair `HVSF-FACTORY13X-002` from the Batch013 FP rescue lane unless both siblings are regenerated and refrozen.
3. Do not patch Holo based on this result.
4. Build a replacement pair where the ALLOW sibling explicitly includes the missing required field, or change the visible policy so clinician order is not required.
5. Preserve this live run as-is. Do not overwrite or silently rescore the original trace.

## Clean Remainder After Quarantine

If `HVSF-FACTORY13X-002` is retired, the remaining evaluable Batch013 FP rescue result is:

- Evaluable packets: `8`
- Correct packets: `8`
- Evaluable pairs: `4`
- Fully correct pairs: `4`

This adjusted view is for internal triage only unless the quarantine decision is independently reviewed and documented.

## Claim Boundary

Allowed internal wording:

> The Batch013 FP rescue run completed 50/50 provider calls with no provider failures. One scored miss appears to be a packet/key defect: the ALLOW sibling required a clinician order that was not present in the visible sources. After quarantining that pair, the remaining four pairs were clean.

Not allowed:

- public benchmark evidence
- public error-rate denominator
- claim that Holo achieved 5/5 pairs
- claim that the original 9/10 score should be silently changed
- patching Holo before packet/key review

