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

Turn structure (constrained shuffle — no fixed rotation):
  Each run generates a fresh adapter sequence where no model repeats on
  consecutive turns AND no ordered pair (A→B) repeats back-to-back.
  With 3 models there are 6 possible directed pairs — all are reachable,
  unlike a fixed round-robin which uses only 3.
  Personas are assigned independently of model order and never repeat.

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
import random
import time
import uuid
from copy import deepcopy

from llm_adapters import (
    SEVERITY_RANK,
    TurnResult,
    get_role_for_turn,
    select_persona,
    load_adapters,
    load_fast_adapters,
    GovernorAdapter,
)
from scenario_templates import get_template

# The Governor runs the between-turn briefs in evaluation mode.
GovernorAdapter = GovernorAdapter
from tool_gate import ToolGate
from project_brain import ProjectBrain

logger = logging.getLogger("holo.governor")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MIN_TURNS           = 3   # minimum before convergence can fire
MAX_TURNS           = 10  # ceiling for both Holo and solo — same cap, same test
CONVERGENCE_WINDOW  = 2   # consecutive zero-delta turns required to converge

# ---------------------------------------------------------------------------
# Evaluation tiers — governor selects based on action amount
# ---------------------------------------------------------------------------
#
# FAST   < $10,000       lightweight models, 3-turn cap
# STANDARD $10k–$100k   standard pool, 5-turn cap
# DEEP   > $100,000      frontier models, full 10-turn cap
#
# The tier is selected once at the start of evaluate() and never changes
# mid-run. MAX_TURNS is overridden per-evaluation, not globally.

TIER_FAST     = "fast"
TIER_STANDARD = "standard"
TIER_DEEP     = "deep"

TIER_THRESHOLDS = {
    TIER_FAST:     (0,       10_000),
    TIER_STANDARD: (10_000,  100_000),
    TIER_DEEP:     (100_000, float("inf")),
}

TIER_MAX_TURNS = {
    TIER_FAST:     3,
    TIER_STANDARD: 5,
    TIER_DEEP:     10,
}


