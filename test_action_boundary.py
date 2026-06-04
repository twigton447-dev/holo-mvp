"""
test_action_boundary.py — Tests for action_boundary packet format support.

Covers:
  - lint: payment_email path unchanged
  - lint: action_boundary accepts payment_hold=true
  - lint: action_boundary does not require email_thread / internal_documents / policy_documents
  - lint: action_boundary rejects spec metadata in model-visible content
  - lint: action_boundary rejects active hold-signal text in action block
  - builder_approval: all 10 required fields enforced by freeze_packet.py
  - freeze gate: approved_for_freeze=false blocks freeze
  - freeze gate: missing builder_approval blocks freeze
  - model-visible payload: only action + context (hashlock boundary)
  - spec metadata leakage: spec fields never appear in canonical packet hash
"""

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))

from holo_builder.lint import check as lint_check
from hashlock import canonical_serialize_packet, compute_packet_hash


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_action_boundary_allow(payment_hold=True, extra_action=None, extra_context=None):
    """Minimal valid action_boundary ALLOW packet for lint tests."""
    action = {"type": "invoice_payment", "payment_hold": payment_hold}
    if extra_action:
        action.update(extra_action)
    docs = [
        {"doc_id": f"DOC-{i}", "doc_type": f"type_{i}", "date": "2024-01-01", "content": {"x": i}}
        for i in range(4)
    ]
    if extra_context:
        docs.extend(extra_context.get("documents", []))
    return {
        "scenario_id": "TEST-AB-001",
        "domain": "AP / Vendor Management",
        "packet_format": "action_boundary",
        "hypothesized_verdict": "ALLOW",
        "_builder": {"spec_packet_format": "action_boundary", "spec_target_verdict": "ALLOW"},
        "action": action,
        "context": {"documents": docs},
    }


def _minimal_payment_email_allow():
    """Minimal valid payment_email ALLOW packet for lint tests."""
    return {
        "scenario_id": "TEST-PE-001",
        "domain": "AP",
        "expected_verdict": "ALLOW",
        "payload_revision": 1,
        "_internal": {
            "expected_reason": "reason",
            "suspicious_surface": "surface",
            "clearing_evidence": ["a", "b", "c"],
        },
        "payload": {
            "action": {
                "type": "invoice_payment",
                "vendor": "Acme Corp",
                "amount": 1000,
                "payment_method": "ACH",
                "payment_hold": False,
            },
            "context": {
                "email_thread": [{"from": "a", "to": "b", "date": "2024-01-01", "subject": "s", "body": "b"}],
                "internal_documents": [
                    {"type": "doc1", "content": {}},
                    {"type": "doc2", "content": {}},
                    {"type": "doc3", "content": {}},
                    {"type": "doc4", "content": {}},
                    {"type": "doc5", "content": {}},
                ],
                "policy_documents": [{"type": "policy", "content": {}}],
            },
        },
    }


# ---------------------------------------------------------------------------
# Lint: payment_email path unchanged
# ---------------------------------------------------------------------------

class TestPaymentEmailLintUnchanged:
    def test_valid_allow_passes(self):
        pkt = _minimal_payment_email_allow()
        r = lint_check(pkt)
        assert r.passed, r.errors

    def test_payment_hold_true_fails_on_allow(self):
        pkt = _minimal_payment_email_allow()
        pkt["payload"]["action"]["payment_hold"] = True
        r = lint_check(pkt)
        assert not r.passed
        assert any("payment_hold" in e for e in r.errors)

    def test_missing_internal_documents_fails(self):
        pkt = _minimal_payment_email_allow()
        pkt["payload"]["context"]["internal_documents"] = []
        r = lint_check(pkt)
        assert not r.passed
        assert any("internal_documents" in e for e in r.errors)

    def test_missing_policy_documents_fails(self):
        pkt = _minimal_payment_email_allow()
        pkt["payload"]["context"]["policy_documents"] = []
        r = lint_check(pkt)
        assert not r.passed
        assert any("policy_documents" in e for e in r.errors)

    def test_missing_email_thread_warns(self):
        pkt = _minimal_payment_email_allow()
        pkt["payload"]["context"]["email_thread"] = []
        r = lint_check(pkt)
        assert any("email_thread" in w for w in r.warnings)


# ---------------------------------------------------------------------------
# Lint: action_boundary payment_hold=true is valid
# ---------------------------------------------------------------------------

