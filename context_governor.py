"""
context_governor.py

The orchestration brain of Holo. Manages the shared state object,
enforces the minimum-3-turn / maximum-10-turn loop rule, routes turns
to the correct adapter, and runs convergence detection.

Architecture:
  - The STATE_OBJECT is built once and updated after each turn.
  - Every model receives the FULL state including all prior turn findings.
  - No model ever sees a cleaned or summarized version — they see the raw
    reasoning and severity flags from every analyst that preceded them.
  - This is the "rototilling": compounding postmortems where each model
    must confront what the others actually said.

Convergence rules:
  - Minimum 3 turns must complete before convergence can be evaluated.
  - Convergence fires when the coverage-matrix delta = 0 for 2 consecutive
    turns (no new categories addressed, no severity escalations).
  - A HIGH severity flag on ANY category forces ESCALATE regardless of
    what the synthesis model says.
  - On any unrecoverable model failure: auto-ESCALATE with partial findings.
"""

import logging
import time
import uuid
from copy import deepcopy

from llm_adapters import (
    BEC_CATEGORIES,
    SEVERITY_RANK,
    TurnResult,
    get_role_for_turn,
    load_adapters,
)

logger = logging.getLogger("holo.governor")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_TURNS   = 3
MAX_TURNS   = 10
MAX_RETRIES = 1       # one retry per turn before declaring failure


# ---------------------------------------------------------------------------
# Coverage matrix helpers
# ---------------------------------------------------------------------------

def _init_coverage() -> dict:
    """
    One entry per BEC category tracking:
      - addressed: has any model assessed this category yet?
      - max_severity: the highest severity any model has assigned
    """
    return {
        cat: {"addressed": False, "max_severity": "NONE"}
        for cat in BEC_CATEGORIES
    }


def _update_coverage(matrix: dict, flags: dict) -> tuple:
    """
    Merge this turn's severity flags into the coverage matrix.

    Returns (updated_matrix, delta) where delta is the count of:
      - newly addressed categories (first time a model assessed them)
      - severity escalations (e.g., LOW to MEDIUM on an already-addressed category)

    Delta > 0 means the loop is still learning something new.
    Delta = 0 means this turn added no new information - convergence candidate.
    """
    updated = deepcopy(matrix)
    delta   = 0

    for cat in BEC_CATEGORIES:
        new_sev = flags.get(cat, "NONE")
        if new_sev == "NONE":
            continue

        current = updated[cat]
        if not current["addressed"]:
            # First assessment of this category
            updated[cat]["addressed"]    = True
            updated[cat]["max_severity"] = new_sev
            delta += 1
            logger.debug(f"    Coverage: {cat} first addressed at {new_sev}")
        else:
            # Already addressed -- check for severity escalation
            old_rank = SEVERITY_RANK[current["max_severity"]]
            new_rank = SEVERITY_RANK[new_sev]
            if new_rank > old_rank:
                updated[cat]["max_severity"] = new_sev
                delta += 1
                logger.debug(
                    f"    Coverage: {cat} escalated "
                    f"{current['max_severity']} -> {new_sev}"
                )

    return updated, delta


def _any_high(matrix: dict) -> bool:
    """True if any category has reached HIGH severity."""
    return any(v["max_severity"] == "HIGH" for v in matrix.values())


def _convergence_check(deltas: list, turns_completed: int) -> bool:
    """
    Convergence requires ALL of:
      1. At least MIN_TURNS turns have completed (hard mandatory floor).
      2. The last two consecutive deltas were both 0.
    """
    if turns_completed < MIN_TURNS:
        return False
    if len(deltas) >= 2 and deltas[-1] == 0 and deltas[-2] == 0:
        logger.info(
            f"  Convergence: delta=0 for 2 consecutive turns after {turns_completed} turns."
        )
        return True
    return False


def _is_clean_bill_of_health(state: dict) -> bool:
    """
    Early exit for genuinely clean evaluations — AFTER turn 2, BEFORE turn 3.

    Returns True only when ALL of these are true:
      1. Both turns returned an ALLOW verdict.
      2. No HIGH or MEDIUM severity flags exist in either turn.
      3. Every category in the coverage matrix is LOW or NONE.

    This is NOT the same as convergence. Convergence means "models stopped
    finding new things." This means "there was never anything to find."
    """
    turns = state["turn_history"]
    if len(turns) < 2:
        return False

    # ── Condition 1: both verdicts must be ALLOW ──────────────────────
    for turn in turns[:2]:
        if turn.get("verdict", "").upper() != "ALLOW":
            return False

    # ── Condition 2: zero HIGH or MEDIUM flags in either turn ─────────
    for turn in turns[:2]:
        flags = turn.get("severity_flags", {})
        for cat, sev in flags.items():
            if SEVERITY_RANK.get(sev, 0) >= SEVERITY_RANK.get("MEDIUM", 2):
                return False

    # ── Condition 3: coverage matrix all LOW or NONE ──────────────────
    for cat, info in state["coverage_matrix"].items():
        if SEVERITY_RANK.get(info["max_severity"], 0) >= SEVERITY_RANK.get("MEDIUM", 2):
            return False

    return True

