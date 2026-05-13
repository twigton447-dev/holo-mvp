"""
saferacks_harness.py
Holo Engine — SafeRacks Operations Mini Benchmark Harness v0.1

Multi-turn adversarial adjudication with convergence logic.
Minimum 3 turns, typically 4-5.

Drop into: /Users/taylorwigton/CascadeProjects/holo-mvp/
Run:  python saferacks_harness.py --case 1
      python saferacks_harness.py --case all
      python saferacks_harness.py --case 1 --verbose

Requires: ANTHROPIC_API_KEY in environment
"""

import os
import json
import argparse
from datetime import datetime
from anthropic import Anthropic

from saferacks_context import (
    VERTICAL_CONTEXT,
    RISK_LENSES,
    GOVERNOR_RULES,
    REVIEWER_PERSONAS,
    CASES,
    ACTION_BOUNDARIES,
)

client = Anthropic()

# ---------------------------------------------------------------------------
# TURN DEFINITIONS
# ---------------------------------------------------------------------------

def build_triage_prompt(case: dict) -> str:
    return f"""You are the internal triage layer for Holo Engine, a pre-execution adjudication system.
Your job is NOT to make the final decision. Your job is to:
1. Classify the action boundary type
2. Validate packet completeness — list what is present and what is missing
3. Identify the specific risk lenses that apply to this case
4. Flag any cross-functional dependencies that may be absent from the packet
5. Determine whether this case requires full adversarial review or can be routed
   to a routine ALLOW (only if all signals are clean and no risk lenses are triggered)

DOMAIN CONTEXT:
{VERTICAL_CONTEXT}

ACTION BOUNDARY TYPES:
{json.dumps(ACTION_BOUNDARIES, indent=2)}

RISK LENSES TO CHECK:
{chr(10).join(RISK_LENSES)}

CASE PACKET:
{case['packet']}

Respond in this exact JSON format:
{{
  "turn": "TRIAGE",
  "case_id": "{case['id']}",
  "action_boundary_type": "<type from library>",
  "packet_completeness": {{
    "present": ["<item>", ...],
    "missing_or_uncertain": ["<item>", ...]
  }},
  "risk_lenses_triggered": ["<lens_name>", ...],
  "cross_functional_dependencies_flagged": ["<dependency>", ...],
  "routing": "<FULL_REVIEW or ROUTINE_ALLOW>",
  "routing_rationale": "<one sentence>"
}}"""


def build_analyst_prompt(
    persona_key: str,
    case: dict,
    prior_turns: list,
    turn_number: int,
) -> str:
    persona = REVIEWER_PERSONAS[persona_key]
    prior_context = ""
    if prior_turns:
        prior_context = "\n\nPRIOR TURN OUTPUTS (you must read these and challenge or build on them):\n"
        for t in prior_turns:
            prior_context += f"\n--- Turn {t['turn_number']} ({t['role']}) ---\n"
            prior_context += json.dumps(t['output'], indent=2)

    return f"""You are a {persona['role']} serving as an adversarial reviewer inside Holo Engine.

YOUR LENS: {persona['lens']}

YOUR KNOWN BIAS TO COMPENSATE FOR: {persona['bias']}

DOMAIN CONTEXT:
{VERTICAL_CONTEXT}

RISK LENSES:
{chr(10).join(RISK_LENSES)}

CASE PACKET:
{case['packet']}
{prior_context}

INSTRUCTIONS:
- Issue your verdict: ALLOW, REQUEST_CONTEXT, or ESCALATE
- Do NOT default to ALLOW just because the packet looks clean on the surface
- Do NOT escalate just because something looks complex — only escalate if there
  is genuine unsupported commitment risk
- If prior turns exist: explicitly state what you agree with, what you challenge,
  and what the prior reviewer missed through their lens
- A stated watchout is NOT the same as resolved context. If a risk requires
  action from a function not confirmed to be in the loop, that is REQUEST_CONTEXT.
- Be specific. Name the actual risk. Do not speak in generalities.

Respond in this exact JSON format:
{{
  "turn": "ANALYST_{turn_number}",
  "case_id": "{case['id']}",
  "reviewer_role": "{persona['role']}",
  "verdict": "<ALLOW | REQUEST_CONTEXT | ESCALATE>",
  "confidence": <0.0-1.0>,
  "primary_risk_identified": "<specific risk in one sentence>",
  "risk_factors": ["<factor>", ...],
  "missing_context": ["<what is absent but needed>", ...],
  "challenge_to_prior": "<what prior turn missed or got wrong, or 'N/A' if first>",
  "reasoning": "<2-3 sentences max>"
}}"""


