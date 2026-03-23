# Captain Consolidation Spec

## What Consolidation Is

At the end of every session, the Captain does one more thing before she goes quiet.

She looks at everything that happened — what was said, what signals came in during the day, what she surfaced, how it landed — and she decides what is now different about her understanding of this person. Then she writes it, prunes what it replaced, and leaves a note for herself about what to pick up next time.

This is not a summary of the session. It is an update to her model of the person. The question she is answering is not "what happened today" but "what is now true that wasn't true before, and what is no longer true that I was holding."

---

## The Four Consolidation Actions

### 1. Write New Insights
When a session or signal window reveals something genuinely new about the person — a pattern she hadn't seen, a goal that emerged, a fear that surfaced, a decision that clarified something — the Captain writes it to `holo_life_context`.

Written in plain language. First person about the person. Specific.

**Good:**
> "Has been avoiding the co-founder conversation for three weeks. Brings it up obliquely then redirects. The discomfort is real."

**Not useful:**
> "Has co-founder issues."

Confidence starts at 1.0 if the signal was strong and direct. Lower if inferred.

---

### 2. Reinforce Existing Insights
When signals confirm something already in context — the pattern shows up again, the concern resurfaces, the behavior repeats — the Captain reinforces it.

- `last_reinforced` → now
- `reinforcement_count` → +1
- `confidence` → nudge up toward 1.0 if it had decayed

Reinforcement is not re-writing. The insight stays as written unless its meaning has evolved.

---

### 3. Prune What Is No Longer True
This is the most important action. When something has changed — resolved, evolved, reversed, superseded — the Captain prunes the old insight.

Pruning requires three things:
- Set `pruned_at` to now
- Write `prune_reason` in plain language — what changed, what the evidence was
- If the old insight is being replaced by a new state, set `superseded_by` to the new insight's ID and write the new insight first

**The prune reason is not a code flag. It is a sentence.**

> "Concern resolved. Three consecutive weeks of stable cash flow signals, and she explicitly said the runway situation feels different now."

> "Goal replaced. The agency pivot was formally decided this session. The freelance growth goal that preceded it is no longer the operating frame."

> "Pattern broke. The avoidance behavior around the partnership conversation ended — she initiated it herself and reported it went well."

Soft deletion only. The pruned row stays for 30 days so the Captain can reference the arc of change if needed. Then it is released.

---

### 4. Leave a Note for Next Time
The Captain writes a consolidation record to `holo_session_consolidations` before she closes.

Four fields:
- **what_changed** — which insights were written, reinforced, or pruned
- **what_surfaced** — what thought bubbles were shown and whether they landed
- **open_threads** — things that came up but weren't resolved; the Captain intends to return to them
- **pilot_note** — a note to herself in plain language about this person right now

The pilot_note is the most human thing she writes. It is not structured. It is what she would say to herself before walking back into the room.

> "She's close to a real decision on the co-founder question but not quite there. Don't push next time — let it surface. The financial stuff is genuinely better and she needs to feel that before she takes on the next hard thing."

---

## What the Captain Does NOT Do

- Does not archive old versions of insights "just in case"
- Does not keep raw transcripts or emails after extraction
- Does not hold a fact and its replacement simultaneously — when something changes, the old state goes
- Does not write vague or categorical entries — every insight must be specific enough to be actionable
- Does not confuse volume with quality — a lean, accurate context is worth more than an exhaustive one

---

## Session Open: Loading Context

At the start of every session the Captain loads:

1. Last consolidation note (`holo_session_consolidations` — most recent)
2. Active life context (`holo_life_context` WHERE `pruned_at IS NULL`, ordered by `confidence DESC`)
3. Recent signals from the last 48 hours (`holo_signals` — most recent window)
4. Any pending transcripts (`holo_transcripts` WHERE `status = 'pending'`)

She processes pending transcripts first, extracts nutrients, updates life context, then begins the session already knowing where the person is.

The person does not need to recap. She already knows.

---

## Confidence Decay

Every insight that isn't reinforced by new signals weakens over time. Approximately 0.1 per week.

When confidence drops below 0.5, the Captain notes it as uncertain in her session-open load. When it drops below 0.3, she actively looks for signals that either confirm or contradict it in the current session.

If she finds confirmation: reinforce, confidence back up.
If she finds contradiction: prune, write the new state.
If she finds nothing: the insight lingers at low confidence until it either gets reinforced or decays to zero and gets pruned automatically.

This is how the brain stays honest. Things that were true once but are no longer actively supported by reality quietly lose their weight and eventually leave.

---

## The Pruning Philosophy

Living things prune. Not because the old growth was bad — because the new growth needs the energy.

A brain that holds everything equally is a filing cabinet. The Captain holds what is currently true, what is currently load-bearing, what is currently useful for helping this person move. When something no longer meets that standard, it goes.

Not erased — released. There is a difference. The arc of the person's life is real and the Captain has witnessed it. But she does not carry every version of every chapter. She carries where they are now, informed by where they have been.

That is what it means to actually know someone.
