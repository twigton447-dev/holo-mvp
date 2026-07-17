# HoloChat Phone Message Integration V0

## Purpose

Enable a user-owned Personal Holo to receive approved message context from an
iPhone or Android device. This is not an Enterprise connector and it does not
create a Personal-to-Enterprise transfer path.

## Non-negotiable boundary

- Personal messages remain Personal source evidence.
- Holo may derive a time-bound context shape such as `availability_constrained`
  or `supportive_low_pressure_approach` only inside Personal.
- No message body, attachment, contact identity, or derived message context may
  cross to Enterprise without a separately approved HoloPulse rule.
- Reading, sending, deleting, reacting to, or modifying messages are separate
  permissions. Start with read-only intake.
- A connected source must be visible, pausable, and revocable from HoloChat.

## Personal Access Is A User Choice

Holo does not need to be artificially limited to a few messages when a person
explicitly wants their Personal Holo to understand their life. The product must
make the following decisions separately and in plain language:

1. **Source access**: no access, selected conversations, or full Personal
   message access. Full access means the local device bridge may read the
   Messages or SMS data available to that device owner.
2. **Processing**: context-only extraction or full Personal Holo reasoning over
   the source text.
3. **Retention and sync**: no raw retention, local encrypted retention, or a
   separately designed encrypted Personal archive that can sync across a
   user's devices.

V0 implements the first two source levels only through a local bridge and
stores no raw message text in HoloChat. A future full Personal archive must be
a distinct, explicit consent flow with encryption, retention, export, deletion,
and third-party model data-use controls. It must never imply permission to send
Personal message data to Enterprise Holo.

## Local installation state

This worktree contains an isolated OpenClaw runtime at `.tools/openclaw` and a
wrapper at `scripts/openclaw-local`. It is not running as a daemon and has no
connected channel, model, account, or device permission. It also contains the
checksum-verified `imsg` v0.13.1 release under `.tools/imsg`; invoke it only
through the read-only `scripts/holochat-imessage-source` wrapper.

Use the wrapper for inspection only until the integration policy and HoloChat
connector endpoints are ready:

```bash
scripts/openclaw-local --version
scripts/openclaw-local channels status --probe
scripts/holochat-imessage-source --version
```

## iPhone / iMessage

OpenClaw's iMessage channel runs on a Mac that is signed into Messages. It
uses the `imsg` bridge and requires Full Disk Access to read the local Messages
database. Sending requires macOS Automation permission. Basic read/send works
without weakening System Integrity Protection; advanced reactions and message
mutation are out of scope for V0.

Before pairing, the user must explicitly approve:

1. A read-only iMessage source connection.
2. The allowed chat set or contact allowlist.
3. Whether Holo may retain only normalized context events, or may retain a
   source reference for later user review.

Do not grant message-send, reaction, edit, unsend, or group-management actions
in V0.

The Holo wrapper permits only `status`, `chats`, `group`, `history`, `watch`,
`search`, `stats`, and `scheduled`. It blocks `send`, `react`, `launch`, and
all private-bridge mutation commands before `imsg` runs.

## Android

Use an OpenClaw Android node for V0. `sms.search` requires both Android's
`READ_SMS` permission and an explicit gateway command allowlist. Do not enable
`sms.send` in V0. Notification forwarding is not a substitute for SMS access:
it is noisier, may duplicate events, and must not be used to ingest other chat
apps into Holo without a source-specific connection.

Use `scripts/holochat-android-sms-source` for the device source. It hardcodes
only `sms.search`, refuses an unreviewed broad default query, and cannot invoke
`sms.send` or any other OpenClaw node command. The gateway must separately
allow `sms.search` and deny `sms.send`:

```json5
{
  gateway: {
    nodes: {
      allowCommands: ["sms.search"],
      denyCommands: ["sms.send"],
    },
  },
}
```

Before pairing, the user must explicitly approve:

1. A read-only Android node.
2. `sms.search` only, scoped to the user's own device.
3. The message period and contact scope Holo may inspect.

## HoloChat Foundation In This Worktree

The following is implemented here but not deployed or connected to a device:

1. `migrations/20260717_holochat_phone_message_connectors.sql` creates a
   Personal-only connector registry and normalized event ledger. Database
   triggers reject Enterprise scopes and scope/capsule mismatches.
2. `POST /v1/capsule/message-connectors` issues a one-time, hashed bridge
   secret to the authenticated Personal-space owner. The browser never receives
   the hash and the server never returns the secret again.
3. `POST /v1/connectors/messages/events` accepts only bounded context events.
   It rejects fields such as `body`, `message`, `summary`, `contact`,
   `phone_number`, and `attachments` before database access. The source submits
   an approved signal type; the server generates the stored summary.
4. `scripts/holochat_message_context_bridge.py` validates one normalized JSON
   event from stdin and posts it with connector credentials held only in local
   environment variables. It does not read a message database itself.

Validate a proposed event without credentials or network activity:

```bash
printf '%s\n' '{"source_event_id":"imsg-001","occurred_at":"2026-07-17T10:00:00Z","event_type":"message_received","signal_type":"schedule_change","context_shape":{"capacity":"constrained","timing":"today","approach":["supportive","concise"]}}' \
  | .venv312/bin/python scripts/holochat_message_context_bridge.py --dry-run
```

After the reviewed migration is applied and the user has created a connector,
the local bridge needs only these transient environment variables:

```bash
export HOLOCHAT_MESSAGE_INGEST_URL='https://your-holochat-host/v1/connectors/messages/events'
export HOLOCHAT_MESSAGE_CONNECTOR_ID='returned-once-connector-id'
export HOLOCHAT_MESSAGE_CONNECTOR_SECRET='returned-once-connector-secret'
```

The connector secret belongs in a user-owned secret manager or local session,
never a committed `.env` file. The bridge is still read-only: it has no send,
delete, reaction, or message-mutation capability.

## Remaining Work Before Live Pairing

1. Apply the reviewed database migration through the normal Supabase path.
2. Add a reviewed OpenClaw source adapter that emits only the normalized event
   schema to the bridge; no direct raw-message upload is permitted.
3. Add a HoloPulse governor that defaults to deny and requires source policy,
   user consent, destination entitlement, recipient scope, and expiry.
4. Test source-to-shape, shape-to-pulse, and prohibited-detail cases before any
   Enterprise use.
5. Require an explicit user confirmation before every external action.
