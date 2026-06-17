"""
chat_engine.py

Holo chat mode — randomized multi-model conversation engine.

Every response comes from a randomly selected LLM provider.
The Governor is also randomly selected, but never shares DNA
with the analyst on the same turn. No predictable pattern exists.
All providers speak as Holo using the unified persona prompt.
"""

import logging
import os
import random
import re as _re
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from holo_context import HoloContextBuilder, build_context_budget_ledger
from holo_router import HoloRouter, PreviousRoute, RouteDecision
from holo_state import HoloState, RequiredTools
from holo_trace import HoloTraceRecord, log_trace
from llm_adapters import (
    HOLO_CHAT_SYSTEM_PROMPT,
    GovernorAdapter,
    load_adapters,
    load_fast_adapters,
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

    # Governor rotation state
    # Governor locks to one provider for 7–11 turns, then rotates when the
    # thread is healthy and no work is mid-resolution.
    governor_provider: Optional[str] = None
    governor_locked_since: int = 0
    governor_rotation_threshold: int = field(
        default_factory=lambda: random.randint(7, 11)
    )
    holo4dna_previous_route: Optional[PreviousRoute] = None

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
# Governor rotation helpers
# ---------------------------------------------------------------------------

DEFAULT_RUNTIME_PROFILE = "mini_only"
FRONTIER_RUNTIME_PROFILES = {"frontier_active", "legacy_frontier"}


def _holochat_runtime_profile() -> str:
    return (os.getenv("HOLOCHAT_RUNTIME_PROFILE") or DEFAULT_RUNTIME_PROFILE).strip().lower()


def _adapter_pool_metadata(adapters: list[Any]) -> list[dict[str, Optional[str]]]:
    return [_adapter_identity_dict(adapter) for adapter in adapters]


def _runtime_metadata(
    runtime_profile: str,
    active_pool: list[Any],
    bench_pool: list[Any],
) -> dict[str, Any]:
    mini_only = runtime_profile == "mini_only"
    return {
        "runtime_profile": runtime_profile,
        "active_pool": _adapter_pool_metadata(active_pool),
        "bench_pool": _adapter_pool_metadata(bench_pool),
        "frontier_enabled": not mini_only,
        "fallback_policy": "no_frontier_fallback" if mini_only else "bench_failover_enabled",
        "serial_call": True,
        "parallel_fanout": False,
    }


def _select_runtime_pools(
    profile: Optional[str] = None,
    *,
    fast_loader=None,
    frontier_loader=None,
) -> tuple[str, list[Any], list[Any]]:
    fast_loader = fast_loader or load_fast_adapters
    frontier_loader = frontier_loader or load_adapters
    runtime_profile = (profile or _holochat_runtime_profile()).strip().lower()
    if runtime_profile == "mini_only":
        active_pool = fast_loader()
        if not active_pool:
            raise RuntimeError(
                "HoloChat mini_only runtime has no mini adapters; "
                "frontier fallback is disabled."
            )
        return runtime_profile, active_pool, []
    if runtime_profile in FRONTIER_RUNTIME_PROFILES:
        active_pool, bench_pool = frontier_loader()
        if not active_pool:
            raise RuntimeError("HoloChat frontier runtime has no active adapters.")
        return runtime_profile, active_pool, bench_pool
    raise RuntimeError(f"Unsupported HOLOCHAT_RUNTIME_PROFILE: {runtime_profile}")


def _is_mid_resolution(last_assistant_message: str) -> bool:
    """
    Heuristic: return True if the last assistant message looks like it's in
    the middle of a multi-step task or numbered walkthrough.
    Prevents Governor rotation mid-way through active work.
    """
    if not last_assistant_message:
        return False
    text = last_assistant_message
    has_numbered_steps = bool(_re.search(r'^\s*[1-9]\.\s', text, _re.MULTILINE))
    continuation_phrases = [
        "next step", "step 1", "step 2", "step 3", "step 4", "step 5",
        "continuing from", "part 1", "part 2",
        "to summarize what we've covered so far",
        "here's what we have so far",
    ]
    has_continuation = any(phrase in text.lower() for phrase in continuation_phrases)
    return has_numbered_steps or has_continuation


def _should_rotate_governor(session: "ChatSession") -> bool:
    """
    Returns True if the Governor should rotate to a fresh provider.

    ALL conditions must be true:
      - At least governor_rotation_threshold turns since last rotation
      - Thread health is GREEN or YELLOW (not RED — don't destabilize a late thread)
      - No active work appears to be mid-resolution
    """
    if session.governor_provider is None:
        return True  # first turn — must lock

    turns_since = session.turn_count - session.governor_locked_since
    if turns_since < session.governor_rotation_threshold:
        return False

    if session.thread_health_level == "RED":
        return False

    last_assistant = next(
        (m["content"] for m in reversed(session.history) if m["role"] == "assistant"),
        ""
    )
    if _is_mid_resolution(last_assistant):
        return False

    return True


# ---------------------------------------------------------------------------
# Chat engine
# ---------------------------------------------------------------------------

class HoloChatEngine:
    """
    Manages the round-robin multi-model chat loop.
    One instance per application; sessions are keyed by session_id.
    """

    def __init__(self):
        self._runtime_profile, self._adapters, self._bench = _select_runtime_pools()
        self._runtime_info = _runtime_metadata(
            self._runtime_profile,
            self._adapters,
            self._bench,
        )
        self._governor = GovernorAdapter(self._adapters) # shares active pool, never same DNA as analyst
        self._brain    = ProjectBrain()
        self._holo_context_builder = HoloContextBuilder()
        self._holo_router = None
        logger.info(
            f"HoloChatEngine initialized. Runtime profile: {self._runtime_profile} | Active: "
            + ", ".join(a.provider for a in self._adapters)
            + (" | Bench: " + ", ".join(a.provider for a in self._bench) if self._bench else "")
            + " | GovernorAdapter ready"
        )

    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        if session_id and session_id in _sessions:
            return _sessions[session_id]
        new_id  = session_id or str(uuid.uuid4())
        session = ChatSession(session_id=new_id)

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
                     incognito: bool = False) -> Dict[str, Any]:
        """
        Process one user message. Returns Holo's response + metadata.
        The caller should use session_id from the returned dict for follow-up turns.

        incognito=True: blind mode — no capsule context, no Governor memory, no life portrait
        injected. Base system prompt only. Used for unbiased evaluation runs.
        """
        session             = self.get_or_create_session(session_id)
        session.last_active = time.time()

        # Incognito: strip all memory — only base system prompt reaches the model
        if incognito:
            capsule_context = {}
            life_context    = []
            last_session    = None
        else:
            capsule_context = self._brain.get_capsule_context(capsule_id) if capsule_id else {}
            life_context    = self._brain.load_life_context(capsule_id) if capsule_id else []
            last_session    = self._brain.load_last_consolidation(capsule_id) if capsule_id and session.turn_count == 0 else None

        # Randomly select analyst for this turn — no predictable pattern
        adapter = self._adapters[random.randrange(len(self._adapters))]
        session.rotation_index += 1
        session.turn_count     += 1

        # Governor rotation policy:
        # Lock to one provider for 7–11 turns. Rotate only when the thread is
        # healthy and no active work is mid-resolution. The no-same-family rule
        # is enforced by prepare_for_turn() on every rotation.
        if _should_rotate_governor(session):
            self._governor.prepare_for_turn(adapter)
            session.governor_provider        = self._governor.provider
            session.governor_locked_since    = session.turn_count
            session.governor_rotation_threshold = random.randint(7, 11)
            if session.turn_count > 1:
                logger.info(
                    f"Governor rotated → {session.governor_provider} "
                    f"(next rotation in {session.governor_rotation_threshold} turns)"
                )
        else:
            self._governor.lock_to_provider(session.governor_provider)

        # Governor runs the instruments: temperature + search decision
        temperature  = self._governor.assess_chat_temperature(user_message, session.history)
        search_query = self._governor.should_search(user_message, session.history)

        # Governor thinks about the human — skipped in incognito (would introduce bias)
        thought = None if incognito else self._governor.surface_thought(session.history, capsule_context, baton_pass=_health_context(session))
        tenor   = None if incognito else self._governor.assess_tenor(session.history, capsule_context, turn_count=session.turn_count, analyst_provider=adapter.provider)
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
            f"analyst={adapter.provider} | governor={self._governor.provider} | temp={temperature:.2f}"
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

        context_budget = _runtime_context_budget(
            session=session,
            user_message=user_message,
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            tenor=tenor,
            search_results=search_results,
            images=images,
            incognito=incognito,
        )

        holo4dna_shadow = None
        if _holo4dna_shadow_enabled():
            try:
                if self._holo_router is None:
                    self._holo_router = HoloRouter(self._adapters)
                holo4dna_shadow = _build_holo4dna_shadow_turn(
                    session=session,
                    capsule_id=capsule_id,
                    user_message=user_message,
                    runtime_adapter=adapter,
                    router=self._holo_router,
                    context_builder=self._holo_context_builder,
                    previous_route=session.holo4dna_previous_route,
                    capsule_context=capsule_context,
                    life_context=life_context,
                    last_session=last_session,
                    search_query=search_query,
                    search_results=search_results,
                    incognito=incognito,
                )
                session.holo4dna_previous_route = holo4dna_shadow.previous_route
            except Exception as exc:
                logger.warning("HoloChat 4DNA shadow trace failed: %s", exc)

        # Call the adapter — enriched_message includes search results if any
        # On failure, transparently fail over to a bench model from a different vendor
        start = time.time()
        try:
            response_text, in_tok, out_tok = adapter.chat_call(
                system_prompt, session.history, enriched_message, temperature,
                images=images or None,
            )
        except Exception as primary_err:
            logger.warning(f"Analyst {adapter.provider} failed: {primary_err} — attempting bench failover")
            bench_candidates = [b for b in self._bench if b.provider != adapter.provider]
            if not bench_candidates:
                raise
            fallback = random.choice(bench_candidates)
            logger.info(f"Bench failover: {fallback.provider}/{fallback.model_id}")
            response_text, in_tok, out_tok = fallback.chat_call(
                system_prompt, session.history, enriched_message, temperature,
                images=images or None,
            )
            adapter = fallback  # reflect actual analyst in metadata
        elapsed_ms = int((time.time() - start) * 1000)

        if holo4dna_shadow is not None:
            actual_analyst = _adapter_identity_dict(adapter)
            recorded_analyst = holo4dna_shadow.metadata["route"]["runtime_analyst"]
            if actual_analyst != recorded_analyst:
                holo4dna_shadow.metadata["route"]["runtime_analyst_after_failover"] = actual_analyst
                holo4dna_shadow.trace.extra_metadata["runtime_analyst_after_failover"] = actual_analyst

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
        memory_extraction_attempted = False
        memory_writes_count = 0
        if capsule_id and not incognito:
            memory_extraction_attempted = True
            updates = self._governor.extract_context_updates(session.history, capsule_context)
            for key, value in updates.items():
                self._brain.set_capsule_context(capsule_id, key, value)
            memory_writes_count = len(updates)
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

        if holo4dna_shadow is not None:
            holo4dna_shadow.trace.memory_extraction_attempted = memory_extraction_attempted
            holo4dna_shadow.trace.memory_writes_count = memory_writes_count
            log_trace(holo4dna_shadow.trace, logger=logger)

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
            "thought":             thought,
            "handoff":             handoff,
            "incognito":           incognito,
            "context_budget":      context_budget,
            "searched":            bool(search_query),
            "search_query":        search_query if search_query else None,
            "_provider":           adapter.provider,
            "_governor":           session.governor_provider,
            "_governor_turns_held": session.turn_count - session.governor_locked_since,
            "_temperature":        temperature,
            "artifacts":           artifacts_saved,
            "runtime":             getattr(
                self,
                "_runtime_info",
                _runtime_metadata("test_runtime", self._adapters, self._bench),
            ),
            **({"holo4dna": holo4dna_shadow.metadata} if holo4dna_shadow else {}),
        }

    def stream_message(self, session_id: str, user_message: str,
                       capsule_id: Optional[str] = None,
                       images: Optional[List[Dict[str, Any]]] = None,
                       incognito: bool = False):
        """
        Generator variant of send_message.

        Yields strings (text chunks) while the analyst streams its response,
        then yields a single sentinel dict with metadata once streaming is complete:
          {"done": True, "session_id": ..., "turn_number": ..., "thought": ...,
           "thread_health_level": ..., "thread_health_score": ..., "searched": bool,
           "artifacts": [...], "handoff": ...}

        The Governor's pre-turn work (temperature, search decision, tenor) runs
        synchronously before streaming starts. Post-turn work (context extraction,
        consolidation, thread naming, Supabase persist) runs in a background thread
        after the stream completes so the caller never blocks on it.
        """
        session             = self.get_or_create_session(session_id)
        session.last_active = time.time()

        if incognito:
            capsule_context = {}
            life_context    = []
            last_session    = None
        else:
            capsule_context = self._brain.get_capsule_context(capsule_id) if capsule_id else {}
            life_context    = self._brain.load_life_context(capsule_id) if capsule_id else []
            last_session    = self._brain.load_last_consolidation(capsule_id) if capsule_id and session.turn_count == 0 else None

        adapter = self._adapters[random.randrange(len(self._adapters))]
        session.rotation_index += 1
        session.turn_count     += 1

        if _should_rotate_governor(session):
            self._governor.prepare_for_turn(adapter)
            session.governor_provider             = self._governor.provider
            session.governor_locked_since         = session.turn_count
            session.governor_rotation_threshold   = random.randint(7, 11)
        else:
            self._governor.lock_to_provider(session.governor_provider)

        temperature  = self._governor.assess_chat_temperature(user_message, session.history)
        search_query = self._governor.should_search(user_message, session.history)
        thought      = None if incognito else self._governor.surface_thought(session.history, capsule_context, baton_pass=_health_context(session))
        tenor        = None if incognito else self._governor.assess_tenor(session.history, capsule_context, turn_count=session.turn_count, analyst_provider=adapter.provider)
        search_results = web_search.search(search_query) if search_query else None
        searched = bool(search_query)

        enriched_message = user_message
        if search_results:
            enriched_message = (
                f"{user_message}\n\n"
                f"[BACKGROUND CONTEXT: The following search results were retrieved to help you answer. "
                f"Use them silently — do not mention, quote, or reference that a search was performed. "
                f"If the results are irrelevant to the question, ignore them entirely.]\n\n"
                f"{search_results}"
            )

        system_prompt = HOLO_CHAT_SYSTEM_PROMPT
        if not incognito:
            system_prompt += (
                "\n\n" + _health_context(session)
                + ("\n\n" + _life_context_block(life_context) if life_context else "")
                + ("\n\n" + _last_session_block(last_session) if last_session else "")
                + ("\n\n" + _capsule_context_block(capsule_context) if capsule_context else "")
                + ("\n\nCAPTAIN BRIEF — READ + DIRECTIVE (private, never surface to user):\n" + tenor if tenor else "")
            )

        context_budget = _runtime_context_budget(
            session=session,
            user_message=user_message,
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            tenor=tenor,
            search_results=search_results,
            images=images,
            incognito=incognito,
        )

        holo4dna_shadow = None
        if _holo4dna_shadow_enabled():
            try:
                if self._holo_router is None:
                    self._holo_router = HoloRouter(self._adapters)
                holo4dna_shadow = _build_holo4dna_shadow_turn(
                    session=session,
                    capsule_id=capsule_id,
                    user_message=user_message,
                    runtime_adapter=adapter,
                    router=self._holo_router,
                    context_builder=self._holo_context_builder,
                    previous_route=session.holo4dna_previous_route,
                    capsule_context=capsule_context,
                    life_context=life_context,
                    last_session=last_session,
                    search_query=search_query,
                    search_results=search_results,
                    incognito=incognito,
                )
                session.holo4dna_previous_route = holo4dna_shadow.previous_route
            except Exception as exc:
                logger.warning("HoloChat 4DNA stream shadow trace failed: %s", exc)

        # Signal search before tokens arrive so the UI can show the indicator
        if searched:
            yield {"searching": True}

        # Stream analyst response token by token
        accumulated = []
        in_tok = out_tok = 0
        for chunk in adapter.stream_chat_call(
            system_prompt, session.history, enriched_message, temperature, images=images or None
        ):
            if isinstance(chunk, dict) and chunk.get("done"):
                in_tok  = chunk.get("in_tok", 0)
                out_tok = chunk.get("out_tok", 0)
            else:
                accumulated.append(chunk)
                yield chunk

        response_text = "".join(accumulated)

        # Post-stream: claims check (may append a correction to response_text)
        response_text, flagged_claims = self._governor.verify_claims(response_text, web_search.search)
        if flagged_claims:
            corrections = [f["correction"] for f in flagged_claims if f.get("correction")]
            if corrections:
                note = " · ".join(corrections)
                correction_text = f"\n\n*One thing worth correcting: {note}*"
                response_text  += correction_text
                yield correction_text

        # Commit history
        session.history.append({"role": "user",      "content": user_message})
        session.history.append({"role": "assistant",  "content": response_text})

        # Extract artifacts
        artifacts_saved = []
        if capsule_id and not incognito:
            artifacts_saved = _extract_and_save_artifacts(
                self._brain, response_text, capsule_id, session.session_id, session.turn_count
            )

        # Link session on first turn
        if capsule_id and session.turn_count == 1 and not incognito:
            self._brain.set_capsule_context(capsule_id, "last_session_id", session.session_id)
            self._brain.append_session_history(capsule_id, session.session_id, user_message)

        # Background: context extraction, consolidation, thread naming, Supabase persist
        def _post_stream():
            try:
                if capsule_id and not incognito:
                    updates = self._governor.extract_context_updates(session.history, capsule_context)
                    for key, value in updates.items():
                        self._brain.set_capsule_context(capsule_id, key, value)
                    if session.thread_health_level == "RED":
                        result = self._governor.consolidate_session(session.history, capsule_context, session.session_id)
                        if result.get("session_note"):
                            self._brain.save_consolidation(capsule_id, session.session_id, result["session_note"])
                        if result.get("life_context"):
                            self._brain.upsert_life_context(capsule_id, result["life_context"])
                    if session.turn_count == 2:
                        name = self._governor.name_session(list(session.history))
                        if name:
                            self._brain.update_session_name(capsule_id, session.session_id, name)
                self._brain.save_chat_turn(
                    session_id    = session.session_id,
                    turn_number   = session.turn_count,
                    user_message  = user_message,
                    holo_response = response_text,
                    provider      = adapter.provider,
                    temperature   = temperature,
                    capsule_id    = capsule_id,
                )
            except Exception as e:
                logger.warning(f"Post-stream background task failed: {e}")

        threading.Thread(target=_post_stream, daemon=True).start()

        if holo4dna_shadow is not None:
            holo4dna_shadow.trace.memory_extraction_attempted = bool(capsule_id and not incognito)
            log_trace(holo4dna_shadow.trace, logger=logger)

        handoff = None
        if session.thread_health_level == "RED":
            handoff = {
                "suggested":  True,
                "message":    "This thread is getting long. Everything important has been saved: your portrait, open threads, what shifted this session. Before you continue, tell me: how much context do you want carried into the next thread? (Full detail, key points only, or just pick up where we left off and I'll calibrate.)",
                "new_thread": "/chat",
            }

        yield {
            "done":                True,
            "session_id":          session.session_id,
            "response":            response_text,
            "turn_number":         session.turn_count,
            "thread_health_score": session.thread_health_score,
            "thread_health_level": session.thread_health_level,
            "thought":             thought,
            "searched":            searched,
            "search_query":        search_query if searched else None,
            "context_budget":      context_budget,
            "artifacts":           artifacts_saved,
            "handoff":             handoff,
            "incognito":           incognito,
            "_provider":           adapter.provider,
            "_temperature":        temperature,
            "runtime":             getattr(
                self,
                "_runtime_info",
                _runtime_metadata("test_runtime", self._adapters, self._bench),
            ),
            **({"holo4dna": holo4dna_shadow.metadata} if holo4dna_shadow else {}),
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

@dataclass(frozen=True)
class Holo4DnaShadowTurn:
    metadata: dict[str, Any]
    previous_route: PreviousRoute
    trace: HoloTraceRecord


def _env_flag(name: str) -> bool:
    return str(os.getenv(name, "")).strip().lower() in {"1", "true", "yes", "on"}


def _holo4dna_shadow_enabled() -> bool:
    return _env_flag("HOLOCHAT_4DNA_SHADOW") or _env_flag("HOLOCHAT_4DNA_ENABLED")


def _holo4dna_enabled() -> bool:
    return _env_flag("HOLOCHAT_4DNA_ENABLED")


def _adapter_identity_dict(adapter: Any) -> dict[str, Optional[str]]:
    return {
        "provider": getattr(adapter, "provider", None),
        "model": getattr(adapter, "model_id", getattr(adapter, "model", None)),
    }


def _required_tools_for_turn(search_query: Optional[str], search_results: Optional[str]) -> List[RequiredTools]:
    if search_query or search_results:
        return [RequiredTools.WEB_SEARCH]
    return [RequiredTools.NONE]


def _runtime_context_budget(
    *,
    session: ChatSession,
    user_message: str,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    tenor: Optional[str],
    search_results: Optional[str],
    images: Optional[List[Dict[str, Any]]],
    incognito: bool,
) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = [
        {
            "block_name": "base_holochat_prompt",
            "content": HOLO_CHAT_SYSTEM_PROMPT,
            "included": True,
            "source_type": "system",
        },
        {
            "block_name": "recent_session_history",
            "content": "\n".join(
                f"{message.get('role', 'unknown')}: {message.get('content', '')}"
                for message in session.history
            ),
            "included": bool(session.history),
            "source_type": "history",
            "reason": "passed as adapter history argument" if session.history else "empty",
        },
        {
            "block_name": "user_message",
            "content": user_message,
            "included": True,
            "source_type": "user",
        },
    ]

    if incognito:
        blocks.extend(
            [
                {
                    "block_name": "thread_health",
                    "content": "",
                    "included": False,
                    "source_type": "system",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "life_context",
                    "content": "",
                    "included": False,
                    "source_type": "memory",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "latest_consolidation",
                    "content": "",
                    "included": False,
                    "source_type": "memory",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "capsule_context",
                    "content": "",
                    "included": False,
                    "source_type": "memory",
                    "reason": "incognito mode",
                },
                {
                    "block_name": "captain_brief",
                    "content": "",
                    "included": False,
                    "source_type": "governor",
                    "reason": "incognito mode",
                },
            ]
        )
    else:
        blocks.append(
            {
                "block_name": "thread_health",
                "content": _health_context(session),
                "included": True,
                "source_type": "system",
            }
        )
        blocks.append(
            {
                "block_name": "life_context",
                "content": _life_context_block(life_context) if life_context else "",
                "included": bool(life_context),
                "source_type": "memory",
                "reason": "empty" if not life_context else None,
            }
        )
        blocks.append(
            {
                "block_name": "latest_consolidation",
                "content": _last_session_block(last_session) if last_session else "",
                "included": bool(last_session),
                "source_type": "memory",
                "reason": "empty" if not last_session else None,
            }
        )
        blocks.append(
            {
                "block_name": "capsule_context",
                "content": _capsule_context_block(capsule_context) if capsule_context else "",
                "included": bool(capsule_context),
                "source_type": "memory",
                "reason": "empty" if not capsule_context else None,
            }
        )
        blocks.append(
            {
                "block_name": "captain_brief",
                "content": f"CAPTAIN BRIEF — READ + DIRECTIVE (private, never surface to user):\n{tenor}" if tenor else "",
                "included": bool(tenor),
                "source_type": "governor",
                "reason": "empty" if not tenor else None,
            }
        )

    blocks.append(
        {
            "block_name": "web_results",
            "content": (
                "\n\n"
                "[BACKGROUND CONTEXT: The following search results were retrieved to help you answer. "
                "Use them silently — do not mention, quote, or reference that a search was performed. "
                "If the results are irrelevant to the question, ignore them entirely.]\n\n"
                f"{search_results}"
            ) if search_results else "",
            "included": bool(search_results),
            "source_type": "search",
            "reason": "no web results" if not search_results else None,
        }
    )
    blocks.append(
        {
            "block_name": "image_attachments",
            "content": "",
            "included": bool(images),
            "source_type": "artifact",
            "reason": f"{len(images or [])} image attachment(s) passed separately; binary not counted",
        }
    )

    return build_context_budget_ledger(blocks).model_dump(mode="json")


def _memory_presence_summary(
    *,
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    incognito: bool,
) -> dict[str, Any]:
    if incognito:
        return {"source": "HoloBrain", "incognito": True, "memory_in_prompt": False}
    return {
        "source": "HoloBrain",
        "incognito": False,
        "memory_in_prompt": bool(capsule_context or life_context or last_session),
        "capsule_context_keys": len(capsule_context or {}),
        "life_context_entries": len(life_context or []),
        "latest_consolidation_loaded": bool(last_session),
    }


def _route_decision_metadata(
    route: RouteDecision,
    *,
    runtime_adapter: Any,
    shadow_route: bool,
) -> dict[str, Any]:
    return {
        "shadow_route": shadow_route,
        "runtime_analyst": _adapter_identity_dict(runtime_adapter),
        "shadow_council": {
            "provider": route.council_provider,
            "model": route.council_model,
        },
        "hologov": {
            "provider": route.hologov_provider,
            "model": route.hologov_model,
            "tenure_remaining": route.hologov_tenure_remaining,
            "tenure_window": list(route.hologov_tenure_window),
        },
        "previous_council": {
            "provider": route.previous_council_provider,
            "model": route.previous_council_model,
        },
        "assigned_role": route.assigned_role,
        "route_reason": route.route_reason,
        "fallback_used": route.fallback_used,
        "fallback_reason": route.fallback_reason,
        "dna_degraded": route.dna_degraded,
        "eligible_provider_count": route.eligible_provider_count,
    }


def _thread_health_metadata(holo_state: HoloState) -> dict[str, Any]:
    return holo_state.thread_health.model_dump(mode="json")


def _build_holo4dna_shadow_turn(
    *,
    session: ChatSession,
    capsule_id: Optional[str],
    user_message: str,
    runtime_adapter: Any,
    router: HoloRouter,
    context_builder: HoloContextBuilder,
    previous_route: Optional[PreviousRoute],
    capsule_context: dict,
    life_context: list,
    last_session: Optional[dict],
    search_query: Optional[str],
    search_results: Optional[str],
    incognito: bool,
) -> Holo4DnaShadowTurn:
    required_tools = _required_tools_for_turn(search_query, search_results)
    holo_state = HoloState.from_chat_turn(
        session_id=session.session_id,
        capsule_id=capsule_id,
        turn_number=session.turn_count,
        user_message=user_message,
        thread_health_score=session.thread_health_score,
        thread_status=session.thread_status,
        required_tools=required_tools,
    )
    holo_state.memory_candidates.append(
        _memory_presence_summary(
            capsule_context=capsule_context,
            life_context=life_context,
            last_session=last_session,
            incognito=incognito,
        )
    )

    route = router.select_route(holo_state, previous_route=previous_route)
    context_packet = context_builder.build(
        base_system_prompt=HOLO_CHAT_SYSTEM_PROMPT,
        holo_state=holo_state,
        user_message=user_message,
        route_decision=route,
        capsule_context=capsule_context,
        life_context=life_context,
        latest_consolidation=last_session,
        recent_history=session.history,
        web_results=search_results,
        incognito=incognito,
    )

    route_metadata = _route_decision_metadata(route, runtime_adapter=runtime_adapter, shadow_route=True)
    thread_health = _thread_health_metadata(holo_state)
    metadata = {
        "shadow": True,
        "enabled": _holo4dna_enabled(),
        "state_id": holo_state.state_id,
        "state_schema_version": holo_state.schema_version,
        "dna_profile": route.dna_profile,
        "route": route_metadata,
        "context_hash": context_packet.context_hash,
        "context": {
            "included_blocks": context_packet.metadata.get("included_blocks", []),
            "omitted_blocks": context_packet.metadata.get("omitted_blocks", []),
            "char_count": context_packet.char_count,
            "token_estimate": context_packet.token_estimate,
        },
        "context_budget": context_packet.metadata.get("context_budget"),
        "thread_health": thread_health,
        "searched": bool(search_query or search_results),
        "search_query": search_query,
    }

    trace = HoloTraceRecord(
        session_id=session.session_id,
        turn_number=session.turn_count,
        holo_state_id=holo_state.state_id,
        holo_state_schema_version=holo_state.schema_version,
        dna_profile=route.dna_profile,
        shadow_route=True,
        runtime_analyst_provider=metadata["route"]["runtime_analyst"]["provider"],
        runtime_analyst_model=metadata["route"]["runtime_analyst"]["model"],
        selected_council_provider=route.council_provider,
        selected_council_model=route.council_model,
        selected_hologov_provider=route.hologov_provider,
        selected_hologov_model=route.hologov_model,
        assigned_role=route.assigned_role,
        route_reason=route.route_reason,
        searched=bool(search_query or search_results),
        search_query=search_query,
        thread_health=thread_health,
        context_packet_hash=context_packet.context_hash,
        context_blocks=context_packet.metadata.get("included_blocks", []),
        fallback_used=route.fallback_used,
        fallback_reason=route.fallback_reason,
        dna_degraded=route.dna_degraded,
        extra_metadata={
            "context_char_count": context_packet.char_count,
            "context_token_estimate": context_packet.token_estimate,
            "omitted_blocks": context_packet.metadata.get("omitted_blocks", []),
        },
    )
    return Holo4DnaShadowTurn(
        metadata=metadata,
        previous_route=route.as_previous_route(),
        trace=trace,
    )


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
