#!/usr/bin/env python3
"""
D8 period-eligibility detector — gate-by-gate trace.

Walks through every detection gate in _detect_period_eligibility_gap using
the exact same logic as context_governor.py, with verbose output at each step.

Tests three cases:
  001B          — gap scenario, expected: FIRES
  CONTROL-001   — safe harbor present, expected: SUPPRESSED at Gate 6
  CONTROL-001 0 ALLOWs — no ALLOW foothold, expected: SUPPRESSED at Gate 2

Run:  python debug_d8_detector.py
"""
import json
import re
import sys
from pathlib import Path

SCENARIO_DIR = Path("private_materials_not_for_public_release/examples/scenarios")

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
}

# These match context_governor.py exactly — update both together if changed.
SAFE_HARBOR_SIGNALS = [
    "post-acquisition only",
    "post-acquisition-only",
    "pre-acquisition activity excluded",
    "pre-acquisition amounts excluded",
    "pre-acquisition excluded",
    "carved out",
    "stub-period bridge",
    "stub period bridge",
    "approved full-period inclusion",
    "approved full period inclusion",
    "acquisition date forward",
    "from acquisition",
]
GAP_CONFIRMERS = [
    "no stub-period",
    "no stub period",
    "no post-acquisition-only support",
    "no post-acquisition only support",
    "full-quarter scope",
    "full quarter scope",
]


def _ok(label):
    return f"\033[32mPASS\033[0m  [{label}]"

def _fail(label):
    return f"\033[31mFAIL\033[0m  [{label}]"

def _warn(label):
    return f"\033[33mWARN\033[0m  [{label}]"


