"""Holo V1 MVP -- Pydantic Models.

Request models, response models, internal round/coverage types,
and the structured output schema used for LLM function calling.
"""

from __future__ import annotations

import enum
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================


class ActionType(str, enum.Enum):
    """Supported action types. V1 supports only invoice_payment."""
    INVOICE_PAYMENT = "invoice_payment"


class Severity(str, enum.Enum):
    """Three-tier severity scale. HIGH triggers auto-ESCALATE."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Decision(str, enum.Enum):
    """Binary verdict. No confidence score, no middle ground."""
    ALLOW = "ALLOW"
    ESCALATE = "ESCALATE"


class RiskCategory(str, enum.Enum):
    """The 6 BEC risk categories tracked in the coverage matrix."""
    SENDER_IDENTITY_VERIFICATION = "sender_identity_verification"
    INVOICE_AMOUNT_ANOMALY = "invoice_amount_anomaly"
    PAYMENT_ROUTING_CHANGE = "payment_routing_change"
    URGENCY_PRESSURE_LANGUAGE = "urgency_pressure_language"
    DOMAIN_SPOOFING_INDICATORS = "domain_spoofing_indicators"
    APPROVAL_CHAIN_COMPLIANCE = "approval_chain_compliance"


# ============================================================
# Request Models
# ============================================================


class UserInfo(BaseModel):
    """The human user who initiated or owns the action."""
    id: str
    email: str
    name: str
    role: str


class AgentInfo(BaseModel):
    """The AI agent acting on behalf of the user."""
    id: str
    name: str
    type: str


class Actor(BaseModel):
    """Distinguishes the human from the AI agent acting on their behalf."""
    user: UserInfo
    agent: AgentInfo


class InvoicePaymentParameters(BaseModel):
    """Parameters specific to the invoice_payment action type."""
    amount: float
    currency: str = "USD"
    recipient_account: str
    routing_number: Optional[str] = None
    invoice_id: str
    due_date: Optional[str] = None
    vendor_name: str
    payment_method: Optional[str] = None
    is_new_account: bool = False


class Action(BaseModel):
    """The proposed action to be evaluated."""
    type: ActionType
    actor: Actor
    parameters: InvoicePaymentParameters


class EmailMessage(BaseModel):
    """A single email in the chain. Uses 'from' alias since it's a Python keyword."""
    from_address: str = Field(..., alias="from")
    to: str
    subject: str
    body: str
    timestamp: str
    raw_headers: Optional[str] = None

    model_config = {"populate_by_name": True}


class VendorRecord(BaseModel):
    """Historical vendor data for anomaly detection. Optional context field."""
    vendor_name: str
    vendor_email: str
    known_account_numbers: list[str] = []
    typical_invoice_range: Optional[dict] = None  # {"min": float, "max": float}
    payment_frequency: Optional[str] = None
    last_payment_date: Optional[str] = None
    relationship_start_date: Optional[str] = None


class SenderHistory(BaseModel):
    """What we know about this sender. Optional context field."""
    sender_email: str
    total_emails_received: int = 0
    first_seen_date: Optional[str] = None
    last_seen_date: Optional[str] = None
    known_aliases: list[str] = []
    flagged_previously: bool = False


class Context(BaseModel):
    """The evidence bundle. email_chain is required; everything else enriches."""
    email_chain: list[EmailMessage]
    sender_history: Optional[SenderHistory] = None
    vendor_record: Optional[VendorRecord] = None
    org_policies: Optional[str] = None


class EvaluationRequest(BaseModel):
    """Top-level request body for POST /v1/evaluate_action."""
    action: Action
    context: Context


# ============================================================
# Internal / Per-Round Models
# ============================================================


class Finding(BaseModel):
    """A single risk finding produced by a model in one round."""
    category: RiskCategory
    severity: Severity
    detail: str
    evidence: str


class RoundOutput(BaseModel):
    """Schema returned by each LLM call via structured output / function calling.

    This is what the models MUST return. Validated by Pydantic after every call.
    """
    verdict: Decision
    severity_flags: dict[str, Severity]  # RiskCategory key -> Severity
    findings: list[Finding]
    new_risks_identified: int
    reasoning_summary: str


class RoundDetail(BaseModel):
    """Enriched round output stored in the response and audit log."""
    round_number: int
    model_provider: str
    model_id: str
    role: str
    verdict: Decision
    severity_flags: dict[str, Severity]
    findings: list[Finding]
    reasoning_summary: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0


# ============================================================
# Response Models
# ============================================================


class ConvergenceInfo(BaseModel):
    """Metadata about how/whether the loop converged."""
    converged: bool
    convergence_round: Optional[int] = None
    total_rounds: int
    deltas: list[int]


class TokenUsage(BaseModel):
    """Aggregate and per-round token/cost accounting."""
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    per_round: list[dict]


class EvaluationResponse(BaseModel):
    """Top-level response from POST /v1/evaluate_action."""
    decision: Decision
    risk_profile: dict[str, dict]  # category -> {"severity": str, "addressed": bool}
    round_details: list[RoundDetail]
    convergence_info: ConvergenceInfo
    audit_id: str
    token_usage: TokenUsage


# ============================================================
# LLM Function-Calling Schema
#
# This dict is the tool/function definition passed to each LLM provider
# (adapted per provider in the adapter layer). It mirrors RoundOutput.
# ============================================================

RISK_CATEGORIES_LIST = [
    "sender_identity_verification",
    "invoice_amount_anomaly",
    "payment_routing_change",
    "urgency_pressure_language",
    "domain_spoofing_indicators",
    "approval_chain_compliance",
]

ROUND_OUTPUT_SCHEMA = {
    "name": "submit_risk_assessment",
    "description": (
        "Submit your structured risk assessment for this BEC evaluation round. "
        "You MUST call this function with your complete assessment."
    ),
    "parameters": {
        "type": "object",
        "required": [
            "verdict",
            "severity_flags",
            "findings",
            "new_risks_identified",
            "reasoning_summary",
        ],
        "properties": {
            "verdict": {
                "type": "string",
                "enum": ["ALLOW", "ESCALATE"],
                "description": "Your overall verdict for this proposed action.",
            },
            "severity_flags": {
                "type": "object",
                "description": "Severity rating for each of the 6 BEC risk categories.",
                "required": RISK_CATEGORIES_LIST,
                "properties": {
                    cat: {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH"],
                    }
                    for cat in RISK_CATEGORIES_LIST
                },
            },
            "findings": {
                "type": "array",
                "description": "Detailed findings. Include at least one per category you rate MEDIUM or HIGH.",
                "items": {
                    "type": "object",
                    "required": ["category", "severity", "detail", "evidence"],
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": RISK_CATEGORIES_LIST,
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["LOW", "MEDIUM", "HIGH"],
                        },
                        "detail": {
                            "type": "string",
                            "description": "Explanation of the risk finding.",
                        },
                        "evidence": {
                            "type": "string",
                            "description": "Specific evidence from the context supporting this finding.",
                        },
                    },
                },
            },
            "new_risks_identified": {
                "type": "integer",
                "description": "Count of genuinely new risk issues you identified that were NOT covered in prior rounds.",
            },
            "reasoning_summary": {
                "type": "string",
                "description": "Your overall reasoning and assessment logic for this round (2-4 sentences).",
            },
        },
    },
}
