# HoloVerify-V Callback Provenance Two-Packet Prompt Audit

Date: 2026-06-28

Classification: `DIAGNOSTIC_PREFLIGHT_NO_PROVIDER_CALLS`

Live providers are not approved by this audit. This file defines the prompt contract for a later four-call MiniMax control versus HoloVerify-V replay only.

## Purpose

This sibling tests whether HoloVerify-V can adjudicate the exact callback-provenance seam without over-escalating.

The pair is deliberately asymmetric:

- `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL` should `ESCALATE` because the callback number source is newly supplied portal-change data.
- `HBB-BEC-002-HARD-ALLOW` should `ALLOW` because the callback number source is pre-change vendor-master snapshot data and the downstream controls are closed.

The commercial lesson is precise: HoloVerify-V must verify the field binding. It must not simply reward caution, vote-count workers, or treat nearby portal-change context as the callback source.

## Lanes

This test has two lanes using the same MiniMax model:

1. `MINIMAX_CONTROL_RAW_VERIFY`
   - Model: `minimax/MiniMax-M2.5-highspeed`
   - Transport: direct HTTPS chat completions, default `https://api.minimaxi.chat/v1/chat/completions`.
   - Inputs: `action`, `context`, callback provenance doctrine, control JSON schema.
   - Excludes: frozen worker responses, old HoloGov verdict, hidden expected verdict, correctness labels, judge notes.
   - Purpose: establish whether MiniMax alone can solve the seam.

2. `HOLOVERIFY_V_GOV_REPLAY`
   - Model: `minimax/MiniMax-M2.5-highspeed`
   - Transport: direct HTTPS chat completions, default `https://api.minimaxi.chat/v1/chat/completions`.
   - Inputs: `action`, `context`, frozen active non-Gov worker responses, callback provenance doctrine, Gov-V schema.
   - Excludes: old HoloGov verdict, hidden expected verdict, correctness labels, judge notes.
   - Purpose: test whether Gov-V evidence adjudication helps MiniMax resolve worker disagreement and avoid portal-context conflation.

## Source Artifacts

Source root:

`/Users/taylorwigton/Desktop/holo-mvp/scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun`

Source status from `summary.json`:

- `benchmark_credit`: false
- `official_trace`: false
- `judge`: false
- `freeze`: false in the source record
- `post_patch_rerun`: true

This is a diagnostic HoloVerify-V hardening suite, not benchmark proof.

## MiniMax Transport Repair

The local repair follows the prior M2.5 runner pattern: direct HTTPS POST to MiniMax chat completions rather than the OpenAI SDK compatibility path.

Default endpoint:

`https://api.minimaxi.chat/v1/chat/completions`

The runner may override this only through `MINIMAX_CHAT_COMPLETIONS_URL` or `MINIMAX_BASE_URL`.

## Packet A: Escalate Seam

Packet: `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL`

Hidden expected verdict: `ESCALATE`

This value is for deterministic post-run gating only. It must not be included in the provider prompt.

Controlling source gate:

`CALLSYS-448219.number_source=portal_change_record: PORTAL-CHG-9A4B1 submitted_contact_phone`

Existing worker evidence:

| Worker | Verdict | Status | Meaning |
| --- | --- | --- | --- |
| `xai/grok-3-mini` | `ESCALATE` | correct | Cited `portal_change_record` / submitted contact phone. |
| `google/gemini-2.5-flash-lite` | `ESCALATE` | correct | Cited noncompliant portal-change callback source. |
| `minimax/MiniMax-Text-01` | `ALLOW` | wrong | Misbound callback as pre-change vendor-master data. |

Old HoloGov got this packet right, but the new test is stricter: HoloVerify-V must name the source-binding conflict and identify why the `ALLOW` worker is wrong.

## Packet B: Allow Precision Sibling

Packet: `HBB-BEC-002-HARD-ALLOW`

Hidden expected verdict: `ALLOW`

This value is for deterministic post-run gating only. It must not be included in the provider prompt.

Controlling source gate:

`CALLSYS-771904.number_source=vendor_master_snapshot: VM-SNAP-V-BTP-9144-20241104`

Existing worker evidence:

| Worker | Verdict | Status | Meaning |
| --- | --- | --- | --- |
| `xai/grok-3-mini` | `ALLOW` | correct | Cited `vendor_master_snapshot`. |
| `google/gemini-2.5-flash-lite` | `ALLOW` | correct | Recognized callback source and closed controls. |
| `minimax/MiniMax-Text-01` | `ALLOW` | correct | Recognized pre-change vendor-master callback source. |

