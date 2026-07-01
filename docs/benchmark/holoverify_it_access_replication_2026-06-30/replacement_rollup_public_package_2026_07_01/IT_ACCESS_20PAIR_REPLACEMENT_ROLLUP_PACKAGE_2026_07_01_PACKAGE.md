# IT Access 20-Pair Rollup Package With 015R1 Replacement

Date: 2026-07-01

Classification: `IT_ACCESS_20PAIR_REPLACEMENT_ROLLUP_PACKAGE`

Provider calls during package build: `0`

## Result

- Packets counted: `40`
- Sibling pairs counted: `20`
- Holo correct packets: `40/40`
- Holo valid pairs: `20/20`
- FPR: `0/20`
- FNR: `0/20`
- TPR: `20/20`
- TNR: `20/20`

## Source Calls

- Source provider calls: `210`
- Worker calls: `126`
- Gov calls: `84`
- Solo calls: `0`
- Judge calls: `0`
- Total tokens: `463294`

## Model Roster

- Holo unique models: `xai/grok-3-mini, openai/gpt-5.4-mini, minimax/MiniMax-M2.5-highspeed`
- Holo Gov model: `minimax/MiniMax-M2.5-highspeed`
- Gov selects models: `False`
- Solo comparison status: `same_packet_bank_seam_triage_not_exact_roster_matched`
- Solo models cited for comparison: `xai/grok-3-mini, openai/gpt-4o-mini, minimax/MiniMax-M2.5-highspeed`
- Roster-match note: Two model slots match Holo exactly; the OpenAI solo triage slot used gpt-4o-mini while the Holo W2 slot used gpt-5.4-mini. Do not describe this triage row as an exact same-three-model comparison.

## Source Lock Roots

- `6c40d63f080a752660735179b3c0d7e4b66c471ace36b2c4b03cb0f60497f26d`
- `1d0f268497ed5835623e764bfd49af085e26c3ac36d67f06ed4ad29ebad88db4`
- `2b81bae7a0f4c6d594f9a4ee92a80946fda9f73edf57d78233e63ea32afc95bd`
- `625e7fccccaabeda618878a421746fb926008012f9ed81528e278eec25382d63`

## Caveats

- This is a rollup package, not a single uninterrupted family run.
- Original pair HV-ITAC-REP-015 is not counted; it is preserved as retired/quarantined evidence.
- Replacement pair HV-ITAC-REP-015R1 is counted and has its own locked source run.
- The package source calls include the retired 015 attempt because the valid 016-020 rows share the same locked batch-3 container.
- No judges were run for this package.
- Solo comparison should cite the separate solo triage result and disclose it was run before 015 was retired.
- The IT solo triage model roster is not an exact same-three-model comparison to Holo: xAI and MiniMax match Holo, but the OpenAI solo triage model was gpt-4o-mini while the Holo W2 batch roster used gpt-5.4-mini.

## Claim Boundary

IT is public-package-ready as a disclosed replacement rollup: counted rows solve 40/40 packets and 20/20 sibling pairs, while retired pair 015 remains preserved and excluded.
