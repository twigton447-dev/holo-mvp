# HoloBrain Daily Status Delivery Design

Status: design note only.

## Current Manual Command

Run the local HoloBrain status check from the repo worktree:

```bash
./venv/bin/python -m holobrain.operations.daily_control --dry-run
```

Live email delivery is explicit and requires environment configuration:

```bash
./venv/bin/python -m holobrain.operations.daily_control --send-email
```

Default mode remains dry-run and no-send. The command does not update canonical benchmark state, doctrine, manifests, memory objects, or benchmark packets.

## Email Configuration

Use environment variables only:

- `HOLOBRAIN_STATUS_EMAIL_TO`
- `HOLOBRAIN_STATUS_EMAIL_FROM`
- `HOLOBRAIN_STATUS_EMAIL_PROVIDER`
- `HOLOBRAIN_STATUS_SMTP_HOST`
- `HOLOBRAIN_STATUS_SMTP_USER`
- `HOLOBRAIN_STATUS_SMTP_SECRET`

Secrets must stay out of Git. The email body must not include secrets, raw traces, benchmark packets, API keys, or full diffs.

## Later 8am Scheduling With launchd

Because local dirty-worktree status only exists on Taylor's local Mac/worktree, the eventual daily 8am job should run locally via `launchd`.

Proposed shape:

- Program: repo-local virtualenv Python.
- Arguments: `-m holobrain.operations.daily_control --send-email`.
- Working directory: this repo checkout.
- StartCalendarInterval: hour `8`, minute `0`.
- Environment variables: loaded from a local-only launchd environment or a local secret manager, not from committed files.
- Logs: write stdout/stderr to local-only files outside canonical docs.

GitHub Actions may later verify remote repo state, but it cannot see local dirty files unless they are pushed or uploaded. Local launchd remains the source for dirty-worktree status.

## SMS/Text Later

SMS is a later adapter. It should send only a short escalation summary and use provider-specific environment variables. It should not be coupled to the email adapter.
