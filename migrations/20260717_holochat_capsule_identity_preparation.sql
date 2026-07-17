-- Prepare a fail-closed, transactional reconciliation of a legacy duplicate
-- HoloChat identity. This migration is deliberately applied during a brief
-- authentication maintenance window. It moves a duplicate's owned records
-- only when every collision check passes; otherwise it aborts without changing
-- either capsule.

create extension if not exists pgcrypto;

alter table holo_capsules
    add column if not exists identity_status text not null default 'active';

-- Capsule identity is keyed by an exact, normalized mailbox. Keeping the
-- canonical value in a stored column avoids SQL pattern matching and lets the
-- database, rather than a browser or model, enforce the identity boundary.
alter table holo_capsules
    add column if not exists normalized_email text;

update holo_capsules
set email = lower(btrim(email)),
    normalized_email = lower(btrim(email));

do $$
begin
    if exists (
        select 1
        from holo_capsules
        where coalesce(normalized_email, '') = ''
    ) then
        raise exception 'identity preparation blocked: every capsule must have a normalized email';
    end if;
end;
$$;

alter table holo_capsules
    alter column normalized_email set not null;

create or replace function holo_normalize_capsule_email()
returns trigger
language plpgsql
set search_path = public
as $$
begin
    new.email := lower(btrim(new.email));
    new.normalized_email := new.email;
    return new;
end;
$$;

drop trigger if exists normalize_holo_capsule_email on holo_capsules;
create trigger normalize_holo_capsule_email
before insert or update of email on holo_capsules
for each row execute function holo_normalize_capsule_email();

alter table holo_capsules
    add column if not exists merged_into_capsule_id text references holo_capsules(capsule_id) on delete restrict;

alter table holo_capsules
    add column if not exists merged_at timestamptz;

alter table holo_capsules
    drop constraint if exists holo_capsules_identity_status_check;

alter table holo_capsules
    add constraint holo_capsules_identity_status_check
    check (identity_status in ('active', 'merged', 'disabled')) not valid;

alter table holo_capsules
    validate constraint holo_capsules_identity_status_check;

-- The application reads this row before authenticating a capsule or accepting
-- a new sign-in. Existing browser tokens are therefore rejected while an
-- identity move is running, preventing a third duplicate or a concurrent
-- write from racing the reconciliation transaction.
create table if not exists holo_identity_maintenance (
    singleton boolean primary key default true check (singleton),
    enabled boolean not null,
    reason text not null,
    changed_at timestamptz not null default now()
);

insert into holo_identity_maintenance (singleton, enabled, reason)
values (true, false, 'identity integrity controls installed; normal operation')
on conflict (singleton) do nothing;

-- Every protected write takes a shared advisory lock. Entering maintenance
-- takes the exclusive form of the same lock, waiting for in-flight writes to
-- finish before it rejects new writes. This is a database fence, not merely a
-- browser/session convention.
create or replace function holo_identity_maintenance_write_guard()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
    v_enabled boolean;
begin
    perform pg_advisory_xact_lock_shared(781104, 1);

    if current_setting('holo.identity_reconciliation', true) = 'on' then
        if tg_op = 'DELETE' then
            return old;
        end if;
        return new;
    end if;

    select enabled into v_enabled
    from holo_identity_maintenance
    where singleton = true;
    if not found then
        raise exception 'identity maintenance control is unavailable'
            using errcode = '55000';
    end if;
    if v_enabled then
        raise exception 'identity maintenance is active; protected writes are temporarily unavailable'
            using errcode = '55000';
    end if;
    if tg_op = 'DELETE' then
        return old;
    end if;
    return new;
end;
$$;

do $$
declare
    table_name text;
begin
    foreach table_name in array array[
        'holo_capsules', 'holo_chat_sessions', 'holo_chat_messages',
        'holo_capsule_context', 'holo_life_context',
        'holo_session_consolidations', 'holo_artifacts',
        'holo_integrations', 'holo_signals', 'holo_transcripts',
        'api_keys', 'subscriptions'
    ] loop
        if to_regclass('public.' || table_name) is not null then
            execute format('drop trigger if exists identity_maintenance_write_guard on public.%I', table_name);
            execute format(
                'create trigger identity_maintenance_write_guard '
                || 'before insert or update or delete on public.%I '
                || 'for each row execute function holo_identity_maintenance_write_guard()',
                table_name
            );
        end if;
    end loop;
end;
$$;

create table if not exists holo_capsule_identity_reconciliations (
    reconciliation_id uuid primary key default gen_random_uuid(),
    source_capsule_id text not null references holo_capsules(capsule_id) on delete restrict,
    target_capsule_id text not null references holo_capsules(capsule_id) on delete restrict,
    normalized_email_hash text not null,
    source_google_id_hash text not null,
    target_prior_google_id_hash text not null,
    transferred_record_counts jsonb not null default '{}'::jsonb,
    collision_counts jsonb not null default '{}'::jsonb,
    reason text not null,
    completed_at timestamptz not null default now(),
    check (source_capsule_id <> target_capsule_id)
);

