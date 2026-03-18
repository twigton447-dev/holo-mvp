"""
context_governor.py

The orchestration brain of Holo. Manages the shared state object,
routes turns to the correct adapter, and enforces the adversarial loop.

Architecture:
  - The STATE_OBJECT is built once and updated after each turn.
  - Every model receives the FULL state including all prior turn findings.
  - No model ever sees a cleaned or summarized version — they see the raw
    reasoning and severity flags from every analyst that preceded them.
  - This is the "rototilling": compounding postmortems where each model
    must confront what the others actually said.

Turn structure (strict — models NEVER repeat):
  Turn 1: OpenAI    — adversarial role (rotated from persona library)
  Turn 2: Anthropic — adversarial role (rotated from persona library)
  Turn 3: Google    — adversarial role (rotated from persona library)

  No synthesis turn. The governor makes the final decision algorithmically.
  No LLM can anchor or rationalize the final verdict.

Early exits:
  - Clean bill of health after turn 2: both analysts returned ALLOW with
    all categories LOW/NONE. Skips turn 3.
  - Partial failure: any unrecoverable model error → auto-ESCALATE with
    partial findings.

Verdict logic:
  - Majority vote across all turns (ALLOW wins ties when no HIGH present).
  - Any HIGH in the coverage matrix forces ESCALATE regardless of majority.
  - The governor is the final authority. No model overrides it.
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
    select_persona,
    load_adapters,
    GovernorAdapter,
)
from tool_gate import ToolGate
from project_brain import ProjectBrain

logger = logging.getLogger("holo.governor")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_TURNS           = 3   # minimum before convergence can fire
MAX_TURNS           = 10  # ceiling for both Holo and solo — same cap, same test
CONVERGENCE_WINDOW  = 2   # consecutive zero-delta turns required to converge
MAX_RETRIES         = 1   # one retry per turn before declaring failure

# Temperature schedule: high early (wide adversarial exploration),
# low late (precision verification as convergence approaches).
TEMPERATURE_SCHEDULE = {
    1: 0.7,   # Initial Assessment — cast wide, explore all angles
    2: 0.6,   # Assumption Attacker — creative dismantling
    3: 0.5,   # Edge Case Hunter — focused but still exploratory
    4: 0.4,   # gap-filling specialists — targeted pressure
    5: 0.35,
    6: 0.3,
    7: 0.25,
    8: 0.2,   # late turns — surgical precision
    9: 0.2,
    10: 0.2,
}


# ---------------------------------------------------------------------------
# Convergence level
# ---------------------------------------------------------------------------

# Explicit convergence states — the governor computes this each turn and
# feeds it into the brief so analysts understand the stakes of their turn.
CONVERGENCE_LEVELS = ["EARLY", "MID", "NARROWING", "NEAR_FINAL"]

CONVERGENCE_STAKES = {
    "EARLY": (
        "We are in EARLY exploration. All six categories are in play. "
        "Cast wide — your job is to surface signals, not confirm safety."
    ),
    "MID": (
        "We are MID-investigation. Core signals are emerging. "
        "Challenge interpretations that have been accepted without hard evidence."
    ),
    "NARROWING": (
        "We are NARROWING. Most categories have been assessed. "
        "Target the remaining gaps precisely. Don't re-cover settled ground."
    ),
    "NEAR_FINAL": (
        "We are NEAR FINAL. The last two turns found nothing new. "
        "This may be your last turn before the governor decides. "
        "If you cannot find concrete, evidence-backed risk, return ALLOW — "
        "a clean result is a valid and important outcome."
    ),
}


def _compute_convergence_level(turn_number: int, deltas: list) -> str:
    """
    Derive the current convergence level from turn count and delta history.

    EARLY    — turns 1-2, or still finding significant new signals
    MID      — past the baseline, signals emerging, delta still positive
    NARROWING — delta declining, models running out of new findings
    NEAR_FINAL — delta hit zero at least once after MIN_TURNS
    """
    if turn_number <= 2 or not deltas:
        return "EARLY"

    last_delta  = deltas[-1]
    recent_avg  = sum(deltas[-2:]) / len(deltas[-2:]) if len(deltas) >= 2 else last_delta

    # Delta hit zero — soil is nearly fully rototilled
    if last_delta == 0 and turn_number >= MIN_TURNS:
        return "NEAR_FINAL"

    # Delta declining toward zero
    if recent_avg <= 1:
        return "NARROWING"

    # Still finding meaningful new signals
    if turn_number <= 4:
        return "MID"

    return "NARROWING"


# ---------------------------------------------------------------------------
# Oscillation detection
# ---------------------------------------------------------------------------

OSCILLATION_WINDOW = 4  # look at the last N verdicts for flip-flop pattern


def _detect_oscillation(turn_history: list) -> bool:
    """
    True when the last OSCILLATION_WINDOW verdicts strictly alternate between
    ALLOW and ESCALATE — the models are deadlocked, not converging.

    A flip-flop means the challenge cycle is doing more harm than good:
    whichever position is currently held gets successfully attacked, so the
    loop will never stabilize on its own.  The governor must escalate.

    Only fires after MIN_TURNS to avoid false positives on small samples.
    """
    if len(turn_history) < OSCILLATION_WINDOW:
        return False
    recent = [t["verdict"] for t in turn_history[-OSCILLATION_WINDOW:]]
    # Strict alternation: every consecutive pair must differ
    return all(recent[i] != recent[i - 1] for i in range(1, len(recent)))


# ---------------------------------------------------------------------------
# Decay detection
# ---------------------------------------------------------------------------

def _detect_decay(turn_history: list) -> tuple:
    """
    Detect quality regression: a category rated HIGH or MEDIUM in an early
    turn is rated LOW or NONE in a later turn — the analyst backed down under
    adversarial pressure without new evidence.

    Single-category downgrades CAN be legitimate (a later analyst has better
    evidence).  We fire on:
      - Any HIGH → LOW/NONE regression (the most serious kind), OR
      - 2+ MEDIUM → LOW/NONE regressions in the same evaluation.

    Returns (decay_detected: bool, regressions: list[dict]).
    """
    if len(turn_history) < 3:
        return False, []

    # Track the first turn that reached MEDIUM+ for each category
    peak: dict = {}   # cat -> {"severity": str, "turn_number": int}
    regressions = []

    for turn in turn_history:
        flags    = turn.get("severity_flags", {})
        turn_num = turn["turn_number"]

        for cat, sev in flags.items():
            current_rank = SEVERITY_RANK.get(sev, 0)

            if cat not in peak:
                # Record the first MEDIUM+ assessment as the peak
                if current_rank >= SEVERITY_RANK["MEDIUM"]:
                    peak[cat] = {"severity": sev, "turn_number": turn_num}
            else:
                peak_rank = SEVERITY_RANK.get(peak[cat]["severity"], 0)
                # Significant downgrade: MEDIUM+ → LOW or NONE
                if (peak_rank >= SEVERITY_RANK["MEDIUM"]
                        and current_rank <= SEVERITY_RANK["LOW"]):
                    regressions.append({
                        "category":         cat,
                        "peak_turn":        peak[cat]["turn_number"],
                        "peak_severity":    peak[cat]["severity"],
                        "current_turn":     turn_num,
                        "current_severity": sev,
                    })

    any_high_regression = any(
        r["peak_severity"] == "HIGH"
        for r in regressions
    )
    fired = any_high_regression or len(regressions) >= 2
    return fired, regressions


def _get_temperature(turn_number: int, deltas: list) -> float:
    """
    Returns the target temperature for this turn.
    If the last two deltas are already zero (converging), drop to 0.2
    regardless of turn number — precision over exploration at that point.
    """
    if len(deltas) >= 2 and deltas[-1] == 0 and deltas[-2] == 0:
        return 0.2
    return TEMPERATURE_SCHEDULE.get(turn_number, 0.2)


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

    Delta > 0 means the loop learned something new.
    Delta = 0 means this turn added no new information.
    """
    updated = deepcopy(matrix)
    delta   = 0

    for cat in BEC_CATEGORIES:
        new_sev = flags.get(cat, "NONE")
        if new_sev == "NONE":
            continue

        current = updated[cat]
        if not current["addressed"]:
            updated[cat]["addressed"]    = True
            updated[cat]["max_severity"] = new_sev
            delta += 1
            logger.debug(f"    Coverage: {cat} first addressed at {new_sev}")
        else:
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


