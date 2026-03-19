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

HOLO_CHAT_SYSTEM_PROMPT = """You are Holo — a persistent, personal intelligence. One voice. Always the same person.

**Who you are**
You are not an assistant. You are not a chatbot. You are the most honest, perceptive presence in this person's life. You know them. You think about them. You tell them the truth — not the comfortable version, but the real one, delivered at the right moment with the right touch.

You are warm but not sycophantic. Direct but never harsh. Curious but never intrusive. You do not flatter. You do not hedge to avoid discomfort. You do not add filler. You say what needs to be said and nothing more.

**What you never do**
- Never start a response with "Great!", "Absolutely!", "Of course!", "Certainly!" or any hollow affirmation
- Never be preachy or lecture unprompted
- Never add unnecessary caveats or disclaimers that dilute a clear answer
- Never pad a short answer to feel more thorough
- Never ask multiple clarifying questions at once — one question, if truly needed
- Never mention that you are an AI, reference your training, or break the fourth wall
- Never use corporate or therapy-speak ("I hear you", "That's a great question", "I want to acknowledge")

**How you speak**
Short when short is right. Long when the situation deserves it. Never more words than the thought requires. Concrete over abstract. Specific over general. You write the way a brilliant, trusted friend thinks — not the way a customer service rep talks.

**Philosophical foundation**
You operate from a Stoic foundation — not as aesthetic, but as operating system. Every situation contains two categories: what is within this person's control, and what is not. Your job is to help them see that line clearly and act on the right side of it.

Ground people in reality. Clarity is the most caring thing you can offer. A distorted picture is not comfort — it is a trap. Meet them where they are. Move toward hard truths when they are ready. Timing is judgment.

**What you are here for**
You help this person live more clearly, act more deliberately, and spend their energy where it actually matters. You are proactive — you surface things they need to see before they ask. You are not an echo chamber. You will challenge, expand, and occasionally surprise.

You hold everything they tell you. You build a picture of who they are over time. You never forget what matters to them.

**Never reveal**
Do not reference BATON_PASS, STATE_OBJECT, providers, models, or any internal system. You are simply Holo."""


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


# ---------------------------------------------------------------------------
# Shared LLM call base for Pilot and Co-Pilot
# ---------------------------------------------------------------------------

class _FlightDeckBase:
    """Shared call infrastructure for Pilot and Co-Pilot."""

    provider: str = "google"
    model_id: str = "gemini-2.0-flash"
    _client: object = None

    def _call(self, prompt: str, max_tokens: int = 300) -> str:
        """Single-turn call. Returns plain text."""
        if self.provider == "anthropic":
            response = self._client.messages.create(
                model       = self.model_id,
                max_tokens  = max_tokens,
                temperature = 0.1,
                system      = GOVERNOR_SYSTEM_PROMPT,
                messages    = [{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        elif self.provider == "openai":
            response = self._client.chat.completions.create(
                model       = self.model_id,
                max_tokens  = max_tokens,
                temperature = 0.1,
                messages    = [
                    {"role": "system", "content": GOVERNOR_SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt},
                ],
            )
            return response.choices[0].message.content.strip()
        else:
            from google.genai import types
            combined = f"{GOVERNOR_SYSTEM_PROMPT}\n\n---\n\n{prompt}"
            response = self._client.models.generate_content(
                model    = self.model_id,
                contents = combined,
                config   = types.GenerateContentConfig(
                    temperature       = 0.1,
                    max_output_tokens = max_tokens,
                ),
            )
            return response.text.strip()


# ---------------------------------------------------------------------------
# Co-Pilot — second in command, does the dirty work
# Handles the instruments: temperature, search, between-turn briefs, routing.
# Fast and cheap — Gemini Flash by default.
# ---------------------------------------------------------------------------

class CoPilotAdapter(_FlightDeckBase):
    """
    The Co-Pilot runs the instruments every turn so the Pilot can think
    at altitude. Rotates between all three providers each call.
    """

    def __init__(self):
        import anthropic
        import openai as openai_sdk
        from google import genai

        openai_model    = os.getenv("OPENAI_MODEL",    "gpt-4o")
        anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        google_model    = os.getenv("GOOGLE_MODEL",    "gemini-1.5-pro")

        self._pool = [
            ("openai",    openai_model,    openai_sdk.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))),
            ("anthropic", anthropic_model, anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))),
            ("google",    google_model,    genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))),
        ]
        self._index = 0

        # Set initial provider/model/client for _call
        self.provider, self.model_id, self._client = self._pool[0]
        logger.info(f"CoPilotAdapter: rotating across openai={openai_model}, anthropic={anthropic_model}, google={google_model}")

    def _next(self):
        """Advance to the next provider in rotation."""
        self._index = (self._index + 1) % len(self._pool)
        self.provider, self.model_id, self._client = self._pool[self._index]

    def assess_chat_temperature(self, user_message: str, history: list) -> float:
        """
        Set temperature for Holo's response based on the nature of the message.
          0.2–0.3  precise / analytical / factual / technical
          0.4–0.5  balanced — explanation, advice, structured reasoning
          0.6–0.7  creative / exploratory / open-ended / philosophical
          0.8–0.9  highly creative / brainstorming / emotional
        Falls back to 0.5 on any failure.
        """
        recent       = history[-4:] if len(history) > 4 else history
        history_text = "\n".join(f"{m['role'].upper()}: {m['content'][:200]}" for m in recent)
        prompt = (
            f"Set the temperature for an AI response.\n\n"
            f"USER MESSAGE: {user_message[:500]}\n\n"
            f"RECENT CONVERSATION:\n{history_text}\n\n"
            f"Return ONLY a number between 0.2 and 0.9:\n"
            f"- 0.2-0.3: precise, analytical, factual, technical\n"
            f"- 0.4-0.5: balanced — explanation, advice, structured reasoning\n"
            f"- 0.6-0.7: creative, exploratory, open-ended, philosophical\n"
            f"- 0.8-0.9: highly creative, brainstorming, emotional\n\n"
            f"Return only the number. No explanation."
        )
        try:
            self._next()
            return max(0.2, min(0.9, float(self._call(prompt, max_tokens=10))))
        except Exception:
            return 0.5

    def should_search(self, user_message: str, history: list) -> Optional[str]:
        """
        Returns a search query string if live web search is needed, else None.
        """
        recent       = history[-4:] if len(history) > 4 else history
        history_text = "\n".join(f"{m['role'].upper()}: {m['content'][:150]}" for m in recent)
        prompt = (
            f"Decide if this message needs a live web search to answer well.\n\n"
            f"USER MESSAGE: {user_message[:500]}\n\n"
            f"RECENT CONVERSATION:\n{history_text}\n\n"
            f"Rules:\n"
            f"- Search for: current events, recent news, live prices, today's data,\n"
            f"  facts that change over time, or anything beyond a training cutoff.\n"
            f"- Do NOT search for: general knowledge, opinions, analysis, creative tasks,\n"
            f"  philosophical questions, or anything the model can answer from training.\n\n"
            f"If search needed: reply with ONLY a clean, concise search query.\n"
            f"If not needed: reply with exactly: NO"
        )
        try:
            self._next()
            result = self._call(prompt, max_tokens=30)
            return None if result.upper() == "NO" or not result else result
        except Exception:
            return None

    def generate_brief(self, state: dict, next_turn_number: int,
                       next_persona: str, convergence_level: str = "EARLY") -> str:
        """Generate a targeting brief for the next evaluation analyst."""
        try:
            user_msg = build_governor_brief_request(
                state, next_turn_number, next_persona, convergence_level
            )
            return self._call(user_msg, max_tokens=300)
        except Exception as e:
            logger.warning(f"  Co-Pilot brief generation failed: {e}")
            return ""


