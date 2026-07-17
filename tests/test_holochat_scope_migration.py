from pathlib import Path


MIGRATION = Path("migrations/20260714_holochat_hybrid_scopes.sql")
PERSONAL_PROVISIONING_MIGRATION = Path(
    "migrations/20260717_holochat_personal_space_provisioning.sql"
)


def test_hybrid_scope_migration_defines_identity_membership_and_transfer_ledger():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    for table in (
        "holo_principals",
        "holo_tenants",
        "holo_scopes",
        "holo_tenant_memberships",
        "holo_capsule_principals",
        "holo_scope_transfers",
    ):
        assert f"create table if not exists {table}" in sql
    assert "personal_to_enterprise" not in sql
    assert "source_scope_id <> destination_scope_id" in sql
    assert "approved_by_membership_id" in sql
    assert "create trigger validate_scope_transfer" in sql
    assert "transfer principal is not authorized for source scope" in sql
    assert "approved transfer requires an active destination owner or admin" in sql


def test_memory_checkpoint_schema_is_atomic_scoped_and_dependency_ordered():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    for table in (
        "holo_memory_checkpoints",
        "holo_memory_entries",
        "holo_memory_revocations",
    ):
        assert f"create table if not exists {table}" in sql
        assert f"alter table {table} enable row level security" in sql
    assert sql.index("create unique index if not exists holo_chat_sessions_id_scope") < sql.index(
        "create table if not exists holo_memory_checkpoints"
    )
    assert "create or replace function holo_commit_memory_checkpoint" in sql
    assert "memory checkpoint session scope mismatch" in sql
    assert "memory checkpoint capsule is not authorized for scope" in sql
    assert "idempotency_key = v_idempotency_key" in sql
    assert "pg_advisory_xact_lock" in sql
    assert "v_disposition = 'quarantine'" in sql
    assert "grant execute on function holo_commit_memory_checkpoint" in sql


def test_all_chat_and_holobrain_surfaces_gain_immutable_non_null_scope():
    sql = MIGRATION.read_text(encoding="utf-8").lower()
    scoped_tables = (
        "holo_chat_sessions",
        "holo_chat_messages",
        "holo_capsule_context",
        "holo_life_context",
        "holo_session_consolidations",
        "holo_artifacts",
        "holo_integrations",
        "holo_signals",
        "holo_transcripts",
    )

    for table in scoped_tables:
        assert f"alter table {table} add column if not exists scope_id" in sql
        assert f"alter table %i alter column scope_id set not null" in sql
    assert "create or replace function holo_reject_scope_reassignment" in sql
    assert "create trigger reject_scope_reassignment" in sql
    assert "create trigger enforce_session_scope" in sql
    assert "child record scope does not match chat session scope" in sql
    assert "create trigger validate_capsule_principal_scope" in sql
    assert "create an audited derivative transfer" in sql


def test_migration_fails_closed_on_legacy_orphans_and_denies_direct_clients():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "scope migration blocked" in sql
    assert "enable row level security" in sql
    assert "from anon, authenticated" in sql
    assert "service-role backend must" in sql


def test_new_capsules_receive_personal_space_without_enterprise_access():
    sql = PERSONAL_PROVISIONING_MIGRATION.read_text(encoding="utf-8").lower()

    assert "create or replace function holo_provision_personal_scope_for_capsule" in sql
    assert "after insert on holo_capsules" in sql
    assert "create trigger provision_personal_scope_for_capsule" in sql
    assert "insert into holo_principals" in sql
    assert "insert into holo_scopes" in sql
    assert "'personal'" in sql
    assert "insert into holo_capsule_principals" in sql
    assert "enterprise scopes are intentionally not created here" in sql
    assert "holo_tenant_memberships" not in sql
