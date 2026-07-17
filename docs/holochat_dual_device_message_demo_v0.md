# HoloChat Dual-Device Message Demo V0

## What This Demo Proves

This is a controlled demonstration of two real source devices producing
Personal Holo context without turning HoloChat into a message archive.

- One iMessage test conversation on Taylor's signed-in Mac.
- One SMS test conversation on Crayton's Android phone.
- Both sources emit a bounded Personal context event.
- HoloChat stores the event summary and context shape, not message bodies,
  phone numbers, contacts, attachments, or transcripts.
- Enterprise Holo remains unable to read either source or event.

This demo does not claim that Holo can inspect arbitrary private messages
without policy. It demonstrates the consented source-to-context boundary.

For the live product, a user may elect full Personal source access. The demo
uses a dedicated test chat because the current V0 bridge stores only bounded
events, not raw message text. Full source access and full encrypted Personal
archive/sync are separate opt-ins.

## Demo Guardrails

1. Use new, dedicated test conversations only. Do not use family, customer,
   medical, legal, HR, or active work threads.
2. Read-only sources. Do not grant message send, reply, reaction, editing,
   attachment, or group-management capabilities.
3. No broad history import. Limit the demonstration to messages created during
   the live demo and a short, agreed lookback.
4. Keep the source allowlist locally with the device bridge. Do not upload
   contact names, phone numbers, or chat identifiers to HoloChat.
5. Show the audience the connector audit record and accepted context event,
   not the test messages themselves.

## Demo Story

### Taylor's iMessage test

Use a new test chat with a harmless, fictional message such as:

> The school meeting moved to 4:30 today. Please keep the afternoon clear.

The Personal event should be:

```json
{
  "signal_type": "schedule_change",
  "context_shape": {
    "capacity": "constrained",
    "availability": "async_first",
    "approach": ["supportive", "concise"],
    "timing": "this_afternoon"
  }
}
```

### Crayton's Android SMS test

Use a new test SMS with a harmless, fictional message such as:

> Your apartment maintenance window is now tomorrow from 8 to 10 AM.

The Personal event should be:

```json
{
  "signal_type": "practical_constraint",
  "context_shape": {
    "capacity": "constrained",
    "availability": "async_first",
    "approach": ["calm", "concise"],
    "timing": "tomorrow_morning"
  }
}
```

## Live Setup Prerequisites

### Taylor's iMessage source

- A Mac signed into Messages with Taylor's Apple account.
- `imsg` installed on that same logged-in Mac user.
- Full Disk Access granted to the exact process context running `imsg` and
  OpenClaw. This grants local access to the Messages database, so it must be
  treated as a high-sensitivity, user-approved permission.
- Basic mode only. Do not disable SIP and do not run `imsg launch`.
- A HoloChat Personal connector ID and one-time connector secret.

No Apple developer API key or iCloud app password is required for the local
Messages database route. Automation permission is not needed because V0 does
not send messages.

### Crayton's Android source

- An OpenClaw Android node paired to the trusted gateway.
- Android `READ_SMS` permission.
- Gateway policy with `sms.search` explicitly allowlisted and `sms.send`
  explicitly absent.
- A HoloChat Personal connector ID and one-time connector secret owned by the
  Android participant's Personal Holo.

## Live Run Sequence

1. Apply the reviewed HoloChat connector migration and deploy the connector
   endpoints.
2. Create one Personal connector per device. Show each one-time secret only to
   its device owner, then store it locally in a secret manager or transient
   session.
3. Configure each local bridge with a single local test-chat allowlist and a
   maximum lookback measured in minutes, not days.
4. Send the two fictional test messages during the demo.
5. Each bridge emits the bounded event through
   `/v1/connectors/messages/events`.
6. In Personal Holo, ask: “What changed in my day that should shape how you
   help me?” The response should use the delivery posture and timing context.
7. Switch to Enterprise. Verify that neither raw source, summary, nor Personal
   event appears there.
8. Pause both connectors. Confirm that subsequent test messages make no new
   context event.

## Success Criteria

- Both devices produce a verified event with `raw_messages_accepted: false`.
- HoloChat reveals no message content, sender identity, or attachment.
- Personal Holo gives a more informed, supportive response.
- Enterprise Holo receives nothing without a separately reviewed HoloPulse
  policy.
- Pause and revoke controls stop intake immediately.

## Not In This Demo

- Sending or replying to messages.
- Full inbox or full conversation history scanning.
- Attachments, photos, audio, or group-message ingestion.
- Personal-to-Enterprise transfer.
- Automated actions based on a message.
