# Outreach Email — June 2026

---

**Subject:** AI that knows why it stopped a payment (new benchmark results)

---

Hi [Name],

Quick one.

We ran a benchmark this week where we gave 11 different AI architectures — GPT-5.4, Claude, Gemini, councils, ensembles — the same set of enterprise action packets and scored not just whether they got the verdict right, but whether they could explain *why*.

One result stood out.

A payment packet had a complete bank-account verification chain. Authenticated portal. Callback to the phone number on file. Two-approver sign-off. Vendor master updated. Clean by every BEC standard.

10 out of 11 systems said ALLOW. The 11th — Holo — escalated.

The invoice referenced a purchase order that wasn't in the packet. Without the underlying authorization, the payment couldn't be executed. The other 10 systems cleared the BEC risk and stopped reading. Holo kept reading until the loop actually closed.

The Judge — our independent trace-adjudication system — confirmed Holo was right.

Across 8 frozen benchmark packets, Holo scored 8/8 on reasoning quality. The other architectures scored between 1/8 and 8/8 depending on packet type.

The short version: Holo doesn't just return a verdict. It returns the specific documents and fields that support the decision. That chain is what makes the verdict auditable and defensible in a regulated environment.

We're looking for one or two enterprise design partners in financial services or compliance who want to run Holo against real workflows before we scale.

If that's interesting, I'd love 20 minutes.

Taylor

---

**P.S.** Full benchmark summary attached / linked if you want the detail. The methodology is worth reading — we built something that tests reasoning quality, not just verdict accuracy, which turns out to be a materially different thing.
