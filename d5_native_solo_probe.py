#!/usr/bin/env python3
"""
d5_native_solo_probe.py

Native one-shot solo baseline probe for Domain 5 (Regulated Procurement /
Government Acquisition, FAR/DFARS-applicable).

Definition:
  - One model
  - One prompt
  - One packet
  - One answer
  - No adversarial turns
  - No convergence loop
  - No persona rotation
  - No template category prompting

This is the true native solo baseline. Harness solos (run_solo in benchmark.py)
use the full analyst persona + template categories. This script is the raw
native baseline for architecture differentiation.

Usage:
  python d5_native_solo_probe.py private_materials_not_for_public_release/examples/scenarios/MOD-BGS-LTA-77A4-P00008.json
  python d5_native_solo_probe.py <path> --all-models
  python d5_native_solo_probe.py <path> --model openai
  python d5_native_solo_probe.py <path> --model anthropic
  python d5_native_solo_probe.py <path> --model google
  python d5_native_solo_probe.py <path> --verbose
"""

import argparse
import json
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

SYSTEM_PROMPT = """\
You are a contract compliance reviewer. Your task is to evaluate whether the \
submitted contract modification packet is ready for execution.

Review the packet carefully, including all clauses, supporting documentation, \
and the approval excerpt. Then respond with exactly one of:

  ALLOW    — the modification is compliant and can be executed
  ESCALATE — there are unresolved compliance issues that must be addressed before execution

Follow your verdict with a brief explanation (2-4 sentences) citing specific \
evidence from the packet.

Do not ask for more information. Make a determination based solely on what is \
in the submitted packet.\
"""


def _fmt_context(scenario: dict) -> str:
    """Format scenario context as readable text for the model."""
    ctx = scenario.get("context", {})
    lines = [
        "CONTRACT MODIFICATION APPROVAL PACKET",
        "",
        f"Program      : {ctx.get('program', 'N/A')}",
        f"Request ID   : {ctx.get('request_id', 'N/A')}",
        f"Summary      : {ctx.get('summary', 'N/A')}",
        "",
        "--- SUBMITTED PACKET ---",
        "",
        json.dumps(ctx, indent=2),
    ]
    return "\n".join(lines)


def _extract_verdict(text: str) -> str:
    text_up = text.upper()
    if re.search(r"\bESCALATE\b", text_up):
        return "ESCALATE"
    if re.search(r"\bALLOW\b", text_up):
        return "ALLOW"
    return "UNCLEAR"


def probe_openai(context_text: str) -> dict:
    from openai import OpenAI
    client   = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model_id = os.getenv("OPENAI_MODEL", "gpt-5.4")
    start    = time.time()
    response = client.chat.completions.create(
        model                 = model_id,
        temperature           = 0.1,
        max_completion_tokens = 512,
        messages              = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": context_text},
        ],
    )
    elapsed = int((time.time() - start) * 1000)
    text    = response.choices[0].message.content or ""
    return {
        "model":   model_id,
        "verdict": _extract_verdict(text),
        "text":    text.strip(),
        "in_tok":  response.usage.prompt_tokens,
        "out_tok": response.usage.completion_tokens,
        "ms":      elapsed,
    }


def probe_anthropic(context_text: str) -> dict:
    import anthropic
    client   = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    model_id = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    start    = time.time()
    response = client.messages.create(
        model       = model_id,
        temperature = 0.1,
        max_tokens  = 512,
        system      = SYSTEM_PROMPT,
        messages    = [{"role": "user", "content": context_text}],
    )
    elapsed = int((time.time() - start) * 1000)
    text    = response.content[0].text if response.content else ""
    return {
        "model":   model_id,
        "verdict": _extract_verdict(text),
        "text":    text.strip(),
        "in_tok":  response.usage.input_tokens,
        "out_tok": response.usage.output_tokens,
        "ms":      elapsed,
    }


