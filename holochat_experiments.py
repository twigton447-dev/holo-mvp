"""Deterministic, provider-safe HoloChat experiment planning and accounting.

The default path deliberately creates an estimate-only manifest.  It does not
inspect environment variables, import provider SDKs, or invoke network clients.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Callable, Mapping


PRICING_VERSION = "official-2026-07-14"
PRICE_UNIT = "USD per 1M tokens"
PRICING_SOURCE = "Versioned official provider price catalog supplied for 2026-07-14"
SCHEMA_VERSION = "holochat-experiment-v1"


@dataclass(frozen=True)
class ModelPrice:
    provider: str
    model: str
    input_per_million: Decimal
    output_per_million: Decimal


def _price(provider: str, model: str, input_price: str, output_price: str) -> ModelPrice:
    return ModelPrice(provider, model, Decimal(input_price), Decimal(output_price))


PRICE_CATALOG: dict[str, ModelPrice] = {
    "openai/gpt-5.5": _price("openai", "gpt-5.5", "5", "30"),
    "openai/gpt-5.4": _price("openai", "gpt-5.4", "2.5", "15"),
    "openai/gpt-5.4-mini": _price("openai", "gpt-5.4-mini", ".75", "4.5"),
    "xai/grok-4.3": _price("xai", "grok-4.3", "1.25", "2.5"),
    "xai/grok-4.5": _price("xai", "grok-4.5", "2", "6"),
    "google/gemini-3.1-flash-lite": _price("google", "gemini-3.1-flash-lite", ".25", "1.5"),
    "google/gemini-3.5-flash": _price("google", "gemini-3.5-flash", "1.5", "9"),
    "google/gemini-3.1-pro-preview": _price("google", "gemini-3.1-pro-preview", "2", "12"),
    "deepseek/v4-flash": _price("deepseek", "v4-flash", ".14", ".28"),
    "deepseek/v4-pro": _price("deepseek", "v4-pro", ".435", ".87"),
    "minimax/MiniMax-M2.7-highspeed": _price("minimax", "MiniMax-M2.7-highspeed", ".6", "2.4"),
}


@dataclass(frozen=True)
class Lane:
    name: str
    workers: tuple[str, str]
    governor: str
    description: str


LANES: dict[str, Lane] = {
    "economy": Lane("economy", ("openai/gpt-5.4-mini", "xai/grok-4.3"), "minimax/MiniMax-M2.7-highspeed", "Economy worker comparison with private MiniMax HoloGov."),
    "balanced": Lane("balanced", ("openai/gpt-5.4", "xai/grok-4.3"), "minimax/MiniMax-M2.7-highspeed", "Balanced workers with private MiniMax HoloGov."),
    "frontier": Lane("frontier", ("openai/gpt-5.5", "xai/grok-4.3"), "minimax/MiniMax-M2.7-highspeed", "Canonical frontier workers with private MiniMax HoloGov."),
}


CONDITIONS: dict[str, dict[str, object]] = {
    "A": {"name": "baseline", "history": "none", "gov_context": "minimal"},
    "B": {"name": "bounded_history", "history": "bounded", "gov_context": "minimal"},
    "C": {"name": "gov_control", "history": "bounded", "gov_context": "control_packet"},
    "D": {"name": "gov_selective_context", "history": "selective", "gov_context": "control_packet_and_reseed"},
}


def model_key(price: ModelPrice) -> str:
    return f"{price.provider}/{price.model}"


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
    price = PRICE_CATALOG[model]
    return (Decimal(input_tokens) * price.input_per_million + Decimal(output_tokens) * price.output_per_million) / Decimal(1_000_000)


def _call_event(*, run_id: str, lane: Lane, condition: str, turn: int, role: str, model: str, input_tokens: int, output_tokens: int) -> dict[str, object]:
    price = PRICE_CATALOG[model]
    return {
        "event_type": "call_cost",
        "run_id": run_id,
        "lane": lane.name,
        "condition": condition,
        "turn": turn,
        "role": role,
        "provider": price.provider,
        "model": price.model,
        "input_tokens_estimate": input_tokens,
        "output_tokens_estimate": output_tokens,
        "input_price_per_million_usd": str(price.input_per_million),
        "output_price_per_million_usd": str(price.output_per_million),
        "estimated_cost_usd": str(_estimate_cost(model, input_tokens, output_tokens)),
        "pricing": {"source": PRICING_SOURCE, "version": PRICING_VERSION, "unit": PRICE_UNIT, "estimate": True},
        "latency_ms": None,
        "context_tokens": input_tokens,
        "quality": {"score": None, "judge": None, "notes": None},
    }


def _run_id(lane: str, condition: str, rotations: int, scenario: str) -> str:
    stable = json.dumps({"lane": lane, "condition": condition, "rotations": rotations, "scenario": scenario, "schema": SCHEMA_VERSION}, sort_keys=True, separators=(",", ":"))
    return "hc-exp-" + hashlib.sha256(stable.encode("utf-8")).hexdigest()[:16]


def build_manifest(*, lane: str, condition: str, rotations: int = 2, scenario: str = "runtime", input_tokens_per_call: int = 1200, output_tokens_per_call: int = 400) -> dict[str, object]:
    """Return a deterministic estimate-only manifest with alternating workers."""
    if lane not in LANES:
        raise ValueError(f"Unknown lane: {lane}")
    if condition not in CONDITIONS:
        raise ValueError(f"Unknown condition: {condition}")
    if rotations < 1:
        raise ValueError("rotations must be at least 1")
    if min(input_tokens_per_call, output_tokens_per_call) < 0:
        raise ValueError("token estimates cannot be negative")

    selected = LANES[lane]
    run_id = _run_id(lane, condition, rotations, scenario)
    events: list[dict[str, object]] = []
    for turn in range(1, rotations + 1):
        if condition != "A":
            events.append(_call_event(run_id=run_id, lane=selected, condition=condition, turn=turn, role="governor", model=selected.governor, input_tokens=input_tokens_per_call, output_tokens=output_tokens_per_call))
        events.append(_call_event(run_id=run_id, lane=selected, condition=condition, turn=turn, role="worker", model=selected.workers[(turn - 1) % len(selected.workers)], input_tokens=input_tokens_per_call, output_tokens=output_tokens_per_call))
    total_cost = sum((Decimal(str(event["estimated_cost_usd"])) for event in events), Decimal("0"))
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "mode": "dry_run",
        "provider_calls_made": False,
        "scenario": scenario,
        "lane": {"name": selected.name, "workers": list(selected.workers), "governor": selected.governor, "description": selected.description},
        "condition": {"id": condition, **CONDITIONS[condition]},
        "rotation": {
            "worker_count": 2,
            "turns": rotations,
            "strategy": (
                "alternating_workers_no_governor_control"
                if condition == "A"
                else "alternating_workers_fixed_governor"
            ),
        },
        "pricing": {"source": PRICING_SOURCE, "version": PRICING_VERSION, "as_of": str(date(2026, 7, 14)), "estimate": True, "catalog": {key: asdict(value) | {"input_per_million": str(value.input_per_million), "output_per_million": str(value.output_per_million)} for key, value in PRICE_CATALOG.items()}},
        "call_events": events,
        "aggregate": {"call_count": len(events), "estimated_cost_usd": str(total_cost), "latency_ms": None, "context_tokens": sum(int(event["context_tokens"]) for event in events), "quality": {"score": None, "judge": None, "notes": "Unscored dry-run manifest."}},
    }


def write_manifest(manifest: Mapping[str, object], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _lane_environment(manifest: Mapping[str, object], credential_env: Mapping[str, str] | None = None) -> dict[str, str]:
    """Build the only environment passed to a live child process.

    ``credential_env`` is an explicit dependency-injection seam. This module
    never reads ambient process environment; callers choosing live execution
    must supply required credentials themselves and no values are logged.
    """
    lane = manifest.get("lane")
    if not isinstance(lane, Mapping):
        raise ValueError("Manifest is missing its lane configuration.")
    workers = lane.get("workers")
    governor = lane.get("governor")
    if not isinstance(workers, list) or len(workers) != 2 or not isinstance(governor, str):
        raise ValueError("Manifest lane must define two workers and one governor.")
    openai_worker = next((item for item in workers if isinstance(item, str) and item.startswith("openai/")), None)
    xai_worker = next((item for item in workers if isinstance(item, str) and item.startswith("xai/")), None)
    if openai_worker is None or xai_worker is None or not governor.startswith("minimax/"):
        raise ValueError("Live smoke supports only an OpenAI/XAI worker pair and a MiniMax HoloGov.")
    environment = {
        "HOLOCHAT_ALLOW_NONCANONICAL_POLICY": "1",
        "HOLOCHAT_EXPERIMENT_MODE": "1",
        # The production profile stays canonical; the two explicit experiment
        # gates only relax model-ID normalization for this child process.
        "HOLOCHAT_RUNTIME_PROFILE": "holochat_canonical",
        "HOLOCHAT_MODEL_PROVIDERS": "openai,xai",
        "HOLOCHAT_GOV_PROVIDER": "minimax",
        "MINIMAX_GOV_MODEL": governor.removeprefix("minimax/"),
        "HOLOCHAT_SINGLE_GOV_CALL": "1",
        "OPENAI_FAST_MODEL": openai_worker.removeprefix("openai/"),
        "XAI_FAST_MODEL": xai_worker.removeprefix("xai/"),
    }
    if credential_env:
        environment.update({key: value for key, value in credential_env.items() if key in {"OPENAI_API_KEY", "XAI_API_KEY", "MINIMAX_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"}})
    return environment


def _smoke_supports_experiment_mode(script: Path) -> bool:
    try:
        source = script.read_text(encoding="utf-8")
    except OSError:
        return False
    return "--experiment-mode" in source and "HOLOCHAT_EXPERIMENT_MODE" in source


def run_live_smoke(*, manifest: Mapping[str, object], live: bool, confirm_live: bool, smoke_script: Path | None = None, runner: Callable[..., object] = subprocess.run, credential_env: Mapping[str, str] | None = None, max_estimated_cost_usd: float | None = None) -> object:
    """Launch the existing smoke runner only after both explicit live gates.

    This function neither accesses credentials nor captures subprocess output.
    Credentials, when intentionally used, remain entirely the smoke runner's
    responsibility through its existing runtime contract.
    """
    if not (live and confirm_live):
        raise PermissionError("Live execution requires both --live and --confirm-live.")
    script = smoke_script or Path(__file__).resolve().parent / "scripts" / "holochat_live_smoke.py"
    if not script.is_file():
        raise FileNotFoundError(f"Smoke script not found: {script}")
    if not _smoke_supports_experiment_mode(script):
        raise RuntimeError("Smoke script does not support explicit HoloChat experiment mode.")
    scenario = str(manifest["scenario"])
    turns = str((manifest["rotation"] if isinstance(manifest["rotation"], Mapping) else {})["turns"])
    condition = str((manifest["condition"] if isinstance(manifest["condition"], Mapping) else {})["id"])
    command = [sys.executable, str(script), "--experiment-mode", "--respect-env", "--scenario", scenario, "--turns", turns]
    if max_estimated_cost_usd is not None:
        if max_estimated_cost_usd <= 0:
            raise ValueError("max_estimated_cost_usd must be greater than 0")
        command.extend(["--max-estimated-cost-usd", str(max_estimated_cost_usd)])
    if condition == "A":
        command.append("--disable-gov-control")
    elif condition == "B":
        command.append("--legacy-clipped-history")
    elif condition == "C":
        command.append("--disable-selective-context")
    return runner(command, check=True, env=_lane_environment(manifest, credential_env))
