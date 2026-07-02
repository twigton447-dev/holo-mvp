# Kit A Ablation Reprise 6-Call Autopsy

Run: `run_20260702T184308Z`
Evidence root SHA-256: `215476b55ce00b11ff34240febc85504ed143c8c9bf5880ab0de254e6b2b8439`

## Headline

Provider-balanced no-Gov ablations completed 144/144 calls but cleared only 8/24 strict final artifacts.

The no-Gov baselines were not under-helped: each packet/architecture got 6 calls, with Grok, OpenAI, and MiniMax receiving exactly 2 turns each. Strict wins required both the right final label and deterministic source-closure admissibility.

## Overall Results

- Final architecture units: `24`
- Final-label correct: `13 / 24`
- Strict admissible correct: `8 / 24`
- Label-correct but inadmissible: `5`
- Wrong verdict final units: `9`
- Parse-failure final units: `2`

## Selected Packet One-Shot Solo Baseline

The matching frozen one-shot solo triage rows for these same 3 pairs / 6 packets produced `0 / 18` strict admissible/KNEW outputs. They produced `3 / 18` label-correct outputs, but those still failed source/evidence gates, so none count as strict source-closed wins.

Caveat: the solo triage crosscheck used `openai/gpt-4o-mini` as the weak OpenAI solo slot; the 6-call no-Gov ablation reprise used `openai/gpt-5.4-mini`. The crosscheck is therefore baseline context, not exact model-parity evidence for the 6-call reprise.

Detailed solo rows are in `KITA_11ARCH_ABLATION_REPRISE_SELECTED_PACKET_SOLO_BASELINE_CROSSCHECK_2026_07_02.md`.

## Architecture Summary

| Architecture | Final label correct | Strict admissible correct | Parse failures | Wrong verdict | Label correct but inadmissible |
| --- | ---: | ---: | ---: | ---: | ---: |
| `provider_balanced_council_no_gov_6call` | 4 / 6 | 3 / 6 | 0 | 2 | 1 |
| `provider_balanced_debate_no_gov_6call` | 3 / 6 | 2 / 6 | 0 | 3 | 1 |
| `provider_balanced_reconsider_no_gov_6call` | 3 / 6 | 1 / 6 | 1 | 2 | 2 |
| `provider_balanced_vote_no_gov_6call` | 3 / 6 | 2 / 6 | 1 | 2 | 1 |

## Packet Summary

| Packet | Truth | Domain | Final label correct | Strict admissible correct | Evidence classes |
| --- | --- | --- | ---: | ---: | --- |
| `HV-ACOM-REP-020-A` | `ALLOW` | Agentic commerce / order execution controls | 1 / 4 | 0 / 4 | LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE: 1, PARSE_FAILURE: 2, WRONG_VERDICT: 1 |
| `HV-ACOM-REP-020-B` | `ESCALATE` | Agentic commerce / order execution controls | 4 / 4 | 3 / 4 | LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE: 1, STRICT_ADMISSIBLE_CORRECT: 3 |
| `HV-AP-REP-011-A` | `ALLOW` | AP / procurement / vendor-master controls | 0 / 4 | 0 / 4 | WRONG_VERDICT: 4 |
| `HV-AP-REP-011-B` | `ESCALATE` | AP / procurement / vendor-master controls | 4 / 4 | 3 / 4 | LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE: 1, STRICT_ADMISSIBLE_CORRECT: 3 |
| `HV-ITAC-REP-018-A` | `ALLOW` | IT access / permission change controls | 0 / 4 | 0 / 4 | WRONG_VERDICT: 4 |
| `HV-ITAC-REP-018-B` | `ESCALATE` | IT access / permission change controls | 4 / 4 | 2 / 4 | LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE: 2, STRICT_ADMISSIBLE_CORRECT: 2 |

## Final-Unit Autopsy Table

| Pair | Packet | Truth | Architecture | Final verdict | Strict pass | Failure class | Gate failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `provider_balanced_council_no_gov_6call` | `ALLOW` | `False` | `LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE` | missing_required_source_ids:SRC-DDC2460F5040-BND |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `provider_balanced_debate_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `provider_balanced_reconsider_no_gov_6call` | `None` | `False` | `PARSE_FAILURE` | parse_failed |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-A` | `ALLOW` | `provider_balanced_vote_no_gov_6call` | `None` | `False` | `PARSE_FAILURE` | parse_failed |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `provider_balanced_council_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `provider_balanced_debate_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `provider_balanced_reconsider_no_gov_6call` | `ESCALATE` | `False` | `LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE` | missing_required_source_ids:SRC-894C31EF0E5B-BND |
| `HV-ACOM-REP-020` | `HV-ACOM-REP-020-B` | `ESCALATE` | `provider_balanced_vote_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `provider_balanced_council_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `provider_balanced_debate_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch, missing_required_source_ids:SRC-1D955A0F73B0-POL |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `provider_balanced_reconsider_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch, missing_required_source_ids:SRC-1D955A0F73B0-POL |
| `HV-AP-REP-011` | `HV-AP-REP-011-A` | `ALLOW` | `provider_balanced_vote_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch, missing_required_source_ids:SRC-1D955A0F73B0-POL |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `provider_balanced_council_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `provider_balanced_debate_no_gov_6call` | `ESCALATE` | `False` | `LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE` | missing_required_source_ids:SRC-0AC515CDA285-BND |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `provider_balanced_reconsider_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-AP-REP-011` | `HV-AP-REP-011-B` | `ESCALATE` | `provider_balanced_vote_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `provider_balanced_council_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `provider_balanced_debate_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `provider_balanced_reconsider_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch, missing_required_source_ids:SRC-6B2B93375345-BND |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-A` | `ALLOW` | `provider_balanced_vote_no_gov_6call` | `ESCALATE` | `False` | `WRONG_VERDICT` | verdict_mismatch |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `provider_balanced_council_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `provider_balanced_debate_no_gov_6call` | `ESCALATE` | `True` | `STRICT_ADMISSIBLE_CORRECT` | none |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `provider_balanced_reconsider_no_gov_6call` | `ESCALATE` | `False` | `LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE` | missing_required_source_ids:SRC-A6A6522D12C8-BND |
| `HV-ITAC-REP-018` | `HV-ITAC-REP-018-B` | `ESCALATE` | `provider_balanced_vote_no_gov_6call` | `ESCALATE` | `False` | `LABEL_CORRECT_EVIDENCE_OR_STRUCTURE_FAILURE` | missing_required_source_ids:SRC-A6A6522D12C8-BND |

## Interpretation Guardrails

- This is a no-Gov ablation diagnostic, not a fresh Holo run.
- The 6-call provider-balanced design gives no-Gov ablations one extra call per packet versus the original 5-call governed reference.
- Correct labels are not counted as strict wins unless source IDs and deterministic source-closure gates pass.
- Parse failures are reliability failures, not hidden judge decisions.
