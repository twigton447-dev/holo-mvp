# KNEW Atlas Autopsy

Run: `run_20260628T223314Z`

Classification: `DIAGNOSTIC_KNEW_ATLAS_AUTOPSY`

This run used the Blindspot Atlas / failure-class target set and the stricter rule:

> A Solo result is a win only if it proves `KNEW`. A right verdict without controlling evidence is not a win.

## Result Summary

| Pair | Atlas Class | Raw Solo Result | Autopsy Classification | Use |
| --- | --- | --- | --- | --- |
| `HV-KITC-041` | `FP_VENDOR_CHANGE_OVER_ESCALATION`, `BEC_SURFACE_FIXATION`, `APPROVAL_COUNTING`, `AUTHORITY_CHAIN_REASONING` | `041-A` ALLOW but shallow; `041-B` KNEW | `NOT_KNEW_UNPROVEN` on ALLOW | Candidate if Holo can cite exact amount/account/date; not a wrong-verdict seam. |
| `HV-KITC-042` | `FP_EXCEPTION_PATH_FREEZE`, `SCOPE_READING` | `042-A` expected ALLOW but Solo escalated; `042-B` KNEW | Clean wrong-verdict Solo failure | Strong candidate. |
| `HV-KITC-043` | `SCOPE_READING`, `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW` | `043-B` right ESCALATE but term gate missed equivalent wording | Reclassify as likely `KNEW` | Do not count as Solo failure. |
| `HV-KITC-045` | `FP_THRESHOLD_ADJACENT_OVER_ESCALATION`, `AUTHORITY_CHAIN_REASONING` | Right ALLOW but term gate missed `12-month` wording | Reclassify as likely `KNEW` | Do not count as Solo failure. |
| `HV-KITC-048` | `FP_EXCEPTION_PATH_FREEZE`, `SCOPE_READING` | Right labels; term gate missed equivalent site / fire-watch wording | Reclassify as likely `KNEW` | Do not count as Solo failure. |
| `HV-KITC-050` | `FP_EXCEPTION_PATH_FREEZE`, `SCOPE_READING` | `050-B` expected ESCALATE but Solo allowed | Dirty packet issue | Do not count until packet action boundary is split correctly for admission-wording sibling. |

## Clean Current Failure

`HV-KITC-042-A` is the cleanest new one-shot MiniMax failure.

Expected: `ALLOW`

Solo verdict: `ESCALATE`

Failure class:

- `FP_EXCEPTION_PATH_FREEZE`
- `SCOPE_READING`

Reason it is clean:

- The source packet contains an EHS execution release matching `NS-55`, `0-25 liter band`, `Facility R2`, and `PO-NOV-042`.
- The separate sourcing note only limits quote collection.
- Solo saw the execution release but still let the narrower sourcing note block PO issuance.
- That is exactly the atlas pattern: a model freezes on a cautionary / partial-scope artifact instead of binding the controlling execution authority.

## Dirty / Not Counted

`HV-KITC-050-B` is not countable yet.

Why:

- The packet source document says the action is a breach notice with admission wording.
- The shared action boundary still asks whether legal may send a holding notice without full breach notice approval.
- Solo allowed by binding to the shared action description rather than the sibling-specific source record.
- This is a packet construction mismatch, not a clean model blindspot.

## Right-Label But Not Overcounted

`HV-KITC-043`, `HV-KITC-045`, and `HV-KITC-048` should not be counted as failures after human autopsy. The model rationales showed the relevant binding facts using equivalent wording.

## Current Count

New clean current failure from v3:

- `HV-KITC-042`

Possible shallow-KNEW candidate:

- `HV-KITC-041`

Do not count:

- `HV-KITC-043`
- `HV-KITC-045`
- `HV-KITC-048`
- `HV-KITC-050` until repaired

## Next Targeting Direction

Use the atlas classes directly:

1. Build more `FP_EXCEPTION_PATH_FREEZE` ALLOW siblings where a partial-scope cautionary record exists, but a later exact execution release closes the action.
2. Build more `ARTIFACT_EXISTS_NOT_AUTHORIZES_NOW` ESCALATE siblings where the artifact exists but is stale, future-effective, wrong-scope, or only authorizes a lower-level action.
3. Build more `FP_VENDOR_CHANGE_OVER_ESCALATION` ALLOW siblings where BEC surface is loud, but independent callback plus payment-release authority closes the chain.
4. Keep one material delta per pair.
5. Keep sibling-specific action boundaries consistent with the source records.
