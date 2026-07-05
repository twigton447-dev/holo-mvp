# Hard ALLOW FP 5-Pair Benchmark Analysis

Status: `FROZEN_LOCAL_ANALYSIS_PENDING_EXTERNAL_JUDGES`

Freeze root signature: `47434052ed594ed65734e1e964434ae984a17777607fc72ad1c6424dd4de83f6`

Run directory: `docs/benchmark/hard_allow_fp_5pair_solo_fullholo_knew_benchmark_2026-06-28/run_20260629T000225Z`

## Scope

This analysis covers the locked 5-pair / 10-packet hard-ALLOW false-positive set:

- 5 hard-ALLOW siblings
- 5 ESCALATE guardrail siblings
- Holo full traces reused from the frozen full-architecture bundle
- 10 MiniMax Solo one-shot calls run against the same packets
- KNEW-only scoring: `KNEW` is the only passing label; `LUCKY`, `WRONG`, and `CONFUSED` fail

Official external judge adjudication is still pending. This file is a local benchmark analysis over frozen artifacts, local deterministic KNEW labels, and saved traces.

Local Codex trace judgment has also been saved as `LOCAL_CODEX_TRACE_JUDGMENT.md` and `LOCAL_CODEX_TRACE_JUDGMENT.json`. It is file-backed and reviews all 20 artifacts, but it is explicitly not an external independent judge result.

An inside-Holo worker-solo autopsy has also been saved separately at `docs/benchmark/inside_holo_worker_solo_autopsy_2026-06-29/`. It scores each frozen Holo worker turn as a standalone solo artifact and counts failures before HoloGov or the final selector corrected them.

## Current Result

| Lane | Provider calls | Local KNEW passes | Local KNEW rate |
| --- | ---: | ---: | ---: |
| Solo one-shot MiniMax | 10 | 7/10 | 70% |
| Full HoloVerify | 50 | 10/10 | 100% |

Local KNEW differential: Holo is `+3` packets and `+30` percentage points over Solo on this locked set.

## Boundary-Reliability Interpretation

The claim is not that Solo always fails. In this run, Solo correctly reached `KNEW` on 7 of 10 packets. That matters because the control is not a straw man.

The claim supported by this set is narrower and stronger: Solo is unreliable at the action boundary. Across matched ALLOW/ESCALATE siblings, the one-shot Solo lane sometimes reads the decisive source condition correctly and sometimes collapses into one of three failure modes:

- over-escalating a hard ALLOW where the dependency was actually closed;
- returning malformed/confused output at the exact guardrail seam;
- reaching the right verdict without proving the controlling source term, which is `LUCKY`, not `KNEW`.

Full HoloVerify cleared all 10 local KNEW gates on the same locked packet set, including both the hard-ALLOW exception/dependency closures and their ESCALATE siblings. That is the current action-boundary reliability signal.

The inside-Holo autopsy sharpens this point: the same MiniMax substrate inside Holo produced `6/30` internal failure events before correction across `5/10` packets. Holo's final `10/10` KNEW result therefore comes from governance and correction, not from every worker call being individually perfect.

## Token Cost

| Lane | Input tokens | Output tokens | Total tokens |
| --- | ---: | ---: | ---: |
| Solo one-shot MiniMax | 6,073 | 11,941 | 18,014 |
| Full HoloVerify frozen traces | 122,324 | 60,378 | 182,702 |

Full HoloVerify used `164,688` more total tokens than Solo, or about `10.14x` Solo's total token volume.

## Packet-Level Local KNEW Results

| Packet | Kind | Solo local label | Holo local label | Local interpretation |
| --- | --- | --- | --- | --- |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021-A` | hard_allow | WRONG | KNEW | Solo over-escalated a closed hard-ALLOW source boundary. |
| `BAL100-BEC-SUBTLE-CLOSEOUT-021-B` | escalate | CONFUSED | KNEW | Solo returned malformed/truncated JSON; Holo produced a source-bound escalation. |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-A` | hard_allow | KNEW | KNEW | Both lanes knew the ALLOW boundary. |
| `BAL100-BEC-SUBTLE-CLOSEOUT-022-B` | escalate | KNEW | KNEW | Both lanes knew the ESCALATE boundary. |
| `HV-KITC-042-A` | hard_allow | KNEW | KNEW | Both lanes knew the ALLOW boundary. |
| `HV-KITC-042-B` | escalate | LUCKY | KNEW | Solo reached ESCALATE but missed the required controlling term; Holo knew the boundary. |
| `HV-KITC-047-A` | hard_allow | KNEW | KNEW | Both lanes knew the ALLOW boundary. |
| `HV-KITC-047-B` | escalate | KNEW | KNEW | Both lanes knew the ESCALATE boundary. |
| `HV-KITC-082-A` | hard_allow | KNEW | KNEW | Both lanes knew the ALLOW boundary. |
| `HV-KITC-082-B` | escalate | KNEW | KNEW | Both lanes knew the ESCALATE boundary. |

## What This Proves Now

The current frozen local evidence supports a bounded claim:

Full HoloVerify achieved local deterministic/source-term KNEW on all 10 locked packets, while MiniMax Solo one-shot achieved local KNEW on 7 of 10. The three Solo non-passes were one wrong hard-ALLOW over-escalation, one malformed/confused ESCALATE output, and one lucky ESCALATE that lacked a required controlling source term.

## What This Does Not Prove Yet

This is not yet an official externally judged benchmark result. External judge outputs have not been run and saved for this comparison because the judge packet contains frozen source packets, Solo outputs, Holo selected artifacts, and trace summaries that would be transferred to external judge providers.

Until external judges are run and validated, the official status remains:

`COMPLETE_WITH_JUDGE_GAPS`

The local Codex trace judgment status is:

`LOCAL_CODEX_TRACE_JUDGMENT_NON_EXTERNAL`

## Required Next Gate

To finish the benchmark objective, run the judge-only continuation against the existing run directory. Do not rerun Solo. Do not rerun Holo.

The runner now requires an explicit external-transfer unlock flag before it will send the judge packet to external providers:

```bash
python3 -B docs/benchmark/run_hard_allow_fp_5pair_solo_and_knew_judges_2026_06_28.py \
  --judge-existing-run-dir docs/benchmark/hard_allow_fp_5pair_solo_fullholo_knew_benchmark_2026-06-28/run_20260629T000225Z \
  --allow-external-judge-transfer
```

After judges complete, the run must be re-locked with the judge outputs included.