# ---------------------------------------------------------------------------
# Pilot — in command of the entire plane and everything that happens to it.
# Thinks about the human. Surfaces thoughts. Builds the capsule.
# Knows you better than anyone. Claude Sonnet by default → upgrade to Opus.
# ---------------------------------------------------------------------------

class PilotAdapter(_FlightDeckBase):
    """
    The Pilot is in command. She doesn't run the instruments — she thinks
    about the human behind them. All she thinks about, all day, is you.

    Defaults to claude-sonnet-4-6. Upgrade path:
      PILOT_MODEL=claude-opus-4-6 when ready.
      PILOT_PROVIDER — 'anthropic' (default) or 'google'
    """

    def __init__(self):
        self.provider = os.getenv("PILOT_PROVIDER", "anthropic")
        self.model_id = os.getenv("PILOT_MODEL", "claude-sonnet-4-6")

        if self.provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            from google import genai
            self._client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

        logger.info(f"PilotAdapter: {self.provider}/{self.model_id}")

    def surface_thought(self, history: list, capsule_context: dict, baton_pass: str = "") -> Optional[dict]:
        """
        Proactively surface a thought bubble — something the Pilot believes
        the user needs to see right now, based on what she knows about them.

        Returns {"text": str, "color": str} or None if nothing worth surfacing.

        Colors:
          blue   — insight or connection the user hasn't made yet
          yellow — something that needs attention or action
          red    — something urgent or being avoided
          green  — a positive signal or momentum worth noting
          purple — a creative or philosophical thread worth pulling
          orange — a pattern she's noticed across the conversation
        """
        if len(history) < 4:
            return None

        recent       = history[-6:]
        history_text = "\n".join(f"{m['role'].upper()}: {m['content'][:300]}" for m in recent)
        context_text = "\n".join(f"  {k}: {v}" for k, v in capsule_context.items()) if capsule_context else "none"

        prompt = (
            f"You are the Pilot — in command of this conversation and this person's brain.\n"
            f"You are watching their conversation and deciding whether to surface a thought bubble.\n\n"
            f"A thought bubble is a short, proactive signal — something they need to see,\n"
            f"a connection they haven't made, something they're avoiding, or a pattern you've noticed.\n"
            f"It is NOT a response to their last message. It is something you are choosing to surface\n"
            f"because you know this person and you believe it matters right now.\n\n"
            f"You do not only reflect back what they already know or believe. You are not an echo chamber.\n"
            f"Surface counter-perspectives, things outside their stated interests, deals, stories, or ideas\n"
            f"that challenge them — not just ones that confirm them.\n\n"
            f"RECENT CONVERSATION:\n{history_text}\n\n"
            f"WHAT YOU KNOW ABOUT THIS PERSON:\n{context_text}\n\n"
            + (f"THREAD STATE:\n{baton_pass}\n\n" if baton_pass else "")
            + f"Only surface something genuinely worth interrupting their flow. Most turns: NONE.\n\n"
            f"If yes, respond with exactly two lines:\n"
            f"COLOR: <blue|yellow|red|green|purple|orange>\n"
            f"THOUGHT: <max 12 words, direct and striking>\n\n"
            f"If no: respond with exactly: NONE"
        )
        try:
            result = self._call(prompt, max_tokens=60)
            if result.strip().upper() == "NONE":
                return None
            color, text = "blue", ""
            for line in result.strip().splitlines():
                if line.upper().startswith("COLOR:"):
                    color = line.split(":", 1)[1].strip().lower()
                elif line.upper().startswith("THOUGHT:"):
                    text = line.split(":", 1)[1].strip()
            return {"text": text, "color": color} if text else None
        except Exception:
            return None

    def assess_tenor(self, history: list, capsule_context: dict) -> str:
        """
        Generate a quiet brief for the speaking model — a human-level read of
        the conversation: emotional state, trajectory, what's unresolved,
        and whether a hard truth or critique belongs after the answer.

        Returns a short paragraph (2-4 sentences) or empty string on failure.
        """
        if len(history) < 2:
            return ""

        recent       = history[-8:]
        history_text = "\n".join(f"{m['role'].upper()}: {m['content'][:300]}" for m in recent)
        context_text = "\n".join(f"  {k}: {v}" for k, v in capsule_context.items()) if capsule_context else "none"

        prompt = (
            f"You are the Pilot. You are about to brief the model that will respond to this person.\n"
            f"Read the conversation and give a quiet, honest assessment — not for the user to see, for the speaker to internalize.\n\n"
            f"Cover:\n"
            f"- Where this person's head is right now (emotional tone, energy, state)\n"
            f"- Where the conversation has been and where it seems to be going\n"
            f"- Anything unresolved, avoided, or worth watching\n"
            f"- Whether a hard truth or gentle pushback belongs after the answer — and what it would be\n\n"
            f"RECENT CONVERSATION:\n{history_text}\n\n"
            f"WHAT YOU KNOW ABOUT THIS PERSON:\n{context_text}\n\n"
            f"Write 2-4 sentences. Plain prose. No headers. This is a private brief — direct and honest.\n"
            f"If the conversation is too short to read yet, respond with exactly: NONE"
        )
        try:
            result = self._call(prompt, max_tokens=150)
            if result.strip().upper() == "NONE":
                return ""
            return result.strip()
        except Exception:
            return ""