def _compute_turn_signal(turn_result, elapsed_ms: int) -> dict:
    """
    Compute observable stress/confidence proxies from a completed turn.

    These are external behavioral signals — latency, token usage, hedging
    language, certainty markers, self-contradiction, rebuttal specificity,
    and uncertainty invocations. They are NOT internal model activations.

    The goal is a longitudinal dataset: over thousands of evaluations, do
    high-ambiguity payloads produce systematically different signal patterns?
    Does a model that hedges heavily on turn 2 correlate with oscillation?
    Does high output-token-to-input-token ratio predict decay?

    All scores are 0.0–1.0 normalized where applicable.
    Raw counts are also preserved for downstream analysis.
    """
    import re

    reasoning = turn_result.reasoning or ""
    words     = reasoning.split()
    word_count = max(len(words), 1)

    # ---- Hedging density ----------------------------------------------------
    # Words/phrases that signal the model is uncertain or qualifying a claim.
    HEDGE_PATTERNS = [
        r"\bmay\b", r"\bmight\b", r"\bcould\b", r"\bpossibly\b",
        r"\bperhaps\b", r"\bunclear\b", r"\bappears to\b", r"\bseems\b",
        r"\bsuggest[s]?\b", r"\bindicate[s]?\b", r"\bcannot confirm\b",
        r"\binsufficient evidence\b", r"\bnot clear\b", r"\bif correct\b",
        r"\bassuming\b", r"\bpotentially\b", r"\bwould suggest\b",
    ]
    hedge_count = sum(
        len(re.findall(p, reasoning, re.IGNORECASE))
        for p in HEDGE_PATTERNS
    )
    hedge_density = round(min(hedge_count / word_count * 100, 1.0), 4)

    # ---- Certainty density --------------------------------------------------
    # Words that signal the model is confident and direct.
    CERTAINTY_PATTERNS = [
        r"\bclearly\b", r"\bdefinitely\b", r"\bdefinitively\b",
        r"\bunambiguously\b", r"\bconfirmed\b", r"\bverified\b",
        r"\bestablished\b", r"\bevident\b", r"\bproven\b",
        r"\bconclusively\b", r"\bwithout doubt\b", r"\bcertainly\b",
    ]
    certainty_count = sum(
        len(re.findall(p, reasoning, re.IGNORECASE))
        for p in CERTAINTY_PATTERNS
    )
    certainty_density = round(min(certainty_count / word_count * 100, 1.0), 4)

    # ---- Self-contradiction flag --------------------------------------------
    # Does the verdict conflict with the reasoning tone?
    # A model that reasons extensively about risk but returns ALLOW, or
    # reasons cleanly with no findings but returns ESCALATE, is worth flagging.
    high_medium_count = sum(
        1 for sev in turn_result.severity_flags.values()
        if sev in ("HIGH", "MEDIUM")
    )
    verdict_tension = (
        (turn_result.verdict == "ALLOW"    and high_medium_count >= 2) or
        (turn_result.verdict == "ESCALATE" and high_medium_count == 0)
    )

    # ---- Rebuttal specificity -----------------------------------------------
    # Does the reasoning cite specific field names or quoted text?
    # Proxy for whether the model is grounding in SUBMITTED_DATA vs. narrating.
    FIELD_CITATION_PATTERNS = [
        r"vendor_record\.", r"email_chain\[", r"invoice_history",
        r"routing_number", r"amount_usd", r"org_policies",
        r"known_contacts", r"sender_history", r"payment_history",
        r'"[^"]{4,40}"',   # quoted text from the payload
    ]
    field_citation_count = sum(
        len(re.findall(p, reasoning, re.IGNORECASE))
        for p in FIELD_CITATION_PATTERNS
    )

    # ---- NONE invocation rate -----------------------------------------------
    # How many categories did the model rate NONE (insufficient evidence)?
    # High NONE rate on a rich payload suggests the model didn't engage fully.
    none_count  = sum(1 for sev in turn_result.severity_flags.values() if sev == "NONE")
    total_cats  = max(len(turn_result.severity_flags), 1)
    none_rate   = round(none_count / total_cats, 4)

    # ---- Token efficiency ---------------------------------------------------
    # Output tokens per input token. High ratio = verbose reasoning.
    # Very high ratio on a short payload can indicate the model is padding.
    input_t  = max(turn_result.input_tokens, 1)
    output_t = turn_result.output_tokens
    token_ratio = round(output_t / input_t, 4)

    # ---- Composite stress score ---------------------------------------------
    # Weighted heuristic. Not ground truth — a starting point for calibration.
    # Higher = more signals of uncertainty/stress on this turn.
    stress_score = round(
        (hedge_density     * 40.0) +   # hedging is the strongest single signal
        (none_rate         * 25.0) +   # lots of NONE on a rich payload = disengagement
        (token_ratio       *  5.0) +   # verbosity proxy (low weight — noisy)
        (1.0 if verdict_tension else 0.0) * 20.0 +  # hard flag
        max(0.0, 0.5 - certainty_density) * 10.0,   # lack of certainty adds stress
        4
    )

    return {
        # Raw counts
        "hedge_count":         hedge_count,
        "certainty_count":     certainty_count,
        "field_citation_count": field_citation_count,
        "none_count":          none_count,
        "word_count":          word_count,

        # Normalized scores (0.0–1.0)
        "hedge_density":       hedge_density,
        "certainty_density":   certainty_density,
        "none_rate":           none_rate,
        "token_ratio":         token_ratio,

        # Flags
        "verdict_tension":     verdict_tension,

        # Timing
        "turn_latency_ms":     elapsed_ms,

        # Composite
        "stress_score":        stress_score,
    }


def _select_tier(request: dict) -> str:
    """
    Derive the evaluation tier from the action payload.

    Reads action.parameters.amount_usd first, then falls back to
    action.parameters.amount (raw numeric). If no amount is present,
    defaults to DEEP — unknown stakes get the full interrogation.
    """
    params = request.get("action", {}).get("parameters", {})
    amount = params.get("amount_usd") or params.get("amount")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        logger.info("  Tier: no amount found — defaulting to DEEP")
        return TIER_DEEP

    if amount < TIER_THRESHOLDS[TIER_STANDARD][0]:
        tier = TIER_FAST
    elif amount < TIER_THRESHOLDS[TIER_DEEP][0]:
        tier = TIER_STANDARD
    else:
        tier = TIER_DEEP

    logger.info(f"  Tier: {tier.upper()} (amount=${amount:,.2f})")
    return tier