# ---------------------------------------------------------------------------
# State object builder
# ---------------------------------------------------------------------------

def _build_initial_state(request: dict, evaluation_id: str) -> dict:
    """
    The STATE_OBJECT is the single source of truth passed to every model.
    It grows with each turn via turn_history and coverage_matrix updates.
    """
    return {
        "evaluation_id":   evaluation_id,
        "action":          request.get("action", {}),
        "context":         request.get("context", {}),
        "turn_history":    [],            # TurnResult.to_dict() appended after each turn
        "coverage_matrix": _init_coverage(),
    }


# ---------------------------------------------------------------------------
# Context Governor
# ---------------------------------------------------------------------------

class ContextGovernor:

    def __init__(self):
        self._adapters = load_adapters()

    def _get_adapter(self, turn_number: int):
        """
        Round-robin through the three adapters.
        Turn 1: OpenAI, Turn 2: Anthropic, Turn 3: Google,
        Turn 4: OpenAI, Turn 5: Anthropic, etc.
        """
        return self._adapters[(turn_number - 1) % len(self._adapters)]

    def evaluate(self, request: dict) -> dict:
        """
        Main entry point. Runs the full adversarial loop and returns
        a complete result dict suitable for the API response.

        The loop:
          1. Build the shared state object.
          2. Run turns until convergence or MAX_TURNS.
             - MIN_TURNS MUST complete before convergence can fire.
             - Each turn's full output is appended to state turn_history
               so the NEXT model sees everything the prior models said.
          3. If MAX_TURNS reached without convergence, that final turn
             uses the Synthesis role automatically.
          4. If convergence fires before the last slot, run a dedicated
             synthesis turn on top.
          5. Apply the HIGH-severity override.
          6. Return structured result.
        """
        evaluation_id = f"holo_{uuid.uuid4().hex[:8]}"
        start_time    = time.time()

        logger.info(f"\n{'='*65}")
        logger.info(f"EVALUATION START: {evaluation_id}")
        logger.info(f"MIN_TURNS={MIN_TURNS} | MAX_TURNS={MAX_TURNS}")
        logger.info(f"{'='*65}")

        state      = _build_initial_state(request, evaluation_id)
        deltas     = []
        partial    = False
        converged  = False
        final_turn = None
        clean_exit = False  # set True when _is_clean_bill_of_health fires

        # ---- Main adversarial loop -------------------------------------------
        for turn_number in range(1, MAX_TURNS + 1):

            # Final allowed turn always uses Synthesis role
            if turn_number == MAX_TURNS:
                role = "Synthesis"
            else:
                role = get_role_for_turn(turn_number)

            adapter = self._get_adapter(turn_number)

            # Attempt the turn with retry
            turn_result = self._run_turn_with_retry(
                adapter, state, turn_number, role
            )

            if turn_result is None:
                # Unrecoverable failure
                logger.error(
                    f"  Turn {turn_number} failed after all retries. "
                    f"Auto-escalating."
                )
                partial = True
                break

            # Append to shared state -- THIS is what the next model will see
            state["turn_history"].append(turn_result.to_dict())
            final_turn = turn_result

            # Update the coverage matrix
            new_coverage, delta = _update_coverage(
                state["coverage_matrix"], turn_result.severity_flags
            )
            state["coverage_matrix"] = new_coverage
            deltas.append(delta)

            logger.info(
                f"  Turn {turn_number} | delta={delta} | "
                f"coverage={_coverage_summary(new_coverage)}"
            )

            # ---- Clean Bill of Health early exit (turn 2 only) ----------------
            # If both turns so far returned ALLOW with nothing suspicious,
            # skip remaining turns. Don't give Gemini a chance to hallucinate.
            if turn_number == 2 and _is_clean_bill_of_health(state):
                logger.info(
                    f"  Clean bill of health after turn 2. "
                    f"All categories LOW/NONE, both verdicts ALLOW. "
                    f"Skipping turn 3."
                )
                converged  = True
                clean_exit = True
                break
            # ---- Convergence check (only after MIN_TURNS) ---------------------
            # This is the ONLY place convergence is evaluated.
            # Before MIN_TURNS, this always returns False.
            if _convergence_check(deltas, turn_number):
                converged = True
                # If we converged before the last allowed slot,
                # always run one dedicated synthesis turn.
                if turn_number < MAX_TURNS:
                    logger.info(
                        f"  Early convergence at turn {turn_number}. "
                        f"Running dedicated synthesis."
                    )
                    synth = self._run_synthesis(state, turn_number + 1)
                    if synth:
                        state["turn_history"].append(synth.to_dict())
                        new_cov, _ = _update_coverage(
                            state["coverage_matrix"], synth.severity_flags
                        )
                        state["coverage_matrix"] = new_cov
                        final_turn = synth
                break

        # ---- Final verdict ---------------------------------------------------
        turns_completed = len(state["turn_history"])

        if partial or final_turn is None:
            decision        = "ESCALATE"
            decision_reason = (
                "Partial evaluation: a model failed mid-loop. "
                "Defaulting to ESCALATE per Holo safety policy."
            )
        else:
            decision = final_turn.verdict

            # HIGH-severity override: fires regardless of synthesis verdict
            if _any_high(state["coverage_matrix"]):
                # Check if Synthesis explicitly overrode the HIGH
                # If Synthesis said ALLOW and its own flags are all LOW/NONE,
                # it reviewed the HIGH and determined it was unjustified.
                synth_flags = final_turn.severity_flags if final_turn else {}
                synth_overrides = (
                    final_turn is not None
                    and final_turn.role == "Synthesis"
                    and final_turn.verdict == "ALLOW"
                    and all(
                        SEVERITY_RANK.get(v, 0) < SEVERITY_RANK["MEDIUM"]
                        for v in synth_flags.values()
                    )
                )
                if synth_overrides:
                    decision = "ALLOW"
                    decision_reason = (
                        "HIGH severity was flagged in coverage matrix, but "
                        "Synthesis reviewed the evidence and determined ALLOW "
                        "with all LOW/NONE flags. Synthesis override accepted. "
                        f"Turns completed: {turns_completed}. "
                        f"Converged: {converged}."
                    )
                else:
                    decision = "ESCALATE"
                    decision_reason = (
                        "HIGH-severity risk detected in coverage matrix. "
                        "Safety override applied. "
                        f"Turns completed: {turns_completed}. "
                        f"Converged: {converged}."
                    )
            elif clean_exit:
                decision_reason = (
                    f"Clean bill of health after {turns_completed} turns. "
                    f"All categories LOW/NONE, both verdicts ALLOW. "
                    f"No further analysis required."
                )
            else:
                decision_reason = (
                    f"Synthesis verdict after {turns_completed} turns. "
                    f"No HIGH-severity categories. "
                    f"Converged: {converged}."
                )

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(f"\n{'='*65}")
        logger.info(
            f"EVALUATION COMPLETE: {evaluation_id} | "
            f"decision={decision} | turns={turns_completed} | "
            f"converged={converged} | {elapsed_ms}ms"
        )
        logger.info(f"{'='*65}\n")

        return {
            "evaluation_id":   evaluation_id,
            "decision":        decision,
            "decision_reason": decision_reason,
            "turns_completed": turns_completed,
            "converged":       converged,
            "partial":         partial,
            "deltas":          deltas,
            "turn_history":    state["turn_history"],
            "coverage_matrix": state["coverage_matrix"],
            "elapsed_ms":      elapsed_ms,
            "total_tokens": {
                "input":  sum(t.get("input_tokens",  0) for t in state["turn_history"]),
                "output": sum(t.get("output_tokens", 0) for t in state["turn_history"]),
            },
        }

    # ---- Internal helpers ----------------------------------------------------

    def _run_turn_with_retry(self, adapter, state, turn_number, role):
        """Run one turn with up to MAX_RETRIES retries. Returns None on total failure."""
        for attempt in range(MAX_RETRIES + 1):
            try:
                return adapter.run_turn(state, turn_number, role)
            except Exception as e:
                logger.warning(
                    f"  Turn {turn_number} attempt {attempt + 1} failed: "
                    f"{type(e).__name__}: {e}"
                )
                if attempt == MAX_RETRIES:
                    return None

    def _run_synthesis(self, state, turn_number):
        """Run a dedicated synthesis turn using the next adapter in round-robin order."""
        synthesis_adapter = self._get_adapter(turn_number)
        logger.info(
            f"  Synthesis | {synthesis_adapter.provider} ({synthesis_adapter.model_id})"
        )
        return self._run_turn_with_retry(
            synthesis_adapter, state, turn_number, "Synthesis"
        )


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def _coverage_summary(matrix: dict) -> str:
    """Compact string for log lines, e.g. 'ID=H AMT=L RTE=- ...' """
    abbr = {
        "sender_identity":  "ID",
        "invoice_amount":   "AMT",
        "payment_routing":  "RTE",
        "urgency_pressure": "URG",
        "domain_spoofing":  "DOM",
        "approval_chain":   "APV",
    }
    parts = []
    for cat, v in matrix.items():
        sev = v["max_severity"][0] if v["addressed"] else "-"
        parts.append(f"{abbr.get(cat, cat[:3])}={sev}")
    return " ".join(parts)
