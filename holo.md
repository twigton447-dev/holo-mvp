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
