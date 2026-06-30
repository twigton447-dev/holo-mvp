# AP Solo One-Shot Baseline

Classification: `AP_SOLO_ONE_SHOT_3MINI_COMPLETE`
Provider calls: `120` / `120`
Gov calls: `0`
Judge calls: `0`
Tokens: `65347` input / `59167` output / `146061` total
Solo KNEW/admissible total: `53`

## Model Results

| Model | Calls | Correct verdict | KNEW/admissible | Wrong verdict | Structural/evidence fail | Parse fail | Provider fail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `xai/grok-3-mini` | 40 | 35 | 7 | 5 | 28 | 0 | 0 |
| `openai/gpt-5.4-mini` | 40 | 36 | 30 | 4 | 6 | 0 | 0 |
| `minimax/MiniMax-M2.5-highspeed` | 40 | 23 | 16 | 0 | 7 | 17 | 0 |
