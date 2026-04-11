"""Holo V1 MVP -- Configuration via Pydantic Settings.

All values loaded from .env file or environment variables.
For Step 1, LLM keys and Supabase are optional (startup validation comes later).
"""

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RoutingSettings(BaseModel):
    """
    Client-configurable routing parameters.

    Set during pilot onboarding. Stored as config.routing.*
    All defaults represent the system-wide baseline — clients may override
    fast_amount_floor_usd to match their typical transaction profile.

    Fields:
      fast_amount_floor_usd    Transactions at or below this amount are eligible
                               for FAST tier (lightweight models, 3-turn cap).
                               Default: $1,000. Client may lower for high-volume
                               low-value processors or raise for conservative routing.
      urgency_patterns_path    Path to urgency_patterns.json. Relative to the
                               working directory of the server process.
    """
    fast_amount_floor_usd:  float = 1_000.0
    urgency_patterns_path:  str   = "urgency_patterns.json"


class Settings(BaseSettings):
    """Central configuration. Every field maps to an env var (case-insensitive)."""

    # --- LLM Provider API Keys ---
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # --- Model IDs ---
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-sonnet-4-20250514"
    google_model: str = "gemini-2.5-pro"

    # --- Supabase ---
    supabase_url: str = ""
    supabase_key: str = ""

    # --- Evaluation Defaults ---
    max_rounds: int = 5
    min_rounds_before_convergence: int = 3
    consecutive_zero_deltas_for_convergence: int = 2
    temperature: float = 0.2
    per_call_timeout_seconds: int = 15
    total_timeout_seconds: int = 120

    # --- Routing ---
    # Override via env vars: ROUTING__FAST_AMOUNT_FLOOR_USD, etc.
    routing: RoutingSettings = RoutingSettings()

    # --- Logging ---
    log_level: str = "INFO"

    # --- Streamlit ---
    holo_api_key: str = ""
    api_base_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Module-level singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
