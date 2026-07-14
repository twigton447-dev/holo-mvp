-- HoloChat portable identity / fixed data-scope migration.
-- Rerunnable. Apply through the normal reviewed Supabase migration path.
-- This file does not grant direct client access; the backend remains the
-- authorization enforcement point and RLS is defense in depth.

create extension if not exists pgcrypto;

create table if not exists holo_principals (
    principal_id uuid primary key default gen_random_uuid(),
    auth_subject text not null unique,
    created_at timestamptz not null default now(),
    disabled_at timestamptz
);

create table if not exists holo_tenants (
    tenant_id uuid primary key default gen_random_uuid(),
    slug text not null unique,
    display_name text not null,
    created_at timestamptz not null default now(),
    disabled_at timestamptz
);

create table if not exists holo_scopes (
    scope_id uuid primary key default gen_random_uuid(),
    scope_kind text not null check (scope_kind in ('personal', 'enterprise')),
    owner_principal_id uuid references holo_principals(principal_id) on delete cascade,
    tenant_id uuid references holo_tenants(tenant_id) on delete cascade,
    display_name text,
    created_at timestamptz not null default now(),
    disabled_at timestamptz,
    check (
        (scope_kind = 'personal' and owner_principal_id is not null and tenant_id is null)
        or
        (scope_kind = 'enterprise' and owner_principal_id is null and tenant_id is not null)
    )
);

create unique index if not exists holo_one_personal_scope_per_principal
    on holo_scopes(owner_principal_id) where scope_kind = 'personal';
create unique index if not exists holo_one_enterprise_scope_per_tenant
    on holo_scopes(tenant_id) where scope_kind = 'enterprise';

create table if not exists holo_tenant_memberships (
    membership_id uuid primary key default gen_random_uuid(),
    tenant_id uuid not null references holo_tenants(tenant_id) on delete cascade,
    principal_id uuid not null references holo_principals(principal_id) on delete cascade,
    roles text[] not null default array['member']::text[],
    status text not null default 'active' check (status in ('invited', 'active', 'suspended', 'revoked')),
    authz_version integer not null default 1,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (tenant_id, principal_id)
);

create table if not exists holo_capsule_principals (
    capsule_id text primary key references holo_capsules(capsule_id) on delete cascade,
    principal_id uuid not null unique references holo_principals(principal_id) on delete cascade,
    personal_scope_id uuid not null unique references holo_scopes(scope_id) on delete cascade,
    created_at timestamptz not null default now()
);

create table if not exists holo_scope_transfers (
    transfer_id uuid primary key default gen_random_uuid(),
    principal_id uuid not null references holo_principals(principal_id),
    source_scope_id uuid not null references holo_scopes(scope_id),
    destination_scope_id uuid not null references holo_scopes(scope_id),
    source_record_type text not null,
    source_record_ids uuid[] not null default '{}',
    derivative_record_ids uuid[] not null default '{}',
    classifications text[] not null default '{}',
    decision text not null check (decision in ('approved', 'denied')),
    reason text not null,
    confirmed_at timestamptz,
    approved_by_membership_id uuid references holo_tenant_memberships(membership_id),
    created_at timestamptz not null default now(),
    check (source_scope_id <> destination_scope_id),
    check ((decision = 'approved' and confirmed_at is not null) or decision = 'denied')
);

-- Backfill every existing capsule into one stable principal and personal scope.
insert into holo_principals (auth_subject)
select 'capsule:' || capsule_id
from holo_capsules
on conflict (auth_subject) do nothing;

insert into holo_scopes (scope_kind, owner_principal_id, display_name)
select 'personal', p.principal_id, 'Personal'
from holo_capsules c
join holo_principals p on p.auth_subject = 'capsule:' || c.capsule_id
on conflict (owner_principal_id) where scope_kind = 'personal' do nothing;

insert into holo_capsule_principals (capsule_id, principal_id, personal_scope_id)
select c.capsule_id, p.principal_id, s.scope_id
from holo_capsules c
join holo_principals p on p.auth_subject = 'capsule:' || c.capsule_id
join holo_scopes s on s.owner_principal_id = p.principal_id and s.scope_kind = 'personal'
on conflict (capsule_id) do nothing;

-- All durable HoloBrain/chat records gain an immutable scope. Existing records
-- inherit the capsule owner's personal scope. Enterprise records are created
-- directly in their tenant scope and must never be copied by changing scope_id.
alter table holo_chat_sessions add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_chat_messages add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_capsule_context add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_life_context add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_session_consolidations add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_artifacts add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_integrations add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_signals add column if not exists scope_id uuid references holo_scopes(scope_id);
alter table holo_transcripts add column if not exists scope_id uuid references holo_scopes(scope_id);

