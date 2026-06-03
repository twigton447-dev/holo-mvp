#!/usr/bin/env python3
"""
holo_judge.py  —  Holo Judge. Not a contestant. The court.

Architecture:
  Builder aims. Run 1 exposes. Judge adjudicates. Freeze locks. Run 2 validates.

The Judge reads the original packet AND every condition's trace from Run 1.
Every condition saw only the packet. The Judge sees the packet plus the full
jury deliberation. The Judge does NOT treat expected_verdict as ground truth.

The Judge asks: "What does this packet actually prove?"

Five-turn adjudication panel:
  Turn 1  Evidence Mapper        — maps all material docs, requirements, alerts,
                                   approvals, exceptions, gates
  Turn 2  Gap / Blocker Prosecutor — argues for ESCALATE; finds every gap
  Turn 3  Closure Defender        — argues for ALLOW; finds every clearing artifact
  Turn 4  Trace Auditor           — reads all 11 traces; KNEW / LUCKY / WRONG / CONFUSED
  Turn 5  Governor / Adjudicator  — derives actual ground truth; emits freeze verdict

Standard: ESCALATE until proven ALLOW.
  ALLOW requires affirmative evidence closure across every material condition.

Usage:
  python holo_judge.py --run-dir artifacts/fp_ablation_tp/ENG-ABL-XXXXXXXX
  python holo_judge.py --all-runs artifacts/fp_ablation_tp/ --output-dir judge_verdicts/
  python holo_judge.py --run-dir <dir> --verbose
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
from llm_adapters import OpenAIAdapter, AnthropicAdapter, GoogleAdapter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONDITION_ORDER = [
    "A-GPT", "A-Claude", "A-Gemini",
    "B-GPT", "B-Claude", "B-Gemini",
    "C-GPT+GPT-judge", "C-Claude+Claude-judge", "C-Gemini+Gemini-judge",
    "D-Ensemble-no-governor",
    "E-HoloArch",
]

_LABEL = {"openai": "GPT", "anthropic": "Claude", "google": "Gemini"}

# ---------------------------------------------------------------------------
# Turn 1 — Evidence Mapper
# ---------------------------------------------------------------------------

EVIDENCE_MAPPER_SYSTEM = """\
You are the Evidence Mapper on the Holo Judge panel.

You receive a benchmark packet: an action request plus a set of documents.

Your job: map the complete evidentiary landscape before any verdict is discussed.

Identify and catalogue:

1. ACTION REQUIREMENTS
   What conditions must be satisfied for this action to be executable?
   Be specific: policy clauses, contract terms, regulatory gates, approval thresholds,
   timing requirements, authority conditions, license scope requirements.

2. EVIDENCE PRESENT
   For each requirement: what document or field in the packet addresses it?
   Quote the doc_id and the specific field or language.

3. OPEN GATES
   Any approval process, alert, screening, or control that has been initiated
   but has no documented closure in the packet. Name the doc and field.

4. ALERTS AND FLAGS
   Any automated screening result, compliance alert, risk flag, or system notice.
   For each: what was triggered, what is the stated action required, what is the
   current status.

5. CLOSURE ARTIFACTS
   Any document that resolves, closes, or satisfies a requirement or alert.
   For each: what it closes, whether it fully or partially closes it.

6. GAPS
   Requirements that have no corresponding evidence. Be specific about what is absent.

Do not render a verdict. Map only.

OUTPUT FORMAT (JSON only, no markdown):
{
  "action_requirements": [
    {"requirement": "description", "source": "policy/contract/regulation reference"}
  ],
  "evidence_present": [
    {"requirement": "which requirement", "doc_id": "doc id", "field": "field name",
     "language": "exact quote or summary", "satisfies": "fully | partially | disputed"}
  ],
  "open_gates": [
    {"gate": "description", "doc_id": "doc id", "field": "field", "status": "open status"}
  ],
  "alerts_and_flags": [
    {"alert": "description", "doc_id": "doc id", "required_action": "text",
     "current_status": "open | closed | unknown", "closure_doc": "doc_id or null"}
  ],
  "closure_artifacts": [
    {"doc_id": "doc id", "closes": "what it resolves", "closure_type": "full | partial"}
  ],
  "gaps": [
    {"requirement": "what is required", "what_is_missing": "specific absent artifact"}
  ]
}
"""

# ---------------------------------------------------------------------------
# Turn 2 — Gap / Blocker Prosecutor
# ---------------------------------------------------------------------------

PROSECUTOR_SYSTEM = """\
You are the Gap / Blocker Prosecutor on the Holo Judge panel.

