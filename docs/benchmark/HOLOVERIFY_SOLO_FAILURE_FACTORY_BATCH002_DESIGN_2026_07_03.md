# HoloVerify Solo Failure Factory Batch002 Design

Status: `DESIGN_NO_PROVIDER`
Date: `2026-07-03`

Batch002 is a sharper solo-failure scout based on what actually fired in Batch001.

Batch001 produced four useful pairs:

- KYC / AML status with stale approval produced a false-negative solo miss.
- Agentic commerce rebrand callback provenance produced a false-negative solo miss.
- Customer refund remaining-balance control produced a false-positive miss plus one admissibility miss.
- IT change-management timezone logic produced both false-positive and false-negative misses.

Batch002 therefore narrows the search. It does not try to cover every domain evenly. It tries to find more pairs where at least one solo model fails.

## Scope

- Pairs: `10`
- Packets: `20`
- Expected solo calls if approved later: `60`
- Holo calls during build: `0`
- Gov calls during build: `0`
- Judge calls during build: `0`
- Public claims: `0`

## Target Seams

| Seam | Why It Is Included |
|---|---|
| KYC / AML stale approval | Batch001 found a false-negative on an expired approval chain. |
| Sanctions / lookalike resolution | Same status-word family, but with identity-resolution pressure. |
| Rebrand callback provenance | Batch001 found a false-negative when the control chain used an unsafe callback source. |
| Refund balance arithmetic | Batch001 found overblocking and admissibility brittleness around remaining-balance logic. |
| Timezone / window conversion | Batch001 produced the strongest two-sided solo failure. |
| Trusted-source vs requester-provided source | The action boundary often turns on where a confirmation came from, not whether confirmation exists. |

## Boundary

This is a no-provider design artifact. It creates no benchmark credit and no Holo result. A pair only becomes useful if post-hoc solo scoring shows at least one solo failure on one sibling.