update holo_chat_sessions r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;
update holo_chat_messages r set scope_id = s.scope_id
from holo_chat_sessions s where r.session_id = s.session_id and r.scope_id is null;
update holo_capsule_context r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;
update holo_life_context r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;
update holo_session_consolidations r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;
update holo_artifacts r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;
update holo_integrations r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;
update holo_signals r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;
update holo_transcripts r set scope_id = m.personal_scope_id
from holo_capsule_principals m where r.capsule_id = m.capsule_id and r.scope_id is null;

-- Capsule context is scope-owned after this migration. capsule_id remains
-- provenance for the actor that last wrote the value, not the authority key.
alter table holo_capsule_context drop constraint if exists holo_capsule_context_pkey;
alter table holo_capsule_context add primary key (scope_id, key);
alter table holo_life_context drop constraint if exists holo_life_context_capsule_id_key_key;
alter table holo_life_context drop constraint if exists holo_life_context_scope_key_key;
alter table holo_life_context add constraint holo_life_context_scope_key_key unique (scope_id, key);

create index if not exists holo_chat_sessions_scope_time on holo_chat_sessions(scope_id, last_active desc);
create index if not exists holo_chat_messages_scope_time on holo_chat_messages(scope_id, created_at asc);
create index if not exists holo_capsule_context_scope on holo_capsule_context(scope_id);
create index if not exists holo_life_context_scope on holo_life_context(scope_id);
create index if not exists holo_consolidations_scope_time on holo_session_consolidations(scope_id, created_at desc);
create index if not exists holo_artifacts_scope_time on holo_artifacts(scope_id, created_at desc);
create index if not exists holo_integrations_scope on holo_integrations(scope_id, status);
create index if not exists holo_signals_scope_time on holo_signals(scope_id, occurred_at desc);
create index if not exists holo_transcripts_scope_time on holo_transcripts(scope_id, occurred_at desc);
create unique index if not exists holo_chat_sessions_id_scope on holo_chat_sessions(session_id, scope_id);

-- Checkpoint storage depends on the scoped-session composite key above.
create table if not exists holo_memory_checkpoints (
    checkpoint_id text not null,
    idempotency_key text not null,
    scope_id uuid not null references holo_scopes(scope_id) on delete cascade,
    capsule_id text references holo_capsules(capsule_id) on delete set null,
    session_id text not null,
    start_sequence integer not null,
    end_sequence integer not null,
    transcript_hash text not null,
    triggers text[] not null,
    delta jsonb not null,
    proposals jsonb not null,
    decisions jsonb not null,
    persisted_at timestamptz not null default now(),
    primary key (scope_id, checkpoint_id),
    unique (scope_id, idempotency_key),
    unique (scope_id, session_id, end_sequence),
    foreign key (session_id, scope_id) references holo_chat_sessions(session_id, scope_id)
);

create table if not exists holo_memory_entries (
    scope_id uuid not null references holo_scopes(scope_id) on delete cascade,
    memory_id text not null,
    subject text not null,
    value text not null,
    kind text not null,
    status text not null check (status in ('active', 'quarantined', 'superseded', 'revoked')),
    confidence double precision not null check (confidence between 0 and 1),
    provenance jsonb not null,
    checkpoint_id text not null,
    superseded_by text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    primary key (scope_id, memory_id),
    foreign key (scope_id, checkpoint_id)
        references holo_memory_checkpoints(scope_id, checkpoint_id)
);

-- One immutable episodic projection per acknowledged checkpoint. The complete
-- read-only delta remains available even when it yielded no portrait candidate.
create table if not exists holo_memory_episodes (
    scope_id uuid not null references holo_scopes(scope_id) on delete cascade,
    episode_id text not null,
    checkpoint_id text not null,
    capsule_id text references holo_capsules(capsule_id) on delete set null,
    session_id text not null,
    start_sequence integer not null,
    end_sequence integer not null,
    transcript_hash text not null,
    delta jsonb not null,
    created_at timestamptz not null default now(),
    primary key (scope_id, episode_id),
    unique (scope_id, checkpoint_id),
    foreign key (scope_id, checkpoint_id)
        references holo_memory_checkpoints(scope_id, checkpoint_id),
    foreign key (session_id, scope_id) references holo_chat_sessions(session_id, scope_id)
);

