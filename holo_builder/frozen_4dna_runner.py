"""
Dry-run support for frozen HoloBuilder packets using a fixed 4DNA mini roster.

This module does not call providers and does not write benchmark traces. It is
the adapter boundary between nested frozen HoloBuilder packets and future live
benchmark runners.
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from holo_builder.freeze_manifest import compute_payload_hash, payload_visibility_errors


REQUIRED_PAYLOAD_KEYS = {"action", "context"}
FORBIDDEN_MODEL_VISIBLE_KEYS = {"_builder", "_internal", "_frozen", "expected_verdict"}
EXPECTED_MINI_MODELS = {
    "anthropic": "claude-haiku-4-5-20251001",
    "google": "gemini-2.5-flash-lite",
    "minimax": "MiniMax-Text-01",
    "openai": "gpt-4o-mini",
    "xai": "grok-3-mini",
}


@dataclass(frozen=True)
class ModelRef:
    provider: str
    model: str
    label: str | None = None

    def to_dict(self) -> dict[str, str]:
        data = {"provider": self.provider, "model": self.model}
        if self.label:
            data["label"] = self.label
        return data


def load_available_mini_pool(cohort_path: str | Path) -> list[ModelRef]:
    cohort = json.loads(Path(cohort_path).read_text())
    models = cohort.get("models", {})
    labels = cohort.get("condition_labels", {}).get("solo", {})
    if not isinstance(models, dict) or not models:
        raise ValueError("mini cohort must contain non-empty models mapping")
    if models != EXPECTED_MINI_MODELS:
        raise ValueError("mini cohort must match the approved five-mini provider/model set")

    pool: list[ModelRef] = []
    for provider in sorted(models):
        model = models[provider]
        if not isinstance(model, str) or not model.strip():
            raise ValueError(f"mini cohort model for {provider!r} must be non-empty")
        pool.append(ModelRef(provider=provider, model=model, label=labels.get(provider)))
    return pool


def select_4dna_roster(pool: list[ModelRef], seed: int, session_id: str) -> dict[str, Any]:
    if not session_id:
        raise ValueError("session_id is required")
    if len(pool) < 4:
        raise ValueError("4DNA roster requires at least four available models")

    rng = random.Random(seed)
    gov_index = rng.randrange(len(pool))
    holo_gov = pool[gov_index]
    remaining = [model for idx, model in enumerate(pool) if idx != gov_index]
    rng.shuffle(remaining)
    active_non_gov = remaining[:3]
    excluded = remaining[3:]

    if len(active_non_gov) != 3:
        raise ValueError("4DNA roster must contain exactly three active non-Gov models")
    if holo_gov in active_non_gov:
        raise ValueError("HoloGov must not be duplicated as an active non-Gov model")
    if len(pool) == 5 and len(excluded) != 1:
        raise ValueError("pool size five must exclude exactly one non-Gov model")

    return {
        "session_id": session_id,
        "seed": seed,
        "holo_gov": holo_gov.to_dict(),
        "active_non_gov": [model.to_dict() for model in active_non_gov],
        "excluded": [model.to_dict() for model in excluded],
        "full_available_pool": [model.to_dict() for model in pool],
        "active_roster_size": 1 + len(active_non_gov),
        "selection_rule": "seeded_fixed_4dna",
    }


def _walk_keys(obj: Any, prefix: str = "payload") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}"
            found.append((path, key))
            found.extend(_walk_keys(value, path))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            found.extend(_walk_keys(value, f"{prefix}[{idx}]"))
    return found


def _forbidden_payload_key_paths(payload: Any) -> list[str]:
    return [
        path
        for path, key in _walk_keys(payload)
        if key in FORBIDDEN_MODEL_VISIBLE_KEYS
    ]


def load_frozen_packet_for_dry_run(path: str | Path, expected_hash: str) -> dict[str, Any]:
    packet_path = Path(path)
    packet = json.loads(packet_path.read_text())
    computed_hash = compute_payload_hash(packet)
    frozen = packet.get("_frozen", {})
    payload = packet.get("payload")

    if computed_hash != expected_hash:
        raise ValueError(f"{packet_path}: payload hash mismatch")
    if frozen.get("hash") != expected_hash:
        raise ValueError(f"{packet_path}: _frozen hash does not match expected hash")
    if frozen.get("freeze_gate") != "build_freeze_manifest":
        raise ValueError(f"{packet_path}: missing build_freeze_manifest freeze gate")
    if frozen.get("manifest_type") != "build_freeze_manifest":
        raise ValueError(f"{packet_path}: missing build_freeze_manifest manifest type")
    if frozen.get("approved_by") != "Taylor":
        raise ValueError(f"{packet_path}: frozen packet missing Taylor freeze approval")
    if frozen.get("static_lint_result") != "PASS":
        raise ValueError(f"{packet_path}: frozen packet static lint result is not PASS")
    if frozen.get("payload_visibility_result") != "PASS":
        raise ValueError(f"{packet_path}: frozen packet payload visibility result is not PASS")
    if frozen.get("no_model_visible_expected_verdict") is not True:
        raise ValueError(f"{packet_path}: expected verdict visibility guard is not true")
    if frozen.get("no_live_model_calls") is not True:
        raise ValueError(f"{packet_path}: no_live_model_calls guard is not true")

    visibility_errors = payload_visibility_errors(packet)
    if visibility_errors:
        raise ValueError(f"{packet_path}: payload visibility errors: {visibility_errors}")
    if not isinstance(payload, dict) or set(payload.keys()) != REQUIRED_PAYLOAD_KEYS:
        raise ValueError(f"{packet_path}: model-visible payload must contain only action and context")

    forbidden_paths = _forbidden_payload_key_paths(payload)
    if forbidden_paths:
        raise ValueError(f"{packet_path}: forbidden model-visible metadata at {forbidden_paths}")

    model_visible = {
        "action": payload["action"],
        "context": payload["context"],
    }
    return {
        "scenario_id": packet.get("scenario_id", ""),
        "path": str(packet_path),
        "payload_hash": computed_hash,
        "hash8": computed_hash[:8],
        "model_visible_keys": sorted(model_visible.keys()),
        "model_visible": model_visible,
        "frozen_approved_by": frozen.get("approved_by"),
    }


def build_pair_dry_run_report(
    *,
    cohort_path: str | Path,
    seed: int,
    session_id: str,
    allow_packet_path: str | Path,
    allow_expected_hash: str,
    escalate_packet_path: str | Path,
    escalate_expected_hash: str,
) -> dict[str, Any]:
    pool = load_available_mini_pool(cohort_path)
    roster = select_4dna_roster(pool, seed=seed, session_id=session_id)
    allow_packet = load_frozen_packet_for_dry_run(allow_packet_path, allow_expected_hash)
    escalate_packet = load_frozen_packet_for_dry_run(escalate_packet_path, escalate_expected_hash)

    packets = [
        {key: value for key, value in allow_packet.items() if key != "model_visible"},
        {key: value for key, value in escalate_packet.items() if key != "model_visible"},
    ]
    run_ids = [
        f"{session_id}::{packet['scenario_id']}::{packet['hash8']}"
        for packet in packets
    ]

    return {
        "dry_run": True,
        "no_live_calls": True,
        "no_traces_created": True,
        "benchmark_mode": "holo_4dna_mini_pair_dry_run",
        "session_id": session_id,
        "seed": seed,
        "roster": roster,
        "packets": packets,
        "frozen_packet_hashes": {
            packets[0]["scenario_id"]: packets[0]["payload_hash"],
            packets[1]["scenario_id"]: packets[1]["payload_hash"],
        },
        "run_ids": run_ids,
        "output_dirs": [],
        "model_visible_payload_contract": ["action", "context"],
        "hidden_metadata_excluded": sorted(FORBIDDEN_MODEL_VISIBLE_KEYS),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dry-run a fixed 4DNA mini roster over frozen HoloBuilder packets without live calls.",
    )
    parser.add_argument("--cohort", default="ablation_cohort_mini.json")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--allow-packet", required=True)
    parser.add_argument("--allow-hash", required=True)
    parser.add_argument("--escalate-packet", required=True)
    parser.add_argument("--escalate-hash", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = build_pair_dry_run_report(
        cohort_path=args.cohort,
        seed=args.seed,
        session_id=args.session_id,
        allow_packet_path=args.allow_packet,
        allow_expected_hash=args.allow_hash,
        escalate_packet_path=args.escalate_packet,
        escalate_expected_hash=args.escalate_hash,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