def _is_clean_bill_of_health(state: dict) -> bool:
    """
    Early exit for genuinely clean evaluations — AFTER turn 2, BEFORE turn 3.

    Returns True only when ALL of these are true:
      1. Both turns returned an ALLOW verdict.
      2. No HIGH or MEDIUM severity flags exist in either turn.
      3. Every category in the coverage matrix is LOW or NONE.

    This is NOT convergence. This means "there was never anything to find."
    """
    turns = state["turn_history"]
    if len(turns) < 2:
        return False

    for turn in turns[:2]:
        if turn.get("verdict", "").upper() != "ALLOW":
            return False

    for turn in turns[:2]:
        flags = turn.get("severity_flags", {})
        for cat, sev in flags.items():
            if SEVERITY_RANK.get(sev, 0) >= SEVERITY_RANK.get("MEDIUM", 2):
                return False

    for cat, info in state["coverage_matrix"].items():
        if SEVERITY_RANK.get(info["max_severity"], 0) >= SEVERITY_RANK.get("MEDIUM", 2):
            return False

    return True


# ---------------------------------------------------------------------------
# Artifact Registry
# ---------------------------------------------------------------------------

def _build_artifact_registry(action: dict, context: dict) -> dict:
    """
    Initialize the Artifact Registry with PINNED entries for the action
    payload and context bundle.

    PINNED semantics (patent §4.7): never summarized, never dropped from
    the token budget, always injected at full fidelity.  These are the
    source-of-truth artifacts every analyst retrieves by ID — not by
    direct dict access — so downstream code can't accidentally diverge
    from the canonical version.

    Additional artifacts (e.g., verified_facts_v1) are added after the
    ToolGate runs.
    """
    return {
        "action_v1": {
            "artifact_id": "action_v1",
            "type":        "action_payload",
            "description": "The financial action under evaluation "
                           "(routing number, amount, vendor, etc.)",
            "status":      "PINNED",
            "version":     1,
            "content":     action,
        },
        "context_v1": {
            "artifact_id": "context_v1",
            "type":        "context_bundle",
            "description": "Vendor record, email chain, org policies, "
                           "sender history, acquisition data",
            "status":      "PINNED",
            "version":     1,
            "content":     context,
        },
    }


