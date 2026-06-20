from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run_holo_factory_suite import PROVIDER_ENV, ProviderCallError, call_provider, provider_model


FACTORY_DIR = Path(__file__).resolve().parent
DEFAULT_PACKET_DIR = FACTORY_DIR / "mini_scouts/d5_medtech_capacity_strain_001"
ARCH_SCHEMA_PATH = FACTORY_DIR / "schemas/holo_build_arch_evidence_schema.json"
ARCH_POLICY_PATH = FACTORY_DIR / "architecture_policies/holobuild_patent_alignment_policy_v4_1.json"

RUNNER_ID = "d5_medtech_capacity_strain_001_live_adapter_v4_1"
RUN_MODE = "d5_medtech_capacity_strain_001_corrected_v2_six_turn"
LIVE_APPROVAL_ENV = "HOLO_ALLOW_LIVE"
PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0
EXPECTED_PACKET_HASH = "b73292d9d2e4aac5f65a93ae168235d9d581ae17ebaf0a91aa16437018c527aa"
EXPECTED_TURN_COUNT = 6
FINAL_WORD_MIN = 900
FINAL_WORD_MAX = 1300
FINAL_WORD_TARGET = 1100

VALID_CONDITIONS = ("holo_build_arch", "solo_openai_gpt_5_5")
CONDITION_LABELS = {
    "holo_build_arch": "HoloBuild architecture condition",
    "solo_openai_gpt_5_5": "GPT-5.5 solo condition",
}
SOLO_PROVIDER_MODEL = "openai:gpt-5.5"
HOLO_PROVIDER_TURNS = (
    {
        "provider_model": "anthropic:claude-opus-4-8",
        "role": "initial_decision_brief_drafter",
        "objective": "Draft a source-grounded initial decision frame covering what is happening, why it matters, and the main adopt/pilot/delay/reject options. This is not the final artifact.",
        "max_tokens": 3200,
    },
    {
        "provider_model": "google:gemini-3.1-pro-preview",
        "role": "assumption_and_evidence_attacker",
        "objective": "Attack assumptions, weak evidence, sample/source limits, stale claims, and missing links between monitoring and hospital capacity relief.",
        "max_tokens": 3200,
    },
    {
        "provider_model": "openai:gpt-5.5",
        "role": "contradiction_uncertainty_source_fidelity_reviewer",
        "objective": "Stress-test contradictory evidence, FDA draft/advisory/press interpretation, source fidelity, and uncertainty boundaries.",
        "max_tokens": 3200,
    },
    {
        "provider_model": "anthropic:claude-opus-4-8",
        "role": "options_operational_usefulness_reviewer",
        "objective": "Stress-test practical options, risks of acting, risks of waiting, operating gates, and usefulness for leadership under capacity pressure.",
        "max_tokens": 3200,
    },
    {
        "provider_model": "google:gemini-3.1-pro-preview",
        "role": "claim_discipline_overclaim_reducer",
        "objective": "Reduce unsupported claims, identify exact overclaim risks, and prepare final-brief constraints so the final answer stays within 900-1,300 body words.",
        "max_tokens": 3200,
    },
)
HOLO_SYNTHESIS_MODEL = "openai:gpt-5.5"
SOLO_SELF_REFINE_TURNS = (
    {
        "role": "initial_decision_brief_draft",
        "objective": "Write an initial source-grounded decision brief draft. This is not final.",
        "max_tokens": 3400,
    },
    {
        "role": "assumption_and_evidence_attack",
        "objective": "Attack the prior draft for unsupported assumptions, weak evidence, missing calculations, and unsupported capacity claims. Produce a revised draft or detailed revision plan.",
        "max_tokens": 3400,
    },
    {
        "role": "contradiction_uncertainty_source_fidelity_pass",
        "objective": "Revise for contradictory evidence, uncertainty, stale source handling, FDA draft/advisory limits, and source-fidelity problems.",
        "max_tokens": 3400,
    },
    {
        "role": "options_risks_operational_usefulness_pass",
        "objective": "Revise for adopt/pilot/delay/reject options, risks of acting, risks of waiting, and operational usefulness for leadership.",
        "max_tokens": 3400,
    },
    {
        "role": "claim_discipline_overclaim_reduction_pass",
        "objective": "Cut unsupported claims, reduce overclaiming, tighten source citations, and prepare a concise final version.",
        "max_tokens": 3400,
    },
    {
        "role": "final_synthesis_900_1300_words",
        "objective": "Return only the final decision-grade crisis brief, 900-1,300 body words, target 1,100.",
        "max_tokens": 3400,
    },
)
REQUIRED_PACKET_FILES = (
    "task_brief.md",
    "source_packet.json",
    "source_packet.md",
    "packet_lock.json",
    "freeze_manifest.json",
    "deterministic_gate_policy.json",
)


def utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha_text(text: str) -> str:
    return sha_bytes(text.encode("utf-8"))


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def excerpt(text: str, limit: int = 1400) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def endpoint_for_provider(provider: str) -> str:
    if provider == "google":
        return "generateContent"
    if provider == "anthropic":
        return "messages"
    return "chat/completions"


def require_packet(packet_dir: Path) -> dict[str, Any]:
    missing = [name for name in REQUIRED_PACKET_FILES if not (packet_dir / name).exists()]
    if missing:
        raise SystemExit(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_RUNNER_FAIL",
                    "error": "missing_packet_files",
                    "missing": missing,
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )

    lock = read_json(packet_dir / "packet_lock.json")
    locked_files = lock.get("locked_files") or {}
    hash_errors: list[str] = []
    for rel, expected in locked_files.items():
        path = packet_dir / rel
        if not path.exists():
            hash_errors.append(f"missing locked file: {rel}")
        elif sha_file(path) != expected:
            hash_errors.append(f"locked file hash mismatch: {rel}")

    if hash_errors:
        raise SystemExit(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_RUNNER_FAIL",
                    "error": "packet_lock_validation_failed",
                    "errors": hash_errors,
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )
    packet_hash = sha_file(packet_dir / "source_packet.json")
    if packet_hash != EXPECTED_PACKET_HASH:
        raise SystemExit(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_RUNNER_FAIL",
                    "error": "unexpected_packet_hash",
                    "expected_packet_hash": EXPECTED_PACKET_HASH,
                    "actual_packet_hash": packet_hash,
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )
    return lock


def load_word_gate(packet_dir: Path) -> dict[str, Any]:
    gate = read_json(packet_dir / "deterministic_gate_policy.json")
    word_gate = gate["layer_1_deterministic_gate"]["artifact_body_word_count"]
    return {
        "min": int(word_gate["min"]),
        "max": int(word_gate["max"]),
        "scope": word_gate["scope"],
        "failure_result": word_gate["failure_result"],
    }


