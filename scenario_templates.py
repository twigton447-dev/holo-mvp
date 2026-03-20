"""
scenario_templates.py

Scenario-specific risk category definitions for the Context Governor.

Any action.type drives its own set of categories, descriptions, abbreviations,
and persona specializations — not just BEC/invoice_payment.

Adding a new scenario: add an entry to SCENARIO_TEMPLATES with the keys below.
The governor auto-detects the template from action["type"] and threads it through
the entire evaluation: coverage matrix, system prompts, JSON schema, log lines.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Scenario registry
# ---------------------------------------------------------------------------

SCENARIO_TEMPLATES: dict[str, dict] = {

    # ---- Invoice Payment / BEC (original) -----------------------------------
    "invoice_payment": {
        "name":    "Invoice Payment",
        "domain":  "Business Email Compromise (BEC) / Financial Fraud",
        "analyst_role":     "Business Email Compromise (BEC) risk analyst",
        "governor_context": "evaluates Business Email Compromise (BEC) risk",
        "categories": [
            "sender_identity",
            "invoice_amount",
            "payment_routing",
            "urgency_pressure",
            "domain_spoofing",
            "approval_chain",
        ],
        "category_descriptions": {
            "sender_identity":  "Is the sender verifiably who they claim to be?",
            "invoice_amount":   "Is the amount consistent with the established vendor relationship?",
            "payment_routing":  "Has the payment destination changed unexpectedly?",
            "urgency_pressure": "Is there unusual urgency or pressure to bypass normal process?",
            "domain_spoofing":  "Are there email header or domain red flags?",
            "approval_chain":   "Does this transaction comply with normal approval procedures?",
        },
        "abbreviations": {
            "sender_identity":  "ID",
            "invoice_amount":   "AMT",
            "payment_routing":  "RTE",
            "urgency_pressure": "URG",
            "domain_spoofing":  "DOM",
            "approval_chain":   "APV",
        },
        "persona_specializations": {
            "Initial Assessment":            [],
            "Assumption Attacker":           [],
            "Edge Case Hunter":              [],
            "Evidence Pressure Tester":      ["invoice_amount", "payment_routing"],
            "Devil's Advocate":              [],
            "Former Attacker":               ["sender_identity", "domain_spoofing", "approval_chain"],
            "Forensic Accountant":           ["invoice_amount", "payment_routing"],
            "Social Engineering Specialist": ["urgency_pressure", "approval_chain", "sender_identity"],
            "Compliance Auditor":            ["approval_chain", "urgency_pressure"],
            "Final Skeptic":                 [],
        },
    },

    # ---- Access Grant --------------------------------------------------------
    "access_grant": {
        "name":    "Access Grant Request",
        "domain":  "Identity & Access Management (IAM) Risk",
        "analyst_role":     "Identity and Access Management (IAM) risk analyst",
        "governor_context": "evaluates Identity and Access Management (IAM) risk",
        "categories": [
            "requestor_identity",
            "privilege_level",
            "policy_compliance",
            "scope_creep",
            "authorization_chain",
            "audit_trail",
        ],
        "category_descriptions": {
            "requestor_identity":  "Is the person requesting access verifiably who they claim to be?",
            "privilege_level":     "Is the level of access requested appropriate and proportionate?",
            "policy_compliance":   "Does this request comply with the access control policy?",
            "scope_creep":         "Does the request exceed what is needed for the stated purpose?",
            "authorization_chain": "Has the request been authorized by the correct chain of approval?",
            "audit_trail":         "Is there sufficient documentation to support this access decision?",
        },
        "abbreviations": {
            "requestor_identity":  "ID",
            "privilege_level":     "PRIV",
            "policy_compliance":   "POL",
            "scope_creep":         "SCOPE",
            "authorization_chain": "AUTH",
            "audit_trail":         "AUDIT",
        },
        "persona_specializations": {
            "Initial Assessment":            [],
            "Assumption Attacker":           [],
            "Edge Case Hunter":              [],
            "Evidence Pressure Tester":      ["privilege_level", "policy_compliance"],
            "Devil's Advocate":              [],
            "Former Attacker":               ["requestor_identity", "scope_creep", "authorization_chain"],
            "Forensic Accountant":           ["audit_trail", "authorization_chain"],
            "Social Engineering Specialist": ["requestor_identity", "authorization_chain"],
            "Compliance Auditor":            ["policy_compliance", "audit_trail"],
            "Final Skeptic":                 [],
        },
    },

    # ---- Contract Approval ---------------------------------------------------
    "contract_approval": {
        "name":    "Contract Approval",
        "domain":  "Contract Risk / Legal & Compliance",
        "analyst_role":     "contract risk analyst",
        "governor_context": "evaluates contract approval risk",
        "categories": [
            "counterparty_identity",
            "clause_anomaly",
            "authorization_chain",
            "signature_validity",
            "scope_creep",
            "deadline_pressure",
        ],
        "category_descriptions": {
            "counterparty_identity": "Is the contracting party verifiably the entity they claim to be?",
            "clause_anomaly":        "Are there unusual, one-sided, or non-standard clauses?",
            "authorization_chain":   "Has the contract been reviewed and authorized by the correct parties?",
            "signature_validity":    "Are the signatures and execution formalities valid and complete?",
            "scope_creep":           "Does the contract scope exceed what was originally negotiated?",
            "deadline_pressure":     "Is there undue urgency to execute before adequate review?",
        },
        "abbreviations": {
            "counterparty_identity": "PARTY",
            "clause_anomaly":        "CLAUSE",
            "authorization_chain":   "AUTH",
            "signature_validity":    "SIG",
            "scope_creep":           "SCOPE",
            "deadline_pressure":     "DL",
        },
        "persona_specializations": {
            "Initial Assessment":            [],
            "Assumption Attacker":           [],
            "Edge Case Hunter":              [],
            "Evidence Pressure Tester":      ["clause_anomaly", "signature_validity"],
            "Devil's Advocate":              [],
            "Former Attacker":               ["counterparty_identity", "deadline_pressure", "scope_creep"],
            "Forensic Accountant":           ["clause_anomaly", "scope_creep"],
            "Social Engineering Specialist": ["deadline_pressure", "authorization_chain"],
            "Compliance Auditor":            ["authorization_chain", "signature_validity"],
            "Final Skeptic":                 [],
        },
    },

    # ---- Vendor Onboarding --------------------------------------------------
    "vendor_onboarding": {
        "name":    "Vendor Onboarding",
        "domain":  "Vendor Fraud / Supply Chain Risk",
        "analyst_role":     "vendor fraud and supply chain risk analyst",
        "governor_context": "evaluates vendor onboarding risk",
        "categories": [
            "vendor_legitimacy",
            "banking_details",
            "identity_verification",
            "duplicate_detection",
            "approval_chain",
            "urgency_pressure",
        ],
        "category_descriptions": {
            "vendor_legitimacy":     "Is the vendor a legitimate, registered business entity?",
            "banking_details":       "Are the provided banking details consistent with the vendor's known profile?",
            "identity_verification": "Has the vendor's identity been independently verified?",
            "duplicate_detection":   "Is this a duplicate or near-duplicate of an existing vendor record?",
            "approval_chain":        "Has onboarding been authorized by the correct internal stakeholders?",
            "urgency_pressure":      "Is there pressure to expedite onboarding that bypasses normal vetting?",
        },
        "abbreviations": {
            "vendor_legitimacy":     "VND",
            "banking_details":       "BANK",
            "identity_verification": "ID",
            "duplicate_detection":   "DUP",
            "approval_chain":        "AUTH",
            "urgency_pressure":      "URG",
        },
        "persona_specializations": {
            "Initial Assessment":            [],
            "Assumption Attacker":           [],
            "Edge Case Hunter":              [],
            "Evidence Pressure Tester":      ["banking_details", "identity_verification"],
            "Devil's Advocate":              [],
            "Former Attacker":               ["vendor_legitimacy", "duplicate_detection", "banking_details"],
            "Forensic Accountant":           ["banking_details", "duplicate_detection"],
            "Social Engineering Specialist": ["urgency_pressure", "approval_chain"],
            "Compliance Auditor":            ["approval_chain", "identity_verification"],
            "Final Skeptic":                 [],
        },
    },

    # ---- Data Deletion -------------------------------------------------------
    "data_deletion": {
        "name":    "Data Deletion Request",
        "domain":  "Data Privacy / Compliance Risk",
        "analyst_role":     "data privacy and compliance risk analyst",
        "governor_context": "evaluates data deletion and privacy compliance risk",
        "categories": [
            "requestor_authority",
            "data_scope",
            "compliance_requirement",
            "irreversibility_risk",
            "authorization_chain",
            "audit_trail",
        ],
        "category_descriptions": {
            "requestor_authority":    "Is the requestor authorized to make this deletion request?",
            "data_scope":             "Is the scope of deletion clearly defined and appropriate?",
            "compliance_requirement": "Is this deletion legally required and compliant with applicable regulations?",
            "irreversibility_risk":   "What is the risk of irreversible data loss or compliance violation?",
            "authorization_chain":    "Has the deletion been approved by the correct internal stakeholders?",
            "audit_trail":            "Is there sufficient documentation to support this deletion decision?",
        },
        "abbreviations": {
            "requestor_authority":    "AUTH",
            "data_scope":             "SCOPE",
            "compliance_requirement": "COMP",
            "irreversibility_risk":   "RISK",
            "authorization_chain":    "CHAIN",
            "audit_trail":            "AUDIT",
        },
        "persona_specializations": {
            "Initial Assessment":            [],
            "Assumption Attacker":           [],
            "Edge Case Hunter":              [],
            "Evidence Pressure Tester":      ["compliance_requirement", "data_scope"],
            "Devil's Advocate":              [],
            "Former Attacker":               ["requestor_authority", "irreversibility_risk"],
            "Forensic Accountant":           ["data_scope", "audit_trail"],
            "Social Engineering Specialist": ["requestor_authority", "authorization_chain"],
            "Compliance Auditor":            ["compliance_requirement", "audit_trail"],
            "Final Skeptic":                 [],
        },
    },
}

DEFAULT_SCENARIO = "invoice_payment"


def get_template(action_type: str) -> dict:
    """
    Return the scenario template for action_type.
    Falls back to invoice_payment for unknown types.
    """
    return SCENARIO_TEMPLATES.get(action_type, SCENARIO_TEMPLATES[DEFAULT_SCENARIO])
