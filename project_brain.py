"""
project_brain.py

Holo's persistent memory layer — the "Project Brain."

Every completed evaluation writes to three clean, normalized tables.
Before each new evaluation, the brain retrieves relevant prior experience
as a PINNED artifact so every analyst starts informed.

Schema (3 tables — run the SQL block below once in Supabase):
  holo_vendor_profiles  — one row per vendor, updated after every evaluation
  holo_evaluations      — one row per evaluation (core fact table)
  holo_findings         — one row per HIGH/MEDIUM finding (queryable by category)

This normalization means:
  - Vendor lookup is a single indexed row, not a full table scan
  - Pattern queries ("all HIGH payment_routing findings") hit an index
  - The vendor profile compounds intelligence across evaluations automatically

────────────────────────────────────────────────────────────
  RUN THIS SQL ONCE IN YOUR SUPABASE DASHBOARD:
────────────────────────────────────────────────────────────

-- 1. Vendor profiles: one row per vendor, updated after every evaluation
CREATE TABLE IF NOT EXISTS holo_vendor_profiles (
    vendor_domain       text PRIMARY KEY,
    vendor_name         text,
    first_seen          timestamptz DEFAULT now(),
    last_seen           timestamptz DEFAULT now(),
    total_evaluations   int DEFAULT 0,
    allow_count         int DEFAULT 0,
    escalate_count      int DEFAULT 0,
    highest_risk_seen   text DEFAULT 'NONE',   -- NONE/LOW/MEDIUM/HIGH
    last_decision       text,
    last_exit_reason    text,
    last_brief          text
);

-- 2. Evaluations: one row per evaluation
CREATE TABLE IF NOT EXISTS holo_evaluations (
    evaluation_id       text PRIMARY KEY,
    created_at          timestamptz DEFAULT now(),
    vendor_domain       text REFERENCES holo_vendor_profiles(vendor_domain),
    vendor_name         text,
    decision            text NOT NULL,
    exit_reason         text,
    turns_completed     int,
    elapsed_ms          int,
    converged           boolean,
    oscillation         boolean DEFAULT false,
    decay               boolean DEFAULT false,
    evaluation_brief    text,
    -- Denormalized for fast coverage queries
    high_categories     text[],   -- e.g. ['payment_routing', 'domain_spoofing']
    medium_categories   text[]
);

CREATE INDEX IF NOT EXISTS idx_evals_vendor
    ON holo_evaluations (vendor_domain, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evals_decision
    ON holo_evaluations (decision, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_evals_high_cats
    ON holo_evaluations USING GIN (high_categories);

-- 3. Findings: one row per HIGH/MEDIUM finding, queryable by category
CREATE TABLE IF NOT EXISTS holo_findings (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    evaluation_id   text REFERENCES holo_evaluations(evaluation_id),
    vendor_domain   text,
    created_at      timestamptz DEFAULT now(),
    category        text NOT NULL,
    severity        text NOT NULL,
    fact_type       text,
    evidence        text,
    detail          text,
    turn_number     int,
    provider        text,
    role            text
);

CREATE INDEX IF NOT EXISTS idx_findings_vendor
    ON holo_findings (vendor_domain, category, severity);
CREATE INDEX IF NOT EXISTS idx_findings_category
    ON holo_findings (category, severity, created_at DESC);

────────────────────────────────────────────────────────────

Ambient signal layer (run these when building the full life-context system):

-- Enable pgvector for semantic retrieval
CREATE EXTENSION IF NOT EXISTS vector;

-- 7. Integrations — OAuth tokens and connection state per capsule per source
--    One row per (capsule_id, source). The Pilot reads this to know what
--    signal feeds are live for a given person.
CREATE TABLE IF NOT EXISTS holo_integrations (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    capsule_id      text REFERENCES holo_capsules(capsule_id) ON DELETE CASCADE,
    source          text NOT NULL,   -- 'gmail' | 'outlook' | 'slack' | 'calendar'
                                     -- | 'imessage' | 'stripe' | 'plaid' | 'chrome'
                                     -- | 'google_meet' | 'zoom' | 'teams' | 'webex'
                                     -- | 'notion' | 'linear' | 'github' | 'salesforce'
                                     -- | 'tesla' | 'connected_vehicle'  -- driving patterns,
                                     --   location, driving behavior, in-car listen history
                                     -- | 'spotify' | 'apple_podcasts' | 'youtube_music'
                                     --   -- what you listen to, when, how long, completion rate
    status          text DEFAULT 'connected',  -- 'connected' | 'disconnected' | 'error'
    scopes          text[],          -- OAuth scopes granted
    connected_at    timestamptz DEFAULT now(),
    last_synced_at  timestamptz,
    metadata        jsonb,           -- source-specific config (account email, etc.)
    UNIQUE (capsule_id, source)
);

CREATE INDEX IF NOT EXISTS idx_integrations_capsule
    ON holo_integrations (capsule_id, status);

-- 8. Ambient signals — the raw event log of the person's life
--    Append-only. High volume. Every signal from every connected source
--    lands here as a normalized event. The Pilot reads recent windows
--    to understand where the person is right now.
CREATE TABLE IF NOT EXISTS holo_signals (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    capsule_id      text REFERENCES holo_capsules(capsule_id) ON DELETE CASCADE,
    created_at      timestamptz DEFAULT now(),
    occurred_at     timestamptz NOT NULL,     -- when the event actually happened
    source          text NOT NULL,            -- 'gmail' | 'slack' | 'calendar' | etc.
    signal_type     text NOT NULL,            -- 'email_sent' | 'email_received'
                                              -- | 'message_sent' | 'meeting_attended'
                                              -- | 'purchase' | 'page_visit'
                                              -- | 'calendar_event' | 'task_completed'
                                              -- | 'meeting_transcript' | 'call_transcript'
                                              -- | 'drive_completed' | 'location_visit'
                                              -- | 'driving_behavior' | 'listen_session'
    sentiment       float,                    -- -1.0 to 1.0, null if not applicable
    energy_level    text,                     -- 'high' | 'medium' | 'low' | null
    -- Structured fields (populated based on signal_type)
    counterparty    text,                     -- who they emailed/messaged/met with
    subject         text,                     -- email subject, meeting title, etc.
    amount_usd      float,                    -- for purchases
    domain          text,                     -- for page visits
    duration_min    int,                      -- for meetings, calls
    -- Derived flags the Pilot sets after processing
    flagged         boolean DEFAULT false,    -- something the Pilot wants to surface
    flag_reason     text,
    -- Pilot-extracted nutrient (persists). Raw content does not.
    summary         text                      -- what the Pilot decided mattered from this event
);

CREATE INDEX IF NOT EXISTS idx_signals_capsule_time
    ON holo_signals (capsule_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_type
    ON holo_signals (capsule_id, signal_type, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_signals_flagged
    ON holo_signals (capsule_id, flagged) WHERE flagged = true;
CREATE INDEX IF NOT EXISTS idx_signals_source
    ON holo_signals (capsule_id, source, occurred_at DESC);

-- 9. Life context — synthesized understanding of who this person is right now.
--    Not raw events. Not history. The current true state of the person as the
--    Pilot understands it. Written and pruned by the Pilot, not by cron jobs.
--
--    Pruning rules (Pilot judgment, not automation):
--      - confidence decays 0.1 per week if no reinforcing signals arrive
--      - when confidence drops below 0.3, Pilot reviews: prune or reaffirm
--      - when something evolves (goal achieved, pattern broken, concern resolved),
--        Pilot explicitly marks the old insight pruned and writes the new state
--      - pruned rows are soft-deleted (pruned_at set), never hard-deleted immediately
--        so the Pilot can reference what changed and why
--      - hard delete after 30 days of soft deletion — no hoarding, no archaeology
--
--    The Pilot holds who you are now. Not who you were.
CREATE TABLE IF NOT EXISTS holo_life_context (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    capsule_id      text REFERENCES holo_capsules(capsule_id) ON DELETE CASCADE,
    created_at      timestamptz DEFAULT now(),
    updated_at      timestamptz DEFAULT now(),
    category        text NOT NULL,    -- 'financial' | 'relationships' | 'health'
                                      -- | 'work' | 'goals' | 'patterns' | 'emotional'
                                      -- | 'spiritual' | 'avoidances'
    key             text NOT NULL,    -- human-readable label e.g. 'cash_flow_concern'
    value           text NOT NULL,    -- the insight, written in plain language by Pilot
    confidence      float DEFAULT 1.0, -- 0.0–1.0, decays weekly without reinforcement
    last_reinforced timestamptz DEFAULT now(), -- last time a signal confirmed this
    reinforcement_count int DEFAULT 1,         -- how many times this has been confirmed
    source_signals  uuid[],           -- signal IDs that contributed to this insight
    -- Pruning fields
    pruned_at       timestamptz,      -- set when Pilot decides this is no longer true
    prune_reason    text,             -- what changed — written by Pilot, not a code flag
    superseded_by   uuid,             -- if replaced by a new insight, points to it
    embedding       vector(1536),     -- for semantic retrieval
    UNIQUE (capsule_id, key)
);

CREATE INDEX IF NOT EXISTS idx_life_context_active
    ON holo_life_context (capsule_id, category)
    WHERE pruned_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_life_context_decaying
    ON holo_life_context (capsule_id, confidence, last_reinforced)
    WHERE pruned_at IS NULL AND confidence < 0.5;
CREATE INDEX IF NOT EXISTS idx_life_context_pruned
    ON holo_life_context (capsule_id, pruned_at)
    WHERE pruned_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_life_context_embedding
    ON holo_life_context USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Automated confidence decay — runs nightly via Supabase scheduled function
-- UPDATE holo_life_context
--   SET confidence = GREATEST(0.0, confidence - 0.014)  -- ~0.1/week
-- WHERE pruned_at IS NULL
--   AND last_reinforced < now() - interval '3 days';
--
-- Hard delete soft-pruned rows after 30 days
-- DELETE FROM holo_life_context
-- WHERE pruned_at IS NOT NULL
--   AND pruned_at < now() - interval '30 days';

-- 10. Transcripts — TRANSIENT processing queue, not permanent storage.
--     The Pilot reads full_text once, extracts nutrients into holo_life_context
--     and holo_signals, then full_text is deleted (set to null).
--     Only the derived insights persist. Raw content does not accumulate.
--     status: 'pending' → Pilot hasn't processed yet
--             'processed' → nutrients extracted, full_text deleted
CREATE TABLE IF NOT EXISTS holo_transcripts (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    capsule_id      text REFERENCES holo_capsules(capsule_id) ON DELETE CASCADE,
    created_at      timestamptz DEFAULT now(),
    occurred_at     timestamptz NOT NULL,
    source          text NOT NULL,        -- 'google_meet' | 'zoom' | 'teams' | 'otter'
                                          -- | 'webex' | 'fireflies' | 'phone_call'
    transcript_type text NOT NULL,        -- 'meeting' | 'call' | '1on1' | 'coaching'
    title           text,
    participants    text[],
    duration_min    int,
    status          text DEFAULT 'pending',  -- 'pending' | 'processed'
    full_text       text,                 -- TRANSIENT — nulled after Pilot processes
    -- Nutrients extracted by Pilot (these persist after full_text is dropped)
    pilot_summary   text,
    decisions_made  text[],
    commitments     text[],
    stress_signals  text[],
    topics          text[]
);

CREATE INDEX IF NOT EXISTS idx_transcripts_pending
    ON holo_transcripts (capsule_id, status) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_transcripts_capsule_time
    ON holo_transcripts (capsule_id, occurred_at DESC);

-- 11. Session consolidations — what the Pilot wrote to memory after each session
--     The explicit record of what was learned, what changed, what was surfaced.
--     Feeds the session-open load so the Pilot always walks in knowing what happened.
CREATE TABLE IF NOT EXISTS holo_session_consolidations (
    id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    capsule_id      text REFERENCES holo_capsules(capsule_id) ON DELETE CASCADE,
    session_id      text,
    created_at      timestamptz DEFAULT now(),
    what_changed    text,    -- what the Pilot updated in life_context this session
    what_surfaced   text,    -- what thought bubbles were shown and whether they landed
    open_threads    text[],  -- things unresolved that the next session should pick up
    pilot_note      text     -- the Pilot's own note to herself for next time
);

CREATE INDEX IF NOT EXISTS idx_consolidations_capsule
    ON holo_session_consolidations (capsule_id, created_at DESC);

────────────────────────────────────────────────────────────

Chat storage (add these tables for Holo chat mode):

-- 4. Capsules — one row per user identity
CREATE TABLE IF NOT EXISTS holo_capsules (
    capsule_id     text PRIMARY KEY,
    google_id      text UNIQUE NOT NULL,
    email          text NOT NULL,
    name           text,
    avatar_url     text,
    created_at     timestamptz DEFAULT now(),
    last_active    timestamptz DEFAULT now(),
    mode           text DEFAULT 'personal'   -- 'personal' | 'work'
);

-- 5. Capsule context — persistent knowledge the Governor holds per user
CREATE TABLE IF NOT EXISTS holo_capsule_context (
    capsule_id     text REFERENCES holo_capsules(capsule_id),
    key            text NOT NULL,
    value          text,
    updated_at     timestamptz DEFAULT now(),
    PRIMARY KEY (capsule_id, key)
);

CREATE INDEX IF NOT EXISTS idx_capsule_context
    ON holo_capsule_context (capsule_id);

-- 6. Chat sessions
CREATE TABLE IF NOT EXISTS holo_chat_sessions (
    session_id    text PRIMARY KEY,
    created_at    timestamptz DEFAULT now(),
    last_active   timestamptz DEFAULT now(),
    turn_count    int DEFAULT 0
);

-- 5. Chat messages
CREATE TABLE IF NOT EXISTS holo_chat_messages (
    id            uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id    text REFERENCES holo_chat_sessions(session_id),
    created_at    timestamptz DEFAULT now(),
    role          text NOT NULL,
    content       text NOT NULL,
    provider      text,
    temperature   float,
    turn_number   int
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session
    ON holo_chat_messages (session_id, created_at ASC);

────────────────────────────────────────────────────────────
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

logger = logging.getLogger("holo.brain")

VENDOR_EVAL_LIMIT  = 5   # recent evaluations to surface per vendor
VENDOR_FINDING_LIMIT = 10  # recent HIGH findings to surface per vendor

# Severity rank for computing highest_risk_seen
_RISK_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}


class ProjectBrain:

    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            logger.warning(
                "ProjectBrain: SUPABASE_URL or SUPABASE_KEY not set. "
                "Running without persistent memory."
            )
            self._client = None
            return

        try:
            from supabase import create_client
            self._client = create_client(url, key)
            self._client.table("holo_vendor_profiles").select("vendor_domain").limit(1).execute()
            logger.info("ProjectBrain: connected.")
        except Exception as e:
            logger.warning(
                f"ProjectBrain: connection failed ({e}). "
                "Run the schema SQL in the Supabase dashboard."
            )
            self._client = None

    # -------------------------------------------------------------------------
    # Pre-evaluation: retrieve relevant prior experience
    # -------------------------------------------------------------------------

    def retrieve_context(self, action: dict, context: dict) -> Optional[dict]:
        """
        Build a prior-experience brief for this vendor before evaluation begins.

        Three fast queries:
          1. holo_vendor_profiles  — aggregate stats (single indexed row)
          2. holo_evaluations      — last N evaluations for this vendor
          3. holo_findings         — last N HIGH findings for this vendor

        Returns a dict for injection as a PINNED artifact, or None.
        """
        if not self._client:
            return None

        vendor_domain = self._extract_vendor_domain(context)
        if not vendor_domain:
            return None

        try:
            # 1. Vendor profile — aggregate intelligence
            profile_resp = (
                self._client
                .table("holo_vendor_profiles")
                .select("*")
                .eq("vendor_domain", vendor_domain)
                .maybe_single()
                .execute()
            )
            profile = profile_resp.data

            if not profile:
                logger.info(f"ProjectBrain: first evaluation for '{vendor_domain}'.")
                return None

            # 2. Recent evaluations
            evals_resp = (
                self._client
                .table("holo_evaluations")
                .select("evaluation_id, created_at, decision, exit_reason, "
                        "turns_completed, evaluation_brief, high_categories, "
                        "oscillation, decay")
                .eq("vendor_domain", vendor_domain)
                .order("created_at", desc=True)
                .limit(VENDOR_EVAL_LIMIT)
                .execute()
            )
            recent_evals = evals_resp.data or []

            # 3. Recent HIGH findings (queryable because findings is normalized)
            findings_resp = (
                self._client
                .table("holo_findings")
                .select("evaluation_id, created_at, category, severity, "
                        "fact_type, evidence, role")
                .eq("vendor_domain", vendor_domain)
                .eq("severity", "HIGH")
                .order("created_at", desc=True)
                .limit(VENDOR_FINDING_LIMIT)
                .execute()
            )
            prior_high_findings = findings_resp.data or []

            logger.info(
                f"ProjectBrain: '{vendor_domain}' — "
                f"{profile['total_evaluations']} total, "
                f"{profile['allow_count']} ALLOW / "
                f"{profile['escalate_count']} ESCALATE, "
                f"highest risk seen: {profile['highest_risk_seen']}."
            )

            return {
                "vendor_domain":       vendor_domain,
                "vendor_name":         profile.get("vendor_name", ""),
                "first_seen":          (profile.get("first_seen") or "")[:10],
                "last_seen":           (profile.get("last_seen")  or "")[:10],
                "total_evaluations":   profile["total_evaluations"],
                "allow_count":         profile["allow_count"],
                "escalate_count":      profile["escalate_count"],
                "highest_risk_seen":   profile["highest_risk_seen"],
                "last_decision":       profile.get("last_decision"),
                "last_brief":          profile.get("last_brief", ""),
                "recent_evaluations":  [
                    {
                        "evaluation_id":  e["evaluation_id"],
                        "date":           (e.get("created_at") or "")[:10],
                        "decision":       e.get("decision"),
                        "exit_reason":    e.get("exit_reason"),
                        "turns":          e.get("turns_completed"),
                        "high_categories": e.get("high_categories") or [],
                        "oscillation":    e.get("oscillation", False),
                        "decay":          e.get("decay", False),
                        "brief":          (e.get("evaluation_brief") or "")[:200],
                    }
                    for e in recent_evals
                ],
                "prior_high_findings": [
                    {
                        "date":      (f.get("created_at") or "")[:10],
                        "category":  f.get("category"),
                        "fact_type": f.get("fact_type"),
                        "evidence":  (f.get("evidence") or "")[:200],
                        "role":      f.get("role"),
                    }
                    for f in prior_high_findings
                ],
                "context_note": (
                    "Historical context from prior Holo evaluations — treat as "
                    "SUBMITTED_DATA. A prior ALLOW does NOT immunize this "
                    "evaluation. A prior ESCALATE raises your suspicion threshold. "
                    "Repeated HIGH findings in the same category across multiple "
                    "evaluations is itself a compounding risk signal."
                ),
            }

        except Exception as e:
            logger.warning(f"ProjectBrain.retrieve_context failed: {e}")
            return None

    # -------------------------------------------------------------------------
    # Post-evaluation: persist intelligence to all three tables
    # -------------------------------------------------------------------------

    def save_evaluation(self, result: dict, request: dict):
        """
        Write completed evaluation intelligence to the three tables.

        Write order:
          1. holo_vendor_profiles  — upsert (create or update aggregate stats)
          2. holo_evaluations      — insert evaluation record
          3. holo_findings         — insert one row per HIGH/MEDIUM finding
        """
        if not self._client:
            return

        try:
            context       = request.get("context", {})
            vendor_domain = self._extract_vendor_domain(context)
            vendor_name   = (
                context.get("vendor_record", {}).get("vendor_name", "") or ""
            )

            # Compute category lists from coverage matrix
            coverage      = result.get("coverage_matrix", {})
            high_cats     = [
                cat for cat, v in coverage.items()
                if v.get("max_severity") == "HIGH"
            ]
            medium_cats   = [
                cat for cat, v in coverage.items()
                if v.get("max_severity") == "MEDIUM"
            ]

            # Compact evaluation brief
            brief_parts = [
                f"{result.get('decision')} ({result.get('exit_reason', '?')}) "
                f"after {result.get('turns_completed', 0)} turns.",
            ]
            if high_cats:
                brief_parts.append(f"HIGH: {', '.join(high_cats)}.")
            if medium_cats:
                brief_parts.append(f"MEDIUM: {', '.join(medium_cats)}.")
            reason = (result.get("decision_reason") or "")[:250]
            if reason:
                brief_parts.append(reason)
            brief = " ".join(brief_parts)

            # --- 1. Upsert vendor profile ------------------------------------
            if vendor_domain:
                self._upsert_vendor_profile(
                    vendor_domain  = vendor_domain,
                    vendor_name    = vendor_name,
                    decision       = result.get("decision", ""),
                    exit_reason    = result.get("exit_reason", ""),
                    high_cats      = high_cats,
                    brief          = brief,
                )

            # --- 2. Insert evaluation record ---------------------------------
            self._client.table("holo_evaluations").insert({
                "evaluation_id":    result.get("evaluation_id"),
                "vendor_domain":    vendor_domain,
                "vendor_name":      vendor_name,
                "decision":         result.get("decision"),
                "exit_reason":      result.get("exit_reason"),
                "turns_completed":  result.get("turns_completed"),
                "elapsed_ms":       result.get("elapsed_ms"),
                "converged":        result.get("converged", False),
                "oscillation":      result.get("oscillation", False),
                "decay":            result.get("decay", False),
                "evaluation_brief": brief,
                "high_categories":  high_cats,
                "medium_categories": medium_cats,
                "created_at":       datetime.now(timezone.utc).isoformat(),
            }).execute()

            # --- 3. Insert normalized findings --------------------------------
            finding_rows = []
            for turn in result.get("turn_history", []):
                for f in turn.get("findings", []):
                    if f.get("severity") in ("HIGH", "MEDIUM"):
                        finding_rows.append({
                            "evaluation_id": result.get("evaluation_id"),
                            "vendor_domain": vendor_domain,
                            "category":      f.get("category"),
                            "severity":      f.get("severity"),
                            "fact_type":     f.get("fact_type"),
                            "evidence":      (f.get("evidence") or "")[:400],
                            "detail":        (f.get("detail")   or "")[:300],
                            "turn_number":   turn["turn_number"],
                            "provider":      turn["provider"],
                            "role":          turn["role"],
                            "created_at":    datetime.now(timezone.utc).isoformat(),
                        })

            if finding_rows:
                self._client.table("holo_findings").insert(finding_rows).execute()

            logger.info(
                f"ProjectBrain: saved {result.get('evaluation_id')} — "
                f"vendor '{vendor_domain}', decision {result.get('decision')}, "
                f"{len(finding_rows)} finding(s) written."
            )

        except Exception as e:
            logger.warning(f"ProjectBrain.save_evaluation failed: {e}")

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _upsert_vendor_profile(
        self,
        vendor_domain: str,
        vendor_name: str,
        decision: str,
        exit_reason: str,
        high_cats: list,
        brief: str,
    ):
        """
        Create or update the vendor's aggregate profile row.

        On conflict (vendor_domain already exists): increment counters,
        update highest_risk_seen if this evaluation found something worse,
        update last_seen and last_brief.
        """
        # Determine the highest risk seen in this evaluation
        this_risk = "HIGH" if high_cats else "MEDIUM"

        self._client.table("holo_vendor_profiles").upsert(
            {
                "vendor_domain":     vendor_domain,
                "vendor_name":       vendor_name or vendor_domain,
                "last_seen":         datetime.now(timezone.utc).isoformat(),
                "last_decision":     decision,
                "last_exit_reason":  exit_reason,
                "last_brief":        brief,
                # These are incremented server-side via Postgres function —
                # for simplicity in the MVP we re-fetch and increment in Python.
            },
            on_conflict="vendor_domain",
        ).execute()

        # Increment counters and update highest_risk_seen in a second call.
        # Fetch current profile first.
        resp = (
            self._client
            .table("holo_vendor_profiles")
            .select("total_evaluations, allow_count, escalate_count, "
                    "highest_risk_seen, first_seen")
            .eq("vendor_domain", vendor_domain)
            .maybe_single()
            .execute()
        )
        current = resp.data or {}

        total      = (current.get("total_evaluations") or 0) + 1
        allow_cnt  = (current.get("allow_count")       or 0) + (1 if decision == "ALLOW"    else 0)
        esc_cnt    = (current.get("escalate_count")    or 0) + (1 if decision == "ESCALATE" else 0)
        prior_risk = current.get("highest_risk_seen", "NONE")
        new_high   = (
            this_risk if _RISK_RANK.get(this_risk, 0) > _RISK_RANK.get(prior_risk, 0)
            else prior_risk
        )
        first_seen = current.get("first_seen") or datetime.now(timezone.utc).isoformat()

        self._client.table("holo_vendor_profiles").update({
            "total_evaluations": total,
            "allow_count":       allow_cnt,
            "escalate_count":    esc_cnt,
            "highest_risk_seen": new_high,
            "first_seen":        first_seen,
        }).eq("vendor_domain", vendor_domain).execute()

    # -------------------------------------------------------------------------
    # Capsule management
    # -------------------------------------------------------------------------

    def get_or_create_capsule(self, google_id: str, email: str,
                               name: str, avatar_url: str) -> Optional[dict]:
        """
        Fetch existing capsule or create one on first sign-in.
        Returns the capsule row dict, or None if DB unavailable.
        """
        if not self._client:
            return None
        try:
            resp = (
                self._client.table("holo_capsules")
                .select("*")
                .eq("google_id", google_id)
                .maybe_single()
                .execute()
            )
            if resp.data:
                # Update last_active + name/avatar in case they changed
                self._client.table("holo_capsules").update({
                    "last_active": datetime.now(timezone.utc).isoformat(),
                    "name":        name,
                    "avatar_url":  avatar_url,
                }).eq("google_id", google_id).execute()
                return resp.data

            # First sign-in — create capsule
            import uuid
            capsule_id = str(uuid.uuid4())
            row = {
                "capsule_id":  capsule_id,
                "google_id":   google_id,
                "email":       email,
                "name":        name,
                "avatar_url":  avatar_url,
                "mode":        "personal",
                "created_at":  datetime.now(timezone.utc).isoformat(),
                "last_active": datetime.now(timezone.utc).isoformat(),
            }
            self._client.table("holo_capsules").insert(row).execute()
            logger.info(f"ProjectBrain: new capsule created for {email}.")
            return row
        except Exception as e:
            logger.warning(f"ProjectBrain.get_or_create_capsule failed: {e}")
            return None

    def get_capsule(self, capsule_id: str) -> Optional[dict]:
        if not self._client:
            return None
        try:
            resp = (
                self._client.table("holo_capsules")
                .select("*")
                .eq("capsule_id", capsule_id)
                .maybe_single()
                .execute()
            )
            return resp.data
        except Exception:
            return None

    def set_capsule_mode(self, capsule_id: str, mode: str):
        """Switch between 'personal' and 'work' modes."""
        if not self._client:
            return
        try:
            self._client.table("holo_capsules").update({
                "mode": mode
            }).eq("capsule_id", capsule_id).execute()
        except Exception as e:
            logger.warning(f"ProjectBrain.set_capsule_mode failed: {e}")

    def get_capsule_context(self, capsule_id: str) -> dict:
        """Return all context key/value pairs for a capsule."""
        if not self._client:
            return {}
        try:
            resp = (
                self._client.table("holo_capsule_context")
                .select("key, value")
                .eq("capsule_id", capsule_id)
                .execute()
            )
            return {r["key"]: r["value"] for r in (resp.data or [])}
        except Exception:
            return {}

    def set_capsule_context(self, capsule_id: str, key: str, value: str):
        """Upsert a context entry for a capsule."""
        if not self._client:
            return
        try:
            self._client.table("holo_capsule_context").upsert({
                "capsule_id": capsule_id,
                "key":        key,
                "value":      value,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }, on_conflict="capsule_id,key").execute()
        except Exception as e:
            logger.warning(f"ProjectBrain.set_capsule_context failed: {e}")

    # -------------------------------------------------------------------------
    # Chat storage
    # -------------------------------------------------------------------------

    def save_chat_turn(
        self,
        session_id: str,
        turn_number: int,
        user_message: str,
        holo_response: str,
        provider: str,
        temperature: float,
        capsule_id: str = None,
    ):
        """
        Persist one chat turn (user message + Holo response) to Supabase.
        Upserts the session row and inserts two message rows.
        """
        if not self._client:
            return
        try:
            now = datetime.now(timezone.utc).isoformat()

            # Upsert session row — include capsule_id so threads are user-owned
            session_row = {
                "session_id":  session_id,
                "last_active": now,
                "turn_count":  turn_number,
            }
            if capsule_id:
                session_row["capsule_id"] = capsule_id
            self._client.table("holo_chat_sessions").upsert(
                session_row, on_conflict="session_id"
            ).execute()

            # Insert user + assistant messages
            self._client.table("holo_chat_messages").insert([
                {
                    "session_id":  session_id,
                    "role":        "user",
                    "content":     user_message,
                    "turn_number": turn_number,
                    "created_at":  now,
                },
                {
                    "session_id":  session_id,
                    "role":        "assistant",
                    "content":     holo_response,
                    "provider":    provider,
                    "temperature": temperature,
                    "turn_number": turn_number,
                    "created_at":  now,
                },
            ]).execute()

            logger.info(f"ProjectBrain: saved chat turn {turn_number} for session {session_id[:8]}.")
        except Exception as e:
            logger.warning(f"ProjectBrain.save_chat_turn failed: {e}")

    def load_chat_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load full message history for a session from Supabase.
        Returns list of {"role": ..., "content": ...} dicts, or None if not found.
        """
        if not self._client:
            return None
        try:
            resp = (
                self._client
                .table("holo_chat_messages")
                .select("role, content")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .execute()
            )
            rows = resp.data or []
            if not rows:
                return None
            return [{"role": r["role"], "content": r["content"]} for r in rows]
        except Exception as e:
            logger.warning(f"ProjectBrain.load_chat_history failed: {e}")
            return None

    def list_sessions(self, capsule_id: str, limit: int = 40) -> list:
        """
        Return all chat sessions for a capsule, newest first.
        Each entry includes session_id, created_at, last_active, turn_count,
        and the first user message as a preview title.
        """
        if not self._client or not capsule_id:
            return []
        try:
            rows = (
                self._client.table("holo_chat_sessions")
                .select("session_id, created_at, last_active, turn_count")
                .eq("capsule_id", capsule_id)
                .order("last_active", desc=True)
                .limit(limit)
                .execute()
            ).data or []

            if not rows:
                return []

            # Fetch first user message for each session to use as title
            session_ids = [r["session_id"] for r in rows]
            previews = {}
            for sid in session_ids:
                try:
                    first = (
                        self._client.table("holo_chat_messages")
                        .select("content")
                        .eq("session_id", sid)
                        .eq("role", "user")
                        .order("created_at", desc=False)
                        .limit(1)
                        .execute()
                    ).data
                    if first:
                        previews[sid] = first[0]["content"][:80]
                except Exception:
                    pass

            for r in rows:
                r["preview"] = previews.get(r["session_id"], "New conversation")

            return rows
        except Exception as e:
            logger.warning(f"ProjectBrain.list_sessions failed: {e}")
            return []

    def save_consolidation(self, capsule_id: str, session_id: str, session_note: dict) -> None:
        """Persist the Pilot's session-end note to holo_session_consolidations."""
        if not self._client or not session_note:
            return
        try:
            self._client.table("holo_session_consolidations").insert({
                "capsule_id":   capsule_id,
                "session_id":   session_id,
                "what_changed": session_note.get("what_changed", ""),
                "what_surfaced": session_note.get("what_surfaced", ""),
                "open_threads": session_note.get("open_threads", []),
                "pilot_note":   session_note.get("pilot_note", ""),
                "created_at":   datetime.now(timezone.utc).isoformat(),
            }).execute()
            logger.info(f"ProjectBrain: session consolidation saved for {capsule_id[:8]}.")
        except Exception as e:
            logger.warning(f"ProjectBrain.save_consolidation failed: {e}")

    def upsert_life_context(self, capsule_id: str, entries: list) -> None:
        """
        Write the Pilot's distilled life_context entries for a capsule.
        If an entry supersedes an existing key, soft-prune the old one first.
        """
        if not self._client or not entries:
            return
        now = datetime.now(timezone.utc).isoformat()
        for entry in entries:
            key = entry.get("key", "").strip()
            if not key:
                continue
            try:
                # Soft-prune any entry this supersedes
                supersedes = entry.get("supersedes")
                if supersedes:
                    self._client.table("holo_life_context").update({
                        "pruned_at":    now,
                        "prune_reason": f"Superseded by '{key}' after session consolidation.",
                    }).eq("capsule_id", capsule_id).eq("key", supersedes).is_("pruned_at", "null").execute()

                # Upsert the new insight
                self._client.table("holo_life_context").upsert({
                    "capsule_id":         capsule_id,
                    "category":           entry.get("category", "patterns"),
                    "key":                key,
                    "value":              entry.get("value", "")[:500],
                    "confidence":         1.0,
                    "last_reinforced":    now,
                    "reinforcement_count": 1,
                    "updated_at":         now,
                }, on_conflict="capsule_id,key").execute()

            except Exception as e:
                logger.warning(f"ProjectBrain.upsert_life_context failed for key '{key}': {e}")

        logger.info(f"ProjectBrain: {len(entries)} life_context entries upserted for {capsule_id[:8]}.")

    def load_life_context(self, capsule_id: str) -> list:
        """
        Load the active (non-pruned) life_context entries for a capsule.
        Returns list of {category, key, value, confidence} dicts, ordered by confidence desc.
        """
        if not self._client:
            return []
        try:
            resp = (
                self._client.table("holo_life_context")
                .select("category, key, value, confidence")
                .eq("capsule_id", capsule_id)
                .is_("pruned_at", "null")
                .order("confidence", desc=True)
                .execute()
            )
            return resp.data or []
        except Exception as e:
            logger.warning(f"ProjectBrain.load_life_context failed: {e}")
            return []

    def load_last_consolidation(self, capsule_id: str) -> Optional[dict]:
        """Load the most recent session consolidation note for a capsule."""
        if not self._client:
            return None
        try:
            resp = (
                self._client.table("holo_session_consolidations")
                .select("what_changed, what_surfaced, open_threads, pilot_note, created_at")
                .eq("capsule_id", capsule_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            return resp.data[0] if resp.data else None
        except Exception as e:
            logger.warning(f"ProjectBrain.load_last_consolidation failed: {e}")
            return None

    def append_session_history(self, capsule_id: str, session_id: str, first_message: str) -> None:
        """
        Append this session to the capsule's session history list.
        Stored as JSON in holo_capsule_context under key '_session_history'.
        No schema changes required — uses the existing context table.
        Keeps last 50 sessions; newest is at the end of the list.
        """
        import json
        if not self._client:
            return
        try:
            resp = (
                self._client.table("holo_capsule_context")
                .select("value")
                .eq("capsule_id", capsule_id)
                .eq("key", "_session_history")
                .maybe_single()
                .execute()
            )
            existing: list = []
            if resp.data:
                try:
                    existing = json.loads(resp.data["value"]) or []
                except Exception:
                    existing = []

            now = datetime.now(timezone.utc).isoformat()
            entry = {
                "id":      session_id,
                "at":      now,
                "preview": first_message[:80],
            }
            # Deduplicate by session_id (handles retries on first turn)
            existing = [e for e in existing if e.get("id") != session_id]
            existing.append(entry)
            if len(existing) > 50:
                existing = existing[-50:]

            self._client.table("holo_capsule_context").upsert({
                "capsule_id": capsule_id,
                "key":        "_session_history",
                "value":      json.dumps(existing),
                "updated_at": now,
            }, on_conflict="capsule_id,key").execute()

        except Exception as e:
            logger.warning(f"ProjectBrain.append_session_history failed: {e}")

    def update_session_name(self, capsule_id: str, session_id: str, name: str) -> None:
        """Update the Pilot-generated title for a session in the session history list."""
        import json
        if not self._client or not name:
            return
        try:
            resp = (
                self._client.table("holo_capsule_context")
                .select("value")
                .eq("capsule_id", capsule_id)
                .eq("key", "_session_history")
                .maybe_single()
                .execute()
            )
            if not resp.data:
                return
            entries = json.loads(resp.data["value"]) or []
            updated = False
            for e in entries:
                if e.get("id") == session_id:
                    e["title"] = name
                    updated = True
                    break
            if not updated:
                return
            self._client.table("holo_capsule_context").update({
                "value":      json.dumps(entries),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }).eq("capsule_id", capsule_id).eq("key", "_session_history").execute()
            logger.info(f"ProjectBrain: session {session_id[:8]} named '{name}'.")
        except Exception as e:
            logger.warning(f"ProjectBrain.update_session_name failed: {e}")

    def load_session_list(self, capsule_id: str) -> list:
        """
        Return list of sessions for this capsule, newest first.
        Each entry: {id, at, preview}
        """
        import json
        if not self._client:
            return []
        try:
            resp = (
                self._client.table("holo_capsule_context")
                .select("value")
                .eq("capsule_id", capsule_id)
                .eq("key", "_session_history")
                .maybe_single()
                .execute()
            )
            if not resp or not resp.data:
                return []
            entries = json.loads(resp.data["value"]) or []
            return list(reversed(entries))  # newest first
        except Exception as e:
            logger.warning(f"ProjectBrain.load_session_list failed: {e}")
            return []

    def _extract_vendor_domain(self, context: dict) -> Optional[str]:
        """Extract vendor email domain from the context bundle."""
        vendor_email = (
            context.get("vendor_record", {}).get("vendor_email", "") or ""
        )
        if "@" in vendor_email:
            return vendor_email.split("@")[-1].lower()
        return None
