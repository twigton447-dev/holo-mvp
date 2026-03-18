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
"""

import logging
import os
from datetime import datetime, timezone
from typing import Optional

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
                .single()
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
            .single()
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

    def _extract_vendor_domain(self, context: dict) -> Optional[str]:
        """Extract vendor email domain from the context bundle."""
        vendor_email = (
            context.get("vendor_record", {}).get("vendor_email", "") or ""
        )
        if "@" in vendor_email:
            return vendor_email.split("@")[-1].lower()
        return None
