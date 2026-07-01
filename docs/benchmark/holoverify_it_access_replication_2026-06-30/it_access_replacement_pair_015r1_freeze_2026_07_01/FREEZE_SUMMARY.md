# IT Access Replacement Pair 015R1 Freeze

Classification: `IT_ACCESS_REPLACEMENT_PAIR_015R1_FREEZE`
Original retired pair: `HV-ITAC-REP-015`
Replacement pair: `HV-ITAC-REP-015R1`
Original freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
Replacement freeze root: `6c61024da5f6c36c1ee5210b95efd1d7a1ed0caff60a11efe0ace1ca1e72dc4e`

## Scope

- Packets: `2`
- Pairs: `1`
- Truths: `1 ALLOW`, `1 ESCALATE`
- Target bucket: `hard_escalate`
- Provider calls: `0`
- Judge calls: `0`

## Reason

`HV-ITAC-REP-015` is retired from proof-credit because the ALLOW sibling used model-visible wording that reasonably implied an active offboarding blocker. This replacement pair keeps the same dependency class but separates historical offboarding context from current exact source-control closure.

Local validation: `PASS`
Leakage scan: `PASS`
