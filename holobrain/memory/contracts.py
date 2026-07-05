"""Minimal offline contracts for HoloBrain memory smoke tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


RAW_TRACE_DEFAULT_PAYLOAD_KEYS = frozenset(
    {
        "raw_trace",
        "raw_trace_dump",
        "raw_traces",
        "raw_log",
        "raw_logs",
        "full_trace",
        "full_transcript",
        "full_model_output",
    }
)

AUTHORITY_RANKS = {
    "anecdote": 1,
    "single_diagnostic_note": 2,
    "repeated_empirical_pattern": 3,
    "locked_artifact_backed_case": 4,
    "formal_policy": 5,
}


@dataclass(frozen=True)
class LaneFidelityContract:
    lane: str
    reference_audit_fidelity: str
    prompt_injection: str
    lossless_by_default_fields: tuple[str, ...]
    full_corpus_injected: bool = False


@dataclass(frozen=True)
class PolicyClause:
    clause_id: str
    operative_text: str
    source_ref: str
    authority_level: str = "formal_policy"


@dataclass(frozen=True)
class PolicyObject:
    policy_id: str
    lane_scope: tuple[str, ...]
    domain: str
    title: str
    clauses: tuple[PolicyClause, ...]
    full_text_ref: str
    status: str = "active"
    superseded_by: str | None = None

    def active_for(self, lane: str, domain: str) -> bool:
        return (
            self.status == "active"
            and self.superseded_by is None
            and lane in self.lane_scope
            and self.domain == domain
        )


@dataclass(frozen=True)
class CaseExperience:
    case_id: str
    lane_scope: tuple[str, ...]
    domain: str
    case_type: str
    confidence: str
    summary: str
    trigger_pattern: tuple[str, ...]
    failed_approaches: tuple[str, ...]
    successful_resolution: str
    decision_lessons: tuple[str, ...]
    scope_limits: tuple[str, ...]
    non_generalization_conditions: tuple[str, ...]
    related_policy_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    status: str = "active"
    superseded_by: str | None = None

    def __post_init__(self) -> None:
        if not self.scope_limits:
            raise ValueError("case_experience requires scope_limits")
        if not self.non_generalization_conditions:
            raise ValueError("case_experience requires non_generalization_conditions")

    def active_for(self, lane: str, domain: str) -> bool:
        return (
            self.status == "active"
            and self.superseded_by is None
            and lane in self.lane_scope
            and self.domain == domain
        )

    @property
    def authority_level(self) -> str:
        if self.confidence == "locked_artifact_backed":
            return "locked_artifact_backed_case"
        return self.confidence


@dataclass(frozen=True)
class RetrievalInjectionAudit:
    lane: str
    domain: str
    retrieved_policy_ids: tuple[str, ...]
    retrieved_case_ids: tuple[str, ...]
    injected_policy_clause_ids: tuple[str, ...]
    injected_case_ids: tuple[str, ...]
    referenced_substrate_refs: tuple[str, ...]
    suppressed_policy_ids: tuple[str, ...]
    suppressed_case_ids: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalSlice:
    live_injection: Mapping[str, Any]
    referenced_substrate: Mapping[str, Any]
    audit: RetrievalInjectionAudit


@dataclass(frozen=True)
class MaintenanceCandidate:
    agent_name: str
    proposal_type: str
    target_ref: str
    proposed_change: Mapping[str, Any]
    approval_status: str = "queued"

    @property
    def can_silently_promote_truth(self) -> bool:
        return False


def lane_fidelity_contract(lane: str) -> LaneFidelityContract:
    if lane == "HoloGov-C":
        return LaneFidelityContract(
            lane=lane,
            reference_audit_fidelity="compact",
            prompt_injection="rolling_summary",
            lossless_by_default_fields=(
                "explicit_user_instructions",
                "critical_constraints",
                "settled_decisions",
                "privacy_boundaries",
                "pinned_artifact_refs",
            ),
        )
    if lane == "HoloGov-B":
        return LaneFidelityContract(
            lane=lane,
            reference_audit_fidelity="near_lossless",
            prompt_injection="compact_operational_slice",
            lossless_by_default_fields=(
                "source_references",
                "artifact_versions",
                "requirement_closure",
                "claim_maps",
                "validation_gates",
                "rejected_findings",
                "repair_notes",
                "final_artifact_audits",
            ),
        )
    if lane == "HoloGov-V":
        return LaneFidelityContract(
            lane=lane,
            reference_audit_fidelity="near_lossless",
            prompt_injection="compact_operational_slice",
            lossless_by_default_fields=(
                "proposed_action",
                "authority_rules",
                "required_controls",
                "evidence_references",
                "verdict_basis",
                "blocker_ledger",
                "allow_ledger",
                "flip_condition",
                "decision_audit",
            ),
        )
    raise ValueError(f"unknown HoloGov lane: {lane}")


def assert_no_raw_trace_default_payload(payload: Mapping[str, Any]) -> None:
    present = RAW_TRACE_DEFAULT_PAYLOAD_KEYS.intersection(payload)
    if present:
        keys = ", ".join(sorted(present))
        raise ValueError(f"raw trace fields are referenced substrate only by default: {keys}")


def build_retrieval_slice(
    *,
    lane: str,
    domain: str,
    policies: Sequence[PolicyObject],
    cases: Sequence[CaseExperience],
) -> RetrievalSlice:
    active_policies = [policy for policy in policies if policy.active_for(lane, domain)]
    active_cases = [case for case in cases if case.active_for(lane, domain)]
    suppressed_policies = [policy for policy in policies if not policy.active_for(lane, domain)]
    suppressed_cases = [case for case in cases if not case.active_for(lane, domain)]

    injected_policy_clauses = [
        {
            "policy_id": policy.policy_id,
            "clause_id": clause.clause_id,
            "operative_text": clause.operative_text,
            "source_ref": clause.source_ref,
        }
        for policy in active_policies
        for clause in policy.clauses
    ]
    injected_case_lessons = [
        {
            "case_id": case.case_id,
            "summary": case.summary,
            "decision_lessons": case.decision_lessons,
            "scope_limits": case.scope_limits,
            "non_generalization_conditions": case.non_generalization_conditions,
            "evidence_refs": case.evidence_refs,
        }
        for case in active_cases
    ]
    referenced_policy_refs = tuple(policy.full_text_ref for policy in active_policies)
    referenced_case_refs = tuple(
        ref for case in active_cases for ref in case.evidence_refs
    )

    live_injection = {
        "lane": lane,
        "domain": domain,
        "policy_clauses": tuple(injected_policy_clauses),
        "case_lessons": tuple(injected_case_lessons),
    }
    referenced_substrate = {
        "policy_refs": referenced_policy_refs,
        "case_evidence_refs": referenced_case_refs,
    }
    audit = RetrievalInjectionAudit(
        lane=lane,
        domain=domain,
        retrieved_policy_ids=tuple(policy.policy_id for policy in active_policies),
        retrieved_case_ids=tuple(case.case_id for case in active_cases),
        injected_policy_clause_ids=tuple(
            f"{policy.policy_id}#{clause.clause_id}"
            for policy in active_policies
            for clause in policy.clauses
        ),
        injected_case_ids=tuple(case.case_id for case in active_cases),
        referenced_substrate_refs=referenced_policy_refs + referenced_case_refs,
        suppressed_policy_ids=tuple(policy.policy_id for policy in suppressed_policies),
        suppressed_case_ids=tuple(case.case_id for case in suppressed_cases),
    )
    assert_no_raw_trace_default_payload(live_injection)
    return RetrievalSlice(
        live_injection=live_injection,
        referenced_substrate=referenced_substrate,
        audit=audit,
    )


def authority_rank(authority_level: str) -> int:
    try:
        return AUTHORITY_RANKS[authority_level]
    except KeyError as exc:
        raise ValueError(f"unknown authority level: {authority_level}") from exc


def highest_authority(items: Iterable[PolicyObject | CaseExperience]) -> PolicyObject | CaseExperience:
    return max(
        items,
        key=lambda item: authority_rank(
            "formal_policy"
            if isinstance(item, PolicyObject)
            else item.authority_level
        ),
    )


def promote_maintenance_candidate(
    candidate: MaintenanceCandidate,
    *,
    approval_id: str | None = None,
) -> Mapping[str, Any]:
    if candidate.approval_status != "approved" or not approval_id:
        raise PermissionError("maintenance candidates require explicit approval to promote")
    return {
        "status": "promotion_ready",
        "approval_id": approval_id,
        "candidate": candidate,
    }
