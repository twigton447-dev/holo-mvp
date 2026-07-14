"""Server-side active-scope resolution for hybrid HoloChat.

The caller may request a scope identifier. Only this resolver can authorize it
from the durable capsule/principal mapping and an active tenant membership.
"""

from __future__ import annotations

from typing import Any, Optional

from holochat_scope import AccessContext, ScopeKind


class ScopeResolutionError(Exception):
    """Raised when a requested data scope is absent or unauthorized."""


class HoloChatScopeStore:
    def __init__(self, client: Any):
        self._client = client

    def _one(self, table: str, columns: str, **filters: Any) -> Optional[dict[str, Any]]:
        query = self._client.table(table).select(columns)
        for key, value in filters.items():
            query = query.eq(key, value)
        rows = query.limit(1).execute().data or []
        return dict(rows[0]) if rows else None

    def resolve(self, capsule_id: str, requested_scope_id: str | None = None) -> AccessContext:
        if not capsule_id:
            raise ScopeResolutionError("authenticated capsule is required")
        mapping = self._one(
            "holo_capsule_principals",
            "principal_id, personal_scope_id",
            capsule_id=capsule_id,
        )
        if not mapping:
            raise ScopeResolutionError("capsule has no principal mapping")

        principal_id = str(mapping.get("principal_id") or "").strip()
        personal_scope_id = str(mapping.get("personal_scope_id") or "").strip()
        if not principal_id or not personal_scope_id:
            raise ScopeResolutionError("capsule principal mapping is invalid")
        scope_id = str(requested_scope_id or personal_scope_id).strip()
        if not scope_id:
            raise ScopeResolutionError("scope is unavailable")
        scope = self._one(
            "holo_scopes",
            "scope_id, scope_kind, owner_principal_id, tenant_id, disabled_at",
            scope_id=scope_id,
        )
        if not scope or scope.get("disabled_at"):
            raise ScopeResolutionError("scope is unavailable")

        if scope.get("scope_kind") == ScopeKind.PERSONAL.value:
            if str(scope.get("owner_principal_id") or "") != principal_id:
                raise ScopeResolutionError("personal scope belongs to another principal")
            return AccessContext(
                principal_id=principal_id,
                scope_id=scope_id,
                scope_kind=ScopeKind.PERSONAL,
                workspace_id=None,
            )

        if scope.get("scope_kind") != ScopeKind.ENTERPRISE.value or not scope.get("tenant_id"):
            raise ScopeResolutionError("scope kind is invalid")
        tenant_id = str(scope["tenant_id"])
        membership = self._one(
            "holo_tenant_memberships",
            "membership_id, roles, authz_version, status",
            tenant_id=tenant_id,
            principal_id=principal_id,
            status="active",
        )
        if not membership:
            raise ScopeResolutionError("active enterprise membership is required")
        membership_id = str(membership.get("membership_id") or "").strip()
        roles = membership.get("roles")
        try:
            authz_version = int(membership.get("authz_version"))
        except (TypeError, ValueError):
            raise ScopeResolutionError("enterprise membership authority is invalid")
        if (
            not membership_id
            or not isinstance(roles, (list, tuple))
            or any(not str(role).strip() for role in roles)
            or authz_version < 1
        ):
            raise ScopeResolutionError("enterprise membership authority is invalid")
        return AccessContext(
            principal_id=principal_id,
            scope_id=scope_id,
            scope_kind=ScopeKind.ENTERPRISE,
            tenant_id=tenant_id,
            workspace_id=None,
            membership_id=membership_id,
            roles=tuple(str(role).strip() for role in roles),
            authz_version=authz_version,
        )