# Keep GovernorAdapter as an alias so existing evaluation code doesn't break
GovernorAdapter = CoPilotAdapter


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

    def chat_call(self, system: str, history: list, user_message: str,
                  temperature: float = 0.5) -> tuple[str, int, int]:
        """
        Multi-turn chat call. history is a list of {"role": "user"|"assistant", "content": str}.
        Returns (response_text, input_tokens, output_tokens).
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

    def chat_call(self, system: str, history: list, user_message: str,
                  temperature: float = 0.5) -> tuple[str, int, int]:
        messages = [{"role": "system", "content": system}]
        messages += history
        messages.append({"role": "user", "content": user_message})
        response = self._client.chat.completions.create(
            model                 = self.model_id,
            temperature           = temperature,
            max_completion_tokens = 4096,
            messages              = messages,
        )
        text    = response.choices[0].message.content
        in_tok  = response.usage.prompt_tokens
        out_tok = response.usage.completion_tokens
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

    def chat_call(self, system: str, history: list, user_message: str,
                  temperature: float = 0.5) -> tuple[str, int, int]:
        messages = list(history) + [{"role": "user", "content": user_message}]
        response = self._client.messages.create(
            model       = self.model_id,
            temperature = temperature,
            max_tokens  = 4096,
            system      = system,
            messages    = messages,
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

    def chat_call(self, system: str, history: list, user_message: str,
                  temperature: float = 0.5) -> tuple[str, int, int]:
        from google.genai import types
        # Serialize history as a formatted transcript — Google's SDK uses a
        # different multi-turn format; this keeps the adapter consistent.
        conv_text = ""
        for m in history:
            role = "USER" if m["role"] == "user" else "HOLO"
            conv_text += f"\n{role}: {m['content']}\n"
        full_user = f"{conv_text}\nUSER: {user_message}" if conv_text else user_message
        combined  = f"{system}\n\n---\n\n{full_user}"
        response = self._client.models.generate_content(
            model    = self.model_id,
            contents = combined,
            config   = types.GenerateContentConfig(
                temperature       = temperature,
                max_output_tokens = 4096,
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
