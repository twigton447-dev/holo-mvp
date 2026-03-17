"""Holo V1 MVP -- LLM Provider Adapters.

Abstract base + concrete adapters for OpenAI (GPT-5.4),
Anthropic (Claude Sonnet 4.6), and Google (Gemini 3.1 Pro).

Each adapter uses native structured output / function calling
and returns a Pydantic-validated RoundOutput.
"""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod

from models import ROUND_OUTPUT_SCHEMA, RoundOutput

logger = logging.getLogger("holo.adapters")


class ModelResponse:
    """Wrapper for a model API response with token usage."""

    def __init__(
        self,
        round_output: RoundOutput,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: int = 0,
    ):
        self.round_output = round_output
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.latency_ms = latency_ms


class BaseModelAdapter(ABC):
    """Abstract base for LLM provider adapters."""

    provider_name: str
    model_id: str

    @abstractmethod
    def evaluate(
        self,
        system_prompt: str,
        user_message: str,
        timeout: int = 15,
    ) -> ModelResponse:
        """Call the LLM and return a validated ModelResponse."""
        ...


# ============================================================
# OpenAI Adapter (GPT-5.4)
# ============================================================


class OpenAIAdapter(BaseModelAdapter):
    provider_name = "openai"

    def __init__(self, api_key: str, model_id: str, temperature: float = 0.2):
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model_id = model_id
        self.temperature = temperature

    def evaluate(
        self,
        system_prompt: str,
        user_message: str,
        timeout: int = 15,
    ) -> ModelResponse:
        start = time.time()

        response = self.client.chat.completions.create(
            model=self.model_id,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            tools=[
                {"type": "function", "function": ROUND_OUTPUT_SCHEMA}
            ],
            tool_choice={
                "type": "function",
                "function": {"name": "submit_risk_assessment"},
            },
            timeout=timeout,
        )

        latency_ms = int((time.time() - start) * 1000)

        # Extract function call arguments
        tool_call = response.choices[0].message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)

        # Validate with Pydantic
        round_output = RoundOutput(**args)

        usage = response.usage
        return ModelResponse(
            round_output=round_output,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms,
        )


# ============================================================
# Anthropic Adapter (Claude Sonnet 4.6)
# ============================================================


class AnthropicAdapter(BaseModelAdapter):
    provider_name = "anthropic"

    def __init__(self, api_key: str, model_id: str, temperature: float = 0.2):
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)
        self.model_id = model_id
        self.temperature = temperature

    def evaluate(
        self,
        system_prompt: str,
        user_message: str,
        timeout: int = 15,
    ) -> ModelResponse:
        start = time.time()

        # Convert to Anthropic tool format
        tool_def = {
            "name": ROUND_OUTPUT_SCHEMA["name"],
            "description": ROUND_OUTPUT_SCHEMA["description"],
            "input_schema": ROUND_OUTPUT_SCHEMA["parameters"],
        }

        response = self.client.messages.create(
            model=self.model_id,
            max_tokens=4096,
            temperature=self.temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            tools=[tool_def],
            tool_choice={"type": "tool", "name": "submit_risk_assessment"},
            timeout=timeout,
        )

        latency_ms = int((time.time() - start) * 1000)

        # Extract tool use block
        tool_block = next(
            b for b in response.content if b.type == "tool_use"
        )
        args = tool_block.input

        # Validate with Pydantic
        round_output = RoundOutput(**args)

        usage = response.usage
        return ModelResponse(
            round_output=round_output,
            input_tokens=usage.input_tokens if usage else 0,
            output_tokens=usage.output_tokens if usage else 0,
            latency_ms=latency_ms,
        )


# ============================================================
# Google Adapter (Gemini 3.1 Pro)
# ============================================================


class GeminiAdapter(BaseModelAdapter):
    provider_name = "google"

    def __init__(self, api_key: str, model_id: str, temperature: float = 0.2):
        from google import genai
        from google.genai import types

        self._genai = genai
        self._types = types
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id
        self.temperature = temperature

    def evaluate(
        self,
        system_prompt: str,
        user_message: str,
        timeout: int = 15,
    ) -> ModelResponse:
        start = time.time()
        types = self._types

        # Build Gemini function declaration
        func_decl = types.FunctionDeclaration(
            name=ROUND_OUTPUT_SCHEMA["name"],
            description=ROUND_OUTPUT_SCHEMA["description"],
            parameters=ROUND_OUTPUT_SCHEMA["parameters"],
        )

        tool = types.Tool(function_declarations=[func_decl])

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[tool],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="ANY",
                    allowed_function_names=["submit_risk_assessment"],
                )
            ),
            temperature=self.temperature,
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=user_message,
            config=config,
        )

        latency_ms = int((time.time() - start) * 1000)

        # Extract function call from response
        fc = response.candidates[0].content.parts[0].function_call

        # Normalize Gemini's proto objects to plain dicts
        if hasattr(fc.args, "items"):
            args = dict(fc.args)
        else:
            args = json.loads(str(fc.args))
        args = json.loads(json.dumps(args, default=str))

        # Validate with Pydantic
        round_output = RoundOutput(**args)

        # Token usage from Gemini metadata
        usage = getattr(response, "usage_metadata", None)
        input_tokens = (
            getattr(usage, "prompt_token_count", 0) if usage else 0
        )
        output_tokens = (
            getattr(usage, "candidates_token_count", 0) if usage else 0
        )

        return ModelResponse(
            round_output=round_output,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )


# ============================================================
# Factory
# ============================================================


def create_adapters(settings) -> dict[str, BaseModelAdapter]:
    """Create all three provider adapters from settings."""
    return {
        "openai": OpenAIAdapter(
            api_key=settings.openai_api_key,
            model_id=settings.openai_model,
            temperature=settings.temperature,
        ),
        "anthropic": AnthropicAdapter(
            api_key=settings.anthropic_api_key,
            model_id=settings.anthropic_model,
            temperature=settings.temperature,
        ),
        "google": GeminiAdapter(
            api_key=settings.google_api_key,
            model_id=settings.google_model,
            temperature=settings.temperature,
        ),
    }
