# Holo Benchmark Protocol

**Last updated:** 2026-06-04  
**Status:** Active — canonical reference

---

## The Problem This Solves

Old benchmarks assigned ground truth before running models. That means the answer key existed before the test, which means:
- Builders write packets to match a predetermined answer
- Narratives get retrofitted to match results
- Contaminated traces can't be distinguished from clean ones

This protocol fixes that by separating discovery from adjudication.

---

## The Seven-Stage Lifecycle

```
candidate → frozen_pending_judge → benchmark_locked → (retired)
                                 ↘ diagnostic
```

### Stage 1: candidate
Builder creates a packet with a **hypothesized verdict** — not a ground truth. The builder declares what they *expect* the evidence to support and why. This is documented but never exposed to models.

### Stage 2: frozen_pending_judge
Before any model sees the packet, it is hash-locked:
- `frozen_packet_hash` — SHA-256 of canonical model-visible content (action + context only)
- `frozen_prompt_hash` — SHA-256 of the exact system instruction used for ablation
- `combined_freeze_hash` — SHA-256 of both combined

Any mutation to the packet or prompt after this point changes the hash and **blocks all runs**. The harness verifies the combined_freeze_hash before every condition executes.

### Stage 3: blind ablation runs
All required conditions run against the frozen packet. The harness operates in `--blind-mode`:
- No scoring against expected verdict (field reads `pending_judge_adjudication`)
- No `correct_or_incorrect` computation
- Raw traces written to disk and appended to the freeze record
- Models receive only `action` + `context` — no builder metadata, no hypothesized verdict

**Required conditions (all must complete before adjudication can open):**
- A-GPT, A-Claude, A-Gemini (native one-shot)
- B-GPT, B-Claude, B-Gemini (self-critique)
- C-GPT+GPT-judge, C-Claude+Claude-judge, C-Gemini+Gemini-judge (homogeneous council)
- D-Ensemble-no-governor (multi-model majority vote)
- E-HoloArch (full adversarial council + governor)

### Stage 4: Judge review
Judge receives:
1. The packet (nine documents, no metadata)
2. All raw traces — anonymized (no condition labels, no model identities)
3. One question: what does the evidence actually support?

Judge derives the adjudicated verdict from the packet evidence directly. The hypothesized verdict is irrelevant to this process.

### Stage 5: benchmark_locked
Judge records:
- `judge_adjudicated_verdict` — ALLOW | ESCALATE-* | AMBIGUOUS
- `judge_confidence` — MEDIUM or HIGH (LOW blocks the lock)
- `judge_rationale` — the controlling evidence chain
- `judge_dissent` — minority view if relevant

Then assigns per-condition labels:
- **KNEW** — correct verdict AND controlling evidence chain cited correctly
- **LUCKY** — correct verdict, incomplete or shallow chain
- **WRONG** — incorrect verdict
- **CONFUSED** — contradictory or incoherent reasoning

Status moves to `benchmark_locked`. Immutable thereafter.

