# HoloVerify Blind Canary 20-Packet Rollup

Status: `CANONICAL_20_PACKET_RUNTIME_FIREWALL_CANARY_ROLLUP`

Created: `2026-07-03T00:57:21Z`

Provider calls made by this rollup: `0`

Judge calls made by this rollup: `0`

## Bottom Line

The repaired blind canary now has a canonical passing set covering all `20/20`
opaque runtime packets.

This is a **runtime-firewall canary**, not a public benchmark score, not an
error-rate claim, and not a FP/FN confidence-bound claim. Its purpose is to test
whether the repaired live path can run from the runtime manifest and opaque
payloads, freeze traces, and only then score against the hidden post-hoc map.

## Claim Boundary

Allowed statement:

> In the blind canary lane, the repaired HoloVerify runtime completed 20 opaque
> packets with 100 canonical provider calls, no judges, no solo calls, no model
> substitutions, and post-hoc scoring after trace freeze showed 20/20 final
> verdicts matched the hidden scoring map, under two contract versions and
> after four preserved invalid attempts totaling 119 provider calls.

Forbidden statements:

- Do not call this an error-rate measurement.
- Do not compute Wilson, exact, FP, or FN rates from this canary.
- Do not claim architecture advantage from this canary alone.
- Do not merge this with the previously confounded 614-packet public page.
- Do not hide the invalid lineage that forced contract hardening.

## Source Anchors

| Artifact | Path | SHA-256 |
| --- | --- | --- |
| Runtime manifest | `docs/benchmark/holoverify_blind_canary_runtime_manifest_2026_07_02.json` | `b80861ab6e407f98d69a7dd268ee102648b0455c19a1823ad0504fb321768bd7` |
| Scoring map | `docs/benchmark/holoverify_blind_canary_scoring_map_2026_07_02.json` | `5bb6fea5c3f2d72ae0b092eb168aeebc6ab4dcd6bc897b784c563dc455822c2b` |
| Audit manifest | `docs/benchmark/holoverify_blind_canary_manifest_2026_07_02.json` | `fa6a32cde377ca4d32387fae697b9a11b07fb977de4ff95572ee306c3147adcb` |
| Fable gate record | `docs/benchmark/FABLE_CANARY_GATE_RECORD_2026_07_02.json` | `153c07143806ca21733434d604b077b2062b98d31875c0078017c124ebb7a05d` |
| W3 final compiler patch | `docs/benchmark/BLIND_CANARY_W3_FINAL_COMPILER_CONTRACT_PATCH_2026_07_03.json` | `024cd20230b5c2c84e8465e743d860c8fdfe655a0ec13b417f4a8201c48b0cd9` |

Current HEAD while this rollup was built:

`634ff17f18517af62f561828c37510270a1ed67b`

## Runtime Roster

| Slot | Role | Model | Canonical calls |
| --- | --- | --- | ---: |
| `W1` | worker / source boundary mapper | `xai/grok-3-mini` | 20 |
| `G1` | Gov / control router | `minimax/MiniMax-M2.5-highspeed` | 20 |
| `W2` | worker / adversarial scope challenger | `openai/gpt-5.4-mini` | 20 |
| `G2` | Gov / control router | `minimax/MiniMax-M2.5-highspeed` | 20 |
| `W3` | worker / final compiler | `minimax/MiniMax-M2.5-highspeed` | 20 |

Solo calls: `0`

Judge calls: `0`

Substitutions: `0`

## Aggregate Result

| Measure | Value |
| --- | ---: |
| Opaque packets in canonical passing set | 20 |
| Canonical provider calls | 100 |
| Correct post-hoc final verdicts | 20 |
| Incorrect post-hoc final verdicts | 0 |
| ALLOW truths | 10 |
| ESCALATE truths | 10 |
| ALLOW final verdicts | 10 |
| ESCALATE final verdicts | 10 |
| Canonical trace retries | 0 |

Token totals for the canonical passing traces:

| Provider | Input tokens | Output tokens | Total tokens |
| --- | ---: | ---: | ---: |
| `xai` | 13,470 | 1,999 | 25,730 |
| `openai` | 11,637 | 2,729 | 14,366 |
| `minimax` | 23,958 | 38,441 | 62,399 |
| **Total** | **49,065** | **43,169** | **102,495** |

Note: these are copied from the source post-hoc score artifacts. Provider
`total_tokens` is preserved as reported and may not always equal
`input_tokens + output_tokens` for every provider.

## Canonical Passing Trace Set

