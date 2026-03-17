"""Holo V1 MVP -- Configuration via Pydantic Settings.

All values loaded from .env file or environment variables.
For Step 1, LLM keys and Supabase are optional (startup validation comes later).
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration. Every field maps to an env var (case-insensitive)."""

    # --- LLM Provider API Keys ---
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # --- Model IDs ---
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-sonnet-4-20250514"
    google_model: str = "gemini-1.5-pro"

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

    # --- Logging ---
    log_level: str = "INFO"

    # --- Streamlit ---
    holo_api_key: str = ""
    api_base_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Module-level singleton
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
