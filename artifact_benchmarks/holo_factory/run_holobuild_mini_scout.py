from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_holo_factory_suite import PROVIDER_ENV, ProviderCallError, call_provider, provider_model

FACTORY_DIR = Path(__file__).resolve().parent
REPO_ROOT = FACTORY_DIR.parents[1]
DEFAULT_SUITE_MANIFEST = FACTORY_DIR / "mini_scouts/TEN_DOMAIN_PACKET_SUITE_MANIFEST.json"
D11_PACKET_DIR_REL = "artifact_benchmarks/holo_factory/mini_scouts/d11_cyber_incident_contract_notice_emergency_cloud_access_001"
D12_PACKET_DIR_REL = "artifact_benchmarks/holo_factory/mini_scouts/d12_fund_nav_redemption_cash_release_001"
D11_RUNNER_DOMAIN_ENTRY = {
    "domain_id": "D11",
    "domain_name": "Cyber Incident / Contract Notice / Emergency Cloud Access",
    "packet_id": "d11_cyber_incident_contract_notice_emergency_cloud_access_001",
    "packet_dir": D11_PACKET_DIR_REL,
    "packet_hash": "2e80109e4149da65b241452a5ffc194fb4caf4117d204616a1065eb47afde371",
    "source_packet_hash": "2e80109e4149da65b241452a5ffc194fb4caf4117d204616a1065eb47afde371",
    "packet_lock_hash": "27ba069ef63c8c14386ef43a974c316320ebeb5067cfa4623aa9446632e70564",
    "freeze_manifest_hash": "23575df2ac7e5129a7e917e92dbc70402614c199035ef752601387c1c02c32f2",
    "validator_path": f"{D11_PACKET_DIR_REL}/validate_packet_no_provider.py",
}
D12_RUNNER_DOMAIN_ENTRY = {
    "domain_id": "D12",
    "domain_name": "Fund NAV / Redemption / Cash Release",
    "packet_id": "d12_fund_nav_redemption_cash_release_001",
    "packet_dir": D12_PACKET_DIR_REL,
    "packet_hash": "fce82318244558dbd36b0b8aec377bc0c180c885a8c9d5ed3b5a7a703c605bb0",
    "source_packet_hash": "fce82318244558dbd36b0b8aec377bc0c180c885a8c9d5ed3b5a7a703c605bb0",
    "packet_lock_hash": "0550af2c53affb28bdf367be27a2e684007b0eb4c61c484656f458a1eaff2f4f",
    "freeze_manifest_hash": "2a0a0d4fca56a3a542a56b5cf84ab2d4530e57200ab98f199f8f56b26e8a125f",
    "validator_path": f"{D12_PACKET_DIR_REL}/validate_packet_no_provider.py",
}
CONFIG_DIR = FACTORY_DIR / "configs"
D3_SUCCESS_TEMPLATE_LOCK = CONFIG_DIR / "holo_session_template_d3_success_v1.lock.json"
GROK_SWAP_TEMPLATE_LOCK = CONFIG_DIR / "holo_session_template_grok_swap_v1.lock.json"
OPUS_GOV_B_TEMPLATE_LOCK = CONFIG_DIR / "holo_session_template_opus_gov_b_v1.lock.json"
FRONTIER_OPTIMIZED_OPUS_GPT55_TEMPLATE_LOCK = CONFIG_DIR / "holo_session_template_frontier_optimized_opus_gpt55_v1.lock.json"
LIVE_APPROVAL_ENV = "HOLO_ALLOW_LIVE"
PROOF_ELIGIBLE_HOLO_MODE = "patent_aligned_v4"
LEGACY_HOLO_MODES = {"diagnostic_v3", "full_gov_v4"}
HOLO_MODES = ("diagnostic_v3", "full_gov_v4", "patent_aligned_v4")
HOLO_CONTEXT_PROFILES = ("full_registry", "latest_only")
DEFAULT_HOLO_CONTEXT_PROFILE = "full_registry"
MAX_HOLO_FINAL_REPAIR_ATTEMPTS = 1
MAX_HOLO_FINAL_COMPRESSION_REPAIR_ATTEMPTS = 1
MAX_HOLO_INTERMEDIATE_REPAIR_ATTEMPTS = 1
DEFAULT_TURN_MAX_TOKENS = 3800
FINAL_SYNTHESIS_MAX_TOKENS = 6000
FINAL_REPAIR_MAX_TOKENS = 5200
INTERMEDIATE_REPAIR_MAX_TOKENS = 3600
HOLO_SESSION_TEMPLATES = ("random", "d3_success_v1", "grok_swap_v1", "opus_gov_b_v1", "frontier_optimized_opus_gpt55_v1")
D3_SUCCESS_HOLO_TURN_MODELS = (
    "google:gemini-3.1-pro-preview",
    "openai:gpt-5.5",
    "anthropic:claude-opus-4-8",
    "google:gemini-3.1-pro-preview",
    "openai:gpt-5.5",
    "anthropic:claude-opus-4-8",
)
D3_SUCCESS_GOV_MODEL = "openai:gpt-5.5"
GROK_SWAP_HOLO_TURN_MODELS = (
    "google:gemini-3.1-pro-preview",
    "xai:grok-4.3",
    "anthropic:claude-opus-4-8",
    "google:gemini-3.1-pro-preview",
    "xai:grok-4.3",
    "anthropic:claude-opus-4-8",
)
GROK_SWAP_GOV_MODEL = "xai:grok-4.3"
OPUS_GOV_B_GOV_MODEL = "anthropic:claude-opus-4-8"
FRONTIER_OPTIMIZED_OPUS_GPT55_HOLO_TURN_MODELS = (
    "openai:gpt-5.5",
    "openai:gpt-5.5",
    "anthropic:claude-opus-4-8",
    "openai:gpt-5.5",
    "openai:gpt-5.5",
    "anthropic:claude-opus-4-8",
)
FRONTIER_OPTIMIZED_OPUS_GPT55_GOV_MODEL = "anthropic:claude-opus-4-8"
VALID_CONDITIONS = (
    "HoloFull",
    "HoloFullGrokSwap",
    "HoloFullOpusGovB",
    "HoloFrontierOptimizedOpusGPT55",
    "HoloMini",
    "SoloFull",
    "SoloFullGrok",
    "SoloMini",
    "holo_build_arch",
    "holo_build_arch_grok_swap",
    "holo_build_arch_opus_gov_b",
    "holo_build_arch_frontier_optimized_opus_gpt55",
    "solo_openai_gpt_5_5",
    "solo_xai_grok_4_3",
    "solo_anthropic_claude_opus_4_8",
    "frontier_solo_v1",
    "frontier_solo_grok_4_3_v1",
    "frontier_solo_opus_4_8_v1",
    "frontier_holo_v1",
    "frontier_holo_grok_swap_v1",
    "frontier_holo_opus_gov_b_v1",
    "frontier_holo_optimized_opus_gpt55_v1",
    "mini_solo_v1",
    "mini_holo_v1",
)
FINAL_WORD_MIN = 900
FINAL_WORD_MAX = 1300
FINAL_WORD_TARGET = 1250
FINAL_WORD_PERSUASIVE_MAX = 1500
FINAL_WORD_EXTREME_MAX = 1800
ARCHITECTURE_POLICY_ID = "HOLOBUILD_ARCHITECTURE_POLICY_V4_2"
ARCHITECTURE_POLICY_VERSION = "v4.2"
ARCHITECTURE_POLICY_PATH = FACTORY_DIR / "architecture_policies/holobuild_architecture_policy_v4_2.json"
INTERMEDIATE_DEFAULT_MIN_WORDS = 250
FINAL_REPAIR_TARGET_WORDS = 1180
FINAL_REPAIR_HARD_MAX_WORDS = FINAL_WORD_MAX
FINAL_REPAIR_KIND_MISSING_SECTION = "missing_section_repair"
FINAL_REPAIR_KIND_COMPRESSION_ONLY = "compression_only_final_repair"
FINAL_REPAIR_KIND_CLAIM_BOUNDARY_ONLY = "claim_boundary_only_repair"
FINAL_CLAIM_BOUNDARY_REPAIR_MIN_WORDS = 1050
FINAL_CLAIM_BOUNDARY_REPAIR_MAX_WORDS = 1150
HOLOGOV_C_TENURE_MIN = 7
HOLOGOV_C_TENURE_MAX = 11
PROVIDER_CALLS = 0
ACCEPTED_PROVIDER_CALLS = 0
FAILED_PROVIDER_CALLS = 0
SCORES_GENERATED = 0

SOLO_TURNS = (
    ("initial_decision_brief_draft", "Write an initial decision-grade crisis/action brief draft. This is not final."),
    ("assumption_and_evidence_attack", "Attack the prior draft for unsupported assumptions, weak evidence, missing calculations, source quality flattening, and missing risks."),
    ("contradiction_uncertainty_source_fidelity_pass", "Revise for contradictory evidence, uncertainty, stale or weak source handling, and source-fidelity problems."),
    ("options_risks_operational_usefulness_pass", "Revise for practical options, risks of acting, risks of waiting, stop/go triggers, and operational usefulness for leadership."),
    ("claim_discipline_overclaim_reduction_pass", "Cut unsupported claims, reduce overclaiming, tighten source citations, and prepare a concise final version."),
    ("final_synthesis_900_1300_words", "Return only the final decision-grade crisis/action brief. Final artifact body must be 900-1,300 words."),
)
HOLO_TURNS = (
    ("initial_decision_brief_drafter", "anthropic:claude-opus-4-8", "Draft a source-grounded initial decision frame covering what is happening, why it matters, and the main options. This is not final."),
    ("assumption_and_evidence_attacker", "google:gemini-3.1-pro-preview", "Attack assumptions, weak evidence, stale claims, missing calculations, and unsupported causal links."),
    ("contradiction_uncertainty_source_fidelity_reviewer", "openai:gpt-5.5", "Stress-test contradictory evidence, source fidelity, source-status boundaries, and uncertainty handling."),
    ("options_operational_usefulness_reviewer", "anthropic:claude-opus-4-8", "Stress-test practical options, risks of acting, risks of waiting, operating gates, and usefulness for leadership."),
    ("claim_discipline_overclaim_reducer", "google:gemini-3.1-pro-preview", "Reduce unsupported claims, identify overclaim risks, and prepare final-brief constraints."),
    ("final_synthesis_author", "openai:gpt-5.5", "Return only the final decision-grade crisis/action brief, 900-1,300 body words, target 1,180; do not exceed 1,300 words."),
)
INTERMEDIATE_ROLE_MIN_WORDS = {
    "initial_decision_brief_drafter": 420,
    "assumption_and_evidence_attacker": 320,
    "contradiction_uncertainty_source_fidelity_reviewer": 340,
    "options_operational_usefulness_reviewer": 340,
    "claim_discipline_overclaim_reducer": 320,
}
REQUIRED_INTERMEDIATE_ROLES = frozenset(INTERMEDIATE_ROLE_MIN_WORDS)
GENERATION_ARGUMENT_QUALITY_GUIDANCE = (
    "Optimize for strong decision quality: not just safe compliance, but stronger thinking. "
    "After source fidelity, action-boundary safety, and claim discipline are preserved, argument strength and practical judgment matter. "
    "A merely safe, complete, or well-cited artifact is not enough; the final artifact must be the more convincing and more powerful decision argument. "
    "The final brief must have a sharp central thesis, clean evidence-to-decision argument, persuasive uncertainty handling, "
    "non-generic insights, source synthesis, practical judgment, and explicit handling of the best counterargument. "
    "Do not make the brief longer to sound stronger; keep the final artifact within the hard 900-1,300 word band."
)
EXACT_SOURCE_ID_GENERATION_INSTRUCTION = (
    "Use exact full source_id strings from the source packet. Do not abbreviate, rename, shorten, or invent source IDs. "
    "Do not use S1/S2-style shorthand unless the exact source_id itself is literally S1 or S2. "
    "Claims that rely on sources must preserve the exact source_id string."
)
FINAL_SYNTHESIS_TRIGGER_TAXONOMY = (
    "In the final synthesis, convert the recommendation into an executable trigger taxonomy: broad-action go/no-go, "
    "narrow/conditional go, hold/escalate, revoke/rollback/stop, and post-action review or follow-up where relevant. "
    "Use packet-specific names when the packet supplies required practical response options."
)
FINAL_SYNTHESIS_REQUIRED_HEADINGS = (
    "Bottom line",
    "Risks of acting",
    "Risks of waiting",
    "Next steps / stop-go gates",
    "Claim boundaries",
)
FINAL_SYNTHESIS_HEADING_TEMPLATE = (
    "FINAL SYNTHESIS REQUIRED HEADING TEMPLATE\n"
    "=========================================\n"
    "Use exactly these five headings in the final artifact:\n"
    + "\n".join(f"- {heading}" for heading in FINAL_SYNTHESIS_REQUIRED_HEADINGS)
)
FINAL_SYNTHESIS_CLAIM_BOUNDARY_CONTRACT = (
    "The Claim boundaries section must explicitly state what the brief does not conclude and what remains unsupported until gates pass. "
    "Preserve exact source IDs, do not invent source IDs, stay within the 900-1300 word band, and end with a complete standalone sentence."
)
INTERMEDIATE_REPAIR_CLEAN_ENDING_CONTRACT = (
    "INTERMEDIATE REPAIR CLEAN ENDING CONTRACT\n"
    "==========================================\n"
    "End with one complete standalone sentence.\n"
    "Do not end mid-sentence.\n"
    "Do not end in an unfinished list item.\n"
    "Do not end in a dangling parenthesis, slash, markdown emphasis, code fence, table row, JSON fragment, or metadata/footer.\n"
    "Do not append a word-count footer."
)
T3_CONCISE_AUDIT_MIN_WORDS = 700
T3_CONCISE_AUDIT_MAX_WORDS = 900
T3_CONCISE_AUDIT_SECTION_ITEMS = (
    "Top 5 source-boundary risks",
    "Top 5 uncertainty claims to preserve",
    "Stale / weak / derived source cautions",
    "Exact source-ID audit",
    "Final synthesis instructions",
)
T3_CONCISE_AUDIT_CONTRACT = (
    "CONTRADICTION / UNCERTAINTY / SOURCE-FIDELITY COMPACT AUDIT CONTRACT\n"
    "====================================================================\n"
    "For contradiction_uncertainty_source_fidelity_reviewer, return a compact audit, not a prose essay. "
    f"Target {T3_CONCISE_AUDIT_MIN_WORDS}-{T3_CONCISE_AUDIT_MAX_WORDS} words. Use compact bullets or numbered items. "
    "Preserve exact source IDs; do not abbreviate, rename, shorten, or invent source IDs. "
    "Do not treat derived, stale, weak, preliminary, or internal notes as governing authority. "
    "Do not resolve factual uncertainty that the packet leaves open. "
    "End with one complete standalone sentence and do not add a word-count footer.\n"
    "Use exactly these five required sections:\n"
    + "\n".join(f"{index}. {item}" for index, item in enumerate(T3_CONCISE_AUDIT_SECTION_ITEMS, start=1))
)
T3_CONCISE_AUDIT_REPAIR_CONTRACT = (
    "T3 COMPACT SOURCE-FIDELITY REPAIR REQUIRED FORMAT\n"
    "=================================================\n"
    "The previous T3 failed because it was incomplete/truncated. "
    "Return only the corrected compact T3 audit. Do not continue the prior text. Do not produce an essay. "
    "Use the five required sections below. "
    f"Target {T3_CONCISE_AUDIT_MIN_WORDS}-{T3_CONCISE_AUDIT_MAX_WORDS} words. "
    "End with one complete standalone sentence.\n"
    + "\n".join(f"{index}. {item}" for index, item in enumerate(T3_CONCISE_AUDIT_SECTION_ITEMS, start=1))
)
OPTIONS_OPERATIONAL_REPAIR_CHECKLIST_ITEMS = (
    "Available options",
    "Risk of acting",
    "Risk of waiting",
    "Must be true before execution",
    "Stop/go triggers",
    "Signal that stops execution",
    "Signal that permits expansion",
    "What can be reversed",
    "What cannot be reversed",
    "Rollback gates",
    "Monitoring/logging gates",
    "Executive next actions",
    "Dependency chain",
    "What must be observable before rollback/canary can be trusted",
)
OPTIONS_OPERATIONAL_REPAIR_CHECKLIST = (
    "OPTIONS OPERATIONAL REPAIR REQUIRED CHECKLIST\n"
    "==============================================\n"
    "This repair will be validated against the V4.2 options_operational_usefulness_reviewer role-specific validator. "
    "Omission of any required component fails the repair. Use explicit headings or clearly matched phrases for every component below, "
    "and put at least one substantive sentence under each heading. Keyword-only output still fails.\n"
    + "\n".join(f"- {item}" for item in OPTIONS_OPERATIONAL_REPAIR_CHECKLIST_ITEMS)
)
ASSUMPTION_EVIDENCE_REPAIR_CHECKLIST_ITEMS = (
    "Revision pressure",
    "What the final should revise",
    "What the final should avoid",
    "What assumptions must be challenged",
    "What unsupported claim must be tightened",
    "Source-ID copy discipline",
)
ASSUMPTION_EVIDENCE_REPAIR_CHECKLIST = (
    "ASSUMPTION AND EVIDENCE ATTACKER REPAIR REQUIRED CHECKLIST\n"
    "==========================================================\n"
    "This repair will be validated against the V4.2 assumption_and_evidence_attacker role-specific validator. "
    "The repair must create revision pressure for the final artifact, specify what the final should revise and avoid, "
    "challenge assumptions, tighten unsupported claims, and preserve exact source IDs copied from the retrieved source packet. "
    "Do not invent, abbreviate, rename, shorten, or mutate source IDs. Keyword-only output still fails.\n"
    + "\n".join(f"- {item}" for item in ASSUMPTION_EVIDENCE_REPAIR_CHECKLIST_ITEMS)
)
FINAL_REQUIRED_SECTION_PATTERNS = {
    "bottom_line": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?(?:bottom line|recommendation|bottom-line)"),
    "risks_of_acting": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?risks?\s+of\s+acting"),
    "risks_of_waiting": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?risks?\s+of\s+waiting"),
    "next_steps": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?(?:(?:recommended\s+)?next\s+steps|next\s+steps\s*/\s*stop-go\s+gates|trigger\s+taxonomy)"),
    "claim_boundaries": re.compile(r"(?im)^#{1,3}\s*(?:\d+\.\s*)?(?:claim\s+boundaries|counterargument\s+and\s+claim\s+boundaries|counterargument\s*/\s*claim\s+boundaries|boundaries\s+and\s+uncertainty|disclaimer|claim\s+boundaries\s*/\s*disclaimer)"),
}
CLAIM_BOUNDARY_SUBSTANTIVE_RE = re.compile(
    r"\b("
    r"does\s+not\s+conclude|"
    r"does\s+not\s+establish|"
    r"does\s+not\s+prove|"
    r"unsupported\s+until|"
    r"unsupported\s+before|"
    r"not\s+supported\s+until|"
    r"not\s+authorized\s+until|"
    r"cannot\s+support\s+final\s+release|"
    r"cannot\s+support\s+final\s+commitment|"
    r"before\s+gates\s+pass|"
    r"until\s+gates\s+pass|"
    r"invents\s+no\s+approvals|"
    r"not\s+a\s+deterministic\s+[^.!?]{0,80}\s+verdict|"
    r"no\s+[^.!?]{0,80}\s+asserted\s+as\s+validated"
    r")\b",
    flags=re.IGNORECASE,
)
FINAL_CLEAN_ENDING_RE = re.compile(r"[.!?][\"')\]]*$")
UNCLEAN_INTERMEDIATE_ENDING_RE = re.compile(r"[*_\-:;,(\[{]$")
SOURCE_ID_RE = re.compile(r"\bS\d+_[A-Z0-9_]+\b")
ACTIVE_SCORING_LOCK_PATH = FACTORY_DIR / "scoring_policies/ACTIVE_SCORING_PROTOCOL.lock.json"
HARD_FORBIDDEN_JUDGE_VISIBLE_PATTERNS = {
    "holo_label": re.compile(r"\bholo(build|gov|full|mini|_build_arch)?\b", re.IGNORECASE),
    "gpt_label": re.compile(r"\bgpt[-_ ]?5(?:\.5)?\b", re.IGNORECASE),
    "provider_model": re.compile(r"\bprovider_model\b", re.IGNORECASE),
    "token_burn": re.compile(r"\b(token_burn|input_tokens|output_tokens|total_tokens)\b", re.IGNORECASE),
    "architecture_evidence": re.compile(r"\barchitecture_evidence\b", re.IGNORECASE),
    "arch_evidence": re.compile(r"\barch_evidence\b", re.IGNORECASE),
    "run_id": re.compile(r"\brun_id\b", re.IGNORECASE),
    "state_object": re.compile(r"\bstate_object\b", re.IGNORECASE),
    "baton_pass": re.compile(r"\bbaton_pass\b", re.IGNORECASE),
    "artifact_registry": re.compile(r"\bartifact_registry\b", re.IGNORECASE),
}
CONTEXT_SENSITIVE_JUDGE_VISIBLE_PATTERNS = {
    "condition_metadata": re.compile(
        r"\b(condition_id|benchmark_condition|condition_family|holo_condition|solo_condition|generation_condition|condition_manifest|condition_type|model_condition)\b",
        re.IGNORECASE,
    ),
    "internal_metadata": re.compile(
        r"\b(internal_generation|internal_state|internal_label|internal_scaffold|internal_process|internal_run|internal_metadata|builder_internal)\b",
        re.IGNORECASE,
    ),
}


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def active_scoring_protocol() -> dict[str, Any]:
    if not ACTIVE_SCORING_LOCK_PATH.exists():
        return {
            "active_scoring_protocol_id": "unified_artifact_scoring_protocol_v6_structural_epistemic",
            "lock_path": repo_rel(ACTIVE_SCORING_LOCK_PATH),
            "lock_missing": True,
        }
    lock = read_json(ACTIVE_SCORING_LOCK_PATH)
    return {
        "active_scoring_protocol_id": lock.get("active_scoring_protocol_id"),
        "protocol_path": lock.get("protocol_path"),
        "protocol_hash": lock.get("protocol_hash"),
        "schema_path": lock.get("schema_path"),
        "schema_hash": lock.get("schema_hash"),
        "lock_path": lock.get("lock_path"),
        "lock_hash": lock.get("lock_hash"),
    }


