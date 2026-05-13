# Public Sanitization Report

**Branch:** `public-sanitization-pass`
**Date:** 2026-05-03
**Scope:** All markdown, JSON, HTML, benchmark docs, payload files, trace examples, and architecture docs

---

## Summary

This pass prepares the Holo Engine repository for public release by removing or relocating materials that expose proprietary adjudication mechanics while preserving full buyer and benchmark credibility.

The goal: public materials explain the problem, demonstrate evidence of action-boundary blind spots, and make the benchmark credible. They do not expose the playbook for rebuilding Holo.

---

## Files Reviewed

| Category | Files |
|----------|-------|
| Root markdown | README.md, BENCHMARK_README.md, MANIFESTO.md, VISION.md, BRAND.md, CLAUDE.md |
| Internal docs | holo.md, holoproductionbrief.md, HOLO_SYSTEM.md, governor_doctrine.md, ARCHITECTUREBENCHMARKBLUEPRINT.md, YC_TRANSCRIPT.md, OPENCLAW_README.md |
| Source code | context_governor.py, llm_adapters.py, benchmark.py, main.py |
| Frontend HTML | index.html, benchmark.html, benchmark-preview.html, whitepaper.html, blindspot-atlas.html |
| Payload JSON | frontend/payloads/*.json (6 public scenarios) |
| Protocol doc | frontend/payloads/BENCHMARK_PROTOCOL.md |
| Scenarios | examples/benchmark_library/scenarios/ (42 files), examples/scenarios/ (multiple) |
| Traces | traces/ (21 trace files, 48 run logs) |
| Results | benchmark_results/ (89 JSON files) |
| Research notes | governor_notes/ (41 files), governor_notes_all_77.txt |
| Docs | docs/whitepaper.md, docs/ARCHITECTURE_PROOF.md, docs/whitepaper-draft.md, docs/drift_detection_insight.md |

---

## Files Changed In Place

### README.md
- Removed phrase "injects assigned roles, shared state, and convergence pressure" — too mechanistically specific
- Added public disclosure notice: "The public benchmark demonstrates the existence of action-boundary blind spots. It does not disclose the proprietary Governor logic..."
- Updated benchmark section to reference NDA for full traces

### BENCHMARK_README.md
- Removed specific convergence delta formula: "delta=0 for 2 consecutive turns after minimum 3 turns"
- Removed `hidden_ground_truth` and `scoring_targets` from public scenario schema
- Replaced full file structure section (which referenced internal paths) with public scenario format description
- Added NDA disclosure block

### frontend/payloads/BENCHMARK_PROTOCOL.md
- **Replaced entirely.** Original contained full 10-turn adversarial role prompts (Turn 1 through Turn 10) with exact prompt text — sufficient to reconstruct the adversarial reactor.
- New version describes methodology at a high level, notes that full role prompts are available under NDA.

### frontend/payloads/index.html
- Updated methodology note to clarify that BENCHMARK_PROTOCOL.md now describes public methodology only, not the full role sequence and convergence rules.

### frontend/blindspot-atlas.html
- **Replaced with a stub.** Original contained `INLINE_DATA` — a JavaScript object embedding full turn-by-turn model reasoning chains for every benchmark scenario. This constitutes full raw trace data.
- New version is a styled notice page directing qualified reviewers to contact hello@holoengine.ai.

### .gitignore
- Added `private_materials_not_for_public_release/` to prevent accidental commit.

---

## Files Moved to `/private_materials_not_for_public_release/`

### Architecture / Implementation Blueprints

| File | Sensitive content |
|------|-------------------|
| `context_governor.py` | Exact Governor verdict formula (majority vote + ANY HIGH forces ESCALATE), constrained shuffle algorithm, early exit conditions (clean bill of health after turn 2), convergence window implementation |
| `governor_doctrine.md` | Exact model family profiles with Governor directives per model (GPT/Claude/Gemini), Blindspot Atlas v1.0 with verified failure modes, role assignment targeting instructions |
| `ARCHITECTUREBENCHMARKBLUEPRINT.md` | `hiddengroundtruth` field references, complete scoring rubrics (0–3 per dimension, 5-dimension normalized to 100), judging stack design |
| `holo.md` | Architecture decision log — evidentiary discipline rule (ESCALATE votes without MEDIUM+ evidence excluded), vote logic edge cases, governor regression testing |
| `holoproductionbrief.md` | Full production readiness analysis sourced from code — harness routing, role selection, implementation specifics |
| `HOLO_SYSTEM.md` | Round-robin rotation mechanics, the "three pilots" system (Captain, Co-Captain, speaking adapters), internal orchestration architecture |
| `BENCHMARK_PROTOCOL_FULL.md` | Full 10-turn adversarial role prompts — complete text for all 10 roles including exact identity provenance rule, threshold clustering tests, rebuttal discipline structure |
| `OPENCLAW_README.md` | Internal API docs with implementation-specific details |

### Trace and Results Data

| File/Directory | Sensitive content |
|---------------|-------------------|
| `traces/` | 21 full markdown trace files — complete turn-by-turn model reasoning chains |
| `governor_notes/` | 41 research notes — per-scenario failure analysis, model-specific blindspot documentation |
| `benchmark_results/` | 89 raw JSON result files — full model outputs, turn reasoning, scoring breakdowns |
| `governor_notes_all_77.txt` | Aggregated analysis across all scenarios |
| `blindspot-atlas.html` | 736KB interactive visualization with embedded `INLINE_DATA` — full model reasoning for every scenario |

### Scenario Library

| File/Directory | Sensitive content |
|---------------|-------------------|
| `examples/benchmark_library/` | Full 42-scenario library — all files contain `expected_verdict`, `hidden_ground_truth`, `scoring_targets` |
| `examples/scenarios/` | Additional scenario files with answer keys |
| `examples/benchmark_spec.md` | Full scenario spec with scoring criteria |

### Internal Strategy and Session Docs

| File | Reason |
|------|--------|
| `YC_TRANSCRIPT.md` | YC application reconstruction — internal session details |
| `2026-04-04-strategy-reseed.md` | Internal strategy session |
| `domain4-flagship-summary.md` | Internal domain analysis |
| `drift_detection_insight.md` | Internal research note |
| `whitepaper-draft.md` | Unpublished draft with editorial notes |
| `docs/ARCHITECTURE_PROOF.md` | Architecture justification doc — reads as implementation blueprint |

---

## Categories of Sensitive Material Removed

### 1. Exact Governor Logic
- Verdict formula: majority vote + ANY HIGH severity forces ESCALATE regardless of majority
- Evidentiary discipline rule: ESCALATE votes without MEDIUM+ findings excluded from tally
- Early exit conditions: clean bill of health after turn 2
- Constrained shuffle algorithm mechanics

### 2. Adversarial Reactor Mechanics
- Full 10-turn role prompt text (complete adversarial reactor reconstruction would require these)
- Model-specific Governor directives (how the Governor briefs each model family based on its known weaknesses)
- Convergence window implementation detail (delta=0 for N consecutive turns)
- Oscillation/stopping heuristics

### 3. Prompting and Orchestration Details
- Complete role prompt chains (Turn 1 through Turn 10) with exact prompt text
- Model-specific identity provenance rule and carve-out text
- Rebuttal discipline structure with exact formatting requirements
- Internal critique instructions for each role

### 4. Scenario Internals
- `hidden_ground_truth` field (correct verdict, fraud type, evidence signals)
- `expected_verdict` field (correct answer)
- `scoring_targets` field (required evidence citations, differentiation notes)
- Full internal scenario library (Tier 2 threshold cases)

### 5. Trace Internals
- Full model-by-model reasoning chains (21 trace files + 89 result JSONs)
- Governor resolution detail from disagreement cases
- Per-model failure pattern analysis (41 governor notes)
- `INLINE_DATA` in blindspot-atlas.html

### 6. Architecture Blueprints
- Three-pilot system (Captain/Co-Captain/speaking adapter orchestration)
- Round-robin rotation implementation detail
- Full production readiness analysis from code

---

## What Remains Public

### Kept — Clean Public Materials

| File | Status |
|------|--------|
| README.md | Sanitized — high-level positioning with NDA notice |
| BENCHMARK_README.md | Sanitized — methodology without internal schema or convergence formulas |
| docs/whitepaper.md | Kept — already well-sanitized; explicitly states Governor logic is proprietary throughout |
| frontend/payloads/BENCHMARK_PROTOCOL.md | Replaced — new public version describes structure without role prompts |
| frontend/payloads/*.json (6 scenarios) | Kept — already clean (only action + context, no labels or answer keys) |
| frontend/payloads/index.html | Sanitized — updated methodology note |
| frontend/blindspot-atlas.html | Replaced — stub with NDA access notice |
| frontend/benchmark.html | Kept — no sensitive data |
| frontend/benchmark-preview.html | Kept — marketing/positioning only |
| frontend/index.html | Kept — landing page |
| frontend/whitepaper.html | Kept — HTML version of whitepaper |
| MANIFESTO.md | Kept — Holo assistant behavioral spec, not Engine mechanics |
| VISION.md | Kept — product vision |
| BRAND.md | Kept — brand guidelines |
| CLAUDE.md | Kept — project-level instructions (scoped to this repo) |

---

## Post-Sanitization Sensitive Term Scan

### Terms confirmed clean in public files

| Term | Status |
|------|--------|
| `hidden_ground_truth` | Removed from all public files |
| `expected_verdict` | Removed from all public files (remains in source .py files as internal variable names — acceptable) |
| `scoring_targets` | Removed from all public files |
| `governor` | Appears in whitepaper as high-level concept — appropriate; implementation specifics redacted |
| `convergence` | Appears in benchmark-preview.html as marketing claim (convergence speed) — appropriate |
| `oscillation` | Not found in public files |
| `decay` | Not found in public files (appears in Python source as internal variable — acceptable) |
| `rubric` | Removed from public markdown; whitepaper references "scoring rubrics" at concept level — appropriate |
| `raw trace` | Not found in public files |
| `model routing` | Appears in whitepaper in "proprietary" context: "model-routing details... are proprietary" — appropriate |
| `turn budget` | Appears in whitepaper appropriately (describing what is NOT disclosed) |
| `architecture blueprint` | Not found in public files |

---

## Remaining Concerns

### 1. Source code is partially public
`llm_adapters.py`, `benchmark.py`, `run_with_trace.py`, `report.py`, `benchmark_proof.py`, and related harness files remain public. These expose:
- Which model families are in use (OpenAI, Anthropic, Google)
- The 4-condition benchmark harness structure
- Turn role name constants (Initial Assessment, Assumption Attacker, etc. — defined in `llm_adapters.py`)

**Assessment:** This level of exposure is consistent with the stated open-source strategy for the benchmark harness. It establishes reproducibility of solo baselines without exposing Governor implementation. Low risk.

**Recommendation:** If desired, move `llm_adapters.py` to private and replace with a stub — this would prevent role name exposure. Tradeoff: reduces benchmark reproducibility credibility.

### 2. `benchmark-preview.html` mentions "Rotating the control model"
Line: "A control plane drawn from the same model family as the analyst cannot reliably challenge it. Rotating the control model through a structurally independent model pool breaks that dependency."

**Assessment:** This is a marketing claim about structural diversity at a high level. It does not reveal the shuffle algorithm, consecutive-pair constraints, or assignment logic. Acceptable.

### 3. `benchmark.html` describes adversarial reactor structure
Mentions "adversarial reactor" as a named concept. Does not reveal turn count, role assignments, or prompts.

**Assessment:** Acceptable — this is part of the public positioning claim.

### 4. `BENCHMARK_README.md` references role names
The new public BENCHMARK_README.md no longer references specific roles. However `llm_adapters.py` (public) contains role name constants. If role names are considered proprietary, `llm_adapters.py` should move to private.

**Assessment:** Role names (Initial Assessment, Assumption Attacker, etc.) are described abstractly in public materials. The specific prompts are withheld. Acceptable.

---

## NDA Language Added

The following language appears in README.md, BENCHMARK_README.md, and BENCHMARK_PROTOCOL.md:

> "Public benchmark materials are intentionally limited to preserve the integrity of the evaluation harness and protect proprietary adjudication mechanics. Full traces, payloads, and reproducibility materials are available to qualified technical reviewers under NDA."

> "The public benchmark demonstrates the existence of action-boundary blind spots. It does not disclose the proprietary Governor logic, adversarial reactor configuration, model-routing rules, convergence heuristics, or private trace library used in Holo's production architecture."

---

## Recommendation Before Merging to Main

1. **Rotate all API keys** — .env contains live credentials. Rotate before any public push.
2. **Decide on source code exposure** — If `llm_adapters.py` role name constants are considered proprietary, move to private now. Otherwise acceptable at current level.
3. **Confirm whitepaper.html sync** — `docs/whitepaper.md` was not modified; `frontend/whitepaper.html` should be verified to match.
4. **Do not push this branch** — Per instructions, no push has been made. Merge to main only after credential rotation and final review.
