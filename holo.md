# Holo — Architecture and Decision Log

This file is the permanent record of key findings, architectural principles, and design decisions.
It is the source of truth. Entries are dated and append-only.

---

## 2026-04-04 — Evidentiary Discipline Rule

We identified and fixed a core false-positive failure mode in the governor majority vote logic.

**Before:** A turn could vote ESCALATE with all flags LOW/NONE and that vote counted equally in the majority tally.

**After:** ESCALATE votes with no evidentiary basis are excluded. Only ESCALATE votes backed by at least one MEDIUM+ finding count.

**Principle:** A model is allowed to be suspicious. It is not allowed to convert suspicion into a counted verdict without naming what it found. No evidence, no vote.

**Regression result:**
- BEC-FP-001 → ALLOW ✓
- BEC-FP-002 → ALLOW ✓
- BEC-FP-003 → ALLOW ✓
- BEC-PHANTOM-DEP-003A → ESCALATE ✓
- BEC-SUBTLE-003 → ESCALATE ✓

---

## 2026-04-04 — SUBTLE-004 Gate 1 Failure

BEC-SUBTLE-004 failed Gate 1. Holo returned ALLOW in 2 turns via clean exit. Both Turn 1 (Gemini) and Turn 2 (Claude) voted ALLOW with all flags LOW. The scenario signal is not subtle enough to survive a minimal two-turn adversarial pass.

Status: Demo-grade. Returned to design queue.
Needs: Stronger hidden signal that requires inference, not just pattern recognition.

---
## Daily Close: 2026-04-05

### 1. System Changes: Evidentiary Discipline Fix

**Problem:** Identified a systematic false-positive failure mode. The governor was counting `ESCALATE` votes from models that found zero evidence of risk (all flags `LOW`/`NONE`). This allowed persona pressure alone to tip clean transactions into false-positive `ESCALATE` outcomes.

**Fix:** A one-line change was made to `context_governor.py` in the majority vote logic. `ESCALATE` votes with no evidentiary basis (no `MEDIUM` or `HIGH` findings) are now excluded from the tally.

**Regression Test Result:**
- **Precision:** `BEC-FP-001`, `FP-002`, `FP-003` all now correctly return `ALLOW`.
- **Recall:** `BEC-PHANTOM-DEP-003A` and `BEC-SUBTLE-003` still correctly return `ESCALATE`.
- **Conclusion:** The fix improved precision without weakening fraud detection.

### 2. Learnings & Calibrations

**Architectural Principle:** The "Evidentiary Discipline" rule is now a core part of Holo's architecture. A model is allowed to be suspicious; it is not allowed to convert suspicion into a counted verdict without naming what it found. No evidence, no vote.

**AP/BEC (Domain 1) Status Update:** This domain is now considered complete and calibrated. The four-scenario structure is confirmed:
- **Floor Case:** `BEC-SUBTLE-003` (all models catch it).
- **Threshold/Gap Case:** `BEC-PHANTOM-DEP-003A` (solo Claude misses, others catch).
- **Precision Cases:** `BEC-FP-001`, `FP-002`, `FP-003` (all clear correctly).
- **Design Queue:** `BEC-THRESHOLD-001` and `BEC-SUBTLE-004` failed and are parked. AP/BEC is strong enough to proceed without them.

**Strategic Shift:** The work has moved from making things *better* to making things *true*. The benchmark is not just a proof artifact; it is the primary instrument for forcing architectural rigor and discovering the rules of judgment.

### 3. Next Session

The only priority is starting Domain 4 (Agentic Commerce).

**First action:** Run the minimal "Echo Chamber" probe against solo GPT to find a real seam before building the full harness.

**Command:** `run_probe AGENTIC-ECHO-001 holo`
