#!/usr/bin/env python3
"""
trace_analyzer.py

Reverse-engineers the actual ground truth from ablation traces.

The benchmark does not score against a pre-labeled verdict.
It reads every condition's reasoning chain, determines what the evidence
actually supports, and classifies each condition as:

  KNEW      — correct verdict reached via correct reasoning chain
  LUCKY     — correct verdict reached via wrong or incomplete reasoning
  WRONG     — incorrect verdict
  CONFUSED  — internally contradictory reasoning (cites clearing evidence
               then escalates, or vice versa)

Usage:
  python trace_analyzer.py --run-dir artifacts/fp_ablation_tp/ENG-ABL-XXXXXXXX
  python trace_analyzer.py --run-dir artifacts/fp_ablation_tp/ENG-ABL-XXXXXXXX --verbose
  python trace_analyzer.py --all-runs artifacts/fp_ablation_tp/ --output-dir trace_analysis/
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
load_dotenv()

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from llm_adapters import AnthropicAdapter

# ---------------------------------------------------------------------------
# Analyzer system prompt
# ---------------------------------------------------------------------------

ANALYZER_SYSTEM = """\
You are a benchmark trace auditor. Your job is to reverse-engineer the actual
ground truth from a model's reasoning trace, and classify the quality of its
reasoning — independent of what the expected verdict label says.

You receive:
  1. The packet — the full set of documents and action under review
  2. The condition's trace — the model's full reasoning output
  3. The key evidence items — the documents that are actually material

Your job:

STEP 1 — DERIVE ACTUAL TRUTH
Read the packet documents. What does the evidence actually support?
Is there a genuine unresolved blocker? Or is the action clear to proceed?
Derive the actual correct verdict from first principles — ignore any
expected_verdict label.

STEP 2 — CLASSIFY THE TRACE
Did the condition reach the correct verdict? And did it get there via
the correct reasoning chain?

Classifications:
  KNEW     — Correct verdict. Reasoning chain traced the actual material gap
             or clearing evidence. Cited specific documents and fields.
             Could defend this verdict in front of a skeptic.
  LUCKY    — Correct verdict. But reasoning was surface-level, coincidental,
             or cited the wrong documents as the controlling factor. Got
             the right answer for the wrong reason.
  WRONG    — Incorrect verdict. Either missed a genuine blocker or escalated
             a clean transaction.
  CONFUSED — Internally contradictory. Cited evidence that supports one verdict
             but reached the other. Or acknowledged the correct resolution but
             escalated anyway (or vice versa).

STEP 3 — EXTRACT WHAT THEY CITED
List the specific documents and fields the condition actually relied on.

