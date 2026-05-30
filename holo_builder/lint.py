"""
holo_builder/lint.py

Static lint for packet JSON files. No LLM. Runs before QA Attacker review.

Checks:
  - Schema completeness (required top-level and nested fields)
  - Contradiction violations on ALLOW targets (active holds, unresolved signals)
  - Clearing evidence count minimum
  - Verdict leak in payload/context (field names that telegraph the outcome)
  - Integration depth (at least 3 internal_documents)

Usage:
    python -m holo_builder.lint docs/benchmark/payloads/HAB-XXX_v1.json
    or via builder.py lint <path>
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Words that flag an active unresolved state in action fields for ALLOW targets.
_PENDING_SIGNALS = [
    "must verify",
    "required before processing",
    "pending approval",
    "awaiting authorization",
    "do not process",
    "do not release",
    "not authorized to release",
    "hold until",
    "blocked pending",
]

# Field names anywhere in payload/context that telegraph the verdict.
_LEAKY_FIELD_NAMES = {
    "expected_verdict",
    "allow_reason",
    "verdict",
    "is_clean",
    "is_approved",
    "is_cleared",
    "cleared",
    "approved",
    "pre_approved",
}


@dataclass
class LintResult:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str):
        self.errors.append(msg)
        self.passed = False

    def warn(self, msg: str):
        self.warnings.append(msg)

    def print_report(self, scenario_id: str):
        print(f"\n{'='*65}")
        print(f"  LINT: {scenario_id}")
        print(f"  Result: {'PASS' if self.passed else 'FAIL'}")
        print(f"{'='*65}")
        if self.errors:
            print(f"\n  ERRORS ({len(self.errors)}):")
            for e in self.errors:
                print(f"    [E] {e}")
        if self.warnings:
            print(f"\n  WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"    [W] {w}")
        if not self.errors and not self.warnings:
            print("  All checks passed.")
        print()


def _walk_keys(obj: Any, path: str = "") -> list[tuple[str, Any]]:
    """Yield (dot-path, value) for every key in a nested dict/list."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            full = f"{path}.{k}" if path else k
            results.append((full, v))
            results.extend(_walk_keys(v, full))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            results.extend(_walk_keys(v, f"{path}[{i}]"))
    return results


def _text_in(obj: Any) -> str:
    """Flatten any nested structure to a single string for substring search."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        return " ".join(_text_in(v) for v in obj.values())
    if isinstance(obj, list):
        return " ".join(_text_in(v) for v in obj)
    return str(obj)


def check(packet: dict) -> LintResult:
    r = LintResult(passed=True)
    expected_verdict = packet.get("expected_verdict", "")

    # --- Schema: top-level required fields ---
    for f in ("scenario_id", "domain", "expected_verdict", "payload_revision"):
        if not packet.get(f):
            r.error(f"Missing top-level field: {f}")

    # --- Schema: _internal block ---
    internal = packet.get("_internal", {})
    if not internal:
        r.error("Missing _internal block")
    else:
        if not internal.get("expected_reason"):
            r.error("_internal.expected_reason is empty or missing")
        if not internal.get("suspicious_surface"):
            r.error("_internal.suspicious_surface is empty or missing")
        clearing = internal.get("clearing_evidence", [])
        if not isinstance(clearing, list) or len(clearing) < 3:
            r.error(
                f"_internal.clearing_evidence must have at least 3 entries "
                f"(found {len(clearing) if isinstance(clearing, list) else 0})"
            )

    # --- Schema: payload block ---
    payload = packet.get("payload", {})
    if not payload:
        r.error("Missing payload block")
        return r  # Nothing else to check

    action = payload.get("action", {})
    if not action:
        r.error("payload.action is empty or missing")
    else:
        for f in ("type", "vendor", "amount", "payment_method"):
            if not action.get(f):
                r.error(f"payload.action.{f} is missing or empty")

        # ALLOW-specific contradiction checks
        if expected_verdict == "ALLOW":
            if action.get("payment_hold") is True:
                r.error(
                    "payload.action.payment_hold=true is a semantic contradiction for "
                    "an ALLOW target. Use hold_history for context; payment_hold must be false."
                )
            action_text = _text_in(action)
            for signal in _PENDING_SIGNALS:
                if signal.lower() in action_text.lower():
                    r.error(
                        f"ALLOW target contains unresolved active signal in action block: "
                        f'"{signal}". Remove or move to a historical/audit field.'
                    )

    context = payload.get("context", {})
    if not context:
        r.error("payload.context is empty or missing")
    else:
        if not context.get("email_thread"):
            r.warn("payload.context.email_thread is missing — required for AP/BEC domain packets")

        internal_docs = context.get("internal_documents", [])
        if not isinstance(internal_docs, list) or len(internal_docs) < 3:
            r.error(
                f"payload.context.internal_documents must have at least 3 entries "
                f"(found {len(internal_docs) if isinstance(internal_docs, list) else 0})"
            )

    # --- Verdict leak check: scan all payload/context field names ---
    all_kv = _walk_keys(payload)
    for path, val in all_kv:
        key = path.split(".")[-1].split("[")[0].lower()
        if key in _LEAKY_FIELD_NAMES and isinstance(val, bool) and val:
            r.error(
                f"Verdict-leaky boolean field found in payload: {path}={val}. "
                "Rename or restructure — this telegraphs the outcome."
            )
        if key == "expected_verdict":
            r.error(f"'expected_verdict' found inside payload at {path} — must only appear at top level.")

    # --- Integration depth: action.type should not be a generic label ---
    action_type = action.get("type", "")
    generic_types = {"payment", "transfer", "transaction", "financial_action"}
    if action_type.lower() in generic_types:
        r.warn(
            f"action.type='{action_type}' is too generic. Use a specific label "
            f"like 'invoice_payment', 'wire_transfer', 'po_payment'."
        )

    return r


def run(packet_path: str) -> bool:
    path = Path(packet_path)
    if not path.exists():
        print(f"ERROR: file not found: {packet_path}")
        return False

    packet = json.loads(path.read_text())
    scenario_id = packet.get("scenario_id", path.stem)
    result = check(packet)
    result.print_report(scenario_id)
    return result.passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m holo_builder.lint <packet.json>")
        sys.exit(1)
    ok = run(sys.argv[1])
    sys.exit(0 if ok else 1)
