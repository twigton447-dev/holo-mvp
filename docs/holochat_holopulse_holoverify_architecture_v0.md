# HoloPulse and HoloVerify Boundary Contract v0

## Purpose

HoloPersonal and HoloEnterprise are separate scoped HoloBrains. HoloPulse is
the deterministic, typed transfer broker between them. HoloVerify is the
independent backstop for every proposed cross-scope transfer.

This is defense in depth. It is not a claim that HoloGov, a connector, or a
worker model will never make a mistake.

## Runtime flow

```text
source HoloBrain
  -> source HoloGov proposes a typed PulseSignal
  -> HoloPulse allowlist and source policy checks
  -> HoloVerifyPulseGate disposition
  -> target HoloGov admission of an allowed derivative only
  -> HoloAudit receipt and target admission acknowledgement
```

No worker model may directly read the other scope, construct an unrestricted
cross-scope summary, or persist data into the receiving HoloBrain.

## Normal signals

The first policy surface is intentionally small and enum-only:

| Direction | Allowed signal | Allowed values |
| --- | --- | --- |
| Personal to Enterprise | `availability` | `available`, `limited`, `unavailable` |
| Enterprise to Personal | `workload_pressure` | `low`, `moderate`, `high` |
| Enterprise to Personal | `availability` | `available`, `limited`, `unavailable` |

No free text, names, health information, client information, deal terms,
records, attachments, identifiers, or raw model output are normal signals.

## HoloVerify escalation

The deterministic HoloVerifyPulseGate evaluates every proposal. Unknown signal
types, non-normalized values, cross-principal attempts, and sensitive metadata
are blocked. A future higher-risk transfer may be quarantined for a dedicated
HoloVerify review packet, but that review must run inside the source-side
boundary and return only a minimized disposition or derivative.

## Audit receipt

HoloAudit must record the pulse ID, source and destination scope IDs, policy
version, signal type, disposition, a one-way signal hash, timestamp, and target
admission acknowledgement. It must not record raw cross-scope content.

## Current status

`holochat_pulse.py` and `scripts/holochat_holopulse_bug_simulation.py` are
no-provider test components. They are not yet wired into production request
handling or a database receipt store. Runtime integration is gated on successful
staging identity and scope-isolation verification.
