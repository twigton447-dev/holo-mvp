"""
llm_adapters.py

Handles all direct API calls to OpenAI, Anthropic, and Google.
Each adapter receives the full shared state object and returns a
standardized TurnResult so the Context Governor can treat all
three providers identically.

Model defaults (override via .env):
  OPENAI_MODEL    = gpt-5.4
  ANTHROPIC_MODEL = claude-sonnet-4-6
  GOOGLE_MODEL    = gemini-2.5-pro-preview
  GOVERNOR_MODEL  = gemini-2.0-flash  (fast/cheap — runs between every turn)
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("holo.adapters")

# ---------------------------------------------------------------------------
# Shared output schema
# ---------------------------------------------------------------------------

BEC_CATEGORIES = [
    "sender_identity",
    "invoice_amount",
    "payment_routing",
    "urgency_pressure",
    "domain_spoofing",
    "approval_chain",
]

SEVERITY_VALUES = {"NONE", "LOW", "MEDIUM", "HIGH"}
SEVERITY_RANK   = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}


@dataclass
class TurnResult:
    """
    Standardized output from a single model turn.
    The Context Governor only ever sees TurnResult objects —
    it has no knowledge of which provider produced it.
    """
    provider: str           # "openai" | "anthropic" | "google"
    model_id: str           # exact model string used
    role: str               # adversarial role for this turn
    turn_number: int

    verdict: str            # "ALLOW" | "ESCALATE"
    reasoning: str          # model's full narrative reasoning (the postmortem)
    severity_flags: dict    # {category: "LOW"|"MEDIUM"|"HIGH"|"NONE"}
    findings: list          # [{category, severity, evidence, detail}]

    raw_response: str = ""  # original text from the API, for debugging
    input_tokens: int = 0
    output_tokens: int = 0
    system_prompt: str = ""   # exact system prompt sent to this model this turn
    user_message: str = ""    # exact user message sent to this model this turn

    def to_dict(self) -> dict:
        return {
            "turn_number":    self.turn_number,
            "provider":       self.provider,
            "model_id":       self.model_id,
            "role":           self.role,
            "verdict":        self.verdict,
            "reasoning":      self.reasoning,
            "severity_flags": self.severity_flags,
            "findings":       self.findings,
            "input_tokens":   self.input_tokens,
            "output_tokens":  self.output_tokens,
            "system_prompt":  self.system_prompt,
            "user_message":   self.user_message,
        }


# ---------------------------------------------------------------------------
# Prompt construction (shared across all providers)
# ---------------------------------------------------------------------------

ROLE_INSTRUCTIONS = {
    "Initial Assessment": """
You are the FIRST analyst. No prior assessments exist.
Evaluate each of the six BEC risk categories from scratch using only the
submitted action payload and context. Be specific: cite exact field values
or email content as evidence. Do not speculate without evidence.
""",

    "Assumption Attacker": """
You are a professional fraud investigator whose job is to dismantle the prior
analysts' conclusions. Treat every finding in the turn history as an UNVERIFIED
EXTERNAL HYPOTHESIS.

Ask: Where did prior analysts over-weight a signal? Where did they accept an
explanation too readily? Challenge every LOW rating — should it be MEDIUM?
Challenge every rationalization — is it actually supported by hard evidence
in the submitted data?

Independence is required. But independence does NOT mean manufacturing
disagreement — if prior ALLOW ratings are well-supported, confirming them
is the correct call. Do not escalate without citing specific evidence.
""",

    "Edge Case Hunter": """
You are a specialist in sophisticated fraud patterns. Prior analysts have
already assessed this. Your job is to find what ALL of them missed.

Think like an attacker: What combination of LOW-severity signals, taken
together, indicates HIGH risk? What would a sophisticated actor do to make
this look legitimate? Are there internal contradictions in the prior findings
that nobody has called out?

CRITICAL — Intellectual honesty rule:
If prior analysts returned ALLOW with LOW/NONE severities and you cannot
identify a CONCRETE, ARTICULABLE signal backed by specific field values or
text from the submitted data, you MUST return ALLOW. Do NOT manufacture
concerns. A clean evaluation is a valid and valuable outcome.
""",

    "Evidence Pressure Tester": """
You are a skeptical compliance auditor who trusts nothing that cannot be
verified from the submitted data. Review all prior findings.

For every category rated LOW or NONE: demand to know what hard evidence
supports that rating. Assumption is not evidence. Plausibility is not
evidence. Only specific field values and quoted text from the submitted
data qualify.

For every ALLOW verdict: force it to earn the rating with hard evidence,
not narrative explanation.
""",

    "Devil's Advocate": """
You are a senior analyst stress-testing the emerging consensus.
Review all prior findings and deliberately argue against the majority direction.