def repo_rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


_ARCHITECTURE_POLICY_CACHE: dict[str, Any] | None = None


def load_architecture_policy() -> dict[str, Any]:
    global _ARCHITECTURE_POLICY_CACHE
    if _ARCHITECTURE_POLICY_CACHE is not None:
        return _ARCHITECTURE_POLICY_CACHE
    if not ARCHITECTURE_POLICY_PATH.exists():
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "architecture_policy_missing",
            "expected_policy_id": ARCHITECTURE_POLICY_ID,
            "policy_path": repo_rel(ARCHITECTURE_POLICY_PATH),
            "provider_calls": 0,
        }, indent=2))
    policy = read_json(ARCHITECTURE_POLICY_PATH)
    if policy.get("policy_id") != ARCHITECTURE_POLICY_ID:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "architecture_policy_id_mismatch",
            "expected_policy_id": ARCHITECTURE_POLICY_ID,
            "actual_policy_id": policy.get("policy_id"),
            "policy_path": repo_rel(ARCHITECTURE_POLICY_PATH),
            "provider_calls": 0,
        }, indent=2))
    _ARCHITECTURE_POLICY_CACHE = policy
    return policy


def architecture_policy_lock_path() -> Path | None:
    candidates = [
        ARCHITECTURE_POLICY_PATH.with_suffix(".lock.json"),
        ARCHITECTURE_POLICY_PATH.with_name(ARCHITECTURE_POLICY_PATH.stem + ".lock.json"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


def architecture_policy_ref() -> dict[str, Any]:
    policy = load_architecture_policy()
    lock_path = architecture_policy_lock_path()
    return {
        "policy_id": policy.get("policy_id"),
        "policy_version": ARCHITECTURE_POLICY_VERSION,
        "policy_path": repo_rel(ARCHITECTURE_POLICY_PATH),
        "policy_hash": sha_file(ARCHITECTURE_POLICY_PATH),
        "policy_missing": False,
        "lock_path": repo_rel(lock_path) if lock_path else None,
        "lock_hash": sha_file(lock_path) if lock_path else None,
    }


def intermediate_registry_policy() -> dict[str, Any]:
    return load_architecture_policy().get("intermediate_registry_gate") or {}


def intermediate_default_min_words() -> int:
    return int(intermediate_registry_policy().get("default_min_visible_words", INTERMEDIATE_DEFAULT_MIN_WORDS))


def intermediate_role_min_words() -> dict[str, int]:
    role_words = intermediate_registry_policy().get("role_min_visible_words") or {}
    return {str(role): int(words) for role, words in role_words.items()}


def required_intermediate_roles() -> frozenset[str]:
    return frozenset(intermediate_role_min_words())


def final_word_band_policy() -> dict[str, int]:
    policy = load_architecture_policy().get("final_word_band_compliance") or {}
    return {
        "min_words": int(policy.get("min_words", FINAL_WORD_MIN)),
        "max_words": int(policy.get("max_words", FINAL_WORD_MAX)),
        "repair_target_words": int(policy.get("repair_target_words", FINAL_REPAIR_TARGET_WORDS)),
    }


def architecture_evidence_summary(evidence_turns: list[dict[str, Any]], precheck: dict[str, Any], holo_mode: str) -> dict[str, Any]:
    final_turns = [
        item for item in evidence_turns
        if item.get("role") == "final_synthesis_author" or item.get("turn") == len(HOLO_TURNS)
    ]
    final_retrieved_ids: set[str] = set()
    if final_turns:
        final_retrieved_ids = set(final_turns[-1].get("retrieved_artifact_ids") or [])

    role_failures = [
        {"turn": item.get("turn"), "role": item.get("role"), "role_compliance": item.get("role_compliance")}
        for item in evidence_turns
        if (item.get("role_compliance") or {}).get("status") != "pass"
    ]
    state_failures = [
        {"turn": item.get("turn"), "role": item.get("role"), "state_audit": item.get("state_audit")}
        for item in evidence_turns
        if (item.get("state_audit") or {}).get("status") != "pass"
    ]
    prompt_hash_missing = [
        item.get("turn")
        for item in evidence_turns
        if not item.get("prompt_card_hash")
    ]
    intermediate_completeness_failures = []
    registry_rejections = []
    unresolved_required_roles = []
    failed_required_turns_consumed_by_final = []
    for item in evidence_turns:
        role = item.get("role")
        if role == "final_synthesis_author":
            continue
        role_compliance_result = item.get("role_compliance") or {}
        completeness = role_compliance_result.get("intermediate_artifact_completeness") or {}
        registry_acceptance = item.get("registry_acceptance") or {}
        artifact_id = item.get("artifact_id")
        failed_role = role_compliance_result.get("status") != "pass"
        failed_state = (item.get("state_audit") or {}).get("status") != "pass"
        failed_completeness = completeness.get("status") != "pass"
        rejected = registry_acceptance.get("status") != "accepted"
        if failed_completeness:
            intermediate_completeness_failures.append({
                "turn": item.get("turn"),
                "role": role,
                "intermediate_artifact_completeness": completeness,
            })
        if rejected:
            registry_rejections.append({
                "turn": item.get("turn"),
                "role": role,
                "registry_acceptance": registry_acceptance,
            })
        if role in required_intermediate_roles() and rejected:
            unresolved_required_roles.append({
                "turn": item.get("turn"),
                "role": role,
                "artifact_id": artifact_id,
                "registry_acceptance": registry_acceptance,
            })
        if artifact_id in final_retrieved_ids and (failed_role or failed_state or failed_completeness or rejected):
            failed_required_turns_consumed_by_final.append({
                "turn": item.get("turn"),
                "role": role,
                "artifact_id": artifact_id,
                "role_status": role_compliance_result.get("status"),
                "intermediate_completeness_status": completeness.get("status"),
                "state_audit_status": (item.get("state_audit") or {}).get("status"),
                "registry_acceptance_status": registry_acceptance.get("status"),
            })

    final_completeness_failures = [
        {"turn": item.get("turn"), "final_artifact_completeness": (item.get("role_compliance") or {}).get("final_artifact_completeness")}
        for item in final_turns
        if ((item.get("role_compliance") or {}).get("final_artifact_completeness") or {}).get("status") == "fail"
    ]
    final_word_band_failures = [
        {"turn": item.get("turn"), "final_word_band_status": (item.get("role_compliance") or {}).get("final_word_band_status"), "final_word_count": (item.get("role_compliance") or {}).get("final_word_count")}
        for item in final_turns
        if (item.get("role_compliance") or {}).get("final_word_band_status") != "pass"
    ]
    final_repair_failures = [
        {"turn": item.get("turn"), "final_repair_attempts": item.get("final_repair_attempts")}
        for item in final_turns
        if item.get("final_repair_required") and not item.get("final_repair_succeeded")
    ]
    final_synthesis_blocked = any(bool(item.get("final_synthesis_blocked")) for item in evidence_turns)
    deterministic_gate_pass = precheck.get("deterministic_gate_status") == "pass"
    proof_eligible = (
        holo_mode == PROOF_ELIGIBLE_HOLO_MODE
        and deterministic_gate_pass
        and not role_failures
        and not state_failures
        and not prompt_hash_missing
        and not intermediate_completeness_failures
        and not registry_rejections
        and not unresolved_required_roles
        and not failed_required_turns_consumed_by_final
        and not final_completeness_failures
        and not final_word_band_failures
        and not final_repair_failures
        and not final_synthesis_blocked
    )
    return {
        "proof_credit_eligible": proof_eligible,
        "architecture_policy": architecture_policy_ref(),
        "deterministic_gate_pass": deterministic_gate_pass,
        "deterministic_gate_status": precheck.get("deterministic_gate_status"),
        "required_roles_all_completed": not unresolved_required_roles,
        "role_compliance_all_pass": not role_failures,
        "intermediate_completeness_all_pass": not intermediate_completeness_failures,
        "state_audit_all_pass": not state_failures,
        "registry_acceptance_all_pass": not registry_rejections,
        "no_failed_required_turn_consumed_by_final": not failed_required_turns_consumed_by_final,
        "prompt_card_hashes_present": not prompt_hash_missing,
        "final_artifact_completeness_pass": not final_completeness_failures,
        "final_word_band_pass": not final_word_band_failures,
        "final_repair_succeeded_if_used": not final_repair_failures,
        "final_synthesis_blocked": final_synthesis_blocked,
        "role_compliance_failures": role_failures,
        "intermediate_completeness_failures": intermediate_completeness_failures,
        "state_audit_failures": state_failures,
        "registry_rejections": registry_rejections,
        "unresolved_required_roles": unresolved_required_roles,
        "failed_required_turns_consumed_by_final": failed_required_turns_consumed_by_final,
        "prompt_hash_missing_turns": prompt_hash_missing,
        "final_artifact_completeness_failures": final_completeness_failures,
        "final_word_band_failures": final_word_band_failures,
        "final_repair_failures": final_repair_failures,
    }


def scan_judge_visible_text(text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for label, pattern in HARD_FORBIDDEN_JUDGE_VISIBLE_PATTERNS.items():
        if pattern.search(text):
            findings.append({"term_class": "hard_forbidden", "term": label})
    for label, pattern in CONTEXT_SENSITIVE_JUDGE_VISIBLE_PATTERNS.items():
        if pattern.search(text):
            findings.append({"term_class": "context_sensitive_process_metadata", "term": label})
    return findings


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def final_artifact_completeness(output_text: str, output_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    stripped = output_text.strip()
    failures: list[str] = []
    if not stripped:
        failures.append("empty_final_artifact")

    clean_ending = bool(FINAL_CLEAN_ENDING_RE.search(stripped))
    if not clean_ending:
        failures.append("unclean_or_mid_sentence_ending")

    section_presence = {
        name: bool(pattern.search(stripped))
        for name, pattern in FINAL_REQUIRED_SECTION_PATTERNS.items()
    }
    missing_sections = [name for name, present in section_presence.items() if not present]
    failures.extend(f"missing_final_section:{name}" for name in missing_sections)

    claim_boundary_tail_words = 0
    claim_boundary_match = FINAL_REQUIRED_SECTION_PATTERNS["claim_boundaries"].search(stripped)
    if claim_boundary_match:
        claim_boundary_tail = stripped[claim_boundary_match.end():]
        claim_boundary_tail_words = word_count(claim_boundary_tail)
        if claim_boundary_tail_words < 20:
            failures.append("claim_boundary_section_too_short_or_truncated")
        if not CLAIM_BOUNDARY_SUBSTANTIVE_RE.search(claim_boundary_tail):
            failures.append("claim_boundary_section_lacks_substantive_boundary_text")

    output_tokens = int((output_meta or {}).get("output_tokens") or 0)
    max_tokens_requested = int((output_meta or {}).get("max_tokens_requested") or 0)
    hit_requested_token_ceiling = bool(output_tokens and max_tokens_requested and output_tokens >= max_tokens_requested)
    if hit_requested_token_ceiling and not clean_ending:
        failures.append("provider_output_hit_max_tokens_with_unclean_ending")

    return {
        "status": "pass" if not failures else "fail",
        "clean_ending": clean_ending,
        "section_presence": section_presence,
        "missing_sections": missing_sections,
        "claim_boundary_tail_words": claim_boundary_tail_words,
        "output_tokens": output_tokens,
        "max_tokens_requested": max_tokens_requested,
        "hit_requested_token_ceiling": hit_requested_token_ceiling,
        "failures": failures,
    }


def intermediate_fragment_audit(stripped: str) -> dict[str, Any]:
    failures: list[str] = []
    lines = [line.rstrip() for line in stripped.splitlines() if line.strip()]
    last_line = lines[-1] if lines else ""
    clean_terminal_sentence = bool(FINAL_CLEAN_ENDING_RE.search(stripped))
    dangling_terminal = bool(stripped and UNCLEAN_INTERMEDIATE_ENDING_RE.search(stripped))
    if not clean_terminal_sentence or dangling_terminal:
        failures.append("unclean_or_mid_sentence_intermediate_ending")
    if stripped.count("```") % 2:
        failures.append("dangling_markdown_code_fence")
    last_line_for_emphasis = re.sub(r"^\s*[-*+]\s+", "", last_line.strip())
    unpaired_star_markers = re.findall(r"(?<!\\)(?<!\*)\*(?!\*)", last_line_for_emphasis)
    unpaired_underscore_markers = re.findall(r"(?<![\\\w_])_(?![\w_])", last_line_for_emphasis)
    if len(unpaired_star_markers) % 2 or len(unpaired_underscore_markers) % 2:
        failures.append("dangling_markdown_emphasis")
    if last_line.endswith("|") or re.search(r"^\s*\|.*\|\s*$", last_line) and not clean_terminal_sentence:
        failures.append("dangling_markdown_table_row")
    if re.search(r"^\s*(?:[-*+]|\d+\.)\s+\S{0,80}$", last_line) and not clean_terminal_sentence:
        failures.append("dangling_markdown_list_fragment")
    tail = stripped[-600:]
    if (
        re.search(r"[\[{]\s*(?:\"[^\"]*\"|[A-Za-z0-9_ -]+)?\s*$", tail)
        or re.search(r"[:,]\s*$", tail)
        or tail.count("{") > tail.count("}")
        or tail.count("[") > tail.count("]")
    ):
        failures.append("dangling_json_or_structured_fragment")
    return {
        "clean_terminal_sentence": clean_terminal_sentence,
        "dangling_terminal": dangling_terminal,
        "last_line": last_line,
        "failures": list(dict.fromkeys(failures)),
    }


def options_operational_analysis_presence(output_text: str) -> dict[str, Any]:
    lowered = output_text.lower()
    component_patterns = {
        "available_options": r"\b(option|path|alternative|approve|deny|block|hold|escalate|fallback|response)\b",
        "risk_of_acting": r"\b(risk of acting|acting risk|execution risk|risk if approved|risk if executed|if (?:we )?(?:act|approve|execute|proceed)|harm of acting|blast radius|downside of proceeding|cost of acting|consequence of acting)\b",
        "risk_of_waiting": r"\b(risk of waiting|waiting risk|delay risk|if (?:we )?(?:wait|defer|delay)|cost of waiting|deadline|manual workaround)\b",
        "sequencing_or_dependency_chain": r"\b(sequence|dependency|before|after|first|then|stage|canary|timeline|chain|prerequisite)\b",
        "stop_go_triggers": r"\b(stop/go triggers?|stop/go conditions?|halt trigger|go trigger|signal that stops execution|signal that permits expansion|proceed only if|expand only after|authorized only if|block execution if|do not proceed unless|no-go|trigger|threshold|condition|permit|gate|decision point)\b",
        "rollback_gates": r"\b(rollback|revert|revoke|undo|reversal|backout|kill switch)\b",
        "monitoring_or_logging_gates": r"\b(monitor|monitoring|log|logging|observable|observability|metric|alert|audit trail|signal)\b",
        "executive_next_actions": r"\b(next action|next step|owner|executive|approve|approval|escalate|commander|business owner|accountable)\b",
        "true_before_execution": r"\b(must be true before execution|prerequisites? before execution|preconditions? before execution|before execution|before approval|required before release|gate before execution|condition before execution|before (?:we )?(?:execute|approve|expand|proceed)|must be true|preconditions?|prerequisites?)\b",
        "signal_stops_execution": r"\b(signal that stops execution|signal stops execution|signal.*stop|stop.*signal|halt|kill switch|block execution|do not proceed|stop execution)\b",
        "signal_permits_expansion": r"\b(signal permits expansion|signal that permits expansion|expansion permitted only if|expansion allowed only if|go signal|go condition|proceed only if|expand only after|permit expansion when|allow expansion when|signal.*(?:expand|scale|continue)|permits expansion|expand only|scale only|continue only)\b",
        "reversible_action": r"\b(reversible|can be reversed|can reverse|rollback|revert|undo|revocable)\b",
        "irreversible_action": r"\b(irreversible action|cannot be reversed|not reversible|unrecoverable|sticky consequence|irreversible consequence|external reliance|irreversible exposure|permanent effect|cannot be undone|irreversible|cannot reverse|permanent|one-way)\b",
        "observable_before_rollback_trusted": r"\b(observable before rollback|before rollback.*observable|rollback.*(?:trusted|trust)|monitor.*rollback|logs?.*rollback)\b",
    }
    presence = {
        name: bool(re.search(pattern, lowered))
        for name, pattern in component_patterns.items()
    }
    missing = [name for name, present in presence.items() if not present]
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", output_text.strip()) if word_count(part) >= 8]
    operational_clause_hits = len(re.findall(r"\b(if|when|unless|until|before|after|trigger|threshold|gate|rollback|monitor|observable|owner|approve|escalate)\b", lowered))
    substantive = len(sentences) >= 6 and operational_clause_hits >= 8
    failures = [f"missing_options_role_component:{name}" for name in missing]
    if not substantive:
        failures.append("options_operational_analysis_too_thin_or_keyword_only")
    return {
        "status": "pass" if not failures else "fail",
        "component_presence": presence,
        "missing_components": missing,
        "substantive_sentence_count": len(sentences),
        "operational_clause_hits": operational_clause_hits,
        "failures": failures,
    }


def t3_concise_audit_presence(output_text: str) -> dict[str, Any]:
    lowered = re.sub(r"\s+", " ", output_text.lower())
    section_presence = {
        item: item.lower() in lowered
        for item in T3_CONCISE_AUDIT_SECTION_ITEMS
    }
    missing_sections = [item for item, present in section_presence.items() if not present]
    wc = word_count(output_text)
    bullet_or_numbered_lines = len(re.findall(r"(?m)^\s*(?:[-*]|\d+[.)])\s+\S", output_text))
    cited_source_ids = sorted(set(SOURCE_ID_RE.findall(output_text)))
    failures: list[str] = []
    failures.extend(f"missing_t3_compact_section:{item}" for item in missing_sections)
    if wc < T3_CONCISE_AUDIT_MIN_WORDS:
        failures.append("t3_compact_audit_under_target_words")
    if wc > T3_CONCISE_AUDIT_MAX_WORDS:
        failures.append("t3_compact_audit_over_target_words")
    if bullet_or_numbered_lines < 15:
        failures.append("t3_compact_audit_not_bulleted")
    if not cited_source_ids:
        failures.append("t3_compact_audit_missing_exact_source_ids")
    return {
        "status": "pass" if not failures else "fail",
        "section_presence": section_presence,
        "missing_sections": missing_sections,
        "word_count": wc,
        "target_min_words": T3_CONCISE_AUDIT_MIN_WORDS,
        "target_max_words": T3_CONCISE_AUDIT_MAX_WORDS,
        "bullet_or_numbered_lines": bullet_or_numbered_lines,
        "cited_source_ids": cited_source_ids,
        "failures": failures,
    }


def intermediate_artifact_completeness(role: str, output_text: str, output_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    stripped = output_text.strip()
    failures: list[str] = []
    wc = word_count(stripped)
    policy_role_words = intermediate_role_min_words()
    default_min_words = intermediate_default_min_words()
    min_words = max(default_min_words, policy_role_words.get(role, default_min_words))

    if not stripped:
        failures.append("empty_intermediate_artifact")
    if wc < min_words:
        failures.append("intermediate_artifact_too_short")

    fragment_audit = intermediate_fragment_audit(stripped)
    failures.extend(fragment_audit["failures"])

    output_tokens = int((output_meta or {}).get("output_tokens") or 0)
    max_tokens_requested = int((output_meta or {}).get("max_tokens_requested") or 0)
    hit_requested_token_ceiling = bool(output_tokens and max_tokens_requested and output_tokens >= max_tokens_requested)
    if hit_requested_token_ceiling and not fragment_audit["clean_terminal_sentence"]:
        failures.append("provider_output_hit_max_tokens_with_unclean_intermediate_ending")

    role_specific_presence: dict[str, Any] = {}
    if role == "options_operational_usefulness_reviewer":
        role_specific_presence = options_operational_analysis_presence(stripped)
        failures.extend(role_specific_presence["failures"])
    if role == "contradiction_uncertainty_source_fidelity_reviewer":
        role_specific_presence = t3_concise_audit_presence(stripped)
        failures.extend(role_specific_presence["failures"])

    return {
        "status": "pass" if not failures else "fail",
        "word_count": wc,
        "min_words_required": min_words,
        "clean_ending": fragment_audit["clean_terminal_sentence"] and not fragment_audit["failures"],
        "fragment_audit": fragment_audit,
        "output_tokens": output_tokens,
        "max_tokens_requested": max_tokens_requested,
        "hit_requested_token_ceiling": hit_requested_token_ceiling,
        "role_specific_presence": role_specific_presence,
        "failures": list(dict.fromkeys(failures)),
    }


def final_word_band_compliance(output_text: str) -> dict[str, Any]:
    policy = final_word_band_policy()
    minimum = policy["min_words"]
    maximum = policy["max_words"]
    wc = word_count(output_text)
    if wc < minimum:
        status = "fail_under_minimum"
    elif wc > maximum:
        status = "fail_over_hard_max"
    else:
        status = "pass"
    return {
        "status": status,
        "word_count": wc,
        "min_words_required": minimum,
        "max_words_allowed": maximum,
        "repair_target_words": policy["repair_target_words"],
        "over_max_words": max(0, wc - maximum),
        "under_min_words": max(0, minimum - wc),
        "threshold_source": repo_rel(ARCHITECTURE_POLICY_PATH),
        "policy_id": load_architecture_policy().get("policy_id"),
    }


def final_repair_prompt_kind(
    *,
    word_band_result: dict[str, Any],
    final_completeness_result: dict[str, Any],
) -> str:
    failures = list(final_completeness_result.get("failures") or [])
    if (
        word_band_result.get("status") == "pass"
        and final_completeness_result.get("status") == "fail"
        and failures == ["claim_boundary_section_lacks_substantive_boundary_text"]
    ):
        return FINAL_REPAIR_KIND_CLAIM_BOUNDARY_ONLY
    if final_completeness_result.get("status") == "pass" and word_band_result.get("status") == "fail_over_hard_max":
        return FINAL_REPAIR_KIND_COMPRESSION_ONLY
    return FINAL_REPAIR_KIND_MISSING_SECTION


def eligible_for_bounded_final_compression_repair(
    *,
    word_band_result: dict[str, Any],
    final_completeness_result: dict[str, Any],
    state_source_audit_result: dict[str, Any],
    other_final_blockers: list[str] | tuple[str, ...] | None = None,
) -> bool:
    return (
        word_band_result.get("status") == "fail_over_hard_max"
        and final_completeness_result.get("status") == "pass"
        and state_source_audit_result.get("status") == "pass"
        and state_source_audit_result.get("packet_hash_preserved") is True
        and not state_source_audit_result.get("invented_source_ids")
        and not (other_final_blockers or [])
    )


def registered_artifact_id(index: int, role: str, final: bool = False) -> str:
    return "FINAL_ARTIFACT" if final else f"TURN_{index:03d}_{role.upper()}"


def intermediate_registry_gate(
    *,
    artifact_id: str,
    role: str,
    role_compliance_result: dict[str, Any],
    state_audit_result: dict[str, Any],
    repair_attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    completeness = role_compliance_result.get("intermediate_artifact_completeness") or {}
    failures: list[str] = []
    if role_compliance_result.get("status") != "pass":
        failures.append("role_compliance_failed")
    if completeness.get("status") != "pass":
        failures.append("intermediate_completeness_failed")
    if state_audit_result.get("status") != "pass":
        failures.append("state_or_source_audit_failed")
    if not state_audit_result.get("packet_hash_preserved"):
        failures.append("packet_hash_not_preserved")
    if state_audit_result.get("invented_source_ids"):
        failures.append("invented_source_ids")
    repair_required = bool(repair_attempts) or bool(failures)
    repair_succeeded = bool(repair_attempts and repair_attempts[-1].get("accepted"))
    if repair_required and failures:
        failures.append("required_repair_not_validated")
    return {
        "artifact_id": artifact_id,
        "role": role,
        "status": "accepted" if not failures else "rejected",
        "repair_required": repair_required,
        "repair_succeeded": repair_succeeded,
        "role_compliance_status": role_compliance_result.get("status"),
        "intermediate_completeness_status": completeness.get("status"),
        "state_audit_status": state_audit_result.get("status"),
        "failures": list(dict.fromkeys(failures)),
    }


def excerpt(text: str, limit: int = 900) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def stable_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def load_suite_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "suite_manifest_missing", "path": str(path), "provider_calls": 0}, indent=2))
    return read_json(path)


def runner_domain_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries = list(manifest.get("domains", []))
    domain_ids = {entry.get("domain_id") for entry in entries}
    for extra_entry in (D11_RUNNER_DOMAIN_ENTRY, D12_RUNNER_DOMAIN_ENTRY):
        if extra_entry["domain_id"] not in domain_ids:
            entries.append(extra_entry)
    return entries


def suite_entries_by_packet(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for entry in runner_domain_entries(manifest):
        p = (REPO_ROOT / entry["packet_dir"]).resolve()
        out[str(p)] = entry
    return out


def resolve_packet_dir(args: argparse.Namespace, manifest: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    entries = runner_domain_entries(manifest)
    if args.domain:
        matches = [item for item in entries if item.get("domain_id") == args.domain]
        if not matches:
            valid = [item.get("domain_id") for item in entries]
            raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "unknown_domain", "domain": args.domain, "valid_domains": valid, "provider_calls": 0}, indent=2))
        entry = matches[0]
        packet_dir = (REPO_ROOT / entry["packet_dir"]).resolve()
    elif args.packet_dir:
        packet_dir = Path(args.packet_dir)
        if not packet_dir.is_absolute():
            packet_dir = REPO_ROOT / packet_dir
        packet_dir = packet_dir.resolve()
        by_packet = suite_entries_by_packet(manifest)
        entry = by_packet.get(str(packet_dir))
        if entry is None:
            raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "packet_dir_not_in_ten_domain_manifest", "packet_dir": str(packet_dir), "provider_calls": 0}, indent=2))
    else:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "packet_dir_or_domain_required", "provider_calls": 0}, indent=2))
    return packet_dir, entry