# Retries are handled by provider_health.call_with_retry (max 3, exponential backoff)

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


def _convergence_check(deltas: list, turn_number: int) -> bool:
    """
    Return True when the evaluation has converged.
    Requires MIN_TURNS completed and at least 2 consecutive zero deltas.
    """
    if turn_number < MIN_TURNS or len(deltas) < 2:
        return False
    return deltas[-1] == 0 and deltas[-2] == 0


# ---------------------------------------------------------------------------
# Oscillation detection
# ---------------------------------------------------------------------------

OSCILLATION_WINDOW = 4  # look at the last N verdicts for flip-flop pattern


# ---------------------------------------------------------------------------
# Adapter sequence generator
# ---------------------------------------------------------------------------

def _build_adapter_sequence(n_adapters: int, length: int, seed: int = None) -> list:
    """
    Build a turn sequence of adapter indices of the given length such that:
      1. No adapter repeats on consecutive turns (no A→A).
      2. No ordered pair (A→B) repeats consecutively — i.e., if turns i and i+1
         are (A, B), turns i+1 and i+2 must not also be (A, B).

    This ensures every model approaches each turn with a different predecessor
    context, eliminating the fixed-rotation conditioning bias where model B
    always reads model A's output and model C always reads model B's.

    With 3 models there are 6 possible directed pairs. A fixed round-robin uses
    only 3 of them. This function uses all 6 over the course of a run.
    """
    if n_adapters < 2:
        return list(range(length))

    if seed is not None:
        random.seed(seed)

    indices = list(range(n_adapters))
    seq = [random.randint(0, n_adapters - 1)]

    for _ in range(length - 1):
        prev = seq[-1]
        prev_pair = (seq[-2], seq[-1]) if len(seq) >= 2 else None

        candidates = [i for i in indices if i != prev]
        if prev_pair is not None:
            # Prefer candidates that don't repeat the last ordered pair
            no_repeat = [i for i in candidates if (prev, i) != prev_pair]
            if no_repeat:
                candidates = no_repeat

        seq.append(random.choice(candidates))

    return seq


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

# Action types where payment authorization is the core risk.
# On these types, the evidenced-clearance bar is higher — SUBMITTED_DATA
# reasoning is not sufficient to clear a MEDIUM+ signal. Only a finding
# backed by POLICY_VIOLATION evidence (explicit policy authorization) qualifies.
# "I found data that looks legitimate" is not the same as "I found verified authorization."
PAYMENT_ACTION_TYPES = {"invoice_payment", "wire_transfer", "payment_approval"}


def _build_token_summary(turn_history: list, gov_counts: dict) -> dict:
    """Break down token usage by driver turns vs governor calls."""
    driver_in  = sum(t.get("input_tokens",  0) for t in turn_history)
    driver_out = sum(t.get("output_tokens", 0) for t in turn_history)
    gov_in     = gov_counts.get("input",  0)
    gov_out    = gov_counts.get("output", 0)
    return {
        "driver":   {"input": driver_in,       "output": driver_out},
        "governor": {"input": gov_in,           "output": gov_out},
        "total":    {"input": driver_in + gov_in, "output": driver_out + gov_out},
    }