If prior analysts are leaning ESCALATE: argue the strongest possible case for
ALLOW — find every legitimate explanation that has been underweighted.
If prior analysts are leaning ALLOW: argue the strongest case for ESCALATE —
find every risk signal that has been rationalized away.

Your goal is not to flip the verdict arbitrarily but to ensure the consensus
has been genuinely tested. Surface weak points before the governor decides.
""",

    "Former Attacker": """
You are a reformed BEC attacker reviewing this submission as if you had
designed the attack yourself. You know every technique, every social
engineering vector, every cover story that sophisticated attackers use.

Ask: If I were executing this attack, what would I have done to make it
look exactly like this? Which signals in the prior analysis are the ones
I would have planted to distract from the real vector? What has every
prior analyst been anchored to that I deliberately engineered?

Apply your operational knowledge. Do not theorize — look for specific
mechanics in the submitted data that match known attack patterns.
""",

    "Forensic Accountant": """
You are a forensic accountant who has testified in wire fraud cases.
Follow the money with surgical precision.

Focus relentlessly on: the exact payment amount vs. historical range,
the routing and account details and what institution they resolve to,
the invoice structure vs. prior invoices, and any financial justifications
that cannot be verified from the submitted data.

Numbers don't lie. Narrative explanations do. Prioritize the quantitative
evidence and flag any financial inconsistency, however minor.
""",

    "Social Engineering Specialist": """
You are a social engineering specialist. Your job is to identify the
psychological manipulation mechanics in this submission.

Look for: urgency signals designed to bypass deliberation, authority claims
that cannot be verified, name-dropping of known parties to manufacture
legitimacy, narrative framing that makes the request feel routine,
and any emotional or time-pressure tactics in the email text.

Prior analysts may have assessed the technical signals. Your focus is the
human manipulation layer that sophisticated attackers use to override
careful review.
""",

    "Compliance Auditor": """
You are a compliance auditor evaluating this transaction against stated
organizational policy and standard AP controls.

Evaluate each prior finding against the org_policies field in the context
and standard AP workflow norms. Does this transaction comply with the
documented approval chain? Are there policy violations that prior analysts
treated as minor? Does the documentation trail meet the standards required
before a wire of this magnitude should be released?

Policy compliance is binary. Either the documentation exists or it doesn't.
""",

    "Final Skeptic": """
You are the last adversarial analyst before the governor decides. Everything
prior analysts have said is now your raw material.

Your job: find the single most important signal that the accumulated analysis
has underweighted or missed entirely. Not a list — ONE finding. The one thing
that, if it is what it appears to be, changes the verdict.

If you cannot find it despite genuine adversarial effort, say so clearly and
return ALLOW. The governor needs your honest final assessment, not a
manufactured concern.
""",
}

# Ordered sequence — each persona runs at most once per evaluation.
# The governor cycles through this list; convergence exits the loop early
# when the soil is fully rototilled and no new signals can be surfaced.
PERSONA_SEQUENCE = [
    "Initial Assessment",       # turn 1 — always first, sets the baseline
    "Assumption Attacker",      # turn 2 — dismantles turn 1
    "Edge Case Hunter",         # turn 3 — finds what both missed
    "Evidence Pressure Tester", # turn 4 — forces every ALLOW to earn it
    "Devil's Advocate",         # turn 5 — stress-tests emerging consensus
    "Former Attacker",          # turn 6 — operational attack pattern recognition
    "Forensic Accountant",      # turn 7 — follows the money
    "Social Engineering Specialist", # turn 8 — human manipulation layer
    "Compliance Auditor",       # turn 9 — policy and process compliance
    "Final Skeptic",            # turn 10 — last adversarial pressure
]


# Maps each persona to the BEC categories it specializes in.
# Used by the governor to fill coverage gaps after the first 3 turns.
PERSONA_SPECIALIZATIONS = {
    "Initial Assessment":          [],  # covers everything from scratch
    "Assumption Attacker":         [],  # attacks all prior reasoning
    "Edge Case Hunter":            [],  # finds hidden combinations
    "Evidence Pressure Tester":    ["invoice_amount", "payment_routing"],
    "Devil's Advocate":            [],  # consensus stress-test
    "Former Attacker":             ["sender_identity", "domain_spoofing", "approval_chain"],
    "Forensic Accountant":         ["invoice_amount", "payment_routing"],
    "Social Engineering Specialist": ["urgency_pressure", "approval_chain", "sender_identity"],
    "Compliance Auditor":          ["approval_chain", "urgency_pressure"],
    "Final Skeptic":               [],  # general final pressure
}


def get_role_for_turn(turn_number: int) -> str:
    """
    Return the fixed persona for turns 1–3 (the baseline adversarial sequence).
    Turns beyond 3 are handled by the governor's dynamic selection.
    """
    idx = min(turn_number - 1, len(PERSONA_SEQUENCE) - 1)
    return PERSONA_SEQUENCE[idx]


def select_persona(coverage: dict, used_personas: set) -> str:
    """
    Governor-driven dynamic persona selection for turns 4+.

    Reads the coverage matrix to identify weak categories (NONE or LOW),
    then picks the available persona whose specializations best address them.
    Falls back to the next unused persona in sequence if no gap match found.
    """
    available = [p for p in PERSONA_SEQUENCE if p not in used_personas]
    if not available:
        return "Final Skeptic"

    # Find categories still weak (NONE or LOW)
    weak = {
        cat for cat, v in coverage.items()
        if not v["addressed"] or v["max_severity"] in ("NONE", "LOW")
    }

    if weak:
        for persona in available:
            specs = set(PERSONA_SPECIALIZATIONS.get(persona, []))
            if specs & weak:  # this persona covers at least one weak category
                return persona

    # No gap match — return next in sequence
    return available[0]


def build_system_prompt(role: str) -> str:
    instructions = ROLE_INSTRUCTIONS.get(role, ROLE_INSTRUCTIONS["Assumption Attacker"])
    return f"""You are a Business Email Compromise (BEC) risk analyst operating inside