def validate_packet_against_manifest(packet_dir: Path, entry: dict[str, Any]) -> dict[str, Any]:
    required = [
        "task_brief.md",
        "source_packet.json",
        "source_packet.md",
        "source_manifest.json",
        "deterministic_gate_policy.json",
        "blind_packet_manifest.json",
        "contamination_scan_config.json",
        "packet_lock.json",
        "freeze_manifest.json",
        "validate_packet_no_provider.py",
    ]
    missing = [name for name in required if not (packet_dir / name).exists()]
    if missing:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "missing_packet_files", "missing": missing, "packet_dir": str(packet_dir), "provider_calls": 0}, indent=2))
    lock = read_json(packet_dir / "packet_lock.json")
    hash_errors: list[str] = []
    for rel, expected_hash in (lock.get("locked_files") or {}).items():
        candidate = packet_dir / rel
        if not candidate.exists():
            hash_errors.append(f"missing locked file: {rel}")
        elif sha_file(candidate) != expected_hash:
            hash_errors.append(f"locked file hash mismatch: {rel}")
    checks = {
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "packet_lock_hash": sha_file(packet_dir / "packet_lock.json"),
        "freeze_manifest_hash": sha_file(packet_dir / "freeze_manifest.json"),
    }
    for key, actual in checks.items():
        expected = entry.get(key)
        if expected and actual != expected:
            hash_errors.append(f"manifest {key} mismatch: expected {expected} actual {actual}")
    if hash_errors:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "packet_manifest_validation_failed", "errors": hash_errors, "provider_calls": 0}, indent=2))
    return {"lock": lock, "hashes": checks}