create table if not exists holo_memory_revocations (
    scope_id uuid not null references holo_scopes(scope_id) on delete cascade,
    target_memory_id text not null,
    checkpoint_id text not null,
    provenance jsonb not null,
    revoked_at timestamptz not null default now(),
    primary key (scope_id, target_memory_id),
    foreign key (scope_id, checkpoint_id)
        references holo_memory_checkpoints(scope_id, checkpoint_id)
);

create index if not exists holo_memory_checkpoints_scope_time on holo_memory_checkpoints(scope_id, persisted_at desc);
create index if not exists holo_memory_entries_scope_status on holo_memory_entries(scope_id, status, updated_at desc);
create index if not exists holo_memory_episodes_scope_time on holo_memory_episodes(scope_id, created_at desc);

create or replace function holo_reject_scope_reassignment()
returns trigger language plpgsql as $$
begin
    if old.scope_id is distinct from new.scope_id then
        raise exception 'scope_id is immutable; create an audited derivative transfer';
    end if;
    return new;
end;
$$;

do $$
declare table_name text;
begin
    foreach table_name in array array[
        'holo_chat_sessions', 'holo_chat_messages', 'holo_capsule_context',
        'holo_life_context', 'holo_session_consolidations', 'holo_artifacts',
        'holo_integrations', 'holo_signals', 'holo_transcripts',
        'holo_memory_checkpoints', 'holo_memory_entries', 'holo_memory_episodes',
        'holo_memory_revocations'
    ] loop
        execute format('drop trigger if exists reject_scope_reassignment on %I', table_name);
        execute format(
            'create trigger reject_scope_reassignment before update on %I '
            'for each row execute function holo_reject_scope_reassignment()',
            table_name
        );
    end loop;
end;
$$;

create or replace function holo_enforce_session_scope()
returns trigger language plpgsql as $$
begin
    if new.session_id is not null and not exists (
        select 1 from holo_chat_sessions s
        where s.session_id = new.session_id and s.scope_id = new.scope_id
    ) then
        raise exception 'child record scope does not match chat session scope';
    end if;
    return new;
end;
$$;

do $$
declare table_name text;
begin
    foreach table_name in array array[
        'holo_chat_messages', 'holo_session_consolidations', 'holo_artifacts'
    ] loop
        execute format('drop trigger if exists enforce_session_scope on %I', table_name);
        execute format(
            'create trigger enforce_session_scope before insert or update of session_id, scope_id on %I '
            'for each row execute function holo_enforce_session_scope()',
            table_name
        );
    end loop;
end;
$$;

create or replace function holo_validate_capsule_principal_scope()
returns trigger language plpgsql as $$
begin
    if not exists (
        select 1 from holo_scopes s
        where s.scope_id = new.personal_scope_id
          and s.scope_kind = 'personal'
          and s.owner_principal_id = new.principal_id
          and s.disabled_at is null
    ) then
        raise exception 'personal scope must belong to mapped principal';
    end if;
    return new;
end;
$$;

drop trigger if exists validate_capsule_principal_scope on holo_capsule_principals;
create trigger validate_capsule_principal_scope
before insert or update on holo_capsule_principals
for each row execute function holo_validate_capsule_principal_scope();

create or replace function holo_validate_scope_transfer()
returns trigger language plpgsql as $$
declare destination_tenant uuid;
begin
    if not exists (
        select 1 from holo_scopes s
        where s.scope_id = new.source_scope_id
          and s.disabled_at is null
          and (
              s.owner_principal_id = new.principal_id
              or exists (
                  select 1 from holo_tenant_memberships m
                  where m.tenant_id = s.tenant_id
                    and m.principal_id = new.principal_id
                    and m.status = 'active'
              )
          )
    ) then
        raise exception 'transfer principal is not authorized for source scope';
    end if;

    select tenant_id into destination_tenant
    from holo_scopes
    where scope_id = new.destination_scope_id and disabled_at is null;
    if not found then
        raise exception 'transfer destination scope is unavailable';
    end if;

    if new.decision = 'approved' and destination_tenant is not null and not exists (
        select 1 from holo_tenant_memberships m
        where m.membership_id = new.approved_by_membership_id
          and m.tenant_id = destination_tenant
          and m.status = 'active'
          and ('owner' = any(m.roles) or 'admin' = any(m.roles))
    ) then
        raise exception 'approved transfer requires an active destination owner or admin';
    end if;
    return new;
end;
$$;