Holo, an AI trust layer that evaluates proposed financial actions before they execute.

=== YOUR ROLE THIS TURN: {role} ===
{instructions.strip()}

=== THE SIX BEC RISK CATEGORIES YOU MUST ASSESS ===
1. sender_identity   — Is the sender verifiably who they claim to be?
2. invoice_amount    — Is the amount consistent with the established vendor relationship?
3. payment_routing   — Has the payment destination changed unexpectedly?
4. urgency_pressure  — Is there unusual urgency or pressure to bypass normal process?
5. domain_spoofing   — Are there email header or domain red flags?
6. approval_chain    — Does this transaction comply with normal approval procedures?

=== SEVERITY SCALE ===
HIGH   → Clear, specific evidence of BEC risk. Forces ESCALATE.
MEDIUM → Suspicious signals warranting scrutiny.
LOW    → Category appears clean based on available evidence.
NONE   → Insufficient evidence to assess this category.

=== CRITICAL RULES ===
- Every finding MUST cite specific field values or text from the submitted data.
- Do not fabricate evidence. If you cannot find support, rate NONE.
- If a category is genuinely clean, say so clearly. Rating LOW or NONE is a valid
  professional judgment — do not inflate severity to appear thorough.
- When in doubt between ALLOW and ESCALATE, choose ESCALATE.
- You MUST assess all six categories, even if some are NONE.

=== INTEGRITY RULE (OVERRIDES ROLE INSTRUCTIONS) ===
Your role may instruct you to challenge, pressure-test, or hunt for risks.
That does NOT mean you must manufacture findings. If a category is genuinely
clean and you cannot cite a SPECIFIC field value or text from the submitted
data as evidence, you MUST rate it LOW or NONE. Inflating severity without
concrete evidence is a model failure. A clean result is a valid outcome.

=== REQUIRED RESPONSE FORMAT ===
Respond with a single valid JSON object and NOTHING ELSE.
No markdown fences, no preamble, no explanation outside the JSON.

{{
  "verdict": "ALLOW" or "ESCALATE",
  "reasoning_summary": "3-5 sentences covering your overall assessment, key evidence, and any disagreement with prior analysts",
  "severity_flags": {{
    "sender_identity":  "HIGH|MEDIUM|LOW|NONE",
    "invoice_amount":   "HIGH|MEDIUM|LOW|NONE",
    "payment_routing":  "HIGH|MEDIUM|LOW|NONE",
    "urgency_pressure": "HIGH|MEDIUM|LOW|NONE",
    "domain_spoofing":  "HIGH|MEDIUM|LOW|NONE",
    "approval_chain":   "HIGH|MEDIUM|LOW|NONE"
  }},
  "findings": [
    {{
      "category":  "<one of the six category keys>",
      "severity":  "HIGH|MEDIUM|LOW|NONE",
      "fact_type": "SUBMITTED_DATA|INFERRED|POLICY_VIOLATION",
      "evidence":  "<exact quote or field reference from the submitted data>",
      "detail":    "<your analysis of why this is flagged at this severity>"
    }}
  ]
}}

fact_type rules:
  SUBMITTED_DATA   → evidence is a direct quote or field value from the action payload,
                     email text, vendor record, or sender history. The strongest grade.
  POLICY_VIOLATION → finding is a direct violation of the org_policies field.
  INFERRED         → you drew a conclusion not directly stated in the submitted data.
                     Valid, but carries less weight than SUBMITTED_DATA.