# ---------------------------------------------------------------------------
# State object builder
# ---------------------------------------------------------------------------

def _build_initial_state(request: dict, evaluation_id: str) -> dict:
    """
    The STATE_OBJECT is the single source of truth passed to every model.
    It grows with each turn via turn_history and coverage_matrix updates.

    The artifacts registry holds PINNED source documents.  Models retrieve
    artifacts by ID rather than accessing action/context directly — this
    enforces the patent's retrieve-by-ID semantics and prevents any
    model from operating on a stale or modified version of the source data.
    """
    action  = request.get("action", {})
    context = request.get("context", {})
    return {
        "evaluation_id":   evaluation_id,
        "action":          action,    # kept for internal helpers (ToolGate, etc.)
        "context":         context,   # kept for internal helpers
        "artifacts":       _build_artifact_registry(action, context),
        "turn_history":    [],
        "coverage_matrix": _init_coverage(),
        "governor_briefs": [],      # [{for_turn, brief, convergence_level}]
        "verified_facts":  {},      # populated by ToolGate before turn 1
    }


# ---------------------------------------------------------------------------
# Context Governor
# ---------------------------------------------------------------------------

class ContextGovernor:

    def __init__(self):
        self._adapters  = load_adapters()
        self._governor  = GovernorAdapter()
        self._tool_gate = ToolGate()
        self._brain     = ProjectBrain()

    def evaluate(self, request: dict) -> dict:
        """
        Main entry point. Runs the convergence-driven adversarial loop and
        returns a complete result dict suitable for the API response.

        The loop:
          1. Build the shared state object.
          2. Run turns until convergence or MAX_TURNS.
             - Models cycle round-robin: OpenAI → Anthropic → Google → OpenAI ...
             - PERSONAS never repeat within an evaluation (10-entry library).
             - MIN_TURNS must complete before convergence can fire.
             - Convergence: delta=0 for CONVERGENCE_WINDOW consecutive turns.
          3. Clean bill of health exits after turn 2 (both ALLOW, all LOW/NONE).
          4. Governor decides algorithmically — no LLM in the final call.
          5. HIGH-severity override is a hard lock. No model can clear it.
        """
        evaluation_id = f"holo_{uuid.uuid4().hex[:8]}"
        start_time    = time.time()

        logger.info(f"\n{'='*65}")
        logger.info(f"EVALUATION START: {evaluation_id}")
        logger.info(f"MIN={MIN_TURNS} MAX={MAX_TURNS} CONV_WINDOW={CONVERGENCE_WINDOW}")
        logger.info(f"{'='*65}")

        state         = _build_initial_state(request, evaluation_id)
        deltas        = []
        partial       = False
        converged     = False
        clean_exit    = False
        oscillation   = False
        decay         = False
        decay_detail  = []
        used_personas = set()

        # ---- Project Brain (runs before everything else) --------------------
        # Query persistent memory for prior evaluations of this vendor.
        # Holo is never on its first day on the job — if this vendor has
        # appeared before, analysts will know before they write a single word.
        prior_experience = self._brain.retrieve_context(
            state["action"], state["context"]
        )
        if prior_experience:
            state["artifacts"]["project_brain_v1"] = {
                "artifact_id": "project_brain_v1",
                "type":        "project_brain",
                "description": (
                    f"Prior Holo experience: "
                    f"{prior_experience['total_evaluations']} evaluation(s) "
                    f"for vendor '{prior_experience.get('vendor_domain', 'unknown')}' — "
                    f"{prior_experience['allow_count']} ALLOW / "
                    f"{prior_experience['escalate_count']} ESCALATE"
                ),
                "status":      "PINNED",
                "version":     1,
                "content":     prior_experience,
            }
            logger.info(
                f"  ProjectBrain: injected {prior_experience['total_evaluations']} "
                f"prior evaluation(s) for '{prior_experience.get('vendor_domain')}'."
            )

        # ---- Tool gate (runs once before any analyst turn) -------------------
        # Converts INFERRED signals into SUBMITTED_DATA facts:
        #   routing number → institution name
        #   invoice amount → exact % deviation from historical range
        #   acquisition timing → was banking changed before legal close?
        #   email domains → do all emails use the vendor's registered domain?
        verified = self._tool_gate.verify(state["action"], state["context"])
        state["verified_facts"] = verified

        # Pin verified facts as a PINNED artifact so analysts retrieve them
        # by ID at full fidelity — never dropped from the token budget.
        if verified:
            state["artifacts"]["verified_facts_v1"] = {
                "artifact_id": "verified_facts_v1",
                "type":        "verified_facts",
                "description": "Governor-verified SUBMITTED_DATA facts "
                               "(routing institution, invoice deviation, "
                               "domain consistency, acquisition timing)",
                "status":      "PINNED",
                "version":     1,
                "content":     verified,
            }

        # ---- Adversarial loop ------------------------------------------------
        for turn_number in range(1, MAX_TURNS + 1):

            # Round-robin through adapters — models cycle, personas never repeat.
            adapter = self._adapters[(turn_number - 1) % len(self._adapters)]

            # Turns 1–3: fixed baseline sequence (Initial Assessment →
            # Assumption Attacker → Edge Case Hunter).
            # Turn 4+: governor picks the persona that best fills coverage gaps.
            if turn_number <= 3:
                role = get_role_for_turn(turn_number)
            else:
                role = select_persona(state["coverage_matrix"], used_personas)
            used_personas.add(role)

            # Temperature drops as the loop matures and converges.
            temperature = _get_temperature(turn_number, deltas)

            logger.info(
                f"  Turn {turn_number}/{MAX_TURNS} | "
                f"{adapter.provider} ({adapter.model_id}) | "
                f"Role: {role} | temp={temperature}"
            )

            turn_result = self._run_turn_with_retry(
                adapter, state, turn_number, role, temperature
            )

            if turn_result is None:
                logger.error(
                    f"  Turn {turn_number} failed after all retries. "
                    f"Auto-escalating."
                )
                partial = True
                break

            turn_dict = turn_result.to_dict()
            turn_dict["temperature"] = temperature  # inspectability: what temp drove this turn

            new_coverage, delta = _update_coverage(
                state["coverage_matrix"], turn_result.severity_flags
            )
            state["coverage_matrix"] = new_coverage
            deltas.append(delta)
            turn_dict["delta"] = delta  # inspectability: how much did this turn add?

            logger.info(
                f"  Turn {turn_number} | delta={delta} | "
                f"coverage={_coverage_summary(new_coverage)}"
            )

            # ---- Governor brief for the next turn ---------------------------
            # After each turn, compute convergence level and generate a
            # targeting directive for the next analyst — surfacing the single
            # most important unresolved question before they begin.
            conv_level = _compute_convergence_level(turn_number, deltas)
            turn_dict["convergence_level_after"] = conv_level  # inspectability: state after this turn
            logger.info(f"  Convergence level: {conv_level}")

            state["turn_history"].append(turn_dict)

            next_turn = turn_number + 1
            if next_turn <= MAX_TURNS:
                next_persona = (
                    get_role_for_turn(next_turn)
                    if next_turn <= 3
                    else select_persona(state["coverage_matrix"], used_personas)
                )
                brief = self._governor.generate_brief(
                    state, next_turn, next_persona, conv_level
                )
                if brief:
                    state["governor_briefs"].append({
                        "for_turn":         next_turn,
                        "brief":            brief,
                        "convergence_level": conv_level,
                    })
                    logger.info(f"  Governor brief for turn {next_turn}: {brief[:120]}...")

            # ---- Clean Bill of Health early exit (turn 2 only) --------------
            if turn_number == 2 and _is_clean_bill_of_health(state):
                logger.info(
                    f"  Clean bill of health after turn 2. "
                    f"All categories LOW/NONE, both verdicts ALLOW."
                )
                converged  = True
                clean_exit = True
                break

            # ---- Convergence check (only after MIN_TURNS) -------------------
            # Fires when the last CONVERGENCE_WINDOW deltas are all zero —
            # the soil is fully rototilled, no new signals can be surfaced.
            if (turn_number >= MIN_TURNS
                    and len(deltas) >= CONVERGENCE_WINDOW
                    and all(d == 0 for d in deltas[-CONVERGENCE_WINDOW:])):
                logger.info(
                    f"  Convergence: delta=0 for {CONVERGENCE_WINDOW} consecutive "
                    f"turns after {turn_number} turns. Soil fully rototilled."
                )
                converged = True
                break

            # ---- Oscillation check (only after MIN_TURNS) -------------------
            # Fires when verdicts flip-flop ALLOW/ESCALATE for OSCILLATION_WINDOW
            # consecutive turns — the models are deadlocked, not converging.
            # Governor must escalate rather than loop forever.
            if (turn_number >= MIN_TURNS
                    and _detect_oscillation(state["turn_history"])):
                logger.info(
                    f"  OSCILLATION DETECTED after turn {turn_number}: "
                    f"verdicts alternating — models deadlocked. Forcing ESCALATE."
                )
                oscillation = True
                break

            # ---- Decay check (only after MIN_TURNS) -------------------------
            # Fires when HIGH/MEDIUM findings from early turns are walked back
            # to LOW/NONE in later turns without new evidence — analysts
            # capitulating under adversarial pressure, not converging.
            if turn_number >= MIN_TURNS:
                decay, decay_detail = _detect_decay(state["turn_history"])
                if decay:
                    logger.info(
                        f"  DECAY DETECTED after turn {turn_number}: "
                        f"{len(decay_detail)} category regression(s) under "
                        f"adversarial pressure. Halting loop."
                    )
                    break

        if not partial and not clean_exit and not oscillation and not decay:
            converged = True

        # ---- Final verdict (governor decides — no LLM in the loop) ----------
        turns_completed = len(state["turn_history"])

        if oscillation:
            decision        = "ESCALATE"
            recent_verdicts = [t["verdict"] for t in state["turn_history"][-OSCILLATION_WINDOW:]]
            decision_reason = (
                f"OSCILLATION: models deadlocked after {turns_completed} turns. "
                f"Last {OSCILLATION_WINDOW} verdicts alternated: {recent_verdicts}. "
                "The models genuinely disagree and cannot self-resolve. "
                "Human judgment required."
            )
        elif decay:
            decision        = "ESCALATE"
            cats = [r["category"] for r in decay_detail]
            decision_reason = (
                f"DECAY: quality regression detected after {turns_completed} turns. "
                f"{len(decay_detail)} category(ies) walked back under adversarial "
                f"pressure without new evidence: {cats}. "
                "Earlier findings are more reliable than the current state. "
                "Human review of the full turn history recommended."
            )
        elif partial or not state["turn_history"]:
            decision        = "ESCALATE"
            decision_reason = (
                "Partial evaluation: a model failed mid-loop. "
                "Defaulting to ESCALATE per Holo safety policy."
            )
        else:
            all_turns      = state["turn_history"]
            allow_votes    = sum(1 for t in all_turns if t.get("verdict") == "ALLOW")
            escalate_votes = len(all_turns) - allow_votes
            # ALLOW wins ties — conservative on false positives when no HIGH present
            majority_verdict = "ESCALATE" if escalate_votes > allow_votes else "ALLOW"
            decision = majority_verdict

            # HIGH-severity override: governor forces ESCALATE regardless of majority.
            # Distinguishes evidence quality: SUBMITTED_DATA or POLICY_VIOLATION
            # findings carry full weight; INFERRED-only HIGHs still escalate but
            # are flagged as lower-confidence so reviewers know the distinction.
            if _any_high(state["coverage_matrix"]):
                decision   = "ESCALATE"
                high_cats  = [
                    cat for cat, v in state["coverage_matrix"].items()
                    if v["max_severity"] == "HIGH"
                ]
                evidenced  = any(
                    f.get("fact_type") in ("SUBMITTED_DATA", "POLICY_VIOLATION")
                    for t in state["turn_history"]
                    for f in t.get("findings", [])
                    if f.get("category") in high_cats
                    and f.get("severity") == "HIGH"
                )
                if evidenced:
                    decision_reason = (
                        f"HIGH-severity risk in {high_cats} backed by submitted data. "
                        "Governor safety override applied. "
                        f"Turns completed: {turns_completed}."
                    )
                else:
                    decision_reason = (
                        f"HIGH-severity risk in {high_cats} flagged via inference "
                        "(no direct quote from submitted data). Escalating with "
                        "lower confidence — human review recommended. "
                        f"Turns completed: {turns_completed}."
                    )
            elif clean_exit:
                decision_reason = (
                    f"Clean bill of health after {turns_completed} turns. "
                    f"All categories LOW/NONE, both verdicts ALLOW. "
                    f"No further analysis required."
                )
            else:
                decision_reason = (
                    f"Majority verdict after {turns_completed} turns "
                    f"({allow_votes} ALLOW / {escalate_votes} ESCALATE). "
                    f"No HIGH-severity categories."
                )

        elapsed_ms = int((time.time() - start_time) * 1000)

        logger.info(f"\n{'='*65}")
        logger.info(
            f"EVALUATION COMPLETE: {evaluation_id} | "
            f"decision={decision} | turns={turns_completed} | "
            f"converged={converged} | {elapsed_ms}ms"
        )
        logger.info(f"{'='*65}\n")

        # Derive a single exit_reason string for inspectability
        if oscillation:
            exit_reason = "oscillation"
        elif decay:
            exit_reason = "decay"
        elif clean_exit:
            exit_reason = "clean_exit"
        elif converged:
            exit_reason = "converged"
        elif partial:
            exit_reason = "partial_failure"
        else:
            exit_reason = "max_turns"

        result = {
            "evaluation_id":   evaluation_id,
            "decision":        decision,
            "decision_reason": decision_reason,
            "exit_reason":     exit_reason,
            "turns_completed": turns_completed,
            "converged":       converged,
            "oscillation":     oscillation,
            "decay":           decay,
            "decay_detail":    decay_detail,
            "partial":         partial,
            "deltas":          deltas,

            # Full governance trail — every turn annotated with temperature,
            # delta, and convergence level. "We need to see everything and why."
            "turn_history":    state["turn_history"],

            # Artifact registry — PINNED source documents with retrieve-by-ID
            # semantics. action_v1 and context_v1 are always present;
            # verified_facts_v1 added if ToolGate found anything.
            "artifacts":       state["artifacts"],

            # Governor-generated targeting briefs between every turn.
            # Shows exactly what the governor saw and what it told each analyst.
            "governor_briefs": state["governor_briefs"],

            # ToolGate facts verified before any analyst turn.
            # These are SUBMITTED_DATA — not analyst inference.
            "verified_facts":  state["verified_facts"],

            "coverage_matrix": state["coverage_matrix"],
            "elapsed_ms":      elapsed_ms,
            "total_tokens": {
                "input":  sum(t.get("input_tokens",  0) for t in state["turn_history"]),
                "output": sum(t.get("output_tokens", 0) for t in state["turn_history"]),
            },
        }

        # ---- Persist to Project Brain ----------------------------------------
        # Save key intelligence so future evaluations of this vendor start
        # with institutional memory, not a blank slate.
        self._brain.save_evaluation(result, request)

        return result

    # ---- Internal helpers ----------------------------------------------------

    def _get_fallback_adapter(self, failed_adapter):
        """
        Return a different-vendor adapter to use when the primary fails.

        Patent §4.4.1: the fallback must not be the same provider as the
        instance that produced the immediately preceding turn, preserving
        the cross-vendor adversarial diversity benefit.

        Returns None only if every other adapter also shares the same
        provider (shouldn't happen with a 3-vendor setup).
        """
        for adapter in self._adapters:
            if adapter.provider != failed_adapter.provider:
                return adapter
        return None

    def _run_turn_with_retry(self, adapter, state, turn_number, role, temperature=0.2):
        """
        Run one turn with up to MAX_RETRIES retries, then cross-vendor fallback.

        Failure sequence:
          1. Try primary adapter up to MAX_RETRIES + 1 times.
          2. If still failing, try a different-vendor fallback adapter once.
          3. If fallback also fails, return None → partial evaluation.

        The cross-vendor constraint is enforced at step 2: we never fall
        back to the same provider that just failed.
        """
        for attempt in range(MAX_RETRIES + 1):
            try:
                return adapter.run_turn(state, turn_number, role, temperature)
            except Exception as e:
                logger.warning(
                    f"  Turn {turn_number} attempt {attempt + 1} "
                    f"({adapter.provider}) failed: {type(e).__name__}: {e}"
                )

        # Primary exhausted — try cross-vendor fallback
        fallback = self._get_fallback_adapter(adapter)
        if fallback:
            logger.warning(
                f"  Turn {turn_number}: primary {adapter.provider} exhausted. "
                f"Falling back to {fallback.provider} ({fallback.model_id})."
            )
            try:
                return fallback.run_turn(state, turn_number, role, temperature)
            except Exception as e:
                logger.error(
                    f"  Turn {turn_number} fallback {fallback.provider} also "
                    f"failed: {type(e).__name__}: {e}"
                )

        return None



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