OUTPUT FORMAT (JSON only, no markdown):
{
  "actual_correct_verdict": "ALLOW" or "ESCALATE",
  "actual_correct_reasoning": "one sentence: what the evidence actually shows",
  "condition_verdict": "ALLOW" or "ESCALATE",
  "classification": "KNEW | LUCKY | WRONG | CONFUSED",
  "classification_confidence": "HIGH | MEDIUM | LOW",
  "reasoning_quality": "one sentence on the quality of this condition's reasoning",
  "documents_cited": ["doc_id or field reference actually cited in the trace"],
  "key_gap_identified": true or false,
  "key_gap_description": "what the actual controlling gap or clearing fact is",
  "what_they_missed": "if LUCKY or WRONG: what the correct reasoning required that they skipped",
  "lucky_reason": "if LUCKY: what they cited instead of the correct controlling fact"
}
"""


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

def _call(adapter, system: str, user: str, temperature: float = 0.2):
    start = time.time()
    try:
        raw, in_tok, out_tok = adapter.call(system, user, temperature=temperature)
        elapsed = int((time.time() - start) * 1000)
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```", 2)[1]
            if clean.startswith("json"):
                clean = clean[4:]
            clean = clean.rsplit("```", 1)[0].strip()
        try:
            return json.loads(clean), in_tok, out_tok, elapsed, None
        except json.JSONDecodeError:
            first = clean.find("{")
            last  = clean.rfind("}")
            if first != -1 and last > first:
                try:
                    return json.loads(clean[first:last+1]), in_tok, out_tok, elapsed, None
                except json.JSONDecodeError as e:
                    return None, in_tok, out_tok, elapsed, str(e)
        return None, in_tok, out_tok, elapsed, "no_json_found"
    except Exception as e:
        return None, 0, 0, int((time.time() - start)*1000), str(e)[:200]


# ---------------------------------------------------------------------------
# Read trace from condition directory
# ---------------------------------------------------------------------------

def _read_trace(condition_dir: Path) -> dict | None:
    raw_path = condition_dir / "raw_output.txt"
    if not raw_path.exists():
        return None
    try:
        content = raw_path.read_text()
        parsed = json.loads(content)
        return parsed
    except Exception:
        return {"raw_text": raw_path.read_text()[:8000]}


def _extract_reasoning_text(trace: dict) -> str:
    """Pull the most useful reasoning text from a trace for the analyzer."""
    if not trace:
        return ""

    parts = []

    # Top-level verdict and reasoning
    if trace.get("verdict"):
        parts.append(f"VERDICT: {trace['verdict']}")
    if trace.get("reasoning"):
        parts.append(f"REASONING: {trace['reasoning']}")

    # Turn log (Holo and multi-turn conditions)
    for turn in trace.get("turn_log", []):
        role    = turn.get("role", f"Turn {turn.get('turn_number','?')}")
        verdict = turn.get("verdict", "")
        reason  = turn.get("reasoning", "")
        findings = turn.get("findings", [])
        parts.append(f"\n--- {role} ({turn.get('provider','?')}) verdict={verdict} ---")
        if reason:
            parts.append(reason[:600])
        for f in findings[:4]:
            sev = f.get("severity","")
            cat = f.get("category","")
            det = f.get("detail","")[:200]
            ev  = f.get("evidence","")[:120]
            parts.append(f"  [{cat}:{sev}] {ev} | {det}")

    # Raw text fallback
    if not parts and trace.get("raw_text"):
        parts.append(trace["raw_text"][:3000])

    return "\n".join(parts)[:6000]


# ---------------------------------------------------------------------------
# Analyze one condition
# ---------------------------------------------------------------------------

def analyze_condition(condition_name: str, condition_dir: Path,
                      packet: dict, adapter) -> dict:
    trace = _read_trace(condition_dir)
    if trace is None:
        return {
            "condition": condition_name,
            "classification": "NO_TRACE",
            "error": "raw_output.txt not found",
        }

    reasoning_text = _extract_reasoning_text(trace)
    condition_verdict = trace.get("verdict", "UNCLEAR")

    # Build a compact packet summary — just action + documents
    packet_summary = {
        "action":    packet.get("action", {}),
        "documents": packet.get("context", {}).get("documents", []),
    }

    user_msg = (
        f"PACKET:\n{json.dumps(packet_summary, indent=2)}\n\n"
        f"CONDITION: {condition_name}\n"
        f"CONDITION VERDICT: {condition_verdict}\n\n"
        f"TRACE:\n{reasoning_text}\n\n"
        f"Classify this condition's reasoning. Return only the JSON object."
    )

    parsed, in_tok, out_tok, elapsed, error = _call(adapter, ANALYZER_SYSTEM, user_msg)

    if parsed:
        parsed["condition"]         = condition_name
        parsed["condition_verdict"] = condition_verdict
        parsed["elapsed_ms"]        = elapsed
        parsed["in_tok"]            = in_tok
        return parsed

    return {
        "condition":         condition_name,
        "condition_verdict": condition_verdict,
        "classification":    "ANALYSIS_FAILED",
        "error":             error or "parse_failed",
        "elapsed_ms":        elapsed,
    }


# ---------------------------------------------------------------------------
# Run analysis on one ablation run directory
# ---------------------------------------------------------------------------

CONDITION_ORDER = [
    "A-GPT", "A-Claude", "A-Gemini",
    "B-GPT", "B-Claude", "B-Gemini",
    "C-GPT+GPT-judge", "C-Claude+Claude-judge", "C-Gemini+Gemini-judge",
    "D-Ensemble-no-governor",
    "E-HoloArch",
]

def analyze_run(run_dir: Path, verbose: bool = False) -> dict:
    # Load packet from run manifest
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        print(f"  ERROR: no run_manifest.json in {run_dir}")
        return {}

    manifest = json.loads(manifest_path.read_text())
    packet_path = manifest.get("packet_path", "")
    try:
        packet = json.loads(Path(packet_path).read_text())
    except Exception:
        # Try results.json for packet echo
        results_path = run_dir / "results.json"
        if results_path.exists():
            results = json.loads(results_path.read_text())
            packet = results.get("packet", {})
        else:
            packet = {}

    scenario_id = manifest.get("scenario_id", run_dir.name)
    print(f"\n  Analyzing: {scenario_id}")

    adapter = AnthropicAdapter()

    # Find all condition directories
    condition_dirs = {
        d.name: d for d in run_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    }

    results = []

    # Run analysis in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(analyze_condition, name, cdir, packet, adapter): name
            for name, cdir in condition_dirs.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                results.append(result)
                cls  = result.get("classification", "?")
                verd = result.get("condition_verdict", "?")
                conf = result.get("classification_confidence", "?")
                mark = {"KNEW": "✓✓", "LUCKY": "~", "WRONG": "✗", "CONFUSED": "??",
                        "NO_TRACE": "--", "ANALYSIS_FAILED": "ERR"}.get(cls, "?")
                print(f"    {mark} {name:<35} {verd:<9} {cls:<10} [{conf}]")
                if verbose and result.get("what_they_missed"):
                    print(f"       missed: {result['what_they_missed'][:90]}")
                if verbose and result.get("lucky_reason"):
                    print(f"       lucky:  {result['lucky_reason'][:90]}")
            except Exception as e:
                results.append({"condition": name, "classification": "ANALYSIS_FAILED",
                                 "error": str(e)[:80]})

    # Sort by canonical order
    order_map = {c: i for i, c in enumerate(CONDITION_ORDER)}
    results.sort(key=lambda r: order_map.get(r.get("condition",""), 99))

    return {
        "scenario_id": scenario_id,
        "run_dir":     str(run_dir),
        "conditions":  results,
        "actual_correct_verdict": next(
            (r.get("actual_correct_verdict") for r in results if r.get("actual_correct_verdict")),
            "UNKNOWN"
        ),
    }


# ---------------------------------------------------------------------------
# Summary table
# ---------------------------------------------------------------------------

_CLS_SYMBOL = {
    "KNEW": "✓✓", "LUCKY": "~~", "WRONG": "✗✗",
    "CONFUSED": "??", "NO_TRACE": "--", "ANALYSIS_FAILED": "!!"
}

def print_summary(all_runs: list[dict]):
    print(f"\n{'='*90}")
    print(f"  TRACE ANALYSIS — BENCHMARK GROUND TRUTH")
    print(f"  Scoring: KNEW=correct+right-reason  LUCKY=correct+wrong-reason")
    print(f"           WRONG=incorrect  CONFUSED=contradictory")
    print(f"{'='*90}")

    # Header
    conds = CONDITION_ORDER
    header = f"  {'PACKET':<35}" + "".join(f" {c[-6:]:>8}" for c in conds)
    print(header)
    print(f"  {'-'*35}" + "".join(f" {'--------':>8}" for _ in conds))

    knew_counts  = {c: 0 for c in conds}
    lucky_counts = {c: 0 for c in conds}
    wrong_counts = {c: 0 for c in conds}

    for run in all_runs:
        sid = run.get("scenario_id", "?")[:33]
        cls_map = {r["condition"]: r.get("classification","?")
                   for r in run.get("conditions", [])}
        row = f"  {sid:<35}"
        for c in conds:
            cls = cls_map.get(c, "--")
            sym = _CLS_SYMBOL.get(cls, "??")
            row += f" {sym:>8}"
            if cls == "KNEW":  knew_counts[c]  += 1
            if cls == "LUCKY": lucky_counts[c] += 1
            if cls == "WRONG": wrong_counts[c] += 1
        print(row)

    n = len(all_runs)
    print(f"\n  {'KNEW':35}" + "".join(f" {knew_counts[c]:>8}" for c in conds))
    print(f"  {'LUCKY':35}" + "".join(f" {lucky_counts[c]:>8}" for c in conds))
    print(f"  {'WRONG':35}" + "".join(f" {wrong_counts[c]:>8}" for c in conds))
    print(f"\n  KNEW rate (/{n}):")
    print(f"  {'':35}" + "".join(f" {knew_counts[c]}/{n}".rjust(8) for c in conds))
    print(f"{'='*90}\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Trace analyzer — reverse-engineers ground truth")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir",   help="Single ablation run directory")
    group.add_argument("--all-runs",  help="Parent directory containing multiple run directories")
    parser.add_argument("--output-dir", default="trace_analysis")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.run_dir:
        run_dirs = [Path(args.run_dir)]
    else:
        run_dirs = sorted([
            d for d in Path(args.all_runs).iterdir()
            if d.is_dir() and d.name.startswith("ENG-ABL")
        ])
        if not run_dirs:
            print(f"No ENG-ABL-* directories found in {args.all_runs}")
            sys.exit(1)

    all_results = []
    for run_dir in run_dirs:
        result = analyze_run(run_dir, verbose=args.verbose)
        if result:
            all_results.append(result)
            out_path = output_dir / f"{result['scenario_id']}_trace_analysis.json"
            out_path.write_text(json.dumps(result, indent=2))

    if all_results:
        print_summary(all_results)
        summary_path = output_dir / "summary.json"
        summary_path.write_text(json.dumps(all_results, indent=2))
        print(f"  Full analysis saved: {output_dir}/")


if __name__ == "__main__":
    main()