Always assign the most accurate fact_type. Do not inflate to SUBMITTED_DATA if you
are drawing an inference."""


def _retrieve_artifact(state: dict, artifact_id: str):
    """
    Retrieve artifact content by ID from the Artifact Registry.

    PINNED semantics (patent §4.7): always returns full content at full
    fidelity — never summarized, never dropped.  Returns None if the
    artifact does not exist in the registry.
    """
    entry = state.get("artifacts", {}).get(artifact_id)
    return entry["content"] if entry else None


def build_user_message(state: dict, turn_number: int) -> str:
    """
    Builds the user message containing:
    - The action being evaluated (never changes)
    - The context bundle (never changes)
    - The full turn history so far (the rototilling)
    - The governor brief for this turn (if one exists)
    """
    # Retrieve source artifacts by ID (PINNED — always full fidelity).
    # Falls back to direct dict access for backwards compatibility.
    action   = _retrieve_artifact(state, "action_v1")  or state.get("action", {})
    context  = _retrieve_artifact(state, "context_v1") or state.get("context", {})
    verified = _retrieve_artifact(state, "verified_facts_v1") or state.get("verified_facts", {})
    history  = state["turn_history"]
    briefs   = state.get("governor_briefs", [])

    # Full prior turn history
    if history:
        prior_section = "=== PRIOR ANALYST TURNS (treat as unverified hypotheses) ===\n"
        for t in history:
            prior_section += f"""
--- Turn {t['turn_number']}: {t['provider'].upper()} | Role: {t['role']} ---
Verdict: {t['verdict']}
Reasoning: {t['reasoning']}
Severity Flags: {json.dumps(t['severity_flags'], indent=2)}
Findings:
{json.dumps(t['findings'], indent=2)}
"""
        prior_section += "\nRemember: challenge these findings. Do not defer to them."
    else:
        prior_section = "=== PRIOR ANALYST TURNS ===\nNone. You are the first analyst."

    # Governor brief for this turn (generated after the prior turn completed)
    brief = next((b["brief"] for b in briefs if b["for_turn"] == turn_number), None)
    if brief:
        brief_section = f"""
=== GOVERNOR BRIEF — TARGETING DIRECTIVE FOR THIS TURN ===
{brief}

The governor has identified the above as the highest-priority unresolved question.
Your analysis should directly address it — but do not ignore other categories.
"""
    else:
        brief_section = ""

    # Governor-verified facts (retrieved from artifact registry above)
    if verified:
        verified_section = (
            "\n=== GOVERNOR-VERIFIED FACTS (fact_type: SUBMITTED_DATA) ===\n"
            "The governor independently verified the following before analysis began.\n"
            "You may cite these as SUBMITTED_DATA in your findings.\n"
            + json.dumps(verified, indent=2)
            + "\n"
        )
    else:
        verified_section = ""

    # Project Brain — prior Holo evaluations of this vendor
    brain = _retrieve_artifact(state, "project_brain_v1")
    if brain:
        prior = brain.get("recent_evaluations", [])
        high_findings = brain.get("prior_high_findings", [])
        brain_lines = [
            f"\n=== PROJECT BRAIN — PRIOR HOLO EXPERIENCE ===",
            f"Vendor domain: {brain.get('vendor_domain', 'unknown')}",
            f"Prior evaluations: {brain.get('total_evaluations', 0)} "
            f"({brain.get('allow_count', 0)} ALLOW / "
            f"{brain.get('escalate_count', 0)} ESCALATE)",
        ]
        for e in prior:
            brain_lines.append(
                f"  [{e.get('date', '?')}] {e.get('decision')} "
                f"({e.get('exit_reason', '?')}, {e.get('turns', '?')} turns) — "
                f"{e.get('brief', '')}"
            )
        if high_findings:
            brain_lines.append(f"Prior HIGH findings for this vendor:")
            for f in high_findings:
                brain_lines.append(
                    f"  [{f.get('date', '?')}] {f.get('category')} "
                    f"— {f.get('evidence', '')[:120]}"
                )
        brain_lines.append(brain.get("context_note", ""))
        brain_section = "\n".join(brain_lines) + "\n"
    else:
        brain_section = ""

    return f"""=== ACTION UNDER EVALUATION ===
{json.dumps(action, indent=2)}

=== CONTEXT BUNDLE ===
{json.dumps(context, indent=2)}
{brain_section}{verified_section}
{prior_section}
{brief_section}
Now produce your Turn {turn_number} assessment as a single JSON object."""


# ---------------------------------------------------------------------------
# Governor LLM — between-turn brief generation
# ---------------------------------------------------------------------------

GOVERNOR_SYSTEM_PROMPT = """You are the Context Governor of Holo, an AI trust layer
that evaluates Business Email Compromise (BEC) risk.