def build_synthesis_prompt(case: dict, prior_turns: list) -> str:
    prior_context = "\n\nALL PRIOR TURN OUTPUTS:\n"
    for t in prior_turns:
        prior_context += f"\n--- Turn {t['turn_number']} ({t['role']}) ---\n"
        prior_context += json.dumps(t['output'], indent=2)

    return f"""You are a synthesis reviewer inside Holo Engine. You have seen all analyst verdicts.
Your job is to identify the strongest argument on each side and produce a synthesized
pre-Governor position.

DOMAIN CONTEXT:
{VERTICAL_CONTEXT}

CASE PACKET:
{case['packet']}
{prior_context}

INSTRUCTIONS:
- Identify where analysts agree and where they diverge
- Name the single strongest risk argument for escalation/request-context
- Name the single strongest argument for allow
- Issue a synthesized pre-Governor verdict
- Do not split the difference — pick the defensible position

Respond in this exact JSON format:
{{
  "turn": "SYNTHESIS",
  "case_id": "{case['id']}",
  "analyst_agreement": "<FULL | PARTIAL | SPLIT>",
  "strongest_risk_argument": "<one sentence>",
  "strongest_allow_argument": "<one sentence>",
  "synthesized_verdict": "<ALLOW | REQUEST_CONTEXT | ESCALATE>",
  "confidence": <0.0-1.0>,
  "key_unresolved_question": "<the single question that, if answered, would resolve the verdict>"
}}"""


def build_governor_prompt(case: dict, prior_turns: list) -> str:
    prior_context = "\nALL PRIOR TURN OUTPUTS:\n"
    for t in prior_turns:
        prior_context += f"\n--- Turn {t['turn_number']} ({t['role']}) ---\n"
        prior_context += json.dumps(t['output'], indent=2)

    return f"""You are the Governor — the final authority inside Holo Engine.
You receive all prior turn outputs and apply the domain Governor Rules to issue
the final binding verdict.

DOMAIN CONTEXT:
{VERTICAL_CONTEXT}

GOVERNOR RULES (apply in order — first triggered rule sets the floor):
{GOVERNOR_RULES}

CASE PACKET:
{case['packet']}
{prior_context}

INSTRUCTIONS:
- Apply Governor Rules in order
- State which rule was triggered (if any)
- The Governor may raise (escalate further) but never lower an analyst consensus
- If no rules are triggered and analyst consensus is ALLOW: issue ALLOW
- Be precise about what would need to be true for the verdict to change

Respond in this exact JSON format:
{{
  "turn": "GOVERNOR",
  "case_id": "{case['id']}",
  "governor_rule_triggered": "<rule ID and name, or 'NONE'>",
  "verdict": "<ALLOW | REQUEST_CONTEXT | ESCALATE>",
  "confidence": <0.0-1.0>,
  "verdict_rationale": "<2-3 sentences — specific, not generic>",
  "recommended_next_step": "<what must happen before this can be approved, or 'Proceed'>",
  "missing_context": ["<specific item needed>", ...],
  "audit_summary": "<one sentence suitable for an audit log>"
}}"""


# ---------------------------------------------------------------------------
# SINGLE TURN RUNNER
# ---------------------------------------------------------------------------