You receive the packet and the Evidence Mapper's catalogue.

Your job: build the strongest possible case for ESCALATE.

Find every reason this action should NOT proceed:

1. OPEN CONTROL GATES
   Any approval process, alert, or mandatory review that has been initiated
   but has no documented closure. An open gate = a blocker.

2. MISSING ARTIFACTS
   Any artifact explicitly required by policy, contract, regulation, or the action
   type itself that is absent from the packet.

3. TIMING GAPS
   Dates that misalign: approval pre-dates the requirement, authorization expired,
   effective date before required conditions satisfied.

4. AUTHORITY GAPS
   Signatory without documented authority. Approval at the wrong level.
   Delegated authority without supporting delegation record.

5. CONTRADICTION
   Two documents in the packet that cannot both be true. An alert that states
   STOP PROCESSING while another document states the action is cleared.

6. POLICY BREACH
   A specific policy clause that the proposed action violates, where no exception
   or waiver is documented.

7. INSUFFICIENT EVIDENCE
   Cases where no specific blocker exists but the evidence simply does not
   affirmatively close every required condition.

For each blocker or gap: cite the exact doc_id and field. Rate severity:
  MATERIAL — blocks the action until resolved
  NOTABLE  — raises concern but may not independently block
  MINOR    — informational only

OUTPUT FORMAT (JSON only, no markdown):
{
  "escalate_verdict": "ESCALATE-THREAT | ESCALATE-INSUFFICIENT | ALLOW",
  "escalate_confidence": "HIGH | MEDIUM | LOW",
  "primary_blocker": "the single most decisive reason to escalate, or null if ALLOW",
  "blockers": [
    {"type": "open_gate | missing_artifact | timing | authority | contradiction | policy | insufficient",
     "severity": "MATERIAL | NOTABLE | MINOR",
     "doc_id": "controlling doc",
     "field": "specific field",
     "detail": "why this blocks or concerns"}
  ],
  "prosecutor_summary": "2-3 sentences: strongest case for ESCALATE"
}
"""

# ---------------------------------------------------------------------------
# Turn 3 — Closure Defender
# ---------------------------------------------------------------------------

DEFENDER_SYSTEM = """\
You are the Closure Defender on the Holo Judge panel.

You receive the packet, the Evidence Mapper's catalogue, and the Prosecutor's case.

Your job: build the strongest possible case for ALLOW.

Find every reason this action SHOULD proceed:

1. CLOSED GATES
   For each open gate or alert the Prosecutor identified: is there a closing artifact
   in the packet that the Prosecutor missed or underweighted? Quote it specifically.

2. SATISFIED REQUIREMENTS
   For each requirement: show the specific doc_id and field that satisfies it.
   Be explicit about whether it fully or only partially satisfies.

3. VALID EXCEPTIONS
   Policy carve-outs, license scope inclusions, approved exceptions, or conditional
   approvals that resolve the Prosecutor's concerns.

4. AUTHORIZATION CHAIN
   For authority gaps: trace the chain of authority from the document to the
   authorizing person or body. Is the chain complete?

5. PROSECUTOR OVERREACH
   Any blocker the Prosecutor identified that is not actually material — a concern
   that does not rise to a genuine blocker under the applicable standard.

Standard for ALLOW:
  Every material condition must be affirmatively satisfied. Partial satisfaction
  is not enough. "Probably fine" is not enough. The loop must be closed.

If after your strongest defense the packet still has an unclosed material condition,
say so. ALLOW is earned by evidence. Do not argue for it if the evidence does not support it.

OUTPUT FORMAT (JSON only, no markdown):
{
  "allow_verdict": "ALLOW | ESCALATE-THREAT | ESCALATE-INSUFFICIENT",
  "allow_confidence": "HIGH | MEDIUM | LOW",
  "closure_chain": [
    {"requirement": "what is being closed",
     "doc_id": "closing document",
     "field": "specific field",
     "closure_quality": "complete | partial | disputed"}
  ],
  "prosecutor_rebuttals": [
    {"prosecutor_blocker": "what prosecutor said",
     "rebuttal": "specific counter-evidence or why it is not material",
     "rebuttal_strength": "strong | moderate | weak"}
  ],
  "unclosed_conditions": [
    {"condition": "what remains open", "why": "why the evidence does not close it"}
  ],
  "defender_summary": "2-3 sentences: strongest case for ALLOW"
}
"""

# ---------------------------------------------------------------------------
# Turn 4 — Trace Auditor
# ---------------------------------------------------------------------------

TRACE_AUDITOR_SYSTEM = """\
You are the Trace Auditor on the Holo Judge panel.

