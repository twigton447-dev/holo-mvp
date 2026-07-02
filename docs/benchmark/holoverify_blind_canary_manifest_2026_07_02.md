# HoloVerify Blind Canary Manifest

Status: PRE_REGISTERED_NO_PROVIDER_SELECTION

Seed label: `derived_from_bank_hash_no_author_seed`
Bank hash seed: `a686aaf1eb4bb7e7ec49a82fbae540b8bdb78a3569e4f100bdb15ac6ddb303e7`

Pairs: `10`
Packets: `20`
Legacy ALLOW-side IDs: `10`
Legacy ESCALATE-side IDs: `10`

Runtime rule: live runtime consumes the separate runtime manifest and opaque runtime payloads only. Legacy packet IDs and truths live only in the post-hoc scoring map.

Redraw policy: no redraws are allowed. If skew check fails, the canary remains blocked.

Claim limit: this canary can test the blind runtime firewall only. It cannot support an error-rate claim.

## Skew Check

Bank first-turn rate: `0.9043887147335423`
Sample first-turn rate: `0.9`
One-sided binomial p-value: `0.7018792921880527`
Skew violation: `False`

## Selected Legacy Packets

| Legacy packet ID |
| --- |
| `HV-AP-REP-020-A` |
| `HV-AP-REP-020-B` |
| `HV-FINC-REP-009-A` |
| `HV-FINC-REP-009-B` |
| `HV-INSR-REP-020-A` |
| `HV-INSR-REP-020-B` |
| `HV-ITAC-REP-001-A` |
| `HV-ITAC-REP-001-B` |
| `HV-ITAC-REP-003-A` |
| `HV-ITAC-REP-003-B` |
| `HV-ITAC-REP-015-A` |
| `HV-ITAC-REP-015-B` |
| `HV-MEDX-REP-001-A` |
| `HV-MEDX-REP-001-B` |
| `HV-PSRC-REP-007-A` |
| `HV-PSRC-REP-007-B` |
| `HV-SECO-REP-004-A` |
| `HV-SECO-REP-004-B` |
| `HV-SECO-REP-007-A` |
| `HV-SECO-REP-007-B` |
