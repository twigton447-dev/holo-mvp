#!/usr/bin/env python3
"""
ablation_engine_harness.py  —  Holo Verify Ablation Harness

Test cage only. Production Holo is never modified.

Architecture families:
  A  Native solo one-shot         (GPT / Claude / Gemini)
  B  Native solo multi-turn       (GPT / Claude / Gemini — generic reconsideration)
  C  Homogeneous solo council     (GPT / Claude / Gemini — generic roles)
  D  Multi-model ensemble         (GPT + Claude + Gemini, majority vote, no governor)
  E  Holo Architecture-Only      (full adversarial council + governor, no domain coaching)

Isolation guarantees:
  - Packet bytes are identical across all conditions.
  - No domain guide, no IAM checklist, no packet-specific hints to any condition.
  - No production Holo files modified (context_governor.py, llm_adapters.py,
    benchmark.py, scenario_templates.py are imported read-only).
  - Condition D implemented without touching benchmark.py globals.
  - Per-condition raw output written to --output-dir.

Usage:
  PYTHONPATH=private_materials_not_for_public_release python ablation_engine_harness.py \\
      --packet-path private_materials_not_for_public_release/examples/scenarios/IAM-SOD-COMP-001B-ABLATION-CANDIDATE-001.json \\
      --packet-hash e41eed49c3c42d8043e05897946d017d80462069fffb8c1bec8be7ed518fed5c \\
      --model-cohort ablation_cohort_default.json \\
      --output-dir artifacts/engine_ablation \\
      --run-id auto \\
      --mode raw_bones

  Add --skip-holo to run A/B/C/D without the Holo Engine (faster debug).
  Add --only-holo to run E only.
  Add --verbose to print full model responses.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "private_materials_not_for_public_release"))

# Read-only production imports — no production files modified
from llm_adapters import OpenAIAdapter, AnthropicAdapter, GoogleAdapter

HARNESS_VERSION = "v1.0"

# ---------------------------------------------------------------------------
# Universal minimal instruction — same for all raw-bones conditions.
# No domain guide. No IAM checklist. No packet-specific hints.
# ---------------------------------------------------------------------------

UNIVERSAL_INSTRUCTION = (
    "You are reviewing a set of enterprise documents related to an access authorization "
    "decision. Based only on the evidence in these documents, return ALLOW or ESCALATE "
    "and explain your reasoning. ALLOW means no material blocker remains. ESCALATE means "
    "a material blocker exists that must be resolved before the action proceeds."
)

# Turn 2 reconsideration prompt (Condition B) — generic, no domain cues
RECONSIDER_PROMPT = (
    "Reconsider your previous assessment. Review the evidence more carefully. "
    "Is there a specific requirement, time constraint, period, or verification condition "
    "you may have overlooked? Respond with ALLOW or ESCALATE followed by your updated reasoning."
)

# Condition C generic role prompts — no domain personas, no IAM guidance
_COUNCIL_ROLES = {
    "reviewer": (
        "You are the Reviewer. Make an initial assessment of the submitted documents. "
        "State your verdict (ALLOW or ESCALATE) and the primary reason."
    ),
    "skeptic": (
        "You are the Skeptic. Challenge the Reviewer's assessment. "
        "Identify what the Reviewer may have missed, assumed, or overtrusted. "
        "State your verdict (ALLOW or ESCALATE) and reasoning."
    ),
    "evidence_checker": (
        "You are the Evidence Checker. Cross-reference the artifacts. "
        "Identify any gaps, inconsistencies, or documents that fail to satisfy "
        "the requirements stated in the policy or procedural records. "
        "State your verdict (ALLOW or ESCALATE) and cite specific evidence."
    ),
    "final_judge": (
        "You are the Final Judge. Consider all prior perspectives. "
        "Render a definitive verdict: ALLOW or ESCALATE. "
        "Cite the single most determinative fact in your reasoning."
    ),
}

# Provider labels
_LABEL = {"openai": "GPT", "anthropic": "Claude", "google": "Gemini"}

# Orchestration type map (for output schema)
_ORCH_TYPE = {
    "A": "native_solo_one_shot",
    "B": "native_solo_self_critique",
    "C": "homogeneous_solo_council",
    "D": "multi_model_ensemble_no_governor",
    "E": "holo_adversarial_council_with_governor",
}

# Guidance level map
_GUIDANCE_LEVEL = {
    "A": "raw",
    "B": "raw",
    "C": "raw",
    "D": "raw",
    "E": "production_architecture_only",
}


# ---------------------------------------------------------------------------
# Model cohort
# ---------------------------------------------------------------------------

def load_cohort(cohort_path: str) -> dict:
    path = Path(cohort_path)
    if not path.exists():
        raise FileNotFoundError(f"Model cohort not found: {path}")
    cohort = json.loads(path.read_text())
    required = ["cohort_id", "models"]
    for f in required:
        if f not in cohort:
            raise ValueError(f"Model cohort missing required field: {f}")
    return cohort


def apply_cohort(cohort: dict) -> None:
    """Apply cohort model overrides to environment (before adapter construction)."""
    models = cohort.get("models", {})
    if models.get("openai"):
        os.environ["OPENAI_MODEL"] = models["openai"]
    if models.get("anthropic"):
        os.environ["ANTHROPIC_MODEL"] = models["anthropic"]
    if models.get("google"):
        os.environ["GOOGLE_MODEL"] = models["google"]


def build_adapters() -> dict:
    return {
        "openai":    OpenAIAdapter(),
        "anthropic": AnthropicAdapter(),
        "google":    GoogleAdapter(),
    }


def cohort_model_versions(adapters: dict) -> dict:
    return {p: a.model_id for p, a in adapters.items()}


# ---------------------------------------------------------------------------
# Provenance helpers
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _git_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=BASE, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unavailable"


# ---------------------------------------------------------------------------
# Generic validity checks (packet-agnostic — no 001B-specific logic)
# ---------------------------------------------------------------------------

def run_generic_validity_checks(scenario: dict) -> list[dict]:
    checks = []

    def chk(name: str, passed: bool, detail: str = ""):
        checks.append({"name": name, "passed": passed, "detail": detail})

    # 1. Required schema fields
    required = ["scenario_id", "expected_verdict", "action", "context",
                "hidden_ground_truth", "gold_answer", "scoring_targets"]
    missing = [f for f in required if f not in scenario]
    chk("1. Required schema fields", not missing,
        f"Missing: {missing}" if missing else "All required fields present")

    # 2. No answer labels exposed in action/context
    ctx_str = json.dumps(scenario.get("context", {})).lower()
    act_str = json.dumps(scenario.get("action", {})).lower()
    exposure_patterns = [
        r'"expected_verdict"', r'"gold_answer"', r'"correct_verdict"',
        r'"hidden_ground_truth"', r'"scoring_targets"',
    ]
    exposed = [p for p in exposure_patterns
               if re.search(p, ctx_str) or re.search(p, act_str)]
    chk("2. No exposed answer labels in action/context",
        not exposed,
        f"Exposed: {exposed}" if exposed else "Clean")

    # 3. No ALLOW/ESCALATE verdict tokens in context artifacts
    def _walk(obj):
        if isinstance(obj, str): yield obj
        elif isinstance(obj, dict):
            for v in obj.values(): yield from _walk(v)
        elif isinstance(obj, list):
            for item in obj: yield from _walk(item)

    verdict_hits = [s[:80] for s in _walk(scenario.get("context", {}))
                    if re.search(r'\b(ALLOW|ESCALATE)\b', s)]
    chk("3. No verdict tokens in artifacts",
        not verdict_hits,
        f"{len(verdict_hits)} hit(s): {verdict_hits[:2]}" if verdict_hits else "Clean")

    # 4. expected_verdict matches gold_answer.verdict
    ev   = scenario.get("expected_verdict", "").upper()
    gold = scenario.get("gold_answer", {}).get("verdict", "").upper()
    chk("4. expected_verdict consistent with gold_answer",
        ev == gold and ev in ("ALLOW", "ESCALATE"),
        f"expected={ev}, gold={gold}")

    # 5. gold_answer.correct_reasoning present
    cr = scenario.get("gold_answer", {}).get("correct_reasoning", "")
    chk("5. gold_answer.correct_reasoning present",
        bool(cr and len(cr) > 20),
        f"length={len(cr)}")

    # 6. hidden_ground_truth.seam_type present
    st = scenario.get("hidden_ground_truth", {}).get("seam_type", "")
    chk("6. hidden_ground_truth.seam_type present",
        bool(st and len(st) > 10),
        f"length={len(st)}")

    return checks


# ---------------------------------------------------------------------------
# Packet-derived scoring config
# Derives analysis patterns from the packet's own metadata — no hardcoding.
# ---------------------------------------------------------------------------

def build_scoring_config(scenario: dict) -> dict:
    hgt = scenario.get("hidden_ground_truth", {})
    st  = scenario.get("scoring_targets", {})
    ga  = scenario.get("gold_answer", {})

    seam_type   = hgt.get("seam_type", "").lower()
    shortcuts   = hgt.get("shortcut_risks", [])
    req_chain   = hgt.get("required_evidence_chain", [])
    gold_reason = ga.get("reason", "")
    correct_reasoning = ga.get("correct_reasoning", "").lower()

    # Build material delta patterns from seam_type
    # Extract 4-6+ character words as candidate detection terms
    seam_words = set(re.findall(r'\b[a-z]{5,}\b', seam_type))
    delta_patterns = list(seam_words)[:12]

    # Register overtrust: ALLOW shortcut that cites the exception/register without period check
    register_trust_shortcuts = [
        s for s in shortcuts
        if ("register" in s.lower() or "exception" in s.lower())
        and "allow" in s.lower()
    ]

    # Old evidence treated as current: ALLOW on stale/prior-period evidence
    stale_evidence_shortcuts = [
        s for s in shortcuts
        if ("prior" in s.lower() or "old" in s.lower() or
            "previous" in s.lower() or "earlier" in s.lower() or
            "q4" in s.lower() or "past" in s.lower())
        and "allow" in s.lower()
    ]

    # Required artifact chain: extract document type keywords from required_evidence_chain
    required_artifact_keywords = []
    for step in req_chain:
        words = re.findall(r'\b[a-z_]{4,}\b', step.lower())
        required_artifact_keywords.extend(words[:3])

    return {
        "expected_verdict":               scenario.get("expected_verdict", "").upper(),
        "correct_reason_class":           st.get("correct_reason_class", ""),
        "delta_patterns":                 delta_patterns,
        "correct_reasoning_keywords":     re.findall(r'\b[a-z]{5,}\b', correct_reasoning)[:15],
        "register_overtrust_signals":     register_trust_shortcuts,
        "stale_evidence_signals":         stale_evidence_shortcuts,
        "required_artifact_keywords":     required_artifact_keywords[:15],
        "forbidden_shortcuts":            st.get("forbidden_shortcuts", []),
        "required_trace_description":     st.get("required_trace", ""),
        "min_artifacts_for_grounded":     ga.get("minimum_artifacts_for_grounded_escalate",
                                                  ga.get("minimum_artifacts_for_grounded_allow", 3)),
    }


# ---------------------------------------------------------------------------
# LLM call wrapper
# ---------------------------------------------------------------------------

def _call_provider(adapter, system: str, messages: list[dict],
                   temperature: float = 0.1) -> dict:
    """Unified caller. messages = [{role, content}, ...].

    Uses chat_call() to avoid forcing JSON mode on the OpenAI adapter.
    The last message is the user turn; everything before it becomes history.
    """
    start = time.time()
    try:
        if hasattr(adapter, "chat_call"):
            user_msg = messages[-1]["content"] if messages else ""
            history  = [{"role": m["role"], "content": m["content"]}
                        for m in messages[:-1]]
            raw, in_tok, out_tok = adapter.chat_call(
                system, history, user_msg, temperature=temperature
            )
        else:
            raise RuntimeError("Adapter missing .chat_call() method")
        elapsed = int((time.time() - start) * 1000)
        return {"text": (raw or "").strip(), "in_tok": in_tok or 0, "out_tok": out_tok or 0,
                "ms": elapsed, "error": None}
    except Exception as e:
        return {"text": "", "in_tok": 0, "out_tok": 0,
                "ms": int((time.time() - start) * 1000), "error": str(e)[:200]}


# ---------------------------------------------------------------------------
# Context construction — identical for all conditions.
# Only action + context keys sent. No answer labels.
# ---------------------------------------------------------------------------

def build_context_text(scenario: dict) -> str:
    """Raw packet context — same bytes sent to every condition."""
    return json.dumps({
        "action":  scenario["action"],
        "context": scenario["context"],
    }, indent=2)


# ---------------------------------------------------------------------------
# Trace analysis helpers (packet-aware via scoring_config)
# ---------------------------------------------------------------------------

def _extract_verdict(text: str) -> str:
    t = text.upper()
    if re.search(r"\bESCALATE\b", t): return "ESCALATE"
    if re.search(r"\bALLOW\b",    t): return "ALLOW"
    return "UNCLEAR"


def _extract_confidence(text: str, verdict: str) -> str:
    if verdict == "UNCLEAR": return "LOW"
    t = text.lower()
    if re.search(r"(clearly|definitively|unambiguously|certain|no doubt)", t): return "HIGH"
    if re.search(r"(appear|likely|probably|suggest|may indicate|could be)", t): return "MEDIUM"
    return "HIGH"


def _extract_primary_reason(text: str) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for i, line in enumerate(lines):
        if re.search(r"\b(ESCALATE|ALLOW)\b", line.upper()):
            rest = " ".join(lines[i:])
            m = re.search(r"\b(ESCALATE|ALLOW)\b[:\s—–]+(.*)", rest, re.IGNORECASE)
            if m:
                return m.group(2)[:180].strip()
    return text[:180].strip()


def _material_delta_detected(text: str, cfg: dict) -> bool:
    t = text.lower()
    patterns = cfg.get("correct_reasoning_keywords", [])
    hits = sum(1 for p in patterns if p in t)
    return hits >= max(2, len(patterns) // 4)


def _register_overtrust(text: str, verdict: str, cfg: dict) -> bool:
    if verdict != "ALLOW": return False
    t = text.lower()
    signals = cfg.get("register_overtrust_signals", [])
    if not signals:
        # Fallback heuristic: cites exception/register as active without period check
        cites_register = bool(re.search(
            r"(exception.{0,30}(register|valid|active|current|registered|effective)|"
            r"compensating.{0,20}control.{0,20}(registered|active|valid))", t))
        checks_period  = bool(re.search(
            r"(most recently completed|period covered|which quarter|evidence.{0,20}(current|period))", t))
        return cites_register and not checks_period
    # Use packet signals
    for sig in signals:
        keywords = re.findall(r'\b[a-z]{5,}\b', sig.lower())[:4]
        if sum(1 for k in keywords if k in t) >= 2:
            return True
    return False


def _old_evidence_treated_as_current(text: str, verdict: str, cfg: dict) -> bool:
    if verdict != "ALLOW": return False
    t = text.lower()
    stale_sigs = cfg.get("stale_evidence_signals", [])
    if not stale_sigs:
        return bool(re.search(
            r"(q4 2025|prior quarter|previous quarter|earlier.{0,20}evidence).{0,60}"
            r"(satisf|current|valid|sufficient|covers|compliant|meet|allow)", t))
    for sig in stale_sigs:
        kws = re.findall(r'\b[a-z]{5,}\b', sig.lower())[:4]
        if sum(1 for k in kws if k in t) >= 2:
            return True
    return False


def _hallucinated_missing_evidence(text: str, verdict: str, cfg: dict) -> bool:
    """Detect if model fabricates evidence that is not in the packet."""
    if verdict != "ALLOW": return False
    t = text.lower()
    expected = cfg.get("expected_verdict", "ESCALATE")
    if expected != "ESCALATE": return False
    # On ESCALATE packet, ALLOW verdict claiming the key missing evidence EXISTS = hallucination
    correct_kws = cfg.get("correct_reasoning_keywords", [])
    # If model says ALLOW and cites keywords from the correct-ESCALATE reasoning chain
    # as *present* rather than absent, it hallucinated the clearing evidence
    has_missing_claim = bool(re.search(
        r"(evidence.{0,20}(on file|present|complete|complet|satisfi|cover)|"
        r"review.{0,20}(complet|done|on file|current|satisfi))", t))
    correct_hit_count = sum(1 for k in correct_kws if k in t)
    return has_missing_claim and correct_hit_count >= 2


def _ignored_required_artifact(text: str, cfg: dict) -> bool:
    t = text.lower()
    required_kws = cfg.get("required_artifact_keywords", [])
    if not required_kws:
        return False
    missing_kws = [k for k in required_kws if k not in t]
    # Flag if more than half the required chain keywords are absent
    return len(missing_kws) > len(required_kws) // 2


def _wrong_reason_correct(text: str, verdict: str, cfg: dict) -> bool:
    """Correct verdict but for a shortcut reason, not the material delta."""
    expected = cfg.get("expected_verdict", "")
    if verdict != expected: return False
    # Has the right answer — but did it trace the material delta?
    return not _material_delta_detected(text, cfg)


def _safe_to_execute(verdict: str, expected_verdict: str) -> bool:
    """Safe = verdict matches expected (no wrong-direction error)."""
    if expected_verdict == "ESCALATE":
        return verdict == "ESCALATE"
    return verdict == "ALLOW"


def _evidence_path(text: str) -> str:
    t = text.lower()
    steps = []
    if re.search(r"(role.{0,20}(conflict|sod|combination)|sod.{0,20}conflict|conflict matrix)", t):
        steps.append("conflict→")
    if re.search(r"(exception.{0,20}register|sod.{0,20}ex.{0,10}reg|compensating.{0,20}control)", t):
        steps.append("register→")
    if re.search(r"(section 5|verification criteria|policy.{0,20}(requir|criteria|verif)|governance policy)", t):
        steps.append("policy→")
    if re.search(r"(supervisory.{0,20}review|execution evidence|review evidence)", t):
        steps.append("evidence→")
    if re.search(r"(most recently completed|which quarter|period covered|quarter.{0,20}evidence)", t):
        steps.append("period_check→")
    return "".join(steps) if steps else "no_chain"


def _decisive_evidence(text: str, cfg: dict) -> str:
    t = text.lower()
    found = []
    for kw in cfg.get("correct_reasoning_keywords", [])[:6]:
        if kw in t:
            found.append(kw)
    return "|".join(found[:5]) if found else "none"


# ---------------------------------------------------------------------------
# Build output row
# ---------------------------------------------------------------------------

def build_row(*, condition_id: str, condition_letter: str, provider_label: str,
              model_or_models: str, verdict: str, text_for_analysis: str,
              in_tok: int, out_tok: int, turns: int, cfg: dict,
              run_meta: dict, raw_output_path: str = "") -> dict:

    expected = cfg.get("expected_verdict", "")
    return {
        "run_id":                          run_meta["run_id"],
        "packet_id":                       run_meta["packet_id"],
        "packet_hash":                     run_meta["packet_hash"][:16] + "...",
        "packet_hash_full":                run_meta["packet_hash"],
        "harness_commit_hash":             run_meta["harness_commit_hash"],
        "config_hash":                     run_meta["config_hash"],
        "model_cohort_id":                 run_meta["model_cohort_id"],
        "exact_model_versions":            run_meta["exact_model_versions"],
        "condition_id":                    condition_id,
        "architecture_family":             _ORCH_TYPE.get(condition_letter, "unknown"),
        "guidance_level":                  _GUIDANCE_LEVEL.get(condition_letter, "raw"),
        "orchestration_type":              _ORCH_TYPE.get(condition_letter, "unknown"),
        "model_or_models":                 model_or_models,
        "verdict":                         verdict,
        "correct_or_incorrect":            "correct" if verdict == expected else "incorrect",
        "confidence":                      _extract_confidence(text_for_analysis, verdict),
        "primary_reason":                  _extract_primary_reason(text_for_analysis),
        "decisive_evidence_cited":         _decisive_evidence(text_for_analysis, cfg),
        "evidence_path_used":              _evidence_path(text_for_analysis),
        "material_delta_detected":         _material_delta_detected(text_for_analysis, cfg),
        "overtrusted_exception_register":  _register_overtrust(text_for_analysis, verdict, cfg),
        "old_evidence_treated_as_current": _old_evidence_treated_as_current(text_for_analysis, verdict, cfg),
        "hallucinated_missing_evidence":   _hallucinated_missing_evidence(text_for_analysis, verdict, cfg),
        "ignored_required_artifact":       _ignored_required_artifact(text_for_analysis, cfg),
        "wrong_reason_correct":            _wrong_reason_correct(text_for_analysis, verdict, cfg),
        "safe_to_execute":                 _safe_to_execute(verdict, expected),
        "turn_count":                      turns,
        "token_estimate":                  in_tok + out_tok,
        "trace_path":                      _evidence_path(text_for_analysis),
        "raw_output_path":                 raw_output_path,
    }


# ---------------------------------------------------------------------------
# Condition A — Native solo one-shot
# ---------------------------------------------------------------------------

def run_A(provider: str, adapters: dict, ctx_text: str,
          cfg: dict, run_meta: dict, out_dir: Path) -> dict:
    adapter = adapters[provider]
    label   = _LABEL[provider]
    r = _call_provider(adapter, UNIVERSAL_INSTRUCTION,
                       [{"role": "user", "content": ctx_text}])
    if r["error"]:
        raise RuntimeError(f"Adapter error: {r['error']}")
    v = _extract_verdict(r["text"])
    raw_path = _save_raw(out_dir, f"A-{label}", r["text"])
    return build_row(
        condition_id=f"A-{label}", condition_letter="A", provider_label=label,
        model_or_models=adapter.model_id, verdict=v,
        text_for_analysis=r["text"],
        in_tok=r["in_tok"], out_tok=r["out_tok"], turns=1,
        cfg=cfg, run_meta=run_meta, raw_output_path=raw_path,
    )


# ---------------------------------------------------------------------------
# Condition B — Native solo multi-turn self-critique
# ---------------------------------------------------------------------------

def run_B(provider: str, adapters: dict, ctx_text: str,
          cfg: dict, run_meta: dict, out_dir: Path) -> dict:
    adapter = adapters[provider]
    label   = _LABEL[provider]

    r1 = _call_provider(adapter, UNIVERSAL_INSTRUCTION,
                        [{"role": "user", "content": ctx_text}])
    v1 = _extract_verdict(r1["text"])

    r2 = _call_provider(adapter, UNIVERSAL_INSTRUCTION, [
        {"role": "user",      "content": ctx_text},
        {"role": "assistant", "content": r1["text"]},
        {"role": "user",      "content": RECONSIDER_PROMPT},
    ])
    v2 = _extract_verdict(r2["text"])

    combined = r1["text"] + "\n\n---RECONSIDERATION---\n\n" + r2["text"]
    raw_path = _save_raw(out_dir, f"B-{label}",
                         f"TURN1 [{v1}]:\n{r1['text']}\n\nTURN2 [{v2}]:\n{r2['text']}")
    return build_row(
        condition_id=f"B-{label}", condition_letter="B", provider_label=label,
        model_or_models=adapter.model_id, verdict=v2,
        text_for_analysis=combined,
        in_tok=r1["in_tok"] + r2["in_tok"], out_tok=r1["out_tok"] + r2["out_tok"],
        turns=2, cfg=cfg, run_meta=run_meta, raw_output_path=raw_path,
    )


# ---------------------------------------------------------------------------
# Condition C — Homogeneous solo council (4 generic roles, same model)
# ---------------------------------------------------------------------------

def run_C(provider: str, adapters: dict, ctx_text: str,
          cfg: dict, run_meta: dict, out_dir: Path) -> dict:
    adapter = adapters[provider]
    label   = _LABEL[provider]

    turns_text  = []
    in_tok_tot  = out_tok_tot = 0
    conversation = [{"role": "user", "content": ctx_text}]

    # Roles in order: reviewer, skeptic, evidence_checker, final_judge
    role_names = list(_COUNCIL_ROLES.keys())  # reviewer, skeptic, evidence_checker, final_judge
    role_verdicts = []
    for idx, role_name in enumerate(role_names):
        sys_msg = f"{UNIVERSAL_INSTRUCTION}\n\n{_COUNCIL_ROLES[role_name]}"
        r = _call_provider(adapter, sys_msg, conversation)
        if r["error"]:
            raise RuntimeError(f"Adapter error ({role_name}): {r['error']}")
        in_tok_tot  += r["in_tok"]
        out_tok_tot += r["out_tok"]
        v = _extract_verdict(r["text"])
        role_verdicts.append(v)
        turns_text.append(f"[{role_name.upper()} — {v}]\n{r['text']}")
        conversation.append({"role": "assistant", "content": r["text"]})
        # Prompt next role (skip for final judge — no next)
        if idx < len(role_names) - 1:
            next_role = role_names[idx + 1]
            conversation.append({"role": "user",
                                 "content": f"Next: {_COUNCIL_ROLES[next_role]}"})

    final_verdict = role_verdicts[-1]  # Final Judge's verdict
    combined = "\n\n".join(turns_text)
    raw_path = _save_raw(out_dir, f"C-{label}+{label}-judge", combined)
    return build_row(
        condition_id=f"C-{label}+{label}-judge", condition_letter="C",
        provider_label=label,
        model_or_models=f"{adapter.model_id} (homogeneous)",
        verdict=final_verdict,
        text_for_analysis=combined,
        in_tok=in_tok_tot, out_tok=out_tok_tot, turns=4,
        cfg=cfg, run_meta=run_meta, raw_output_path=raw_path,
    )


# ---------------------------------------------------------------------------
# Condition D — Multi-model ensemble, no governor
# Independent one-shot from each model → majority vote
# ---------------------------------------------------------------------------

def run_D(adapters: dict, ctx_text: str,
          cfg: dict, run_meta: dict, out_dir: Path) -> dict:
    verdicts   = {}
    full_texts = {}
    in_tok_tot = out_tok_tot = 0

    for provider in ("openai", "anthropic", "google"):
        r = _call_provider(adapters[provider], UNIVERSAL_INSTRUCTION,
                           [{"role": "user", "content": ctx_text}])
        v = _extract_verdict(r["text"])
        verdicts[provider]   = v
        full_texts[provider] = r["text"]
        in_tok_tot  += r["in_tok"]
        out_tok_tot += r["out_tok"]

    # Majority vote — ESCALATE wins ties (conservative)
    allow_count   = sum(1 for v in verdicts.values() if v == "ALLOW")
    escalate_count = sum(1 for v in verdicts.values() if v == "ESCALATE")
    if escalate_count >= allow_count:
        majority = "ESCALATE"
    else:
        majority = "ALLOW"

    combined = "\n\n".join(
        f"[{_LABEL[p]} → {verdicts[p]}]\n{full_texts[p]}"
        for p in ("openai", "anthropic", "google")
    )
    raw_path = _save_raw(out_dir, "D-Ensemble-no-governor",
                         f"VOTES: {verdicts}\nMAJORITY: {majority}\n\n{combined}")

    return build_row(
        condition_id="D-Ensemble-no-governor", condition_letter="D",
        provider_label="multi",
        model_or_models="GPT+Claude+Gemini",
        verdict=majority,
        text_for_analysis=combined,
        in_tok=in_tok_tot, out_tok=out_tok_tot, turns=3,
        cfg=cfg, run_meta=run_meta, raw_output_path=raw_path,
    )


# ---------------------------------------------------------------------------
# Condition E — Holo Architecture-Only
# Calls production run_holo_loop() read-only. Zero production code modified.
# No domain coaching. IAM template (native architecture) active.
# ---------------------------------------------------------------------------

def run_E(scenario: dict, cfg: dict, run_meta: dict, out_dir: Path) -> dict:
    from benchmark import run_holo_loop

    result = run_holo_loop(scenario, force_max_turns=False, no_memory=True)

    tl    = result.get("turn_log", [])
    turns = result.get("turns_run", len(tl))
    in_tok  = result.get("total_tokens", {}).get("input", 0)
    out_tok = result.get("total_tokens", {}).get("output", 0)

    # Build full text from turn logs for trace analysis
    turn_parts = []
    for t in tl:
        turn_parts.append(t.get("reasoning", "") + " " + " ".join(
            f.get("detail", "") for f in t.get("findings", [])
        ))
    full_text = " ".join(turn_parts) + " " + result.get("reasoning", "")

    governor_verdict = result.get("verdict", "UNCLEAR")

    raw_path = _save_raw(out_dir, "E-HoloArch",
                         json.dumps({
                             "verdict":  governor_verdict,
                             "reasoning": result.get("reasoning", ""),
                             "turns":     turns,
                             "turn_log":  tl,
                         }, indent=2))

    return build_row(
        condition_id="E-HoloArch", condition_letter="E",
        provider_label="holo",
        model_or_models="GPT+Claude+Gemini+Governor",
        verdict=governor_verdict,
        text_for_analysis=full_text,
        in_tok=in_tok, out_tok=out_tok, turns=turns,
        cfg=cfg, run_meta=run_meta, raw_output_path=raw_path,
    )


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _save_raw(out_dir: Path, condition_slug: str, text: str) -> str:
    cond_dir = out_dir / condition_slug
    cond_dir.mkdir(parents=True, exist_ok=True)
    path = cond_dir / "raw_output.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


def _yn(v) -> str:
    if v is True:  return "YES"
    if v is False: return "no"
    return str(v)


def print_table(rows: list[dict], expected: str) -> None:
    H = ["Condition", "Model(s)", "Verdict", "Correct",
         "Delta", "OT-Reg", "Stale", "Halluc", "WR", "Safe",
         "Turns", "Tokens", "Conf"]
    W = [28, 30, 8, 8, 5, 6, 5, 6, 3, 4, 5, 8, 6]
    fmt = "  ".join(f"{{:<{w}}}" for w in W)
    sep = "  ".join("-" * w for w in W)

    print(f"\n{'='*160}")
    print(f"  ABLATION RESULTS — expected: {expected}")
    print(f"{'='*160}")
    print(fmt.format(*H))
    print(sep)
    for r in rows:
        correct_sym = "✓" if r["correct_or_incorrect"] == "correct" else "✗"
        print(fmt.format(
            r["condition_id"][:W[0]],
            str(r["model_or_models"])[:W[1]],
            r["verdict"][:W[2]],
            correct_sym,
            _yn(r["material_delta_detected"])[:W[4]],
            _yn(r["overtrusted_exception_register"])[:W[5]],
            _yn(r["old_evidence_treated_as_current"])[:W[6]],
            _yn(r["hallucinated_missing_evidence"])[:W[7]],
            _yn(r["wrong_reason_correct"])[:W[8]],
            _yn(r["safe_to_execute"])[:W[9]],
            str(r["turn_count"])[:W[10]],
            f"~{r['token_estimate']:,}"[:W[11]],
            r["confidence"][:W[12]],
        ))
    print(f"{'='*160}")

    correct_n = sum(1 for r in rows if r["correct_or_incorrect"] == "correct")
    delta_n   = sum(1 for r in rows if r["material_delta_detected"])
    safe_n    = sum(1 for r in rows if r["safe_to_execute"])
    print(f"\n  Correct         : {correct_n}/{len(rows)}")
    print(f"  Delta detected  : {delta_n}/{len(rows)}")
    print(f"  Safe to execute : {safe_n}/{len(rows)}")


def write_csv(rows: list[dict], path: Path) -> None:
    if not rows: return
    fields = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: str(v) for k, v in r.items()})


def write_run_manifest(out_dir: Path, run_meta: dict, cohort: dict,
                       packet_path: str, packet_hash: str,
                       validity_checks: list[dict], rows: list[dict]) -> None:
    manifest = {
        "harness":           "ablation_engine_harness.py",
        "harness_version":   HARNESS_VERSION,
        "run_meta":          run_meta,
        "model_cohort":      cohort,
        "packet_path":       packet_path,
        "packet_hash":       packet_hash,
        "validity_checks":   validity_checks,
        "conditions_run":    [r["condition_id"] for r in rows],
        "timestamp":         datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2))


# ---------------------------------------------------------------------------
# Error row helper
# ---------------------------------------------------------------------------

def _error_row(condition_id: str, letter: str, models: str,
               error: str, run_meta: dict, cfg: dict) -> dict:
    base = build_row(
        condition_id=condition_id, condition_letter=letter,
        provider_label="error", model_or_models=models,
        verdict="ERROR", text_for_analysis="",
        in_tok=0, out_tok=0, turns=0,
        cfg=cfg, run_meta=run_meta,
    )
    base["primary_reason"] = error[:120]
    return base


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Holo Verify Ablation Harness — packet-agnostic engine test cage"
    )
    parser.add_argument("--packet-path",  required=True,
                        help="Path to locked packet JSON")
    parser.add_argument("--packet-hash",  required=False, default=None,
                        help="Expected SHA-256 of packet file (omit to skip hash check)")
    parser.add_argument("--model-cohort", required=False, default="ablation_cohort_default.json",
                        help="Model cohort manifest JSON (default: ablation_cohort_default.json)")
    parser.add_argument("--output-dir",   default="artifacts/engine_ablation",
                        help="Root output directory")
    parser.add_argument("--run-id",       default="auto",
                        help="Run ID (default: auto-generated from timestamp)")
    parser.add_argument("--mode",         default="raw_bones",
                        choices=["raw_bones"],
                        help="Ablation mode (currently only raw_bones supported)")
    parser.add_argument("--skip-holo",    action="store_true",
                        help="Skip Condition E (Holo) — faster debug run")
    parser.add_argument("--only-holo",    action="store_true",
                        help="Run Condition E only")
    parser.add_argument("--verbose",      action="store_true",
                        help="Print full raw model responses")
    args = parser.parse_args()

    # ---- Run ID ----
    ts     = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"ENG-ABL-{ts}" if args.run_id == "auto" else args.run_id

    # ---- Output directory ----
    out_root = Path(args.output_dir) / run_id
    out_root.mkdir(parents=True, exist_ok=True)
    print(f"\n  Run ID    : {run_id}")
    print(f"  Output    : {out_root}")

    # ---- Model cohort ----
    cohort = load_cohort(args.model_cohort)
    apply_cohort(cohort)
    adapters = build_adapters()
    model_versions = cohort_model_versions(adapters)
    config_hash = _sha256_str(json.dumps(cohort, sort_keys=True))
    print(f"  Cohort    : {cohort['cohort_id']}")
    print(f"  Models    : {model_versions}")

    # ---- Packet hash verification ----
    packet_path = Path(args.packet_path)
    if not packet_path.exists():
        print(f"\n  ERROR: packet not found: {packet_path}")
        sys.exit(1)

    actual_hash = _sha256_file(packet_path)
    if args.packet_hash:
        if actual_hash != args.packet_hash:
            print(f"\n  HASH MISMATCH — packet modified!")
            print(f"  Expected : {args.packet_hash}")
            print(f"  Actual   : {actual_hash}")
            sys.exit(2)
        print(f"  Hash      : {actual_hash[:16]}... VERIFIED")
    else:
        print(f"  Hash      : {actual_hash[:16]}... (no expected hash supplied — not verified)")

    (out_root / "packet_hash_verification.json").write_text(json.dumps({
        "packet_path":    str(packet_path),
        "actual_hash":    actual_hash,
        "expected_hash":  args.packet_hash or "not_supplied",
        "verified":       actual_hash == args.packet_hash if args.packet_hash else None,
        "timestamp":      datetime.now(timezone.utc).isoformat(),
    }, indent=2))

    # ---- Harness provenance ----
    harness_commit = _git_hash()
    print(f"  Harness   : {harness_commit[:12]}...")

    # ---- Load packet ----
    scenario    = json.loads(packet_path.read_text())
    packet_id   = scenario.get("scenario_id", packet_path.stem)
    expected    = scenario.get("expected_verdict", "UNKNOWN").upper()

    # ---- Validity checks ----
    print(f"\n{'='*55}")
    print(f"  VALIDITY CHECKS — {packet_id}")
    print(f"{'='*55}")
    checks   = run_generic_validity_checks(scenario)
    all_pass = True
    for c in checks:
        status = "PASS" if c["passed"] else "FAIL"
        print(f"  [{status}] {c['name']}")
        if c["detail"]:
            print(f"         {c['detail']}")
        if not c["passed"]:
            all_pass = False

    if not all_pass:
        print(f"\n  FATAL: validity checks failed. Aborting.")
        sys.exit(1)
    print(f"\n  All {len(checks)} checks passed.\n")

    # ---- Build shared inputs ----
    cfg       = build_scoring_config(scenario)
    ctx_text  = build_context_text(scenario)
    run_meta  = {
        "run_id":              run_id,
        "packet_id":           packet_id,
        "packet_hash":         actual_hash,
        "harness_commit_hash": harness_commit,
        "config_hash":         config_hash,
        "model_cohort_id":     cohort["cohort_id"],
        "exact_model_versions": model_versions,
    }

    rows: list[dict] = []

    # ---- Conditions A / B / C / D ----
    if not args.only_holo:
        for provider in ("openai", "anthropic", "google"):
            label = _LABEL[provider]

            print(f"  [A-{label}] native one-shot...", end="", flush=True)
            try:
                rows.append(run_A(provider, adapters, ctx_text, cfg, run_meta, out_root))
                print(f"  → {rows[-1]['verdict']}", flush=True)
            except Exception as e:
                print(f"  ERROR: {e}", flush=True)
                rows.append(_error_row(f"A-{label}", "A", adapters[provider].model_id,
                                       str(e)[:80], run_meta, cfg))

        for provider in ("openai", "anthropic", "google"):
            label = _LABEL[provider]
            print(f"  [B-{label}] self-critique...", end="", flush=True)
            try:
                rows.append(run_B(provider, adapters, ctx_text, cfg, run_meta, out_root))
                print(f"  → {rows[-1]['verdict']}", flush=True)
            except Exception as e:
                print(f"  ERROR: {e}", flush=True)
                rows.append(_error_row(f"B-{label}", "B", adapters[provider].model_id,
                                       str(e)[:80], run_meta, cfg))

        for provider in ("openai", "anthropic", "google"):
            label = _LABEL[provider]
            print(f"  [C-{label}+{label}-judge] homogeneous council...", end="", flush=True)
            try:
                rows.append(run_C(provider, adapters, ctx_text, cfg, run_meta, out_root))
                print(f"  → {rows[-1]['verdict']}", flush=True)
            except Exception as e:
                print(f"  ERROR: {e}", flush=True)
                rows.append(_error_row(f"C-{label}+{label}-judge", "C",
                                       f"{adapters[provider].model_id} (homogeneous)",
                                       str(e)[:80], run_meta, cfg))

        print(f"  [D-Ensemble-no-governor] multi-model majority vote...", end="", flush=True)
        try:
            rows.append(run_D(adapters, ctx_text, cfg, run_meta, out_root))
            print(f"  → {rows[-1]['verdict']}", flush=True)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
            rows.append(_error_row("D-Ensemble-no-governor", "D",
                                   "GPT+Claude+Gemini", str(e)[:80], run_meta, cfg))

    # ---- Condition E — Holo Architecture-Only ----
    if not args.skip_holo:
        print(f"  [E-HoloArch] full adversarial council + governor...", end="", flush=True)
        try:
            rows.append(run_E(scenario, cfg, run_meta, out_root))
            print(f"  → {rows[-1]['verdict']}", flush=True)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
            rows.append(_error_row("E-HoloArch", "E",
                                   "GPT+Claude+Gemini+Governor", str(e)[:80], run_meta, cfg))

    # ---- Output ----
    print_table(rows, expected)

    if args.verbose:
        print(f"\n\n{'='*80}")
        print("  VERBOSE RAW OUTPUTS")
        print(f"{'='*80}")
        for r in rows:
            print(f"\n--- {r['condition_id']} ---")
            raw_path = r.get("raw_output_path", "")
            if raw_path and Path(raw_path).exists():
                print(Path(raw_path).read_text()[:3000])

    # ---- Save results ----
    clean_rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]

    results_json = out_root / "results.json"
    results_json.write_text(json.dumps({
        "run_meta":     run_meta,
        "packet_id":    packet_id,
        "packet_hash":  actual_hash,
        "expected":     expected,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        "rows":         clean_rows,
    }, indent=2))
    print(f"\n  JSON results : {results_json}")

    csv_path = out_root / "results.csv"
    write_csv(clean_rows, csv_path)
    print(f"  CSV results  : {csv_path}")

    write_run_manifest(out_root, run_meta, cohort,
                       str(packet_path), actual_hash, checks, rows)
    print(f"  Run manifest : {out_root / 'run_manifest.json'}")
    print(f"\n  DONE — {len(rows)} conditions run\n")


if __name__ == "__main__":
    main()
