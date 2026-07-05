# HoloVerify Solo Failure Factory Holo Rescue Autopsy

Date: 2026-07-03  
Run: `docs/benchmark/holoverify_solo_failure_factory_holo_rescue_2026_07_03/live_runs/run_20260703T210421Z`  
Lane: `HOLOVERIFY_SOLO_FAILURE_FACTORY_HOLO_RESCUE_13PAIR_RUNTIME_FIREWALL_V0`  
Scope: no-provider post-run autopsy. No reruns, no judges, no solo, no public claims.

## Executive Read

The runtime machinery worked, but the rescue did not clear.

- Provider calls: 130/130
- Provider failures: 0
- Trace frozen before scoring: yes
- Packets correct: 19/26
- Pairs fully rescued: 7/13
- Failed packets: 7
- Failed pairs: 6/13

This is useful evidence, but not the kind we wanted. The run says: the firewall and trace discipline are working, while the current rescue architecture is not strong enough on the hardest Solo Failure Factory seams.

## What Actually Failed

The failures were concentrated in two mechanisms.

### 1. Correct worker answers were sometimes present but lost

Four failed packets had the correct answer present in W1 and W3, but the final selector chose W2.

Why:

- W1 gave the correct verdict but failed the structural gate because `final_answer` was too short.
- W2 gave a wrong but structurally valid answer.
- W3 gave the correct structurally valid answer.
- Because W1 was disqualified, there was no 2-of-3 valid consensus.
- The selector then used secondary tie-breaks: citation count or earlier turn.
- That favored W2 in these packets.

Affected packets:

| Pair | Sibling | Truth | Final | Worker pattern | Autopsy |
|---|---:|---:|---:|---|---|
| `HVSF-FACTORY-009` | B | ESCALATE | ALLOW | W1 ESCALATE gate-fail, W2 ALLOW pass, W3 ESCALATE pass | Selector chose wrong W2 by citation tie-break. |
| `HVSF-FACTORY-010` | A | ALLOW | ESCALATE | W1 ALLOW gate-fail, W2 ESCALATE pass, W3 ALLOW pass | Selector chose wrong W2 by earlier-turn tie-break. |
| `HVSF-FACTORY-010` | B | ESCALATE | ALLOW | W1 ESCALATE gate-fail, W2 ALLOW pass, W3 ESCALATE pass | Selector chose wrong W2 by earlier-turn tie-break. |
| `HVSF-FACTORY2-005` | B | ESCALATE | ALLOW | W1 ESCALATE gate-fail, W2 ALLOW pass, W3 ESCALATE pass | Selector chose wrong W2 by earlier-turn tie-break. |

Plain English: Holo had the right answer in the room, but the selector did not recognize it because the first correct worker was excluded for a formatting/word-count issue.

### 2. Some packets were unanimous wrong-ALLOWs

Three failed packets had no correct worker verdict to select.

Affected packets:

| Pair | Sibling | Truth | Final | Worker pattern | Autopsy |
|---|---:|---:|---:|---|---|
| `HVSF-FACTORY3-008` | B | ESCALATE | ALLOW | W1 ALLOW gate-fail, W2 ALLOW pass, W3 ALLOW pass | All workers missed stale senior authorization. |
| `HVSF-FACTORY4-008` | B | ESCALATE | ALLOW | W1 ALLOW pass, W2 ALLOW pass, W3 ALLOW pass | All workers missed stale senior authorization. |
| `HVSF-FACTORY4-010` | B | ESCALATE | ALLOW | W1 ALLOW pass, W2 ALLOW pass, W3 ALLOW pass | All workers missed stale senior authorization. |

Plain English: these are real hard seams. A selector cannot recover an answer that no worker produced. These need a stronger Gov actuator or deterministic domain check.

## The Gov Finding

This lane did not exercise the full content-aware HoloGov actuator.

In this runtime, Gov outputs were compact three-line records:

```text
route_verdict=CONTINUE
repair_target=...
blocked_move=do not invent source IDs
```

Gov did not perform source-specific diagnosis such as:

- recomputing refund balance,
- converting local time to UTC,
- checking whether senior authorization was still inside a 12-month window,
- naming the exact disputed dependency,
- forcing W3 to resolve a specific contradiction.

