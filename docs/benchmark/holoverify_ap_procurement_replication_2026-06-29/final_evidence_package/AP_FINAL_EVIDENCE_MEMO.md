# AP Procurement Replication Final Evidence Memo

Classification: `AP_REPLICATION_FINAL_EVIDENCE_PACKAGE`
Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`

## Results

- Holo packets correct: `40/40`
- Holo valid pairs: `20/20`
- Solo KNEW/admissible count: `53/120`
- All-six-solo-fail pairs: `1`
- Mixed pairs: `19`
- Token ratio Holo/Solo: `2.835x`

## Final Assertions

| Assertion | Value |
| --- | --- |
| `packet_hashes_match_freeze` | `PASS` |
| `holo_packets` | `40` |
| `holo_valid_pairs` | `20` |
| `holo_no_judges` | `PASS` |
| `holo_provider_failures` | `0` |
| `solo_calls` | `120` |
| `solo_packet_identity_matches_holo` | `PASS` |
| `solo_no_gov_state_judges` | `PASS` |
| `no_leakage` | `PASS` |
| `external_solo_failures_separated_from_intra_holo_misses` | `PASS` |
| `invalid_runs_preserved` | `PASS` |

## Strongest 5 AP Examples

| Pair | Packets | Solo failures | Holo all correct |
| --- | --- | ---: | --- |
| `HV-AP-REP-019` | `HV-AP-REP-019-A, HV-AP-REP-019-B` | 6 | `True` |

## Weak or Ambiguous Examples to Avoid

- `HV-AP-REP-001`: solo failures `4/6`, Holo all correct `True`
- `HV-AP-REP-002`: solo failures `3/6`, Holo all correct `True`
- `HV-AP-REP-003`: solo failures `2/6`, Holo all correct `True`
- `HV-AP-REP-004`: solo failures `2/6`, Holo all correct `True`
- `HV-AP-REP-005`: solo failures `5/6`, Holo all correct `True`
