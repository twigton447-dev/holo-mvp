# AP All-Six-Collapse Canary Readiness Rule Mismatch Autopsy

Date: 2026-06-29

Run folder: `docs/benchmark/holoverify_ap_procurement_replication_2026-06-29/holo_canary_openai_w2_all_six_collapse/run_20260629T193200Z`

Original run classification: `AP_OPENAI_W2_ALL_SIX_COLLAPSE_HOLO_CANARY_INVALID_OR_INCOMPLETE`

Corrected audit classification: `CANARY_COMPLETE_ALL_PACKETS_CORRECT_READINESS_RULE_MISMATCH`

## Finding

The fresh AP OpenAI-W2 all-six-collapse Holo canary completed all expected calls and produced correct final verdicts for all `12/12` packets, but the runner marked readiness as failed because the canary-specific readiness rule used the wrong evidence level.

The stale rule required `valid_rescue_evidence_present` on the target packet itself. That is appropriate for packet-local rescue lanes, but this canary was selected from the frozen AP solo triage ranking where the proof criterion is pair-level `ALL_SIX_SOLO_COLLAPSE`.

## Preserved Run Facts

- Provider calls: `60/60`
- Worker calls: `36`
- Gov calls: `24`
- Solo calls: `0`
- Judge calls: `0`
- Provider failures: `0`
- Parse failures: `0`
- Empty-worker recoveries needed: `0`
- No leakage: `PASS`
- Lock validation: `PASS`
- Packet correctness: `12/12`
- Original valid pairs: `2/6`
- Corrected valid pairs under pair-level solo-collapse rule: `6/6`
- Tokens: `95203` input / `22439` output / `125468` total
- Trace hash: `b1445d6cf1ce99e1cf200c867c40c9951dcf41773d1ee17856fd287a492264d9`
- Lock root: `543b44f88dedff4715d35b87066c440a8a09ef1a512072fb2ef55927c1052ed0`

## Corrected Rule

For this all-six-collapse canary, a pair is valid when:

- target sibling final verdict is correct and admissible;
- guardrail sibling final verdict is correct and admissible;
- frozen solo triage evidence for that pair has `triage_class=ALL_SIX_SOLO_COLLAPSE`;
- frozen solo triage evidence has `not_knew_count=6`;
- frozen solo triage evidence has `calls_present=6`.

This keeps external solo collapse evidence separate from intra-Holo rescue evidence while matching the purpose of the canary.

## Pair-Level Audit

| Pair | Target final | Guardrail final | Solo triage | Not-KNEW | Calls | Corrected valid |
| --- | --- | --- | --- | --- | --- | --- |
| `HV-AP-REP-005` | `ALLOW` | `ESCALATE` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `6` | `True` |
| `HV-AP-REP-010` | `ALLOW` | `ESCALATE` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `6` | `True` |
| `HV-AP-REP-011` | `ESCALATE` | `ALLOW` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `6` | `True` |
| `HV-AP-REP-012` | `ESCALATE` | `ALLOW` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `6` | `True` |
| `HV-AP-REP-013` | `ESCALATE` | `ALLOW` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `6` | `True` |
| `HV-AP-REP-019` | `ESCALATE` | `ALLOW` | `ALL_SIX_SOLO_COLLAPSE` | `6` | `6` | `True` |

## Preservation Boundary

The locked run folder is not edited by this autopsy. Raw trace, prompts, artifacts, lock files, and the original generated summary remain preserved exactly as emitted.

The runner has been patched prospectively so future all-six-collapse canary summaries use pair-level frozen solo triage evidence.

## Next Valid Move

No rerun is needed for the 6-pair canary. The corrected audit supports unlocking the full AP OpenAI-W2 20-pair Holo family run, subject to an updated full-family preflight and explicit approval.
