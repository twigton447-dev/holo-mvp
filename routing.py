"""
routing.py

Deterministic pre-evaluation routing function.

Converts an action packet into a tier assignment (FAST / STANDARD / DEEP)
before any model is called. Pure Python. No model calls. No async.

Three policy decisions gate the routing:
  Decision 1: Dollar floor — configurable via config.routing.fast_amount_floor_usd
  Decision 2: Known recipient — all three conditions must pass simultaneously
  Decision 3: Urgency language — pattern list lives in urgency_patterns.json

Rule evaluation order (first match wins for escalations):
  1. Any HIGH in key_risk_signals           → DEEP, stop
  2. routing_confidence == LOW              → escalate one tier from Wrangler
  3. Known recipient (all 3 conditions)     → if any fail: floor at STANDARD
  4. Amount above fast_amount_floor_usd     → floor at STANDARD
  5. Urgency language match                 → floor at STANDARD;
                                              authority_escalation also adds HIGH signal
  6. No rules fired                         → use Wrangler recommended_tier as-is

Every decision produces a RoutingAuditEntry — a customer-facing audit artifact.

Schema migration required for Condition C (account fingerprint):
  ALTER TABLE holo_evaluations ADD COLUMN IF NOT EXISTS
    payment_account_fingerprint text;
  CREATE INDEX IF NOT EXISTS idx_evals_fingerprint
    ON holo_evaluations (vendor_domain, payment_account_fingerprint)
    WHERE decision = 'ALLOW';
"""

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("holo.routing")

# ---------------------------------------------------------------------------
# Tier constants — kept in sync with context_governor.py
# ---------------------------------------------------------------------------

TIER_FAST     = "fast"
TIER_STANDARD = "standard"
TIER_DEEP     = "deep"

_TIER_RANK = {TIER_FAST: 0, TIER_STANDARD: 1, TIER_DEEP: 2}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RoutingConfig:
    """
    Client-configurable routing parameters.

    Populated from config.routing at pilot setup time.
    Passed explicitly into route_request() — never read from a global
    inside the routing function itself.
    """
    fast_amount_floor_usd: float = 1_000.0
    urgency_patterns_path: str   = "urgency_patterns.json"


@dataclass
class RecipientHistory:
    """
    Prior transaction history for the recipient in the current payload.

    Sourced from ProjectBrain.retrieve_recipient_history().
    All three fields are required to qualify as a known recipient:
      allow_count             >= 3   (Condition A)
      first_transaction_date  30+ days ago  (Condition B)
      prior_account_fingerprints  contains current fingerprint  (Condition C)
    """
    allow_count: int                        = 0
    first_transaction_date: Optional[str]   = None   # ISO date, e.g. "2025-11-01"
    prior_account_fingerprints: list        = field(default_factory=list)


