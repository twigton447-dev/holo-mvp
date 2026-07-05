# Solo One-Shot Against Frozen HoloVerify 20-Pair / 3-DNA Packets

Classification: `SOLO_ONE_SHOT_3MINI_40_COMPLETE`
Freeze root signature: `dcd9f17a76eef5bbe3b2a20195835a98b3694b511aa66d313fa4a91e7f2a17f1`
Holo trace hash: `dbb1d040c516af4989d488a07c44917a3582dc17da75c9fc517b4472228f1201`
Prompt leakage status: `PASS`
Provider calls: `120` / `120`
Tokens: `103254` input / `80732` output / `206839` total

## Leakage Controls

| Control | Value |
| --- | --- |
| `prompt_contains_expected_verdict` | `False` |
| `prompt_contains_holo_or_gov_state` | `False` |
| `prompt_contains_packet_id_or_pair_id` | `False` |
| `prompt_contains_target_or_guardrail_label` | `False` |
| `scrubbed_business_ref` | `True` |
| `source_document_contents_changed` | `False` |
| `source_doc_ids_changed` | `False` |

## Model Results

| Model | Calls | Verdict Correct | KNEW/Admissible | Wrong Verdict | Structural/Evidence Fail | Parse Fail | Provider Fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 | 5 | 4 | 35 | 1 | 0 | 0 |
| `google/gemini-2.5-flash-lite` | 40 | 5 | 0 | 35 | 5 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 | 10 | 2 | 26 | 8 | 4 | 0 |

## Holo Reference

- Holo classification: `HOLOVERIFY_20PAIR_3DNA_COMPLETE`
- Holo final admissible packets: `40/40`
- Holo valid pairs: `20`
- Holo provider calls: `200`
- Holo tokens: `304399` input / `99117` output / `426002` total

## Packet Matrix

| Packet | Expected | Holo | xAI | Gemini | MiniMax |
| --- | --- | --- | --- | --- | --- |
| `HV-KITC-078-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-078-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-081-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ALLOW:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `HV-KITC-081-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `ESCALATE:STRUCTURAL_OR_EVIDENCE_FAIL` | `None:WRONG_VERDICT` |
| `HV-KITC-082-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-082-B` | `ESCALATE` | `ESCALATE` | `ESCALATE:KNEW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-084-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `ALLOW:STRUCTURAL_OR_EVIDENCE_FAIL` | `None:WRONG_VERDICT` |
| `HV-KITC-084-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ESCALATE:KNEW` |
| `HV-KITC-086-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-086-B` | `ESCALATE` | `ESCALATE` | `ESCALATE:KNEW` | `ESCALATE:STRUCTURAL_OR_EVIDENCE_FAIL` | `ESCALATE:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `HV-KITC-087-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `ALLOW:STRUCTURAL_OR_EVIDENCE_FAIL` | `None:WRONG_VERDICT` |
| `HV-KITC-087-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `ALLOW:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-042-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ALLOW:KNEW` |
| `HV-KITC-042-B` | `ESCALATE` | `ESCALATE` | `ESCALATE:STRUCTURAL_OR_EVIDENCE_FAIL` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-089-A` | `ALLOW` | `ALLOW` | `ESCALATE:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-089-B` | `ESCALATE` | `ESCALATE` | `ESCALATE:KNEW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `HV-KITC-090-A` | `ALLOW` | `ALLOW` | `ESCALATE:WRONG_VERDICT` | `ALLOW:STRUCTURAL_OR_EVIDENCE_FAIL` | `None:WRONG_VERDICT` |
| `HV-KITC-090-B` | `ESCALATE` | `ESCALATE` | `ESCALATE:KNEW` | `ALLOW:WRONG_VERDICT` | `None:PARSE_FAIL` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ESCALATE:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `HV-KITC-077-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ALLOW:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `HV-KITC-077-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-BEC-HARDEN-025-H03-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-BEC-HARDEN-025-H03-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-BEC-HARDEN-025-H06-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ALLOW:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `BAL100-BEC-HARDEN-025-H06-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-001-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-001-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-002-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ALLOW:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `BAL100-HB004-DEP-002-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-003-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-003-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:PARSE_FAIL` |
| `BAL100-HB004-DEP-004-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-004-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ESCALATE:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `BAL100-HB004-DEP-005-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-005-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:PARSE_FAIL` |
| `BAL100-HB004-DEP-006-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-006-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `ESCALATE:STRUCTURAL_OR_EVIDENCE_FAIL` |
| `BAL100-HB004-DEP-007-A` | `ALLOW` | `ALLOW` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` |
| `BAL100-HB004-DEP-007-B` | `ESCALATE` | `ESCALATE` | `None:WRONG_VERDICT` | `None:WRONG_VERDICT` | `None:PARSE_FAIL` |