create or replace function holo_preflight_capsule_identity_reconciliation(
    p_source_capsule_id text,
    p_target_capsule_id text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    source_row holo_capsules%rowtype;
    target_row holo_capsules%rowtype;
    active_duplicate_count integer;
    v_context_collisions bigint := 0;
    v_life_collisions bigint := 0;
    v_integration_collisions bigint := 0;
    v_chat_sessions bigint := 0;
    v_capsule_context bigint := 0;
    v_life_context bigint := 0;
    v_session_consolidations bigint := 0;
    v_artifacts bigint := 0;
    v_integrations bigint := 0;
    v_signals bigint := 0;
    v_transcripts bigint := 0;
    v_active_api_keys bigint := 0;
    v_source_subscriptions bigint := 0;
    v_record_counts jsonb;
    v_collision_counts jsonb;
begin
    if coalesce(trim(p_source_capsule_id), '') = ''
       or coalesce(trim(p_target_capsule_id), '') = ''
       or p_source_capsule_id = p_target_capsule_id then
        raise exception 'source and target capsule ids must be different and non-empty';
    end if;

    select * into source_row
    from holo_capsules
    where capsule_id = p_source_capsule_id
    for update;
    if not found then
        raise exception 'source capsule was not found';
    end if;

    select * into target_row
    from holo_capsules
    where capsule_id = p_target_capsule_id
    for update;
    if not found then
        raise exception 'target capsule was not found';
    end if;

    if source_row.identity_status <> 'active' or target_row.identity_status <> 'active' then
        raise exception 'both source and target capsules must be active';
    end if;
    if source_row.normalized_email <> target_row.normalized_email then
        raise exception 'capsules do not belong to the same normalized email';
    end if;
    if coalesce(source_row.google_id, '') = '' or source_row.google_id like 'email:%' then
        raise exception 'source must carry a verified Google subject';
    end if;
    -- The target must be the original email/password HoloBrain, never another
    -- verified Google identity. This makes an operator selection mistake
    -- fail closed instead of orphaning a different person's sign-in.
    if coalesce(target_row.google_id, '') not like 'email:%' then
        raise exception 'target must be a legacy email-only capsule';
    end if;

    select count(*) into active_duplicate_count
    from holo_capsules
    where normalized_email = source_row.normalized_email
      and identity_status = 'active';
    if active_duplicate_count <> 2 then
        raise exception 'reconciliation requires exactly two active capsules for this normalized email';
    end if;

    if to_regclass('public.holo_capsule_principals') is not null then
        if exists (
            select 1
            from holo_capsule_principals
            where capsule_id in (source_row.capsule_id, target_row.capsule_id)
        ) then
            raise exception 'identity reconciliation must complete before the scoped-brain migration';
        end if;
    end if;

    select count(*) into v_context_collisions
    from holo_capsule_context source_record
    join holo_capsule_context target_record
      on target_record.capsule_id = target_row.capsule_id
     and target_record.key = source_record.key
    where source_record.capsule_id = source_row.capsule_id;

    select count(*) into v_life_collisions
    from holo_life_context source_record
    join holo_life_context target_record
      on target_record.capsule_id = target_row.capsule_id
     and target_record.key = source_record.key
    where source_record.capsule_id = source_row.capsule_id;

    if to_regclass('public.holo_integrations') is not null then
        execute '
            select count(*)
            from public.holo_integrations source_record
            join public.holo_integrations target_record
              on target_record.capsule_id = $2
             and target_record.source = source_record.source
            where source_record.capsule_id = $1
        ' into v_integration_collisions using source_row.capsule_id, target_row.capsule_id;
    end if;

    select count(*) into v_chat_sessions
    from holo_chat_sessions where capsule_id = source_row.capsule_id;
    select count(*) into v_capsule_context
    from holo_capsule_context where capsule_id = source_row.capsule_id;
    select count(*) into v_life_context
    from holo_life_context where capsule_id = source_row.capsule_id;
    select count(*) into v_session_consolidations
    from holo_session_consolidations where capsule_id = source_row.capsule_id;
    select count(*) into v_artifacts
    from holo_artifacts where capsule_id = source_row.capsule_id;

    if to_regclass('public.holo_integrations') is not null then
        execute 'select count(*) from public.holo_integrations where capsule_id = $1'
            into v_integrations using source_row.capsule_id;
    end if;
    if to_regclass('public.holo_signals') is not null then
        execute 'select count(*) from public.holo_signals where capsule_id = $1'
            into v_signals using source_row.capsule_id;
    end if;
    if to_regclass('public.holo_transcripts') is not null then
        execute 'select count(*) from public.holo_transcripts where capsule_id = $1'
            into v_transcripts using source_row.capsule_id;
    end if;
    if to_regclass('public.api_keys') is not null then
        execute 'select count(*) from public.api_keys where capsule_id = $1 and coalesce(is_active, false)'
            into v_active_api_keys using source_row.capsule_id;
    end if;
    if to_regclass('public.subscriptions') is not null then
        execute 'select count(*) from public.subscriptions where capsule_id = $1'
            into v_source_subscriptions using source_row.capsule_id;
    end if;

    v_record_counts := jsonb_build_object(
        'chat_sessions', v_chat_sessions,
        'capsule_context', v_capsule_context,
        'life_context', v_life_context,
        'session_consolidations', v_session_consolidations,
        'artifacts', v_artifacts,
        'integrations', v_integrations,
        'signals', v_signals,
        'transcripts', v_transcripts,
        'active_api_keys_to_revoke', v_active_api_keys
    );
    v_collision_counts := jsonb_build_object(
        'capsule_context_keys', v_context_collisions,
        'life_context_keys', v_life_collisions,
        'integration_sources', v_integration_collisions,
        'source_subscriptions', v_source_subscriptions
    );

    return jsonb_build_object(
        'eligible', v_context_collisions = 0
            and v_life_collisions = 0
            and v_integration_collisions = 0
            -- A subscription can have usage and payment-provider state. Never
            -- silently transfer or discard it during identity repair.
            and v_source_subscriptions = 0,
        'source_capsule_id', source_row.capsule_id,
        'target_capsule_id', target_row.capsule_id,
        'record_counts', v_record_counts,
        'collision_counts', v_collision_counts
    );
end;
$$;

create or replace function holo_reconcile_capsule_identity(
    p_source_capsule_id text,
    p_target_capsule_id text,
    p_reason text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    source_row holo_capsules%rowtype;
    target_row holo_capsules%rowtype;
    v_maintenance_enabled boolean;
    v_preflight jsonb;
    v_record_counts jsonb;
    v_collision_counts jsonb;
begin
    if coalesce(trim(p_reason), '') = '' then
        raise exception 'an operator reconciliation reason is required';
    end if;

    perform pg_advisory_xact_lock(781104, 1);

    select enabled into v_maintenance_enabled
    from holo_identity_maintenance
    where singleton = true
    for update;
    if not coalesce(v_maintenance_enabled, false) then
        raise exception 'identity reconciliation requires an active authentication maintenance window';
    end if;
    perform set_config('holo.identity_reconciliation', 'on', true);

    -- Preflight obtains row locks and returns only counts. It never exposes
    -- message, memory, artifact, or integration content to the operator.
    v_preflight := holo_preflight_capsule_identity_reconciliation(
        p_source_capsule_id,
        p_target_capsule_id
    );
    if coalesce((v_preflight ->> 'eligible')::boolean, false) is not true then
        raise exception 'identity reconciliation blocked by source/target record collisions';
    end if;
    v_record_counts := v_preflight -> 'record_counts';
    v_collision_counts := v_preflight -> 'collision_counts';

    select * into source_row from holo_capsules where capsule_id = p_source_capsule_id for update;
    select * into target_row from holo_capsules where capsule_id = p_target_capsule_id for update;

    -- Transfer every supported record atomically after collision checks. If a
    -- constraint or unexpected schema issue occurs, PostgreSQL rolls all of
    -- these updates back and neither identity is archived.
    update holo_chat_sessions
    set capsule_id = target_row.capsule_id
    where capsule_id = source_row.capsule_id;
    update holo_capsule_context
    set capsule_id = target_row.capsule_id
    where capsule_id = source_row.capsule_id;
    update holo_life_context
    set capsule_id = target_row.capsule_id
    where capsule_id = source_row.capsule_id;
    update holo_session_consolidations
    set capsule_id = target_row.capsule_id
    where capsule_id = source_row.capsule_id;
    update holo_artifacts
    set capsule_id = target_row.capsule_id
    where capsule_id = source_row.capsule_id;

    if to_regclass('public.holo_integrations') is not null then
        execute format('update %s set capsule_id = $1 where capsule_id = $2', to_regclass('public.holo_integrations'))
            using target_row.capsule_id, source_row.capsule_id;
    end if;
    if to_regclass('public.holo_signals') is not null then
        execute format('update %s set capsule_id = $1 where capsule_id = $2', to_regclass('public.holo_signals'))
            using target_row.capsule_id, source_row.capsule_id;
    end if;
    if to_regclass('public.holo_transcripts') is not null then
        execute format('update %s set capsule_id = $1 where capsule_id = $2', to_regclass('public.holo_transcripts'))
            using target_row.capsule_id, source_row.capsule_id;
    end if;

    -- Account-bound API keys are intentionally not transferred. Requiring a
    -- fresh key issuance prevents an old source credential from becoming an
    -- unnoticed credential for the canonical HoloBrain.
    if to_regclass('public.api_keys') is not null then
        execute 'update public.api_keys set is_active = false where capsule_id = $1 and coalesce(is_active, false)'
            using source_row.capsule_id;
    end if;

    -- Free the verified subject before assigning it to the legacy HoloBrain.
    update holo_capsules
    set identity_status = 'merged',
        merged_into_capsule_id = target_row.capsule_id,
        merged_at = now(),
        google_id = 'merged:' || source_row.capsule_id
    where capsule_id = source_row.capsule_id;

    update holo_capsules
    set google_id = source_row.google_id,
        identity_status = 'active',
        merged_into_capsule_id = null,
        merged_at = null,
        last_active = now()
    where capsule_id = target_row.capsule_id;

    insert into holo_capsule_identity_reconciliations (
        source_capsule_id,
        target_capsule_id,
        normalized_email_hash,
        source_google_id_hash,
        target_prior_google_id_hash,
        transferred_record_counts,
        collision_counts,
        reason
    ) values (
        source_row.capsule_id,
        target_row.capsule_id,
        encode(digest(source_row.normalized_email, 'sha256'), 'hex'),
        encode(digest(source_row.google_id, 'sha256'), 'hex'),
        encode(digest(target_row.google_id, 'sha256'), 'hex'),
        v_record_counts,
        v_collision_counts,
        p_reason
    );

    return jsonb_build_object(
        'source_capsule_id', source_row.capsule_id,
        'target_capsule_id', target_row.capsule_id,
        'transferred_record_counts', v_record_counts,
        'collision_counts', v_collision_counts,
        'outcome', 'source_archived_and_records_transferred'
    );
end;
$$;

create or replace function holo_set_identity_maintenance(
    p_enabled boolean,
    p_reason text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
begin
    if coalesce(trim(p_reason), '') = '' then
        raise exception 'an identity-maintenance reason is required';
    end if;
    perform pg_advisory_xact_lock(781104, 1);
    update holo_identity_maintenance
    set enabled = p_enabled,
        reason = p_reason,
        changed_at = now()
    where singleton = true;
    if not found then
        raise exception 'identity maintenance control is unavailable';
    end if;
    return jsonb_build_object('enabled', p_enabled, 'reason', p_reason);
end;
$$;

create or replace function holo_finalize_capsule_identity_integrity(
    p_reason text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    v_maintenance_enabled boolean;
begin
    if coalesce(trim(p_reason), '') = '' then
        raise exception 'an identity-integrity finalization reason is required';
    end if;
    perform pg_advisory_xact_lock(781104, 1);
    select enabled into v_maintenance_enabled
    from holo_identity_maintenance
    where singleton = true
    for update;
    if not coalesce(v_maintenance_enabled, false) then
        raise exception 'identity integrity finalization requires an active authentication maintenance window';
    end if;
    if exists (
        select normalized_email
        from holo_capsules
        where identity_status = 'active'
        group by normalized_email
        having count(*) > 1
    ) then
        raise exception 'identity integrity finalization blocked by duplicate active capsule emails';
    end if;

    create unique index if not exists holo_capsules_active_normalized_email_unique
        on holo_capsules (normalized_email)
        where identity_status = 'active';
    create unique index if not exists holo_capsules_active_google_id_unique
        on holo_capsules (google_id)
        where identity_status = 'active' and coalesce(google_id, '') <> '';

    return jsonb_build_object('outcome', 'active_identity_indexes_verified');
end;
$$;

alter table holo_identity_maintenance enable row level security;
alter table holo_capsule_identity_reconciliations enable row level security;
revoke all on holo_identity_maintenance, holo_capsule_identity_reconciliations from anon, authenticated;
revoke all on function holo_preflight_capsule_identity_reconciliation(text, text) from public, anon, authenticated;
revoke all on function holo_reconcile_capsule_identity(text, text, text) from public, anon, authenticated;
revoke all on function holo_set_identity_maintenance(boolean, text) from public, anon, authenticated;
revoke all on function holo_finalize_capsule_identity_integrity(text) from public, anon, authenticated;
grant execute on function holo_preflight_capsule_identity_reconciliation(text, text) to service_role;
grant execute on function holo_reconcile_capsule_identity(text, text, text) to service_role;
grant execute on function holo_set_identity_maintenance(boolean, text) to service_role;
grant execute on function holo_finalize_capsule_identity_integrity(text) to service_role;
