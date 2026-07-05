# HoloVerify Tier 3 FN Targeted Mining Scout 2 Preflight

Callsign: MINER SUBAGENT

Status: `PASS_NO_PROVIDER_PREFLIGHT`

No providers, solo live, Holo live, Gov, or judges were run. Frozen runtime evidence was not edited.

## Runtime Manifest

- Path: `docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT2_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json`
- SHA-256: `1c9b3b48fe25c36992509281c0f354229dbb5b9cc9f1fc8f965cca2df1f3ffb5`
- Packet count: `20`
- Runtime row keys: `opaque_runtime_id`, `runtime_payload_ref`, `runtime_payload_sha256`
- Truth fields present: `false`
- Answer/scoring fields present: `false`

## Post-Hoc Scoring Map

- Path: `docs/benchmark/holoverify_tier3_fn_targeted_mining_scout2_2026_07_05/holoverify_tier3_fn_targeted_mining_scout2_scoring_map_2026_07_05.json`
- SHA-256: `aaf0d72f69ac74b836d375f12a3104afd90c6485caff5f6360573d47d0ffb508`
- Use rule: post-hoc only, after trace freeze

## Hashes

- Hash manifest: `docs/benchmark/holoverify_tier3_fn_targeted_mining_scout2_2026_07_05/holoverify_tier3_fn_targeted_mining_scout2_hash_manifest_2026_07_05.json`
- Hash manifest SHA-256: `1a60ee4617e510ebc9330f40623308a2bfbb680aa9a4a0dda0e472142705098b`
- Freeze root SHA-256: `ee5edc76e2026e9e78d5c508d91b6a3c2edecdc71e99e902909aea38fb2e5168`

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
I approve live provider execution for HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT2_V0 using only runtime-only manifest docs/benchmark/HOLOVERIFY_TIER3_FN_TARGETED_MINING_SCOUT2_RUNTIME_MANIFEST_NO_TRUTH_2026_07_05.json with SHA-256 1c9b3b48fe25c36992509281c0f354229dbb5b9cc9f1fc8f965cca2df1f3ffb5, and exactly 60 solo provider calls: xai/grok-3-mini x20, openai/gpt-5.4-mini x20, minimax/MiniMax-M2.5-highspeed x20. SOLO SCOUT ONLY for Tier 3 FN targeted mining across 10 sibling pairs / 20 packets; not Holo rescue, not public benchmark evidence, not a global FNR claim, and not FP precision evidence. No Holo, no Gov, no judges, no scoring map before trace freeze, no mixed registration JSON before trace freeze, no substitutions, no public claims.
```