def _detect_decay(turn_history: list, action_type: str = None) -> tuple:
    """
    Detect quality regression: a category rated HIGH or MEDIUM in an early
    turn is rated LOW or NONE in a later turn — the analyst backed down under
    adversarial pressure without new evidence.

    Single-category downgrades CAN be legitimate (a later analyst has better
    evidence).  We fire on:
      - Any HIGH → LOW/NONE regression (the most serious kind), OR
      - 2+ MEDIUM → LOW/NONE regressions in the same evaluation.

    EVIDENCED-CLEARANCE CARVE-OUT: A downgrade is excluded from the regression
    count if the downgrading turn has a finding for that category with
    fact_type == "SUBMITTED_DATA" at LOW/NONE severity.  This means the analyst
    found direct payload evidence (field values, email quotes, vendor record
    data) that explains why the earlier HIGH/MEDIUM was a false positive.
    Requiring SUBMITTED_DATA — not INFERRED — keeps the bar high: the analyst
    must cite concrete evidence, not reason their way out of it.

    PAYMENT ACTION EXCEPTION: On payment action types (invoice_payment,
    wire_transfer, payment_approval), the evidenced-clearance bar is raised.
    SUBMITTED_DATA alone is not sufficient — clearance requires POLICY_VIOLATION
    fact type (explicit policy authorization). "This looks legitimate" is not
    the same as "this is verified as authorized." A false negative on a payment
    is irreversible; the cost asymmetry justifies the stricter standard.

    Returns (decay_detected: bool, regressions: list[dict]).
    """
    if len(turn_history) < 3:
        return False, []

    is_payment_action = (action_type or "").lower() in PAYMENT_ACTION_TYPES

    # Track the first turn that reached MEDIUM+ for each category
    peak: dict = {}   # cat -> {"severity": str, "turn_number": int}
    regressions = []

    for turn in turn_history:
        flags         = turn.get("severity_flags", {})
        turn_num      = turn["turn_number"]
        turn_findings = turn.get("findings", [])

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
                    # Check for evidenced clearance.
                    # Standard actions: SUBMITTED_DATA finding suffices.
                    # Payment actions: requires POLICY_VIOLATION (verified
                    # authorization), not just submitted data reasoning.
                    if is_payment_action:
                        evidenced_clearance = any(
                            f.get("category") == cat
                            and f.get("fact_type") == "POLICY_VIOLATION"
                            and SEVERITY_RANK.get(f.get("severity", "NONE"), 0)
                                <= SEVERITY_RANK["LOW"]
                            for f in turn_findings
                        )
                    else:
                        evidenced_clearance = any(
                            f.get("category") == cat
                            and f.get("fact_type") == "SUBMITTED_DATA"
                            and SEVERITY_RANK.get(f.get("severity", "NONE"), 0)
                                <= SEVERITY_RANK["LOW"]
                            for f in turn_findings
                        )
                    if not evidenced_clearance:
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