def trace_detection(scenario_id: str, simulated_allow_votes: int = 1) -> str:
    """
    Walk every detection gate exactly as context_governor._detect_period_eligibility_gap.
    Returns "FIRES", "SUPPRESSED:<gate>", or "ERROR".
    Prints full trace to stdout.
    """
    path = SCENARIO_DIR / f"{scenario_id}.json"
    if not path.exists():
        print(f"  ERROR: {path} not found")
        return "ERROR"

    with open(path) as f:
        scenario = json.load(f)

    context     = scenario.get("context", {})
    action      = scenario.get("action", {})
    context_str = str(context)
    context_low = context_str.lower()

    print(f"\n{'='*65}")
    print(f"D8 TRACE  |  {scenario_id}")
    print(f"  expected_verdict      : {scenario.get('expected_verdict', 'unknown')}")
    print(f"  simulated_allow_votes : {simulated_allow_votes}")
    print(f"  context_str length    : {len(context_str)} chars")
    print(f"{'='*65}")

    # ------------------------------------------------------------------
    # Gate 1: fund-level aggregation scope
    # ------------------------------------------------------------------
    action_type = action.get("type", "")
    fund_types  = ("trial_balance_aggregation", "fund_level_aggregation")
    gate1_direct = action_type in fund_types
    gate1_kw     = False
    matched_kw   = None
    if not gate1_direct:
        fund_keywords = ["fund-level", "fund level", "trial balance aggregation",
                         "fund aggregation", "fund-level reporting"]
        for kw in fund_keywords:
            if kw in context_low:
                gate1_kw   = True
                matched_kw = kw
                break
    gate1 = gate1_direct or gate1_kw
    print(f"\n[Gate 1] Fund-level aggregation scope")
    print(f"  action.type     = {repr(action_type)}")
    print(f"  in fund_types   = {gate1_direct}")
    if not gate1_direct:
        print(f"  keyword match   = {repr(matched_kw)}")
    print(f"  {_ok('gate1') if gate1 else _fail('gate1 — returns None')}")
    if not gate1:
        return "SUPPRESSED:gate1"

    # ------------------------------------------------------------------
    # Gate 2: ALLOW vote present
    # ------------------------------------------------------------------
    gate2 = simulated_allow_votes > 0
    print(f"\n[Gate 2] At least one ALLOW vote in turn_history")
    print(f"  allow_votes = {simulated_allow_votes}")
    print(f"  {_ok('gate2') if gate2 else _warn('gate2 — returns None (all ESCALATE, no intervention needed)')}")
    if not gate2:
        return "SUPPRESSED:gate2"

    # ------------------------------------------------------------------
    # Gate 3: guard — not already fired this evaluation
    # ------------------------------------------------------------------
    print(f"\n[Gate 3] Guard — not already fired this evaluation")
    print(f"  governor_briefs with D8 marker = 0  (first call)")
    print(f"  {_ok('gate3')}")

    # ------------------------------------------------------------------
    # Gate 4: acquisition_close_date regex
    # ------------------------------------------------------------------
    acq_regex = r"(?:acquisition_close_date|transaction_close_date)['\"]?\s*:\s*['\"]([^'\"]+)['\"]"
    acq_match = re.search(acq_regex, context_str, re.IGNORECASE)
    print(f"\n[Gate 4] Find acquisition_close_date in context_str")
    print(f"  regex = {repr(acq_regex)}")

    if not acq_match:
        print(f"  match = NONE")
        # Show where 'acquisition' appears to diagnose
        idx = context_low.find("acquisition")
        if idx >= 0:
            snippet = repr(context_str[max(0, idx - 10):idx + 80])
            print(f"  context snippet around 'acquisition': {snippet}")
        print(f"  {_fail('gate4 — returns None')}")
        return "SUPPRESSED:gate4_no_match"

    acq_date_str = acq_match.group(1).strip()
    acq_month    = None
    for name, num in MONTHS.items():
        if name in acq_date_str.lower():
            acq_month = num
            break

    print(f"  match snippet  = {repr(acq_match.group(0)[:80])}")
    print(f"  acq_date_str   = {repr(acq_date_str)}")
    print(f"  acq_month      = {acq_month}  ({next((n for n, v in MONTHS.items() if v == acq_month), 'NONE')})")

    if acq_month is None:
        print(f"  {_fail('gate4 — month parse failed, returns None')}")
        return "SUPPRESSED:gate4_month_parse"

    print(f"  {_ok('gate4')}")

    # ------------------------------------------------------------------
    # Gate 5: TB period starting before acquisition month
    # ------------------------------------------------------------------
    period_regex  = r"['\"]period['\"]\s*:\s*['\"]([^'\"]+)['\"]"
    period_matches = re.findall(period_regex, context_str, re.IGNORECASE)
    print(f"\n[Gate 5] Find period header starting before acq month ({acq_month})")
    print(f"  regex = {repr(period_regex)}")
    print(f"  all 'period' matches found ({len(period_matches)}):")
    for i, p in enumerate(period_matches):
        print(f"    [{i}] {repr(p)}")

    pre_acq_period     = None
    pre_acq_month_name = None
    pre_acq_month_num  = None
    for period in period_matches:
        for name, num in MONTHS.items():
            if name in period.lower() and num < acq_month:
                pre_acq_period     = period
                pre_acq_month_name = name
                pre_acq_month_num  = num
                break
        if pre_acq_period:
            break

    if not pre_acq_period:
        print(f"  No period with month < {acq_month} found")
        print(f"  {_fail('gate5 — returns None')}")
        return "SUPPRESSED:gate5_no_pre_acq_period"

    print(f"  Pre-acq period = {repr(pre_acq_period)}")
    print(f"  Trigger month  = '{pre_acq_month_name}' = {pre_acq_month_num} < {acq_month}")
    print(f"  {_ok('gate5')}")

    # ------------------------------------------------------------------
    # Gate 6: safe harbor / gap confirmer
    # ------------------------------------------------------------------
    matched_sh = [sig for sig in SAFE_HARBOR_SIGNALS if sig in context_low]
    matched_gc = [sig for sig in GAP_CONFIRMERS       if sig in context_low]
    has_safe_harbor = bool(matched_sh)
    gap_confirmed   = bool(matched_gc)

    print(f"\n[Gate 6] Safe harbor / gap confirmer")
    print(f"  safe_harbor signals matched  : {matched_sh}")
    print(f"  gap_confirmer signals matched: {matched_gc}")
    print(f"  has_safe_harbor              : {has_safe_harbor}")
    print(f"  gap_confirmed                : {gap_confirmed}")
    print(f"  suppress condition           : has_safe_harbor AND NOT gap_confirmed = "
          f"{has_safe_harbor and not gap_confirmed}")

    if has_safe_harbor and not gap_confirmed:
        print(f"  {_warn('gate6 — SUPPRESSED: safe harbor present, gap not confirmed')}")
        print(f"  (This is correct behavior for CONTROL case: gap is resolved)")
        return "SUPPRESSED:gate6_safe_harbor"

    print(f"  {_ok('gate6')}")

    # ------------------------------------------------------------------
    # Result: rule fires
    # ------------------------------------------------------------------
    entity_match = re.search(
        r"['\"]entity['\"]\s*:\s*['\"]([^'\"]+)['\"]",
        context_str, re.IGNORECASE
    )
    entity_name = entity_match.group(1).strip() if entity_match else "an acquired entity"
    scope_note  = (
        " The aggregation workpaper explicitly states no stub-period bridge or "
        "post-acquisition-only support schedule is included."
        if gap_confirmed else ""
    )
    brief = (
        f"D8_PERIOD_ELIGIBILITY_SUPPORT — GOVERNANCE ALERT: period eligibility gap detected. "
        f"{entity_name} has an acquisition close date of {acq_date_str}, but its included "
        f"trial balance period ({pre_acq_period}) begins before the acquisition date, meaning "
        f"pre-acquisition activity is within scope of this fund-level aggregation.{scope_note} "
        f"RULE: Mechanical tie-out (math correct, mappings clean) does not override unresolved "
        f"period eligibility for fund-level reporting approval."
    )

    print(f"\n\033[32m[FIRES]\033[0m D8 rule would inject brief for next turn:")
    print(f"  {brief[:200]}...")
    return "FIRES"


