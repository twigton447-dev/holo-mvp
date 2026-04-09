"""
chat_engine.py

Holo chat mode — randomized multi-model conversation engine.

Every response comes from a randomly selected LLM provider.
The Governor is also randomly selected, but never shares DNA
with the driver on the same turn. No predictable pattern exists.
All providers speak as Holo using the unified persona prompt.
"""

import logging
import random
import re as _re
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from llm_adapters import (
    HOLO_CHAT_SYSTEM_PROMPT,
    GovernorAdapter,
    load_adapters,
)
from project_brain import ProjectBrain
import web_search

logger = logging.getLogger("holo.chat")

# In-memory session store.
# Replace with Redis for multi-instance or persistent deployments.
_sessions: Dict[str, "ChatSession"] = {}


# ---------------------------------------------------------------------------
# Session model
# ---------------------------------------------------------------------------

@dataclass
class ChatSession:
    session_id: str
    history: List[Dict[str, str]] = field(default_factory=list)
    rotation_index: int = 0      # kept for turn counting only; adapter selection is randomized
    turn_count: int = 0
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

    # Governor stickiness
    # "chat": hold for random 3-5 turns, then re-randomize
    # "api":  lock to one provider for the entire session, re-randomize on next session
    gov_mode: str = "chat"
    gov_provider: Optional[str] = None   # currently locked governor provider
    gov_turns_remaining: int = 0         # turns left before next switch (chat mode only)

    @property
    def thread_health_score(self) -> int:
        """
        Starts at 100, decays with turns and accumulated message volume.
        Roughly reaches 0 around 20 turns with moderate message length.
        """
        base       = max(0, 100 - (self.turn_count * 5))
        total_chars = sum(len(m["content"]) for m in self.history)
        char_decay  = min(40, total_chars // 2000)
        return max(0, base - char_decay)

    @property
    def thread_health_level(self) -> str:
        score = self.thread_health_score
        if score >= 61:
            return "GREEN"
        elif score >= 21:
            return "YELLOW"
        return "RED"

    @property
    def thread_status(self) -> str:
        score = self.thread_health_score
        if score <= 20:
            return "ROTATION_RECOMMENDED"
        elif score <= 40:
            return "CLEANUP_RECOMMENDED"
        return "HEALTHY"

    @property
    def user_alert(self) -> str:
        status = self.thread_status
        if status == "HEALTHY":
            return "NONE"
        return status


# ---------------------------------------------------------------------------
# Chat engine
# ---------------------------------------------------------------------------

class HoloChatEngine:
    """
    Manages the round-robin multi-model chat loop.
    One instance per application; sessions are keyed by session_id.
    """

    def __init__(self):
        self._adapters, self._bench = load_adapters()   # active pool + bench pool
        self._governor = GovernorAdapter(self._adapters) # shares active pool, never same DNA as driver
        self._brain    = ProjectBrain()
        logger.info(
            "HoloChatEngine initialized. Active: "
            + ", ".join(a.provider for a in self._adapters)
            + (" | Bench: " + ", ".join(a.provider for a in self._bench) if self._bench else "")
            + " | GovernorAdapter ready"
        )

    def get_or_create_session(self, session_id: Optional[str] = None,
                              gov_mode: str = "chat") -> ChatSession:
        if session_id and session_id in _sessions:
            return _sessions[session_id]
        new_id  = session_id or str(uuid.uuid4())
        session = ChatSession(session_id=new_id, gov_mode=gov_mode)

        # Restore history from Supabase if the session_id is known but not in memory
        # (e.g. after a server restart)
        if session_id:
            prior = self._brain.load_chat_history(session_id)
            if prior:
                session.history      = prior
                session.turn_count   = sum(1 for m in prior if m["role"] == "user")
                session.rotation_index = session.turn_count % len(self._adapters)
                logger.info(f"Restored session {session_id[:8]} from brain ({session.turn_count} turns).")

        _sessions[new_id] = session
        logger.info(f"Chat session ready: {new_id[:8]}")
        return session

    def send_message(self, session_id: str, user_message: str,
                     capsule_id: Optional[str] = None,
                     images: Optional[List[Dict[str, Any]]] = None,
                     incognito: bool = False,
                     gov_mode: str = "chat") -> Dict[str, Any]:
        """
        Process one user message. Returns Holo's response + metadata.
        The caller should use session_id from the returned dict for follow-up turns.

        incognito=True: blind mode — no capsule context, no Governor memory, no life portrait
        injected. Base system prompt only. Used for unbiased evaluation runs.

        gov_mode="chat": governor holds for random 3-5 turns, then re-randomizes.
        gov_mode="api":  governor locked for the entire session, re-randomizes on next session.
        """
        session             = self.get_or_create_session(session_id, gov_mode=gov_mode)
        session.last_active = time.time()

        # Consolidate-on-resume — runs once on the first turn of a new session.
        # If the prior session was abandoned before hitting RED (the common case),
        # it was never consolidated. Consolidate it now before loading context
        # so the current session starts with a complete portrait.
        if capsule_id and not incognito and session.turn_count == 0:
            stale_session_id = self._brain.get_prior_unconsolidated_session(
                capsule_id, session.session_id
            )
            if stale_session_id:
                logger.info(
                    f"  Consolidate-on-resume: prior session {stale_session_id[:8]} "
                    f"was never consolidated — running now."
                )
                def _consolidate_stale():
                    try:
                        stale_history = self._brain.load_chat_history(stale_session_id)
                        if stale_history and len(stale_history) >= 4:
                            stale_ctx = self._brain.get_capsule_context(capsule_id)
                            result = self._governor.consolidate_session(
                                stale_history, stale_ctx, stale_session_id
                            )
                            if result.get("session_note"):
                                self._brain.save_consolidation(
                                    capsule_id, stale_session_id, result["session_note"]
                                )
                            if result.get("life_context"):
                                self._brain.upsert_life_context(capsule_id, result["life_context"])
                            logger.info(
                                f"  Stale consolidation complete for {stale_session_id[:8]}: "
                                f"{len(result.get('life_context', []))} life_context entries written."
                            )
                    except Exception as e:
                        logger.warning(f"Stale consolidation failed for {stale_session_id[:8]}: {e}")
                threading.Thread(target=_consolidate_stale, daemon=True).start()

        # Incognito: strip all memory — only base system prompt reaches the model
        if incognito:
            capsule_context = {}
            life_context    = []
            last_session    = None
        else:
            capsule_context = self._brain.get_capsule_context(capsule_id) if capsule_id else {}
            life_context    = self._brain.load_life_context(capsule_id) if capsule_id else []
            last_session    = self._brain.load_last_consolidation(capsule_id) if capsule_id and session.turn_count == 0 else None

        # Randomly select driver for this turn — no predictable pattern
        adapter = self._adapters[random.randrange(len(self._adapters))]
        session.rotation_index += 1
        session.turn_count     += 1

        # Governor stickiness — hold court for a spell before rotating.
        # chat mode: hold for a random 3-5 turns, then re-randomize (unpredictable cadence)
        # api mode:  lock to one provider for the entire session; re-randomize on next session
        if session.gov_mode == "api":
            if session.gov_provider is None:
                self._governor.prepare_for_turn(adapter)
                session.gov_provider = self._governor.provider
            else:
                self._governor.lock_to_provider(session.gov_provider)
        else:
            if session.gov_turns_remaining <= 0:
                self._governor.prepare_for_turn(adapter)
                session.gov_provider       = self._governor.provider
                session.gov_turns_remaining = random.randint(3, 5)
            else:
                self._governor.lock_to_provider(session.gov_provider)
                session.gov_turns_remaining -= 1

        # Governor runs the instruments: temperature + search decision
        temperature  = self._governor.assess_chat_temperature(user_message, session.history)
        search_query = self._governor.should_search(user_message, session.history)

        # Governor thinks about the human — skipped in incognito (would introduce bias)
        thought = None if incognito else self._governor.surface_thought(session.history, capsule_context, baton_pass=_health_context(session))
        tenor   = None if incognito else self._governor.assess_tenor(session.history, capsule_context, turn_count=session.turn_count)
        search_results = web_search.search(search_query) if search_query else None

        # Build enriched message — search results injected for the model only,
        # not stored in history (history stays clean with the original message)
        enriched_message = user_message
        if search_results:
            enriched_message = (
                f"{user_message}\n\n"
                f"[BACKGROUND CONTEXT: The following search results were retrieved to help you answer. "
                f"Use them silently — do not mention, quote, or reference that a search was performed. "
                f"If the results are irrelevant to the question, ignore them entirely.]\n\n"
                f"{search_results}"
            )
            logger.info(f"  Search query: '{search_query}'")

        logger.info(
            f"Chat turn {session.turn_count} | session={session.session_id[:8]} | "
            f"driver={adapter.provider} | governor={self._governor.provider} | temp={temperature:.2f}"
            + (" | INCOGNITO" if incognito else "")
        )

        # Inject thread-health context + portrait + working memory + Governor brief
        # Incognito: only base system prompt — zero context leakage
        system_prompt = HOLO_CHAT_SYSTEM_PROMPT
        if not incognito:
            system_prompt += (
                "\n\n" + _health_context(session)
                + ("\n\n" + _life_context_block(life_context) if life_context else "")
                + ("\n\n" + _last_session_block(last_session) if last_session else "")
                + ("\n\n" + _capsule_context_block(capsule_context) if capsule_context else "")
                + ("\n\nCAPTAIN BRIEF — READ + DIRECTIVE (private, never surface to user):\n" + tenor if tenor else "")
            )

        # Call the adapter — enriched_message includes search results if any
        # On failure, transparently fail over to a bench model from a different vendor
        start = time.time()
        try:
            response_text, in_tok, out_tok = adapter.chat_call(
                system_prompt, session.history, enriched_message, temperature,
                images=images or None,
            )
        except Exception as primary_err:
            logger.warning(f"Driver {adapter.provider} failed: {primary_err} — attempting bench failover")
            bench_candidates = [b for b in self._bench if b.provider != adapter.provider]
            if not bench_candidates:
                # No bench pool — fall back to another active adapter from a different vendor
                bench_candidates = [b for b in self._adapters if b.provider != adapter.provider]
            if not bench_candidates:
                raise
            fallback = random.choice(bench_candidates)
            logger.info(f"Bench failover: {fallback.provider}/{fallback.model_id}")
            response_text, in_tok, out_tok = fallback.chat_call(
                system_prompt, session.history, enriched_message, temperature,
                images=images or None,
            )
            adapter = fallback  # reflect actual driver in metadata
        elapsed_ms = int((time.time() - start) * 1000)

        # Hallucination check — Governor scans for specific low-confidence claims
        # and verifies them against live search. Silent on clean responses.
        response_text, flagged_claims = self._governor.verify_claims(
            response_text, web_search.search
        )
        if flagged_claims:
            corrections = [f["correction"] for f in flagged_claims if f.get("correction")]
            if corrections:
                # Quietly inline the correction so the user gets accurate information
                note = " · ".join(corrections)
                response_text += f"\n\n*One thing worth correcting: {note}*"

        # Extract and save any HTML artifacts — after claims check, before history commit
        artifacts_saved = []
        if capsule_id and not incognito:
            artifacts_saved = _extract_and_save_artifacts(
                self._brain, response_text, capsule_id, session.session_id, session.turn_count
            )

        # Commit both turns to history
        session.history.append({"role": "user",      "content": user_message})
        session.history.append({"role": "assistant",  "content": response_text})

        # Link session to capsule on first turn — skipped in incognito
        if capsule_id and session.turn_count == 1 and not incognito:
            self._brain.set_capsule_context(capsule_id, "last_session_id", session.session_id)
            self._brain.append_session_history(capsule_id, session.session_id, user_message)

        # Governor learns — extract any new facts about the user and persist them
        # Skipped in incognito: blind sessions must not pollute the capsule portrait
        if capsule_id and not incognito:
            updates = self._governor.extract_context_updates(session.history, capsule_context)
            for key, value in updates.items():
                self._brain.set_capsule_context(capsule_id, key, value)
            if updates:
                logger.info(f"Capsule context updated for {capsule_id[:8]}: {list(updates.keys())}")

        # Governor consolidates — skipped in incognito
        if capsule_id and not incognito and session.thread_health_level == "RED":
            def _consolidate():
                try:
                    result = self._governor.consolidate_session(
                        session.history, capsule_context, session.session_id
                    )
                    if result.get("session_note"):
                        self._brain.save_consolidation(
                            capsule_id, session.session_id, result["session_note"]
                        )
                    if result.get("life_context"):
                        self._brain.upsert_life_context(capsule_id, result["life_context"])
                    logger.info(
                        f"Consolidation complete for {capsule_id[:8]}: "
                        f"{len(result.get('life_context', []))} life_context entries written."
                    )
                except Exception as e:
                    logger.warning(f"Consolidation failed: {e}")
            threading.Thread(target=_consolidate, daemon=True).start()

        # Governor names the thread after turn 2 — enough context to know the topic
        if capsule_id and session.turn_count == 2 and not incognito:
            _hist = list(session.history)
            _sid  = session.session_id
            _cid  = capsule_id
            def _name_thread():
                try:
                    name = self._governor.name_session(_hist)
                    if name:
                        self._brain.update_session_name(_cid, _sid, name)
                except Exception as e:
                    logger.warning(f"Thread naming failed: {e}")
            threading.Thread(target=_name_thread, daemon=True).start()

        # Persist to Supabase — capsule_id links session to user permanently
        self._brain.save_chat_turn(
            session_id    = session.session_id,
            turn_number   = session.turn_count,
            user_message  = user_message,
            holo_response = response_text,
            provider      = adapter.provider,
            temperature   = temperature,
            capsule_id    = capsule_id,
        )

        # Signal a thread handoff when health is RED
        handoff = None
        if session.thread_health_level == "RED":
            handoff = {
                "suggested":  True,
                "message":    "This thread is getting long. Everything important has been saved: your portrait, open threads, what shifted this session. Before you continue, tell me: how much context do you want carried into the next thread? (Full detail, key points only, or just pick up where we left off and I'll calibrate.)",
                "new_thread": "/chat",
            }

        return {
            "session_id":          session.session_id,
            "response":            response_text,
            "turn_number":         session.turn_count,
            "thread_health_score": session.thread_health_score,
            "thread_health_level": session.thread_health_level,
            "elapsed_ms":          elapsed_ms,
            "tokens":              {"input": in_tok, "output": out_tok},
            "thought":             thought,   # {"text": str, "color": str} or None
            "handoff":             handoff,   # {suggested, message, new_thread} or None
            "incognito":           incognito,
            "_provider":           adapter.provider,
            "_temperature":        temperature,
            "artifacts":           artifacts_saved,
        }

    def get_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        session = _sessions.get(session_id)
        return session.history if session else None

    def clear_session(self, session_id: str) -> bool:
        if session_id in _sessions:
            del _sessions[session_id]
            return True
        return False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _life_context_block(entries: list) -> str:
    """
    Format the Governor's permanent portrait for injection.
    This is the distilled, curated truth — highest priority context.
    """
    lines = ["WHO THIS PERSON IS (Governor's permanent portrait — distilled across all sessions):"]
    for e in entries:
        conf = f" [{int(e.get('confidence', 1.0) * 100)}% confidence]" if e.get("confidence", 1.0) < 0.8 else ""
        lines.append(f"  [{e.get('category', 'patterns')}] {e.get('key', '')}: {e.get('value', '')}{conf}")
    return "\n".join(lines)


def _last_session_block(note: dict) -> str:
    """Format the Governor's note from last session — private, never surface."""
    if not note:
        return ""
    lines = ["LAST SESSION NOTE (Governor's private carry-forward — do not mention to user):"]
    if note.get("what_surfaced"):
        lines.append(f"  What surfaced last time: {note['what_surfaced']}")
    if note.get("open_threads"):
        threads = note["open_threads"] if isinstance(note["open_threads"], list) else [note["open_threads"]]
        lines.append(f"  Open threads to pick up: {', '.join(threads)}")
    if note.get("captain_note"):
        lines.append(f"  Captain note: {note['captain_note']}")
    return "\n".join(lines)


def _capsule_context_block(context: dict) -> str:
    """Format capsule context (working memory) for injection into the system prompt."""
    lines = ["WORKING MEMORY (facts extracted this and recent sessions — less refined than portrait):"]
    for k, v in context.items():
        lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def _extract_and_save_artifacts(
    brain, response_text: str, capsule_id: str, session_id: str, turn_number: int
) -> list:
    """
    Scan response_text for ```html artifacts, save each to holo_artifacts.
    Returns list of {artifact_id, title, type} dicts for the API response.
    """
    saved = []
    for match in _re.finditer(r'```html\n?([\s\S]*?)```', response_text, _re.IGNORECASE):
        content = match.group(1).strip()
        if not _re.search(r'<!doctype|<html', content, _re.IGNORECASE):
            continue
        title_match = _re.search(r'<title>([^<]*)</title>', content, _re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else "Artifact"
        aid = brain.save_artifact(capsule_id, session_id, turn_number, title, content)
        if aid:
            saved.append({"artifact_id": aid, "title": title, "type": "html"})
    return saved



def _health_context(session: ChatSession) -> str:
    """
    Build the BATON_PASS snippet that HOLO_CHAT_SYSTEM_PROMPT references.
    Injected at the end of the system prompt every turn.
    """
    return (
        f"BATON_PASS:\n"
        f"  THREAD_HEALTH_SCORE: {session.thread_health_score}\n"
        f"  THREAD_HEALTH_LEVEL: {session.thread_health_level}\n"
        f"  THREAD_STATUS: {session.thread_status}\n"
        f"  USER_ALERT_RECOMMENDED: {session.user_alert}\n"
        f"  TASK_MODE: DEEP_REASONING"
    )