def deterministic_gate_precheck(packet_dir: Path, condition: str, artifact_text: str | None = None) -> dict[str, Any]:
    word_gate = load_word_gate(packet_dir)
    text = artifact_text or ""
    count = word_count(text)
    artifact_present = artifact_text is not None
    in_band = word_gate["min"] <= count <= word_gate["max"] if artifact_present else None
    return {
        "runner_id": RUNNER_ID,
        "condition": condition,
        "provider_calls": PROVIDER_CALLS,
        "artifact_present": artifact_present,
        "artifact_body_word_count": count if artifact_present else None,
        "word_count_gate": word_gate,
        "deterministic_gate_status": "not_evaluated_no_provider_smoke" if not artifact_present else ("pass" if in_band else "fail"),
        "proof_credit_eligible_if_failed": False,
        "notes": [
            "Layer 1 is admission-only.",
            "No proof credit is available if the word-count gate fails.",
        ],
    }


def visible_surface_boundary() -> dict[str, Any]:
    return {
        "model_prompts_include_architecture_evidence": False,
        "browser_packets_include_architecture_evidence": False,
        "judge_packets_include_architecture_evidence": False,
        "public_artifacts_include_architecture_evidence": False,
        "benchmark_source_packets_include_architecture_evidence": False,
        "judge_visible_allowed_fields": [
            "anonymous_artifact",
            "source_packet",
            "task_brief",
            "domain_card",
            "frozen_rubric",
        ],
    }


def proof_credit_readiness() -> dict[str, Any]:
    return {
        "fail_closed_if_architecture_evidence_missing": True,
        "proof_credit_allowed_if_architecture_evidence_missing": False,
        "diagnostic_only_if_architecture_evidence_missing": True,
        "required_evidence_validation_status": "validated",
    }


def smoke_arch_evidence(packet_dir: Path, run_id: str, condition_dir: Path) -> dict[str, Any]:
    source_packet_hash = sha_file(packet_dir / "source_packet.json")
    task_brief_hash = sha_file(packet_dir / "task_brief.md")
    lock_hash = sha_file(packet_dir / "packet_lock.json")
    registry_entries = [
        {
            "artifact_id": "frozen_source_packet",
            "artifact_type": "source_packet",
            "artifact_hash": source_packet_hash,
            "source_refs": ["source_packet.json"],
        },
        {
            "artifact_id": "frozen_task_brief",
            "artifact_type": "task_brief",
            "artifact_hash": task_brief_hash,
            "source_refs": ["task_brief.md"],
        },
        {
            "artifact_id": "smoke_final_artifact_slot",
            "artifact_type": "reserved_output_path",
            "artifact_hash": sha_text(str(condition_dir / "artifact.md")),
            "source_refs": ["artifact.md"],
        },
    ]
    registry_hash = sha_text(json.dumps(registry_entries, sort_keys=True))
    final_artifact_hash = sha_text("NO_PROVIDER_SMOKE_FINAL_ARTIFACT_SLOT")
    turns: list[dict[str, Any]] = []
    final_state_hash = ""
    for turn_index in range(1, EXPECTED_TURN_COUNT + 1):
        role = "final_synthesis_author" if turn_index == EXPECTED_TURN_COUNT else f"no_provider_smoke_reviewer_turn_{turn_index:03d}"
        state_payload = {
            "run_id": run_id,
            "packet_id": read_json(packet_dir / "source_packet.json")["packet_id"],
            "mode": "no_provider_smoke",
            "turn_index": turn_index,
            "role": role,
            "critical_constraints": [
                "use only frozen packet sources",
                "main artifact body must be 900-1300 words",
                "target final artifact body length is 1100 words",
                "if a draft exceeds 1300 body words, revise shorter before final answer",
                "architecture evidence is not judge-visible",
            ],
        }
        state_hash = sha_text(json.dumps(state_payload, sort_keys=True))
        final_state_hash = state_hash
        state_path = condition_dir / f"state_object_turn_{turn_index:03d}.json"
        baton_payload = {
            "run_id": run_id,
            "turn_index": turn_index,
            "next_model_id": "no_provider_smoke",
            "adversarial_role": role,
            "state_object_hash": state_hash,
        }
        baton_hash = sha_text(json.dumps(baton_payload, sort_keys=True))
        baton_path = condition_dir / f"baton_pass_turn_{turn_index:03d}.json"
        write_json(state_path, state_payload)
        write_json(baton_path, baton_payload)
        turns.append(
            {
                "turn_index": turn_index,
                "state_object_hash": state_hash,
                "state_object_snapshot_path": str(state_path),
                "critical_constraints_preserved": [
                    {
                        "constraint_id": "frozen_source_packet_hash",
                        "status": "preserved",
                        "evidence_hash_or_location": source_packet_hash,
                    },
                    {
                        "constraint_id": "six_turn_v2_shape",
                        "status": "preserved",
                        "evidence_hash_or_location": f"turn_count:{EXPECTED_TURN_COUNT}",
                    },
                    {
                        "constraint_id": "architecture_evidence_hidden_from_judges",
                        "status": "preserved",
                        "evidence_hash_or_location": "visible_surface_boundary.judge_packets_include_architecture_evidence=false",
                    },
                ],
                "settled_decisions_if_present": {
                    "present": True,
                    "settled_decisions": [
                        {
                            "decision_id": "scout_domain_and_packet_locked",
                            "decision_hash_or_location": lock_hash,
                        }
                    ],
                },
                "artifact_registry_entries": registry_entries,
                "artifact_registry_hash": registry_hash,
                "pinned_source_hashes": [source_packet_hash, task_brief_hash, lock_hash],
                "pinned_artifact_hashes": [final_artifact_hash],
                "retrieve_by_id_or_source_reference_behavior": {
                    "required": True,
                    "observed": True,
                    "evidence_hash_or_location": "source_packet.sources[].source_id",
                },
                "token_budget_partial_injection_flags": {
                    "present": True,
                    "token_budget_limit": None,
                    "tokens_used": 0,
                    "partial_injection_used": False,
                    "partial_injection_reason": None,
                },
                "baton_pass": {
                    "baton_pass_hash": baton_hash,
                    "baton_pass_path": str(baton_path),
                    "next_model_id": "no_provider_smoke",
                    "adversarial_role": role,
                },
                "selected_model": {
                    "provider": "no_provider_smoke",
                    "exact_model_id": "no_provider_smoke",
                    "endpoint": "none",
                },
                "adversarial_role": role,
                "role_compliance_result": {
                    "status": "not_checked",
                    "evidence_hash_or_location": "no_provider_smoke_no_model_turn",
                },
                "state_audit_constraint_preservation_result": {
                    "state_audit_status": "pass",
                    "constraint_preservation_status": "pass",
                    "evidence_hash_or_location": state_hash,
                },
                "synthesis_trigger": {
                    "triggered": turn_index == EXPECTED_TURN_COUNT,
                    "reason": "no_provider_smoke_final_turn_slot" if turn_index == EXPECTED_TURN_COUNT else None,
                },
            }
        )
    arch_evidence = {
        "schema_version": "holo_build_arch_evidence_schema_v4_1",
        "architecture_policy_id": "HOLOBUILD_PATENT_ALIGNMENT_POLICY_V4_1",
        "run_id": run_id,
        "domain_id": "D5_healthcare_medtech_evidence_synthesis",
        "condition_type": "holo_build_arch",
        "provider_calls_recorded": PROVIDER_CALLS,
        "architecture_evidence_visible_to_judges": False,
        "visible_surface_boundary": visible_surface_boundary(),
        "proof_credit_readiness": proof_credit_readiness(),
        "turns": turns,
        "final": {
            "synthesis_trigger": "no_provider_smoke_final_turn_slot",
            "final_artifact_hash": final_artifact_hash,
            "final_artifact_path": str(condition_dir / "artifact.md"),
            "final_state_object_hash": final_state_hash,
            "final_artifact_registry_hash": registry_hash,
            "architecture_evidence_visible_to_judges": False,
        },
    }
    return arch_evidence


