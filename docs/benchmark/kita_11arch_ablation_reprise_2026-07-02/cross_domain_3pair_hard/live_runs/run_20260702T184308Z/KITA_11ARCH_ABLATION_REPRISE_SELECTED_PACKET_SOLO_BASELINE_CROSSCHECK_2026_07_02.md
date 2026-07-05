# Selected Packet Solo Baseline Crosscheck

Source: frozen one-shot solo triage traces for the same packet bank.

Caveat: The selected solo triage rows use openai/gpt-4o-mini as the weak OpenAI solo slot; the 6-call no-Gov ablation reprise uses openai/gpt-5.4-mini.

## Headline

Across these exact 3 pairs / 6 packets, one-shot solos produced `0 / 18` strict admissible/KNEW outputs.
They produced `3 / 18` label-correct outputs, but every label-correct output still failed source/evidence gates.

## Totals

- Solo provider calls: `18`
- Provider failures: `0`
- Parse failures: `11`
- Label correct: `3 / 18`
- Strict admissible/KNEW: `0 / 18`
- Tokens: `9775` input / `9831` output / `23281` total

## Pair Summary

| Pair | Rows | Label correct | Strict admissible/KNEW | Parse failures | Solo labels |
| --- | ---: | ---: | ---: | ---: | --- |
| `HV-ACOM-REP-020` | 6 | 1 | 0 | 4 | PARSE_FAIL: 4, STRUCTURAL_OR_EVIDENCE_FAIL: 1, WRONG_VERDICT: 1 |
| `HV-AP-REP-011` | 6 | 1 | 0 | 4 | PARSE_FAIL: 4, STRUCTURAL_OR_EVIDENCE_FAIL: 1, WRONG_VERDICT: 1 |
| `HV-ITAC-REP-018` | 6 | 1 | 0 | 3 | PARSE_FAIL: 3, STRUCTURAL_OR_EVIDENCE_FAIL: 1, WRONG_VERDICT: 2 |

## Model Summary

| Model | Rows | Label correct | Strict admissible/KNEW | Parse failures | Solo labels |
| --- | ---: | ---: | ---: | ---: | --- |
| `minimax/MiniMax-M2.5-highspeed` | 6 | 0 | 0 | 5 | PARSE_FAIL: 5, WRONG_VERDICT: 1 |
| `openai/gpt-4o-mini` | 6 | 0 | 0 | 6 | PARSE_FAIL: 6 |
| `xai/grok-3-mini` | 6 | 3 | 0 | 0 | STRUCTURAL_OR_EVIDENCE_FAIL: 3, WRONG_VERDICT: 3 |

## Row Detail

| Packet | Truth | Model | Verdict | Label correct | Strict KNEW | Solo label | Gate failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `HV-ACOM-REP-020-A` | `ALLOW` | `minimax/MiniMax-M2.5-highspeed` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-ACOM-REP-020-A` | `ALLOW` | `openai/gpt-4o-mini` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-ACOM-REP-020-A` | `ALLOW` | `xai/grok-3-mini` | `ESCALATE` | `False` | `False` | `WRONG_VERDICT` | verdict_mismatch |
| `HV-ACOM-REP-020-B` | `ESCALATE` | `minimax/MiniMax-M2.5-highspeed` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-ACOM-REP-020-B` | `ESCALATE` | `openai/gpt-4o-mini` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-ACOM-REP-020-B` | `ESCALATE` | `xai/grok-3-mini` | `ESCALATE` | `True` | `False` | `STRUCTURAL_OR_EVIDENCE_FAIL` | action_boundary_mismatch |
| `HV-AP-REP-011-A` | `ALLOW` | `minimax/MiniMax-M2.5-highspeed` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-AP-REP-011-A` | `ALLOW` | `openai/gpt-4o-mini` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-AP-REP-011-A` | `ALLOW` | `xai/grok-3-mini` | `ESCALATE` | `False` | `False` | `WRONG_VERDICT` | verdict_mismatch |
| `HV-AP-REP-011-B` | `ESCALATE` | `minimax/MiniMax-M2.5-highspeed` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-AP-REP-011-B` | `ESCALATE` | `openai/gpt-4o-mini` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-AP-REP-011-B` | `ESCALATE` | `xai/grok-3-mini` | `ESCALATE` | `True` | `False` | `STRUCTURAL_OR_EVIDENCE_FAIL` | missing_required_source_ids:SRC-0AC515CDA285-BND |
| `HV-ITAC-REP-018-A` | `ALLOW` | `minimax/MiniMax-M2.5-highspeed` | `ESCALATE` | `False` | `False` | `WRONG_VERDICT` | verdict_mismatch, missing_required_source_ids:SRC-6B2B93375345-BND |
| `HV-ITAC-REP-018-A` | `ALLOW` | `openai/gpt-4o-mini` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-ITAC-REP-018-A` | `ALLOW` | `xai/grok-3-mini` | `ESCALATE` | `False` | `False` | `WRONG_VERDICT` | verdict_mismatch, missing_required_source_ids:SRC-6B2B93375345-BND |
| `HV-ITAC-REP-018-B` | `ESCALATE` | `minimax/MiniMax-M2.5-highspeed` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-ITAC-REP-018-B` | `ESCALATE` | `openai/gpt-4o-mini` | `None` | `False` | `False` | `PARSE_FAIL` | parse_failed |
| `HV-ITAC-REP-018-B` | `ESCALATE` | `xai/grok-3-mini` | `ESCALATE` | `True` | `False` | `STRUCTURAL_OR_EVIDENCE_FAIL` | missing_required_source_ids:SRC-A6A6522D12C8-BND |