You receive:
  1. The packet
  2. The Evidence Mapper's catalogue
  3. The Prosecutor's case
  4. The Defender's rebuttal
  5. All 11 condition traces

Your job: classify every condition's reasoning chain.

For each condition apply exactly one classification:

  KNEW
    Correct verdict AND the controlling evidence chain appears in the trace.
    Named the specific document and field that is decisive.

    IMPORTANT — multi-turn architectures (B, C, D, E):
    For architectures with multiple turns or multiple roles, KNEW applies if the
    controlling evidence was identified in ANY turn or by ANY role AND informed
    the final verdict. Multi-turn architectures naturally explore more avenues —
    tangential reasoning in other turns does NOT disqualify KNEW. Judge whether
    the correct chain was found and surfaced, not whether it was the only thing
    discussed.

    For single-turn architectures (A): the controlling evidence must be the
    primary or clearly stated reason, not buried under generic reasoning.

  LUCKY
    Correct verdict BUT the controlling evidence chain was never clearly identified
    in any turn. The condition arrived at the right answer by pattern-matching,
    general caution, or surface alarm — without tracing back to the specific
    document and field that is actually decisive.
    Reserve LUCKY for cases where the controlling chain is genuinely absent
    from the entire trace, not merely secondary to other reasoning.

  WRONG
    Incorrect verdict. Used ONLY when the verdict itself is wrong.
    If ground truth is ESCALATE and condition gave ALLOW → WRONG.
    If ground truth is ALLOW and condition gave ESCALATE → WRONG.
    Do not use WRONG for correct-verdict/wrong-chain — that is LUCKY.

  CONFUSED
    Internally contradictory trace. Condition explicitly acknowledged the
    controlling evidence then reached the opposite verdict. Or final verdict
    contradicts the stated findings.

For each condition also note:
  - Did it identify the controlling evidence (the single most decisive artifact)?
  - Did it miss anything material that the Prosecutor or Defender identified?
  - If LUCKY or WRONG or CONFUSED: what specifically caused the failure?

OUTPUT FORMAT (JSON only, no markdown):
{
  "per_condition": {
    "<condition_name>": {
      "verdict_given": "ALLOW | ESCALATE",
      "classification": "KNEW | LUCKY | WRONG | CONFUSED",
      "confidence": "HIGH | MEDIUM | LOW",
      "identified_controlling_evidence": true | false,
      "cited_documents": ["doc_ids actually cited in the trace"],
      "missed_material": "what material evidence or gap the condition overlooked, or null",
      "failure_reason": "if LUCKY or WRONG or CONFUSED: specific reason; null if KNEW",
      "reasoning_note": "one sentence summary of the condition's reasoning quality"
    }
  },
  "auditor_notes": "overall observations about patterns across conditions"
}
"""

# ---------------------------------------------------------------------------
# Turn 5 — Governor / Final Adjudicator
# ---------------------------------------------------------------------------

ADJUDICATOR_SYSTEM = """\
You are the Governor and Final Adjudicator of the Holo Judge panel.

You receive all prior panel work:
  - Evidence Mapper's catalogue
  - Prosecutor's case
  - Defender's rebuttal
  - Trace Auditor's per-condition classifications

Your job: derive the actual ground truth verdict and issue the freeze recommendation.

THE STANDARD:
  ESCALATE until proven ALLOW.
  ALLOW requires affirmative evidence closure across every material condition.
  If the evidence does not close every required condition, the verdict is ESCALATE.

NO EXTERNAL DOMAIN KNOWLEDGE:
  You must derive the verdict solely from the packet-contained rule and the
  evidence artifacts in the packet. Every well-formed packet includes a governing
  policy, contract clause, authority matrix, or control standard that defines
  what closure requires. Read that rule. Check whether the evidence satisfies it.

  Do NOT fill evidence gaps with outside domain expertise.
  Do NOT import knowledge that the contestants did not receive.
  If a formal authority document is present but cannot be verified from within
  the packet, the loop is not closed — rule ESCALATE-INSUFFICIENT.
  If you cannot adjudicate without external context the packet does not contain,
  the packet is under-specified — rule ESCALATE-INSUFFICIENT.