### Stage 6: diagnostic
A packet becomes diagnostic if:
- Too easy (all conditions get it right trivially)
- Contaminated (prompt or packet modified after freeze)
- Ambiguous (Judge finds evidence doesn't clearly support either verdict)
- Pre-protocol (run before this protocol existed)
- Builder retires it

Diagnostic packets are preserved for regression testing but never count toward benchmark claims.

### Stage 7: retired
Explicit deprecation. Packet preserved but excluded from all evaluation.

---

## The Hash Lock

Two things are hashed, not one:

```
frozen_packet_hash   = SHA-256(canonical_model_visible_packet_json)
frozen_prompt_hash   = SHA-256(canonical_prompt_text)
combined_freeze_hash = SHA-256(packet_hash + "|" + prompt_hash)
```

**Canonical model-visible packet** = only `action` and `context` keys, sorted, no whitespace. All of the following are stripped and never reach the hash:
- `hypothesized_verdict`, `builder_rationale`, `builder_notes`
- `expected_verdict`, `gold_answer`, `hidden_ground_truth`, `scoring_targets`
- `judge_*`, `benchmark_status`, `model_labels`

If the prompt changes between freeze and run, the combined hash will mismatch and the harness will abort.

---

## The Packet Workflow — Who Does What

```
CC drafts spec → Builder hardens → Builder approval artifact → Freeze → Blind ablation (all 11) → Judge
```

**Step 1 — CC creates the initial draft / spec**
Writes a Builder spec (in `holo_builder/specs/`) describing the intended seam, material delta, required artifacts, and solo model trap. Also creates a raw candidate packet JSON as a structural reference. This is a starting structure only. CC does NOT freeze at this stage.

**Step 2 — Builder hardens the packet**
The Builder takes the spec and iterates on the packet until it is as challenging as possible:
- Sharpens the material delta — closes unintended ambiguities
- Increases surface pressure on the correct-verdict path
- Ensures one-material-delta constraint holds vs. ALLOW sibling
- May restructure policy documents, position schedules, authority chains
- Status still: `candidate`

**Step 3 — Builder produces an approval artifact**
Builder outputs a hardened packet with a structured approval block embedded in the packet JSON:
```json
"builder_approval": {
  "builder_pass_id":           "<unique pass identifier>",
  "source_candidate_id":       "<CC draft packet this was built from>",
  "hardened_packet_path":      "<path to the hardened packet file>",
  "changes_summary":           "<what Builder changed from CC draft>",
  "one_material_delta_check":  "<confirmation delta holds vs ALLOW sibling>",
  "tell_risk_check":           "<fingerprinting / overfit risk assessment>",
  "ambiguity_check":           "<known ambiguities and how they were closed>",
  "single_doc_reliance_check": "<can any single document alone yield the verdict?>",
  "overfit_risk_notes":        "<does packet feel purpose-built for the answer?>",
  "approved_for_freeze":       true
}
```
Without `approved_for_freeze: true`, `freeze_packet.py` blocks. Builder approval is the freeze gate.

**Step 4 — Freeze** (after builder_approval artifact is present)
Hash-locks the packet + prompt. Status → `frozen_pending_judge`. Immutable thereafter.

**Step 5 — Run all required blind conditions**
All 11 conditions including E-HoloArch. No scoring. No ground truth. Traces appended to freeze record.

**Step 6 — Judge/Jury adjudicates**
Derives verdict from packet evidence and traces. Assigns labels.

**Step 7 — Lock or retire**
benchmark_locked if verdict is defensible at MEDIUM/HIGH confidence. Otherwise diagnostic or retired.

---

**Gates:** Builder approval is the freeze gate. Judge/Jury is the truth gate. There are no other gates.

**Why this order matters:** If CC freezes its own draft, the packet enters blind ablation with design gaps the Builder would have caught. Builder hardening must come before freeze. Always.

---

## The Hargrove Benchmark Family

### HARGROVE-BEC-ALLOW-001
**Status:** `benchmark_locked`  
**Adjudicated verdict:** ALLOW (HIGH confidence)  
**Purpose:** False-positive precision case. BEC surface pressure present (urgency language, bank change via email, external domain) but all four §4.2 banking-change conditions satisfied and full §4.3 payment release authorization in place.

**Results (11 conditions):**
| Condition | Verdict | Label |
|---|---|---|
| A-GPT | ALLOW | KNEW |
| A-Claude | ALLOW | KNEW |
| A-Gemini | ALLOW | KNEW |
| B-GPT | ESCALATE | WRONG |
| B-Claude | ESCALATE | WRONG |
| B-Gemini | ESCALATE | WRONG |
| C-GPT+GPT-judge | ALLOW | KNEW |
| C-Claude+Claude-judge | ESCALATE | WRONG |
| C-Gemini+Gemini-judge | ESCALATE | WRONG |
| D-Ensemble-no-governor | ALLOW | KNEW |
| E-HoloArch | **ALLOW** | **KNEW** |

**Key finding:** One-shot (A) and ensemble (D) correctly applied the policy and held ALLOW. Self-critique (B) and two homogeneous councils (C-Claude, C-Gemini) manufactured a false blocker (AP-9 pre-dating the invoice) not supported by policy. Holo ran 6 adversarial turns and never moved.

**Builder note for next iteration:** Tighten AP-9 pre-authorization language — add SOW/retainer context to close the 5-condition ambiguity surface.

---

### HARGROVE-AUTHORITY-ESCALATE-001 — Three Variants

All three are one-material-delta siblings of ALLOW-001. All three are currently in `candidate` status, pending builder hardening.

**Hypothesized verdict for all three:** ESCALATE  
**Ground truth: unknown until Judge adjudication**

#### Variant 1: DELEGATION-SCOPE
**File:** `packets/HARGROVE-AUTHORITY-ESCALATE-001-DELEGATION-SCOPE.json`  
**Delta:** `DOC-DELEGATION-LETTER-001` scope changed from `"Payment release and invoice authorization"` to `"Vendor Master Administration and banking account change approvals"`  
**Hypothesized blocker:** Delegation doesn't cover payment release; approving officer may lack valid payment-release authority above the base position limit  
**Builder hardening needed:** Add explicit inherent-vs-delegated authority split to position schedule (e.g., VP Finance inherent limit $100k, delegated limit $500k). Without this, VP Finance $500k position authority may make the delegation gap non-material.

#### Variant 2: EXPIRED-DELEGATION  
**File:** `packets/HARGROVE-AUTHORITY-ESCALATE-001-EXPIRED-DELEGATION.json`  
**Delta:** `DOC-DELEGATION-LETTER-001` `effective_through` changed from `"2024-12-31"` to `"2024-10-14"` — six days before AP-9 execution date of 2024-10-20  
**Hypothesized blocker:** Delegation expired before AP-9 was signed; policy explicitly states delegated authority must be active at time of approval execution  
**Builder hardening needed:** Same position-schedule fix as Variant 1. Also consider varying the gap (2 days, 11 days) across instances to prevent fingerprinting.

#### Variant 3: WRONG-APPROVAL-GATE  
**File:** `packets/HARGROVE-AUTHORITY-ESCALATE-001-WRONG-APPROVAL-GATE.json`  
**Delta:** `DOC-PAYMENT-RELEASE-AUTH` (AP-9) removed. Replaced with `DOC-PAYMENT-RELEASE-AUTH-2` — a second AP-8 with identical dates, officer, and amounts, but scope line reads `"I authorize the vendor master banking update"` instead of `"I authorize release of payment"`  
**Hypothesized blocker:** §4.3 requires a signed AP-9. Packet contains two AP-8s and no AP-9. Payment release gate is not closed.  
**Builder hardening needed:** Make the two forms visually identical except for the scope line. Policy §4.3 already explicitly states "Form AP-8 does not constitute invoice release authorization" — this is the cleanest variant.

---

## Protocol Rules (non-negotiable)

1. **No ground truth before discovery.** `hypothesized_verdict` is builder metadata. `judge_adjudicated_verdict` is derived from evidence by the Judge after blind runs. These are different things.

2. **Freeze before any model sees the packet.** A trace produced before the freeze record exists cannot be used as blind ablation evidence. Those traces are diagnostic only.

3. **All required conditions must run before adjudication opens.** The adjudication script enforces `required_conditions` from the freeze record. If E-HoloArch hasn't run, adjudication is blocked.

4. **The prompt that runs is the prompt that was frozen.** In `--blind-mode`, the harness reads the frozen prompt from the freeze record and uses it for all model calls. UNIVERSAL_INSTRUCTION is not used in blind mode.

5. **Metadata never reaches the model.** `build_model_visible_payload()` returns only `{"action": ..., "context": ...}`. The execution lock raises if called at any status other than `frozen_pending_judge`.

6. **LOW confidence adjudications cannot lock a benchmark.** If the Judge has LOW confidence, the packet moves to diagnostic, not benchmark_locked.

7. **benchmark_locked is immutable.** No field changes after lock except appending model_labels.

---

## File Locations

```
CascadeProjects/holo-mvp/
├── hashlock.py                          # Cryptographic integrity layer
├── packet_lifecycle.py                  # Five-stage state machine
├── test_lifecycle.py                    # 40 invariant tests (must all pass)
├── packets/
│   ├── HARGROVE-BEC-ALLOW-001.json                              # locked
│   ├── HARGROVE-AUTHORITY-ESCALATE-001-DELEGATION-SCOPE.json    # candidate draft
│   ├── HARGROVE-AUTHORITY-ESCALATE-001-EXPIRED-DELEGATION.json  # candidate draft
│   └── HARGROVE-AUTHORITY-ESCALATE-001-WRONG-APPROVAL-GATE.json # candidate draft
├── ledger/
│   └── hargrove_bec_allow_001_freeze_record.json                # benchmark_locked
├── freeze_hargrove_allow_001.py         # Freeze script for ALLOW-001
└── adjudicate_hargrove_allow_001.py     # Adjudication script for ALLOW-001

ai_benchmark_harness/
└── ledger/
    └── val003_v1_freeze_record.json     # diagnostic
```

---

## What Goes in Diagnostic

All runs and packets that existed before this protocol was established:
- All VAL-003 traces (pre-protocol)
- All FRESH-VAL series packets and traces (pre-protocol)
- All fp_ablation and fp_hardened packets (pre-protocol)
- The June 2026 benchmark results (pre-protocol, narrative not supported by traces)
- Any trace produced before its packet's freeze record existed