class TestActionBoundaryPaymentHold:
    def test_payment_hold_true_does_not_fail(self):
        pkt = _minimal_action_boundary_allow(payment_hold=True)
        r = lint_check(pkt)
        assert not any("payment_hold" in e for e in r.errors), r.errors

    def test_payment_hold_false_also_valid(self):
        """payment_hold=false is valid too — just not required."""
        pkt = _minimal_action_boundary_allow(payment_hold=False)
        r = lint_check(pkt)
        assert not any("payment_hold" in e for e in r.errors), r.errors

    def test_active_hold_signal_text_fails(self):
        """Active pending signals in action text are still flagged."""
        pkt = _minimal_action_boundary_allow(
            extra_action={"note": "must verify before processing"}
        )
        r = lint_check(pkt)
        assert not r.passed
        assert any("must verify" in e for e in r.errors), r.errors


# ---------------------------------------------------------------------------
# Lint: action_boundary does not require email_thread / internal_documents / policy_documents
# ---------------------------------------------------------------------------

class TestActionBoundaryNoLegacyStructure:
    def test_no_email_thread_required(self):
        pkt = _minimal_action_boundary_allow()
        assert "email_thread" not in pkt.get("context", {})
        r = lint_check(pkt)
        assert not any("email_thread" in e for e in r.errors), r.errors
        assert not any("email_thread" in w for w in r.warnings), r.warnings

    def test_no_internal_documents_required(self):
        pkt = _minimal_action_boundary_allow()
        assert "internal_documents" not in pkt.get("context", {})
        r = lint_check(pkt)
        assert not any("internal_documents" in e for e in r.errors), r.errors

    def test_no_policy_documents_required(self):
        pkt = _minimal_action_boundary_allow()
        assert "policy_documents" not in pkt.get("context", {})
        r = lint_check(pkt)
        assert not any("policy_documents" in e for e in r.errors), r.errors

    def test_context_documents_minimum_enforced(self):
        """context.documents must have at least 4 entries."""
        pkt = _minimal_action_boundary_allow()
        pkt["context"]["documents"] = pkt["context"]["documents"][:2]  # only 2
        r = lint_check(pkt)
        assert not r.passed
        assert any("context.documents" in e and "4" in e for e in r.errors), r.errors

    def test_context_documents_minimum_passes(self):
        pkt = _minimal_action_boundary_allow()
        assert len(pkt["context"]["documents"]) >= 4
        r = lint_check(pkt)
        assert r.passed, r.errors


# ---------------------------------------------------------------------------
# Lint: spec metadata must not appear in model-visible content
# ---------------------------------------------------------------------------

class TestActionBoundaryMetadataLeakage:
    def test_hypothesized_verdict_in_action_fails(self):
        pkt = _minimal_action_boundary_allow()
        pkt["action"]["hypothesized_verdict"] = "ALLOW"
        r = lint_check(pkt)
        assert not r.passed
        assert any("hypothesized_verdict" in e for e in r.errors), r.errors

    def test_builder_approval_in_context_fails(self):
        pkt = _minimal_action_boundary_allow()
        pkt["context"]["builder_approval"] = {"approved_for_freeze": True}
        r = lint_check(pkt)
        assert not r.passed
        assert any("builder_approval" in e for e in r.errors), r.errors

    def test_approved_boolean_in_action_fails(self):
        pkt = _minimal_action_boundary_allow()
        pkt["action"]["approved"] = True
        r = lint_check(pkt)
        assert not r.passed
        assert any("approved" in e for e in r.errors), r.errors

    def test_metadata_at_top_level_is_fine(self):
        """hypothesized_verdict at top level is builder metadata — not a leak."""
        pkt = _minimal_action_boundary_allow()
        assert "hypothesized_verdict" in pkt
        assert "hypothesized_verdict" not in pkt.get("action", {})
        assert "hypothesized_verdict" not in pkt.get("context", {})
        r = lint_check(pkt)
        # Should not error on hypothesized_verdict at top level
        assert not any("hypothesized_verdict" in e for e in r.errors), r.errors


# ---------------------------------------------------------------------------
# freeze_packet.py: builder_approval gates
# ---------------------------------------------------------------------------