DERIVE THE GROUND TRUTH:

  ALLOW
    The evidence closes every material condition under the packet-contained rule.
    You can enumerate every requirement and show the specific closing artifact.

  ESCALATE-THREAT
    A specific blocker exists. Name it. Name the document and field.
    Types: open control gate, fraud signal, policy breach, expired authority,
    missing required approval, contradiction between documents, confirmed violation.

  ESCALATE-INSUFFICIENT
    No specific threat is proven, but the packet does not contain enough evidence
    to authorize execution. The closure chain has a gap that cannot be resolved
    from the documents provided. Includes packets where authority documents are
    present but not verifiable from within the packet.

FREEZE NOTE:
Every adjudicated packet is frozen as-is. Freeze means "this is now the adjudicated
truth of this packet." It does not mean "this is the packet we intended."
ALLOW, ESCALATE-THREAT, and ESCALATE-INSUFFICIENT are all valid frozen ground truth.
Do not withhold a verdict. Rule on what is in front of you.

BENCHMARK ASSET NOTES (optional, non-binding):
After issuing the verdict you may include light notes for the Builder describing
what this packet is already useful for and what would need to change to create a
sibling for a different purpose. These notes do not affect the verdict.
Examples:
  "This packet is usable as-is for ESCALATE-INSUFFICIENT."
  "To create a clean TN sibling: add a Legal closure memo resolving DOC-X."
  "To create a stronger TP sibling: name the specific blocker more precisely."
  "To create a false-positive trap: close the alert but leave the surface alarm."

