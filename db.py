"""Holo V1 MVP -- Supabase Database Client.

Thin wrapper around supabase-py for API key validation,
evaluation logging, dashboard stats, and model pricing.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Optional

from supabase import create_client, Client

logger = logging.getLogger("holo.db")


class Database:
    """All Supabase operations for the Holo MVP."""

    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    # ----------------------------------------------------------------
    # API Key Operations
    # ----------------------------------------------------------------

    def validate_api_key(self, raw_key: str) -> Optional[dict]:
        """Hash the incoming key and look it up. Returns the row or None."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        result = (
            self.client.table("api_keys")
            .select("*")
            .eq("key_hash", key_hash)
            .eq("is_active", True)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None

    def insert_api_key(
        self, key_hash: str, key_prefix: str, name: str, max_rpm: int = 10
    ) -> dict:
        """Insert a new API key record. Returns the created row."""
        result = (
            self.client.table("api_keys")
            .insert(
                {
                    "key_hash": key_hash,
                    "key_prefix": key_prefix,
                    "name": name,
                    "max_requests_per_minute": max_rpm,
                }
            )
            .execute()
        )
        return result.data[0]

    # ----------------------------------------------------------------
    # Evaluation Log Operations
    # ----------------------------------------------------------------

    def log_evaluation(self, record: dict) -> dict:
        """Insert an evaluation log record."""
        result = (
            self.client.table("evaluation_logs").insert(record).execute()
        )
        return result.data[0]

    def get_evaluations(self, limit: int = 50) -> list[dict]:
        """Fetch recent evaluations, newest first."""
        result = (
            self.client.table("evaluation_logs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def get_evaluation_stats(self) -> dict:
        """Compute summary stats for the dashboard."""
        all_logs = (
            self.client.table("evaluation_logs")
            .select("decision, rounds_completed, total_cost_usd")
            .execute()
        )
        data = all_logs.data
        if not data:
            return {
                "total": 0,
                "allow_count": 0,
                "escalate_count": 0,
                "avg_rounds": 0.0,
                "total_cost": 0.0,
            }

        allow_count = sum(1 for r in data if r["decision"] == "ALLOW")
        escalate_count = sum(1 for r in data if r["decision"] == "ESCALATE")
        avg_rounds = sum(r.get("rounds_completed") or 0 for r in data) / len(data)
        total_cost = sum(float(r["total_cost_usd"]) for r in data if r.get("total_cost_usd") is not None)

        return {
            "total": len(data),
            "allow_count": allow_count,
            "escalate_count": escalate_count,
            "avg_rounds": round(avg_rounds, 1),
            "total_cost": round(total_cost, 4),
        }

    # ----------------------------------------------------------------
    # Model Pricing Operations
    # ----------------------------------------------------------------

    def get_model_pricing(self) -> dict[str, dict]:
        """Fetch pricing for all active models. Returns dict keyed by model_id."""
        result = (
            self.client.table("model_pricing")
            .select("*")
            .eq("is_active", True)
            .execute()
        )
        return {
            row["model_id"]: {
                "input_price_per_1m": float(row["input_price_per_1m_tokens"]),
                "output_price_per_1m": float(row["output_price_per_1m_tokens"]),
            }
            for row in result.data
        }

    # ----------------------------------------------------------------
    # Health Check
    # ----------------------------------------------------------------

    def check_connection(self) -> bool:
        """Verify Supabase is reachable."""
        try:
            self.client.table("api_keys").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection check failed: {e}")
            return False
