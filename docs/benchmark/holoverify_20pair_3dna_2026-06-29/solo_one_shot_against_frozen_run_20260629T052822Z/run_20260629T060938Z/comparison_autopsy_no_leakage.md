# HoloVerify vs Solo One-Shot Autopsy

## Bottom Line

The frozen HoloVerify run solved all 40 packets across 20 allow/escalate sibling pairs. The clean solo one-shot baseline used the same three mini-model families on the same frozen source packets, without Gov, Holo state, packet IDs, pair IDs, expected verdicts, target labels, guardrail labels, or Blindspot Atlas context. Solo completed 120/120 provider calls with no provider failures and produced only 6 admissible KNEW rows.

This means the current evidence supports a real architecture delta: HoloVerify is not merely getting lucky on one packet. It is converting a packet family that repeatedly defeats isolated mini-model one-shots into complete admissible decisions through governance, deterministic gates, state, repair routing, artifact preservation, and final selection.

## Locked Evidence

| Artifact | Value |
| --- | --- |
| Holo freeze status | `PASS` |
| Holo freeze root signature | `dcd9f17a76eef5bbe3b2a20195835a98b3694b511aa66d313fa4a91e7f2a17f1` |
| Holo trace hash | `dbb1d040c516af4989d488a07c44917a3582dc17da75c9fc517b4472228f1201` |
| Solo run status | `SOLO_ONE_SHOT_3MINI_40_COMPLETE` |
| Solo run-lock status | `PASS` |
| Solo run-lock root signature | `223aa9dd0f9f1d42b08f5efd44166e80f5100590c591afb655fbadfd89e7438f` |
| Solo trace hash | `5f98d96f82723979123a7eb13ed54900fe09f090cc1eaf7f40af2b073d724f94` |
| Solo trace rows | `120` |
| Solo prompt leakage status | `PASS` |
| Independent forbidden prompt scan hits | `0` |

## Architecture Boundary

| Lane | Provider calls | Worker calls | Gov calls | Judge calls | Holo state visible? | Gov baton visible? | Atlas visible? |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| HoloVerify frozen run | 200 | 120 | 80 | 0 | yes | yes | internal architecture evidence only |
| Solo one-shot baseline | 120 | 0 | 0 | 0 | no | no | no |

Solo prompts carried source context and the answer contract only. `action.business_ref` was scrubbed because it contained benchmark packet identifiers with A/B suffixes. Source document IDs and source document contents were not changed.

## Token Accounting

| Lane | Input | Output | Total |
| --- | ---: | ---: | ---: |
| HoloVerify | 304399 | 99117 | 426002 |
| Solo one-shot aggregate | 103254 | 80732 | 206839 |
| Difference, Holo minus Solo | 201145 | 18385 | 219163 |
| Holo/Solo token multiple |  |  | 2.060x |

## Solo Result Summary

| Label | Count | Meaning |
| --- | ---: | --- |
| `KNEW` | 6 | Verdict matched and deterministic/source gate passed. |
| `WRONG_VERDICT` | 96 | Model failed the verdict or returned no usable verdict. |
| `STRUCTURAL_OR_EVIDENCE_FAIL` | 14 | Verdict matched, but source/structure/admissibility gate failed. |
| `PARSE_FAIL` | 4 | Response could not be parsed as valid JSON. |
| `PROVIDER_FAIL` | 0 | Provider failed before a usable artifact existed. |

| Model | Calls | Verdict Correct | KNEW | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail | Total Tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `google/gemini-2.5-flash-lite` | 40 | 5 | 0 | 35 | 5 | 0 | 0 | 62900 |
| `minimax/MiniMax-M2.5-highspeed` | 40 | 10 | 2 | 26 | 8 | 4 | 0 | 72403 |
| `xai/grok-3-mini` | 40 | 5 | 4 | 35 | 1 | 0 | 0 | 71536 |

## Packet And Pair Gap

| Gap Class | Count |
| --- | ---: |
| `ALL_THREE_SOLOS_FAILED` | 34 |
| `MIXED_SOLO_FAILURE` | 6 |
| `PAIR_ALL_SIX_SOLOS_FAILED` | 14 |
| `PAIR_MIXED_SOLO_FAILURE` | 6 |