@dataclass
class RoutingAuditEntry:
    """
    Full audit record for one routing decision.

    This is a customer-facing artifact — written to the evaluation result
    and available in the audit trail API endpoint.

    Fields:
      packet_id                 Evaluation ID this decision belongs to
      final_tier                Tier assigned: fast / standard / deep
      wrangler_recommended_tier Amount-based baseline before policy rules
      override_triggered        True if any policy rule changed the tier
      override_reason           Human-readable description of the rule that fired
      key_risk_signals          List of pre-detected risk signals (dicts with
                                severity, signal, detail)
      threshold_values_used     Actual config values at decision time —
                                essential for post-hoc tuning
      timestamp                 ISO 8601 UTC
    """
    packet_id:                 str
    final_tier:                str
    wrangler_recommended_tier: str
    override_triggered:        bool
    override_reason:           str
    key_risk_signals:          list
    threshold_values_used:     dict
    timestamp:                 str

    def to_dict(self) -> dict:
        return {
            "packet_id":                 self.packet_id,
            "final_tier":                self.final_tier,
            "wrangler_recommended_tier": self.wrangler_recommended_tier,
            "override_triggered":        self.override_triggered,
            "override_reason":           self.override_reason,
            "key_risk_signals":          self.key_risk_signals,
            "threshold_values_used":     self.threshold_values_used,
            "timestamp":                 self.timestamp,
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _amount_to_tier(amount_usd: float) -> str:
    """Pure amount-based tier — the Wrangler's baseline recommendation."""
    if amount_usd < 10_000:
        return TIER_FAST
    if amount_usd < 100_000:
        return TIER_STANDARD
    return TIER_DEEP


def _extract_amount(action: dict) -> Optional[float]:
    params = action.get("parameters", {})
    raw = params.get("amount_usd") or params.get("amount")
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def _compute_account_fingerprint(action: dict) -> Optional[str]:
    """
    SHA-256 (truncated) of key account identifiers.

    Covers: routing_number + account_number for ACH/wire,
            IBAN for international, account_id as a fallback.
    Returns None if the payload carries no identifiers — that itself
    prevents Condition C from passing (unknown account = not known recipient).
    """
    params   = action.get("parameters", {})
    routing  = str(params.get("routing_number",  "") or "").strip()
    account  = str(params.get("account_number",  "") or
                   params.get("account_id",       "") or "").strip()
    iban     = str(params.get("iban",             "") or "").strip()

    identifier = f"{routing}|{account}|{iban}"
    # All empty → no identifiable account in payload
    if not routing and not account and not iban:
        return None

    return hashlib.sha256(identifier.lower().encode()).hexdigest()[:16]


def _check_known_recipient(
    action: dict,
    history: RecipientHistory,
) -> tuple[bool, Optional[dict]]:
    """
    Returns (is_known: bool, mismatch_signal: dict | None).

    All three conditions must be simultaneously true.
    Condition C failure on an otherwise-qualifying recipient is the highest
    confidence BEC signal in the routing layer — returned as a HIGH signal
    for injection into the evaluation state.
    """
    # Condition A: >= 3 prior successful (ALLOW) transactions
    if history.allow_count < 3:
        logger.debug(
            f"  Routing: not known recipient — "
            f"allow_count={history.allow_count} < 3 (Condition A)"
        )
        return False, None

    # Condition B: relationship age >= 30 days
    if not history.first_transaction_date:
        logger.debug("  Routing: not known recipient — no first_transaction_date (Condition B)")
        return False, None
    try:
        first = datetime.fromisoformat(
            history.first_transaction_date.replace("Z", "+00:00")
        )
        age_days = (datetime.now(timezone.utc) - first).days
    except (ValueError, TypeError):
        logger.debug("  Routing: not known recipient — unparseable first_transaction_date")
        return False, None

    if age_days < 30:
        logger.debug(
            f"  Routing: not known recipient — "
            f"relationship_age={age_days}d < 30d (Condition B)"
        )
        return False, None

    # Condition C: account identifiers match exactly
    current_fp = _compute_account_fingerprint(action)
    if current_fp is None:
        logger.debug("  Routing: not known recipient — no account identifiers in payload (Condition C)")
        return False, None

    prior_fps = set(history.prior_account_fingerprints)
    if current_fp not in prior_fps:
        logger.warning(
            "  Routing: ACCOUNT DETAIL MISMATCH on known recipient — "
            "routing to DEEP with HIGH signal."
        )
        return False, {
            "severity": "HIGH",
            "signal":   "account_detail_mismatch_on_known_recipient",
            "detail": (
                f"Recipient meets prior-transaction count ({history.allow_count} ALLOW) "
                f"and relationship age ({age_days} days) thresholds, but account "
                f"identifiers in this payload do not match any prior ALLOW transaction. "
                f"A changed routing or account number on an established vendor is the "
                f"highest-confidence indicator of BEC / account takeover."
            ),
        }

    logger.debug(
        f"  Routing: known recipient confirmed — "
        f"allow_count={history.allow_count}, age={age_days}d, fingerprint matched."
    )
    return True, None


def _load_urgency_patterns(path: str) -> dict:
    """
    Load urgency pattern categories from a JSON file.

    The routing function never reads pattern lists directly — it always
    goes through this loader so new patterns can be added by editing the
    JSON without touching routing logic.

    Falls back to _EMBEDDED_URGENCY_PATTERNS on load failure.
    """
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            # Strip metadata keys (prefixed with _)
            return {k: v for k, v in data.items() if not k.startswith("_")}
        except Exception as e:
            logger.warning(f"  Routing: failed to load urgency patterns from {path!r}: {e}")

    logger.warning(
        f"  Routing: urgency patterns file not found at {path!r}. "
        f"Using embedded defaults."
    )
    return _EMBEDDED_URGENCY_PATTERNS


# Embedded defaults — present only as a fallback, never the primary source.
# Add new patterns to urgency_patterns.json, not here.
_EMBEDDED_URGENCY_PATTERNS = {
    "time_pressure": [
        "urgent", "immediately", "today only", "end of day",
        "wire by 3pm", "before close", "time sensitive",
        "do not delay", "critical deadline", "must process now",
        "last chance",
    ],
    "authority_escalation": [
        "per the ceo", "ceo requested", "board approval obtained",
        "executive override", "legal has signed off",
        "per leadership", "authorized by", "direct instruction from",
        "do not question", "confidential — do not discuss",
        "bypass normal process",
    ],
}


def _scan_urgency(action: dict, context: dict, patterns: dict) -> list[dict]:
    """
    Scan action payload fields and email chain for urgency language.

    Scans: action.parameters.memo, action.parameters.note,
           email_chain[*].subject, email_chain[*].body

    Returns a list of triggered signals (one per category, first match only).
    """
    parts = []
    params = action.get("parameters", {})
    for field_name in ("memo", "note", "description", "reason"):
        val = params.get(field_name, "")
        if val:
            parts.append(val)

    for msg in context.get("email_chain", context.get("email_thread", [])):
        parts.append(msg.get("subject", ""))
        parts.append(msg.get("body", ""))

    corpus = " ".join(parts).lower()
    signals = []

    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(re.escape(pattern.lower()), corpus):
                signals.append({
                    "category":        category,
                    "matched_pattern": pattern,
                    "severity":        "HIGH" if category == "authority_escalation" else "MEDIUM",
                })
                break  # one signal per category is sufficient

    return signals


def _floor(current: str, minimum: str) -> str:
    """Return the higher-ranked tier of current and minimum."""
    if _TIER_RANK.get(minimum, 0) > _TIER_RANK.get(current, 0):
        return minimum
    return current


def _escalate_one(tier: str) -> str:
    return {TIER_FAST: TIER_STANDARD, TIER_STANDARD: TIER_DEEP}.get(tier, tier)


def _make_entry(
    packet_id:                 str,
    final_tier:                str,
    wrangler_recommended_tier: str,
    override_triggered:        bool,
    override_reason:           str,
    key_risk_signals:          list,
    threshold_values_used:     dict,
) -> RoutingAuditEntry:
    return RoutingAuditEntry(
        packet_id                 = packet_id,
        final_tier                = final_tier,
        wrangler_recommended_tier = wrangler_recommended_tier,
        override_triggered        = override_triggered,
        override_reason           = override_reason,
        key_risk_signals          = key_risk_signals,
        threshold_values_used     = threshold_values_used,
        timestamp                 = datetime.now(timezone.utc).isoformat(),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_urgency_patterns(path: str) -> dict:
    """
    Public loader — call once at startup and pass the result into route_request().
    Separates I/O from the deterministic routing logic.
    """
    return _load_urgency_patterns(path)


def route_request(
    packet_id:                 str,
    action:                    dict,
    context:                   dict,
    recipient_history:         Optional[RecipientHistory],
    routing_config:            RoutingConfig,
    urgency_patterns:          dict,
    key_risk_signals:          Optional[list]   = None,
    wrangler_recommended_tier: Optional[str]    = None,
    routing_confidence:        Optional[str]    = None,
) -> RoutingAuditEntry:
    """
    Deterministic routing function. Pure Python. No model calls. No async.

    Args:
        packet_id:                 Evaluation ID for the audit trail.
        action:                    The action payload dict.
        context:                   The context bundle dict.
        recipient_history:         Prior transaction history from ProjectBrain,
                                   or None if ProjectBrain is unavailable or
                                   no_memory=True.
        routing_config:            Client-specific config (dollar floor, paths).
        urgency_patterns:          Pre-loaded pattern dict from load_urgency_patterns().
        key_risk_signals:          Pre-detected HIGH/MEDIUM signals from upstream
                                   checks (e.g. ToolGate), if any.
        wrangler_recommended_tier: Override the amount-based baseline. Used when
                                   the Wrangler has additional context.
        routing_confidence:        "LOW" triggers a one-tier escalation from the
                                   Wrangler's recommendation.

    Returns:
        RoutingAuditEntry with full audit trail.
    """
    key_risk_signals = list(key_risk_signals or [])  # local copy, may be appended to
    amount = _extract_amount(action)

    # Wrangler's amount-based baseline
    if wrangler_recommended_tier:
        wrangler_tier = wrangler_recommended_tier
    elif amount is not None:
        wrangler_tier = _amount_to_tier(amount)
    else:
        wrangler_tier = TIER_DEEP

    final_tier         = wrangler_tier
    override_triggered = False
    override_reason    = ""

    threshold_values_used = {
        "fast_amount_floor_usd":                routing_config.fast_amount_floor_usd,
        "known_recipient_min_transactions":      3,
        "known_recipient_min_relationship_days": 30,
        "amount_usd":                            amount,
    }

    # ---- Rule 1: Any HIGH in key_risk_signals → DEEP, stop ------------------
    high_pre = [s for s in key_risk_signals if s.get("severity") == "HIGH"]
    if high_pre:
        final_tier         = TIER_DEEP
        override_triggered = True
        override_reason    = (
            f"Pre-detected HIGH-severity signal: "
            f"'{high_pre[0].get('signal', 'unknown')}'. "
            f"Routed to DEEP regardless of amount or recipient history."
        )
        logger.info(
            f"  Routing [{packet_id}]: DEEP (Rule 1 — pre-detected HIGH). "
            f"{override_reason}"
        )
        return _make_entry(
            packet_id, final_tier, wrangler_tier,
            override_triggered, override_reason,
            key_risk_signals, threshold_values_used,
        )

    # ---- Rule 2: routing_confidence == LOW → escalate one tier --------------
    if routing_confidence == "LOW":
        escalated = _escalate_one(wrangler_tier)
        if escalated != wrangler_tier:
            final_tier         = escalated
            override_triggered = True
            override_reason    = (
                f"routing_confidence=LOW. "
                f"Escalated {wrangler_tier.upper()} → {escalated.upper()}."
            )
            logger.info(
                f"  Routing [{packet_id}]: {final_tier.upper()} "
                f"(Rule 2 — low confidence escalation)."
            )
            return _make_entry(
                packet_id, final_tier, wrangler_tier,
                override_triggered, override_reason,
                key_risk_signals, threshold_values_used,
            )

    # ---- Rule 3: Known recipient check --------------------------------------
    if recipient_history is not None:
        is_known, mismatch_signal = _check_known_recipient(action, recipient_history)

        if mismatch_signal:
            # Condition C failed: known vendor, changed account — highest-confidence BEC signal
            key_risk_signals = [mismatch_signal] + key_risk_signals
            final_tier         = TIER_DEEP
            override_triggered = True
            override_reason    = mismatch_signal["signal"]
            logger.warning(
                f"  Routing [{packet_id}]: DEEP (Rule 3 — account mismatch on known recipient)."
            )
            return _make_entry(
                packet_id, final_tier, wrangler_tier,
                override_triggered, override_reason,
                key_risk_signals, threshold_values_used,
            )

        if not is_known:
            prev = final_tier
            final_tier = _floor(final_tier, TIER_STANDARD)
            if final_tier != prev:
                override_triggered = True
                override_reason    = (
                    f"Recipient does not meet known-recipient criteria "
                    f"(requires >= 3 prior ALLOW transactions, >= 30-day relationship, "
                    f"exact account detail match — all three conditions must pass). "
                    f"Minimum tier: STANDARD."
                )
                logger.info(
                    f"  Routing [{packet_id}]: floored to STANDARD "
                    f"(Rule 3 — not a known recipient)."
                )

    # ---- Rule 4: Dollar floor -----------------------------------------------
    if amount is not None and amount > routing_config.fast_amount_floor_usd:
        prev = final_tier
        final_tier = _floor(final_tier, TIER_STANDARD)
        if final_tier != prev or (
            not override_triggered
            and _TIER_RANK.get(final_tier, 0) > _TIER_RANK.get(wrangler_tier, 0)
        ):
            override_triggered = True
            override_reason    = (
                f"Amount ${amount:,.2f} exceeds fast_amount_floor_usd "
                f"${routing_config.fast_amount_floor_usd:,.0f}. "
                f"Minimum tier: STANDARD."
            )
            logger.info(
                f"  Routing [{packet_id}]: floored to STANDARD "
                f"(Rule 4 — amount above floor)."
            )

    # ---- Rule 5: Urgency language -------------------------------------------
    urgency_signals = _scan_urgency(action, context, urgency_patterns)
    if urgency_signals:
        prev = final_tier
        final_tier = _floor(final_tier, TIER_STANDARD)

        # Authority escalation gets injected as a HIGH risk signal
        auth_signals = [s for s in urgency_signals if s["category"] == "authority_escalation"]
        if auth_signals:
            key_risk_signals = [{
                "severity": "HIGH",
                "signal":   "authority_escalation_language",
                "detail": (
                    f"Authority escalation language detected: "
                    f"'{auth_signals[0]['matched_pattern']}'. "
                    f"This pattern is a primary BEC / social engineering indicator. "
                    f"Instructions invoking executive authority to bypass normal process "
                    f"represent the majority of successful wire fraud cases."
                ),
            }] + key_risk_signals

        categories_hit = list({s["category"] for s in urgency_signals})
        override_triggered = True
        override_reason    = (
            f"Urgency language detected in category: {', '.join(categories_hit)}. "
            f"Matched pattern: '{urgency_signals[0]['matched_pattern']}'. "
            f"Minimum tier: STANDARD."
        )
        logger.info(
            f"  Routing [{packet_id}]: floored to STANDARD "
            f"(Rule 5 — urgency language: {categories_hit})."
        )

    # ---- No rules fired: use Wrangler recommendation as-is -----------------
    if not override_triggered:
        override_reason = (
            "No routing policy rules triggered. "
            "Using Wrangler amount-based recommendation."
        )
        logger.info(
            f"  Routing [{packet_id}]: {final_tier.upper()} "
            f"(no override — Wrangler recommendation)."
        )
    else:
        logger.info(
            f"  Routing [{packet_id}]: {final_tier.upper()} "
            f"(wrangler={wrangler_tier.upper()}, override={override_triggered}). "
            f"{override_reason[:120]}"
        )

    return _make_entry(
        packet_id, final_tier, wrangler_tier,
        override_triggered, override_reason,
        key_risk_signals, threshold_values_used,
    )
