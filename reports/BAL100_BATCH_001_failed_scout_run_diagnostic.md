# BAL100 Batch 001 Failed Scout Run Diagnostic

Run: `BAL100-BATCH-001_five_mini_solo_scout_20260617T225401Z`

The 20260617T225401Z scout run is unusable for packet selection because all 80 attempts returned ERROR due to runner/provider dependency failures. It must not be used as collapse evidence, promotion evidence, repair evidence, or discard evidence.

Observed failure class:

```text
ModuleNotFoundError: No module named 'openai'      # OpenAI / xAI / MiniMax path
ModuleNotFoundError: No module named 'anthropic'
ModuleNotFoundError: No module named 'google'
```

Classification: scout-runner dependency failure, not packet collapse and not model behavior.

Benchmark credit: false.  
Official trace: false.  
Judge: false.  
Freeze: false.