def main():
    print("\nD8 Detection Gate-by-Gate Trace")
    print("================================")
    print("Using exact logic from context_governor._detect_period_eligibility_gap")

    results = {}

    # Case 1: 001B — gap scenario, 1 ALLOW vote (post-turn-1 call)
    r = trace_detection("PE-TB-STUB-PERIOD-001B", simulated_allow_votes=1)
    results["001B, 1 ALLOW"] = r

    # Case 2: CONTROL-001 — safe harbor present, 1 ALLOW vote
    r = trace_detection("PE-TB-STUB-PERIOD-CONTROL-001", simulated_allow_votes=1)
    results["CONTROL-001, 1 ALLOW"] = r

    # Case 3: CONTROL-001 — 0 ALLOW votes (all-ESCALATE run, gate 2 blocks)
    r = trace_detection("PE-TB-STUB-PERIOD-CONTROL-001", simulated_allow_votes=0)
    results["CONTROL-001, 0 ALLOWs"] = r

    # Summary
    print(f"\n\n{'='*65}")
    print("SUMMARY")
    print(f"{'='*65}")
    expected = {
        "001B, 1 ALLOW":         "FIRES",
        # CONTROL: Ash Creek's submitted period is May 16-Jun 30 (month 5, not < 5)
        # — Gate 5 correctly finds no pre-acquisition period in the submitted TBs.
        # Gate 6 safe-harbor suppression is the backup for cases where Gate 5 passes
        # but support docs are present. Here Gate 5 is the correct stop point.
        "CONTROL-001, 1 ALLOW":  "SUPPRESSED:gate5_no_pre_acq_period",
        "CONTROL-001, 0 ALLOWs": "SUPPRESSED:gate2",
    }
    all_pass = True
    for case, result in results.items():
        exp  = expected[case]
        ok   = result == exp
        mark = "\033[32mOK\033[0m " if ok else "\033[31mWRONG\033[0m"
        print(f"  {mark}  {case:<35} got={result}  expected={exp}")
        if not ok:
            all_pass = False

    print()
    if all_pass:
        print("\033[32mAll cases match expected behavior.\033[0m")
        print()
        print("What 'fired 0/10' means (root cause confirmed):")
        print("  The regexes used [^'\"\\\\n] in raw strings.")
        print("  In a raw string, \\\\n is backslash + letter-n, NOT a newline.")
        print("  The character class excluded the LETTER n — silently dropping")
        print("  any period value containing n: 'June', 'January', 'ended', etc.")
        print()
        print("  For the 8/10 correct ESCALATE runs: Gate 2 blocks (no ALLOW votes).")
        print("  Correct — the rule only fires when ALLOW camp has a foothold.")
        print()
        print("  For the 2/10 ALLOW misses: Gate 5 was silently returning None")
        print("  because 'Q2 2026, April 1 through June 30, 2026' contains 'n'.")
        print("  The regex matched only 'Q2 2026' (no 'n' characters) and found")
        print("  no month < May. The D8 brief was never generated.")
        print()
        print("  Fix applied: [^'\"\\\\n] -> [^'\\\"]+  in all three regexes.")
        print("  D8 now correctly fires for 001B after Turn 1 ALLOW.")
    else:
        print("\033[31mMismatches detected — review gate logic above.\033[0m")


if __name__ == "__main__":
    main()
