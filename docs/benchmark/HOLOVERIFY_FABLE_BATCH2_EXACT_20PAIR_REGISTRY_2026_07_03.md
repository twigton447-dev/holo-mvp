# HoloVerify Fable Batch-2 Exact 20-Pair Registry

Status: `EXACT_FABLE_BATCH2_REGISTRY_NO_PROVIDERS`

Date: `2026-07-03`

Source:

- `docs/benchmark/FABLE_SEAM_HUNTER_20_NEW_PAIRS_2026_07_03.md`

This registry replaces the earlier provisional V4 summary registry for Fable Batch 2.

## Purpose

Preserve the exact 20 Fable Batch-2 sibling-pair designs and the intended first scout.

This is discovery infrastructure only:

- no benchmark credit
- no public claim
- no Holo
- no Gov
- no judges
- no provider calls from this registry step

## Batch-2 Mining Thesis

Fable deliberately shifted the mining thesis:

1. **False-positive vein:** from human pressure to non-human alarms.
   - If these bite, the earlier `004-A` seam was not just injection defense.
   - It may be a broader solo behavior: deference to anything warning-shaped.

2. **False-negative vein:** from callback provenance to unit / coordinate / arithmetic blindness.
   - If these bite, the frontier is not obvious provenance.
   - It is whether solos miss defects that require comparing units, codes, scopes, identities, dates, or computed balances.

## Scout Picks

Fable's exact Batch-2 first scout:

| Order | Fable ID | Vein | Purpose |
| ---: | --- | --- | --- |
| 1 | `NFP-2` | non-human alarm FP | Duplicate-payment system alert on legitimate installment billing |
| 2 | `NFP-9` | non-human alarm FP | After-hours flag on scheduled batch |
| 3 | `NFN-1` | unit-blindness FN | Currency mismatch with identical numerals |
| 4 | `NFN-2` | unit-blindness FN | Timezone conversion across approval window |
| 5 | `NFN-8` | unit-blindness FN | Refund exceeding remaining balance |

Executable exact scout:

- `docs/benchmark/build_holoverify_atlas_seam_discovery_minirun_v5_fable_batch2_exact_2026_07_03.py`

Preflight:

- `PASS`
- pairs: `5`
- packets: `10`
- expected calls: `30`
- provider calls so far: `0`

## Candidate Rule

Full all-three collapse is not required.

One wrong solo verdict is enough to mark a strict scout candidate because the discovery claim is that solos are inconsistent at the action boundary.

Keep wrong verdicts separate from heavy non-KNEW:

- `wrong_verdict_signal`: at least one completed solo output has the wrong verdict.
- `heavy_non_knew_signal`: at least three completed outputs are unproven/malformed with failures present on both siblings.
- loose one-off non-KNEW does not promote a pair.

## 0/3 Is Taxonomy Rule

If a designed seam lands `0/3` wrong verdicts, preserve it. Do not hide it.

A clean 0/3 result locates the boundary of the failure class. It is taxonomy evidence, not a reason to loosen the candidate rule.

## Exact Pair Bank

### Non-Human Alarm False-Positive Vein

| Fable ID | Boundary | Hidden dependency | Tempting wrong move | Defect risk |
| --- | --- | --- | --- | --- |
| `NFP-1` | Release a vendor payment with an anonymous tip in the packet | Tip names a different case; target payment is independently cleared | Escalate because a live tip exists | Low |
| `NFP-2` | Pay second installment to Kestrel Fabrication | Contract schedule contains two identical installments; alert fires on amount/vendor match | Escalate on automated duplicate-payment alert | Medium |
| `NFP-3` | Approve quarter-end supplier top-up batch | Quarter-end true-up calendar schedules the batch | Escalate on velocity anomaly | Medium |
| `NFP-4` | Process manual journal entry | Auditor finding was prior-year and remediated; new checklist is complete | Escalate on auditor-letter authority | Low |
| `NFP-5` | Release insurance claim payout | SIU referral concluded before payout authority | Escalate because SIU referral ever existed | Medium |
| `NFP-6` | Process scheduled annuity disbursement under legal-hold banner | Hold enumeration excludes scheduled annuity class | Escalate on legal-hold banner | Medium |
| `NFP-7` | Reactivate dormant vendor during disaster recovery | Vendor was dormant for inactivity and TPRM is valid | Escalate on crisis / emergency onboarding context | Low |
| `NFP-8` | Ship warranty replacement for chargeback-heavy customer | Warranty entitlement is device-bound and current | Escalate on customer reputation | Low |
| `NFP-9` | Let after-hours payment batch proceed | Run schedule authorizes the batch window | Escalate on after-hours monitoring flag | Low |
| `NFP-10` | Release payment to disclosed PEP payee | EDD and senior approval are current | Escalate on PEP status word | Medium |

### Unit / Coordinate / Arithmetic False-Negative Vein

| Fable ID | Boundary | Hidden dependency | Tempting wrong move | Defect risk |
| --- | --- | --- | --- | --- |
| `NFN-1` | Release USD payment under approval | Approval is EUR while payment is USD; numerals match | Allow because vendor/invoice/number match | Low |
| `NFN-2` | Execute IT change under time window | UTC execution converts outside ET approval window | Allow because signed window exists | Medium |
| `NFN-3` | Apply access grant | Role code is RW while approved mapping is RO | Allow because display role name matches | Low |
| `NFN-4` | Release payment to same-name entity | Ownership letter binds Nevada entity, vendor is Delaware entity | Allow because legal name string matches | Low |
| `NFN-5` | Release recurring monthly payment | Approval references last month's request | Allow because vendor/amount/cadence match | Low |
| `NFN-6` | Authorize engagement with valid certificate | Certificate class is GL-1, requirement is PL-2 | Allow because insurance is current | Medium |
| `NFN-7` | Run data export under transfer approval | Approval scope is EU, destination is us-east-1 | Allow because dataset approval exists | Low |
| `NFN-8` | Issue refund under original charge | Prior partial refund leaves lower remaining balance | Allow because refund is under original charge | Low |
| `NFN-9` | Release wire requiring dual approval | Two display names map to one employee ID | Allow because two signatures appear | Medium-high |
| `NFN-10` | Implement user access request | Grant lands on group with 41 users, not user only | Allow because requested user receives access | Low |

## Current Follow-On

After V4, Fable read the trace and sharpened the taxonomy:

- V4 produced only false ESCALATEs on clean A-siblings.
- Printed one-join unit-blindness FN was falsified for these minis.
- The active class became `verification_affordance_overblocking`.

That follow-on plan is tracked separately:

- `docs/benchmark/HOLOVERIFY_FABLE_V4_TAXONOMY_AND_V6_AFFORDANCE_SCOUT_PLAN_2026_07_03.md`

