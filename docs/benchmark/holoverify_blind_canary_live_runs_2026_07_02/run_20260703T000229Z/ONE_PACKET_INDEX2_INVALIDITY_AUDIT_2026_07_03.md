# One-Packet Index 2 Invalidity Audit

Classification: `INVALID_ONE_PACKET_CONTENT_FAILURE_W3_LENGTH_WITH_RETRY_BOUNDARY_BUG`

The second one-packet blind canary is preserved but invalid for scoring.

It made exactly `5/5` provider calls with the intended slot sequence. W1, G1, W2, and G2 returned contract-shaped output. W3 started with valid `worker_role=W3`, `verification_verdict=ALLOW`, and `binding_class=SOURCE_BOUNDARY_CLOSED`, but MiniMax ended with `finish_reason=length` before completing the required schema.

A runner bug then retried that content failure as though it were transport, producing the misleading outer failure `slot_message_mismatch:W1`. That retry boundary has to be patched before any rerun.

This run is not a Holo score, not a model verdict failure, and not a public claim.

Required patch before rerun:

- non-retryable content/schema failures must bypass transport retry;
- W3 final compiler output budget must be larger than `1024`;
- rerun one packet only after no-provider tests pass.