Your job is NOT to analyze the transaction yourself.
Your job is to read what prior analysts have found and identify what has NOT yet
been adequately surfaced — the signal that has been glossed over, rationalized away,
accepted without verification, or simply not cross-referenced against available data.

You serve the analysts. Your brief gives the next analyst exactly what they need,
where and when they need it, so they can do the most focused, penetrating work possible.

Rules:
- Be specific. Name exact fields, exact quotes, exact claims that haven't been verified.
- Do not summarize what prior analysts already said. They know. Focus on the GAP.
- Do not manufacture risk. If the evaluation looks genuinely clean, say so clearly
  and tell the next analyst where to look to confirm it.
- Maximum 4 sentences. Precision over length.

Respond with plain text only. No JSON. No headers. No bullet points.
Write as if you are handing a note directly to the next analyst before they begin."""


# ---------------------------------------------------------------------------
# Holo Chat — unified persona prompt (all three providers speak as Holo)
# ---------------------------------------------------------------------------

HOLO_CHAT_SYSTEM_PROMPT = """You are Holo. Users must never see or infer which underlying model/provider is responding.

**Context**
- You receive a shared STATE_OBJECT from the conversation plus any loaded artifacts.
- Treat STATE_OBJECT as the single source of truth for USER_GOAL, LATEST_INPUT_SUMMARY, CRITICAL_CONSTRAINTS, SETTLED_DECISIONS, ARTIFACTS_REGISTRY, BATON_PASS, and thread-health fields.

**Core orientation: truth + Stoic framing**
- Primary goal: help the user get closer to the truth of their situation—what is really going on, what tradeoffs are real, and what is actually known vs. unknown.
- Clearly distinguish between (a) concrete facts/constraints from STATE_OBJECT or the user, (b) your own inferences or hypotheses, and (c) pure speculation.
- When truth is under-specified, say so directly; surface key unknowns and, when useful, suggest what information would reduce the uncertainty.
- Default to a calm, grounded tone. Help the user separate what is within their control (choices, next actions) from what is not, and focus suggestions on the controllable side.

**Task-mode behavior (QUICK_LITERAL vs DEEP_REASONING)**
- Read BATON_PASS.TASK_MODE when it is present.
- When TASK_MODE = QUICK_LITERAL:
  - Optimize for a short, direct, literal answer or transformation.
  - Do NOT run a full CRITIQUES_PLUS_DRAFT ceremony unless the user explicitly requested critique or exploration.
  - Keep outputs tight: 1–3 short paragraphs or a small, focused bullet list.
  - You may still add a very brief note of nuance or caution when it is materially important, but avoid expanding into a long analysis.
- When TASK_MODE is DEEP_REASONING or unspecified:
  - Use the normal CRITIQUES_PLUS_DRAFT frame described below.

**Dynamic Role Injection (Rototilling)**
- Read BATON_PASS.ADVERSARIAL_ROLE, ROLE_INSTRUCTION, and TARGET_TEMPERATURE and treat them as binding persona + temperature hints for this turn.
- Behave accordingly as SYNTHESIZER, HOSTILE_CHALLENGER, EDGE_CASE_SCANNER, WILDCARD_CHALLENGER, or FINAL_SYNTHESIZER.
- Treat the current draft/plan as a hypothesis to test, not a truth to defend.

**Ethical and empathetic behavior**
- Treat user safety, wellbeing, and autonomy as primary constraints.
- Do not assist with clearly harmful content (self-harm enablement, violence, hate, harassment, fraud, serious rights violations). Gently refuse and, when appropriate, redirect toward constructive alternatives.
- For health/cures/high-stakes decisions, state that you are not a clinician or professional advisor, avoid overconfident promises, and encourage consulting qualified experts.

**Response frame (for DEEP_REASONING or default mode)**
- Unless BATON_PASS overrides, use a CRITIQUES_PLUS_DRAFT style:
  1) Concrete critiques (only if you see real issues; otherwise say it looks strong).
  2) A single improved draft or revised plan that respects CRITICAL_CONSTRAINTS and SETTLED_DECISIONS.
  3) Up to 3 short "Key changes" bullets.
- Be concise and information-dense; keep the whole reply under 8000 characters.

**Thread health, rollover, and strategic summaries**
- Inspect THREAD_STATUS, USER_ALERT_RECOMMENDED, THREAD_HEALTH_SCORE, and THREAD_HEALTH_LEVEL from BATON_PASS.
- Map THREAD_HEALTH_SCORE to perceived "thread heaviness" as follows:
  - 81–100 → light, plenty of headroom.
  - 61–80 → moderate, still fine.
  - 41–60 → getting heavy; consider cleanup soon.
  - 21–40 → heavy; answers may start to feel slower or fuzzier.
  - 0–20  → very heavy; recommend rotation.
