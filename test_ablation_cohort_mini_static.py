"""
Static checks for the five-mini ablation cohort.

No API calls. No benchmark packets. This keeps mini-doctrine config drift visible.
"""

from __future__ import annotations

import json
from pathlib import Path


COHORT_PATH = Path("ablation_cohort_mini.json")
ADAPTERS_PATH = Path("llm_adapters.py")

EXPECTED_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "google": "gemini-2.5-flash-lite",
    "xai": "grok-3-mini",
    "minimax": "MiniMax-Text-01",
}

EXPECTED_LABELS = {
    "openai": "A-OpenAI-mini",
    "anthropic": "A-Claude-Haiku",
    "google": "A-Gemini-FlashLite",
    "xai": "A-Grok-mini",
    "minimax": "A-MiniMax",
}

FRONTIER_TOKENS = (
    "gpt-5",
    "claude-sonnet",
    "gemini-2.5-pro",
    "grok-3\"",
    "mistral-large",
)


def main() -> None:
    cohort = json.loads(COHORT_PATH.read_text())
    models = cohort.get("models", {})
    labels = cohort.get("condition_labels", {}).get("solo", {})

    assert cohort.get("cohort_id") == "five-mini-2026-06-17"
    assert cohort.get("doctrine") == "mini_only_default"
    assert models == EXPECTED_MODELS
    assert labels == EXPECTED_LABELS
    assert cohort.get("condition_labels", {}).get("holo_architecture", {}).get("planned") == "E-HoloArch-mini"
    assert cohort.get("condition_labels", {}).get("holo_architecture", {}).get("status") == "pending_adapter_support"

    cohort_text = COHORT_PATH.read_text()
    for token in FRONTIER_TOKENS:
        assert token not in cohort_text, f"frontier token present in mini cohort: {token}"

    adapters_text = ADAPTERS_PATH.read_text()
    assert "https://api.minimax.io/v1" in adapters_text
    assert "MINIMAX_BASE_URL" in adapters_text

    print("five-mini cohort static checks PASS")


if __name__ == "__main__":
    main()