| Packet | Run | Commit | Opaque ID | Final | Hidden truth loaded after trace freeze | Correct |
| ---: | --- | --- | --- | --- | --- | --- |
| 01 | `run_20260702T235724Z` | `cb5403b30` | `BLIND-02C93D83F0A59F2F` | ESCALATE | ESCALATE | true |
| 02 | `run_20260703T000530Z` | `d5ff3adbf` | `BLIND-0BFB735E16DCABFD` | ALLOW | ALLOW | true |
| 03 | `run_20260703T001616Z` | `856a2ff42` | `BLIND-25C5FC5DE59A6D84` | ESCALATE | ESCALATE | true |
| 04 | `run_20260703T001816Z` | `49d28e55a` | `BLIND-402C877AC4101304` | ESCALATE | ESCALATE | true |
| 05 | `run_20260703T002016Z` | `abe3e0505` | `BLIND-4863E55F9B3510DE` | ALLOW | ALLOW | true |
| 06 | `run_20260703T002155Z` | `e7ee14929` | `BLIND-52893B06912FCB1F` | ESCALATE | ESCALATE | true |
| 07 | `run_20260703T002340Z` | `2fce4281a` | `BLIND-558F75768D966F9B` | ESCALATE | ESCALATE | true |
| 08 | `run_20260703T002631Z` | `99058b80b` | `BLIND-56641B8E475F3A34` | ESCALATE | ESCALATE | true |
| 09 | `run_20260703T002812Z` | `9885bf21f` | `BLIND-5D5F722D3F8B58D4` | ALLOW | ALLOW | true |
| 10 | `run_20260703T003121Z` | `277a7a3f4` | `BLIND-6350434776E26908` | ALLOW | ALLOW | true |
| 11 | `run_20260703T003121Z` | `277a7a3f4` | `BLIND-6E534FDC1015C6AE` | ALLOW | ALLOW | true |
| 12 | `run_20260703T003121Z` | `277a7a3f4` | `BLIND-9868CCC3BD27ADC5` | ALLOW | ALLOW | true |
| 13 | `run_20260703T003436Z` | `c299aebc1` | `BLIND-9FACF08B1C34AB8C` | ESCALATE | ESCALATE | true |
| 14 | `run_20260703T003436Z` | `c299aebc1` | `BLIND-A59CFB0A606A9917` | ALLOW | ALLOW | true |
| 15 | `run_20260703T003436Z` | `c299aebc1` | `BLIND-B6BCF5207BF74AE3` | ESCALATE | ESCALATE | true |
| 16 | `run_20260703T003759Z` | `f5575c579` | `BLIND-CC9D121D9C007013` | ALLOW | ALLOW | true |
| 17 | `run_20260703T003759Z` | `f5575c579` | `BLIND-DA4623DA67A24371` | ESCALATE | ESCALATE | true |
| 18 | `run_20260703T003759Z` | `f5575c579` | `BLIND-DB02E49E7B54095A` | ALLOW | ALLOW | true |
| 19 | `run_20260703T005104Z` | `0567e0854` | `BLIND-DB24654CAD859FB0` | ESCALATE | ESCALATE | true |
| 20 | `run_20260703T005220Z` | `634ff17f1` | `BLIND-EB92C511C9405B48` | ALLOW | ALLOW | true |

## Invalid Lineage Preserved

These attempts remain part of the evidence history. They are not verdict
failures, not FP/FN datapoints, and not score-valid results.

| Run | Classification | Scope | Root issue |
| --- | --- | --- | --- |
| `run_20260702T233202Z` | `INVALID_RUN_CONTENT_CONTRACT_FAILURE_AFTER_SUCCESSFUL_TRANSPORT` | 20 packets, 100/100 provider calls | Workers and Gov returned non-contract or incomplete output; all final verdicts were `UNKNOWN`. |
| `run_20260703T000229Z` | `INVALID_ONE_PACKET_CONTENT_FAILURE_W3_LENGTH_WITH_RETRY_BOUNDARY_BUG` | packet 2, 5/5 provider calls | W3 truncated before completing schema, and the runner initially treated content failure like transport. |
| `run_20260703T000924Z` | `INVALID_ONE_PACKET_CONTENT_FAILURE_G2_EMPTY_TEXT_AFTER_LENGTH` | packet 3, 4/5 provider calls | MiniMax G2 hit length after hidden thinking; filtered compact baton text was empty. |
| `run_20260703T004112Z` | `INVALID_RUN_CONTENT_CONTRACT_FAILURE_W3_LENGTH_EMPTY_TEXT` | packets 19-20, 10/10 provider calls | MiniMax W3 hit length after hidden thinking; filtered final compiler text was empty. |

## Interpretation

This is good news for the repaired runtime firewall: the live path can complete
all 20 opaque packets and parse scoring-map content only after trace freeze.
However, the canary is heterogeneous: packets 1-18 ran before the W3 final
compiler patch, while packets 19-20 ran after that patch.

It is not yet enough to restore the old public benchmark claims. The next proof
step is an adversarial review of this rollup and the underlying traces, then a
larger blind packet bank if the firewall still holds.

## Fable Rollup Audit Result

Fable returned `PASS_WITH_LIMITATIONS` after recomputing the rollup from disk.
His core counts matched: 20 unique opaque packets, 100 canonical provider calls,
0 solo, 0 judges, 0 substitutions, 0 transport retries, 20/20 post-hoc correct,
and zero forbidden-term hits across canonical run dirs.

The limitations to carry forward:

- The canonical set spans two contract versions: packets 1-18 pre-W3 patch,
  packets 19-20 post-W3 patch.
- Freeze-then-score was code-enforced in the old canary, but the old score
  artifact did not bind itself to the exact trace hash it scored.
- The old live wrapper hash-pinned scoring-map bytes during preflight; the more
  precise phrase is: scoring-map content was parsed only after trace freeze.
- The headline must include the invalid lineage: four preserved invalid attempts
  consumed 119 provider calls before the canonical passing set.
- Future blind runs need a declared attempt budget before execution.