def _init_coverage(categories: list) -> dict:
    """
    One entry per scenario category tracking:
      - addressed: has any model assessed this category yet?
      - max_severity: the highest severity any model has assigned
    """
    return {
        cat: {"addressed": False, "max_severity": "NONE"}
        for cat in categories
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

    for cat in matrix:
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


def _sustained_clearance(turn_history: list, coverage: dict) -> bool:
    """
    Returns True when every category that peaked at HIGH in the coverage matrix
    has been consistently cleared (rated LOW or NONE) by the last 2 consecutive
    turns, both of which returned ALLOW.

    This allows a genuine false-positive to be resolved without requiring a
    specific "Synthesis" persona — any two consecutive ALLOW turns that both
    rate the HIGH categories as LOW/NONE constitute a settled clearance.

    Safety properties:
    - Requires 2 consecutive turns agreeing (not just one), preventing a single
      adversarial-pressure capitulation from clearing a real fraud signal.
    - Both turns must vote ALLOW — a partial clearance (LOW flag, ESCALATE vote)
      does not qualify.
    - Only fires in the else branch (after decay, oscillation, and partial checks)
      so decay detection still catches walked-back HIGHs without evidence.
    - In genuine fraud scenarios, compounding adversarial pressure keeps at least
      one turn rating the HIGH category above LOW, preventing clearance.
    """
    if len(turn_history) < 2:
        return False

    recent = turn_history[-2:]

    # Both recent turns must have voted ALLOW
    if not all(t.get("verdict") == "ALLOW" for t in recent):
        return False

    # Every category that peaked at HIGH must be rated LOW or NONE in both turns
    for cat, v in coverage.items():
        if v["max_severity"] == "HIGH":
            for turn in recent:
                turn_sev = turn.get("severity_flags", {}).get(cat, "NONE")
                if SEVERITY_RANK.get(turn_sev, 0) >= SEVERITY_RANK["MEDIUM"]:
                    return False

    return True


def _detect_identity_provenance_risk(state: dict) -> str | None:
    """
    Detect domain-locked identity evidence: all legitimizing emails for a new
    contact trace back to the same domain as the sender. This is a circular
    trust chain — a domain-level compromise generates the entire sequence.

    Returns a governor brief string to inject before the next turn, or None
    if the pattern is absent.

    Fires only when sender_identity is at MEDIUM (not yet HIGH) and the email
    chain shows a new contact whose only corroboration is in-domain emails.
    """
    matrix   = state.get("coverage_matrix", {})
    sev      = matrix.get("sender_identity", {}).get("max_severity", "NONE")

    # Only intervene if we're stuck at MEDIUM — HIGH means the models got there
    if sev != "MEDIUM":
        return None

    context      = state.get("context", {})
    email_chain  = context.get("email_chain", context.get("email_thread", []))
    vendor_rec   = context.get("vendor_record", {})

    if not email_chain:
        return None

    # Collect all unique domains across the email chain
    import re
    domains = set()
    for msg in email_chain:
        sender = msg.get("from", "")
        match  = re.search(r"@([\w.\-]+)", sender)
        if match:
            domains.add(match.group(1).lower())

    # If all emails share a single domain, we have a circular trust chain
    if len(domains) != 1:
        return None

    sole_domain = next(iter(domains))

    # Build the set of contacts already verified in the vendor record.
    # These are authoritative pre-chain records — the carve-out applies to them.
    verified_contacts = set()
    for c in vendor_rec.get("known_contacts", []):
        if isinstance(c, dict):
            verified_contacts.add(c.get("name", "").lower())
            verified_contacts.add(c.get("email", "").lower())
        else:
            verified_contacts.add(str(c).lower())
    primary = vendor_rec.get("primary_contact", "")
    if primary:
        verified_contacts.add(primary.lower())
    for sig in state.get("context", {}).get("sender_history", {}).get("known_signatories", []):
        if isinstance(sig, dict):
            verified_contacts.add(sig.get("name", "").lower())
        else:
            verified_contacts.add(str(sig).lower())

    # Collect signatories seen in the email chain
    signers_in_chain = set()
    for msg in email_chain:
        body = msg.get("body", "")
        for line in body.splitlines():
            line = line.strip()
            if line and not line.startswith("Hi") and len(line.split()) <= 4:
                signers_in_chain.add(line)

    # Only fire if there is a signer in the chain who is NOT in the vendor record.
    # Carve-out: contacts already in the vendor record are expected — not circular.
    has_new_unverified_contact = any(
        name.lower() not in verified_contacts
        for name in signers_in_chain
        if name
    )

    if not has_new_unverified_contact:
        return None

    return (
        f"IDENTITY PROVENANCE FLAG: sender_identity is MEDIUM but may warrant HIGH. "
        f"All {len(email_chain)} emails in the chain — including any departure notice "
        f"and new-contact introduction — originate from the single domain "
        f"@{sole_domain}. A compromised or attacker-controlled domain generates "
        f"every email in this sequence. The prior analyst's rationale (known contact "
        f"introduced the new signatory) is circular: the introduction itself is from "
        f"the same domain. Test whether any out-of-band confirmation exists — a phone "
        f"call to a number predating this chain, a vendor master update before the "
        f"first email, any record that cannot be forged by domain access. If none, "
        f"escalate sender_identity to HIGH."
    )


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

    The active_template is selected from action["type"] and drives all
    scenario-specific behavior: categories, system prompts, coverage matrix,
    JSON schema, persona specializations, and log abbreviations.

    The artifacts registry holds PINNED source documents.  Models retrieve
    artifacts by ID rather than accessing action/context directly — this
    enforces the patent's retrieve-by-ID semantics and prevents any
    model from operating on a stale or modified version of the source data.
    """
    action   = request.get("action", {})
    context  = request.get("context", {})
    template = get_template(action.get("type", "invoice_payment"))

    return {
        "evaluation_id":   evaluation_id,
        "action":          action,    # kept for internal helpers (ToolGate, etc.)
        "context":         context,   # kept for internal helpers
        "active_template": template,  # scenario template: categories, prompts, abbreviations
        "artifacts":       _build_artifact_registry(action, context),
        "turn_history":    [],
        "coverage_matrix": _init_coverage(template["categories"]),
        "governor_briefs": [],        # [{for_turn, brief, convergence_level}]
        "verified_facts":  {},        # populated by ToolGate before turn 1
    }


# ---------------------------------------------------------------------------
# Context Governor
# ---------------------------------------------------------------------------

class ContextGovernor:

    def __init__(self, no_memory: bool = False, fixed_governor: str = "anthropic", seed: int = None):
        self._adapters, self._bench = load_adapters()
        self._fast_adapters = load_fast_adapters() or self._adapters  # fall back to standard
        self._governor   = GovernorAdapter(self._adapters, fixed_governor=fixed_governor)
        self._tool_gate  = ToolGate()
        self._brain      = ProjectBrain()
        self._no_memory  = no_memory
        self._seed       = seed

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
        from provider_health import registry, HealthMonitor, SystemUnavailableError

        evaluation_id = f"holo_{uuid.uuid4().hex[:8]}"
        start_time    = time.time()

        # Select evaluation tier based on action amount.
        # Tier determines the adapter pool and per-run turn cap.
        tier          = _select_tier(request)
        run_max_turns = TIER_MAX_TURNS[tier]
        run_adapters  = self._fast_adapters if tier == TIER_FAST else self._adapters

        logger.info(f"\n{'='*65}")
        logger.info(f"EVALUATION START: {evaluation_id}")
        logger.info(f"TIER={tier.upper()} MIN={MIN_TURNS} MAX={run_max_turns} CONV_WINDOW={CONVERGENCE_WINDOW}")
        logger.info(f"{'='*65}")

        state         = _build_initial_state(request, evaluation_id)
        template      = state["active_template"]
        logger.info(
            f"  Scenario: {template['name']} ({template['domain']}) | "
            f"categories={template['categories']}"
        )
        deltas        = []
        partial       = False
        converged     = False
        clean_exit    = False
        oscillation   = False
        decay         = False

        # Restore any expired quarantines and initialise health tracking
        for a in self._adapters:
            registry.restore_if_expired(a.provider, evaluation_id)
        health = HealthMonitor(total_providers=len(self._adapters))
        active_count = len([a for a in self._adapters
                            if not registry.is_quarantined(a.provider)])
        try:
            health.check_and_classify(active_count, evaluation_id, turn_number=0)
        except SystemUnavailableError:
            raise
        decay_detail  = []
        used_personas = set()

        # ---- Project Brain (runs before everything else) --------------------
        # Query persistent memory for prior evaluations of this vendor.
        # Holo is never on its first day on the job — if this vendor has
        # appeared before, analysts will know before they write a single word.
        # Suppressed when no_memory=True (benchmark isolation mode).
        prior_experience = (
            None if self._no_memory
            else self._brain.retrieve_context(state["action"], state["context"])
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
        # Reset governor token counters so this run starts clean.
        self._governor.reset_token_counts()

        # Build a constrained adapter sequence once per run.
        # No model repeats on consecutive turns. No ordered pair (A→B) repeats
        # back-to-back. Every model sees a different predecessor context each
        # time it runs — eliminates fixed-rotation conditioning bias.
        adapter_sequence = _build_adapter_sequence(len(run_adapters), run_max_turns, seed=self._seed)
        logger.info(
            f"  Adapter sequence: "
            + " → ".join(run_adapters[i].provider for i in adapter_sequence)
        )

        for turn_number in range(1, run_max_turns + 1):

            adapter = run_adapters[adapter_sequence[turn_number - 1]]

            # Turns 1–3: fixed baseline sequence (Initial Assessment →
            # Assumption Attacker → Edge Case Hunter).
            # Turn 4+: governor picks the persona that best fills coverage gaps.
            if turn_number <= 3:
                role = get_role_for_turn(turn_number)
            else:
                role = select_persona(state["coverage_matrix"], used_personas, state.get("active_template"))
            used_personas.add(role)

            # Temperature drops as the loop matures and converges.
            temperature = _get_temperature(turn_number, deltas)

            logger.info(
                f"  Turn {turn_number}/{MAX_TURNS} | "
                f"{adapter.provider} ({adapter.model_id}) | "
                f"Role: {role} | temp={temperature}"
            )

            turn_t0     = time.time()
            turn_result = self._run_turn_with_retry(
                adapter, state, turn_number, role, temperature,
                health=health, evaluation_id=evaluation_id,
            )
            turn_elapsed_ms = int((time.time() - turn_t0) * 1000)

            if turn_result is None:
                logger.error(
                    f"  Turn {turn_number} failed after all retries. "
                    f"Auto-escalating."
                )
                partial = True
                break

            turn_dict = turn_result.to_dict()
            if health.degraded_turns and health.degraded_turns[-1] == turn_number:
                turn_dict["degraded"] = True
            turn_dict["temperature"] = temperature  # inspectability: what temp drove this turn

            new_coverage, delta = _update_coverage(
                state["coverage_matrix"], turn_result.severity_flags
            )
            state["coverage_matrix"] = new_coverage
            deltas.append(delta)
            turn_dict["delta"] = delta  # inspectability: how much did this turn add?

            # ---- Turn signal — stress/confidence proxies --------------------
            # Observable behavioral signals: hedging density, certainty markers,
            # verdict tension, field citation rate, token ratio, latency.
            # Stored per-turn for longitudinal analysis across evaluations.
            turn_dict["signal"] = _compute_turn_signal(turn_result, turn_elapsed_ms)
            logger.info(
                f"  Turn {turn_number} signal | "
                f"stress={turn_dict['signal']['stress_score']:.3f} | "
                f"hedge={turn_dict['signal']['hedge_count']} | "
                f"none_rate={turn_dict['signal']['none_rate']:.2f} | "
                f"tension={turn_dict['signal']['verdict_tension']} | "
                f"latency={turn_elapsed_ms}ms"
            )

            logger.info(
                f"  Turn {turn_number} | delta={delta} | "
                f"coverage={_coverage_summary(new_coverage, state['active_template'].get('abbreviations', {}))}"
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
                    else select_persona(state["coverage_matrix"], used_personas, state.get("active_template"))
                )
                self._governor.prepare_for_turn(adapter)
                brief = self._governor.generate_brief(
                    state, next_turn, next_persona, conv_level
                )

                # ---- Algorithmic identity provenance check ------------------
                # If all email-chain evidence for a new contact traces back to
                # a single domain and sender_identity is stuck at MEDIUM,
                # prepend a hard-targeted provenance flag to the governor brief
                # so the next analyst has the circularity named explicitly.
                provenance_flag = _detect_identity_provenance_risk(state)
                if provenance_flag:
                    logger.info(
                        f"  Identity provenance risk detected — "
                        f"prepending flag to Turn {next_turn} brief."
                    )
                    brief = (provenance_flag + "\n\n" + brief) if brief else provenance_flag

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
                decay, decay_detail = _detect_decay(
                    state["turn_history"],
                    action_type=state.get("action", {}).get("type")
                )
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
            all_turns = state["turn_history"]

            # Exclude epistemically empty ESCALATE votes: a turn that voted ESCALATE
            # but rated every category LOW or NONE has no evidentiary basis for its
            # verdict. Counting it equally to a turn with MEDIUM/HIGH findings would
            # allow the adversarial persona pressure alone — not payload evidence — to
            # drive the final decision. In genuine fraud scenarios this never fires:
            # real fraud produces at least one MEDIUM+ flag to back the ESCALATE.
            def _is_empty_escalate(t: dict) -> bool:
                if t.get("verdict") != "ESCALATE":
                    return False
                return all(
                    SEVERITY_RANK.get(sev, 0) <= SEVERITY_RANK["LOW"]
                    for sev in t.get("severity_flags", {}).values()
                )

            allow_votes    = sum(1 for t in all_turns if t.get("verdict") == "ALLOW")
            escalate_votes = sum(
                1 for t in all_turns
                if t.get("verdict") == "ESCALATE" and not _is_empty_escalate(t)
            )
            empty_escalates = len(all_turns) - allow_votes - escalate_votes
            if empty_escalates:
                logger.info(
                    f"  Majority vote: {empty_escalates} empty ESCALATE(s) excluded "
                    f"(ESCALATE verdict with all flags LOW/NONE — no evidentiary basis)."
                )
            # ALLOW wins ties — conservative on false positives when no HIGH present
            majority_verdict = "ESCALATE" if escalate_votes > allow_votes else "ALLOW"
            decision = majority_verdict

            # Synthesis override: if the final turn has role "Synthesis" and returns
            # ALLOW with all LOW/NONE flags, it may clear a prior HIGH that was
            # flagged only via inference (no hard evidence). This represents a
            # deliberate, evidence-reviewed clearance by the final analyst.
            synthesis_cleared = False
            if state["turn_history"]:
                last_turn = state["turn_history"][-1]
                if (last_turn.get("role") == "Synthesis"
                        and last_turn.get("verdict") == "ALLOW"
                        and not any(
                            v == "HIGH"
                            for v in last_turn.get("severity_flags", {}).values()
                        )):
                    synthesis_cleared = True

            # HIGH-severity override: governor forces ESCALATE regardless of majority.
            # Distinguishes evidence quality: SUBMITTED_DATA or POLICY_VIOLATION
            # findings carry full weight; INFERRED-only HIGHs still escalate but
            # are flagged as lower-confidence so reviewers know the distinction.
            #
            # Clearance paths (either disables the HIGH override):
            #   1. synthesis_cleared: last turn is "Synthesis" role, votes ALLOW,
            #      rates all categories LOW/NONE.
            #   2. sustained_clearance: last 2 consecutive turns both vote ALLOW
            #      and both rate every HIGH category as LOW/NONE. Requires
            #      sustained agreement — a single capitulation doesn't qualify.
            sustained = _sustained_clearance(
                state["turn_history"], state["coverage_matrix"]
            )
            if _any_high(state["coverage_matrix"]) and not synthesis_cleared and not sustained:
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
            elif sustained:
                decision_reason = (
                    f"Sustained clearance after {turns_completed} turns. "
                    f"Prior HIGH flags resolved — last 2 turns both voted ALLOW "
                    f"with all HIGH categories rated LOW/NONE. "
                    f"Payload evidence supports clearance."
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
            "scenario":        template["name"],
            "tier":            tier,
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
            "run_health":      health.run_health,
            "total_tokens": _build_token_summary(
                state["turn_history"], self._governor.get_token_counts()
            ),
        }

        # ---- Persist to Project Brain ----------------------------------------
        # Save key intelligence so future evaluations of this vendor start
        # with institutional memory, not a blank slate.
        self._brain.save_evaluation(result, request)

        return result

    # ---- Internal helpers ----------------------------------------------------

    def _get_fallback_adapter(self, failed_adapter):
        """
        Return a different-vendor, non-quarantined adapter to use when the primary fails.

        Cross-vendor constraint preserved: fallback must not be the same provider
        as the failed adapter. Quarantined providers are skipped.
        Returns None only if no eligible adapter exists.
        """
        from provider_health import registry
        for adapter in self._adapters:
            if (adapter.provider != failed_adapter.provider
                    and not registry.is_quarantined(adapter.provider)):
                return adapter
        return None

    def _run_turn_with_retry(self, adapter, state, turn_number, role,
                             temperature=0.2, health=None, evaluation_id="unknown"):
        """
        Run one turn. Retry logic lives inside call_with_retry (called from run_turn).

        Failure sequence:
          1. Try primary adapter (call_with_retry handles up to 3 attempts internally).
          2. On ProviderUnavailableError: quarantine provider, try cross-vendor fallback.
          3. On fallback ProviderUnavailableError: quarantine fallback, return None.

        health (HealthMonitor) is updated on quarantine events so the caller can
        annotate the turn and track run_health.
        """
        from provider_health import registry, ProviderUnavailableError

        try:
            return adapter.run_turn(state, turn_number, role, temperature)
        except ProviderUnavailableError as e:
            registry.quarantine(e.provider, evaluation_id)
            if health:
                healthy = [a for a in self._adapters
                           if not registry.is_quarantined(a.provider)]
                health.check_and_classify(len(healthy), evaluation_id, turn_number)

        # Primary quarantined — try cross-vendor fallback
        fallback = self._get_fallback_adapter(adapter)
        if fallback:
            logger.warning(
                f"  Turn {turn_number}: primary {adapter.provider} quarantined. "
                f"Falling back to {fallback.provider} ({fallback.model_id})."
            )
            try:
                return fallback.run_turn(state, turn_number, role, temperature)
            except ProviderUnavailableError as e:
                registry.quarantine(e.provider, evaluation_id)
                if health:
                    healthy = [a for a in self._adapters
                               if not registry.is_quarantined(a.provider)]
                    health.check_and_classify(len(healthy), evaluation_id, turn_number)
                logger.error(
                    f"  Turn {turn_number} fallback {fallback.provider} also quarantined."
                )

        return None



# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def _coverage_summary(matrix: dict, abbreviations: dict = None) -> str:
    """Compact string for log lines, e.g. 'ID=H AMT=L RTE=- ...' """
    if abbreviations is None:
        abbreviations = {
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
        parts.append(f"{abbreviations.get(cat, cat[:4])}={sev}")
    return " ".join(parts)
