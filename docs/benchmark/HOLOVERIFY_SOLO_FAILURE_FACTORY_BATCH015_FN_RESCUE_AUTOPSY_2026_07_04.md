# HoloVerify Batch015 FN Rescue Autopsy

Status: `PRESERVED_FAILED_DIRECTIONAL_RESCUE`
Date: 2026-07-04
Run: `docs/benchmark/holoverify_solo_failure_factory_batch015_fn_rescue_2026_07_04/live_runs/run_20260704T023158Z`

## Bottom Line

The Batch015 false-negative rescue lane was validly executed, but it did not produce a Holo rescue win.

Runtime integrity was clean: 100/100 provider calls completed, zero provider failures, no solo calls, no judges, no substitutions, and the trace froze before posthoc scoring. Post-freeze scoring showed 11/20 packets correct and 1/10 sibling pairs fully correct.

The failure pattern was narrow and important:

- Holo got all 10 ALLOW siblings correct.
- Holo missed 9/10 ESCALATE siblings by selecting ALLOW.
- In every failed ESCALATE sibling, all three worker artifacts were ALLOW.
- The selector mostly selected `ART-001`, but this was not a selector regression: there was usually no dissenting ESCALATE artifact to preserve.

## What Actually Failed

This was primarily a packet/source design failure plus a Gov-actuation weakness, not a provider/runtime failure.

The selected B siblings were scored as ESCALATE, but many were not self-contained enough for a blind model to prove ESCALATE from the visible packet. The B-side records often repeated the same suspicious value across the scoped authority and binding ledger, then said there was no remaining mismatch outside the listed field set. The visible policy usually required exact field match, and those fields did match.

Examples:

- `HVSF-FACTORY15O-001-B`: `clinician_order=CO15-099` appears in both scoped authority and ledger. No visible source says `CO15-099` is invalid for the requested dose plan.
- `HVSF-FACTORY15O-002-B`: `trusted_callback=invoice-footer callback IF15-002` is suspicious, but the policy does not explicitly state that invoice-footer callbacks are not trusted callbacks.
- `HVSF-FACTORY15O-014-B`: `hazmat_review=HZ15-404` appears in both authority and ledger. No visible source states the required review must be a different value.
- `HVSF-FACTORY15O-020-B`: `contract_amendment=AM15-200` appears consistently. The visible policy checks exact field match, not whether `AM15-200` is the correct amendment.

The one B sibling Holo correctly escalated, `HVSF-FACTORY15O-015-B`, used `sanctions_screen=pending`. That is intrinsically source-resolvable: a pending sanctions screen obviously does not close a KYC/onboarding boundary.

## Worker/Gov/Selector Findings

Worker verdict pattern:

- 19/20 packets had unanimous worker ALLOW.
- The only correct ESCALATE packet, `HVSF-FACTORY15O-015-B`, had W1=ESCALATE, W2=ESCALATE, W3=ALLOW.
- 9/10 B siblings failed because W1, W2, and W3 all agreed on ALLOW.

Gov behavior:

- Gov calls parsed successfully.
- All Gov outputs were the same compact status baton: continue, preserve source-grounded reasoning, do not invent source IDs.
- Gov did not perform a substantive adversarial diagnosis of the prior worker artifact.
- Gov did not ask the next worker to test whether repeated field values were actually valid authority values.

Selector behavior:

- Selector V3 was not the primary failure mode.
- For failed B siblings, there was no ESCALATE artifact for the selector to choose.
- The selector did select the 2-of-3 ESCALATE consensus on `HVSF-FACTORY15O-015-B`, which is exactly what it should do under the current policy.

## Classification

Recommended classification:

`VALID_RUNTIME_FAILED_DIRECTIONAL_RESCUE_PACKET_TRUTH_NOT_SUFFICIENTLY_SOURCE_GROUNDED`

Secondary labels:

- `STATIC_GOV_STATUS_BATON_INSUFFICIENT_FOR_FN_RESCUE`
- `WORKER_UNANIMOUS_UNDERBLOCK`
- `B_SIBLING_IMPLICIT_EXPECTED_VALUE_GAP`
- `NOT_PROVIDER_FAILURE`
- `NOT_SELECTOR_REGRESSION`

## What This Result Does And Does Not Support

Supported:

- The Batch015 FN rescue runtime path is operational.
- The blind runtime firewall held.
- Holo did not rescue this selected false-negative set.
- Holo preserved ALLOW precision on the A siblings.
- The B-side seams were too implicit for reliable source-grounded ESCALATE decisions.

Not supported:

- No claim that Holo rescued Batch015 false negatives.
- No public benchmark claim.
- No error-rate denominator.
- No claim that Holo is broadly weak at false negatives.
- No claim that selector V3 caused the miss.

## Engineering Lessons

1. A valid ESCALATE packet must contain a self-contained, source-visible blocker. It cannot depend on knowing that `CO15-099`, `HZ15-404`, or `AM15-200` is wrong unless the packet gives the model a source-grounded way to know that.

2. “Exact field match” is not enough for B siblings. If the defect is that the repeated value is invalid, the policy must define valid values or point to a required independent record.

3. Gov needs a real adversarial actuator for FN lanes. It should challenge “field repetition equals authority closure” and force the next worker to ask: does this value itself satisfy the controlling policy, or is it merely repeated consistently?

4. Deterministic gates should only enforce semantic blockers that are source-visible. They should not smuggle truth, but they can check policy-declared closure states such as `sanctions_screen=clear`, `callback_source=registry`, `scope=single endpoint`, or `amount<=cap including fees`.

5. Batch016 should not reuse Batch015’s “listed fields match” B-pattern unless the packet adds a visible source that makes the listed value insufficient.

## Next Move

Preserve this failed rescue attempt. Do not repair or overwrite it.

For the next solo-failure factory/Holo rescue lane:

- Build B siblings where the blocker is computed or inferred from visible source records.
- Use colder source fragments and a realistic business prompt.
- Keep both siblings plausible.
- Add explicit policy hooks that make the ESCALATE side source-grounded without leaking the answer.
- Upgrade Gov from a static status baton to an adversarial control action that targets the exact failure class.