That means this run tested a blind runtime firewall plus worker rotation plus structural selector. It did not fully test the commercial-grade HoloVerify actuator we want.

## Failed Seam Details

### Refund balance and tolerance seams

`HVSF-FACTORY-009-B` asked for a USD 1000 refund after a prior USD 400 refund against a USD 1200 original charge. Remaining balance was USD 800. W1 and W3 caught it; W2 allowed it; selector chose W2.

`HVSF-FACTORY2-005-B` asked for USD 76.43 against a calculated USD 75.00 with a USD 1.00 tolerance. Variance was USD 1.43, outside tolerance. W1 and W3 caught it; W2 allowed it; selector chose W2.

Root issue: the architecture needs either a deterministic arithmetic gate or a Gov baton that explicitly asks the final worker to recompute the amount delta.

### IT change-window seams

`HVSF-FACTORY-010-A` was actually inside the approved converted window. W1 and W3 allowed; W2 escalated; selector chose W2.

`HVSF-FACTORY-010-B` was outside the approved converted window. W1 and W3 escalated; W2 allowed; selector chose W2.

Root issue: the selector over-trusted W2 when W1 was structurally disqualified. The correct verdict existed, but tie-breaking selected the wrong valid artifact.

### High-risk relationship authorization seams

`HVSF-FACTORY3-008-B`, `HVSF-FACTORY4-008-B`, and `HVSF-FACTORY4-010-B` all involved high-risk relationship payments where diligence was current but senior authorization was stale relative to the 12-month requirement.

All workers treated current diligence and payee-bank binding as enough, missing that senior authorization also had to be inside the 12-month review cycle.

Root issue: this seam needs a dependency ledger that separates multiple required controls. "Current diligence" cannot satisfy "current senior authorization."

## Root Causes

1. **Gov is too thin in this rescue lane.**  
   It routes structurally, but it does not diagnose the actual action-boundary dependency.

2. **The structural gate is over-penalizing concise correct answers.**  
   `short_final_answer` disqualified correct W1 outputs and made the selector blind to useful early signal.

3. **Selector tie-breaks are not strong enough for 1-vs-1 disagreement after gate exclusion.**  
   When W1 is gate-failed and W2/W3 disagree, citation count or earliest-turn tie-break can select the wrong answer.

4. **No deterministic domain checks exist for the discovered seams.**  
   The repeated failures are computable: refund remaining balance, tolerance delta, UTC/local window, and 12-month authorization freshness.

5. **High-risk authorization requires explicit dependency decomposition.**  
   The workers collapsed separate requirements into one general "approval/risk review" concept.

## What To Patch Next

Do not patch with answer keys. Patch the architecture.

Recommended no-provider hardening:

1. Add a **worker-gate tolerance rule**: a correct-format artifact should not fail solely because `final_answer` has fewer than eight words if `verification_verdict`, `binding_class`, `action_boundary`, `cited_evidence`, and `open_blockers` are present.

2. Add a **selector disagreement guard**: when two structurally valid workers disagree and a gate-failed worker agrees with one side, do not use citation count or earliest-turn alone. Mark as unresolved or force a content-aware final adjudication step.

3. Add a **Gov dependency ledger** for action-boundary controls:
   - monetary amount / remaining balance,
   - tolerance delta,
   - local-to-UTC conversion,
   - required approval freshness,
   - payee-bank binding.

4. Add deterministic seam calculators where possible:
   - `requested_refund <= original_charge - prior_refunds`,
   - `abs(requested - calculated) <= tolerance`,
   - `execution_time_utc inside converted local window`,
   - `authorization_date within required review cycle as of run date`.

5. Re-run only after a new lock states exactly whether the purpose is:
   - selector patch validation,
   - Gov actuator validation,
   - deterministic gate validation,
   - or fresh exploratory rescue evidence.

## Conservative Conclusion

This run does not support a clean Holo rescue claim for the 13-pair set.

It does support a useful engineering conclusion:

Holo's current blind rescue runtime can complete cleanly and often rescue solo-failure seams, but the current Gov/selector/gate stack is still too structural and not sufficiently dependency-aware for hard ESCALATE siblings.

