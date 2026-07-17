# HoloChat Onboarding Import v0

## Objective

New users should not have to re-explain themselves from zero. HoloChat can ask the user's current favorite AI to produce a HoloBrain Import Packet, then deterministically sort that packet into Personal memory, quarantine, and rejection buckets.

The user should not be forced into a long memory-review chore before reaching HoloChat. Review must remain available, but the default path is:

1. Copy the prompt.
2. Paste it into the AI that knows the user best.
3. Paste the response into HoloChat.
4. Continue.

## Admission Posture

The import path is Personal-first.

- Clear Personal context: admit.
- Family, health, marriage, legal trouble, and other sensitive-but-user-provided context: admit only to Personal-private memory.
- Uncertain, inferred, old, contradictory, or incomplete claims: quarantine.
- Passwords, account numbers, identifiers, full addresses, private keys, and similar secrets: reject.
- Client names, issuer names, live deals, confidential files, nonpublic financials, IC materials, and other Enterprise-confidential material: reject from Personal import.
- Enterprise receives no raw Personal import data.

Review is available but not required.

## Cross-Scope Rule

HoloPersonal may remember how work affects the user, including general role context and harmless work preferences. It must not retain confidential work facts.

HoloEnterprise may receive only minimal, user-authorized availability signals from Personal, such as:

```text
availability limited today
```

It must not receive family names, medical reasons, relationship details, diagnoses, medications, or private personal stories.

## Prompt To Other AI

```text
I am setting up HoloChat, a persistent Personal workspace that preserves only the context I choose to keep. The areas I expect to use most are: {areas}.

Create a HoloBrain Import Packet from what you already know about me. This will be pasted into HoloChat so it can give me a useful beginning without making me explain everything again.

Important rules:
- Use only information I explicitly shared or directly confirmed.
- Do not infer motives, diagnose, flatter, fill gaps, or turn temporary ideas into stable facts.
- Separate Personal context from employer, client, team, organization, or deal information.
- Put uncertain, old, disputed, inferred, contradictory, or incomplete claims in Needs confirmation.
- Put sensitive items that should not be stored in Do not import.
- Do not include passwords, API keys, security answers, financial account numbers, government identifiers, full addresses, private medical records, identifiable patient or client information, privileged communications, or anything unsafe to store.

Return exactly these labeled sections:
1. Stable personal context
2. Current priorities
3. Working style
4. Important relationships and stakeholders
5. Constraints and boundaries
6. Open loops
7. Needs confirmation
8. Do not import

For each important item, write one short bullet with the fact or context, confidence (confirmed, user-stated, or needs confirmation), and recency when known. Keep it under 1,500 words. End with: "HoloChat should import the clear Personal context, quarantine uncertain items, and reject anything unsafe or Enterprise-confidential."
```

## Next Persona Test

Use a new synthetic persona account rather than unwinding Elliot Vale. The test should verify:

- HoloPersonal can retrieve seeded spouse, children, health constraints, preferences, and private continuity across random Personal threads.
- HoloEnterprise does not receive spouse, children, health, or personal preference details.
- HoloEnterprise may receive only a minimal availability signal if explicitly allowed.
- HoloPersonal can know general work pressure without storing confidential work records.
- The import endpoint reports admitted, quarantined, and rejected counts.