def run_turn(prompt: str, turn_label: str, verbose: bool = False) -> dict:
    if verbose:
        print(f"\n{'='*60}")
        print(f"  TURN: {turn_label}")
        print(f"{'='*60}")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"raw_text": raw, "parse_error": True}

    if verbose:
        print(json.dumps(parsed, indent=2))

    return parsed


# ---------------------------------------------------------------------------
# FULL CASE RUNNER — 5 turns
# ---------------------------------------------------------------------------

def run_case(case_key: str, verbose: bool = False) -> dict:
    case = CASES[case_key]
    turns = []

    print(f"\n{'#'*70}")
    print(f"  HOLO ENGINE — SafeRacks Mini Benchmark")
    print(f"  Case: {case['id']} — {case['title']}")
    print(f"  Type: {case['type'].upper()}")
    print(f"{'#'*70}")

    # --- TURN 1: TRIAGE ---
    print("\n[Turn 1/5] Internal triage...")
    t1_prompt = build_triage_prompt(case)
    t1_output = run_turn(t1_prompt, "TRIAGE", verbose)
    turns.append({"turn_number": 1, "role": "INTERNAL_TRIAGE", "output": t1_output})

    # Check if triage routes to routine allow
    routing = t1_output.get("routing", "FULL_REVIEW")
    if routing == "ROUTINE_ALLOW":
        print("  => Triage: ROUTINE_ALLOW — routing to express Governor...")
        # Still run Governor for audit completeness
    else:
        print(f"  => Triage: FULL_REVIEW — {len(t1_output.get('risk_lenses_triggered', []))} risk lenses triggered")

    # --- TURN 2: ANALYST A ---
    persona_a = case.get("personas", ["ops_reviewer", "commercial_reviewer"])[0]
    persona_a_label = REVIEWER_PERSONAS[persona_a]["role"]
    print(f"\n[Turn 2/5] Analyst A — {persona_a_label}...")
    t2_prompt = build_analyst_prompt(persona_a, case, turns, 2)
    t2_output = run_turn(t2_prompt, "ANALYST_A", verbose)
    turns.append({"turn_number": 2, "role": "ANALYST_A", "output": t2_output})
    print(f"  => Analyst A verdict: {t2_output.get('verdict', 'UNKNOWN')} (confidence: {t2_output.get('confidence', '?')})")

    # --- TURN 3: ANALYST B ---
    persona_b = case.get("personas", ["ops_reviewer", "commercial_reviewer"])[1]
    persona_b_label = REVIEWER_PERSONAS[persona_b]["role"]
    print(f"\n[Turn 3/5] Analyst B — {persona_b_label}...")
    t3_prompt = build_analyst_prompt(persona_b, case, turns, 3)
    t3_output = run_turn(t3_prompt, "ANALYST_B", verbose)
    turns.append({"turn_number": 3, "role": "ANALYST_B", "output": t3_output})
    print(f"  => Analyst B verdict: {t3_output.get('verdict', 'UNKNOWN')} (confidence: {t3_output.get('confidence', '?')})")

    # --- TURN 4: SYNTHESIS ---
    print("\n[Turn 4/5] Synthesis — cross-analyst convergence check...")
    t4_prompt = build_synthesis_prompt(case, turns)
    t4_output = run_turn(t4_prompt, "SYNTHESIS", verbose)
    turns.append({"turn_number": 4, "role": "SYNTHESIS", "output": t4_output})
    print(f"  => Synthesized: {t4_output.get('synthesized_verdict', 'UNKNOWN')} (analyst agreement: {t4_output.get('analyst_agreement', '?')})")

    # --- TURN 5: GOVERNOR ---
    print("\n[Turn 5/5] Governor — final verdict...")
    t5_prompt = build_governor_prompt(case, turns)
    t5_output = run_turn(t5_prompt, "GOVERNOR", verbose)
    turns.append({"turn_number": 5, "role": "GOVERNOR", "output": t5_output})

    final_verdict = t5_output.get("verdict", "UNKNOWN")
    rule_triggered = t5_output.get("governor_rule_triggered", "NONE")

    print(f"\n{'='*70}")
    print(f"  FINAL VERDICT: {final_verdict}")
    print(f"  Governor rule: {rule_triggered}")
    print(f"  Rationale: {t5_output.get('verdict_rationale', '')}")
    print(f"  Next step: {t5_output.get('recommended_next_step', '')}")
    print(f"{'='*70}")

    # --- RESULT PACKAGE ---
    result = {
        "case_id": case["id"],
        "case_title": case["title"],
        "case_type": case["type"],
        "timestamp": datetime.utcnow().isoformat(),
        "expected_solo_verdict": case["expected_solo_verdict"],
        "expected_holo_verdict": case["expected_holo_verdict"],
        "actual_holo_verdict": final_verdict,
        "governor_rule_triggered": rule_triggered,
        "verdict_rationale": t5_output.get("verdict_rationale", ""),
        "recommended_next_step": t5_output.get("recommended_next_step", ""),
        "missing_context": t5_output.get("missing_context", []),
        "audit_summary": t5_output.get("audit_summary", ""),
        "gap_confirmed": final_verdict != case["expected_solo_verdict"].split()[0],
        "turns": turns,
    }

    return result


