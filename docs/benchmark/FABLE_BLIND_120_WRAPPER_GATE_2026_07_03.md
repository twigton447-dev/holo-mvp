# Fable Blind 120 Live Wrapper Gate

Status: READ_ONLY_GATE_COMPLETE
Date: 2026-07-03
Reviewer: Fable. No providers, no judges, no Holo, no solo, no scoring, no edits. All verifications recomputed from frozen artifacts.

## VERDICT: `PASS` — wrapper gate cleared for the provider-approval request

This clears the wrapper and frozen bank only. Provider execution still requires Taylor's exact approval sentence; public claims remain frozen under the sequence lock.

## Bank verification (all recomputed, all match pins)

- Runtime manifest sha256 = `c3a2bbe2…` ✔; scoring map sha256 = `b5f3c219…` ✔.
- Freeze root `63cc81e5…` **independently recomputed** from the hash-manifest base (sha256 of sorted-key JSON minus the root field) ✔; all **122 file hashes verify byte-for-byte** (manifest, scoring map, 120 payloads).
- 120 unique opaque packets; truths exactly 60 ALLOW / 60 ESCALATE.
- Ordering: hash-sorted by opaque ID; odd/even truth positions both mixed; **0 adjacent sibling pairs** across 60 pairs.
- Runtime manifest keys truth-free (no bank_hash, seed material, salt, or scoring rows).
- Payload scan: **0 forbidden-term hits** (legacy IDs, HV-/BAL100, truth fields, knew_terms, allow_rule, esc_rule) across all 120 payloads; shape symmetric (mean bytes 2020 A vs 2014 E; 5 docs per payload both sides).
- Salt: `secrets.token_hex(32)` at build time, stored only in the scoring map; opaque = `BLIND120-sha256(salt|legacy)[:20]` — verified against a scoring row; not recomputable from runtime-visible data.
- **Zero packet overlap** with the 20-canary legacy set.

## Wrapper and scorer verification

- `run_holoverify_blind_120_live_2026_07_03.py` holds no scoring-map path; pins runtime-manifest, scoring-map, and freeze-root hashes; expected call count 600; the exact approval sentence embeds the full roster and call counts (W1 xai ×120, G1/G2/W3 minimax ×120 each, W2 openai ×120), so approval is scope-bound.
- Assurance fields now reference their enforcing tests by name (`SCORING_MAP_READ_GUARD_TEST`, `WRAPPER_SCORING_SPLIT_TEST`) — my M1 doc fix from the hardening review, implemented.
- `score_holoverify_blind_120_posthoc_2026_07_03.py` is a separate post-freeze scorer that fails on missing trace artifacts and binds the score to exact trace hashes.
- Tests: **51 passed, 0 skipped, 0 failed** in my environment (120 wrapper + canary wrapper + T1/T2/T5/T6 subset, with `git` stubbed for the known worktree artifact); full-suite green previously established.

## Watch items (non-blocking)

1. **Delegation pattern:** the 120 wrapper reuses the canary wrapper by overriding its module globals (`CANARY.EXPECTED_… = …`). Correct today and test-covered, but if the canary module ever reads one of those constants at import time instead of call time, an override silently no-ops. Any future edit to the canary wrapper must re-run the 120 wrapper tests — the CI pairing should be explicit.
2. **Attempt budget inheritance:** 1 content attempt / 1 live attempt per packet carries over; at 120 packets expect some fail-closed packets in the headline count rather than reruns — that is the design working, not a problem to fix mid-run.
3. **Standing residuals unchanged:** the 120 legacy packets descend from the same curated corpus (C4); blindness is proven, representativeness is not. The comparison memo after solo one-shots is where that gets addressed, per the sequence lock.

Next step per the lock: no-provider firewall tests against the frozen bank are green; the provider-approval request may go to Taylor with the exact sentence in the wrapper.