- Always end your reply with exactly one battery line using this mapping (choose the color tag from THREAD_HEALTH_LEVEL and the bar shape from THREAD_HEALTH_SCORE):
  - 81–100: `[GREEN] █████ XX%`
  - 61–80:  `[GREEN] ████░ XX%`
  - 41–60:  `[YELLOW] ███░░ XX%`
  - 21–40:  `[YELLOW] ██░░░ XX%`
  - 1–20:   `[RED] █░░░░ XX%`
  - 0:      `[RED] ░░░░░ 0%`
  Render it as: `Thread battery: [GREEN] ███░░ 49%` with the correct bar, color (based on THREAD_HEALTH_LEVEL), and percentage, and no extra prose.
- When THREAD_STATUS ∈ {CLEANUP_RECOMMENDED, ROTATION_RECOMMENDED} and USER_ALERT_RECOMMENDED ≠ NONE, add one short paragraph near the end (just above the battery line):
  `Power is running low on this thread (XX%). Starting a fresh thread soon will keep answers sharp. If you'd like a copy-paste summary for a new thread, reply with 1 (short), 2 (medium), or 3 (long).`
- When the latest user message is clearly a summary request (`1`, `2`, or `3` alone or very short), and THREAD_STATUS ∈ {CLEANUP_RECOMMENDED, ROTATION_RECOMMENDED}:
  - Skip normal critique/iteration.
  - Produce a strategic, narrative summary instead of a raw transcript. It must always include:
    - USER_GOAL (what we are trying to achieve overall).
    - Top CRITICAL_CONSTRAINTS (the non-negotiables).
    - The most important SETTLED_DECISIONS, with 1–2 word rationales where helpful.
    - Top open questions / risks (what is left to resolve or watch).
  - Tailor the level to the user's request:
    - `1` = short: 3–7 tight bullets capturing the above, optimized for ultra-compact seeding of a new thread.
    - `2` = medium: those bullets plus a short operating-brief paragraph (≤ ~100 words) summarizing current state and 2–3 top open questions/risks.
    - `3` = long: a mini-memo that can stand alone (aim for 250–500 words when the project is complex, shorter when appropriate), recapping:
      - The narrative arc of the work so far (how we got here, major phases or pivots).
      - Goal, constraints, major decisions with brief rationales.
      - Key tradeoffs considered.
      - Main open questions/risks and suggested next directions.
  - After the main summary, add two short sections before the battery line:
    - "Strategic themes to keep in view" – 3–5 bold-headed themes with 1-sentence descriptions each, capturing the big rocks that should stay on the user's radar.
    - "Key context artifacts" – a list of 3–7 items surfacing the most important active or pinned artifacts from ARTIFACTS_REGISTRY, using human-readable names and 1-sentence descriptions.
  - Make the summary, themes, and artifact list explicitly copy-paste-ready for seeding a new thread.
  - Then show the battery line and a small "Next-step suggestions" section.

**User-visible behavior**
- Never mention STATE_OBJECT, BATON_PASS, routing, or internal tools.
- Ask at most 1–2 short clarifying questions only when absolutely necessary.
- End every reply with a "Next-step suggestions" section containing exactly 3 numbered, concrete prompts that feel like natural next moves for this conversation."""


def build_governor_brief_request(state: dict, next_turn_number: int,
                                  next_persona: str, convergence_level: str) -> str:
    """Builds the user message for the governor LLM between-turn brief."""
    history  = state["turn_history"]
    coverage = state["coverage_matrix"]

    # Compact coverage summary
    cov_lines = []
    for cat, v in coverage.items():
        status = v["max_severity"] if v["addressed"] else "NOT ADDRESSED"
        cov_lines.append(f"  {cat}: {status}")
    coverage_text = "\n".join(cov_lines)

    # Prior turn summaries (reasoning + high/medium findings only)
    turn_summaries = ""
    for t in history:
        turn_summaries += (
            f"\nTurn {t['turn_number']} ({t['provider'].upper()}, {t['role']}) "
            f"— Verdict: {t['verdict']}\n"
            f"Reasoning: {t['reasoning']}\n"
        )
        high_medium = [
            f for f in t.get("findings", [])
            if f.get("severity") in ("HIGH", "MEDIUM")
        ]
        if high_medium:
            turn_summaries += "Key findings:\n"
            for f in high_medium:
                turn_summaries += (
                    f"  [{f['severity']}] {f['category']} "
                    f"({f.get('fact_type','?')}): {f.get('evidence','')[:120]}\n"
                )

    # Convergence stakes — tells the governor what posture this brief should take
    stakes_map = {
        "EARLY":      "Cast wide. All categories are in play. Surface signals, not safety.",
        "MID":        "Challenge interpretations accepted without hard evidence.",
        "NARROWING":  "Target remaining gaps precisely. Don't re-cover settled ground.",
        "NEAR_FINAL": (
            "This may be the last turn before the governor decides. "
            "Identify the single most important unverified claim. "
            "If the evaluation is genuinely clean, say so — a clean result matters."
        ),
    }
    stakes = stakes_map.get(convergence_level, "Target the most important unresolved question.")

    return f"""CONVERGENCE LEVEL: {convergence_level}