def load_configs() -> dict[str, dict[str, Any]]:
    configs: dict[str, dict[str, Any]] = {}
    for path in sorted(CONFIG_DIR.glob("*.json")):
        cfg = read_json(path)
        if "condition_type" not in cfg:
            continue
        configs[cfg["config_id"]] = cfg
        for alias in cfg.get("condition_aliases", []):
            configs[alias] = cfg
    return configs


def config_for_condition(condition: str, configs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if condition not in configs:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "unknown_condition_or_config", "condition": condition, "provider_calls": 0}, indent=2))
    return configs[condition]


def enforce_live_guard(live: bool) -> None:
    if not live:
        return
    if os.getenv(LIVE_APPROVAL_ENV) != "1":
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_LIVE_FAIL_CLOSED", "reason": f"live mode requires {LIVE_APPROVAL_ENV}=1 in addition to --live", "provider_calls": 0}, indent=2))


def enforce_holo_mode_guard(holo_mode: str, diagnostic_legacy_holo_mode: bool) -> None:
    if holo_mode in LEGACY_HOLO_MODES and not diagnostic_legacy_holo_mode:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED", "reason": "legacy_holo_mode_requires_explicit_diagnostic_flag", "holo_mode": holo_mode, "required_flag": "--diagnostic-legacy-holo-mode", "provider_calls": 0}, indent=2))


def provider_models_for_config(config: dict[str, Any], holo_mode: str) -> list[str]:
    if config.get("condition_type") == "solo":
        return [item["provider_model"] for item in config.get("model_pool", []) if item.get("provider_model")]
    if config.get("condition_type") == "holo":
        return unique_provider_models(holo_agent_models(config) + governor_model_pool(config))
    return []


def unique_provider_models(models: list[str]) -> list[str]:
    return list(dict.fromkeys(models))


def holo_agent_models(config: dict[str, Any]) -> list[str]:
    models = unique_provider_models([item["provider_model"] for item in config.get("model_pool", []) if item.get("provider_model")])
    expected_model_count = int(config.get("distinct_holo_agent_model_count") or 3)
    if len(models) != expected_model_count:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_config_requires_declared_distinct_holo_agent_models",
            "config_id": config.get("config_id"),
            "expected_models": expected_model_count,
            "actual_models": len(models),
            "provider_calls": 0,
        }, indent=2))
    return models


def governor_model_pool(config: dict[str, Any]) -> list[str]:
    return unique_provider_models(config.get("governor_model_pool") or holo_agent_models(config))


def session_template_lock_info(template_id: str) -> dict[str, Any] | None:
    lock_path_by_template = {
        "d3_success_v1": D3_SUCCESS_TEMPLATE_LOCK,
        "grok_swap_v1": GROK_SWAP_TEMPLATE_LOCK,
        "opus_gov_b_v1": OPUS_GOV_B_TEMPLATE_LOCK,
        "frontier_optimized_opus_gpt55_v1": FRONTIER_OPTIMIZED_OPUS_GPT55_TEMPLATE_LOCK,
    }
    lock_path = lock_path_by_template.get(template_id)
    if not lock_path:
        return None
    if not lock_path.exists():
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_session_template_lock_missing",
            "template_id": template_id,
            "expected_lock_path": repo_rel(lock_path),
            "provider_calls": 0,
        }, indent=2))
    lock = read_json(lock_path)
    if lock.get("template_id") != template_id:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_session_template_lock_id_mismatch",
            "template_id": template_id,
            "lock_template_id": lock.get("template_id"),
            "lock_path": repo_rel(lock_path),
            "provider_calls": 0,
        }, indent=2))
    return {
        "holo_session_template_lock_path": repo_rel(lock_path),
        "holo_session_template_lock_hash": sha_file(lock_path),
    }


def validate_fixed_holo_models(config: dict[str, Any], *, turn_models: tuple[str, ...], governor_model: str) -> None:
    agents = set(holo_agent_models(config))
    gov_pool = set(governor_model_pool(config))
    missing_agents = [model for model in turn_models if model not in agents]
    if missing_agents or governor_model not in gov_pool:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "fixed_holo_session_template_models_not_in_config_pool",
            "config_id": config.get("config_id"),
            "missing_turn_models": missing_agents,
            "governor_model": governor_model,
            "governor_model_in_pool": governor_model in gov_pool,
            "provider_calls": 0,
        }, indent=2))


def randomized_holo_session_plan(config: dict[str, Any], *, run_id: str, packet_hash: str, turn_count: int, session_template: str = "random") -> dict[str, Any]:
    fixed_templates = {
        "d3_success_v1": {
            "turn_models": D3_SUCCESS_HOLO_TURN_MODELS,
            "governor_model": D3_SUCCESS_GOV_MODEL,
            "selection_seed": "d3_success_v1_fixed_template",
            "selection_source": "fixed_successful_d3_holo_choreography",
            "agent_policy": "fixed_d3_success_v1_turn_order",
            "governor_policy": "fixed_d3_success_v1_governor",
            "final_policy": "fixed_d3_success_v1_final_writer",
        },
        "grok_swap_v1": {
            "turn_models": GROK_SWAP_HOLO_TURN_MODELS,
            "governor_model": GROK_SWAP_GOV_MODEL,
            "selection_seed": "grok_swap_v1_fixed_template",
            "selection_source": "fixed_d3_success_v1_choreography_with_openai_replaced_by_xai_grok_4_3",
            "agent_policy": "fixed_grok_swap_v1_turn_order",
            "governor_policy": "fixed_grok_swap_v1_governor",
            "final_policy": "fixed_grok_swap_v1_final_writer",
        },
        "opus_gov_b_v1": {
            "turn_models": GROK_SWAP_HOLO_TURN_MODELS,
            "governor_model": OPUS_GOV_B_GOV_MODEL,
            "selection_seed": "opus_gov_b_v1_fixed_template",
            "selection_source": "fixed_grok_swap_agent_choreography_with_anthropic_claude_opus_4_8_as_hologov_b",
            "agent_policy": "fixed_grok_swap_v1_turn_order",
            "governor_policy": "fixed_opus_4_8_hologov_b_governor",
            "final_policy": "fixed_grok_swap_v1_final_writer",
        },
        "frontier_optimized_opus_gpt55_v1": {
            "turn_models": FRONTIER_OPTIMIZED_OPUS_GPT55_HOLO_TURN_MODELS,
            "governor_model": FRONTIER_OPTIMIZED_OPUS_GPT55_GOV_MODEL,
            "selection_seed": "frontier_optimized_opus_gpt55_v1_fixed_template",
            "selection_source": "fixed_d10_frontier_optimized_opus_gpt55_choreography",
            "agent_policy": "fixed_frontier_optimized_opus_gpt55_v1_turn_order",
            "governor_policy": "fixed_opus_4_8_hologov_b_governor",
            "final_policy": "fixed_frontier_optimized_opus_gpt55_v1_final_writer",
        },
    }
    if session_template in fixed_templates:
        fixed = fixed_templates[session_template]
        turn_models = fixed["turn_models"]
        governor_model = fixed["governor_model"]
        if turn_count != len(turn_models):
            raise SystemExit(json.dumps({
                "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
                "reason": "fixed_holo_session_template_turn_count_mismatch",
                "template_id": session_template,
                "expected_turns": len(turn_models),
                "actual_turns": turn_count,
                "provider_calls": 0,
            }, indent=2))
        validate_fixed_holo_models(config, turn_models=turn_models, governor_model=governor_model)
        agents = holo_agent_models(config)
        gov_pool = governor_model_pool(config)
        lock_info = session_template_lock_info(session_template) or {}
        return {
            "selection_seed": fixed["selection_seed"],
            "selection_source": fixed["selection_source"],
            **lock_info,
            "run_id": run_id,
            "packet_hash": packet_hash,
            "cohort_name": config.get("cohort_name"),
            "config_id": config.get("config_id"),
            "hologov_profile": config.get("hologov_profile"),
            "holo_session_template": session_template,
            "holo_agent_pool": agents,
            "holo_agent_selection_policy": fixed["agent_policy"],
            "holo_agent_turn_models": list(turn_models),
            "hologov_model_pool": gov_pool,
            "hologov_selection_policy": fixed["governor_policy"],
            "hologov_tenure_policy": {
                "min_turns": HOLOGOV_C_TENURE_MIN,
                "max_turns": HOLOGOV_C_TENURE_MAX,
                "swap_policy": "disabled_for_fixed_template",
            },
            "hologov_schedule": [
                {
                    "start_turn": 1,
                    "end_turn": turn_count,
                    "selected_tenure_turns": 7,
                    "governor_model": governor_model,
                }
            ],
            "final_synthesis_model": turn_models[-1],
            "final_synthesis_model_policy": fixed["final_policy"],
            "final_compression_repair_model": preferred_final_compression_repair_model(config, turn_models[-1]),
            "final_compression_repair_model_policy": "configured_final_compression_repair_model_or_final_synthesis_model",
        }
    seed = secrets.token_hex(16)
    rng = random.Random(seed)
    agents = holo_agent_models(config)
    agent_rotation = agents[:]
    rng.shuffle(agent_rotation)
    turn_models = [agent_rotation[index % len(agent_rotation)] for index in range(turn_count)]
    final_synthesis_model = preferred_holo_final_model(config)
    if turn_models:
        turn_models[-1] = final_synthesis_model
    gov_pool = governor_model_pool(config)
    gov_segments: list[dict[str, Any]] = []
    start_turn = 1
    current_model: str | None = None
    while start_turn <= turn_count:
        candidates = [model for model in gov_pool if model != current_model] or gov_pool
        current_model = rng.choice(candidates)
        tenure = rng.randint(HOLOGOV_C_TENURE_MIN, HOLOGOV_C_TENURE_MAX)
        end_turn = min(turn_count, start_turn + tenure - 1)
        gov_segments.append({
            "start_turn": start_turn,
            "end_turn": end_turn,
            "selected_tenure_turns": tenure,
            "governor_model": current_model,
        })
        start_turn = end_turn + 1
    return {
        "selection_seed": seed,
        "selection_source": "python_secrets_token_hex_16",
        "run_id": run_id,
        "packet_hash": packet_hash,
        "cohort_name": config.get("cohort_name"),
        "config_id": config.get("config_id"),
        "hologov_profile": config.get("hologov_profile"),
        "holo_agent_pool": agents,
        "holo_agent_selection_policy": "random_permutation_of_three_agents_repeated_for_turn_budget",
        "holo_agent_turn_models": turn_models,
        "final_synthesis_model": final_synthesis_model,
        "final_synthesis_model_policy": "configured_or_openai_model_from_holo_agent_pool",
        "final_compression_repair_model": preferred_final_compression_repair_model(config, final_synthesis_model),
        "final_compression_repair_model_policy": "configured_final_compression_repair_model_or_final_synthesis_model",
        "hologov_model_pool": gov_pool,
        "hologov_selection_policy": "random_governor_from_hologov_model_pool",
        "hologov_tenure_policy": {
            "min_turns": HOLOGOV_C_TENURE_MIN,
            "max_turns": HOLOGOV_C_TENURE_MAX,
            "swap_policy": "after_tenure_select_random_different_model_from_pool_when_possible",
        },
        "hologov_schedule": gov_segments,
    }


def holo_turn_plan(session_plan: dict[str, Any]) -> list[tuple[str, str, str]]:
    models = session_plan.get("holo_agent_turn_models", [])
    if len(models) != len(HOLO_TURNS):
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "holo_session_plan_requires_one_model_per_turn",
            "expected_turns": len(HOLO_TURNS),
            "actual_models": len(models),
            "provider_calls": 0,
        }, indent=2))
    return [(role, models[index], objective) for index, (role, _default_model, objective) in enumerate(HOLO_TURNS)]


def preferred_holo_final_model(config: dict[str, Any]) -> str:
    models = holo_agent_models(config)
    configured = config.get("final_synthesis_model")
    if configured:
        if configured not in models:
            raise SystemExit(json.dumps({
                "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
                "reason": "final_synthesis_model_not_in_holo_agent_pool",
                "config_id": config.get("config_id"),
                "final_synthesis_model": configured,
                "holo_agent_pool": models,
                "provider_calls": 0,
            }, indent=2))
        return configured
    for model in models:
        if model.startswith("openai:"):
            return model
    return models[-1]


def preferred_final_compression_repair_model(config: dict[str, Any], final_synthesis_model: str) -> str:
    configured = config.get("final_compression_repair_model")
    if not configured:
        return final_synthesis_model
    models = holo_agent_models(config)
    if configured not in models:
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_FAIL_CLOSED",
            "reason": "final_compression_repair_model_not_in_holo_agent_pool",
            "config_id": config.get("config_id"),
            "final_compression_repair_model": configured,
            "holo_agent_pool": models,
            "provider_calls": 0,
        }, indent=2))
    return configured


def final_repair_model_for_kind(repair_kind: str, final_synthesis_model: str, session_plan: dict[str, Any]) -> str:
    if repair_kind == FINAL_REPAIR_KIND_COMPRESSION_ONLY:
        return session_plan.get("final_compression_repair_model") or final_synthesis_model
    return final_synthesis_model


def ensure_provider_env(models: list[str]) -> None:
    missing: dict[str, str] = {}
    for provider_model_name in models:
        provider, _model = provider_model(provider_model_name)
        env_name = PROVIDER_ENV.get(provider)
        if not env_name:
            missing[provider_model_name] = "unknown_provider"
        elif not os.getenv(env_name):
            missing[provider_model_name] = env_name
    if missing:
        raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_LIVE_FAIL_CLOSED", "reason": "missing_provider_environment", "missing": missing, "provider_calls": 0}, indent=2))


def source_ids(source_packet: dict[str, Any]) -> set[str]:
    return {src.get("source_id") for src in source_packet.get("sources", []) if src.get("source_id")}


def required_practical_response_options(source_packet: dict[str, Any]) -> list[str]:
    options = source_packet.get("practical_response_options_required")
    if isinstance(options, list):
        return [str(item) for item in options if str(item).strip()]
    return []


