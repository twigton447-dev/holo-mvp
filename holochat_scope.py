"""Portable identity and fixed data-scope policy for hybrid HoloChat.

This module is deliberately storage-agnostic. It gives API and repository code
one typed contract to enforce before enterprise scope switching is enabled.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable, Optional


class ScopeKind(str, Enum):
    PERSONAL = "personal"
    ENTERPRISE = "enterprise"


class DataClassification(str, Enum):
    PERSONAL = "personal"
    ENTERPRISE_INTERNAL = "enterprise_internal"
    ENTERPRISE_RESTRICTED = "enterprise_restricted"
    PUBLIC = "public"


@dataclass(frozen=True)
class AccessContext:
    principal_id: str
    scope_id: str
    scope_kind: ScopeKind
    tenant_id: Optional[str] = None
    workspace_id: Optional[str] = None
    membership_id: Optional[str] = None
    roles: tuple[str, ...] = field(default_factory=tuple)
    authz_version: int = 1
    session_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.principal_id or not self.scope_id:
            raise ValueError("principal_id and scope_id are required")
        if self.scope_kind is ScopeKind.ENTERPRISE:
            if not self.tenant_id or not self.membership_id:
                raise ValueError("enterprise access requires tenant_id and membership_id")
        elif self.tenant_id or self.membership_id:
            raise ValueError("personal access cannot carry enterprise membership authority")
        if self.authz_version < 1:
            raise ValueError("authz_version must be positive")

    def for_session(self, session_id: Optional[str]) -> "AccessContext":
        """Bind immutable request authority to one chat session."""
        normalized = str(session_id or "").strip() or None
        return replace(self, session_id=normalized)

    def operator_metadata(self) -> dict[str, object]:
        """Return private, structured authorization telemetry for operators."""
        return {
            "principal_id": self.principal_id,
            "scope_id": self.scope_id,
            "scope_kind": self.scope_kind.value,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "membership_id": self.membership_id,
            "roles": list(self.roles),
            "authz_version": self.authz_version,
            "session_id": self.session_id,
        }


@dataclass(frozen=True)
class ScopedRecord:
    record_id: str
    scope_id: str
    scope_kind: ScopeKind
    classification: DataClassification
    origin_scope_id: str
    tenant_id: Optional[str] = None


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    requires_confirmation: bool = False
    creates_derivative: bool = False


def can_read_record(access: AccessContext, record: ScopedRecord) -> PolicyDecision:
    """Admit only same-scope records; public data still needs scoped ingestion."""
    if access.scope_id != record.scope_id:
        return PolicyDecision(False, "cross_scope_read_denied")
    if access.scope_kind is not record.scope_kind:
        return PolicyDecision(False, "scope_kind_mismatch")
    if access.scope_kind is ScopeKind.ENTERPRISE and access.tenant_id != record.tenant_id:
        return PolicyDecision(False, "tenant_mismatch")
    return PolicyDecision(True, "same_scope_admitted")


def can_continue_session(access: AccessContext, session_scope_id: str) -> PolicyDecision:
    if not session_scope_id or access.scope_id != session_scope_id:
        return PolicyDecision(False, "session_scope_mismatch")
    return PolicyDecision(True, "session_scope_admitted")


def plan_scope_transfer(
    source: AccessContext,
    destination: AccessContext,
    classifications: Iterable[DataClassification],
    *,
    enterprise_export_approved: bool = False,
) -> PolicyDecision:
    """Return the minimum lawful transfer posture without moving any data."""
    classes = set(classifications)
    if source.scope_id == destination.scope_id:
        return PolicyDecision(True, "same_scope_no_transfer")
    if source.principal_id != destination.principal_id:
        return PolicyDecision(False, "different_principal_transfer_denied")

    if source.scope_kind is ScopeKind.PERSONAL and destination.scope_kind is ScopeKind.ENTERPRISE:
        if DataClassification.ENTERPRISE_RESTRICTED in classes:
            return PolicyDecision(False, "restricted_data_not_valid_in_personal_source")
        return PolicyDecision(
            True,
            "personal_to_enterprise_requires_confirmed_derivative",
            requires_confirmation=True,
            creates_derivative=True,
        )

    if source.scope_kind is ScopeKind.ENTERPRISE and destination.scope_kind is ScopeKind.PERSONAL:
        if not enterprise_export_approved:
            return PolicyDecision(False, "enterprise_to_personal_export_denied")
        if DataClassification.ENTERPRISE_RESTRICTED in classes:
            return PolicyDecision(False, "restricted_enterprise_export_denied")
        return PolicyDecision(
            True,
            "approved_enterprise_export_requires_sanitized_derivative",
            requires_confirmation=True,
            creates_derivative=True,
        )

    return PolicyDecision(False, "cross_tenant_transfer_denied")
