# Agentic Commerce 20-Pair Consolidated Public Package

Date: 2026-07-01

Classification: `COMMERCE_20PAIR_CONSOLIDATED_PUBLIC_PACKAGE`

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

- Source provider calls: `200`
- Worker calls: `120`
- Gov calls: `80`
- Solo calls: `0`
- Judge calls: `0`
- Total tokens: `424236`

## Model Roster

- Holo unique models: `xai/grok-3-mini, openai/gpt-5.4-mini, minimax/MiniMax-M2.5-highspeed`
- Holo Gov model: `minimax/MiniMax-M2.5-highspeed`
- Gov selects models: `False`
- Solo comparison status: `same_packet_bank_seam_triage_not_exact_roster_matched`
- Solo models cited for comparison: `xai/grok-3-mini, openai/gpt-4o-mini, minimax/MiniMax-M2.5-highspeed`
- Roster-match note: Two model slots match Holo exactly; the OpenAI solo triage slot used gpt-4o-mini while the Holo W2 slot used gpt-5.4-mini. Do not describe this triage row as an exact same-three-model comparison.

## Source Lock Roots

- `95c5033ed9d6b5b3fd481fc539e956ecab2bf61e8565002f05c1ba310ec734b6`
- `37c6cef4af7467d93e007edff327ecd3ad9b5bfc47414f4403c7b6d0f18b91a5`
- `ab10e5d5db4c7c4d9b252489258fc3fc669b2759c3e7c9173b84bfb46880f71d`

## Caveats

- This is a consolidated package over three locked batch runs, not one uninterrupted 200-call run.
- No judges were run for this package.
- Solo comparison should cite the separate solo triage result and disclose the model roster difference: xAI and MiniMax match Holo, but the OpenAI solo triage model was gpt-4o-mini while the Holo W2 batch roster used gpt-5.4-mini.

## Claim Boundary

Commerce is now public-package-ready as a consolidated locked batch family: 40/40 packets and 20/20 sibling pairs solved by HoloVerify, with the batch structure disclosed.