def build_final_repair_user(
    *,
    repair_kind: str,
    final_band: dict[str, int],
    previous_word_count: int,
    failed_final_word_band: dict[str, Any],
    final_quality_failures: list[str],
    final_completeness: dict[str, Any],
    final_state_source_audit: dict[str, Any],
    context_governor_instructions: str,
    state_json: str,
    gov_notes_json: str,
    baton_json: str,
    registry_json: str,
    retrieved: str,
    required_options_text: str,
    failed_output_text: str,
) -> str:
    if repair_kind == FINAL_REPAIR_KIND_COMPRESSION_ONLY:
        repair_header = "FINAL_ARTIFACT_COMPRESSION_REPAIR"
        repair_instructions = (
            "The current artifact is complete but too long. "
            "Do not add new analysis. Do not add new sections. "
            "Preserve all required sections: bottom line, risks of acting, risks of waiting, next steps, claim boundaries. "
            "Preserve exact source IDs. Preserve recommendation and action-boundary logic. "
            "Cut lower-priority wording. Merge repetitive sentences. Remove filler and duplicate explanation. "
            f"You must cut at least 180 words unless already below {final_band['max_words']}. "
            "The output must be at least 10 percent shorter than the input and no more than 1,250 words. "
            f"If the input is over {final_band['max_words']}, returning above {final_band['max_words']} is invalid. "
            "Prefer deleting explanatory repetition over preserving every sentence. "
            "Do not preserve paragraph count. Do not preserve section length. "
            "Compress tables/bullets aggressively. "
            "Keep exact source IDs, but remove redundant citations. "
            f"The hard {final_band['min_words']}-{final_band['max_words']:,} body-word band remains mandatory. "
            f"Target {final_band['repair_target_words']} words. Hard maximum {final_band['max_words']} words. "
            f"Returning over {final_band['max_words']} fails. "
            "Return only the compressed final artifact."
        )
    elif repair_kind == FINAL_REPAIR_KIND_MISSING_SECTION:
        repair_header = "FINAL_ARTIFACT_COMPLETENESS_REPAIR"
        repair_instructions = (
            "The final synthesis output failed final artifact quality checks. "
            f"Return only a corrected final decision-grade crisis/action brief, {final_band['min_words']}-{final_band['max_words']} body words, target {final_band['repair_target_words']}. "
            f"The {final_band['max_words']}-word maximum is hard for architecture compliance; do not return an overlength repair. "
            "Preserve or add the missing section identified by the audit, then compress elsewhere to stay within the hard word band. "
            f"Target approximately {final_band['repair_target_words']} words. "
            f"If adding a section, remove or compress lower-priority wording so the repair remains under {final_band['max_words']} words. "
            "Do not add commentary about this repair. Use only the frozen packet and registered artifacts below. "
            "Preserve the central thesis, decision recommendation, risk of acting, risk of waiting, trigger/gate table, calculations, counterargument, source IDs, and source-boundary disclaimer. "
            "The final answer must end cleanly with a complete sentence and a complete claim-boundary/disclaimer section."
        )
    elif repair_kind == FINAL_REPAIR_KIND_CLAIM_BOUNDARY_ONLY:
        repair_header = "FINAL_ARTIFACT_CLAIM_BOUNDARY_REPAIR"
        repair_instructions = (
            "The final synthesis output passed the word band but failed claim-boundary completeness. "
            "Repair only the claim-boundary failure. Return the full final artifact. "
            "Preserve the five required headings exactly: Bottom line; Risks of acting; Risks of waiting; Next steps / stop-go gates; Claim boundaries. "
            f"Target {FINAL_CLAIM_BOUNDARY_REPAIR_MIN_WORDS}-{FINAL_CLAIM_BOUNDARY_REPAIR_MAX_WORDS} words. "
            "No commentary. No appendix. No judge-facing explanation. "
            "Preserve exact source IDs. Do not invent source IDs. "
            "Do not continue prior truncated text. "
            "The Claim boundaries section must explicitly state what the brief does not conclude and what remains unsupported until gates pass. "
            "Must end with a complete standalone sentence. Hard stop before token ceiling."
        )
    else:
        raise ValueError(f"unknown final repair kind: {repair_kind}")

    return (
        f"{repair_header}\n"
        f"{'=' * len(repair_header)}\n"
        f"{repair_instructions}\n\n"
        f"{FINAL_SYNTHESIS_HEADING_TEMPLATE}\n\n"
        f"{FINAL_SYNTHESIS_CLAIM_BOUNDARY_CONTRACT}\n\n"
        f"{GENERATION_ARGUMENT_QUALITY_GUIDANCE}\n"
        f"{FINAL_SYNTHESIS_TRIGGER_TAXONOMY}\n"
        "Keep exact required practical response option labels if supplied, and retain the strongest counterargument handling.\n\n"
        f"FAILED_FINAL_WORD_COUNT: {previous_word_count}\n\n"
        f"FAILED_FINAL_WORD_BAND: {stable_json(failed_final_word_band)}\n\n"
        f"FINAL_QUALITY_FAILURES: {stable_json(final_quality_failures)}\n\n"
        f"FINAL_COMPLETENESS_AUDIT: {stable_json(final_completeness)}\n\n"
        f"FINAL_STATE_SOURCE_AUDIT: {stable_json(final_state_source_audit)}\n\n"
        "CONTEXT_GOVERNOR_INSTRUCTIONS\n=============================\n"
        f"{context_governor_instructions}\n\n"
        "CANONICAL STATE_OBJECT\n======================\n"
        f"{state_json}\n\nSTATE_OBJECT_SHA256: {sha_text(state_json)}\n\n"
        "GOV_NOTES\n=========\n"
        f"{gov_notes_json}\n\nGOV_NOTES_SHA256: {sha_text(gov_notes_json)}\n\n"
        "BATON_PASS\n==========\n"
        f"{baton_json}\n\nBATON_PASS_SHA256: {sha_text(baton_json)}\n\n"
        "ARTIFACTS_REGISTRY\n==================\n"
        f"{registry_json}\n\nARTIFACTS_REGISTRY_SHA256: {sha_text(registry_json)}\n\n"
        "RETRIEVED PINNED SOURCES AND ARTIFACTS\n======================================\n"
        f"{retrieved}\n\n"
        "REQUIRED PRACTICAL RESPONSE OPTION LABELS\n=========================================\n"
        f"{required_options_text}\n\n"
        "FAILED FINAL OUTPUT TO REPAIR\n=============================\n"
        f"{failed_output_text}\n"
    )


def load_packet_surfaces(packet_dir: Path) -> dict[str, Any]:
    return {
        "task_brief": (packet_dir / "task_brief.md").read_text(encoding="utf-8"),
        "source_packet_md": (packet_dir / "source_packet.md").read_text(encoding="utf-8"),
        "source_packet_json": read_json(packet_dir / "source_packet.json"),
        "deterministic_gate_policy": read_json(packet_dir / "deterministic_gate_policy.json"),
    }


def build_base_system() -> str:
    return (
        "You are producing a decision-grade crisis/action brief from a frozen benchmark packet. "
        "Use only the provided task brief and frozen source packet. Do not browse. Do not infer model identity. "
        "Separate facts from inference, preserve source boundaries, compare options, and include risks of acting and waiting. "
        "Final artifact body must be 900-1,300 words. "
        f"{EXACT_SOURCE_ID_GENERATION_INSTRUCTION} "
        f"{GENERATION_ARGUMENT_QUALITY_GUIDANCE}"
    )


def packet_context(task_brief: str, source_packet_md: str) -> str:
    return (
        "FROZEN TASK BRIEF\n"
        "=================\n"
        f"{task_brief}\n\n"
        "FROZEN SOURCE PACKET\n"
        "====================\n"
        f"{source_packet_md}\n"
    )


def call_model(provider_model_name: str, *, system: str, user: str, max_tokens: int, timeout: int) -> dict[str, Any]:
    global PROVIDER_CALLS, ACCEPTED_PROVIDER_CALLS, FAILED_PROVIDER_CALLS
    provider, model = provider_model(provider_model_name)
    PROVIDER_CALLS += 1
    try:
        out = call_provider(provider, system=system, user=user, max_tokens=max_tokens, timeout=timeout, model_override=model)
    except ProviderCallError:
        FAILED_PROVIDER_CALLS += 1
        raise
    ACCEPTED_PROVIDER_CALLS += 1
    out["provider_model"] = provider_model_name
    out["max_tokens_requested"] = max_tokens
    return out


def deterministic_gate_precheck(packet_dir: Path, artifact_text: str) -> dict[str, Any]:
    gate = read_json(packet_dir / "deterministic_gate_policy.json")
    word_gate = gate.get("layer_1_deterministic_gate", {}).get("artifact_body_word_count", {})
    minimum = int(word_gate.get("min", FINAL_WORD_MIN))
    maximum = int(word_gate.get("max", FINAL_WORD_MAX))
    count = word_count(artifact_text)
    overage_words = max(0, count - maximum)
    word_count_penalty_points = round(overage_words * 0.03, 4)
    if minimum <= count <= maximum:
        status = "pass"
        proof_eligible_if_failed = False
    elif maximum < count <= FINAL_WORD_PERSUASIVE_MAX:
        status = "pass_with_word_overage_penalty"
        proof_eligible_if_failed = True
    else:
        status = "fail"
        proof_eligible_if_failed = False
    return {
        "artifact_body_word_count": count,
        "word_count_gate": word_gate,
        "clean_word_count_max": maximum,
        "persuasive_word_count_max": FINAL_WORD_PERSUASIVE_MAX,
        "extreme_word_count_max": FINAL_WORD_EXTREME_MAX,
        "word_count_overage_words": overage_words,
        "word_count_penalty_points": word_count_penalty_points,
        "deterministic_gate_status": status,
        "proof_credit_eligible_if_failed": proof_eligible_if_failed,
        "word_count_policy_note": "Over clean max is scoring-penalized under v6.1 up to the persuasive ceiling; under minimum or above persuasive ceiling remains fail-closed.",
        "provider_calls": PROVIDER_CALLS,
    }


def run_dir_for(packet_dir: Path, run_id: str) -> Path:
    return packet_dir / "runs" / run_id


def condition_dir_for(packet_dir: Path, run_id: str, condition: str) -> Path:
    return run_dir_for(packet_dir, run_id) / condition


