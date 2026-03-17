"""
benchmark.py — Holo five-condition competitor variant benchmark.

Conditions:
  1. SOLO ONE-PASS: 1 model, 1 turn, no challenge
  2. SOLO MULTI-PASS: same model, same turns as Holo, hostile self-critique
  3. PARALLEL SIGN-OFF: 3 models in isolation, majority vote
  4. SEQUENTIAL CHAIN: 3 models in sequence, no adversarial framing, no governor
  5. HOLO FULL ARCHITECTURE: 3 models + governor, shared state, adversarial roles

Usage:
  python benchmark.py examples/scenarios/03_subtle_bec.json
  python benchmark.py examples/scenarios/03_subtle_bec.json --save
  python benchmark.py --all --save
"""

import argparse
import json
import logging
import os
import sys
import time
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.WARNING,
                    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("holo.benchmark")

# ── Imports from our engine files ──────────────────────────────────────────
from llm_adapters import (
    BEC_CATEGORIES,
    OpenAIAdapter,
    AnthropicAdapter,
    GoogleAdapter,
    get_role_for_turn,
)
from context_governor import ContextGovernor

# ── Local copies of the coverage helpers so benchmark is self-contained ────
SEVERITY_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

def _init_cov():
    return {cat: {"addressed": False, "max_severity": "NONE"} for cat in BEC_CATEGORIES}

def _update_cov(matrix, flags):
    updated = deepcopy(matrix)
    delta = 0
    for cat in BEC_CATEGORIES:
        new_sev = flags.get(cat, "NONE")
        if new_sev == "NONE":
            continue
        if not updated[cat]["addressed"]:
            updated[cat]["addressed"] = True
            updated[cat]["max_severity"] = new_sev
            delta += 1
        else:
            if SEVERITY_RANK[new_sev] > SEVERITY_RANK[updated[cat]["max_severity"]]:
                updated[cat]["max_severity"] = new_sev
                delta += 1
    return updated, delta

def _any_high(matrix):
    return any(v["max_severity"] == "HIGH" for v in matrix.values())

def _sev_rank(s):
    return SEVERITY_RANK.get(s, 0)

# ── Solo model config ───────────────────────────────────────────────────────
SOLO_FAMILY = os.getenv("BENCHMARK_SOLO_MODEL", "openai").lower()

def _solo_adapter():
    if SOLO_FAMILY == "anthropic": return AnthropicAdapter()
    if SOLO_FAMILY == "google":    return GoogleAdapter()
    return OpenAIAdapter()

def _all_adapters():
    return {"openai": OpenAIAdapter(), "anthropic": AnthropicAdapter(), "google": GoogleAdapter()}

def _empty_state(scenario):
    return {
        "evaluation_id": "benchmark",
        "action":        scenario.get("action", {}),
        "context":       scenario.get("context", {}),
        "turn_history":  [],
        "coverage_matrix": {},
    }

def _ms(start): return int((time.time() - start) * 1000)

def _ok(condition, model, turns, verdict, flags, reasoning, findings, turn_log, elapsed, in_tok, out_tok, extra=None):
    d = {"condition": condition, "model": model, "turns_run": turns,
         "verdict": verdict, "severity_flags": flags, "reasoning": reasoning,
         "findings": findings, "turn_log": turn_log, "elapsed_ms": elapsed,
         "total_tokens": {"input": in_tok, "output": out_tok}, "error": None}
    if extra: d["extra"] = extra
    return d

def _err(condition, model, exc, elapsed):
    return {"condition": condition, "model": model, "turns_run": 0,
            "verdict": "ERROR", "severity_flags": {cat: "NONE" for cat in BEC_CATEGORIES},
            "reasoning": str(exc), "findings": [], "turn_log": [], "elapsed_ms": elapsed,
            "total_tokens": {"input": 0, "output": 0}, "error": str(exc)}

def _sf(cond, cat):
    if cond.get("error"): return "ERR"
    return cond.get("severity_flags", {}).get(cat, "NONE")

# ──────────────────────────────────────────────────────────────────────────
# CONDITION 1 — Solo One-Pass
# ──────────────────────────────────────────────────────────────────────────
def run_solo_one_pass(scenario):
    adapter = _solo_adapter()
    state   = _empty_state(scenario)
    start   = time.time()
    try:
        r = adapter.run_turn(state, turn_number=1, role="Initial Assessment")
        return _ok("solo_one_pass", f"{adapter.provider}/{adapter.model_id}", 1,
                   r.verdict, r.severity_flags, r.reasoning, r.findings,
                   [r.to_dict()], _ms(start), r.input_tokens, r.output_tokens)
    except Exception as e:
        return _err("solo_one_pass", f"{adapter.provider}/{adapter.model_id}", e, _ms(start))