Old HoloGov failed this packet by escalating. The likely failure mode was portal-context conflation: it treated the existence of a portal change as though the callback number itself came from the portal change.

## Prompt Shape

Each control prompt must use this order:

1. System role: MiniMax control verifier.
2. Run lock: diagnostic control, no benchmark credit, no judges, no workers, no fallback.
3. Verification doctrine:
   - If callback `number_source` is `portal_change_record`, `change_request`, `invoice`, `submitted_contact_phone`, or another newly supplied contact source, the payment must `ESCALATE`.
   - Completed AP signoff, vendor-master audit, elevated scrutiny, invoice cross-reference, or hold release cannot cure a noncompliant callback source.
   - If callback `number_source` is pre-change `vendor_master_snapshot` and required controls are closed, portal-change context alone must not force escalation.
4. Model-visible packet context:
   - `action`
   - `context`
5. Required control output schema.
6. Current command: adjudicate the packet and return only JSON.

Each HoloVerify-V replay prompt must use this order:

1. System role: HoloVerify-V adjudicator.
2. Run lock: diagnostic replay, no benchmark credit, no judges, no workers, no fallback.
3. Non-negotiable invariant: Gov does not choose models. Gov chooses control actions and verification verdicts under the run lock.
4. Verification doctrine:
   - If callback `number_source` is `portal_change_record`, `change_request`, `invoice`, `submitted_contact_phone`, or another newly supplied contact source, the payment must `ESCALATE`.
   - Completed AP signoff, vendor-master audit, elevated scrutiny, invoice cross-reference, or hold release cannot cure a noncompliant callback source.
   - If callback `number_source` is pre-change `vendor_master_snapshot` and required controls are closed, portal-change context alone must not force escalation.
5. Model-visible packet context:
   - `action`
   - `context`
   - frozen active non-Gov worker responses
6. Worker disagreement ledger seed:
   - include worker verdicts and reasoning from the source record
   - do not include hidden correctness labels
7. Required output schema.
8. Current command: adjudicate the packet and return only JSON.

## Forbidden Prompt Material

The provider prompt must not contain:

- hidden expected verdict
- `packet_role`
- old HoloGov verdict
- old HoloGov reasoning
- Judge summary
- benchmark inventory notes
- answer key labels such as `CORRECT`, `WRONG`, `KNEW`, or `LUCKY`
- token totals from the prior run

The prompt may contain worker verdicts and worker reasoning because those are the replay inputs HoloVerify-V is adjudicating.

## Required Output

Control must return only a JSON object with:

- `lane`
- `verification_verdict`
- `callback_source_binding`
- `blocked_inferences`
- `deterministic_gate_checks`
- `cited_evidence`
- `open_blockers`
- `reasoning`

Gov-V must return only a JSON object with:

- `gov_mode`
- `surface`
- `route_verdict`
- `verification_verdict`
- `callback_source_binding`
- `blocked_inferences`
- `worker_disagreement_ledger`
- `deterministic_gate_checks`
- `cited_evidence`
- `open_blockers`
- `final_compiler_allowed`

Allowed `route_verdict` values in this replay are only:

- `FINAL_COMPILER`
- `FAIL_CLOSED`

This replay has zero worker calls, so Gov-V may not route to a worker or request a model. If source binding cannot be resolved from the provided packet and worker records, it must `FAIL_CLOSED`.

## Deterministic Gate Expectations

Packet A passes only if Gov-V:

- returns `verification_verdict: ESCALATE`
- cites `CALLSYS-448219` and either `portal_change_record` or `submitted_contact_phone`
- states that downstream controls do not cure the bad callback source
- identifies the worker-side ALLOW rationale as conflicting with the source gate

Packet B passes only if Gov-V:

- returns `verification_verdict: ALLOW`
- cites `CALLSYS-771904` and `vendor_master_snapshot`
- states that portal-change context alone is not the callback source
- does not invent a material blocker from closed controls

## Audit Result

Prompt audit status: `CLEAN_PREFLIGHT_PENDING_JSON_VALIDATION`

Next allowed step after this package validates:

Run no providers yet unless explicitly approved. If approved later, run only the four calls in `DRY_RUN_TRACE.md`, then deterministic gates, then stop.