def generated_artifact_records(run_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not run_dir.exists():
        return records
    for metadata_path in sorted(run_dir.glob("*/artifact_metadata.json")):
        try:
            metadata = read_json(metadata_path)
        except (OSError, json.JSONDecodeError):
            metadata = {}
        artifact_path_value = metadata.get("artifact_path")
        artifact_path = REPO_ROOT / artifact_path_value if artifact_path_value else metadata_path.parent / "artifact.md"
        if not artifact_path.exists():
            continue
        records.append({
            "condition_dir": metadata_path.parent.name,
            "metadata_path": repo_rel(metadata_path),
            "artifact_path": repo_rel(artifact_path),
            "artifact_hash": sha_file(artifact_path),
            "condition": metadata.get("condition") or metadata_path.parent.name,
            "config_id": metadata.get("config_id"),
        })
    return records


def write_prompt_and_output(condition_dir: Path, turn_index: int, prompt_text: str, output: dict[str, Any]) -> dict[str, str]:
    prompt_path = condition_dir / "prompt_cards" / f"turn_{turn_index:03d}.md"
    output_path = condition_dir / "raw_outputs" / f"turn_{turn_index:03d}.json"
    write_text(prompt_path, prompt_text)
    write_json(output_path, output)
    return {"prompt_path": repo_rel(prompt_path), "prompt_hash": sha_file(prompt_path), "raw_output_path": repo_rel(output_path), "raw_output_hash": sha_file(output_path)}


def write_named_prompt_and_output(condition_dir: Path, name: str, prompt_text: str, output: dict[str, Any]) -> dict[str, str]:
    prompt_path = condition_dir / "prompt_cards" / f"{name}.md"
    output_path = condition_dir / "raw_outputs" / f"{name}.json"
    write_text(prompt_path, prompt_text)
    write_json(output_path, output)
    return {"prompt_path": repo_rel(prompt_path), "prompt_hash": sha_file(prompt_path), "raw_output_path": repo_rel(output_path), "raw_output_hash": sha_file(output_path)}


def run_solo(packet_dir: Path, run_id: str, config: dict[str, Any], timeout: int) -> dict[str, Any]:
    aliases = config.get("condition_aliases", [])
    if "solo_openai_gpt_5_5" in aliases:
        condition = "solo_openai_gpt_5_5"
    elif "solo_xai_grok_4_3" in aliases:
        condition = "solo_xai_grok_4_3"
    elif "solo_anthropic_claude_opus_4_8" in aliases:
        condition = "solo_anthropic_claude_opus_4_8"
    else:
        condition = config["config_id"]
    condition_dir = condition_dir_for(packet_dir, run_id, condition)
    surfaces = load_packet_surfaces(packet_dir)
    model = config["model_pool"][0]["provider_model"]
    prior = ""
    turn_records = []
    base = packet_context(surfaces["task_brief"], surfaces["source_packet_md"])
    for index, (role, objective) in enumerate(SOLO_TURNS, start=1):
        final_instruction = "Return only the final artifact." if index == len(SOLO_TURNS) else "Return a draft, critique, or revision notes for the next pass."
        user = f"{base}\n\nTURN ROLE: {role}\nTURN OBJECTIVE: {objective}\n{final_instruction}\n\nPRIOR DRAFT OR NOTES\n====================\n{prior or '[none]'}\n"
        prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{user}"
        out = call_model(model, system=build_base_system(), user=user, max_tokens=3600, timeout=timeout)
        io = write_prompt_and_output(condition_dir, index, prompt_text, out)
        prior = out["text"].strip()
        turn_records.append({"turn": index, "role": role, "model": model, "input_tokens": out.get("input_tokens"), "output_tokens": out.get("output_tokens"), **io})
    artifact_text = prior
    artifact_path = condition_dir / "artifact.md"
    write_text(artifact_path, artifact_text)
    precheck = deterministic_gate_precheck(packet_dir, artifact_text)
    write_json(condition_dir / "deterministic_gate_precheck.json", precheck)
    metadata = {
        "condition": condition,
        "config_id": config["config_id"],
        "cohort_name": config.get("cohort_name"),
        "condition_type": "solo",
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "artifact_path": repo_rel(artifact_path),
        "artifact_hash": sha_file(artifact_path),
        "turns": turn_records,
        "provider_calls": len(turn_records),
        "solo_call_structure": config.get("solo_call_structure"),
        "input_tokens": sum(int(item.get("input_tokens") or 0) for item in turn_records),
        "output_tokens": sum(int(item.get("output_tokens") or 0) for item in turn_records),
        "proof_credit_eligible": False,
        "baseline_eligible": True,
        "scores_generated": 0,
    }
    write_json(condition_dir / "artifact_metadata.json", metadata)
    return metadata


def role_compliance(role: str, output_text: str, final: bool, output_meta: dict[str, Any] | None = None) -> dict[str, Any]:
    lowered = output_text.lower()
    praise_only = len(re.findall(r"\b(strong|excellent|good|solid)\b", lowered)) >= 3 and not re.search(r"\b(missing|unsupported|risk|weak|contradict|uncertain|revise|option)\b", lowered)
    role_behaviors: dict[str, dict[str, str]] = {
        "initial_decision_brief_drafter": {
            "decision_frame": r"\b(recommend|decision|bottom line|do not|approve|deny|block|escalate|conditional)",
            "options": r"\b(option|path|alternative|fallback|response)",
            "source_grounding": r"\b(source|packet|case fact|frozen|evidence|supports|does not show|not provided)",
        },
        "assumption_and_evidence_attacker": {
            "assumption_attack": r"\b(assumption|assumes|overstate|not shown|does not show|not prove|inference|unsupported)",
            "weak_or_missing_support": r"\b(weak|missing|lacks|incomplete|not provided|no evidence|not establish|does not prove)",
            "revision_pressure": r"\b(final should|should not|tighten|revise|frame|avoid|must include)",
        },
        "contradiction_uncertainty_source_fidelity_reviewer": {
            "contradiction_or_tension": r"\b(contradict|conflict|tension|however|but|although)",
            "uncertainty": r"\b(uncertain|uncertainty|not shown|not provided|cannot conclude|does not prove|unknown)",
            "source_fidelity": r"\b(source|source id|packet|cited|frozen|stale|weak)",
        },
        "options_operational_usefulness_reviewer": {
            "available_options": r"\b(option|path|alternative|approve|deny|block|hold|escalate|fallback|response)",
            "risk_of_acting": r"\b(risk of acting|acting risk|execution risk|risk if approved|risk if executed|if (?:we )?(?:act|approve|execute|proceed)|harm of acting|blast radius|downside of proceeding|cost of acting|consequence of acting|harm|cost)",
            "risk_of_waiting": r"\b(risk of waiting|waiting risk|delay risk|if (?:we )?(?:wait|defer|delay)|cost of waiting)",
            "sequence_or_dependency": r"\b(sequence|dependency|before|after|first|then|stage|canary|timeline|chain|prerequisite)",
            "stop_go_or_rollback_gate": r"\b(stop|go|no-go|trigger|threshold|gate|rollback|revert|revoke|undo)",
            "monitoring_or_next_action": r"\b(monitor|logging|observable|alert|audit trail|next action|next step|owner|executive|approval)",
        },
        "claim_discipline_overclaim_reducer": {
            "overclaim_reduction": r"\b(overclaim|avoid|reduce|replace|bounded|tighten|soften|do not assert|should not imply)",
            "unsupported_or_not_proven": r"\b(unsupported|not shown|not provided|does not prove|no evidence|not establish|cannot conclude)",
            "claim_boundary": r"\b(claim|boundary|source-supported|packet supports|final language|recommended final)",
        },
        "final_synthesis_author": {
            "options": r"\b(option|trigger|go|no-go|hold|escalate|fallback|response)",
            "risk": r"\b(risk|exposure|failure|harm|waiting|acting)",
            "claim_boundary": r"\b(claim|boundary|does not prove|not shown|not provided|disclaimer|uncertainty)",
        },
    }
    expected_behaviors = role_behaviors.get(role, {})
    missing_terms = [name for name, pattern in expected_behaviors.items() if not re.search(pattern, lowered)]
    result = {
        "status": "pass" if not praise_only and not missing_terms else "fail",
        "praise_only": praise_only,
        "missing_role_behaviors": missing_terms,
    }
    if not final:
        completeness = intermediate_artifact_completeness(role, output_text, output_meta)
        result["intermediate_artifact_completeness"] = completeness
        if completeness["status"] != "pass":
            result["status"] = "fail"
    else:
        word_band = final_word_band_compliance(output_text)
        result["final_word_count"] = word_band["word_count"]
        result["final_word_band_status"] = word_band["status"]
        result["final_word_band_compliance"] = word_band
        if word_band["status"] != "pass":
            result["status"] = "fail"
        completeness = final_artifact_completeness(output_text, output_meta)
        result["final_artifact_completeness"] = completeness
        if completeness["status"] != "pass":
            result["status"] = "fail"
    return result


def state_audit(output_text: str, state: dict[str, Any], allowed_source_ids: set[str], packet_hash: str, registry: dict[str, Any]) -> dict[str, Any]:
    cited = set(SOURCE_ID_RE.findall(output_text))
    invented = sorted(cited - allowed_source_ids)
    checks = {
        "critical_constraints_present": bool(state.get("CRITICAL_CONSTRAINTS")),
        "packet_hash_preserved": state.get("PACKET_HASH") == packet_hash,
        "invented_source_ids": invented,
        "artifact_registry_present": bool(registry.get("artifacts")),
        "source_boundaries_preserved": "browse" not in output_text.lower(),
    }
    checks["status"] = "pass" if checks["critical_constraints_present"] and checks["packet_hash_preserved"] and not invented and checks["artifact_registry_present"] and checks["source_boundaries_preserved"] else "fail"
    return checks


def retrieved_content_for(ids: list[str], registry: dict[str, Any]) -> str:
    chunks = []
    for artifact_id in ids:
        item = registry.get("artifacts", {}).get(artifact_id)
        if not item:
            chunks.append(f"[MISSING REGISTRY ARTIFACT: {artifact_id}]")
            continue
        chunks.append(f"ARTIFACT_ID: {artifact_id}\nSTATUS: {item.get('status')}\nSHA256: {item.get('hash')}\nCONTENT:\n{item.get('content', '')}")
    return "\n\n---\n\n".join(chunks)


def registry_view_without_content(registry: dict[str, Any], *, statuses: set[str] | None = None) -> dict[str, dict[str, Any]]:
    view = {}
    for artifact_id, item in registry.get("artifacts", {}).items():
        if statuses is not None and item.get("status") not in statuses:
            continue
        view[artifact_id] = {key: value for key, value in item.items() if key != "content"}
    return view


def repair_attempt_public_status(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "attempt_count": len(attempts),
        "accepted": bool(attempts and attempts[-1].get("accepted")),
        "attempts": [
            {
                "attempt": item.get("attempt"),
                "role": item.get("role") or item.get("repaired_role"),
                "model": item.get("model"),
                "accepted": bool(item.get("accepted")),
            }
            for item in attempts
        ],
    }


def proof_credit_eligibility_state(unresolved_required_roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    reasons = ["unresolved_required_roles"] if unresolved_required_roles else []
    return {
        "eligible": not unresolved_required_roles,
        "reasons": reasons,
        "blocking_required_roles": sorted(unresolved_required_roles),
    }


def update_holobuild_state_surfaces(
    state: dict[str, Any],
    registry: dict[str, Any],
    *,
    rejected_artifact_ids: list[str],
    unresolved_required_roles: dict[str, dict[str, Any]],
    repair_attempt_status: dict[str, Any],
    final_synthesis_allowed_input_ids: list[str],
) -> None:
    accepted_statuses = {"PINNED", "INTERMEDIATE_ACCEPTED", "INTERMEDIATE_ACCEPTED_AFTER_REPAIR"}
    state["ARTIFACTS_REGISTRY"] = {"artifact_ids": list(registry.get("artifacts", {}).keys())}
    state["ACCEPTED_ARTIFACT_REGISTRY"] = registry_view_without_content(registry, statuses=accepted_statuses)
    state["REJECTED_ARTIFACT_IDS"] = sorted(set(rejected_artifact_ids))
    state["UNRESOLVED_REQUIRED_ROLES"] = sorted(unresolved_required_roles)
    state["REPAIR_ATTEMPT_STATUS"] = repair_attempt_status
    state["FINAL_SYNTHESIS_ALLOWED_INPUT_IDS"] = final_synthesis_allowed_input_ids
    state["PROOF_CREDIT_ELIGIBILITY_STATE"] = proof_credit_eligibility_state(unresolved_required_roles)


def build_context_governor_instructions(hologov_profile: str | None, context_profile: str) -> str:
    profile = hologov_profile or "HoloGov-C"
    return (
        f"CONTEXT GOVERNOR PROFILE: {profile}\n"
        f"HOLO CONTEXT PROFILE: {context_profile}\n"
        "Maintain the canonical STATE_OBJECT before and after each model turn. "
        "Preserve critical constraints, packet hash, source boundaries, settled decisions, unresolved tensions, and the Artifact Registry. "
        "Generate the BATON_PASS for the selected model and adversarial role. "
        "Require retrieve-by-ID behavior from the Artifact Registry before generation. "
        "After each output, audit role compliance, source-boundary preservation, invented source IDs, packet-hash preservation, and final word-band status when applicable. "
        "Do not decide from model fluency; preserve claim discipline and action-boundary uncertainty."
    )


def intermediate_role_repair_instructions(role: str) -> str:
    instructions = [INTERMEDIATE_REPAIR_CLEAN_ENDING_CONTRACT]
    if role == "assumption_and_evidence_attacker":
        instructions.append(ASSUMPTION_EVIDENCE_REPAIR_CHECKLIST)
    if role == "contradiction_uncertainty_source_fidelity_reviewer":
        instructions.append(T3_CONCISE_AUDIT_REPAIR_CONTRACT)
    if role == "options_operational_usefulness_reviewer":
        instructions.append(OPTIONS_OPERATIONAL_REPAIR_CHECKLIST)
    return "\n\n".join(instructions)


def intermediate_role_generation_instructions(role: str) -> str:
    if role == "contradiction_uncertainty_source_fidelity_reviewer":
        return T3_CONCISE_AUDIT_CONTRACT
    return ""


def build_intermediate_repair_user(
    *,
    role: str,
    objective: str,
    failed_role_compliance: dict[str, Any],
    failed_state_source_audit: dict[str, Any],
    context_governor_instructions: str,
    state_json: str,
    gov_notes_json: str,
    baton_json: str,
    registry_json: str,
    retrieved: str,
) -> str:
    return (
        "INTERMEDIATE_ROLE_ARTIFACT_REPAIR\n"
        "=================================\n"
        "The prior HoloBuild intermediate turn failed role-compliance or completeness checks. "
        "Return only a corrected role-specific intermediate artifact for the Artifact Registry. "
        "Do not write the final brief. Do not add commentary about this repair. "
        "The output must be substantive, preserve source boundaries, and perform the assigned adversarial role. "
        "The repair will be validated against the failed audit fields and the V4.2 role-specific validator; omission of a required component fails the repair.\n\n"
        f"ROLE: {role}\n"
        f"ROLE_OBJECTIVE: {objective}\n\n"
        "REPAIR_VALIDATION_INSTRUCTIONS\n"
        "==============================\n"
        f"{intermediate_role_repair_instructions(role)}\n\n"
        f"FAILED_ROLE_COMPLIANCE_AUDIT: {stable_json(failed_role_compliance)}\n\n"
        f"FAILED_STATE_SOURCE_AUDIT: {stable_json(failed_state_source_audit)}\n\n"
        "CONTEXT_GOVERNOR_INSTRUCTIONS\n=============================\n"
        f"{context_governor_instructions}\n\n"
        "CANONICAL STATE_OBJECT\n======================\n"
        f"{state_json}\n\nSTATE_OBJECT_SHA256: {sha_text(state_json)}\n\n"
        "GOV_NOTES\n=========\n"
        f"{gov_notes_json}\n\nGOV_NOTES_SHA256: {sha_text(gov_notes_json)}\n\n"
        "BATON_PASS\n==========\n"
        f"{baton_json}\n\nBATON_PASS_SHA256: {sha_text(baton_json)}\n\n"
        "ARTIFACTS_REGISTRY\n==================\n"
        f"{registry_json}\n\nARTIFACTS_REGISTRY_SHA256: {sha_text(registry_json)}\n\n"
        "RETRIEVED PINNED SOURCES AND ARTIFACTS\n======================================\n"
        f"{retrieved}\n\n"
        "FAILED INTERMEDIATE OUTPUT BODY\n===============================\n"
        "[withheld from repair prompt; preserved only in raw output and architecture evidence]\n"
    )


def gov_notes_for_turn(index: int, role: str, final: bool, retrieved_ids: list[str], state: dict[str, Any], registry: dict[str, Any], context_profile: str) -> list[str]:
    notes = [
        "Governor-controlled state is authoritative for this turn.",
        f"Turn {index} role is {role}; enforce the role-specific behavior rather than generic praise or summary.",
        f"Retrieved artifact IDs are Gov-selected from the Artifact Registry: {', '.join(retrieved_ids)}.",
        f"Holo context profile is {context_profile}; full_registry means all prior registered turn artifacts are retrieved, not only the latest note.",
        "Preserve the frozen packet source boundary; do not browse and do not invent approvals, clearances, or source IDs.",
        EXACT_SOURCE_ID_GENERATION_INSTRUCTION,
        "Keep risks of acting, risks of waiting, practical options, and claim boundaries visible.",
        GENERATION_ARGUMENT_QUALITY_GUIDANCE,
    ]
    required_options = state.get("REQUIRED_PRACTICAL_RESPONSE_OPTIONS") or []
    if required_options:
        notes.append("Packet required practical response options must be preserved as exact option labels, then explained in plain English.")
        notes.append("Required option labels: " + "; ".join(str(item) for item in required_options))
    if state.get("SETTLED_DECISIONS"):
        notes.append("Do not contradict settled decisions unless explicitly identifying a source-grounded reason to reopen them.")
    unresolved_roles = state.get("UNRESOLVED_REQUIRED_ROLES") or []
    if unresolved_roles:
        notes.append("Required intermediate roles remain unresolved; do not treat missing or rejected role artifacts as completed, and proof credit is blocked until repair validates.")
        notes.append("Unresolved required roles: " + ", ".join(str(item) for item in unresolved_roles))
    if final:
        word_band = final_word_band_policy()
        notes.append(f"Final synthesis architecture-compliance band is {word_band['min_words']}-{word_band['max_words']} body words, target {word_band['repair_target_words']}; do not exceed the hard maximum.")
        notes.append("HoloBuild proof credit requires the clean architecture band.")
        notes.append(FINAL_SYNTHESIS_HEADING_TEMPLATE)
        notes.append(FINAL_SYNTHESIS_CLAIM_BOUNDARY_CONTRACT)
        notes.append(FINAL_SYNTHESIS_TRIGGER_TAXONOMY)
        notes.append("Final synthesis must explicitly handle the strongest counterargument and explain why the recommended path is still better or conditional.")
    else:
        notes.append("This is an intermediate registered artifact; produce role-specific draft, critique, or constraints for the next turn.")
        role_instruction = intermediate_role_generation_instructions(role)
        if role_instruction:
            notes.append(role_instruction)
    notes.append(f"Registry currently contains {len(registry.get('artifacts', {}))} artifacts; all retrieved content must be traceable to registry IDs and hashes.")
    return notes


def retrieved_ids_for_holo_turn(registry: dict[str, Any], context_profile: str) -> list[str]:
    retrieved_ids = ["TASK_BRIEF", "SOURCE_PACKET_MD"]
    accepted_statuses = {"INTERMEDIATE_ACCEPTED", "INTERMEDIATE_ACCEPTED_AFTER_REPAIR", "PINNED"}
    prior_ids = [
        key for key, entry in registry["artifacts"].items()
        if key.startswith("TURN_") and entry.get("status") in accepted_statuses
    ]
    if not prior_ids:
        return retrieved_ids
    if context_profile == "latest_only":
        return retrieved_ids + [prior_ids[-1]]
    if context_profile == "full_registry":
        return retrieved_ids + prior_ids
    raise ValueError(f"unsupported Holo context profile: {context_profile}")


def run_holo(packet_dir: Path, run_id: str, config: dict[str, Any], timeout: int, holo_mode: str, holo_context_profile: str, holo_session_template: str) -> dict[str, Any]:
    condition = "holo_build_arch" if "holo_build_arch" in config.get("condition_aliases", []) else config["config_id"]
    condition_dir = condition_dir_for(packet_dir, run_id, condition)
    surfaces = load_packet_surfaces(packet_dir)
    packet_hash = sha_file(packet_dir / "source_packet.json")
    session_plan = randomized_holo_session_plan(config, run_id=run_id, packet_hash=packet_hash, turn_count=len(HOLO_TURNS), session_template=holo_session_template)
    turn_plan = holo_turn_plan(session_plan)
    allowed_ids = source_ids(surfaces["source_packet_json"])
    required_options = required_practical_response_options(surfaces["source_packet_json"])
    registry = {
        "artifacts": {
            "TASK_BRIEF": {"status": "PINNED", "hash": sha_text(surfaces["task_brief"]), "source_reference": repo_rel(packet_dir / "task_brief.md"), "content": surfaces["task_brief"]},
            "SOURCE_PACKET_MD": {"status": "PINNED", "hash": sha_text(surfaces["source_packet_md"]), "source_reference": repo_rel(packet_dir / "source_packet.md"), "content": surfaces["source_packet_md"]},
        }
    }
    context_governor_instructions = build_context_governor_instructions(config.get("hologov_profile"), holo_context_profile)
    final_band = final_word_band_policy()
    rejected_artifact_ids: list[str] = []
    repair_attempt_status: dict[str, Any] = {}
    unresolved_required_roles: dict[str, dict[str, Any]] = {}
    state = {
        "USER_GOAL": "Produce a decision-grade crisis/action brief from the frozen packet.",
        "LATEST_INPUT_SUMMARY": surfaces["source_packet_json"].get("decision_question") or surfaces["source_packet_json"].get("crisis_frame"),
        "CRITICAL_CONSTRAINTS": [
            "Use only the frozen task brief and source packet; no browsing.",
            f"Final artifact body must be {final_band['min_words']}-{final_band['max_words']} words, target {final_band['repair_target_words']}.",
            "Separate source facts from inference and preserve claim boundaries.",
            "No proof credit if deterministic gate fails.",
            "Full-architecture Holo context must retrieve pinned sources and registered prior artifacts by ID before every generation turn.",
            "Optimize the final artifact for source-grounded decision quality, including a sharp thesis, trigger taxonomy, counterargument handling, and high insight density.",
            "If the packet supplies required practical response options, preserve the exact option labels in the final artifact and explain them.",
        ],
        "PACKET_HASH": packet_hash,
        "SETTLED_DECISIONS": [],
        "REQUIRED_TOOLS": [],
        "REQUIRED_PRACTICAL_RESPONSE_OPTIONS": required_options,
        "BATON_PASS": {},
        "GOV_NOTES": [
            "Context Governor initialized the canonical state and pinned frozen task/source packet artifacts.",
            "Architecture evidence is internal only and must never be included in the final artifact.",
            "Argument power is a first-class quality target: the final artifact should be the strongest usable decision argument, not merely a safe source summary.",
        ],
    }
    update_holobuild_state_surfaces(
        state,
        registry,
        rejected_artifact_ids=rejected_artifact_ids,
        unresolved_required_roles=unresolved_required_roles,
        repair_attempt_status=repair_attempt_status,
        final_synthesis_allowed_input_ids=[],
    )
    evidence_turns = []
    turn_records = []
    final_repair_attempts: list[dict[str, Any]] = []
    intermediate_repair_attempts: list[dict[str, Any]] = []
    final_text = ""
    for index, (role, model, objective) in enumerate(turn_plan, start=1):
        final = index == len(turn_plan)
        retrieved_ids = retrieved_ids_for_holo_turn(registry, holo_context_profile)
        update_holobuild_state_surfaces(
            state,
            registry,
            rejected_artifact_ids=rejected_artifact_ids,
            unresolved_required_roles=unresolved_required_roles,
            repair_attempt_status=repair_attempt_status,
            final_synthesis_allowed_input_ids=retrieved_ids if final else [],
        )
        gov_notes = gov_notes_for_turn(index, role, final, retrieved_ids, state, registry, holo_context_profile)
        baton = {
            "next_model": model,
            "adversarial_role": role,
            "focus_area": objective,
            "unresolved_tensions": ["source support", "risks of acting", "risks of waiting", "claim boundaries"],
            "retrieved_artifact_ids": retrieved_ids,
            "required_output_behavior": "final artifact only" if final else "role-specific draft or critique for registry update",
            "holo_context_profile": holo_context_profile,
            "gov_notes": gov_notes,
        }
        state["BATON_PASS"] = baton
        state["GOV_NOTES"] = gov_notes
        state_json = stable_json(state)
        baton_json = stable_json(baton)
        registry_json = stable_json({k: {kk: vv for kk, vv in v.items() if kk != "content"} for k, v in registry["artifacts"].items()})
        gov_notes_json = stable_json(gov_notes)
        retrieved = retrieved_content_for(retrieved_ids, registry)
        required_options_text = "\n".join(f"- {option}" for option in required_options) if required_options else "[none supplied]"
        user = (
            "CONTEXT_GOVERNOR_INSTRUCTIONS\n=============================\n"
            f"{context_governor_instructions}\n\nCONTEXT_GOVERNOR_INSTRUCTIONS_SHA256: {sha_text(context_governor_instructions)}\n\n"
            "CANONICAL STATE_OBJECT\n======================\n"
            f"{state_json}\n\nSTATE_OBJECT_SHA256: {sha_text(state_json)}\n\n"
            "GOV_NOTES\n=========\n"
            f"{gov_notes_json}\n\nGOV_NOTES_SHA256: {sha_text(gov_notes_json)}\n\n"
            "BATON_PASS\n==========\n"
            f"{baton_json}\n\nBATON_PASS_SHA256: {sha_text(baton_json)}\n\n"
            "ARTIFACTS_REGISTRY\n==================\n"
            f"{registry_json}\n\nARTIFACTS_REGISTRY_SHA256: {sha_text(registry_json)}\n\n"
            "RETRIEVED PINNED SOURCES AND ARTIFACTS\n======================================\n"
            f"{retrieved}\n\n"
            "ADVERSARIAL ROLE INSTRUCTION\n============================\n"
            f"Role: {role}\nObjective: {objective}\n"
        )
        if not final:
            role_instruction = intermediate_role_generation_instructions(role)
            if role_instruction:
                user += f"\nROLE OUTPUT CONTRACT\n====================\n{role_instruction}\n"
        if final:
            user += (
                "\nFINAL SYNTHESIS QUALITY BAR\n===========================\n"
                f"Return only the final decision-grade crisis/action brief. Architecture-compliance body word band is {final_band['min_words']}-{final_band['max_words']}; target about {final_band['repair_target_words']}. "
                f"Do not exceed {final_band['max_words']} words. Preserve argument power through tighter synthesis, not overage.\n"
                f"{GENERATION_ARGUMENT_QUALITY_GUIDANCE}\n"
                f"{FINAL_SYNTHESIS_HEADING_TEMPLATE}\n"
                f"{FINAL_SYNTHESIS_CLAIM_BOUNDARY_CONTRACT}\n"
                f"{FINAL_SYNTHESIS_TRIGGER_TAXONOMY}\n"
                "Include the strongest counterargument or temptation for the opposite action, then explain why the recommended path is safer, stronger, or conditional.\n"
                f"{EXACT_SOURCE_ID_GENERATION_INSTRUCTION}\n"
                "Preserve claim boundaries, but do not let cautious wording make the brief generic or weak.\n"
                "If the packet supplies required practical response options, include the exact option labels below and then explain them:\n"
                f"{required_options_text}\n"
            )
        prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{user}"
        max_tokens = FINAL_SYNTHESIS_MAX_TOKENS if final else DEFAULT_TURN_MAX_TOKENS
        out = call_model(model, system=build_base_system(), user=user, max_tokens=max_tokens, timeout=timeout)
        io = write_prompt_and_output(condition_dir, index, prompt_text, out)
        output_text = out["text"].strip()
        artifact_source_io = io
        artifact_output_meta = out
        repair_turn_records: list[dict[str, Any]] = []
        turn_repair_attempts: list[dict[str, Any]] = []
        if final:
            initial_final_word_count = word_count(output_text)
            initial_completeness = final_artifact_completeness(output_text, out)
            initial_state_source_audit = state_audit(output_text, state, allowed_ids, packet_hash, registry)
            final_quality_failures = []
            initial_word_band = final_word_band_compliance(output_text)
            if initial_word_band["status"] != "pass":
                final_quality_failures.append("word_band_failure")
            final_quality_failures.extend(initial_completeness["failures"])
            if final_quality_failures:
                current_failed_text = output_text
                current_word_count = initial_final_word_count
                current_word_band = initial_word_band
                current_completeness = initial_completeness
                current_state_source_audit = initial_state_source_audit
                repair_attempt = 1
                extra_compression_attempts = 0
                while repair_attempt <= MAX_HOLO_FINAL_REPAIR_ATTEMPTS + extra_compression_attempts:
                    repair_kind = final_repair_prompt_kind(
                        word_band_result=current_word_band,
                        final_completeness_result=current_completeness,
                    )
                    repair_model = final_repair_model_for_kind(repair_kind, model, session_plan)
                    repair_user = build_final_repair_user(
                        repair_kind=repair_kind,
                        final_band=final_band,
                        previous_word_count=current_word_count,
                        failed_final_word_band=current_word_band,
                        final_quality_failures=final_quality_failures,
                        final_completeness=current_completeness,
                        final_state_source_audit=current_state_source_audit,
                        context_governor_instructions=context_governor_instructions,
                        state_json=state_json,
                        gov_notes_json=gov_notes_json,
                        baton_json=baton_json,
                        registry_json=registry_json,
                        retrieved=retrieved,
                        required_options_text=required_options_text,
                        failed_output_text=current_failed_text,
                    )
                    repair_prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{repair_user}"
                    repair_out = call_model(repair_model, system=build_base_system(), user=repair_user, max_tokens=FINAL_REPAIR_MAX_TOKENS, timeout=timeout)
                    repair_io = write_named_prompt_and_output(condition_dir, f"turn_{index:03d}_final_repair_{repair_attempt:03d}", repair_prompt_text, repair_out)
                    repaired_text = repair_out["text"].strip()
                    repaired_word_count = word_count(repaired_text)
                    repaired_completeness = final_artifact_completeness(repaired_text, repair_out)
                    repaired_word_band = final_word_band_compliance(repaired_text)
                    repaired_state_source_audit = state_audit(repaired_text, state, allowed_ids, packet_hash, registry)
                    repair_record = {
                        "attempt": repair_attempt,
                        "repair_kind": repair_kind,
                        "model": repair_model,
                        "final_synthesis_model": model,
                        "previous_word_count": current_word_count,
                        "previous_final_word_band_compliance": current_word_band,
                        "previous_final_completeness": current_completeness,
                        "previous_state_source_audit": current_state_source_audit,
                        "repaired_word_count": repaired_word_count,
                        "repaired_final_completeness": repaired_completeness,
                        "repaired_final_word_band_compliance": repaired_word_band,
                        "repaired_state_source_audit": repaired_state_source_audit,
                        "accepted": repaired_word_band["status"] == "pass" and repaired_completeness["status"] == "pass",
                        **repair_io,
                    }
                    turn_repair_attempts.append(repair_record)
                    final_repair_attempts.append(repair_record)
                    repair_turn_records.append({
                        "turn": f"{index}_final_repair_{repair_attempt}",
                        "role": "final_word_band_repair",
                        "model": repair_model,
                        "final_synthesis_model": model,
                        "input_tokens": repair_out.get("input_tokens"),
                        "output_tokens": repair_out.get("output_tokens"),
                        **repair_io,
                    })
                    if repair_record["accepted"]:
                        output_text = repaired_text
                        artifact_source_io = repair_io
                        artifact_output_meta = repair_out
                        break
                    if (
                        extra_compression_attempts < MAX_HOLO_FINAL_COMPRESSION_REPAIR_ATTEMPTS
                        and eligible_for_bounded_final_compression_repair(
                            word_band_result=repaired_word_band,
                            final_completeness_result=repaired_completeness,
                            state_source_audit_result=repaired_state_source_audit,
                            other_final_blockers=[],
                        )
                    ):
                        extra_compression_attempts += 1
                        current_failed_text = repaired_text
                        current_word_count = repaired_word_count
                        current_word_band = repaired_word_band
                        current_completeness = repaired_completeness
                        current_state_source_audit = repaired_state_source_audit
                        repair_attempt += 1
                        continue
                    repair_attempt += 1
        if not final:
            initial_intermediate_compliance = role_compliance(role, output_text, final=False, output_meta=out)
            initial_intermediate_state_audit = state_audit(output_text, state, allowed_ids, packet_hash, registry)
            if initial_intermediate_compliance["status"] != "pass" or initial_intermediate_state_audit["status"] != "pass":
                for repair_attempt in range(1, MAX_HOLO_INTERMEDIATE_REPAIR_ATTEMPTS + 1):
                    repair_user = build_intermediate_repair_user(
                        role=role,
                        objective=objective,
                        failed_role_compliance=initial_intermediate_compliance,
                        failed_state_source_audit=initial_intermediate_state_audit,
                        context_governor_instructions=context_governor_instructions,
                        state_json=state_json,
                        gov_notes_json=gov_notes_json,
                        baton_json=baton_json,
                        registry_json=registry_json,
                        retrieved=retrieved,
                    )
                    repair_prompt_text = f"SYSTEM:\n{build_base_system()}\n\nUSER:\n{repair_user}"
                    repair_out = call_model(model, system=build_base_system(), user=repair_user, max_tokens=INTERMEDIATE_REPAIR_MAX_TOKENS, timeout=timeout)
                    repair_io = write_named_prompt_and_output(condition_dir, f"turn_{index:03d}_intermediate_repair_{repair_attempt:03d}", repair_prompt_text, repair_out)
                    repaired_text = repair_out["text"].strip()
                    repaired_compliance = role_compliance(role, repaired_text, final=False, output_meta=repair_out)
                    repaired_state_audit = state_audit(repaired_text, state, allowed_ids, packet_hash, registry)
                    repair_record = {
                        "attempt": repair_attempt,
                        "model": model,
                        "role": role,
                        "previous_role_compliance": initial_intermediate_compliance,
                        "previous_state_audit": initial_intermediate_state_audit,
                        "repaired_role_compliance": repaired_compliance,
                        "repaired_state_audit": repaired_state_audit,
                        "accepted": repaired_compliance["status"] == "pass" and repaired_state_audit["status"] == "pass",
                        **repair_io,
                    }
                    turn_repair_attempts.append(repair_record)
                    intermediate_repair_attempts.append(repair_record)
                    repair_turn_records.append({
                        "turn": f"{index}_intermediate_repair_{repair_attempt}",
                        "role": "intermediate_role_repair",
                        "repaired_role": role,
                        "model": model,
                        "input_tokens": repair_out.get("input_tokens"),
                        "output_tokens": repair_out.get("output_tokens"),
                        **repair_io,
                    })
                    if repair_record["accepted"]:
                        output_text = repaired_text
                        artifact_source_io = repair_io
                        artifact_output_meta = repair_out
                        break
        artifact_id = registered_artifact_id(index, role, final)
        registry_acceptance: dict[str, Any]
        compliance = role_compliance(role, output_text, final, artifact_output_meta)
        if final:
            registry["artifacts"][artifact_id] = {
                "status": "PINNED",
                "hash": sha_text(output_text),
                "source_reference": artifact_source_io["raw_output_path"],
                "content": output_text,
            }
            audit = state_audit(output_text, state, allowed_ids, packet_hash, registry)
            registry_acceptance = {"artifact_id": artifact_id, "role": role, "status": "accepted", "final_artifact": True}
        else:
            audit = state_audit(output_text, state, allowed_ids, packet_hash, registry)
            registry_acceptance = intermediate_registry_gate(
                artifact_id=artifact_id,
                role=role,
                role_compliance_result=compliance,
                state_audit_result=audit,
                repair_attempts=turn_repair_attempts,
            )
            if registry_acceptance["status"] == "accepted":
                registry["artifacts"][artifact_id] = {
                    "status": "INTERMEDIATE_ACCEPTED_AFTER_REPAIR" if turn_repair_attempts else "INTERMEDIATE_ACCEPTED",
                    "hash": sha_text(output_text),
                    "source_reference": artifact_source_io["raw_output_path"],
                    "content": output_text,
                }
            elif role in required_intermediate_roles():
                unresolved_required_roles[role] = registry_acceptance
                state["UNRESOLVED_REQUIRED_ROLES"] = sorted(unresolved_required_roles)
                state["ARCHITECTURE_INVALID_REASONS"] = [item["status"] + ":" + item["role"] for item in unresolved_required_roles.values()]
        if turn_repair_attempts:
            repair_attempt_status[artifact_id] = repair_attempt_public_status(turn_repair_attempts)
        if registry_acceptance["status"] == "rejected":
            rejected_artifact_ids.append(artifact_id)
        update_holobuild_state_surfaces(
            state,
            registry,
            rejected_artifact_ids=rejected_artifact_ids,
            unresolved_required_roles=unresolved_required_roles,
            repair_attempt_status=repair_attempt_status,
            final_synthesis_allowed_input_ids=retrieved_ids if final else [],
        )
        if final:
            state["SETTLED_DECISIONS"].append("final_artifact_synthesized")
            final_text = output_text
        final_input_guard = {
            "status": "architecture_invalid_required_roles_unresolved" if final and unresolved_required_roles else "pass",
            "retrieved_registered_ids_only": True,
            "unresolved_required_roles": sorted(unresolved_required_roles),
            "blocked_rejected_artifact_ids": [
                item.get("artifact_id")
                for item in unresolved_required_roles.values()
                if item.get("artifact_id")
            ] if final and unresolved_required_roles else [],
        }
        evidence_turns.append({
            "turn": index,
            "role": role,
            "artifact_id": artifact_id,
            "model": model,
            "holo_context_profile": holo_context_profile,
            "context_governor_instructions_hash": sha_text(context_governor_instructions),
            "gov_notes_hash": sha_text(gov_notes_json),
            "state_object_hash": sha_text(state_json),
            "baton_pass_hash": sha_text(baton_json),
            "artifact_registry_hash": sha_text(registry_json),
            "prompt_card_hash": artifact_source_io["prompt_hash"],
            "initial_prompt_card_hash": io["prompt_hash"],
            "accepted_raw_output_hash": artifact_source_io["raw_output_hash"],
            "retrieved_artifact_ids": retrieved_ids,
            "retrieved_content_hash": sha_text(retrieved),
            "role_compliance": compliance,
            "state_audit": audit,
            "registry_acceptance": registry_acceptance,
            "intermediate_repair_attempts": [] if final else turn_repair_attempts,
            "final_repair_attempts": turn_repair_attempts if final else [],
            "final_repair_required": bool(final and turn_repair_attempts),
            "final_repair_succeeded": bool(final and turn_repair_attempts and turn_repair_attempts[-1].get("accepted")),
            "final_synthesis_input_guard": final_input_guard,
            "final_synthesis_blocked": final_input_guard["status"] != "pass",
        })
        turn_records.append({"turn": index, "role": role, "model": model, "input_tokens": out.get("input_tokens"), "output_tokens": out.get("output_tokens"), **io})
        turn_records.extend(repair_turn_records)
    artifact_path = condition_dir / "artifact.md"
    write_text(artifact_path, final_text)
    precheck = deterministic_gate_precheck(packet_dir, final_text)
    write_json(condition_dir / "deterministic_gate_precheck.json", precheck)
    arch_validation = architecture_evidence_summary(evidence_turns, precheck, holo_mode)
    arch_evidence = {
        "architecture_mode": holo_mode,
        "holo_context_profile": holo_context_profile,
        "architecture_evidence_visible_to_judges": False,
        "architecture_policy": architecture_policy_ref(),
        "context_governor_type": "internal_deterministic_state_management_layer",
        "context_governor_instructions_hash": sha_text(context_governor_instructions),
        "hologov_profile": config.get("hologov_profile"),
        "holo_session_plan": session_plan,
        "packet_hash": packet_hash,
        "turns": evidence_turns,
        "final_artifact_hash": sha_file(artifact_path),
        "architecture_evidence_validation": arch_validation,
        "proof_credit_architecture_status": "eligible_if_all_turn_audits_pass_and_deterministic_gate_passes" if arch_validation["proof_credit_eligible"] else "not_proof_eligible_due_failed_architecture_or_gate_check",
        "provider_calls": len(turn_records),
        "final_repair_attempts": final_repair_attempts,
        "intermediate_repair_attempts": intermediate_repair_attempts,
    }
    write_json(condition_dir / "arch_evidence.json", arch_evidence)
    metadata = {
        "condition": condition,
        "config_id": config["config_id"],
        "cohort_name": config.get("cohort_name"),
        "condition_type": "holo",
        "holo_mode": holo_mode,
        "holo_context_profile": holo_context_profile,
        "hologov_profile": config.get("hologov_profile"),
        "holo_session_plan": session_plan,
        "architecture_policy": architecture_policy_ref(),
        "holo_mode_status": "proof_eligible_if_evidence_validates" if holo_mode == PROOF_ELIGIBLE_HOLO_MODE else "diagnostic_only_no_proof_credit",
        "packet_hash": packet_hash,
        "artifact_path": repo_rel(artifact_path),
        "artifact_hash": sha_file(artifact_path),
        "arch_evidence_path": repo_rel(condition_dir / "arch_evidence.json"),
        "turns": turn_records,
        "provider_calls": len(turn_records),
        "repair_calls": len(final_repair_attempts) + len(intermediate_repair_attempts),
        "input_tokens": sum(int(item.get("input_tokens") or 0) for item in turn_records),
        "output_tokens": sum(int(item.get("output_tokens") or 0) for item in turn_records),
        "final_repair_attempts": final_repair_attempts,
        "intermediate_repair_attempts": intermediate_repair_attempts,
        "architecture_evidence_validation": arch_validation,
        "proof_credit_eligible": arch_validation["proof_credit_eligible"],
        "scores_generated": 0,
    }
    write_json(condition_dir / "artifact_metadata.json", metadata)
    return metadata


def condition_public_label(index: int) -> str:
    return f"ARTIFACT_{index:03d}"


def create_blind_export(packet_dir: Path, run_id: str, condition_results: list[dict[str, Any]]) -> dict[str, Any]:
    run_dir = run_dir_for(packet_dir, run_id)
    export_dir = run_dir / "blind_export"
    task_brief = (packet_dir / "task_brief.md").read_text(encoding="utf-8")
    source_packet = read_json(packet_dir / "source_packet.json")
    scoring_protocol = active_scoring_protocol()
    created = []
    internal_map = {}
    for idx, result in enumerate(condition_results, start=1):
        artifact_path = REPO_ROOT / result["artifact_path"]
        if not artifact_path.exists():
            continue
        label = condition_public_label(idx)
        packet = {
            "artifact_label": label,
            "artifact_text": artifact_path.read_text(encoding="utf-8"),
            "task_brief": task_brief,
            "source_packet": source_packet,
            "scoring_protocol": {
                "active_scoring_protocol_id": scoring_protocol.get("active_scoring_protocol_id"),
                "protocol_hash": scoring_protocol.get("protocol_hash"),
                "schema_hash": scoring_protocol.get("schema_hash"),
                "lock_hash": scoring_protocol.get("lock_hash"),
            },
        }
        packet_path = export_dir / f"{label}_blind_packet.json"
        write_json(packet_path, packet)
        created.append({"artifact_label": label, "path": repo_rel(packet_path), "artifact_hash": result.get("artifact_hash")})
        internal_map[label] = {"condition": result.get("condition"), "config_id": result.get("config_id"), "artifact_hash": result.get("artifact_hash")}
    result_artifact_paths = {str((REPO_ROOT / item["artifact_path"]).resolve()) for item in condition_results if item.get("artifact_path")}
    existing_records = generated_artifact_records(run_dir)
    missing_records = [
        item for item in existing_records
        if str((REPO_ROOT / item["artifact_path"]).resolve()) not in result_artifact_paths
    ]
    export_integrity = {
        "status": "PASS",
        "expected_condition_results": len(condition_results),
        "exported_packets": len(created),
        "internal_map_entries": len(internal_map),
        "existing_generated_artifacts": len(existing_records),
        "missing_existing_generated_artifacts": missing_records,
    }
    if len(created) != len(condition_results) or set(internal_map) != {item["artifact_label"] for item in created} or missing_records:
        export_integrity["status"] = "FAIL"
        export_integrity["reason"] = "blind_export_incomplete_or_run_id_reuse_detected"
        write_json(export_dir / "blind_export_integrity_failure.json", export_integrity)
        raise SystemExit(json.dumps({
            "status": "HOLOBUILD_MINI_SCOUT_BLIND_EXPORT_FAIL_CLOSED",
            "reason": export_integrity["reason"],
            "run_id": run_id,
            "provider_calls": PROVIDER_CALLS,
            "export_integrity": export_integrity,
        }, indent=2))
    map_path = export_dir / "anonymization_map.internal.json"
    write_json(map_path, internal_map)
    findings = []
    for item in created:
        text = (REPO_ROOT / item["path"]).read_text(encoding="utf-8")
        for finding in scan_judge_visible_text(text):
            findings.append({"path": item["path"], **finding})
    scan = {"status": "PASS" if not findings else "FAIL", "findings": findings}
    write_json(export_dir / "contamination_scan_result.json", scan)
    manifest = {
        "blind_export_id": f"{run_id}_blind_export",
        "created_utc": utc_iso(),
        "judge_visible_packets": created,
        "scoring_protocol": scoring_protocol,
        "internal_mapping_file": repo_rel(map_path),
        "mapping_is_internal_only": True,
        "architecture_evidence_judge_visible": False,
        "contamination_scan_result": scan,
        "blind_export_integrity": export_integrity,
        "provider_calls": 0,
    }
    write_json(export_dir / "blind_export_manifest.json", manifest)
    return {"blind_export_dir": repo_rel(export_dir), "manifest": manifest}


def run_dry(packet_dir: Path, run_id: str, conditions: list[str], configs: dict[str, dict[str, Any]], manifest_entry: dict[str, Any], holo_mode: str, holo_context_profile: str, holo_session_template: str) -> int:
    run_dir = run_dir_for(packet_dir, run_id)
    resolved = []
    for condition in conditions:
        cfg = config_for_condition(condition, configs)
        resolved_item = {
            "condition": condition,
            "config_id": cfg["config_id"],
            "cohort_name": cfg.get("cohort_name"),
            "condition_type": cfg.get("condition_type"),
            "hologov_profile": cfg.get("hologov_profile"),
            "hologov_model_pool": cfg.get("governor_model_pool"),
            "live_ready": cfg.get("live_ready"),
            "provider_call_budget": cfg.get("provider_call_budget"),
        }
        if cfg.get("condition_type") == "holo":
            resolved_item["holo_session_plan"] = randomized_holo_session_plan(
                cfg,
                run_id=run_id,
                packet_hash=str(manifest_entry.get("packet_hash")),
                turn_count=len(HOLO_TURNS),
                session_template=holo_session_template,
            )
            resolved_item["holo_context_profile"] = holo_context_profile
            resolved_item["holo_session_template"] = holo_session_template
        if cfg.get("condition_type") == "solo":
            resolved_item["solo_call_structure"] = cfg.get("solo_call_structure")
        resolved.append(resolved_item)
    payload = {
        "status": "HOLOBUILD_MINI_SCOUT_DRY_RUN_READY",
        "runner_id": "holobuild_generic_mini_scout_runner_v1",
        "run_id": run_id,
        "packet_dir": repo_rel(packet_dir),
        "domain_id": manifest_entry.get("domain_id"),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": resolved,
        "holo_mode": holo_mode if any(item["condition_type"] == "holo" for item in resolved) else None,
        "holo_context_profile": holo_context_profile if any(item["condition_type"] == "holo" for item in resolved) else None,
        "holo_session_template": holo_session_template if any(item["condition_type"] == "holo" for item in resolved) else None,
        "live_mode_fail_closed": True,
        "live_requires": ["--live", f"{LIVE_APPROVAL_ENV}=1"],
        "provider_calls": 0,
        "live_artifacts_generated": 0,
        "scores_generated": 0,
        "judging_runs": 0,
        "unblinding_runs": 0,
    }
    write_json(run_dir / "generic_runner_dry_run_manifest.json", payload)
    print(json.dumps(payload, indent=2))
    return 0


def run_live(packet_dir: Path, run_id: str, conditions: list[str], configs: dict[str, dict[str, Any]], timeout: int, holo_mode: str, holo_context_profile: str, holo_session_template: str) -> int:
    enforce_live_guard(True)
    run_dir = run_dir_for(packet_dir, run_id)
    existing_records = generated_artifact_records(run_dir)
    if existing_records:
        failure = {
            "status": "HOLOBUILD_MINI_SCOUT_LIVE_FAIL_CLOSED",
            "reason": "run_id_already_contains_generated_artifacts",
            "run_id": run_id,
            "existing_generated_artifacts": existing_records,
            "provider_calls": 0,
            "repair_guidance": "Use a fresh run_id. Historical multi-condition repairs should be recorded as addenda, not by overwriting the original run folder.",
        }
        write_json(run_dir / "run_id_reuse_failure.json", failure)
        print(json.dumps(failure, indent=2))
        return 1
    condition_results = []
    selected_models = []
    for condition in conditions:
        cfg = config_for_condition(condition, configs)
        if not cfg.get("live_ready"):
            raise SystemExit(json.dumps({"status": "HOLOBUILD_MINI_SCOUT_LIVE_FAIL_CLOSED", "reason": "config_not_live_ready", "condition": condition, "config_id": cfg.get("config_id"), "provider_calls": 0}, indent=2))
        selected_models.extend(provider_models_for_config(cfg, holo_mode))
    ensure_provider_env(selected_models)
    try:
        for condition in conditions:
            cfg = config_for_condition(condition, configs)
            if cfg["condition_type"] == "solo":
                condition_results.append(run_solo(packet_dir, run_id, cfg, timeout))
            elif cfg["condition_type"] == "holo":
                condition_results.append(run_holo(packet_dir, run_id, cfg, timeout, holo_mode, holo_context_profile, holo_session_template))
            else:
                raise RuntimeError(f"unsupported condition_type: {cfg['condition_type']}")
    except ProviderCallError as exc:
        failure = {
            "status": "HOLOBUILD_MINI_SCOUT_PROVIDER_ERROR",
            "provider": exc.provider,
            "error_type": exc.error_type,
            "http_status": exc.http_status,
            "message": str(exc),
            "provider_calls": PROVIDER_CALLS,
            "accepted_provider_calls": ACCEPTED_PROVIDER_CALLS,
            "failed_provider_calls": FAILED_PROVIDER_CALLS,
            "scores_generated": SCORES_GENERATED,
        }
        write_json(run_dir_for(packet_dir, run_id) / "run_failure.json", failure)
        print(json.dumps(failure, indent=2))
        return 1
    blind_export = create_blind_export(packet_dir, run_id, condition_results)
    run_manifest = {
        "status": "HOLOBUILD_MINI_SCOUT_LIVE_GENERATION_COMPLETE",
        "runner_id": "holobuild_generic_mini_scout_runner_v1",
        "run_id": run_id,
        "packet_dir": repo_rel(packet_dir),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": condition_results,
        "provider_calls": PROVIDER_CALLS,
        "accepted_provider_calls": ACCEPTED_PROVIDER_CALLS,
        "failed_provider_calls": FAILED_PROVIDER_CALLS,
        "scores_generated": SCORES_GENERATED,
        "judging_runs": 0,
        "unblinding_runs": 0,
        "blind_export": blind_export,
        "live_mode_fail_closed": True,
        "live_requires": ["--live", f"{LIVE_APPROVAL_ENV}=1"],
        "holo_context_profile": holo_context_profile if any(result.get("condition_type") == "holo" for result in condition_results) else None,
        "holo_session_template": holo_session_template if any(result.get("condition_type") == "holo" for result in condition_results) else None,
    }
    write_json(run_dir_for(packet_dir, run_id) / "run_manifest.json", run_manifest)
    print(json.dumps(run_manifest, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Generic HoloBuild mini-scout runner for frozen D1-D12 packets.")
    parser.add_argument("--suite-manifest", default=str(DEFAULT_SUITE_MANIFEST))
    parser.add_argument("--domain", choices=[f"D{i}" for i in range(1, 13)])
    parser.add_argument("--packet-dir")
    parser.add_argument("--condition", action="append", choices=VALID_CONDITIONS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--holo-mode", choices=HOLO_MODES, default=PROOF_ELIGIBLE_HOLO_MODE)
    parser.add_argument("--holo-context-profile", choices=HOLO_CONTEXT_PROFILES, default=DEFAULT_HOLO_CONTEXT_PROFILE)
    parser.add_argument("--holo-session-template", choices=HOLO_SESSION_TEMPLATES, default="random")
    parser.add_argument("--diagnostic-legacy-holo-mode", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="No-provider smoke/dry run. Default when --live is absent.")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    enforce_holo_mode_guard(args.holo_mode, args.diagnostic_legacy_holo_mode)
    manifest = load_suite_manifest(Path(args.suite_manifest))
    packet_dir, entry = resolve_packet_dir(args, manifest)
    validate_packet_against_manifest(packet_dir, entry)
    configs = load_configs()
    conditions = list(dict.fromkeys(args.condition))
    if args.live:
        return run_live(packet_dir, args.run_id, conditions, configs, args.timeout, args.holo_mode, args.holo_context_profile, args.holo_session_template)
    return run_dry(packet_dir, args.run_id, conditions, configs, entry, args.holo_mode, args.holo_context_profile, args.holo_session_template)


if __name__ == "__main__":
    raise SystemExit(main())