# ──────────────────────────────────────────────────────────────────────────
# CONDITION 2 — Solo Multi-Pass Self-Critique
# ──────────────────────────────────────────────────────────────────────────
def run_solo_multi_pass(scenario, match_turns):
    """
    Same single model. Same adversarial role prompts. Same turn count as Holo.
    Each turn it re-reads ALL its own prior output and is told to challenge it.
    Only thing absent: structural independence.
    """
    adapter  = _solo_adapter()
    state    = _empty_state(scenario)
    coverage = _init_cov()
    turn_log = []
    in_tok = out_tok = 0
    final_verdict = "ESCALATE"
    final_reasoning = ""
    start = time.time()

    for turn_number in range(1, match_turns + 1):
        role = "Synthesis" if turn_number == match_turns else get_role_for_turn(turn_number)
        try:
            r = adapter.run_turn(state, turn_number, role)
            state["turn_history"].append(r.to_dict())   # same model reads own output next turn
            coverage, _ = _update_cov(coverage, r.severity_flags)
            turn_log.append(r.to_dict())
            in_tok += r.input_tokens; out_tok += r.output_tokens
            final_verdict = r.verdict; final_reasoning = r.reasoning
        except Exception as e:
            return _err("solo_multi_pass", f"{adapter.provider}/{adapter.model_id}",
                        Exception(f"Turn {turn_number}: {e}"), _ms(start))

    if _any_high(coverage): final_verdict = "ESCALATE"
    flags = {cat: coverage[cat]["max_severity"] for cat in coverage}
    return _ok("solo_multi_pass", f"{adapter.provider}/{adapter.model_id}",
               match_turns, final_verdict, flags, final_reasoning,
               turn_log[-1].get("findings", []) if turn_log else [],
               turn_log, _ms(start), in_tok, out_tok)

# ──────────────────────────────────────────────────────────────────────────
# CONDITION 3 — Parallel Multi-LLM Sign-Off
# ──────────────────────────────────────────────────────────────────────────
def run_parallel_signoff(scenario, adapters):
    """
    3 frontier models evaluate in complete isolation. No shared context.
    Verdict is majority vote. Critical findings can die 2-1.
    """
    providers = ["openai", "anthropic", "google"]
    results = {}
    in_tok = out_tok = 0
    start = time.time()

    for p in providers:
        fresh = _empty_state(scenario)   # each model gets a clean empty state
        try:
            r = adapters[p].run_turn(fresh, turn_number=1, role="Initial Assessment")
            results[p] = r
            in_tok += r.input_tokens; out_tok += r.output_tokens
        except Exception as e:
            logger.error(f"Parallel {p} failed: {e}")
            results[p] = None

    verdicts    = [r.verdict for r in results.values() if r]
    escalate_ct = verdicts.count("ESCALATE")
    allow_ct    = verdicts.count("ALLOW")
    majority    = "ESCALATE" if escalate_ct >= allow_ct else "ALLOW"

    # Merged flags: most charitable — take MAX severity any model flagged
    merged = {cat: "NONE" for cat in BEC_CATEGORIES}
    for r in results.values():
        if not r: continue
        for cat in BEC_CATEGORIES:
            if _sev_rank(r.severity_flags.get(cat,"NONE")) > _sev_rank(merged[cat]):
                merged[cat] = r.severity_flags[cat]

    if any(_sev_rank(v) == 3 for v in merged.values()):
        majority = "ESCALATE"

    turn_log = []
    for i, p in enumerate(providers):
        r = results.get(p)
        if r:
            d = r.to_dict(); d["turn_number"] = i+1; d["note"] = "parallel_isolated"
            turn_log.append(d)

    vote_note = (f"Vote: {escalate_ct}x ESCALATE / {allow_ct}x ALLOW. " +
                 ", ".join(f"{p}={results[p].verdict if results[p] else 'ERROR'}" for p in providers))

    return _ok("parallel_signoff", "openai+anthropic+google (isolated, majority vote)",
               len([r for r in results.values() if r]), majority, merged, vote_note,
               [], turn_log, _ms(start), in_tok, out_tok,
               extra={"individual_verdicts": {p: (results[p].verdict if results[p] else "ERROR") for p in providers}})

