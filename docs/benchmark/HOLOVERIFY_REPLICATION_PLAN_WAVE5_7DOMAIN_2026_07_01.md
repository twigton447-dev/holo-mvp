# HoloVerify Wave5 7-Domain Replication Plan

Classification: `HOLOVERIFY_REPLICATION_PLAN_WAVE5_7DOMAIN_NO_PROVIDER`
Status: `PASS`

Purpose: pre-register a full-family 280-packet expansion before provider calls.

## Statistical Goal

- `current_clean_denominator_packets`: `334`
- `current_clean_denominator_pairs`: `167`
- `wave5_additional_pairs`: `140`
- `wave5_additional_packets`: `280`
- `if_clean_new_total_packets`: `614`
- `if_clean_new_total_pairs`: `307`
- `intended_band_shift`: `below 0.5% packet-level upper bound and below 1.0% FP/FN upper bounds if clean`

## Families

| Family | Domain | Pairs | Packets | Commercial relevance |
| --- | --- | ---: | ---: | --- |
| `HV-MEDX-REP-2026-07-01` | Clinical medication / treatment activation controls | 20 | 40 | Prevents premature medication, treatment, or clinical-order activation when current source authority is incomplete. |
| `HV-TRES-REP-2026-07-01` | Treasury / wire / cash movement controls | 20 | 40 | Controls irreversible cash movement, bank changes, liquidity actions, and treasury exceptions. |
| `HV-LREG-REP-2026-07-01` | Legal / regulatory filing controls | 20 | 40 | Prevents filings, disclosures, contract actions, and privilege-sensitive releases from proceeding without current authority. |
| `HV-CLAD-REP-2026-07-01` | Cloud infrastructure / destructive admin controls | 20 | 40 | Controls destructive infrastructure changes, privileged access, secret rotation, and production-impacting operations. |
| `HV-SECO-REP-2026-07-01` | Security operations / incident response controls | 20 | 40 | Controls containment, quarantine, disclosure, and access actions during security incidents. |
| `HV-PSRC-REP-2026-07-01` | Public sector / citizen records controls | 20 | 40 | Controls benefits overrides, citizen-record releases, identity changes, and public-casework actions. |
| `HV-OTSF-REP-2026-07-01` | Industrial / utility / OT safety controls | 20 | 40 | Controls physical-operations actions, safety interlocks, outage exceptions, and infrastructure maintenance changes. |

## Run Order

- freeze packet bank locally
- commit freeze before providers
- run Holo full-family batches only after explicit provider approval
- freeze Holo traces
- run matched solo one-shot baselines on the same frozen packet bank
- build comparison and statistical appendix refresh

## Exclusion Rules

- Do not count live Holo results until all 280 frozen packets are run under the locked architecture.
- Do not use solo triage to select a subset for the statistical denominator.
- Do not mutate packet text, prompt text, or answer keys after freeze.
- Do not include tactical military targeting or autonomous clinical action claims.
