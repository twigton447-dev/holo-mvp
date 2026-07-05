# Commerce OpenAI-W2 Full Run Transport Failure Autopsy

Classification: `COMMERCE_OPENAI_W2_FULL_RUN_TRANSPORT_FAILURE_AUTOPSY_NO_PROVIDER`

Run preserved:

`docs/benchmark/holoverify_agentic_commerce_replication_2026-06-29/holo_live_runs_openai_w2/run_20260630T032421Z`

## Result

The Commerce full-family Holo run stopped fail-closed at `122/200` expected provider calls.

This is not a Holo verdict failure and not a recurrence of the prior W3 truncation bug. The W3 hardening survived through the completed packets before the stop.

## Root Failure

| Field | Value |
| --- | --- |
| Turn | `HV-ACOM-REP-013-A_G1` |
| Packet | `HV-ACOM-REP-013-A` |
| Pair | `HV-ACOM-REP-013` |
| Call kind | `gov` |
| Provider | `minimax` |
| Model | `MiniMax-M2.5-highspeed` |
| Error | `URLError: <urlopen error [Errno 8] nodename nor servname provided, or not known>` |

The actual failure class is a provider transport / DNS-resolution failure.

## Reporting Bug

The summary wrapper checked `call_kind == gov` plus `parse_ok != true` before checking `provider_call_ok != true`.

That caused a failed MiniMax Gov transport call to be mislabeled as:

`GOV_CONTRACT_OR_TRUNCATION_FAILURE`

The corrected precedence is:

1. Provider call failure
2. Gov contract / truncation failure
3. Incomplete trace
4. Verdict or pair admissibility failure

## Transport Policy Gap

Transport retry policy V1 was present, but the DNS `URLError` text was not classified as retryable transport. The patch adds DNS-resolution markers including:

- `nodename nor servname provided`
- `name or service not known`
- `temporary failure in name resolution`
- `getaddrinfo failed`
- `errno 8`
- `gaierror`

Future matching failures are classified as:

`DNS_RESOLUTION_ERROR`

and are handled by the bounded transport retry path.

## Evidence Boundary

No providers were called during this autopsy. No judges, solo runs, Holo reruns, packet edits, prompt edits, trace edits, or raw output edits were performed.