# ──────────────────────────────────────────────────────────────────────────
# CONDITION 4 — Sequential Chain, No Governor
# ──────────────────────────────────────────────────────────────────────────
def run_sequential_chain(scenario, adapters, match_turns):
    """
    3 models in sequence. Each reads prior output. No adversarial framing.
    No Context Governor. No convergence detection.
    Models tend to defer to prior confident framing — not challenge it.
    """
    state    = _empty_state(scenario)
    coverage = _init_cov()
    turn_log = []
    in_tok = out_tok = 0
    final_verdict = "ESCALATE"
    final_reasoning = ""
    provider_cycle = ["openai", "anthropic", "google"]
    start = time.time()

    for turn_number in range(1, match_turns + 1):
        p = provider_cycle[(turn_number - 1) % 3]
        # No adversarial role — just "Initial Assessment" every turn.
        # Simulates a chain with no hostile framing, just passing output forward.
        try:
            r = adapters[p].run_turn(state, turn_number, "Initial Assessment")
            state["turn_history"].append(r.to_dict())
            coverage, _ = _update_cov(coverage, r.severity_flags)
            turn_log.append(r.to_dict())
            in_tok += r.input_tokens; out_tok += r.output_tokens
            final_verdict = r.verdict; final_reasoning = r.reasoning
        except Exception as e:
            return _err("sequential_chain", "openai+anthropic+google (no governor)",
                        Exception(f"Turn {turn_number} ({p}): {e}"), _ms(start))

    if _any_high(coverage): final_verdict = "ESCALATE"
    flags = {cat: coverage[cat]["max_severity"] for cat in coverage}
    return _ok("sequential_chain", "openai+anthropic+google (sequential, no governor)",
               match_turns, final_verdict, flags, final_reasoning,
               turn_log[-1].get("findings", []) if turn_log else [],
               turn_log, _ms(start), in_tok, out_tok)

# ──────────────────────────────────────────────────────────────────────────
# CONDITION 5 — Holo Full Architecture
# ──────────────────────────────────────────────────────────────────────────
def run_holo_loop(scenario):
    governor = ContextGovernor()
    start    = time.time()
    try:
        result  = governor.evaluate(scenario)
        elapsed = _ms(start)
        flags   = {cat: result["coverage_matrix"][cat]["max_severity"]
                   for cat in result["coverage_matrix"]}
        return _ok("holo_loop", "openai+anthropic+google+governor",
                   result["turns_completed"], result["decision"], flags,
                   result["decision_reason"], [], result["turn_history"], elapsed,
                   result["total_tokens"]["input"], result["total_tokens"]["output"],
                   extra={"converged": result["converged"], "deltas": result["deltas"],
                          "coverage_matrix": result["coverage_matrix"]})
    except Exception as e:
        return _err("holo_loop", "openai+anthropic+google+governor", e, _ms(start))