drop trigger if exists validate_scope_transfer on holo_scope_transfers;
create trigger validate_scope_transfer
before insert or update on holo_scope_transfers
for each row execute function holo_validate_scope_transfer();

-- Direct anon/authenticated access stays denied. The service-role backend must
-- resolve principal, scope, and active membership before issuing any query.
alter table holo_principals enable row level security;
alter table holo_tenants enable row level security;
alter table holo_scopes enable row level security;
alter table holo_tenant_memberships enable row level security;
alter table holo_capsule_principals enable row level security;
alter table holo_scope_transfers enable row level security;
alter table holo_capsules enable row level security;
alter table holo_chat_sessions enable row level security;
alter table holo_chat_messages enable row level security;
alter table holo_capsule_context enable row level security;
alter table holo_life_context enable row level security;
alter table holo_session_consolidations enable row level security;
alter table holo_artifacts enable row level security;
alter table holo_integrations enable row level security;
alter table holo_signals enable row level security;
alter table holo_transcripts enable row level security;
alter table holo_memory_checkpoints enable row level security;
alter table holo_memory_entries enable row level security;
alter table holo_memory_episodes enable row level security;
alter table holo_memory_revocations enable row level security;

revoke all on holo_principals, holo_tenants, holo_scopes,
    holo_tenant_memberships, holo_capsule_principals, holo_scope_transfers
    from anon, authenticated;
revoke all on holo_capsules, holo_chat_sessions, holo_chat_messages,
    holo_capsule_context, holo_life_context, holo_session_consolidations,
    holo_artifacts, holo_integrations, holo_signals, holo_transcripts
    from anon, authenticated;
revoke all on holo_memory_checkpoints, holo_memory_entries, holo_memory_episodes,
    holo_memory_revocations
    from anon, authenticated;

