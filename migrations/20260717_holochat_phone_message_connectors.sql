-- Personal-only phone-message connector foundation.
-- Apply after the hybrid-scope migration. No direct client grants are added.

create table if not exists holo_message_connectors (
    connector_id uuid primary key default gen_random_uuid(),
    scope_id uuid not null references holo_scopes(scope_id) on delete cascade,
    capsule_id text references holo_capsules(capsule_id) on delete set null,
    provider text not null check (provider in ('openclaw_imessage', 'openclaw_android')),
    label text not null,
    status text not null check (status in ('pending', 'paired', 'paused', 'revoked', 'error')) default 'pending',
    capabilities text[] not null default array['message_context_ingest']::text[],
    secret_prefix text not null unique,
    secret_hash text not null,
    created_at timestamptz not null default now(),
    last_event_at timestamptz,
    paused_at timestamptz,
    revoked_at timestamptz,
    check (array_length(capabilities, 1) = 1 and capabilities[1] = 'message_context_ingest')
);

-- A revoked pairing can be replaced; only one non-revoked provider pairing may exist.
create unique index if not exists holo_message_connectors_one_active_provider_idx
    on holo_message_connectors (scope_id, provider)
    where status in ('pending', 'paired', 'paused');

-- The API checks scope kind too, but this database trigger makes a Personal to
-- Enterprise message path impossible even if an application route regresses.
create or replace function holo_require_personal_message_connector_scope()
returns trigger
language plpgsql
as $$
begin
    if not exists (
        select 1
        from holo_scopes
        where scope_id = new.scope_id
          and scope_kind = 'personal'
    ) then
        raise exception 'message connectors require a personal scope';
    end if;
    return new;
end;
$$;

drop trigger if exists holo_message_connectors_require_personal_scope
    on holo_message_connectors;
create trigger holo_message_connectors_require_personal_scope
before insert or update of scope_id on holo_message_connectors
for each row execute function holo_require_personal_message_connector_scope();

create table if not exists holo_message_context_events (
    event_id uuid primary key default gen_random_uuid(),
    connector_id uuid not null references holo_message_connectors(connector_id) on delete cascade,
    scope_id uuid not null references holo_scopes(scope_id) on delete cascade,
    capsule_id text references holo_capsules(capsule_id) on delete set null,
    source_event_id text not null,
    occurred_at timestamptz not null,
    event_type text not null check (event_type in ('message_received', 'message_sent')),
    summary text not null,
    context_shape jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    unique (connector_id, source_event_id)
);

create index if not exists holo_message_connectors_scope_status
    on holo_message_connectors(scope_id, status);
create index if not exists holo_message_context_events_scope_time
    on holo_message_context_events(scope_id, occurred_at desc);

create or replace function holo_validate_message_context_event_connector()
returns trigger
language plpgsql
as $$
declare
    connector_scope_id uuid;
    connector_capsule_id text;
begin
    select scope_id, capsule_id
      into connector_scope_id, connector_capsule_id
      from holo_message_connectors
     where connector_id = new.connector_id;

    if connector_scope_id is null
       or connector_scope_id <> new.scope_id
       or connector_capsule_id is distinct from new.capsule_id then
        raise exception 'message context event must match its Personal connector scope and capsule';
    end if;
    return new;
end;
$$;

drop trigger if exists holo_message_context_events_validate_connector
    on holo_message_context_events;
create trigger holo_message_context_events_validate_connector
before insert or update of connector_id, scope_id, capsule_id
on holo_message_context_events
for each row execute function holo_validate_message_context_event_connector();

alter table holo_message_connectors enable row level security;
alter table holo_message_context_events enable row level security;
revoke all on holo_message_connectors, holo_message_context_events from anon, authenticated;