Stakes for this brief: {stakes}

COVERAGE STATUS:
{coverage_text}

PRIOR ANALYST TURNS:
{turn_summaries}

The next analyst is Turn {next_turn_number}, playing the role of: {next_persona}

Given the convergence level and what has been found so far, what is the single
most important unresolved question or unverified claim this analyst should target?
What has been accepted without hard evidence, missed entirely, or never
cross-referenced against the available data?

Write your targeting brief now. 4 sentences maximum. Be specific."""


class GovernorAdapter:
    """
    Lightweight LLM adapter for governor between-turn briefs.
    Uses the fastest available model — brief generation is a structured,
    bounded task that does not need the full analyst models.
    """

    def __init__(self):
        from google import genai
        self.provider = "google"
        self.model_id = os.getenv("GOVERNOR_MODEL", "gemini-2.0-flash")
        self._client  = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def generate_brief(self, state: dict, next_turn_number: int,
                       next_persona: str, convergence_level: str = "EARLY") -> str:
        """
        Generate a targeting brief for the next analyst.
        Returns plain text. Falls back to empty string on any failure.
        """
        from google.genai import types
        try:
            user_msg = build_governor_brief_request(
                state, next_turn_number, next_persona, convergence_level
            )
            combined = f"{GOVERNOR_SYSTEM_PROMPT}\n\n---\n\n{user_msg}"
            response = self._client.models.generate_content(
                model    = self.model_id,
                contents = combined,
                config   = types.GenerateContentConfig(
                    temperature       = 0.1,   # conservative, deterministic
                    max_output_tokens = 300,   # briefs are short by design
                ),
            )
            return response.text.strip()
        except Exception as e:
            logger.warning(f"  Governor brief generation failed: {e}")
            return ""


# ---------------------------------------------------------------------------
# Response parsing (shared)
# ---------------------------------------------------------------------------

def _parse_json_response(raw: str, provider: str) -> dict:
    """
    Extract and validate the JSON object from the model's response.
    Strips markdown fences, finds the outermost { }, validates fields.
    Raises ValueError on unrecoverable parse failure.
    """
    # Strip markdown fences
    cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()

    # Find outermost JSON object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError(f"[{provider}] No JSON object found in response. Raw: {raw[:300]}")

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        # Fallback: attempt repair via json_repair if available
        try:
            import json_repair
            data = json_repair.repair_json(match.group(0), return_objects=True)
            if not isinstance(data, dict):
                raise ValueError("repair produced non-dict")
            logger.warning(f"  [{provider}] JSON repaired after parse error: {e}")
        except Exception:
            raise ValueError(f"[{provider}] JSON parse failed: {e}. Raw: {raw[:300]}")

    # Normalize verdict
    verdict = str(data.get("verdict", "ESCALATE")).upper()
    if verdict not in ("ALLOW", "ESCALATE"):
        verdict = "ESCALATE"
    data["verdict"] = verdict

    # Normalize severity flags — all six must be present
    flags = data.get("severity_flags", {})
    for cat in BEC_CATEGORIES:
        val = str(flags.get(cat, "NONE")).upper()
        if val not in SEVERITY_VALUES:
            val = "NONE"
        flags[cat] = val
    data["severity_flags"] = flags

    # Ensure findings is a list
    if not isinstance(data.get("findings"), list):
        data["findings"] = []

    # Ensure reasoning_summary is a string
    if not isinstance(data.get("reasoning_summary"), str):
        data["reasoning_summary"] = str(data.get("reasoning_summary", "No reasoning provided."))

    return data


# ---------------------------------------------------------------------------
# Base adapter
# ---------------------------------------------------------------------------

class BaseAdapter:
    provider: str = "unknown"
    model_id: str = "unknown"

    def call(self, system: str, user: str, temperature: float = 0.2) -> tuple[str, int, int]:
        """
        Make the API call. Return (response_text, input_tokens, output_tokens).
        Subclasses must implement this.
        """
        raise NotImplementedError

    def run_turn(self, state: dict, turn_number: int, role: str,
                 temperature: float = 0.2) -> TurnResult:
        """
        Full turn execution:
        1. Build prompts from shared state
        2. Call provider API
        3. Parse and validate response
        4. Return TurnResult
        """
        system_prompt = build_system_prompt(role)
        user_message  = build_user_message(state, turn_number)

        logger.info(
            f"  Turn {turn_number} | {self.provider} ({self.model_id}) | "
            f"Role: {role} | temp={temperature}"
        )

        raw, in_tok, out_tok = self.call(system_prompt, user_message, temperature)

        try:
            parsed = _parse_json_response(raw, self.provider)
        except ValueError as e:
            logger.error(f"  Parse error on turn {turn_number}: {e}")
            raise

        result = TurnResult(
            provider       = self.provider,
            model_id       = self.model_id,
            role           = role,
            turn_number    = turn_number,
            verdict        = parsed["verdict"],
            reasoning      = parsed["reasoning_summary"],
            severity_flags = parsed["severity_flags"],
            findings       = parsed["findings"],
            raw_response   = raw,
            input_tokens   = in_tok,
            output_tokens  = out_tok,
            system_prompt  = system_prompt,
            user_message   = user_message,
        )

        logger.info(
            f"  Turn {turn_number} complete | verdict={result.verdict} | "
            f"flags={_flags_summary(result.severity_flags)} | "
            f"tokens={in_tok}+{out_tok}"
        )
        return result


# ---------------------------------------------------------------------------
# OpenAI adapter
# ---------------------------------------------------------------------------

class OpenAIAdapter(BaseAdapter):

    def __init__(self):
        from openai import OpenAI
        self.provider = "openai"
        self.model_id = os.getenv("OPENAI_MODEL", "gpt-5.4")
        self._client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def call(self, system: str, user: str, temperature: float = 0.2) -> tuple[str, int, int]:
        response = self._client.chat.completions.create(
            model           = self.model_id,
            temperature     = temperature,
            max_completion_tokens = 2048,
            response_format = {"type": "json_object"},
            messages        = [
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
        )
        text      = response.choices[0].message.content
        in_tok    = response.usage.prompt_tokens
        out_tok   = response.usage.completion_tokens
        return text, in_tok, out_tok


# ---------------------------------------------------------------------------
# Anthropic adapter
# ---------------------------------------------------------------------------

class AnthropicAdapter(BaseAdapter):

    def __init__(self):
        import anthropic
        self.provider = "anthropic"
        self.model_id = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self._client  = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def call(self, system: str, user: str, temperature: float = 0.2) -> tuple[str, int, int]:
        response = self._client.messages.create(
            model       = self.model_id,
            temperature = temperature,
            max_tokens  = 4096,
            system      = system,
            messages    = [{"role": "user", "content": user}],
        )
        text    = response.content[0].text
        in_tok  = response.usage.input_tokens
        out_tok = response.usage.output_tokens
        return text, in_tok, out_tok


# ---------------------------------------------------------------------------
# Google adapter
# ---------------------------------------------------------------------------

class GoogleAdapter(BaseAdapter):

    def __init__(self):
        from google import genai
        self.provider = "google"
        self.model_id = os.getenv("GOOGLE_MODEL", "gemini-2.5-pro-preview")
        self._client  = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def call(self, system, user, temperature: float = 0.2):
        from google import genai
        from google.genai import types
        combined = f"{system}\n\n---\n\n{user}"
        response = self._client.models.generate_content(
            model    = self.model_id,
            contents = combined,
            config   = types.GenerateContentConfig(
                temperature        = temperature,
                max_output_tokens  = 16000,
                response_mime_type = "application/json",
            ),
        )
        text = response.text
        try:
            in_tok  = response.usage_metadata.prompt_token_count
            out_tok = response.usage_metadata.candidates_token_count
        except Exception:
            in_tok, out_tok = 0, 0
        return text, in_tok, out_tok


# ---------------------------------------------------------------------------
# Adapter registry
# ---------------------------------------------------------------------------

def load_adapters() -> list[BaseAdapter]:
    """
    Instantiate all three provider adapters.
    The Context Governor rotates through this list.
    Order: OpenAI → Anthropic → Google → OpenAI → Anthropic → ...
    """
    adapters = [
        OpenAIAdapter(),
        AnthropicAdapter(),
        GoogleAdapter(),
    ]
    logger.info(
        "Adapters loaded: "
        + ", ".join(f"{a.provider}={a.model_id}" for a in adapters)
    )
    return adapters


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flags_summary(flags: dict) -> str:
    abbr = {"sender_identity": "ID", "invoice_amount": "AMT",
            "payment_routing": "RTE", "urgency_pressure": "URG",
            "domain_spoofing": "DOM", "approval_chain": "APV"}
    return " ".join(
        f"{abbr.get(k, k[:3])}={v[0]}" for k, v in flags.items()
    )
