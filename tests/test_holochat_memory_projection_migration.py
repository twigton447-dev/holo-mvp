"""No-provider contract tests for durable Memory Steward projections."""

from pathlib import Path


MIGRATION = Path("migrations/20260714_holochat_hybrid_scopes.sql")


def migration_sql() -> str:
    return MIGRATION.read_text(encoding="utf-8").lower()


def commit_function(sql: str) -> str:
    start = sql.index("create or replace function holo_commit_memory_checkpoint")
    end = sql.index("revoke all on function holo_commit_memory_checkpoint", start)
    return sql[start:end]


def test_checkpoint_delta_is_projected_to_one_scoped_durable_episode():
    sql = migration_sql()
    function = commit_function(sql)

    assert "create table if not exists holo_memory_episodes" in sql
    assert "primary key (scope_id, episode_id)" in sql
    assert "unique (scope_id, checkpoint_id)" in sql
    assert "foreign key (scope_id, checkpoint_id)" in sql
    assert "references holo_memory_checkpoints(scope_id, checkpoint_id)" in sql
    assert "insert into holo_memory_episodes" in function
    assert "p_checkpoint->'delta'" in function
    assert function.index("insert into holo_memory_episodes") < function.index("for v_proposal in")


def test_portrait_candidates_preserve_admission_lifecycle_semantics():
    function = commit_function(migration_sql())

    assert "v_disposition = 'quarantine'" in function
    assert "v_disposition is distinct from 'admit'" in function
    assert "v_kind = 'supersession'" in function
    assert "status = 'superseded', superseded_by = v_memory_id" in function
    assert "v_kind = 'revocation'" in function
    assert "status = 'revoked'" in function
    assert "delete from holo_memory_entries" not in function
    assert "insert into holo_memory_revocations" in function


def test_checkpoint_idempotency_and_candidate_mutations_are_scope_bound():
    sql = migration_sql()
    function = commit_function(sql)

    assert "primary key (scope_id, checkpoint_id)" in sql
    assert "unique (scope_id, idempotency_key)" in sql
    assert "p_scope_id::text || ':' || v_idempotency_key" in function
    assert "where scope_id = p_scope_id and idempotency_key = v_idempotency_key" in function
    assert "on conflict (scope_id, memory_id)" in function
    assert "where scope_id = p_scope_id and memory_id = v_target" in function
    assert "on conflict (scope_id, target_memory_id)" in function


def test_checkpoint_guards_execute_in_commit_rpc_not_scope_trigger():
    sql = migration_sql()
    function = commit_function(sql)
    trigger_start = sql.index("create or replace function holo_validate_capsule_principal_scope")
    trigger_end = sql.index("drop trigger if exists validate_capsule_principal_scope", trigger_start)
    trigger = sql[trigger_start:trigger_end]

    assert "memory checkpoint identity is required" in function
    assert "pg_advisory_xact_lock" in function
    assert "v_checkpoint_id" not in trigger
    assert "v_idempotency_key" not in trigger
