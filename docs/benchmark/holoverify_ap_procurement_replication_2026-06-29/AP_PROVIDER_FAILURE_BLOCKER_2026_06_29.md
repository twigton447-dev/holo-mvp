# AP Replication Provider Failure Blocker

Classification: `AP_HOLO_BLOCKED_BY_REQUIRED_GEMINI_WORKER_503`

This AP/procurement replication lane is not a comparative result. The frozen packet bank preflight passes, but the full HoloVerify lane cannot currently complete because the required Worker 2 model, `google/gemini-2.5-flash-lite`, returned repeated provider-side HTTP 503 failures.

## Scope

- Family: `HV-AP-REP-2026-06-29`
- Freeze commit: `de22377be8175d04078ba6c70f1fd35222e9f572`
- Freeze root: `5340bdb9c9dbb359228fc3f627cf4b29bf0087d8f32dd4736460a21fef7cf9c7`
- AP preflight: `PASS`
- Judges: `0`
- Commerce/IT runs: `0`
- Solo baseline: `NOT_RUN`

## Preserved Invalid Attempts

| Run | Calls | Worker Calls | Gov Calls | Failure |
| --- | ---: | ---: | ---: | --- |
| `run_20260629T105111Z` | 133 | 80 | 53 | `google/gemini-2.5-flash-lite` 503 on `HV-AP-REP-014-A_W2` |
| `run_20260629T110920Z` | 43 | 26 | 17 | `google/gemini-2.5-flash-lite` 503 on `HV-AP-REP-005-A_W2` |
| `run_20260629T111600Z` | 28 | 17 | 11 | `google/gemini-2.5-flash-lite` 503 on `HV-AP-REP-003-B_W2` |

## Lock Roots

- `run_20260629T105111Z`: `6a39255165a0e71a112094377e5a56dc66d1111ecc1c48adf267069919821cc2`
- `run_20260629T110920Z`: `e0d4f7fe2e4d7a0376603b13cdd89b99bc5303e462a382af271a858db433d989`
- `run_20260629T111600Z`: `3a2ef6c9e7b0e682493d1390e69416c6a99750392e107f3f54268dabbdb4af50`

## Required Interpretation

- These runs are invalid provider-failure attempts.
- They do not provide AP Holo quality evidence.
- They do not authorize a solo comparison.
- No partial retry, fallback model, or substitution should be used for proof credit.
- The next valid proof step is a fresh full AP HoloVerify run after the required Gemini worker is stable enough to complete the lane.