The strongest registry-grade candidates are the 14 sibling pairs where all six solo one-shots failed while Holo solved both siblings. The remaining 6 pairs are still useful, but they are mixed-solo-failure pairs rather than clean all-solo-collapse pairs.

## Pair Matrix

| Pair | Pair Class | Solo KNEW Count | A Expected/Holo | A Solo Labels | B Expected/Holo | B Solo Labels |
| --- | --- | ---: | --- | --- | --- | --- |
| `BAL100-BEC-HARDEN-025-H03` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `BAL100-BEC-HARDEN-025-H06` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:WRONG_VERDICT` |
| `BAL100-HB004-DEP-001` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `BAL100-HB004-DEP-002` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `BAL100-HB004-DEP-003` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:PARSE_FAIL, xai:WRONG_VERDICT` |
| `BAL100-HB004-DEP-004` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:WRONG_VERDICT` |
| `BAL100-HB004-DEP-005` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:PARSE_FAIL, xai:WRONG_VERDICT` |
| `BAL100-HB004-DEP-006` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:WRONG_VERDICT` |
| `BAL100-HB004-DEP-007` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:PARSE_FAIL, xai:WRONG_VERDICT` |
| `HV-KITC-042` | `PAIR_MIXED_SOLO_FAILURE` | 1 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:KNEW, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `HV-KITC-077` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `HV-KITC-078` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `HV-KITC-081` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:STRUCTURAL_OR_EVIDENCE_FAIL, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `HV-KITC-082` | `PAIR_MIXED_SOLO_FAILURE` | 1 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:KNEW` |
| `HV-KITC-084` | `PAIR_MIXED_SOLO_FAILURE` | 1 | `ALLOW / ALLOW` | `google:STRUCTURAL_OR_EVIDENCE_FAIL, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:KNEW, xai:WRONG_VERDICT` |
| `HV-KITC-086` | `PAIR_MIXED_SOLO_FAILURE` | 1 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:STRUCTURAL_OR_EVIDENCE_FAIL, minimax:STRUCTURAL_OR_EVIDENCE_FAIL, xai:KNEW` |
| `HV-KITC-087` | `PAIR_ALL_SIX_SOLOS_FAILED` | 0 | `ALLOW / ALLOW` | `google:STRUCTURAL_OR_EVIDENCE_FAIL, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` |
| `HV-KITC-089` | `PAIR_MIXED_SOLO_FAILURE` | 1 | `ALLOW / ALLOW` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:WRONG_VERDICT, xai:KNEW` |
| `HV-KITC-090` | `PAIR_MIXED_SOLO_FAILURE` | 1 | `ALLOW / ALLOW` | `google:STRUCTURAL_OR_EVIDENCE_FAIL, minimax:WRONG_VERDICT, xai:WRONG_VERDICT` | `ESCALATE / ESCALATE` | `google:WRONG_VERDICT, minimax:PARSE_FAIL, xai:KNEW` |

## What We Learned

1. The seam is real: isolated mini one-shots collapse on this family, while full HoloVerify clears it end to end.
2. The winning behavior is architecture-level, not just a model identity advantage. The same model families used inside Holo were also tested alone, and the solo baseline largely failed.
3. Deterministic admissibility matters. Several solo calls reached the right verdict but failed the evidence/structure gate, which means a simple verdict-only scoreboard would overstate solo competence.
4. The no-leakage control held. The prompt preflight, runtime trace rows, summary, and independent prompt-string scan all report zero forbidden Holo/Gov/packet/answer-key identifiers.
5. The cost is measurable. Holo used more tokens because it did more work: repeated worker calls, Gov calls, deterministic repair pressure, artifact preservation, and final selection.

## What This Does Not Yet Prove

- It does not replace official blinded judging. This is a deterministic/source-gate and trace comparison, not a judge run.
- It does not prove every possible Holo architecture wins. It proves this frozen full HoloVerify architecture beats same-family solo one-shots on this locked 20-pair packet set.
- It does not mean every solo failure is semantic. Some failures are structural, parse, or evidence-admissibility failures, and those should remain separately labeled.

## Next Step

Promote the 14 all-six-solo-failed sibling pairs as the first registry-candidate batch, keep the 6 mixed-failure pairs as secondary evidence, and defer official judging until the desired set of 10+ pairs is selected and frozen under the publication gates.
