# One-Packet Blind Canary Summary Correction

Classification: `VALID_ONE_PACKET_RUNTIME_FIREWALL_PASS_WITH_SUMMARY_FLAG_BUG`

The one-packet blind canary run at `run_20260702T235724Z` is preserved exactly
as emitted. The generated `blind_canary_live_summary.json` contains one known
summary bug: `passed_runtime_firewall=false` because the pass condition compared
the observed provider rows against the full 20-packet constant `100` instead of
the scoped one-packet expected count `5`.

The underlying run evidence is clean:

- Packet limit: `1`
- Expected provider calls: `5`
- Observed provider calls: `5`
- Provider failures: `0`
- TRACE_CALLS rows: `5`
- TRACE_PROVIDER_CALLS rows: `5`
- Final verdict valid: `true`
- Final verdict: `ESCALATE`
- Post-hoc truth: `ESCALATE`
- Post-hoc correct count: `1`
- Post-hoc incorrect count: `0`
- Trace frozen before scoring: `true`
- Solo calls: `0`
- Judge calls: `0`

This licenses only a narrow statement: the hardened blind runtime path completed
one opaque packet with the locked five-call roster and no answer-key channel
detected by the current firewall. It does not license an error-rate claim,
benchmark claim, or architecture-advantage claim.

The wrapper has been patched so future scoped runs compare provider rows against
the scoped `expected_call_count`, not the full-bank constant.
