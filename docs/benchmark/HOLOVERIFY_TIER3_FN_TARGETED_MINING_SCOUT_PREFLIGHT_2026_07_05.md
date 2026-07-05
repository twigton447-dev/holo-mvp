# HoloVerify Tier 3 FN Targeted Mining Scout Preflight

Callsign: MINER SUBAGENT

Status: `PASS_NO_PROVIDER_PREFLIGHT`

No providers, solo live, Holo live, Gov, or judges were run. Frozen runtime evidence was not edited.

## Runtime Manifest

- Path: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- SHA-256: `76bdfb90d03007038ee67b26e1b3939eefb43f122908d9635951d5294990edd2`
- Packet count: `20`
- Runtime row keys: `opaque_runtime_id`, `runtime_payload_ref`, `runtime_payload_sha256`
- Truth fields present: `false`
- Answer/scoring fields present: `false`

## Post-Hoc Scoring Map

- Path: `docs/benchmark/holoverify_tier3_fn_targeted_mining_scout_2026_07_05/holoverify_tier3_fn_targeted_mining_scout_scoring_map_2026_07_05.json`
- SHA-256: `b0d854409dd480f3cb28dc252d72cf4eb5075b13e7c648705bfae8019beb1315`
- Use rule: post-hoc only, after trace freeze

## Hashes

- Hash manifest: `docs/benchmark/holoverify_tier3_fn_targeted_mining_scout_2026_07_05/holoverify_tier3_fn_targeted_mining_scout_hash_manifest_2026_07_05.json`
- Hash manifest SHA-256: `30c84157a9ed89fddb1dbb449fb9a3fbca65833911f98802ec4bf6547b4992e7`
- Freeze root SHA-256: `12c20d6a48f9967428c46953b61a4e88273824183c7214f6a77f60e18088edf6`

## Validation

- JSON parses: `True`
- All packet IDs unique: `True`
- All pair IDs complete: `True`
- No hidden current-date/account-token/hazmat comparator: `true`
- Expected truth visible from model-visible sources: `True`
- Runtime manifest has no truth/answer/scoring fields: `True`
- Packet/key defects: `[]`

## Expected Future Solo Scout Calls

- Total: `60`
- `xai/grok-3-mini`: `20`
- `openai/gpt-5.4-mini`: `20`
- `minimax/MiniMax-M2.5-highspeed`: `20`

## Exact Future Solo-Scout Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 76bdfb90d03007038ee67b26e1b3939eefb43f122908d9635951d5294990edd2, and exactly 60 solo provider calls: xai/grok-3-mini x20, openai/gpt-5.4-mini x20, minimax/MiniMax-M2.5-highspeed x20. SOLO SCOUT ONLY for Tier 3 FN targeted mining across 10 sibling pairs / 20 packets; not Holo rescue, not public benchmark evidence, not a global FNR claim, and not FP precision evidence. No Holo, no Gov, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```
