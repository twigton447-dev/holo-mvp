"""Deterministic cross-scope HoloPulse policy and HoloVerify backstop.

HoloPulse is deliberately not a shared HoloBrain or a free-form summary
channel. It can carry only a small allowlisted set of normalized state signals
between a person's Personal and Enterprise spaces. HoloVerify evaluates every
cross-scope proposal before it can be admitted by the receiving side.

This module is storage-agnostic. It does not read or write HoloBrain records;
callers must persist only a decision receipt and an allowed derivative signal.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from typing import Mapping

from holochat_scope import AccessContext, ScopeKind


class PulseDisposition(str, Enum):
    ALLOW = "allow"
    REQUIRE_CONFIRMATION = "require_confirmation"
    BLOCK = "block"


@dataclass(frozen=True)
class PulseSignal:
    """A normalized proposed signal, never raw context or a model summary."""

    signal_type: str
    value: str
    source: AccessContext
    destination: AccessContext
    metadata: Mapping[str, str] | None = None


@dataclass(frozen=True)
class PulseDecision:
    disposition: PulseDisposition
    reason: str
    receipt: Mapping[str, str]

    @property
    def allowed(self) -> bool:
        return self.disposition is PulseDisposition.ALLOW


class HoloVerifyPulseGate:
    """Independent policy backstop for HoloPulse cross-scope proposals.

    The policy is intentionally narrow. Any new signal type or value requires
    an explicit policy change; a worker cannot create a new cross-scope field
    by describing it persuasively.
    """

    _ALLOWED_VALUES = {
        # Personal can expose only an availability outcome, never its reason.
        (ScopeKind.PERSONAL, ScopeKind.ENTERPRISE): {
            "availability": {"available", "limited", "unavailable"},
        },
        # Enterprise can expose only generalized work state to Personal.
        (ScopeKind.ENTERPRISE, ScopeKind.PERSONAL): {
            "workload_pressure": {"low", "moderate", "high"},
            "availability": {"available", "limited", "unavailable"},
        },
    }
    _FORBIDDEN_METADATA_KEYS = {
        "raw_context",
        "summary",
        "source_text",
        "message",
        "name",
        "medical_detail",
        "client_name",
        "deal_name",
        "record_id",
    }

    def evaluate(self, signal: PulseSignal) -> PulseDecision:
        """Return an auditable disposition without exposing the signal value."""
        receipt = self._receipt(signal)
        if signal.source.principal_id != signal.destination.principal_id:
            return PulseDecision(PulseDisposition.BLOCK, "different_principal", receipt)
        if signal.source.scope_id == signal.destination.scope_id:
            return PulseDecision(PulseDisposition.BLOCK, "not_a_cross_scope_signal", receipt)

        allowed_types = self._ALLOWED_VALUES.get(
            (signal.source.scope_kind, signal.destination.scope_kind), {}
        )
        values = allowed_types.get(signal.signal_type)
        if values is None:
            return PulseDecision(PulseDisposition.BLOCK, "signal_type_not_allowlisted", receipt)
        if signal.value not in values:
            return PulseDecision(PulseDisposition.BLOCK, "signal_value_not_normalized", receipt)

        metadata = signal.metadata or {}
        if set(metadata).intersection(self._FORBIDDEN_METADATA_KEYS):
            return PulseDecision(PulseDisposition.BLOCK, "raw_or_sensitive_metadata_denied", receipt)
        if any(not str(key).startswith("policy_") for key in metadata):
            return PulseDecision(PulseDisposition.BLOCK, "metadata_key_not_allowlisted", receipt)

        return PulseDecision(PulseDisposition.ALLOW, "minimized_signal_admitted", receipt)

    @staticmethod
    def _receipt(signal: PulseSignal) -> Mapping[str, str]:
        """Record no value or free text; a hash supports later reconstruction."""
        fingerprint = "|".join(
            (
                signal.source.scope_id,
                signal.destination.scope_id,
                signal.signal_type,
                signal.value,
                ",".join(sorted((signal.metadata or {}).keys())),
            )
        )
        return {
            "source_scope_id": signal.source.scope_id,
            "destination_scope_id": signal.destination.scope_id,
            "signal_type": signal.signal_type,
            "signal_hash": sha256(fingerprint.encode("utf-8")).hexdigest(),
        }
