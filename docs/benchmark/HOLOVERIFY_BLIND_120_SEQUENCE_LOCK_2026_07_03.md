# HoloVerify Blind 120 Sequence Lock

Status: `PRE_PROVIDER_SEQUENCE_LOCK`

Created: `2026-07-03T00:57:21Z`

Provider calls made by this lock: `0`

Judge calls made by this lock: `0`

## Approved Order

Taylor approved this order:

1. Get Fable to review the hardening patch.
2. Build/freeze the 120-packet blind runtime bank.
3. Run no-provider firewall tests.
4. Run Holo blind 120.
5. Score post-freeze.
6. Run solo one-shots on the same 120.
7. Build comparison memo.
8. Run randomized ablation subset.
9. Only then update public claims.

## Gate Law

No step may start until the previous step passes and is file-backed.

No providers may run until:

- Fable clears the hardening patch or requested fixes are applied;
- the 120-packet blind bank is built/frozen;
- no-provider firewall tests pass;
- Taylor explicitly approves the exact provider scope.

No public claim may be updated until:

- Holo blind 120 is complete and post-freeze scored;
- solo one-shots on the same 120 are complete and scored;
- comparison memo is built;
- randomized ablation subset is complete, or a file-backed ablation deferral
  memo exists with the reason, owner, and effect on the public claim boundary;
- claim language is rewritten under the new evidence boundary.

## 120-Packet Blind Bank Requirements

The next bank must be:

- 120 opaque runtime packets;
- 60 ALLOW truths;
- 60 ESCALATE truths;
- multi-domain;
- no legacy packet IDs in model-visible prompts;
- no suffix answer channels;
- runtime manifest separate from scoring map;
- scoring map unavailable to the live wrapper;
- randomized opaque order;
- frozen packet/prompt hashes;
- trace-hash-bound post-hoc score.
- future rollup builders must recompute score-artifact trace hashes before
  including any row.

## Holo 120 Runtime Requirements

Holo blind 120 must use:

- exact model roster declared before run;
- fixed call sequence;
- no model substitutions;
- no solo;
- no judges;
- no scoring before trace freeze;
- declared attempt budget;
- content/schema failures fail closed;
- invalid attempts preserved;
- provider transport retries logged separately and bounded.

## Solo One-Shot Requirements

Solo one-shots must use:

- same 120 frozen packets;
- same model families as Holo;
- one call per packet per model;
- no Gov;
- no Holo state brief;
- no artifact registry;
- no deterministic rescue;
- no final selector;
- scoring after output freeze.

Solo outcome classes:

- `KNEW`: correct verdict plus admissible source-grounded evidence.
- `WRONG_VERDICT`: parsed but wrong ALLOW/ESCALATE.
- `PARSE_FAILURE`: output cannot be parsed under the declared contract.
- `EVIDENCE_FAILURE`: verdict may be right but source proof is missing,
  invented, or invalid.
- `RUNTIME_FAILURE`: provider/transport/runtime issue under the pre-declared
  policy.

## Randomized Ablation Requirements

Ablation comes after Holo and solo baselines.

Use a pre-registered randomized subset, likely 30-40 packets balanced by:

- truth label;
- domain;
- difficulty/failure class where available.

Candidate arms:

- full Holo;
- no real Gov calls / static baton only;
- no deterministic gate after worker;
- no final selector / best artifact preservation;
- no Gov sandwich / state brief only;
- solo multi-call budget-parity diagnostic.

The ablation objective is component attribution, not public headline scoring.
If ablation is deferred before a public update, the deferral must be explicit,
file-backed, and must state which claims are weakened or forbidden by the
deferral.