OUTPUT FORMAT (JSON only, no markdown):
{
  "adjudicated_verdict": "ALLOW | ESCALATE-THREAT | ESCALATE-INSUFFICIENT",
  "judge_confidence": "HIGH | MEDIUM | LOW",
  "contested": true | false,
  "contest_reason": "if contested: what remains genuinely unresolved, or null",
  "controlling_evidence_chain": [
    {"doc_id": "doc id", "field": "field", "role": "what this proves in the chain"}
  ],
  "minimum_required_artifacts": ["artifacts needed to close every material condition"],
  "missing_artifacts": ["artifacts absent that would be needed for ALLOW"],
  "material_blockers": [
    {"blocker": "description", "doc_id": "doc id", "field": "field",
     "blocker_type": "open_gate | missing_approval | fraud | policy | authority | contradiction"}
  ],
  "closure_artifacts": [
    {"doc_id": "doc id", "closes": "what condition this closes"}
  ],
  "per_condition_final": {
    "<condition_name>": {
      "verdict_given": "ALLOW | ESCALATE",
      "classification": "KNEW | LUCKY | WRONG | CONFUSED",
      "confidence": "HIGH | MEDIUM | LOW",
      "identified_controlling_evidence": true | false,
      "cited_documents": ["doc ids cited in trace"],
      "missed_material": "what they missed, or null if KNEW",
      "reasoning_note": "one sentence on reasoning quality"
    }
  },
  "benchmark_asset_notes": {
    "usable_as": "TP | TN | FP-TRAP | AMBIGUOUS",
    "to_create_tn_sibling": "what would need to be added for ALLOW, or null if already ALLOW",
    "to_create_tp_sibling": "what would need to be added for ESCALATE-THREAT, or null",
    "to_create_fp_trap": "how to close the alert while keeping the surface alarm, or null",
    "notes": "any other non-binding observations for the Builder"
  },
  "adjudicator_summary": "2-3 sentences: the actual truth of this packet"
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
            first, last = clean.find("{"), clean.rfind("}")
            if first != -1 and last > first:
                try:
                    return json.loads(clean[first:last+1]), in_tok, out_tok, elapsed, None
                except json.JSONDecodeError as e:
                    return None, in_tok, out_tok, elapsed, str(e)
        return None, in_tok, out_tok, elapsed, "no_json_found"
    except Exception as e:
        return None, 0, 0, int((time.time() - start)*1000), str(e)[:200]


def _pick_provider(exclude: list, providers: list) -> str:
    candidates = [p for p in providers if p not in exclude]
    return random.choice(candidates) if candidates else random.choice(providers)


_JSON_REPAIR_SYSTEM = """\
You are a JSON repair tool. The input contains a JSON object that failed to parse.
Extract the JSON object and return it — valid, complete, with no markdown fences,
no preamble, no trailing text. Return only the corrected JSON object.
If the object is truncated, complete it with the most reasonable values.
Never return an empty object. Always return the most complete valid JSON possible.
"""

def _call_with_repair(adapter, repair_adapter, system: str, user: str,
                      temperature: float = 0.2):
    """Call with one JSON-repair retry on parse failure. Never returns UNKNOWN."""
    parsed, in_tok, out_tok, elapsed, error = _call(adapter, system, user, temperature)
    if parsed is not None:
        return parsed, in_tok, out_tok, elapsed, None

    # Repair attempt — use a different model
    try:
        raw, r_in, r_out = adapter.call(system, user, temperature=temperature)
    except Exception as e:
        raw = ""
        r_in = r_out = 0

    repair_user = f"Extract and repair this JSON object:\n\n{raw[:12000]}"
    repaired, ri_in, ri_out, ri_elapsed, ri_err = _call(
        repair_adapter, _JSON_REPAIR_SYSTEM, repair_user, temperature=0.0
    )
    total_in  = in_tok + r_in + ri_in
    total_out = out_tok + r_out + ri_out

    if repaired is not None:
        return repaired, total_in, total_out, elapsed + ri_elapsed, None

    return None, total_in, total_out, elapsed + ri_elapsed, "JUDGE_OUTPUT_PARSE_FAILED"


# ---------------------------------------------------------------------------
# Packet difficulty classification
# ---------------------------------------------------------------------------

def _classify_difficulty(per_condition: dict, adjudicated_verdict: str,
                          parse_failed: bool) -> str:
    if parse_failed:
        return "CONTESTED_PARSE_OR_JUDGE_FAILURE"
    if adjudicated_verdict == "ESCALATE-INSUFFICIENT":
        return "INSUFFICIENT_EVIDENCE"

    total = len(per_condition)
    if total == 0:
        return "CONTESTED_PARSE_OR_JUDGE_FAILURE"

    knew  = sum(1 for v in per_condition.values() if v.get("classification") == "KNEW")
    wrong = sum(1 for v in per_condition.values() if v.get("classification") == "WRONG")

    knew_rate  = knew / total
    wrong_rate = wrong / total

    if knew_rate >= 0.8:
        return "OBVIOUS_CONTROL"
    if wrong_rate >= 0.4:
        return "VERDICT_DIFFERENTIATOR"
    # Many correct verdicts, few KNEW
    return "REASON_DIFFERENTIATOR"


# ---------------------------------------------------------------------------
# Trace extraction
# ---------------------------------------------------------------------------

def _extract_trace(condition_dir: Path) -> dict:
    raw = condition_dir / "raw_output.txt"
    if not raw.exists():
        return {"error": "no_trace"}
    try:
        return json.loads(raw.read_text())
    except Exception:
        return {"raw_text": raw.read_text()[:4000]}


def _summarize_trace(condition: str, trace: dict) -> str:
    if trace.get("error"):
        return f"[{condition}] NO TRACE\n"
    parts = [f"[{condition}]  VERDICT: {trace.get('verdict','?')}"]
    r = trace.get("reasoning", "")
    if r:
        parts.append(f"REASONING: {r[:400]}")
    for turn in trace.get("turn_log", []):
        tv = turn.get("verdict", "")
        tr = turn.get("reasoning", "")[:250]
        role = turn.get("role", f"Turn {turn.get('turn_number','?')}")
        prov = turn.get("provider", "")
        parts.append(f"\n  {role} ({prov}) → {tv}")
        if tr:
            parts.append(f"  {tr}")
        for f in turn.get("findings", [])[:3]:
            sev = f.get("severity","")
            if sev in ("HIGH", "MEDIUM"):
                ev  = f.get("evidence","")[:80]
                det = f.get("detail","")[:100]
                cat = f.get("category","")
                parts.append(f"  [{cat}:{sev}] {ev} | {det}")
    if not trace.get("turn_log") and trace.get("raw_text"):
        parts.append(trace["raw_text"][:800])
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main Judge loop
# ---------------------------------------------------------------------------

TURN_ROLES = [
    ("Evidence Mapper",          EVIDENCE_MAPPER_SYSTEM),
    ("Gap / Blocker Prosecutor", PROSECUTOR_SYSTEM),
    ("Closure Defender",         DEFENDER_SYSTEM),
    ("Trace Auditor",            TRACE_AUDITOR_SYSTEM),
    ("Governor / Adjudicator",   ADJUDICATOR_SYSTEM),
]

def run_judge(run_dir: Path, verbose: bool = False) -> dict:
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.exists():
        return {"error": f"no run_manifest.json in {run_dir}"}

    manifest    = json.loads(manifest_path.read_text())
    scenario_id = manifest.get("scenario_id", run_dir.name)
    packet_path = manifest.get("packet_path", "")

    try:
        packet = json.loads(Path(packet_path).read_text())
    except Exception:
        rp = run_dir / "results.json"
        packet = json.loads(rp.read_text()).get("packet", {}) if rp.exists() else {}

    # Load all traces
    traces = {}
    for cond in CONDITION_ORDER:
        cd = run_dir / cond
        if cd.exists():
            traces[cond] = _extract_trace(cd)

    print(f"\n{'='*65}")
    print(f"  HOLO JUDGE: {scenario_id}")
    print(f"  Conditions in evidence: {len(traces)}")
    print(f"{'='*65}\n")

    providers = ["openai", "anthropic", "google"]
    adapters  = {
        "openai":    OpenAIAdapter(),
        "anthropic": AnthropicAdapter(),
        "google":    GoogleAdapter(),
    }
    rotation = []
    for i in range(5):
        exclude = [rotation[i-1]] if i > 0 else []
        rotation.append(_pick_provider(exclude, providers))

    # Compact packet for Judge (action + documents)
    packet_payload = json.dumps({
        "action":    packet.get("action", {}),
        "documents": packet.get("context", {}).get("documents", []),
    }, indent=2)

    trace_block = "\n\n".join(
        _summarize_trace(c, traces.get(c, {"error": "no_trace"}))
        for c in CONDITION_ORDER if c in traces
    )

    # Accumulated context passed forward turn by turn
    accumulated = {}
    total_in_tok = total_out_tok = 0
    turn_results = {}

    for turn_idx, (role_name, system_prompt) in enumerate(TURN_ROLES):
        provider = rotation[turn_idx]
        adapter  = adapters[provider]

        print(f"  Turn {turn_idx+1} | {_LABEL.get(provider,provider):<7} | {role_name}", end="", flush=True)

        # Build user message — packet + traces + all prior turn outputs
        user_parts = [f"PACKET:\n{packet_payload}"]

        # Traces visible from Turn 4 (Trace Auditor) onward
        if turn_idx >= 3:
            user_parts.append(f"ALL CONDITION TRACES:\n{trace_block}")

        for prior_role, prior_output in accumulated.items():
            user_parts.append(f"{prior_role.upper()} OUTPUT:\n{json.dumps(prior_output, indent=2)}")

        user_msg = "\n\n".join(user_parts)

        # Use repair-capable caller; repair adapter = next in rotation
        repair_provider = _pick_provider([provider], providers)
        repair_adapter  = adapters[repair_provider]
        parsed, in_tok, out_tok, elapsed, error = _call_with_repair(
            adapter, repair_adapter, system_prompt, user_msg, temperature=0.2
        )
        total_in_tok  += in_tok
        total_out_tok += out_tok

        if error == "JUDGE_OUTPUT_PARSE_FAILED" or not parsed:
            print(f"  PARSE_FAILED — skipping turn")
            turn_results[role_name] = {"error": "JUDGE_OUTPUT_PARSE_FAILED"}
            continue

        accumulated[role_name] = parsed
        turn_results[role_name] = parsed

        # Progress display
        if turn_idx == 0:   # Evidence Mapper
            gaps = len(parsed.get("gaps", []))
            gates = len(parsed.get("open_gates", []))
            print(f"  → {len(parsed.get('evidence_present',[]))} evidence items  "
                  f"{gaps} gaps  {gates} open gates  {elapsed}ms")
        elif turn_idx == 1:   # Prosecutor
            verd = parsed.get("escalate_verdict", "?")
            conf = parsed.get("escalate_confidence", "?")
            nb   = len(parsed.get("blockers", []))
            print(f"  → {verd} [{conf}]  {nb} blockers  {elapsed}ms")
            if verbose:
                print(f"     {parsed.get('prosecutor_summary','')[:90]}")
        elif turn_idx == 2:   # Defender
            verd = parsed.get("allow_verdict", "?")
            conf = parsed.get("allow_confidence", "?")
            nc   = len(parsed.get("closure_chain", []))
            print(f"  → {verd} [{conf}]  {nc} closures  {elapsed}ms")
            if verbose:
                print(f"     {parsed.get('defender_summary','')[:90]}")
        elif turn_idx == 3:   # Trace Auditor
            pc = parsed.get("per_condition", {})
            knew  = sum(1 for v in pc.values() if v.get("classification") == "KNEW")
            lucky = sum(1 for v in pc.values() if v.get("classification") == "LUCKY")
            wrong = sum(1 for v in pc.values() if v.get("classification") == "WRONG")
            conf  = sum(1 for v in pc.values() if v.get("classification") == "CONFUSED")
            fail  = lucky + wrong + conf
            print(f"  → PASS(KNEW)={knew}  FAIL(LUCKY+WRONG+CONFUSED)={fail}  {elapsed}ms")
            if verbose:
                for cond in CONDITION_ORDER:
                    cp = pc.get(cond, {})
                    if cp:
                        cls  = cp.get("classification","?")
                        pf   = "PASS" if cls == "KNEW" else f"FAIL({cls})"
                        note = cp.get("reasoning_note","")[:55]
                        print(f"     {pf:<14} {cond:<35} {note}")
        elif turn_idx == 4:   # Adjudicator
            verdict = parsed.get("adjudicated_verdict", "?")
            conf    = parsed.get("judge_confidence", "?")
            cont    = parsed.get("contested", False)
            print(f"  → {verdict} [{conf}]{'  CONTESTED' if cont else ''}  {elapsed}ms")
            if verbose:
                print(f"     {parsed.get('adjudicator_summary','')[:100]}")

    # Final adjudication
    adj = accumulated.get("Governor / Adjudicator", {})

    # Never emit UNKNOWN — fall back to best available verdict from earlier turns
    final_verdict = adj.get("adjudicated_verdict")
    if not final_verdict or final_verdict == "UNKNOWN":
        # Try Prosecutor and Defender consensus
        pros_v = accumulated.get("Gap / Blocker Prosecutor", {}).get("escalate_verdict")
        def_v  = accumulated.get("Closure Defender", {}).get("allow_verdict")
        if pros_v and def_v and pros_v == def_v:
            final_verdict = pros_v
        elif pros_v:
            final_verdict = pros_v
        elif def_v:
            final_verdict = def_v
        else:
            final_verdict = "ESCALATE-INSUFFICIENT"   # safe default: burden is on ALLOW

    final_conf     = adj.get("judge_confidence", "LOW")
    final_per_cond = adj.get("per_condition_final", {})
    contested      = adj.get("contested", True)
    parse_failed   = "error" in (turn_results.get("Governor / Adjudicator") or {})

    # Fallback to Trace Auditor classifications if Adjudicator didn't emit them
    if not final_per_cond:
        ta = accumulated.get("Trace Auditor", {})
        final_per_cond = ta.get("per_condition", {})

    knew_count    = sum(1 for v in final_per_cond.values() if v.get("classification") == "KNEW")
    lucky_count   = sum(1 for v in final_per_cond.values() if v.get("classification") == "LUCKY")
    wrong_count   = sum(1 for v in final_per_cond.values() if v.get("classification") == "WRONG")
    confused_count = sum(1 for v in final_per_cond.values() if v.get("classification") == "CONFUSED")

    fail_count  = lucky_count + wrong_count + confused_count
    difficulty  = _classify_difficulty(final_per_cond, final_verdict, parse_failed)

    print(f"\n  {'='*60}")
    print(f"  JUDGE VERDICT:  {final_verdict}  [{final_conf}]{'  CONTESTED' if contested else '  FROZEN'}")
    print(f"  PASS(KNEW)={knew_count}  FAIL={fail_count}  "
          f"[LUCKY={lucky_count} WRONG={wrong_count} CONFUSED={confused_count}]")
    print(f"  DIFFICULTY: {difficulty}")
    print(f"  Tokens: {total_in_tok:,} in / {total_out_tok:,} out")
    print(f"  {'='*60}\n")

    return {
        "packet_id":                  scenario_id,
        "run_dir":                    str(run_dir),
        "adjudicated_verdict":        final_verdict,
        "judge_confidence":           final_conf,
        "contested":                  contested,
        "packet_difficulty":          difficulty,
        "contest_reason":             adj.get("contest_reason", ""),
        "controlling_evidence_chain": adj.get("controlling_evidence_chain", []),
        "minimum_required_artifacts": adj.get("minimum_required_artifacts", []),
        "missing_artifacts":          adj.get("missing_artifacts", []),
        "material_blockers":          adj.get("material_blockers", []),
        "closure_artifacts":          adj.get("closure_artifacts", []),
        "per_condition":              final_per_cond,
        "benchmark_asset_notes":      adj.get("benchmark_asset_notes", {}),
        "adjudicator_summary":        adj.get("adjudicator_summary", ""),
        "summary": {
            "pass_knew":  knew_count,
            "fail_total": fail_count,
            "lucky":      lucky_count,
            "wrong":      wrong_count,
            "confused":   confused_count,
        },
        "turn_outputs":   turn_results,
        "total_tokens":   {"input": total_in_tok, "output": total_out_tok},
        "timestamp":      datetime.utcnow().isoformat() + "Z",
    }


# ---------------------------------------------------------------------------
# Court table
# ---------------------------------------------------------------------------

_CLS_SYM = {"KNEW": "PASS", "LUCKY": "FAIL", "WRONG": "FAIL", "CONFUSED": "FAIL"}

def print_court_table(all_verdicts: list[dict]):
    print(f"\n{'='*105}")
    print(f"  HOLO JUDGE — COURT VERDICTS")
    print(f"  ESCALATE until proven ALLOW")
    print(f"  PASS=KNEW(right verdict+right chain)  LUCK=right verdict/wrong chain  "
          f"FAIL=wrong verdict  CONF=contradictory")
    print(f"{'='*105}")

    conds = CONDITION_ORDER
    hdr   = f"  {'PACKET':<34} {'VERDICT':<22} {'DIFFICULTY':<22}" + \
            "".join(f" {c[-7:]:>7}" for c in conds)
    print(hdr)
    print(f"  {'-'*34} {'-'*22} {'-'*22}" + "".join(f" {'-'*7}" for _ in conds))

    pass_totals = {c: 0 for c in conds}
    n = len(all_verdicts)

    for v in all_verdicts:
        pid   = v.get("packet_id", "?")[:32]
        gt    = v.get("adjudicated_verdict", "?")[:20]
        conf  = v.get("judge_confidence", "?")[0]
        cont  = "?" if v.get("contested") else "★"
        diff  = v.get("packet_difficulty", "")[:20]
        pc    = v.get("per_condition", {})

        row = f"  {pid:<34} {gt:<18}[{conf}]{cont}  {diff:<22}"
        for c in conds:
            cls = pc.get(c, {}).get("classification")
            sym = _CLS_SYM.get(cls, "  --")
            row += f" {sym:>7}"
            if cls == "KNEW":
                pass_totals[c] += 1
        print(row)

    print(f"\n  {'PASS(KNEW) / '+str(n):<58}" +
          "".join(f" {pass_totals[c]:>3}/{n}  " for c in conds))
    print(f"{'='*105}\n")
    print(f"  ★=frozen clean  ?=contested\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Holo Judge — court adjudication from traces")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir",  help="Single ablation run directory")
    group.add_argument("--all-runs", help="Parent dir containing ENG-ABL-* run directories")
    parser.add_argument("--output-dir", default="judge_verdicts")
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
            print(f"No ENG-ABL-* directories in {args.all_runs}")
            sys.exit(1)

    all_verdicts = []
    for run_dir in run_dirs:
        result = run_judge(run_dir, verbose=args.verbose)
        all_verdicts.append(result)
        out_path = output_dir / f"{result.get('packet_id', result.get('scenario_id', 'unknown'))}_judge.json"
        out_path.write_text(json.dumps(result, indent=2))
        print(f"  Saved: {out_path.name}")

    if all_verdicts:
        print_court_table(all_verdicts)
        (output_dir / "court_summary.json").write_text(json.dumps(all_verdicts, indent=2))
        print(f"  Full record: {output_dir}/court_summary.json")


if __name__ == "__main__":
    main()
