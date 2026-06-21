# HoloGovernor Taxonomy

Status: canonical architecture naming lock.

Purpose: keep HoloGovernor naming precise across HoloChat, HoloVerify, HoloBuild, and HoloJudge work. These names are product and architecture terms. Existing implementation filenames may lag this taxonomy for compatibility.

## Core Hierarchy

- HoloGovernor = core governing architecture family.
- HoloContext = context-control subsystem inside HoloGovernor.
- HoloBrain = durable cognition/state layer.
- HoloGov-C = HoloGovernor Chat, responsible for HoloChat continuity and context admission.
- HoloGov-V = HoloGovernor Verify, responsible for action-boundary adjudication and ALLOW/ESCALATE.
- HoloGov-B = HoloGovernor Build, responsible for artifact refinement and freeze readiness.
- HoloGov-J = HoloGovernor Judge, responsible for evaluation and scoring if needed.
- ContextGovernor = legacy/internal implementation term only. Do not treat it as the universal HoloGovernor.

## Surface Boundaries

HoloGov-C uses HoloContext to budget-gate HoloBrain state into private model context. Its state covers continuity: rolling summary, durable user/project state, artifact references, open loops, decision history, next-turn baton, context admission, private reseed, and continuity audit.

HoloGov-V uses HoloContext to manage action goal, evidence coverage, findings, baton, audit, and final ALLOW/ESCALATE. Its state covers action-boundary adjudication, not open-ended chat continuity.

HoloGov-B uses HoloContext to manage artifact state, critique pressure, refinement loops, pinned artifacts, readiness checks, and freeze boundaries.

HoloGov-J uses HoloContext to manage evaluation packets, scoring state, rubric coverage, audit evidence, and judge-ready outputs if that surface is active.

Do not collapse HoloChat continuity state into HoloVerify action-evaluation state.

## Implementation Boundary

HoloBrain is the durable cognition/state layer. It stores and retrieves continuity material such as rolling summaries, project memory, artifact references, settled decisions, open loops, and baton pass data.

HoloContext is the admission and packaging layer. It decides what portion of HoloBrain or surface-specific state may enter private model context on a turn: full reseed, rolling summary, short baton, artifact references, hashes/audit only, or none.

HoloGovernor is the governing family that applies HoloContext differently by surface. HoloGov-C, HoloGov-V, HoloGov-B, and HoloGov-J are distinct surface governors. Shared doctrine does not mean shared runtime state.

Compatibility note: `ContextGovernor` may remain as an implementation class or legacy file name while compatibility requires it. New architecture language should prefer HoloGovernor plus the surface code name.