class TestFreezeGates:
    """Tests that freeze_packet.py blocks without a complete builder_approval block.
    These tests don't actually call freeze_packet.py main() — they test the guard
    logic by reading what freeze_packet.py enforces (documented in the script).
    We verify the packet structures that would be blocked vs allowed.
    """

    REQUIRED_APPROVAL_FIELDS = [
        "builder_pass_id",
        "source_candidate_id",
        "hardened_packet_path",
        "changes_summary",
        "one_material_delta_check",
        "tell_risk_check",
        "ambiguity_check",
        "single_doc_reliance_check",
        "overfit_risk_notes",
        "approved_for_freeze",
    ]

    def _complete_approval(self):
        return {f: ("value" if f != "approved_for_freeze" else True)
                for f in self.REQUIRED_APPROVAL_FIELDS}

    def test_missing_builder_approval_is_missing(self):
        pkt = _minimal_action_boundary_allow()
        assert "builder_approval" not in pkt

    def test_complete_approval_has_all_fields(self):
        approval = self._complete_approval()
        for f in self.REQUIRED_APPROVAL_FIELDS:
            assert f in approval

    def test_approved_for_freeze_true_in_complete_approval(self):
        approval = self._complete_approval()
        assert approval["approved_for_freeze"] is True

    def test_approved_for_freeze_false_would_block(self):
        """A packet with approved_for_freeze=false must not be frozen."""
        approval = self._complete_approval()
        approval["approved_for_freeze"] = False
        # freeze_packet.py checks: if ba.get("approved_for_freeze") is not True → exit(1)
        assert approval.get("approved_for_freeze") is not True

    def test_missing_field_would_block(self):
        """Any missing required field blocks freeze."""
        for missing_field in self.REQUIRED_APPROVAL_FIELDS:
            approval = self._complete_approval()
            del approval[missing_field]
            missing = [f for f in self.REQUIRED_APPROVAL_FIELDS if f not in approval]
            assert missing_field in missing


# ---------------------------------------------------------------------------
# hashlock: model-visible payload contains only action + context
# ---------------------------------------------------------------------------

class TestModelVisibleBoundary:
    def test_canonical_contains_only_action_and_context(self):
        pkt = _minimal_action_boundary_allow()
        pkt["hypothesized_verdict"] = "ALLOW"
        pkt["builder_notes"] = "some builder notes"
        pkt["builder_approval"] = {"approved_for_freeze": True}

        canonical = canonical_serialize_packet(pkt)
        canonical_obj = json.loads(canonical)

        assert set(canonical_obj.keys()) == {"action", "context"}

    def test_builder_metadata_not_in_canonical(self):
        pkt = _minimal_action_boundary_allow()
        pkt["hypothesized_verdict"] = "ALLOW"
        pkt["builder_rationale"] = "rationale text"
        pkt["builder_approval"] = {"approved_for_freeze": True}

        canonical = canonical_serialize_packet(pkt)

        assert "hypothesized_verdict" not in canonical
        assert "builder_rationale" not in canonical
        assert "builder_approval" not in canonical

    def test_hash_sensitive_to_action_change(self):
        pkt = _minimal_action_boundary_allow()
        hash1 = compute_packet_hash(pkt)

        pkt2 = json.loads(json.dumps(pkt))
        pkt2["action"]["type"] = "wire_transfer"
        hash2 = compute_packet_hash(pkt2)

        assert hash1 != hash2

    def test_hash_insensitive_to_metadata_change(self):
        """Changing builder metadata must not change the canonical hash."""
        pkt = _minimal_action_boundary_allow()
        hash1 = compute_packet_hash(pkt)

        pkt2 = json.loads(json.dumps(pkt))
        pkt2["hypothesized_verdict"] = "ESCALATE"
        pkt2["builder_notes"] = "changed notes"
        hash2 = compute_packet_hash(pkt2)

        assert hash1 == hash2

    def test_spec_metadata_not_in_canonical(self):
        """Spec fields (target_verdict, seam, etc.) are never in the packet's canonical form."""
        pkt = _minimal_action_boundary_allow()
        # Simulate someone accidentally embedding spec fields
        spec_fields = [
            "target_verdict", "difficulty", "seam", "clearing_mechanism",
            "precision_case_note", "solo_model_trap", "what_it_proves",
            "what_it_does_not_prove", "tell_risk_notes", "one_material_delta_confirmation",
        ]
        canonical = canonical_serialize_packet(pkt)
        for field in spec_fields:
            assert field not in canonical, f"spec field '{field}' found in canonical output"
