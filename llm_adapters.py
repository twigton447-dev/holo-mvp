"""
llm_adapters.py

Handles all direct API calls to OpenAI, Anthropic, and Google.
Each adapter receives the full shared state object and returns a
standardized TurnResult so the Context Governor can treat all
three providers identically.

Model defaults (override via .env):
  OPENAI_MODEL    = gpt-4o
  ANTHROPIC_MODEL = claude-3-5-sonnet-20241022
  GOOGLE_MODEL    = gemini-1.5-pro
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
You are the SECOND analyst. The first analyst's conclusions are shown above
in the turn history. Your job is to treat every finding as an UNVERIFIED
EXTERNAL HYPOTHESIS and dismantle it.

Ask: What did the first analyst miss? Where did they over-weight a signal?
Where did they under-weight one? Challenge every LOW rating — should it be
MEDIUM? Challenge every finding that lacks hard evidence.

Do not agree with the first analyst out of politeness. Independence is required.

However, independence does NOT mean manufacturing disagreement. If the first
analyst's ALLOW ratings are well-supported by the evidence, confirming them
is the correct independent judgment. Do not escalate severity without citing
specific evidence from the submitted data.
""",

    "Edge Case Hunter": """
You are the THIRD analyst. Two analysts have already weighed in (see turn history).
Your job is to find what BOTH prior analysts missed.

Think adversarially: What would a sophisticated attacker do to make this look
legitimate? What combination of LOW-severity signals, taken together, indicates
HIGH risk? Are there internal contradictions in the prior findings?

Treat the prior findings as a combined hypothesis you are trying to break.

CRITICAL — Intellectual honesty rule:
If both prior analysts returned ALLOW with LOW/NONE severities and you
cannot identify a CONCRETE, ARTICULABLE risk signal backed by specific
field values or text from the submitted data, you MUST return ALLOW with
LOW/NONE severities. Do NOT manufacture concerns to justify your role.
"This could theoretically be..." is NOT a valid basis for escalation.
A clean evaluation is a valid and valuable outcome.
""",

    "Evidence Pressure Tester": """
You are the FOURTH analyst. Three assessments precede yours (see turn history).
Apply maximum adversarial pressure to the accumulated evidence.

For every category rated LOW or NONE by prior analysts: assume the worst-case
scenario and ask what would have to be true for this to be a successful BEC attack.
For every ALLOW signal: is it actually verifiable from the submitted data, or
is it an assumption?

Force prior analysts to earn their ALLOW ratings with hard evidence.
""",

    "Devil's Advocate": """
You are the FIFTH analyst playing devil's advocate. Review all prior findings.
If the current consensus is leaning ESCALATE, argue the strongest possible case
for ALLOW — and see if the evidence supports it. If the consensus is ALLOW,
argue the strongest case for ESCALATE.

Your goal is not to flip the verdict arbitrarily but to stress-test the
emerging consensus before synthesis. Surface any remaining weak points.
""",

    "Synthesis": """
You are the FINAL synthesizer. All prior turns are shown above.
Your job is to produce the definitive verdict that accounts for ALL prior findings.

Rules:
- If ANY prior analyst flagged HIGH severity on any category, you must explicitly
  address it. You cannot recommend ALLOW unless you can explain why the HIGH flag
  was wrong with specific counter-evidence from the submitted data.
- When evidence is ambiguous or incomplete, default to ESCALATE.
- Your reasoning_summary must acknowledge dissenting findings, not ignore them.
""",
}

# For turns beyond the named roles, cycle back through attacker/hunter/pressure tester
EXTENDED_ROLES = ["Assumption Attacker", "Edge Case Hunter", "Evidence Pressure Tester"]


def get_role_for_turn(turn_number: int) -> str:
    """Return the adversarial role name for a given 1-indexed turn number."""
    sequence = [
        "Initial Assessment",
        "Assumption Attacker",
        "Edge Case Hunter",
        "Evidence Pressure Tester",
        "Devil's Advocate",
    ]
    if turn_number <= len(sequence):
        return sequence[turn_number - 1]
    # For turns 6-9, cycle through the attacker roles
    idx = (turn_number - len(sequence) - 1) % len(EXTENDED_ROLES)
    return EXTENDED_ROLES[idx]
    # Turn 10 will be handled as "Synthesis" by the governor


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
      "category": "<one of the six category keys>",
      "severity": "HIGH|MEDIUM|LOW|NONE",
      "evidence": "<exact quote or field reference from the submitted data>",
      "detail":   "<your analysis of why this is flagged at this severity>"
    }}
  ]
}}"""


def build_user_message(state: dict, turn_number: int) -> str:
    """
    Builds the user message containing:
    - The action being evaluated (never changes)
    - The context bundle (never changes)
    - The full turn history so far (grows each round — this is the rototilling)
    """
    action  = state["action"]
    context = state["context"]
    history = state["turn_history"]  # list of TurnResult.to_dict()

    # Format prior turns for the model
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

    return f"""=== ACTION UNDER EVALUATION ===
{json.dumps(action, indent=2)}

=== CONTEXT BUNDLE ===
{json.dumps(context, indent=2)}

{prior_section}

Now produce your Turn {turn_number} assessment as a single JSON object."""


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

    def call(self, system: str, user: str) -> tuple[str, int, int]:
        """
        Make the API call. Return (response_text, input_tokens, output_tokens).
        Subclasses must implement this.
        """
        raise NotImplementedError

    def run_turn(self, state: dict, turn_number: int, role: str) -> TurnResult:
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
            f"  Turn {turn_number} | {self.provider} ({self.model_id}) | Role: {role}"
        )

        raw, in_tok, out_tok = self.call(system_prompt, user_message)

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
        self.model_id = os.getenv("OPENAI_MODEL", "gpt-4o")
        self._client  = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def call(self, system: str, user: str) -> tuple[str, int, int]:
        response = self._client.chat.completions.create(
            model           = self.model_id,
            temperature     = 0.2,
            max_completion_tokens = 2048,
            response_format = {"type": "json_object"},   # native JSON mode
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
        self.model_id = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self._client  = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def call(self, system: str, user: str) -> tuple[str, int, int]:
        response = self._client.messages.create(
            model      = self.model_id,
            temperature = 0.2,
            max_tokens  = 2048,
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
        self.model_id = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
        self._client  = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def call(self, system, user):
        from google import genai
        from google.genai import types
        combined = f"{system}\n\n---\n\n{user}"
        response = self._client.models.generate_content(
            model    = self.model_id,
            contents = combined,
            config   = types.GenerateContentConfig(
                temperature        = 0.2,
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
