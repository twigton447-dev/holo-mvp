import pytest

from holochat_scope import (
    AccessContext,
    DataClassification,
    ScopeKind,
    ScopedRecord,
    can_continue_session,
    can_read_record,
    plan_scope_transfer,
)


def _personal(principal="p1", scope="personal-p1"):
    return AccessContext(principal, scope, ScopeKind.PERSONAL)


def _enterprise(principal="p1", scope="tenant-a", tenant="a"):
    return AccessContext(
        principal,
        scope,
        ScopeKind.ENTERPRISE,
        tenant_id=tenant,
        membership_id=f"membership-{tenant}",
        roles=("member",),
    )


def test_enterprise_access_requires_server_resolved_membership():
    with pytest.raises(ValueError):
        AccessContext("p1", "tenant-a", ScopeKind.ENTERPRISE, tenant_id="a")


def test_session_binding_preserves_private_authorization_context():
    access = AccessContext(
        "p1", "work-a", ScopeKind.ENTERPRISE,
        tenant_id="tenant-a", workspace_id=None, membership_id="membership-a",
        roles=("member", "researcher"), authz_version=4,
    ).for_session("session-a")

    assert access.session_id == "session-a"
    assert access.workspace_id is None
    assert access.operator_metadata() == {
        "principal_id": "p1",
        "scope_id": "work-a",
        "scope_kind": "enterprise",
        "tenant_id": "tenant-a",
        "workspace_id": None,
        "membership_id": "membership-a",
        "roles": ["member", "researcher"],
        "authz_version": 4,
        "session_id": "session-a",
    }


def test_records_and_sessions_are_immutable_to_one_scope():
    access = _personal()
    own = ScopedRecord(
        "r1", access.scope_id, ScopeKind.PERSONAL,
        DataClassification.PERSONAL, access.scope_id,
    )
    work = ScopedRecord(
        "r2", "tenant-a", ScopeKind.ENTERPRISE,
        DataClassification.ENTERPRISE_INTERNAL, "tenant-a", tenant_id="a",
    )

    assert can_read_record(access, own).allowed is True
    assert can_read_record(access, work).reason == "cross_scope_read_denied"
    assert can_continue_session(access, "tenant-a").allowed is False


def test_personal_to_enterprise_requires_confirmed_derivative():
    decision = plan_scope_transfer(
        _personal(), _enterprise(), [DataClassification.PERSONAL]
    )
    assert decision.allowed is True
    assert decision.requires_confirmation is True
    assert decision.creates_derivative is True


def test_enterprise_to_personal_is_denied_without_export_policy():
    denied = plan_scope_transfer(
        _enterprise(), _personal(), [DataClassification.ENTERPRISE_INTERNAL]
    )
    assert denied.allowed is False
    assert denied.reason == "enterprise_to_personal_export_denied"

    restricted = plan_scope_transfer(
        _enterprise(),
        _personal(),
        [DataClassification.ENTERPRISE_RESTRICTED],
        enterprise_export_approved=True,
    )
    assert restricted.allowed is False
    assert restricted.reason == "restricted_enterprise_export_denied"


def test_cross_tenant_and_cross_principal_transfers_are_denied():
    different_principal = plan_scope_transfer(
        _enterprise("p1", "tenant-a", "a"),
        _enterprise("p2", "tenant-b", "b"),
        [DataClassification.ENTERPRISE_INTERNAL],
    )
    assert different_principal.reason == "different_principal_transfer_denied"

    cross_tenant = plan_scope_transfer(
        _enterprise("p1", "tenant-a", "a"),
        _enterprise("p1", "tenant-b", "b"),
        [DataClassification.ENTERPRISE_INTERNAL],
    )
    assert cross_tenant.reason == "cross_tenant_transfer_denied"
