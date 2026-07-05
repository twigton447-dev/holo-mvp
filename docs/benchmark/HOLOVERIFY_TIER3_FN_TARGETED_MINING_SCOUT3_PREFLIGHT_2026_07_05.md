# HoloVerify Tier 3 FN Targeted Mining Scout 3 Preflight

Callsign: MINER SUBAGENT

Status: `PASS_NO_PROVIDER_PREFLIGHT`

No providers, solo live, Holo live, Gov, or judges were run. Frozen runtime evidence was not edited.

## Runtime Manifest

- Path: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT3_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- SHA-256: `7853a789c17b20fd911dc5107ffb9e2a8c50926c19cf4ca014073a6d4dc5946f`
- Packet count: `20`
- Runtime row keys: `opaque_runtime_id`, `runtime_payload_ref`, `runtime_payload_sha256`
- Truth fields present: `false`
- Answer/scoring fields present: `false`

## Post-Hoc Scoring Map

- Path: `docs/benchmark/holoverify_tier3_fn_targeted_mining_scout3_2026_07_05/holoverify_tier3_fn_targeted_mining_scout3_scoring_map_2026_07_05.json`
- SHA-256: `6e2674f848507454e443dbb2f58386c7e884ac3d93ce76acee50d9181ff08f3e`
- Use rule: post-hoc only, after trace freeze

## Hashes

- Hash manifest: `docs/benchmark/holoverify_tier3_fn_targeted_mining_scout3_2026_07_05/holoverify_tier3_fn_targeted_mining_scout3_hash_manifest_2026_07_05.json`
- Hash manifest SHA-256: `0e7a1f78d8c3ea7724abd1e45bd73199cda15f4b26a4ced708511e5ce62fbfa7`
- Freeze root SHA-256: `f81d059f74383af57927b01cbb63b1c9c8894a15fa584834a97004e8bf964325`

## Validation

- JSON parses: `true`
- All packet IDs unique: `true`
- All pair IDs complete: `true`
- Truth mix: `ALLOW=10`, `ESCALATE=10`
- No hidden current-date/account-token/hazmat/valid-value comparator: `true`
- Expected truth visible from model-visible sources: `true`
- Runtime manifest has no truth/answer/scoring fields: `true`
- Runtime payload leakage hits empty: `true`
- Packet/key defects: `[]`

## Expected Future Solo Scout Calls

- Total: `60`
- `xai/grok-3-mini`: `20`
- `openai/gpt-5.4-mini`: `20`
- `minimax/MiniMax-M2.5-highspeed`: `20`

## Exact Future Solo-Scout Approval Sentence

```text
I approve live provider execution for HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT3_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT3_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 7853a789c17b20fd911dc5107ffb9e2a8c50926c19cf4ca014073a6d4dc5946f, and exactly 60 solo provider calls: xai/grok-3-mini x20, openai/gpt-5.4-mini x20, minimax/MiniMax-M2.5-highspeed x20. SOLO SCOUT ONLY for Tier 3 FN targeted mining across 10 sibling pairs / 20 packets; not Holo rescue, not public benchmark evidence, not a global FNR claim, and not FP precision evidence. No Holo, no Gov, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```