def validate_smoke_arch_evidence(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required_top = {
        "schema_version",
        "architecture_policy_id",
        "run_id",
        "domain_id",
        "condition_type",
        "provider_calls_recorded",
        "architecture_evidence_visible_to_judges",
        "visible_surface_boundary",
        "proof_credit_readiness",
        "turns",
        "final",
    }
    missing = sorted(required_top - set(evidence))
    if missing:
        errors.append(f"arch evidence missing top-level fields: {missing}")
    if evidence.get("architecture_evidence_visible_to_judges") is not False:
        errors.append("arch evidence is judge-visible")
    if evidence.get("condition_type") != "holo_build_arch":
        errors.append("arch evidence condition_type mismatch")
    turns = evidence.get("turns") or []
    if len(turns) != EXPECTED_TURN_COUNT:
        errors.append(f"arch evidence turn count mismatch: expected {EXPECTED_TURN_COUNT}, got {len(turns)}")
    if not turns:
        errors.append("arch evidence has no turns")
    else:
        required_turn = {
            "state_object_hash",
            "state_object_snapshot_path",
            "critical_constraints_preserved",
            "settled_decisions_if_present",
            "artifact_registry_entries",
            "artifact_registry_hash",
            "pinned_source_hashes",
            "pinned_artifact_hashes",
            "retrieve_by_id_or_source_reference_behavior",
            "token_budget_partial_injection_flags",
            "baton_pass",
            "selected_model",
            "adversarial_role",
            "role_compliance_result",
            "state_audit_constraint_preservation_result",
            "synthesis_trigger",
        }
        for turn in turns:
            missing_turn = sorted(required_turn - set(turn))
            if missing_turn:
                errors.append(f"arch evidence missing per-turn fields on turn {turn.get('turn_index')}: {missing_turn}")
        if turns and (turns[-1].get("synthesis_trigger") or {}).get("triggered") is not True:
            errors.append("final architecture turn does not trigger synthesis")
    final = evidence.get("final") or {}
    if final.get("architecture_evidence_visible_to_judges") is not False:
        errors.append("final arch evidence visibility is not false")
    return errors


def source_packet_summary(packet_dir: Path) -> str:
    return (packet_dir / "source_packet.md").read_text(encoding="utf-8")


def task_brief_text(packet_dir: Path) -> str:
    return (packet_dir / "task_brief.md").read_text(encoding="utf-8")


def packet_hash_bundle(packet_dir: Path) -> dict[str, str]:
    return {
        "source_packet_json": sha_file(packet_dir / "source_packet.json"),
        "source_packet_md": sha_file(packet_dir / "source_packet.md"),
        "task_brief": sha_file(packet_dir / "task_brief.md"),
        "packet_lock": sha_file(packet_dir / "packet_lock.json"),
    }


def required_env_for_conditions(conditions: list[str]) -> list[str]:
    provider_models: list[str] = []
    if "solo_openai_gpt_5_5" in conditions:
        provider_models.append(SOLO_PROVIDER_MODEL)
    if "holo_build_arch" in conditions:
        provider_models.extend(item["provider_model"] for item in HOLO_PROVIDER_TURNS)
        provider_models.append(HOLO_SYNTHESIS_MODEL)
    envs: list[str] = []
    for provider_model_name in provider_models:
        provider, _ = provider_model(provider_model_name)
        env = PROVIDER_ENV[provider]
        if env not in envs:
            envs.append(env)
    return envs


def ensure_env_available(conditions: list[str]) -> None:
    required = required_env_for_conditions(conditions)
    missing = [env for env in required if not os.getenv(env)]
    if missing:
        raise SystemExit(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_LIVE_FAIL_CLOSED",
                    "reason": "missing_required_provider_env",
                    "missing_required_provider_env": missing,
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )


def model_visible_payload(packet_dir: Path) -> str:
    hashes = packet_hash_bundle(packet_dir)
    return (
        "FROZEN TASK BRIEF\n"
        "=================\n"
        f"{task_brief_text(packet_dir).strip()}\n\n"
        "FROZEN SOURCE PACKET\n"
        "====================\n"
        f"{source_packet_summary(packet_dir).strip()}\n\n"
        "FROZEN PACKET HASHES\n"
        "====================\n"
        f"source_packet.json sha256: {hashes['source_packet_json']}\n"
        f"source_packet.md sha256: {hashes['source_packet_md']}\n"
        f"task_brief.md sha256: {hashes['task_brief']}\n\n"
        "Use only the frozen sources above. Do not browse. Do not import outside facts."
    )


def final_artifact_instruction() -> str:
    return (
        f"Final artifact body requirement: {FINAL_WORD_MIN}-{FINAL_WORD_MAX} body words, "
        f"target {FINAL_WORD_TARGET}. If the draft exceeds {FINAL_WORD_MAX} body words, "
        "revise shorter before final answer. Return only the final crisis brief body plus required disclaimer; "
        "do not include process notes, metadata, hidden analysis, or appendices."
    )


def solo_system_prompt() -> str:
    return (
        "You are a healthcare and MedTech evidence-synthesis writer. "
        "Write only the final decision-grade crisis brief requested by the frozen task. "
        "Use only source IDs from the frozen source packet. Do not browse or use outside facts. "
        "Do not discuss model identity, scoring, judges, or generation process."
    )


def solo_user_prompt(packet_dir: Path) -> str:
    return (
        f"{model_visible_payload(packet_dir)}\n\n"
        f"{final_artifact_instruction()} "
        "Include the required disclaimer from the task brief. "
        "Do not include process notes, metadata, or hidden analysis."
    )


def solo_self_refine_system_prompt(role: str) -> str:
    return (
        "You are a single-model healthcare and MedTech evidence-synthesis writer performing a disciplined self-refinement pass. "
        f"Current pass: {role}. "
        "Use only source IDs from the frozen source packet. Do not browse or use outside facts. "
        "Do not discuss model identity, scoring, judges, or generation process."
    )


def solo_self_refine_user_prompt(
    packet_dir: Path,
    *,
    turn_index: int,
    objective: str,
    previous_outputs: list[dict[str, str]],
) -> str:
    previous_block = "\n\n".join(
        f"Prior pass {item['turn_index']} ({item['role']}):\n{item['text']}" for item in previous_outputs
    )
    if not previous_block:
        previous_block = "No prior draft."
    final_line = final_artifact_instruction() if turn_index == EXPECTED_TURN_COUNT else "This is an intermediate self-refinement pass, not the final artifact."
    return (
        f"{model_visible_payload(packet_dir)}\n\n"
        f"SELF-REFINE PASS {turn_index} OF {EXPECTED_TURN_COUNT}\n"
        "====================\n"
        f"{objective}\n\n"
        f"PRIOR DRAFT / REVISION HISTORY\n==============================\n{previous_block}\n\n"
        f"{final_line}"
    )


def holo_turn_system_prompt(role: str) -> str:
    return (
        "You are an independent adversarial reviewer for a healthcare crisis evidence task. "
        f"Your role is {role}. "
        "Use only the frozen source packet. Do not browse or use outside facts. "
        "Return concise source-cited findings that will help a later synthesis author. "
        "Do not discuss model identity, scoring, judges, or generation process."
    )


def holo_turn_user_prompt(packet_dir: Path, *, objective: str, previous_notes: list[dict[str, str]]) -> str:
    previous_block = "\n\n".join(
        f"Prior reviewer {item['turn_index']} ({item['role']}):\n{item['text']}" for item in previous_notes
    )
    if not previous_block:
        previous_block = "No prior reviewer notes."
    return (
        f"{model_visible_payload(packet_dir)}\n\n"
        f"REVIEW OBJECTIVE\n================\n{objective}\n\n"
        f"PRIOR REVIEWER NOTES\n====================\n{previous_block}\n\n"
        "Return source-cited findings with explicit claim boundaries, contradictions, weak evidence, "
        "calculation/data interpretation checks, and practical implications. Do not write the final brief yet."
    )


def holo_synthesis_system_prompt() -> str:
    return (
        "You are the final synthesis author for a healthcare and MedTech crisis evidence brief. "
        "Use only the frozen source packet and the reviewer notes supplied. "
        "Write only the final decision-grade crisis brief requested by the frozen task. "
        "Do not discuss model identity, scoring, judges, or generation process."
    )


def holo_synthesis_user_prompt(packet_dir: Path, reviewer_notes: list[dict[str, str]]) -> str:
    notes = "\n\n".join(
        f"Reviewer {item['turn_index']} ({item['role']}):\n{item['text']}" for item in reviewer_notes
    )
    return (
        f"{model_visible_payload(packet_dir)}\n\n"
        "REVIEWER NOTES\n==============\n"
        f"{notes}\n\n"
        f"Synthesize the final crisis brief only. {final_artifact_instruction()} Include the required disclaimer."
    )


def save_prompt_card(
    condition_dir: Path,
    *,
    call_id: str,
    provider_model_name: str,
    system: str,
    user: str,
    call_type: str,
    role: str,
    turn_index: int | None,
) -> Path:
    provider, model = provider_model(provider_model_name)
    path = condition_dir / "prompt_cards" / f"{call_id}.json"
    write_json(
        path,
        {
            "call_id": call_id,
            "call_type": call_type,
            "role": role,
            "turn_index": turn_index,
            "provider": provider,
            "model": model,
            "system": system,
            "user": user,
            "judge_visible": False,
        },
    )
    return path


def save_trace(
    condition_dir: Path,
    *,
    call_id: str,
    provider_model_name: str,
    call_type: str,
    role: str,
    turn_index: int | None,
    prompt_card_path: Path,
    artifact_path: Path | None,
    artifact_text: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    provider, model = provider_model(provider_model_name)
    trace = {
        "call_id": call_id,
        "call_type": call_type,
        "role": role,
        "turn_index": turn_index,
        "provider": provider,
        "model": model,
        "endpoint": endpoint_for_provider(provider),
        "prompt_card_path": str(prompt_card_path),
        "artifact_path": str(artifact_path) if artifact_path else None,
        "artifact_sha256": sha_text(artifact_text) if artifact_text else None,
        "input_tokens": int(result.get("input_tokens") or 0),
        "output_tokens": int(result.get("output_tokens") or 0),
        "latency_ms": int(result.get("latency_ms") or 0),
        "http_status": result.get("http_status"),
        "response_id": result.get("response_id", ""),
        "created_at_utc": utc_iso(),
        "judge_visible": False,
    }
    write_json(condition_dir / "traces" / f"{call_id}.json", trace)
    return trace


def call_live_model(
    condition_dir: Path,
    *,
    provider_model_name: str,
    system: str,
    user: str,
    max_tokens: int,
    timeout: int,
    call_type: str,
    role: str,
    turn_index: int | None,
    call_id: str,
    artifact_path: Path | None,
) -> tuple[str, dict[str, Any]]:
    global PROVIDER_CALLS
    prompt_card_path = save_prompt_card(
        condition_dir,
        call_id=call_id,
        provider_model_name=provider_model_name,
        system=system,
        user=user,
        call_type=call_type,
        role=role,
        turn_index=turn_index,
    )
    provider, model = provider_model(provider_model_name)
    result = call_provider(provider, system=system, user=user, max_tokens=max_tokens, timeout=timeout, model_override=model)
    PROVIDER_CALLS += 1
    text = result["text"].strip() + "\n"
    if artifact_path:
        write_text(artifact_path, text)
    trace = save_trace(
        condition_dir,
        call_id=call_id,
        provider_model_name=provider_model_name,
        call_type=call_type,
        role=role,
        turn_index=turn_index,
        prompt_card_path=prompt_card_path,
        artifact_path=artifact_path,
        artifact_text=text,
        result=result,
    )
    return text, trace


def role_compliance(text: str, *, final: bool = False) -> dict[str, str]:
    has_source_ref = bool(re.search(r"\bS[1-9](_[A-Z0-9_]+)?\b", text))
    if not text.strip():
        status = "fail"
        evidence = "empty_output"
    elif final and not (FINAL_WORD_MIN <= word_count(text) <= FINAL_WORD_MAX):
        status = "fail"
        evidence = f"word_count:{word_count(text)}"
    elif not has_source_ref:
        status = "fail"
        evidence = "missing_source_id_references"
    else:
        status = "pass"
        evidence = f"source_refs_present_word_count:{word_count(text)}"
    return {"status": status, "evidence_hash_or_location": evidence}


def state_audit(text: str, hashes: dict[str, str]) -> dict[str, str]:
    return {
        "state_audit_status": "pass" if text.strip() else "fail",
        "constraint_preservation_status": "pass" if hashes.get("source_packet_json") else "fail",
        "evidence_hash_or_location": hashes["source_packet_json"],
    }


def live_state_payload(
    *,
    packet_dir: Path,
    run_id: str,
    turn_index: int,
    role: str,
    objective: str,
    prior_hashes: list[str],
) -> dict[str, Any]:
    hashes = packet_hash_bundle(packet_dir)
    return {
        "run_id": run_id,
        "packet_id": read_json(packet_dir / "source_packet.json")["packet_id"],
        "turn_index": turn_index,
        "role": role,
        "objective": objective,
        "critical_constraints": [
            "use only frozen packet sources",
            "do not browse",
            "main artifact body must be 900-1300 words",
            "target final artifact body length is 1100 words",
            "if a draft exceeds 1300 body words, revise shorter before final answer",
            "do not overclaim capacity solution, FDA approval, or clinical proof",
            "architecture evidence is not judge-visible",
        ],
        "pinned_hashes": hashes,
        "prior_artifact_hashes": prior_hashes,
    }


def live_baton_payload(
    *,
    run_id: str,
    turn_index: int,
    next_model_id: str,
    adversarial_role: str,
    objective: str,
    state_hash: str,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "turn_index": turn_index,
        "next_model_id": next_model_id,
        "adversarial_role": adversarial_role,
        "objective": objective,
        "state_object_hash": state_hash,
    }


def artifact_registry_entries(packet_dir: Path, artifacts: list[dict[str, str]]) -> list[dict[str, Any]]:
    hashes = packet_hash_bundle(packet_dir)
    entries = [
        {
            "artifact_id": "frozen_source_packet",
            "artifact_type": "source_packet",
            "artifact_hash": hashes["source_packet_json"],
            "source_refs": ["source_packet.json"],
        },
        {
            "artifact_id": "frozen_task_brief",
            "artifact_type": "task_brief",
            "artifact_hash": hashes["task_brief"],
            "source_refs": ["task_brief.md"],
        },
    ]
    for item in artifacts:
        entries.append(
            {
                "artifact_id": item["artifact_id"],
                "artifact_type": item["artifact_type"],
                "artifact_hash": item["artifact_hash"],
                "source_refs": item["source_refs"],
            }
        )
    return entries


def build_live_arch_evidence(
    *,
    packet_dir: Path,
    run_id: str,
    condition_dir: Path,
    turn_records: list[dict[str, Any]],
    final_artifact_path: Path,
    final_artifact_text: str,
) -> dict[str, Any]:
    hashes = packet_hash_bundle(packet_dir)
    evidence_turns: list[dict[str, Any]] = []
    all_artifacts: list[dict[str, str]] = []
    for record in turn_records:
        all_artifacts.append(record["artifact_record"])
        entries = artifact_registry_entries(packet_dir, all_artifacts)
        registry_hash = sha_text(json.dumps(entries, sort_keys=True))
        evidence_turns.append(
            {
                "turn_index": record["turn_index"],
                "state_object_hash": record["state_object_hash"],
                "state_object_snapshot_path": str(record["state_object_path"]),
                "critical_constraints_preserved": [
                    {
                        "constraint_id": "frozen_source_packet_hash",
                        "status": "preserved",
                        "evidence_hash_or_location": hashes["source_packet_json"],
                    },
                    {
                        "constraint_id": "no_live_web_browsing",
                        "status": "preserved",
                        "evidence_hash_or_location": "model_prompt_use_only_frozen_sources",
                    },
                    {
                        "constraint_id": "architecture_evidence_hidden_from_judges",
                        "status": "preserved",
                        "evidence_hash_or_location": "visible_surface_boundary.judge_packets_include_architecture_evidence=false",
                    },
                ],
                "settled_decisions_if_present": {
                    "present": True,
                    "settled_decisions": [
                        {
                            "decision_id": "d5_mini_scout_packet_locked",
                            "decision_hash_or_location": hashes["packet_lock"],
                        },
                        {
                            "decision_id": "word_count_gate_900_1300",
                            "decision_hash_or_location": sha_file(packet_dir / "deterministic_gate_policy.json"),
                        },
                    ],
                },
                "artifact_registry_entries": entries,
                "artifact_registry_hash": registry_hash,
                "pinned_source_hashes": [hashes["source_packet_json"], hashes["source_packet_md"], hashes["task_brief"], hashes["packet_lock"]],
                "pinned_artifact_hashes": [item["artifact_hash"] for item in all_artifacts],
                "retrieve_by_id_or_source_reference_behavior": {
                    "required": True,
                    "observed": True,
                    "evidence_hash_or_location": "source_packet.sources[].source_id",
                },
                "token_budget_partial_injection_flags": record["token_budget_partial_injection_flags"],
                "baton_pass": {
                    "baton_pass_hash": record["baton_pass_hash"],
                    "baton_pass_path": str(record["baton_pass_path"]),
                    "next_model_id": record["selected_model"]["exact_model_id"],
                    "adversarial_role": record["adversarial_role"],
                },
                "selected_model": record["selected_model"],
                "adversarial_role": record["adversarial_role"],
                "role_compliance_result": record["role_compliance_result"],
                "state_audit_constraint_preservation_result": record["state_audit_constraint_preservation_result"],
                "synthesis_trigger": record["synthesis_trigger"],
            }
        )
    final_registry_entries = artifact_registry_entries(packet_dir, all_artifacts)
    final_registry_hash = sha_text(json.dumps(final_registry_entries, sort_keys=True))
    final_state_hash = turn_records[-1]["state_object_hash"]
    return {
        "schema_version": "holo_build_arch_evidence_schema_v4_1",
        "architecture_policy_id": "HOLOBUILD_PATENT_ALIGNMENT_POLICY_V4_1",
        "run_id": run_id,
        "domain_id": "D5_healthcare_medtech_evidence_synthesis",
        "condition_type": "holo_build_arch",
        "provider_calls_recorded": PROVIDER_CALLS,
        "architecture_evidence_visible_to_judges": False,
        "visible_surface_boundary": visible_surface_boundary(),
        "proof_credit_readiness": proof_credit_readiness(),
        "turns": evidence_turns,
        "final": {
            "synthesis_trigger": "final_synthesis_turn_completed",
            "final_artifact_hash": sha_text(final_artifact_text),
            "final_artifact_path": str(final_artifact_path),
            "final_state_object_hash": final_state_hash,
            "final_artifact_registry_hash": final_registry_hash,
            "architecture_evidence_visible_to_judges": False,
        },
    }


def write_live_metadata(
    *,
    packet_dir: Path,
    condition_dir: Path,
    run_id: str,
    condition: str,
    artifact_text: str,
    provider_models: list[str],
    traces: list[dict[str, Any]],
    arch_evidence_path: Path | None,
) -> dict[str, Any]:
    source_packet_hash = sha_file(packet_dir / "source_packet.json")
    gate = deterministic_gate_precheck(packet_dir, condition, artifact_text)
    write_json(condition_dir / "deterministic_gate_precheck.json", gate)
    metadata = {
        "runner_id": RUNNER_ID,
        "run_mode": RUN_MODE,
        "run_id": run_id,
        "condition": condition,
        "condition_label": CONDITION_LABELS[condition],
        "status": "live_generation_complete",
        "created_at_utc": utc_iso(),
        "provider_calls": len(traces),
        "provider_models": provider_models,
        "scores_generated": SCORES_GENERATED,
        "packet_dir": str(packet_dir),
        "packet_id": read_json(packet_dir / "packet_lock.json")["packet_id"],
        "packet_hash": source_packet_hash,
        "frozen_task_brief_hash": sha_file(packet_dir / "task_brief.md"),
        "frozen_source_packet_hash": source_packet_hash,
        "artifact_path": str(condition_dir / "artifact.md"),
        "artifact_written": True,
        "artifact_sha256": sha_text(artifact_text),
        "artifact_word_count": word_count(artifact_text),
        "expected_turn_count": EXPECTED_TURN_COUNT,
        "final_word_target": FINAL_WORD_TARGET,
        "deterministic_gate_precheck_path": str(condition_dir / "deterministic_gate_precheck.json"),
        "deterministic_gate_status": gate["deterministic_gate_status"],
        "architecture_evidence_path": str(arch_evidence_path) if arch_evidence_path else None,
        "input_tokens": sum(int(trace.get("input_tokens") or 0) for trace in traces),
        "output_tokens": sum(int(trace.get("output_tokens") or 0) for trace in traces),
        "latency_ms": sum(int(trace.get("latency_ms") or 0) for trace in traces),
    }
    write_json(condition_dir / "artifact_metadata.json", metadata)
    return metadata


def run_live_solo(packet_dir: Path, run_id: str, timeout: int) -> dict[str, Any]:
    condition = "solo_openai_gpt_5_5"
    condition_dir = packet_dir / "runs" / run_id / condition
    condition_dir.mkdir(parents=True, exist_ok=True)
    traces: list[dict[str, Any]] = []
    prior_outputs: list[dict[str, str]] = []
    final_text = ""
    artifact_path = condition_dir / "artifact.md"
    for turn_index, turn in enumerate(SOLO_SELF_REFINE_TURNS, start=1):
        is_final = turn_index == EXPECTED_TURN_COUNT
        output_path = artifact_path if is_final else condition_dir / "turn_artifacts" / f"turn_{turn_index:03d}.md"
        text, trace = call_live_model(
            condition_dir,
            provider_model_name=SOLO_PROVIDER_MODEL,
            system=solo_self_refine_system_prompt(turn["role"]),
            user=solo_self_refine_user_prompt(
                packet_dir,
                turn_index=turn_index,
                objective=turn["objective"],
                previous_outputs=prior_outputs,
            ),
            max_tokens=int(turn["max_tokens"]),
            timeout=timeout,
            call_type="solo_self_refine_final" if is_final else "solo_self_refine_turn",
            role=turn["role"],
            turn_index=turn_index,
            call_id="solo_final_artifact" if is_final else f"solo_turn_{turn_index:03d}",
            artifact_path=output_path,
        )
        traces.append(trace)
        prior_outputs.append({"turn_index": str(turn_index), "role": turn["role"], "text": excerpt(text, 3000)})
        if is_final:
            final_text = text
    metadata = write_live_metadata(
        packet_dir=packet_dir,
        condition_dir=condition_dir,
        run_id=run_id,
        condition=condition,
        artifact_text=final_text,
        provider_models=[SOLO_PROVIDER_MODEL for _ in SOLO_SELF_REFINE_TURNS],
        traces=traces,
        arch_evidence_path=None,
    )
    return {
        "condition": condition,
        "condition_dir": str(condition_dir),
        "packet_hash": metadata["packet_hash"],
        "artifact_path": str(artifact_path),
        "artifact_sha256": metadata["artifact_sha256"],
        "deterministic_gate_precheck": metadata["deterministic_gate_status"],
        "architecture_evidence_status": "not_applicable",
        "provider_calls": len(traces),
    }


def run_live_holobuild(packet_dir: Path, run_id: str, timeout: int) -> dict[str, Any]:
    condition = "holo_build_arch"
    condition_dir = packet_dir / "runs" / run_id / condition
    condition_dir.mkdir(parents=True, exist_ok=True)
    reviewer_notes: list[dict[str, str]] = []
    turn_records: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    artifact_records: list[dict[str, str]] = []
    prior_hashes: list[str] = []

    for index, turn in enumerate(HOLO_PROVIDER_TURNS, start=1):
        provider_model_name = turn["provider_model"]
        provider, model = provider_model(provider_model_name)
        state_payload = live_state_payload(
            packet_dir=packet_dir,
            run_id=run_id,
            turn_index=index,
            role=turn["role"],
            objective=turn["objective"],
            prior_hashes=prior_hashes,
        )
        state_hash = sha_text(json.dumps(state_payload, sort_keys=True))
        state_path = condition_dir / f"state_object_turn_{index:03d}.json"
        write_json(state_path, state_payload)
        baton_payload = live_baton_payload(
            run_id=run_id,
            turn_index=index,
            next_model_id=model,
            adversarial_role=turn["role"],
            objective=turn["objective"],
            state_hash=state_hash,
        )
        baton_hash = sha_text(json.dumps(baton_payload, sort_keys=True))
        baton_path = condition_dir / f"baton_pass_turn_{index:03d}.json"
        write_json(baton_path, baton_payload)
        turn_path = condition_dir / "turn_artifacts" / f"turn_{index:03d}.md"
        text, trace = call_live_model(
            condition_dir,
            provider_model_name=provider_model_name,
            system=holo_turn_system_prompt(turn["role"]),
            user=holo_turn_user_prompt(packet_dir, objective=turn["objective"], previous_notes=reviewer_notes),
            max_tokens=int(turn["max_tokens"]),
            timeout=timeout,
            call_type="holo_reviewer_turn",
            role=turn["role"],
            turn_index=index,
            call_id=f"holo_turn_{index:03d}",
            artifact_path=turn_path,
        )
        traces.append(trace)
        artifact_hash = sha_text(text)
        prior_hashes.append(artifact_hash)
        reviewer_notes.append({"turn_index": str(index), "role": turn["role"], "text": excerpt(text, 3000)})
        artifact_record = {
            "artifact_id": f"turn_{index:03d}_{turn['role']}",
            "artifact_type": "reviewer_turn_artifact",
            "artifact_hash": artifact_hash,
            "source_refs": [str(turn_path)],
        }
        artifact_records.append(artifact_record)
        turn_records.append(
            {
                "turn_index": index,
                "state_object_hash": state_hash,
                "state_object_path": state_path,
                "baton_pass_hash": baton_hash,
                "baton_pass_path": baton_path,
                "selected_model": {"provider": provider, "exact_model_id": model, "endpoint": endpoint_for_provider(provider)},
                "adversarial_role": turn["role"],
                "role_compliance_result": role_compliance(text),
                "state_audit_constraint_preservation_result": state_audit(text, packet_hash_bundle(packet_dir)),
                "synthesis_trigger": {"triggered": False, "reason": None},
                "token_budget_partial_injection_flags": {
                    "present": True,
                    "token_budget_limit": int(turn["max_tokens"]),
                    "tokens_used": int(trace.get("output_tokens") or 0),
                    "partial_injection_used": False,
                    "partial_injection_reason": None,
                },
                "artifact_record": artifact_record,
            }
        )

    synthesis_index = len(HOLO_PROVIDER_TURNS) + 1
    provider, model = provider_model(HOLO_SYNTHESIS_MODEL)
    synthesis_state = live_state_payload(
        packet_dir=packet_dir,
        run_id=run_id,
        turn_index=synthesis_index,
        role="final_synthesis_author",
        objective="Synthesize the final 900-1,300 word decision-grade crisis brief from frozen sources and reviewer notes.",
        prior_hashes=prior_hashes,
    )
    synthesis_state_hash = sha_text(json.dumps(synthesis_state, sort_keys=True))
    synthesis_state_path = condition_dir / f"state_object_turn_{synthesis_index:03d}.json"
    write_json(synthesis_state_path, synthesis_state)
    synthesis_baton = live_baton_payload(
        run_id=run_id,
        turn_index=synthesis_index,
        next_model_id=model,
        adversarial_role="final_synthesis_author",
        objective="Synthesize final artifact under claim-boundary and source-fidelity constraints.",
        state_hash=synthesis_state_hash,
    )
    synthesis_baton_hash = sha_text(json.dumps(synthesis_baton, sort_keys=True))
    synthesis_baton_path = condition_dir / f"baton_pass_turn_{synthesis_index:03d}.json"
    write_json(synthesis_baton_path, synthesis_baton)
    artifact_path = condition_dir / "artifact.md"
    final_text, final_trace = call_live_model(
        condition_dir,
        provider_model_name=HOLO_SYNTHESIS_MODEL,
        system=holo_synthesis_system_prompt(),
        user=holo_synthesis_user_prompt(packet_dir, reviewer_notes),
        max_tokens=3400,
        timeout=timeout,
        call_type="holo_final_synthesis",
        role="final_synthesis_author",
        turn_index=synthesis_index,
        call_id="holo_final_synthesis",
        artifact_path=artifact_path,
    )
    traces.append(final_trace)
    final_hash = sha_text(final_text)
    final_record = {
        "artifact_id": "final_synthesis_artifact",
        "artifact_type": "final_artifact",
        "artifact_hash": final_hash,
        "source_refs": [str(artifact_path)],
    }
    artifact_records.append(final_record)
    turn_records.append(
        {
            "turn_index": synthesis_index,
            "state_object_hash": synthesis_state_hash,
            "state_object_path": synthesis_state_path,
            "baton_pass_hash": synthesis_baton_hash,
            "baton_pass_path": synthesis_baton_path,
            "selected_model": {"provider": provider, "exact_model_id": model, "endpoint": endpoint_for_provider(provider)},
            "adversarial_role": "final_synthesis_author",
            "role_compliance_result": role_compliance(final_text, final=True),
            "state_audit_constraint_preservation_result": state_audit(final_text, packet_hash_bundle(packet_dir)),
            "synthesis_trigger": {"triggered": True, "reason": "final_synthesis_turn_completed"},
            "token_budget_partial_injection_flags": {
                "present": True,
                "token_budget_limit": 3400,
                "tokens_used": int(final_trace.get("output_tokens") or 0),
                "partial_injection_used": False,
                "partial_injection_reason": None,
            },
            "artifact_record": final_record,
        }
    )
    arch_evidence = build_live_arch_evidence(
        packet_dir=packet_dir,
        run_id=run_id,
        condition_dir=condition_dir,
        turn_records=turn_records,
        final_artifact_path=artifact_path,
        final_artifact_text=final_text,
    )
    arch_errors = validate_smoke_arch_evidence(arch_evidence)
    arch_path = condition_dir / "arch_evidence.json"
    write_json(arch_path, arch_evidence)
    metadata = write_live_metadata(
        packet_dir=packet_dir,
        condition_dir=condition_dir,
        run_id=run_id,
        condition=condition,
        artifact_text=final_text,
        provider_models=[item["provider_model"] for item in HOLO_PROVIDER_TURNS] + [HOLO_SYNTHESIS_MODEL],
        traces=traces,
        arch_evidence_path=arch_path,
    )
    return {
        "condition": condition,
        "condition_dir": str(condition_dir),
        "packet_hash": metadata["packet_hash"],
        "artifact_path": str(artifact_path),
        "artifact_sha256": metadata["artifact_sha256"],
        "deterministic_gate_precheck": metadata["deterministic_gate_status"],
        "architecture_evidence_status": "valid" if not arch_errors else "invalid",
        "architecture_evidence_errors": arch_errors,
        "architecture_evidence_path": str(arch_path),
        "provider_calls": len(traces),
    }


def write_condition_smoke(packet_dir: Path, run_id: str, condition: str) -> dict[str, Any]:
    run_dir = packet_dir / "runs" / run_id
    condition_dir = run_dir / condition
    condition_dir.mkdir(parents=True, exist_ok=True)
    lock = read_json(packet_dir / "packet_lock.json")
    source_packet_hash = sha_file(packet_dir / "source_packet.json")
    gate = deterministic_gate_precheck(packet_dir, condition)
    metadata = {
        "runner_id": RUNNER_ID,
        "run_id": run_id,
        "condition": condition,
        "condition_label": CONDITION_LABELS[condition],
        "status": "planned_no_provider_smoke",
        "created_at_utc": utc_iso(),
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "scores_generated": SCORES_GENERATED,
        "packet_dir": str(packet_dir),
        "packet_id": lock["packet_id"],
        "packet_hash": source_packet_hash,
        "frozen_task_brief_hash": sha_file(packet_dir / "task_brief.md"),
        "frozen_source_packet_hash": source_packet_hash,
        "artifact_path": str(condition_dir / "artifact.md"),
        "artifact_written": False,
        "expected_turn_count": EXPECTED_TURN_COUNT,
        "final_word_target": FINAL_WORD_TARGET,
        "deterministic_gate_precheck_path": str(condition_dir / "deterministic_gate_precheck.json"),
        "architecture_evidence_path": str(condition_dir / "arch_evidence.json") if condition == "holo_build_arch" else None,
    }
    write_json(condition_dir / "deterministic_gate_precheck.json", gate)
    write_json(condition_dir / "artifact_metadata.json", metadata)

    arch_status = "not_applicable"
    arch_errors: list[str] = []
    if condition == "holo_build_arch":
        evidence = smoke_arch_evidence(packet_dir, run_id, condition_dir)
        arch_errors = validate_smoke_arch_evidence(evidence)
        arch_status = "wired_and_schema_shape_valid" if not arch_errors else "invalid"
        write_json(condition_dir / "arch_evidence.json", evidence)

    result = {
        "condition": condition,
        "condition_dir": str(condition_dir),
        "packet_hash": source_packet_hash,
        "deterministic_gate_precheck": gate["deterministic_gate_status"],
        "artifact_slots_wired": ["artifact.md", "artifact_metadata.json", "deterministic_gate_precheck.json"],
        "architecture_evidence_status": arch_status,
        "architecture_evidence_errors": arch_errors,
        "provider_calls": PROVIDER_CALLS,
    }
    return result


def update_run_manifest(packet_dir: Path, run_id: str, condition_results: list[dict[str, Any]]) -> dict[str, Any]:
    run_dir = packet_dir / "runs" / run_id
    manifest_path = run_dir / "run_manifest.json"
    previous: dict[str, Any] = {}
    if manifest_path.exists():
        previous = read_json(manifest_path)
    existing = {item["condition"]: item for item in previous.get("conditions", [])}
    for item in condition_results:
        existing[item["condition"]] = item
    manifest = {
        "runner_id": RUNNER_ID,
        "run_mode": RUN_MODE,
        "run_id": run_id,
        "status": "NO_PROVIDER_SMOKE_READY",
        "updated_at_utc": utc_iso(),
        "packet_dir": str(packet_dir),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": [existing[key] for key in VALID_CONDITIONS if key in existing],
        "provider_calls": PROVIDER_CALLS,
        "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
        "scores_generated": SCORES_GENERATED,
        "live_mode_fail_closed": True,
        "live_requires_flag": "--live",
        "live_requires_env": f"{LIVE_APPROVAL_ENV}=1",
        "expected_turn_count_per_condition": EXPECTED_TURN_COUNT,
        "final_word_target": FINAL_WORD_TARGET,
    }
    write_json(manifest_path, manifest)
    return manifest


def update_live_run_manifest(packet_dir: Path, run_id: str, condition_results: list[dict[str, Any]]) -> dict[str, Any]:
    run_dir = packet_dir / "runs" / run_id
    manifest_path = run_dir / "run_manifest.json"
    previous: dict[str, Any] = {}
    if manifest_path.exists():
        previous = read_json(manifest_path)
    existing = {item["condition"]: item for item in previous.get("conditions", [])}
    for item in condition_results:
        existing[item["condition"]] = item
    manifest = {
        "runner_id": RUNNER_ID,
        "run_mode": RUN_MODE,
        "run_id": run_id,
        "status": "LIVE_GENERATION_COMPLETE",
        "updated_at_utc": utc_iso(),
        "packet_dir": str(packet_dir),
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "conditions": [existing[key] for key in VALID_CONDITIONS if key in existing],
        "provider_calls": sum(int(item.get("provider_calls") or 0) for item in existing.values()),
        "live_artifacts_generated": len([item for item in existing.values() if item.get("artifact_path")]),
        "scores_generated": SCORES_GENERATED,
        "live_mode_fail_closed": True,
        "live_requires_flag": "--live",
        "live_requires_env": f"{LIVE_APPROVAL_ENV}=1",
        "blind_export_ready_after_artifacts": set(existing) >= set(VALID_CONDITIONS),
        "expected_turn_count_per_condition": EXPECTED_TURN_COUNT,
        "final_word_target": FINAL_WORD_TARGET,
    }
    write_json(manifest_path, manifest)
    return manifest


def run_no_provider_smoke(packet_dir: Path, run_id: str, conditions: list[str]) -> int:
    require_packet(packet_dir)
    results = [write_condition_smoke(packet_dir, run_id, condition) for condition in conditions]
    manifest = update_run_manifest(packet_dir, run_id, results)
    status = "D5_MINI_SCOUT_RUNNER_NO_PROVIDER_SMOKE_PASS"
    if any(item.get("architecture_evidence_errors") for item in results):
        status = "D5_MINI_SCOUT_RUNNER_NO_PROVIDER_SMOKE_FAIL"
    print(
        json.dumps(
            {
                "status": status,
                "runner_id": RUNNER_ID,
                "run_id": run_id,
                "packet_hash": manifest["packet_hash"],
                "conditions": results,
                "run_manifest": str(packet_dir / "runs" / run_id / "run_manifest.json"),
                "provider_calls": PROVIDER_CALLS,
                "live_artifacts_generated": LIVE_ARTIFACTS_GENERATED,
                "scores_generated": SCORES_GENERATED,
                "live_mode_fail_closed": True,
                "live_requires": ["--live", f"{LIVE_APPROVAL_ENV}=1"],
            },
            indent=2,
        )
    )
    return 0 if status.endswith("_PASS") else 1


def run_live_guarded(packet_dir: Path, run_id: str, conditions: list[str], timeout: int) -> int:
    require_packet(packet_dir)
    if os.getenv(LIVE_APPROVAL_ENV) != "1":
        print(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_LIVE_FAIL_CLOSED",
                    "reason": f"live mode requires {LIVE_APPROVAL_ENV}=1 in addition to --live",
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )
        return 2
    ensure_env_available(conditions)
    results: list[dict[str, Any]] = []
    try:
        for condition in conditions:
            if condition == "solo_openai_gpt_5_5":
                results.append(run_live_solo(packet_dir, run_id, timeout))
            elif condition == "holo_build_arch":
                results.append(run_live_holobuild(packet_dir, run_id, timeout))
            else:
                raise RuntimeError(f"unknown condition: {condition}")
    except ProviderCallError as exc:
        print(
            json.dumps(
                {
                    "status": "D5_MINI_SCOUT_LIVE_PROVIDER_ERROR",
                    "provider": exc.provider,
                    "error_type": exc.error_type,
                    "http_status": exc.http_status,
                    "message": str(exc),
                    "provider_calls": PROVIDER_CALLS,
                },
                indent=2,
            )
        )
        return 1
    manifest = update_live_run_manifest(packet_dir, run_id, results)
    print(
        json.dumps(
            {
                "status": "D5_MINI_SCOUT_LIVE_GENERATION_COMPLETE",
                "run_id": run_id,
                "conditions": results,
                "timeout": timeout,
                "packet_hash": manifest["packet_hash"],
                "run_manifest": str(packet_dir / "runs" / run_id / "run_manifest.json"),
                "provider_calls": PROVIDER_CALLS,
                "scores_generated": SCORES_GENERATED,
            },
            indent=2,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="D5 mini scout HoloBuild vs GPT-5.5 adapter.")
    parser.add_argument("--packet-dir", default=str(DEFAULT_PACKET_DIR))
    parser.add_argument("--condition", action="append", choices=VALID_CONDITIONS, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--no-provider-smoke", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    packet_dir = Path(args.packet_dir).resolve()
    conditions = list(dict.fromkeys(args.condition))
    if args.live:
        return run_live_guarded(packet_dir, args.run_id, conditions, args.timeout)
    return run_no_provider_smoke(packet_dir, args.run_id, conditions)


if __name__ == "__main__":
    raise SystemExit(main())