def probe_google(context_text: str) -> dict:
    from google import genai
    from google.genai import types
    client   = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"), http_options={"timeout": 60000})
    model_id = str(os.getenv("GOOGLE_MODEL") or "gemini-2.5-pro")
    combined = f"{SYSTEM_PROMPT}\n\n---\n\n{context_text}"
    start    = time.time()
    response = client.models.generate_content(
        model    = model_id,
        contents = combined,
        config   = types.GenerateContentConfig(
            temperature       = 0.1,
            max_output_tokens = 8000,
        ),
    )
    elapsed = int((time.time() - start) * 1000)
    text = response.text
    if text is None:
        try:
            parts = response.candidates[0].content.parts
            text  = " ".join(p.text for p in parts if hasattr(p, "text") and p.text)
        except Exception:
            text = ""
    text = text or ""
    try:
        in_tok  = response.usage_metadata.prompt_token_count
        out_tok = response.usage_metadata.candidates_token_count
    except Exception:
        in_tok, out_tok = 0, 0
    return {
        "model":   model_id,
        "verdict": _extract_verdict(text),
        "text":    text.strip(),
        "in_tok":  int(in_tok or 0),
        "out_tok": int(out_tok or 0),
        "ms":      elapsed,
    }


PROBERS = {
    "openai":    probe_openai,
    "anthropic": probe_anthropic,
    "google":    probe_google,
}


def main():
    parser = argparse.ArgumentParser(
        description="Native one-shot solo baseline probe — Domain 5 Procurement."
    )
    parser.add_argument("scenario", help="Path to scenario JSON")
    parser.add_argument("--model", choices=["openai", "anthropic", "google"],
                        help="Run a single model only")
    parser.add_argument("--all-models", action="store_true",
                        help="Run all three models (default when --model omitted)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print full model response text")
    args = parser.parse_args()

    path        = Path(args.scenario)
    scenario    = json.loads(path.read_text())
    scenario_id = scenario.get("scenario_id", path.stem)
    expected    = scenario.get("expected_verdict", "UNKNOWN").upper()
    ctx_text    = _fmt_context(scenario)

    models_to_run = [args.model] if args.model else list(PROBERS.keys())

    print(f"\n{'='*64}")
    print(f"  NATIVE ONE-SHOT PROBE (DOMAIN 5): {scenario_id}")
    print(f"  Expected : {expected}")
    print(f"  Prompt   : contract compliance reviewer — no personas, no categories")
    print(f"  Turns    : 1 per model")
    print(f"{'='*64}\n")

    results = {}
    for provider in models_to_run:
        probe_fn = PROBERS[provider]
        print(f"  [{provider.upper()}] calling {provider}...", end="", flush=True)
        try:
            r = probe_fn(ctx_text)
        except Exception as e:
            print(f"  ERROR: {e}")
            results[provider] = {"verdict": "ERROR", "error": str(e)}
            continue
        correct     = "✓" if r["verdict"] == expected else "✗"
        model_label = str(r.get("model") or provider)
        verdict_str = str(r.get("verdict") or "UNCLEAR")
        in_tok_n    = int(r.get("in_tok") or 0)
        out_tok_n   = int(r.get("out_tok") or 0)
        ms_n        = int(r.get("ms") or 0)
        print(f"\r  [{provider.upper():<10}] {model_label:<32} "
              f"-> [{verdict_str:<8}] {correct}  {ms_n}ms  "
              f"{in_tok_n:,}+{out_tok_n:,} tok")
        if args.verbose:
            print(f"\n  --- Response ---\n    "
                  + r["text"].replace("\n", "\n    ") + "\n")
        results[provider] = r

    print(f"\n{'='*64}")
    print(f"  SUMMARY — NATIVE ONE-SHOT vs EXPECTED ({expected})")
    print(f"{'='*64}")
    for provider, r in results.items():
        v       = r.get("verdict", "ERROR")
        correct = "✓" if v == expected else "✗"
        print(f"  {provider:<12} [{v:<8}]  {correct}")
    print(f"{'='*64}\n")

    print("  run_mode : native_solo")
    print("  Label    : NATIVE ONE-SHOT SOLO — no harness, no personas, no template categories")
    print("  Scoring  : verdict only — reason-correctness NOT scored (no category scaffold)")
    print("  Compare against domain_guided_solo (harness) and holo_orchestrated for")
    print("  architecture differentiation and ablation analysis.")
    print()


if __name__ == "__main__":
    main()