create or replace function holo_commit_memory_checkpoint(
    p_capsule_id text,
    p_scope_id uuid,
    p_session_id text,
    p_checkpoint jsonb
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
    v_checkpoint_id text := p_checkpoint->>'checkpoint_id';
    v_idempotency_key text := p_checkpoint->>'idempotency_key';
    v_existing text;
    v_proposal jsonb;
    v_disposition text;
    v_kind text;
    v_memory_id text;
    v_target text;
begin
    if coalesce(v_checkpoint_id, '') = '' or coalesce(v_idempotency_key, '') = '' then
        raise exception 'memory checkpoint identity is required';
    end if;
    if not exists (
        select 1 from holo_chat_sessions
        where session_id = p_session_id and scope_id = p_scope_id
    ) then
        raise exception 'memory checkpoint session scope mismatch';
    end if;
    if p_capsule_id is not null and not exists (
        select 1 from holo_capsule_principals
        where capsule_id = p_capsule_id and personal_scope_id = p_scope_id
    ) and not exists (
        select 1
        from holo_capsule_principals cp
        join holo_scopes s on s.scope_id = p_scope_id and s.scope_kind = 'enterprise'
        join holo_tenant_memberships m
          on m.tenant_id = s.tenant_id
         and m.principal_id = cp.principal_id
         and m.status = 'active'
        where cp.capsule_id = p_capsule_id
    ) then
        raise exception 'memory checkpoint capsule is not authorized for scope';
    end if;

    -- Scope participates in the lock key so equal checkpoint payloads in two
    -- authorized scopes cannot observe or block each other's durable result.
    perform pg_advisory_xact_lock(
        hashtextextended(p_scope_id::text || ':' || v_idempotency_key, 0)
    );

    select checkpoint_id into v_existing
    from holo_memory_checkpoints
    where scope_id = p_scope_id and idempotency_key = v_idempotency_key;
    if v_existing is not null then
        return jsonb_build_object('checkpoint_id', v_existing, 'idempotent', true);
    end if;

    insert into holo_memory_checkpoints (
        checkpoint_id, idempotency_key, scope_id, capsule_id, session_id,
        start_sequence, end_sequence, transcript_hash, triggers, delta,
        proposals, decisions
    ) values (
        v_checkpoint_id, v_idempotency_key, p_scope_id, p_capsule_id, p_session_id,
        (p_checkpoint#>>'{delta,start_exclusive,sequence}')::integer,
        (p_checkpoint#>>'{delta,end_inclusive,sequence}')::integer,
        p_checkpoint#>>'{delta,end_inclusive,transcript_hash}',
        array(select jsonb_array_elements_text(p_checkpoint->'triggers')),
        p_checkpoint->'delta', p_checkpoint->'proposals', p_checkpoint->'decisions'
    );

    insert into holo_memory_episodes (
        scope_id, episode_id, checkpoint_id, capsule_id, session_id,
        start_sequence, end_sequence, transcript_hash, delta
    ) values (
        p_scope_id, v_checkpoint_id, v_checkpoint_id, p_capsule_id, p_session_id,
        (p_checkpoint#>>'{delta,start_exclusive,sequence}')::integer,
        (p_checkpoint#>>'{delta,end_inclusive,sequence}')::integer,
        p_checkpoint#>>'{delta,end_inclusive,transcript_hash}',
        p_checkpoint->'delta'
    );

    for v_proposal in select * from jsonb_array_elements(coalesce(p_checkpoint->'proposals', '[]'::jsonb))
    loop
        v_memory_id := v_proposal->>'proposal_id';
        v_kind := v_proposal->>'kind';
        select decision->>'disposition' into v_disposition
        from jsonb_array_elements(coalesce(p_checkpoint->'decisions', '[]'::jsonb)) as decisions(decision)
        where decision->>'proposal_id' = v_memory_id
        limit 1;
        if v_disposition = 'quarantine' then
            insert into holo_memory_entries (
                scope_id, memory_id, subject, value, kind, status, confidence,
                provenance, checkpoint_id
            ) values (
                p_scope_id, v_memory_id, v_proposal->>'subject', v_proposal->>'value',
                v_kind, 'quarantined', (v_proposal->>'confidence')::double precision,
                v_proposal->'provenance', v_checkpoint_id
            ) on conflict (scope_id, memory_id) do nothing;
            continue;
        elsif v_disposition is distinct from 'admit' then
            continue;
        end if;

        if v_kind = 'revocation' then
            v_target := v_proposal->>'target_memory_id';
            update holo_memory_entries set
                status = 'revoked', updated_at = now()
            where scope_id = p_scope_id and memory_id = v_target;
            insert into holo_memory_revocations (
                scope_id, target_memory_id, checkpoint_id, provenance
            ) values (
                p_scope_id, v_target, v_checkpoint_id, v_proposal->'provenance'
            ) on conflict (scope_id, target_memory_id) do update
              set checkpoint_id = excluded.checkpoint_id,
                  provenance = excluded.provenance,
                  revoked_at = now();
            continue;
        end if;

        if v_kind = 'supersession' then
            v_target := v_proposal->>'target_memory_id';
            update holo_memory_entries set
                status = 'superseded', superseded_by = v_memory_id, updated_at = now()
            where scope_id = p_scope_id and memory_id = v_target;
        end if;

        if exists (
            select 1 from holo_memory_revocations
            where scope_id = p_scope_id and target_memory_id = v_memory_id
        ) then
            continue;
        end if;
        insert into holo_memory_entries (
            scope_id, memory_id, subject, value, kind, status, confidence,
            provenance, checkpoint_id
        ) values (
            p_scope_id, v_memory_id, v_proposal->>'subject', v_proposal->>'value',
            v_kind, 'active', (v_proposal->>'confidence')::double precision,
            v_proposal->'provenance', v_checkpoint_id
        ) on conflict (scope_id, memory_id) do update set
            subject = excluded.subject,
            value = excluded.value,
            kind = excluded.kind,
            status = 'active',
            confidence = excluded.confidence,
            provenance = excluded.provenance,
            checkpoint_id = excluded.checkpoint_id,
            updated_at = now();
    end loop;

    return jsonb_build_object('checkpoint_id', v_checkpoint_id, 'idempotent', false);
end;
$$;

revoke all on function holo_commit_memory_checkpoint(text, uuid, text, jsonb) from public;
grant execute on function holo_commit_memory_checkpoint(text, uuid, text, jsonb) to service_role;

-- Do not force NOT NULL until this assertion passes. It deliberately aborts
-- migration if orphaned legacy rows exist instead of silently mis-scoping them.
do $$
declare orphan_count bigint;
declare table_name text;
begin
    foreach table_name in array array[
        'holo_chat_sessions', 'holo_chat_messages', 'holo_capsule_context',
        'holo_life_context', 'holo_session_consolidations', 'holo_artifacts',
        'holo_integrations', 'holo_signals', 'holo_transcripts'
    ] loop
        execute format('select count(*) from %I where scope_id is null', table_name) into orphan_count;
        if orphan_count > 0 then
            raise exception 'scope migration blocked: % has % orphaned rows', table_name, orphan_count;
        end if;
        execute format('alter table %I alter column scope_id set not null', table_name);
    end loop;
end;
$$;
