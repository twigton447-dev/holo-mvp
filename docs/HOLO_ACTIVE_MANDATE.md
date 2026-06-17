# Holo Active Mandate

Status: Active  
Scope: HoloEvidence / HoloBuild / HoloVerify benchmark work  
Repo: `/Users/taylorwigton/CascadeProjects/holo-mvp`

This is the operating mission control file. It is not marketing copy.

## Co Re-Read Rule

Before every HoloEvidence / HoloBuild / HoloVerify task:

```bash
cat docs/HOLO_ACTIVE_MANDATE.md
```

For long tasks:

Re-read this mandate every 5 minutes or at each checkpoint, commit, or scope transition, whichever comes first.

If the task starts drifting away from the mandate, stop and report.

## Current Mission

Rob's current bar is:

```text
statistically meaningful sample size
half ALLOW
half ESCALATE
```

The target benchmark shape is:

```text
100 evidence-grade packets
50 ALLOW
50 ESCALATE
50 sibling-pair families
each family = one ALLOW sibling + one ESCALATE sibling
same action boundary
same artifact structure where possible
one material evidence delta
```

The current priority is automation and disciplined promotion into the balanced 100-packet benchmark factory, not random live runs or one-off packet craft.

## Evidence Pipeline

Every packet that counts must move through:

```text
draft
-> prefreeze review
-> freeze manifest
-> Taylor explicit freeze approval
-> frozen/hash-locked packet
-> ledger/accounting
-> dry-run contract
-> live trace only with explicit approval and local Taylor execution when required
-> Judge
-> autopsy every judged loss
-> patch decision
-> regression test
-> validation
-> scorecard
```

No shortcuts.

## Loss Loop

Every judged loss gets:

```text
autopsy -> patch decision -> regression test -> validation -> ledger/report entry
```

Losses are not just recorded. They are the improvement loop.

## Current Known State

### HBB-BEC-001

State: frozen, ledgered, live traced, judged, autopsied, patched, regression protected.

- ALLOW sibling: truth `ALLOW`, HoloGov `WRONG`, failure mode `trigger-vs-completion confusion`.
- ESCALATE sibling: truth `ESCALATE`, HoloGov `KNEW`, success mode `caught callback provenance failure`.

Proof-credit note: existing / judged / loss patched / needs post-patch rerun before `proof_credit_ready`.

### HBB-BEC-002

State: frozen, ledgered, dry-run passed, live traced, judged, loss autopsied, patched, regression protected.

- ALLOW sibling: HoloGov `ALLOW`, Judge `ALLOW`, no loss.
- ESCALATE sibling: HoloGov `ALLOW`, Judge `ESCALATE`, missed-risk loss.
- Failure mode: callback-source provenance not decisive enough.
- Patch: portal/change-request/invoice/submitted-contact `number_source` is decisive `ESCALATE` provenance.

Proof-credit note: existing / judged / loss patched / needs post-patch rerun before `proof_credit_ready`.

## Core Lessons

```text
trigger != blocker
completed scrutiny != unresolved risk
pre-change vendor-master callback source = compliant
portal/change-request/invoice/submitted-contact callback source = noncompliant
completed downstream controls do not cure bad callback-source provenance
```

## Model Doctrine

HoloBuild uses frontier-only committed defaults:

```text
gpt-5.4
claude-sonnet-4-6
gemini-2.5-pro
```

4DNA mini lane is separate benchmark/runtime infrastructure:

```text
gpt-4o-mini
grok-3-mini
gemini-2.5-flash-lite
MiniMax-Text-01
Haiku available in pool, excluded in seed447 roster
```

Do not confuse HoloBuild with the mini benchmark runner.

## Live Call Boundary

```text
Do not run live provider calls from Co.
Do not create traces unless explicitly instructed and allowed by environment.
If provider transmission is required, prepare a local Terminal runbook for Taylor instead.
Do not route around provider-transmission boundaries.
```

## Current Next Strategic Work

```text
Build the balanced 100-packet benchmark factory manifest.
Classify/promote packet families toward 50 ALLOW + 50 ESCALATE.
Do not claim 261 benchmark-grade packets.
Current checkout inventory showed 49 packet-like files, 165 historical ledger rows, and 70 unique latest ledger scenarios.
Historical rows are scout material unless promoted through the current evidence pipeline.
```

Current sequence:

```text
1. Balanced 100-packet factory scaffold: DONE
2. Active mandate docs: NEXT
3. Batch 001 generation: after mandate
```

No more drifting around individual packets without the 100-packet factory map.
