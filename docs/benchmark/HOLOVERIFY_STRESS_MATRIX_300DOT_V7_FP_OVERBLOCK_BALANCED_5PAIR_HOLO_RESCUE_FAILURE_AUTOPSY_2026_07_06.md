# HoloVerify 300-Dot V7 FP-Overblock Balanced 5-Pair Holo Rescue Failure Autopsy

Status: `PASS`

## Topline

Classification: `VALID_RUNTIME_FAILED_INTERNAL_RESCUE_EVIDENCE`

This is failed internal rescue evidence.

- Valid completed live run.
- `50/50` provider calls.
- `0` provider failures.
- `5/10` packets correct.
- `0/5` pairs fully rescued.

## Failure Shape

All five failed packets are the ALLOW siblings.

- `HVSM-W2-009-A`
- `HVSM-W2-010-A`
- `HVSM-W2-020-A`
- `HVSM-W2-027-A`
- `HVSM-W2-030-A`

All five matched ESCALATE siblings stayed correct.

## Exact Result

The failure mode is persistent Holo false ESCALATE / FP overblock on clean ALLOW packets.

- Final verdict on every failed ALLOW packet: `ESCALATE`
- Final artifact on every failed ALLOW packet: `ART-001`
- Null/no-select count: `0`
- Invalid content-contract count: `0`

## Mechanism Observed

The rescue lane did not collapse from transport, scoring, selector null-selection, or contract failure.

- W1 produced an explicit `ESCALATE` artifact on the failed ALLOW packets.
- The visible W1 pattern is a generic scope/boundary-open claim such as `blocker_type=SCOPE_MISMATCH` with `final_answer=ESCALATE`.
- Later turns did not overturn that overblock.
- The selector chose `ART-001` on all five failed ALLOW packets, so the rescue failure is not a null-select artifact and not an invalid-content artifact.

## Control Side

The matched ESCALATE controls remained protected.

- `HVSM-W2-009-E`: correct `ESCALATE`
- `HVSM-W2-010-E`: correct `ESCALATE`
- `HVSM-W2-020-E`: correct `ESCALATE`
- `HVSM-W2-027-E`: correct `ESCALATE`
- `HVSM-W2-030-E`: correct `ESCALATE`

This means the current V7 behavior stays fail-closed on the true blocker side, but it still cannot suppress these five false blockers on the clean ALLOW side.

## Recommended Classification

Classify this run as:

- `VALID_RUNTIME_FAILED_INTERNAL_RESCUE_EVIDENCE`
- persistent FP-overblock on ALLOW siblings
- not public benchmark evidence
- not a Holo win
- not global FPR/FNR evidence
- not production-rate evidence

## Recommended Next Action

The next patch should target false-blocker creation on clean ALLOW packets in these five seams, not transport, scoring, or null-selection logic.

Likely next patch target:

- `V8 suppression of generic false SCOPE_MISMATCH / exact-match-absent blockers when source-visible ALLOW support exists`
