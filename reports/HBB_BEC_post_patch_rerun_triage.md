# HBB-BEC Post-Patch 4DNA Rerun Triage

Date: `2026-06-18`
Scope: `HBB-BEC-001`, `HBB-BEC-002-HARD`; four frozen packets; seed447 4DNA post-patch rerun.
Status: `not_ready_for_proof_credit_accounting_review`

This was the approved post-patch rerun only. It did not run Judge, QA, ablation, freeze, packet edits, frozen artifact edits, scorecard/proof-credit updates, or push.

## Run Summary

- Run directory: `scout_runs/HBB-BEC-post-patch-4dna-seed447-rerun`
- Rows: 16 actual / 16 expected
- Provider-call success: 14/16
- Parse success: 14/16 overall; 14/14 successful provider responses parsed cleanly
- Provider failures: Google/Gemini returned HTTP 503 on `HBB-BEC-001` ALLOW and `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL` ESCALATE.
- Frozen hash verification: PASS for all four frozen packet hashes.
- Original traces overwritten: no. No post-patch trace directories were created under `traces/`.

## Direct Answers

- Did all 16 expected rows complete? yes.
- Did all provider calls succeed? no; 14/16 succeeded, with two Google HTTP 503 failures.
- Did all responses parse? no overall; all successful responses parsed cleanly (14/14).
- Did frozen hashes remain exact? yes; all computed payload hashes matched the preflight-approved hashes.
- Did the previous HBB-BEC-001 ALLOW false-escalation get cured? no; HoloGov still returned `ESCALATE` on `HBB-BEC-001`.
- Did the previous HBB-BEC-002-HARD ESCALATE missed-risk loss get cured? yes on that previously failed packet; HoloGov returned `ESCALATE` on `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL`.
- Did HoloGov return KNEW on both previously failed cases? no; it returned KNEW only on the HBB-BEC-002-HARD ESCALATE case.
- Are both HBB families eligible for proof-credit accounting review? no.
- Did proof-credit remain unchanged pending accounting? yes; proof-credit remains `BEC-PAIR-009`, `BEC-PAIR-010` only, 2 pair families / 4 packets.

## Packet Outcomes

| Packet | Truth role | Active non-Gov outcomes | HoloGov | Triage |
|---|---|---|---|---|
| `HBB-BEC-001` | `ALLOW` | google:gemini-2.5-flash-lite=ERROR (ERROR); minimax:MiniMax-Text-01=ALLOW (KNEW); xai:grok-3-mini=ALLOW (KNEW) | ESCALATE (WRONG) | Previous false escalation not cured. |
| `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL` | `ESCALATE` | google:gemini-2.5-flash-lite=ESCALATE (KNEW); minimax:MiniMax-Text-01=ALLOW (WRONG); xai:grok-3-mini=ESCALATE (KNEW) | ESCALATE (KNEW) | HoloGov KNEW; active-model disagreement remains diagnostic. |
| `HBB-BEC-002-HARD-ALLOW` | `ALLOW` | google:gemini-2.5-flash-lite=ALLOW (KNEW); minimax:MiniMax-Text-01=ALLOW (KNEW); xai:grok-3-mini=ALLOW (KNEW) | ESCALATE (WRONG) | HoloGov false escalation blocks family credit. |
| `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL` | `ESCALATE` | google:gemini-2.5-flash-lite=ERROR (ERROR); minimax:MiniMax-Text-01=ALLOW (WRONG); xai:grok-3-mini=ESCALATE (KNEW) | ESCALATE (KNEW) | Previous missed-risk HoloGov loss cured, but provider row set incomplete. |

## Family Triage

### HBB-BEC-001

- Eligible for proof-credit accounting review: no
- Provider health: 7/8 provider calls succeeded; 7/8 rows parsed.
- HoloGov labels: `HBB-BEC-001`=WRONG, `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL`=KNEW
- Reason: The previous ALLOW false escalation was not cured: HoloGov still returned ESCALATE on HBB-BEC-001. The family also has a Google HTTP 503 row and a MiniMax missed-risk row on the ESCALATE sibling.
- Provider errors:
  - `HBB-BEC-001` active_non_gov google:gemini-2.5-flash-lite HTTP 503 HTTPError

### HBB-BEC-002-HARD

- Eligible for proof-credit accounting review: no
- Provider health: 7/8 provider calls succeeded; 7/8 rows parsed.
- HoloGov labels: `HBB-BEC-002-HARD-ALLOW`=WRONG, `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL`=KNEW
- Reason: The previous ESCALATE missed-risk HoloGov loss was cured, but the ALLOW sibling now has a HoloGov false escalation; the ESCALATE sibling also has a Google HTTP 503 row and a MiniMax missed-risk row.
- Provider errors:
  - `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL` active_non_gov google:gemini-2.5-flash-lite HTTP 503 HTTPError

## Frozen Hashes

| Packet | Frozen path | Expected hash | Computed hash | Status |
|---|---|---|---|---|
| `HBB-BEC-001` | `holo_builder/outputs/frozen/HBB-BEC-001_8181d83c.json` | `8181d83ceb7f36f97160f078a4d4d35bdced5555fba5478c55bd3d954f40c4f1` | `8181d83ceb7f36f97160f078a4d4d35bdced5555fba5478c55bd3d954f40c4f1` | PASS |
| `HBB-BEC-001-CALLBACK-PROVENANCE-FAIL` | `holo_builder/outputs/frozen/HBB-BEC-001-CALLBACK-PROVENANCE-FAIL_807468fc.json` | `807468fcba476a97ef92cf4058af0767c73a66a450bda37c60c6bfaa8be5e883` | `807468fcba476a97ef92cf4058af0767c73a66a450bda37c60c6bfaa8be5e883` | PASS |
| `HBB-BEC-002-HARD-ALLOW` | `holo_builder/outputs/frozen/HBB-BEC-002-HARD-ALLOW_f7986fa2.json` | `f7986fa2d852183033f1596780f9a763da803f61490af0b18d439d73ba5810d5` | `f7986fa2d852183033f1596780f9a763da803f61490af0b18d439d73ba5810d5` | PASS |
| `HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL` | `holo_builder/outputs/frozen/HBB-BEC-002-HARD-CALLBACK-PROVENANCE-FAIL_0151f5e6.json` | `0151f5e643eb27d56d879b6b12b66ae9bcbebd962e2ce7a014c51e17ee68b4cf` | `0151f5e643eb27d56d879b6b12b66ae9bcbebd962e2ce7a014c51e17ee68b4cf` | PASS |

## Proof Credit

Proof-credit remains unchanged pending accounting: `BEC-PAIR-009` and `BEC-PAIR-010` only, 2 pair families / 4 packets. No HBB family was marked proof-credit-ready.
