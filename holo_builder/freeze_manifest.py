"""
holo_builder/freeze_manifest.py

Static build-freeze manifest helpers for nested Holo Builder packets.

The manifest is a non-model freeze authorization artifact. It records static
checks and Taylor's explicit approval; it does not define benchmark truth.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from holo_builder import lint


MANIFEST_TYPE = "build_freeze_manifest"

_MODEL_VISIBLE_KEYS = {"action", "context"}
_FORBIDDEN_MODEL_VISIBLE_KEYS = {
    "expected_verdict",
    "hidden_ground_truth",
    "gold_answer",
    "scoring_targets",
}


def compute_payload_hash(packet: dict[str, Any]) -> str:
    """SHA-256 of canonical nested payload.action + payload.context JSON."""
    payload = packet.get("payload", {})
    canonical = {
        "action": payload.get("action", {}),
        "context": payload.get("context", {}),
    }
    canonical_json = json.dumps(canonical, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


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


def payload_visibility_errors(packet: dict[str, Any]) -> list[str]:
    """Return static visibility failures for the nested model-visible payload."""
    errors: list[str] = []
    payload = packet.get("payload")
    if not isinstance(payload, dict):
        return ["Missing payload block"]

    payload_keys = set(payload.keys())
    if payload_keys != _MODEL_VISIBLE_KEYS:
        extra = sorted(payload_keys - _MODEL_VISIBLE_KEYS)
        missing = sorted(_MODEL_VISIBLE_KEYS - payload_keys)
        if extra:
            errors.append(f"payload has non-model-visible keys: {extra}")
        if missing:
            errors.append(f"payload missing required model-visible keys: {missing}")

    for path, key in _walk_keys(payload):
        if key in _FORBIDDEN_MODEL_VISIBLE_KEYS:
            errors.append(f"forbidden model-visible key found at {path}")

    return errors


def payload_visibility_result(packet: dict[str, Any]) -> str:
    return "PASS" if not payload_visibility_errors(packet) else "FAIL"


def _builder_hypothesis(packet: dict[str, Any]) -> str:
    return (
        packet.get("expected_verdict")
        or packet.get("hypothesized_verdict")
        or packet.get("_builder", {}).get("spec_target_verdict")
        or "UNKNOWN"
    )


def build_freeze_manifest(packet: dict[str, Any], packet_path: str | Path) -> dict[str, Any]:
    """
    Build a static, non-approving freeze manifest.

    Taylor approval intentionally defaults to false and must be set explicitly
    before freeze.
    """
    pkg_hash = compute_payload_hash(packet)
    lint_result = lint.check(packet)
    visibility = payload_visibility_result(packet)
    return {
        "manifest_type": MANIFEST_TYPE,
        "scenario_id": packet.get("scenario_id", ""),
        "packet_path": str(packet_path),
        "payload_hash": pkg_hash,
        "hash8": pkg_hash[:8],
        "builder_hypothesis_verdict": _builder_hypothesis(packet),
        "static_lint_result": "PASS" if lint_result.passed else "FAIL",
        "payload_visibility_result": visibility,
        "no_model_visible_expected_verdict": visibility == "PASS",
        "no_live_model_calls": True,
        "taylor_approved_for_freeze": False,
        "approved_by": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _same_path(manifest_path: str, packet_path: Path) -> bool:
    return Path(manifest_path).expanduser().resolve() == packet_path.expanduser().resolve()


def validate_build_freeze_manifest(
    packet: dict[str, Any],
    manifest: dict[str, Any],
    packet_path: str | Path,
) -> str:
    """
    Validate the manifest and return the computed payload hash.

    Raises ValueError with all blocking reasons if the manifest is not a valid
    freeze authorization artifact.
    """
    packet_path = Path(packet_path)
    scenario_id = packet.get("scenario_id", "")
    pkg_hash = compute_payload_hash(packet)
    hash8 = pkg_hash[:8]
    lint_result = lint.check(packet)
    visibility_errors = payload_visibility_errors(packet)

    errors: list[str] = []
    _require(manifest.get("manifest_type") == MANIFEST_TYPE, "manifest_type must be build_freeze_manifest", errors)
    _require(manifest.get("scenario_id") == scenario_id, "manifest scenario_id must match packet scenario_id", errors)
    _require(_same_path(str(manifest.get("packet_path", "")), packet_path), "manifest packet_path must match packet path", errors)
    _require(manifest.get("payload_hash") == pkg_hash, "manifest payload_hash must match computed payload hash", errors)
    _require(manifest.get("hash8", hash8) == hash8, "manifest hash8 must match computed payload hash", errors)
    _require(manifest.get("static_lint_result") == "PASS", "manifest static_lint_result must be PASS", errors)
    _require(manifest.get("payload_visibility_result") == "PASS", "manifest payload_visibility_result must be PASS", errors)
    _require(manifest.get("no_model_visible_expected_verdict") is True, "manifest no_model_visible_expected_verdict must be true", errors)
    _require(manifest.get("no_live_model_calls") is True, "manifest no_live_model_calls must be true", errors)
    _require(manifest.get("taylor_approved_for_freeze") is True, "manifest taylor_approved_for_freeze must be true", errors)
    _require(lint_result.passed, f"static lint must pass before freeze: {lint_result.errors}", errors)
    _require(not visibility_errors, f"payload visibility must pass before freeze: {visibility_errors}", errors)

    if errors:
        raise ValueError("Invalid build_freeze_manifest: " + "; ".join(errors))
    return pkg_hash
