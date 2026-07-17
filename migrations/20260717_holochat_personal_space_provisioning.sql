-- Give every newly created HoloChat identity a Personal space immediately.
-- Enterprise scopes are intentionally not created here: they require a tenant
-- and an active membership established by the Enterprise authorization flow.
--
-- The hybrid-scope migration backfilled existing capsules. This follow-up
-- trigger keeps that invariant true for signups and healed capsules created
-- after hybrid scopes are enabled.

create or replace function holo_provision_personal_scope_for_capsule()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
    v_principal_id uuid;
    v_personal_scope_id uuid;
begin
    insert into holo_principals (auth_subject)
    values ('capsule:' || new.capsule_id)
    on conflict (auth_subject) do nothing;

    select principal_id into v_principal_id
    from holo_principals
    where auth_subject = 'capsule:' || new.capsule_id;

    insert into holo_scopes (scope_kind, owner_principal_id, display_name)
    values ('personal', v_principal_id, 'Personal')
    on conflict (owner_principal_id) where scope_kind = 'personal' do nothing;

    select scope_id into v_personal_scope_id
    from holo_scopes
    where owner_principal_id = v_principal_id
      and scope_kind = 'personal';

    insert into holo_capsule_principals (
        capsule_id,
        principal_id,
        personal_scope_id
    ) values (
        new.capsule_id,
        v_principal_id,
        v_personal_scope_id
    ) on conflict (capsule_id) do nothing;

    return new;
end;
$$;

drop trigger if exists provision_personal_scope_for_capsule on holo_capsules;
create trigger provision_personal_scope_for_capsule
after insert on holo_capsules
for each row execute function holo_provision_personal_scope_for_capsule();

-- The backend alone exercises the provisioning path. Direct browser roles
-- retain no table access under the hybrid-scope migration's RLS policy.
revoke all on function holo_provision_personal_scope_for_capsule() from public;