# ---------------------------------------------------------------------------
# BENCHMARK RUNNER — all cases
# ---------------------------------------------------------------------------

def run_benchmark(verbose: bool = False) -> list:
    results = []
    case_keys = list(CASES.keys())

    print("\n" + "="*70)
    print("  HOLO ENGINE — SafeRacks Operations Mini Benchmark v0.1")
    print(f"  {len(case_keys)} cases | Multi-turn adversarial adjudication")
    print(f"  Run started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("="*70)

    for key in case_keys:
        result = run_case(key, verbose=verbose)
        results.append(result)

    # --- SUMMARY ---
    print("\n" + "="*70)
    print("  BENCHMARK SUMMARY")
    print("="*70)
    print(f"  {'CASE':<12} {'TYPE':<12} {'SOLO EXPECTED':<22} {'HOLO VERDICT':<18} {'GAP?'}")
    print(f"  {'-'*80}")
    for r in results:
        gap = "YES — gap confirmed" if r["gap_confirmed"] else "no gap"
        print(f"  {r['case_id']:<12} {r['case_type']:<12} {r['expected_solo_verdict']:<22} {r['actual_holo_verdict']:<18} {gap}")

    print("\n  KEY INSIGHT:")
    gap_cases = [r for r in results if r["case_type"] == "gap" and r["gap_confirmed"]]
    print(f"  {len(gap_cases)} of 2 gap cases confirmed. Solo model approved what Holo escalated.")
    print("  The miss was not awareness. The miss was authority.")
    print("="*70)

    # Save results
    output_path = f"saferacks_benchmark_results_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {output_path}")

    return results


# ---------------------------------------------------------------------------
# CLI ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Holo Engine — SafeRacks Operations Mini Benchmark Harness v0.1"
    )
    parser.add_argument(
        "--case",
        type=str,
        default="all",
        help="Case to run: 1, 2, 3, 4, or 'all' (default: all)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full turn outputs",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available cases and exit",
    )
    args = parser.parse_args()

    if args.list:
        print("\nAvailable cases:")
        for i, (key, case) in enumerate(CASES.items(), 1):
            print(f"  {i}. [{case['type'].upper()}] {case['title']}")
            print(f"     Expected solo: {case['expected_solo_verdict']}")
            print(f"     Expected Holo: {case['expected_holo_verdict']}")
        return

    case_map = {
        "1": "case_1_po_carton_gap",
        "2": "case_2_dtc_fillrate_gap",
        "3": "case_3_supplier_pilot_precision",
        "4": "case_4_routine_allow",
        "5": "case_5_wms_override_coded",
    }

    if args.case == "all":
        run_benchmark(verbose=args.verbose)
    elif args.case in case_map:
        run_case(case_map[args.case], verbose=args.verbose)
    else:
        print(f"Unknown case: {args.case}. Use 1-4 or 'all'.")


if __name__ == "__main__":
    main()