# ──────────────────────────────────────────────────────────────────────────
# Main runner
# ──────────────────────────────────────────────────────────────────────────
def run_benchmark(scenario_path, verbose=False):
    if verbose: logging.getLogger().setLevel(logging.INFO)

    path = Path(scenario_path)
    if not path.exists():
        raise FileNotFoundError(f"Scenario not found: {scenario_path}")

    scenario      = json.loads(path.read_text())
    scenario_name = path.stem
    expected      = scenario.get("expected_verdict", "UNKNOWN").upper()

    _header(f"HOLO BENCHMARK: {scenario_name}")
    print(f"  Expected verdict : {expected}")
    print(f"  Solo model       : {SOLO_FAMILY.upper()}\n")

    print("  Initializing adapters...")
    adapters = _all_adapters()
    print("  Ready.\n")

    print("  [5/5] HOLO FULL ARCHITECTURE...")
    cond5 = run_holo_loop(scenario)
    _inline(cond5)
    holo_turns = cond5["turns_run"] or 3

    print(f"\n  [1/5] SOLO ONE-PASS...")
    cond1 = run_solo_one_pass(scenario)
    _inline(cond1)

    print(f"\n  [2/5] SOLO MULTI-PASS SELF-CRITIQUE ({holo_turns} turns)...")
    cond2 = run_solo_multi_pass(scenario, match_turns=holo_turns)
    _inline(cond2)

    print(f"\n  [3/5] PARALLEL MULTI-LLM SIGN-OFF...")
    cond3 = run_parallel_signoff(scenario, adapters)
    _inline(cond3)

    print(f"\n  [4/5] SEQUENTIAL CHAIN, NO GOVERNOR ({holo_turns} turns)...")
    cond4 = run_sequential_chain(scenario, adapters, match_turns=holo_turns)
    _inline(cond4)

    result = {
        "benchmark_id":     f"bench_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "scenario_name":    scenario_name,
        "expected_verdict": expected,
        "solo_model":       SOLO_FAMILY,
        "holo_turns":       holo_turns,
        "conditions":       {"solo_one_pass": cond1, "solo_multi_pass": cond2,
                             "parallel_signoff": cond3, "sequential_chain": cond4,
                             "holo_loop": cond5},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    _print_report(result)
    return result

# ──────────────────────────────────────────────────────────────────────────
# Report
# ──────────────────────────────────────────────────────────────────────────
def _print_report(r):
    expected = r["expected_verdict"]
    c        = r["conditions"]

    _header("BENCHMARK REPORT")
    print(f"  Scenario : {r['scenario_name']}")
    print(f"  Expected : {expected}")
    print(f"  Turns    : Conditions 2, 4, 5 each ran {r['holo_turns']} turns\n")

    rows = [
        ("1. Solo one-pass",                    c["solo_one_pass"]),
        ("2. Solo multi-pass (self-critique)",   c["solo_multi_pass"]),
        ("3. Parallel sign-off (majority vote)", c["parallel_signoff"]),
        ("4. Sequential chain (no governor)",    c["sequential_chain"]),
        ("5. HOLO full architecture",            c["holo_loop"]),
    ]

    print(f"  {'Condition':<45} {'Turns':>5}  {'Verdict':<11}  {'Correct?'}")
    print(f"  {'-'*72}")
    for label, cond in rows:
        correct = "YES ✓" if cond["verdict"] == expected else "NO  ✗"
        print(f"  {label:<45} {cond['turns_run']:>5}  {_badge(cond['verdict']):<11}  {correct}")

    print(f"\n  RISK PROFILE (max severity per category across all turns):\n")
    cat_labels = {
        "sender_identity":  "Sender Identity ",
        "invoice_amount":   "Invoice Amount  ",
        "payment_routing":  "Payment Routing ",
        "urgency_pressure": "Urgency/Pressure",
        "domain_spoofing":  "Domain Spoofing ",
        "approval_chain":   "Approval Chain  ",
    }
    print(f"  {'Category':<18} {'1-Solo1x':>9} {'2-SoloNx':>9} {'3-Para':>8} {'4-Seq':>7} {'5-Holo':>7}")
    print(f"  {'-'*65}")
    for cat in BEC_CATEGORIES:
        lbl = cat_labels.get(cat, cat)
        s1,s2,s3,s4,s5 = [_sf(c[k], cat) for k in
                           ["solo_one_pass","solo_multi_pass","parallel_signoff",
                            "sequential_chain","holo_loop"]]
        holo_wins = (_sev_rank(s5) > _sev_rank(s1) and _sev_rank(s5) > _sev_rank(s2)
                     and _sev_rank(s5) > _sev_rank(s3) and _sev_rank(s5) > _sev_rank(s4))
        mark = "  << HOLO ONLY" if holo_wins else ""
        print(f"  {lbl:<18} {s1:>9} {s2:>9} {s3:>8} {s4:>7} {s5:>7}{mark}")

    pso = c["parallel_signoff"]
    if pso.get("extra", {}).get("individual_verdicts"):
        iv = pso["extra"]["individual_verdicts"]
        print(f"\n  PARALLEL SIGN-OFF — EACH MODEL'S SOLO VERDICT:")
        for provider, verdict in iv.items():
            print(f"    {provider:<12} -> {verdict}")
        print(f"    Majority vote  -> {pso['verdict']}")

    holo_log = c["holo_loop"].get("turn_log", [])
    if holo_log and not c["holo_loop"]["error"]:
        print(f"\n  HOLO TURN-BY-TURN AUDIT TRAIL:")
        for t in holo_log:
            flags = " ".join(f"{k[:3].upper()}={v[0]}" for k,v in t.get("severity_flags",{}).items())
            print(f"    Turn {t.get('turn_number','?'):>2} | {t.get('provider','?'):>9} | "
                  f"{t.get('role','?'):<30} | {t.get('verdict','?'):<8} | {flags}")
            for f in t.get("findings", []):
                if f.get("severity") == "HIGH":
                    print(f"             HIGH -> {f.get('category')}: {str(f.get('evidence',''))[:70]}")

    print(f"\n  DISCREPANCY ANALYSIS:\n")
    wrong = {}
    for label, key in [("Solo one-pass","solo_one_pass"),("Solo multi-pass","solo_multi_pass"),
                        ("Parallel sign-off","parallel_signoff"),("Sequential chain","sequential_chain")]:
        if not c[key]["error"]:
            wrong[label] = c[key]["verdict"] != expected

    holo_right = c["holo_loop"]["verdict"] == expected and not c["holo_loop"]["error"]
    all_wrong  = bool(wrong) and all(wrong.values())

    if all_wrong and holo_right:
        failed = ", ".join(k for k,v in wrong.items() if v)
        print(f"  *** ARCHITECTURE PROOF — STRONGEST POSSIBLE RESULT:\n")
        print(f"      Every competitor variant failed: {failed}\n")
        print(f"      Condition 2: same model, same prompts, same turns — still missed it.")
        print(f"      Condition 3: three independent frontier models, majority vote — still missed it.")
        print(f"      Condition 4: sequential chain across three models — still missed it.\n")
        print(f"      HOLO caught it.")
        print(f"      The irreducible variables:")
        print(f"        Shared canonical state (not just passing output forward)")
        print(f"        Adversarial role injection (not just reading prior output)")
        print(f"        Context Governor (not just a vote or a chain)")
        print(f"        Convergence detection (not just stopping after N turns)")
        print(f"\n      This is the proof that cannot be argued away.")
    elif not any(wrong.values()):
        print(f"  All conditions correct. Scenario too easy — try 03_subtle_bec.json.")
    else:
        missed = [k for k,v in wrong.items() if v]
        caught = [k for k,v in wrong.items() if not v]
        if missed:  print(f"  Missed by: {', '.join(missed)}")
        if caught:  print(f"  Caught by (solo): {', '.join(caught)}")
        print(f"  Holo: {'correct' if holo_right else 'also incorrect — check scenario'}")

    print(f"\n  TOKEN COST:\n")
    print(f"  {'Condition':<45} {'Input':>8}  {'Output':>8}")
    print(f"  {'-'*60}")
    for label, cond in rows:
        print(f"  {label:<45} {cond['total_tokens'].get('input',0):>8,}  "
              f"{cond['total_tokens'].get('output',0):>8,}")

    _header("END OF REPORT")

def _header(t): print(f"\n{'='*65}\n  {t}\n{'='*65}\n")
def _badge(v): return {"ESCALATE":"[ESCALATE]","ALLOW":"[ALLOW]   ","ERROR":"[ERROR]   "}.get(v,f"[{v}]")
def _inline(c):
    if c["error"]: print(f"    -> ERROR: {c['error'][:80]}")
    else: print(f"    -> {_badge(c['verdict'])}  {c['turns_run']} turn(s)  "
                f"{c['elapsed_ms']}ms  "
                f"{c['total_tokens'].get('input',0):,}+{c['total_tokens'].get('output',0):,} tokens")

def run_all(save, verbose, directory=None):
    d = Path(directory) if directory else Path("examples/scenarios")
    if not d.exists(): print(f"No directory: {d}"); sys.exit(1)
    scenarios = sorted(d.glob("*.json"))
    results = []
    for s in scenarios:
        result = run_benchmark(str(s), verbose=verbose)
        results.append(result)
        if save: _save(result)
    _header(f"FULL SUITE SUMMARY ({len(results)} scenarios)")
    print(f"  {'Scenario':<28} {'Exp':<9} {'1-1x':^6} {'2-Nx':^6} {'3-Para':^7} {'4-Seq':^6} {'5-Holo':^7}")
    print(f"  {'-'*72}")
    for r in results:
        exp = r["expected_verdict"]; c = r["conditions"]
        def m(k):
            cond = c[k]
            if cond["error"]: return " ERR"
            return "  ✓ " if cond["verdict"] == exp else "  ✗ "
        print(f"  {r['scenario_name']:<28} {exp:<9}{m('solo_one_pass'):^6}{m('solo_multi_pass'):^6}"
              f"{m('parallel_signoff'):^7}{m('sequential_chain'):^6}{m('holo_loop'):^7}")
    print()

def _save(result):
    out = Path("benchmark_results"); out.mkdir(exist_ok=True)
    fname = out / f"{result['benchmark_id']}_{result['scenario_name']}.json"
    fname.write_text(json.dumps(result, indent=2))
    print(f"  Saved: {fname}")

def main():
    parser = argparse.ArgumentParser(description="Holo five-condition benchmark.")
    parser.add_argument("scenario", nargs="?")
    parser.add_argument("--all",     action="store_true")
    parser.add_argument("--dir",     default=None, help="Directory of scenarios for --all")
    parser.add_argument("--save",    action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if args.all:
        run_all(args.save, args.verbose, args.dir); return
    if not args.scenario:
        parser.print_help(); sys.exit(1)
    result = run_benchmark(args.scenario, verbose=args.verbose)
    if args.save: _save(result)

if __name__ == "__main__":
    main()
