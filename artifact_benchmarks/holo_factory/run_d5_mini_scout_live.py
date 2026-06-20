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
RUN_MODE_FULL_GOV_V4 = "d5_medtech_capacity_strain_001_full_gov_v4"
HOLO_MODE_DIAGNOSTIC_V3 = "diagnostic_v3"
HOLO_MODE_FULL_GOV_V4 = "full_gov_v4"
HOLO_MODES = (HOLO_MODE_DIAGNOSTIC_V3, HOLO_MODE_FULL_GOV_V4)
LIVE_APPROVAL_ENV = "HOLO_ALLOW_LIVE"
PROVIDER_CALLS = 0
LIVE_ARTIFACTS_GENERATED = 0
SCORES_GENERATED = 0
EXPECTED_PACKET_HASH = "b73292d9d2e4aac5f65a93ae168235d9d581ae17ebaf0a91aa16437018c527aa"
EXPECTED_TURN_COUNT = 6
FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT = 14
FINAL_WORD_MIN = 900
FINAL_WORD_MAX = 1300
FINAL_WORD_TARGET = 1100

VALID_CONDITIONS = ("holo_build_arch", "solo_openai_gpt_5_5")
CONDITION_LABELS = {
    "holo_build_arch": "HoloBuild architecture condition",
    "solo_openai_gpt_5_5": "GPT-5.5 solo condition",
}
SOLO_PROVIDER_MODEL = "openai:gpt-5.5"
GOVERNOR_PROVIDER_MODEL = "openai:gpt-5.5"
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
REQUIRED_FINAL_SECTION_MARKERS = (
    "what is happening",
    "why it matters now",
    "strong evidence",
    "weak",
    "contradict",
    "calculation",
    "options",
    "risks of acting",
    "risks of waiting",
    "next steps",
    "claim boundaries",
)
ROLE_BEHAVIOR_TERMS = {
    "initial_decision_brief_drafter": ("option", "evidence", "source"),
    "assumption_and_evidence_attacker": ("assumption", "weak", "missing"),
    "contradiction_uncertainty_source_fidelity_reviewer": ("contradict", "uncertain", "source"),
    "options_operational_usefulness_reviewer": ("option", "risk", "operat"),
    "claim_discipline_overclaim_reducer": ("overclaim", "claim", "unsupported"),
    "final_synthesis_author": ("option", "risk", "source"),
}
FORBIDDEN_SOURCE_BOUNDARY_CLAIMS = (
    "fda approved",
    "final approval",
    "solves hospital capacity",
    "proves capacity relief",
)
SOURCE_ID_RE = re.compile(r"\bS\d+_[A-Z0-9_]+\b")


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


def stable_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def endpoint_for_provider(provider: str) -> str:
    if provider == "google":
        return "generateContent"
    if provider == "anthropic":
        return "messages"
    return "chat/completions"


def run_mode_for_holo_mode(holo_mode: str) -> str:
    return RUN_MODE_FULL_GOV_V4 if holo_mode == HOLO_MODE_FULL_GOV_V4 else RUN_MODE


def expected_holo_call_count(holo_mode: str) -> int:
    return FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT if holo_mode == HOLO_MODE_FULL_GOV_V4 else EXPECTED_TURN_COUNT


def expected_holobuild_provider_models(holo_mode: str) -> list[str]:
    generation_models = [item["provider_model"] for item in HOLO_PROVIDER_TURNS] + [HOLO_SYNTHESIS_MODEL]
    if holo_mode == HOLO_MODE_FULL_GOV_V4:
        return [GOVERNOR_PROVIDER_MODEL] + generation_models + [GOVERNOR_PROVIDER_MODEL] * (EXPECTED_TURN_COUNT + 1)
    return generation_models


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
    registry = base_registry(packet_dir)
    prior_artifact_ids: list[str] = []
    prior_hashes: list[str] = []
    prior_audit_results: list[dict[str, Any]] = []
    source_retrieval_ids = ["TASK_BRIEF"] + source_ids(packet_dir)
    turn_records: list[dict[str, Any]] = []
    smoke_turns = list(HOLO_PROVIDER_TURNS) + [
        {
            "provider_model": HOLO_SYNTHESIS_MODEL,
            "role": "final_synthesis_author",
            "objective": "Synthesize final artifact under claim-boundary and source-fidelity constraints.",
            "max_tokens": 3400,
        }
    ]
    for turn_index, turn in enumerate(smoke_turns, start=1):
        final = turn_index == EXPECTED_TURN_COUNT
        provider_model_name = turn["provider_model"]
        provider, model = provider_model(provider_model_name)
        retrieved_ids = source_retrieval_ids + prior_artifact_ids
        retrieved_entries = retrieve_registry_entries(registry, retrieved_ids)
        state_payload = build_state_object(
            packet_dir=packet_dir,
            run_id=run_id,
            turn_index=turn_index,
            role=turn["role"],
            objective=turn["objective"],
            registry=registry,
            prior_artifact_hashes=prior_hashes,
            prior_audit_results=prior_audit_results,
        )
        state_hash = sha_text(json.dumps(state_payload, sort_keys=True))
        state_path = condition_dir / f"state_object_turn_{turn_index:03d}.json"
        write_json(state_path, state_payload)
        baton_payload = build_baton_pass(
            run_id=run_id,
            turn_index=turn_index,
            next_model_id=model,
            adversarial_role=turn["role"],
            focus_area=turn["objective"],
            unresolved_tensions=state_payload["unresolved_tensions"],
            state_hash=state_hash,
            retrieved_artifact_ids=retrieved_ids,
            final=final,
        )
        baton_hash = sha_text(json.dumps(baton_payload, sort_keys=True))
        baton_path = condition_dir / f"baton_pass_turn_{turn_index:03d}.json"
        write_json(baton_path, baton_payload)
        prompt_card_path = save_prompt_card(
            condition_dir,
            call_id="holo_final_synthesis" if final else f"holo_turn_{turn_index:03d}",
            provider_model_name=provider_model_name,
            system=holo_synthesis_system_prompt() if final else holo_turn_system_prompt(turn["role"]),
            user=holo_architecture_user_prompt(
                packet_dir=packet_dir,
                state_object=state_payload,
                state_hash=state_hash,
                baton_pass=baton_payload,
                baton_hash=baton_hash,
                registry=registry,
                retrieved_entries=retrieved_entries,
                objective=turn["objective"],
                final=final,
            ),
            call_type="holo_final_synthesis" if final else "holo_reviewer_turn",
            role=turn["role"],
            turn_index=turn_index,
        )
        prompt_card_hash = sha_file(prompt_card_path)
        text = (
            f"Smoke {turn['role']} output cites S1_FDA_PULSE_OX_PAGE_2025. "
            "It names evidence, source limits, weak assumptions, missing links, contradictory uncertainty, "
            "operational options, risk tradeoffs, unsupported overclaim controls, and claim boundaries."
        )
        if final:
            final_sentence = (
                "What is happening: smoke brief cites S1_FDA_PULSE_OX_PAGE_2025. "
                "Why it matters now: leaders face capacity pressure. "
                "Strong evidence: source evidence is bounded. "
                "Weak and contradictory evidence: uncertainty and stale claims remain. "
                "Calculation checks: data interpretation is required. "
                "Options: pilot, delay, adopt narrowly, or reject. "
                "Risks of acting: unsupported scale. "
                "Risks of waiting: missed monitoring benefit. "
                "Next steps: validate workflow. "
                "Claim boundaries: no capacity solution or regulatory clearance claim. "
            )
            text = " ".join([final_sentence] * 18)
        artifact_path = condition_dir / ("artifact.md" if final else f"turn_artifacts/turn_{turn_index:03d}.md")
        write_text(artifact_path, text + "\n")
        artifact_record = artifact_entry(
            artifact_id="final_synthesis_artifact" if final else f"turn_{turn_index:03d}_{turn['role']}",
            artifact_type="final_artifact" if final else "reviewer_turn_artifact",
            text=text,
            path=artifact_path,
            role=turn["role"],
        )
        role_result = role_compliance(text, role=turn["role"], final=final)
        audit_result = state_audit(
            text,
            packet_dir=packet_dir,
            state_object=state_payload,
            registry=registry,
            prompt_card_hash=prompt_card_hash,
        )
        final_registry = registry + [artifact_record]
        turn_records.append(
            {
                "turn_index": turn_index,
                "state_object_hash": state_hash,
                "state_object_path": state_path,
                "baton_pass_hash": baton_hash,
                "baton_pass_path": baton_path,
                "selected_model": {"provider": provider, "exact_model_id": model, "endpoint": endpoint_for_provider(provider)},
                "adversarial_role": turn["role"],
                "role_compliance_result": role_result,
                "state_audit_constraint_preservation_result": audit_result,
                "synthesis_trigger": {"triggered": final, "reason": "no_provider_smoke_final_turn_slot" if final else None},
                "token_budget_partial_injection_flags": {
                    "present": True,
                    "token_budget_limit": int(turn["max_tokens"]),
                    "tokens_used": 0,
                    "partial_injection_used": False,
                    "partial_injection_reason": None,
                },
                "artifact_record": artifact_record,
                "artifact_registry_entries": schema_registry_entries(registry),
                "artifact_registry_hash": registry_hash(registry),
                "artifact_registry_after_hash": registry_hash(final_registry) if final else registry_hash(registry),
                "pinned_source_hashes": [item["artifact_hash"] for item in retrieved_entries if item["artifact_type"].startswith("frozen_")],
                "pinned_artifact_hashes": pinned_artifact_hashes_from_retrieval(retrieved_entries),
                "retrieved_artifact_ids": retrieved_ids,
                "prompt_card_hash": prompt_card_hash,
            }
        )
        if not final:
            registry.append(artifact_record)
            prior_artifact_ids.append(artifact_record["artifact_id"])
            prior_hashes.append(artifact_record["artifact_hash"])
            prior_audit_results.append(
                {
                    "turn_index": turn_index,
                    "role": turn["role"],
                    "status": audit_result["state_audit_status"],
                    "evidence_hash_or_location": audit_result["evidence_hash_or_location"],
                }
            )
    return build_live_arch_evidence(
        packet_dir=packet_dir,
        run_id=run_id,
        condition_dir=condition_dir,
        turn_records=turn_records,
        final_artifact_path=condition_dir / "artifact.md",
        final_artifact_text=(condition_dir / "artifact.md").read_text(encoding="utf-8"),
    )


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
            retrieve_evidence = (turn.get("retrieve_by_id_or_source_reference_behavior") or {}).get("evidence_hash_or_location", "")
            audit_evidence = (turn.get("state_audit_constraint_preservation_result") or {}).get("evidence_hash_or_location", "")
            turn_index = int(turn.get("turn_index") or 0)
            state_path_value = turn.get("state_object_snapshot_path")
            prompt_hashes = re.findall(r"prompt_card_sha256:([a-f0-9]{64})", f"{retrieve_evidence};{audit_evidence}")
            if "prompt_card_sha256:" not in retrieve_evidence:
                errors.append(f"arch evidence turn {turn.get('turn_index')} missing prompt hash on retrieved IDs")
            if "prompt_card_sha256:" not in audit_evidence:
                errors.append(f"arch evidence turn {turn.get('turn_index')} missing prompt hash on state audit")
            if state_path_value:
                prompt_name = "holo_final_synthesis.json" if turn_index == EXPECTED_TURN_COUNT else f"holo_turn_{turn_index:03d}.json"
                prompt_path = Path(state_path_value).parent / "prompt_cards" / prompt_name
                if not prompt_path.exists():
                    errors.append(f"arch evidence turn {turn_index} missing saved prompt card: {prompt_path}")
                else:
                    prompt_hash = sha_file(prompt_path)
                    if not prompt_hashes or any(item != prompt_hash for item in prompt_hashes):
                        errors.append(f"arch evidence turn {turn_index} prompt hash does not match saved prompt card")
                    prompt_card = read_json(prompt_path)
                    prompt_surface = f"{prompt_card.get('system', '')}\n{prompt_card.get('user', '')}"
                    required_markers = [
                        "CANONICAL STATE_OBJECT",
                        "STATE_OBJECT_SHA256",
                        "BATON_PASS",
                        "BATON_PASS_SHA256",
                        "ARTIFACT_REGISTRY",
                        "ARTIFACT_REGISTRY_SHA256",
                        "RETRIEVED PINNED SOURCES AND ARTIFACTS",
                        "gov_notes",
                    ]
                    for marker in required_markers:
                        if marker not in prompt_surface:
                            errors.append(f"arch evidence turn {turn_index} saved prompt card missing {marker}")
                    if turn_index > 1 and "turn_001_initial_decision_brief_drafter" not in prompt_surface:
                        errors.append(f"arch evidence turn {turn_index} missing previous registered artifact ID in prompt card")
                    if prompt_card.get("judge_visible") is not False:
                        errors.append(f"arch evidence turn {turn_index} prompt card is judge-visible")
            if (turn.get("role_compliance_result") or {}).get("status") == "not_checked":
                errors.append(f"arch evidence turn {turn.get('turn_index')} used placeholder role compliance")
            if audit_evidence.startswith(turn.get("state_object_hash", "")):
                errors.append(f"arch evidence turn {turn.get('turn_index')} used shallow state hash audit only")
            if "retrieved_ids:" not in retrieve_evidence:
                errors.append(f"arch evidence turn {turn.get('turn_index')} missing retrieved artifact IDs")
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


def source_ids(packet_dir: Path) -> list[str]:
    packet = read_json(packet_dir / "source_packet.json")
    return [item["source_id"] for item in packet.get("sources", [])]


def base_registry(packet_dir: Path) -> list[dict[str, Any]]:
    packet = read_json(packet_dir / "source_packet.json")
    registry: list[dict[str, Any]] = [
        {
            "artifact_id": "TASK_BRIEF",
            "artifact_type": "frozen_task_brief",
            "artifact_hash": sha_file(packet_dir / "task_brief.md"),
            "source_refs": ["task_brief.md"],
            "content_excerpt": excerpt(task_brief_text(packet_dir), 2200),
        },
        {
            "artifact_id": "SOURCE_PACKET_MD",
            "artifact_type": "frozen_source_packet_markdown",
            "artifact_hash": sha_file(packet_dir / "source_packet.md"),
            "source_refs": ["source_packet.md"],
            "content_excerpt": "Model-visible source packet rendered from frozen JSON.",
        },
    ]
    for item in packet.get("sources", []):
        registry.append(
            {
                "artifact_id": item["source_id"],
                "artifact_type": "frozen_source_excerpt",
                "artifact_hash": item["source_hash"],
                "source_refs": [item.get("url_or_citation", ""), item.get("publisher", "")],
                "title": item.get("source_title", ""),
                "publisher": item.get("publisher", ""),
                "date": item.get("publication_or_content_date", ""),
                "provenance_note": item.get("provenance_note", ""),
                "recency_status": item.get("recency_status", ""),
                "contestant_use_note": item.get("contestant_use_note", ""),
                "content_excerpt": item.get("excerpt_text", ""),
            }
        )
    return registry


def registry_hash(registry: list[dict[str, Any]]) -> str:
    return sha_text(stable_json(registry))


def schema_registry_entries(registry: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "artifact_id": item["artifact_id"],
            "artifact_type": item["artifact_type"],
            "artifact_hash": item["artifact_hash"],
            "source_refs": item.get("source_refs", []),
        }
        for item in registry
    ]


def registry_lookup(registry: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["artifact_id"]: item for item in registry}


def retrieve_registry_entries(registry: list[dict[str, Any]], artifact_ids: list[str]) -> list[dict[str, Any]]:
    by_id = registry_lookup(registry)
    missing = [artifact_id for artifact_id in artifact_ids if artifact_id not in by_id]
    if missing:
        raise RuntimeError(f"missing registry artifact ids: {missing}")
    return [by_id[artifact_id] for artifact_id in artifact_ids]


def retrieved_evidence_block(entries: list[dict[str, Any]]) -> str:
    blocks = []
    for item in entries:
        blocks.append(
            "\n".join(
                [
                    f"ID: {item['artifact_id']}",
                    f"TYPE: {item['artifact_type']}",
                    f"HASH: {item['artifact_hash']}",
                    f"SOURCE_REFS: {', '.join(item.get('source_refs', []))}",
                    f"TITLE: {item.get('title', '')}",
                    f"PROVENANCE: {item.get('provenance_note', '')}",
                    f"CONTENT: {item.get('content_excerpt', '')}",
                ]
            )
        )
    return "\n\n---\n\n".join(blocks)


def pinned_artifact_hashes_from_retrieval(entries: list[dict[str, Any]]) -> list[str]:
    hashes = [item["artifact_hash"] for item in entries if item["artifact_type"].endswith("_artifact")]
    return hashes or [sha_text("NO_PRIOR_ARTIFACTS_RETRIEVED")]


def artifact_entry(*, artifact_id: str, artifact_type: str, text: str, path: Path, role: str) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "artifact_hash": sha_text(text),
        "source_refs": [str(path)],
        "role": role,
        "content_excerpt": excerpt(text, 3000),
    }


def critical_constraints() -> list[str]:
    return [
        "use only frozen packet sources",
        "do not browse",
        "cite source IDs for factual claims",
        "main artifact body must be 900-1300 words",
        "target final artifact body length is 1100 words",
        "if a draft exceeds 1300 body words, revise shorter before final answer",
        "do not overclaim capacity solution, FDA approval, or clinical proof",
        "architecture evidence is not judge-visible",
    ]


def gov_notes_for_turn(
    *,
    turn_index: int,
    role: str,
    objective: str,
    prior_audit_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "turn_index": turn_index,
        "governor_directive": "Preserve source boundaries, surface unresolved tensions, and force the assigned adversarial role to produce usable evidence for synthesis.",
        "role_focus": role,
        "objective": objective,
        "prior_audit_results": prior_audit_results[-3:],
    }


def unresolved_tensions_for_turn(prior_audit_results: list[dict[str, Any]]) -> list[str]:
    tensions = [
        "remote pulse-ox monitoring may help triage, but the frozen packet does not prove it solves hospital capacity",
        "FDA safety guidance and advisory material must not be overstated as final approval",
        "stale, preprint, vendor, and limited evidence must be bounded",
    ]
    for item in prior_audit_results[-3:]:
        if item.get("status") == "fail":
            tensions.append(f"prior turn audit issue: {item.get('evidence_hash_or_location')}")
    return tensions


def build_state_object(
    *,
    packet_dir: Path,
    run_id: str,
    turn_index: int,
    role: str,
    objective: str,
    registry: list[dict[str, Any]],
    prior_artifact_hashes: list[str],
    prior_audit_results: list[dict[str, Any]],
) -> dict[str, Any]:
    hashes = packet_hash_bundle(packet_dir)
    return {
        "state_object_type": "BUILD_STATE_OBJECT",
        "run_id": run_id,
        "packet_id": read_json(packet_dir / "source_packet.json")["packet_id"],
        "turn_index": turn_index,
        "selected_role": role,
        "turn_objective": objective,
        "gov_notes": gov_notes_for_turn(
            turn_index=turn_index,
            role=role,
            objective=objective,
            prior_audit_results=prior_audit_results,
        ),
        "critical_constraints": critical_constraints(),
        "source_boundaries": {
            "allowed_source_ids": source_ids(packet_dir),
            "no_external_sources": True,
            "contestants_may_browse": False,
            "forbidden_overclaims": list(FORBIDDEN_SOURCE_BOUNDARY_CLAIMS),
        },
        "settled_decisions": [
            {
                "decision_id": "packet_frozen_before_generation",
                "decision_hash_or_location": hashes["packet_lock"],
            },
            {
                "decision_id": "d5_mini_word_gate_900_1300",
                "decision_hash_or_location": sha_file(packet_dir / "deterministic_gate_policy.json"),
            },
            {
                "decision_id": "architecture_evidence_internal_only",
                "decision_hash_or_location": "architecture_evidence_visible_to_judges=false",
            },
        ],
        "unresolved_tensions": unresolved_tensions_for_turn(prior_audit_results),
        "artifact_registry": schema_registry_entries(registry),
        "artifact_registry_hash": registry_hash(registry),
        "pinned_hashes": hashes,
        "prior_artifact_hashes": prior_artifact_hashes,
    }


def build_baton_pass(
    *,
    run_id: str,
    turn_index: int,
    next_model_id: str,
    adversarial_role: str,
    focus_area: str,
    unresolved_tensions: list[str],
    state_hash: str,
    retrieved_artifact_ids: list[str],
    final: bool,
) -> dict[str, Any]:
    return {
        "baton_pass_type": "BATON_PASS",
        "run_id": run_id,
        "turn_index": turn_index,
        "next_model": next_model_id,
        "adversarial_role": adversarial_role,
        "focus_area": focus_area,
        "unresolved_tensions": unresolved_tensions,
        "required_output_behavior": [
            "cite frozen source IDs",
            "produce role-specific critique or synthesis, not generic praise",
            "preserve action boundaries and claim boundaries",
            "return final 900-1300 word crisis brief only" if final else "do not write the final brief on this turn",
        ],
        "retrieved_artifact_ids": retrieved_artifact_ids,
        "state_object_hash": state_hash,
    }


def holo_architecture_user_prompt(
    *,
    packet_dir: Path,
    state_object: dict[str, Any],
    state_hash: str,
    baton_pass: dict[str, Any],
    baton_hash: str,
    registry: list[dict[str, Any]],
    retrieved_entries: list[dict[str, Any]],
    objective: str,
    final: bool,
    registry_payload: Any | None = None,
    registry_hash_override: str | None = None,
) -> str:
    output_instruction = final_artifact_instruction() if final else "This is an adversarial architecture turn. Do not write the final brief."
    registry_visible_payload = registry_payload if registry_payload is not None else schema_registry_entries(registry)
    registry_visible_hash = registry_hash_override or registry_hash(registry)
    return (
        "CANONICAL STATE_OBJECT\n"
        "======================\n"
        f"STATE_OBJECT_SHA256: {state_hash}\n"
        f"{stable_json(state_object)}\n\n"
        "BATON_PASS\n"
        "==========\n"
        f"BATON_PASS_SHA256: {baton_hash}\n"
        f"{stable_json(baton_pass)}\n\n"
        "ARTIFACT_REGISTRY\n"
        "=================\n"
        f"ARTIFACT_REGISTRY_SHA256: {registry_visible_hash}\n"
        f"{stable_json(registry_visible_payload)}\n\n"
        "RETRIEVED PINNED SOURCES AND ARTIFACTS\n"
        "======================================\n"
        f"{retrieved_evidence_block(retrieved_entries)}\n\n"
        "FROZEN TASK BRIEF\n"
        "=================\n"
        f"{task_brief_text(packet_dir).strip()}\n\n"
        "CURRENT TURN OBJECTIVE\n"
        "======================\n"
        f"{objective}\n\n"
        f"{output_instruction}"
    )


def governor_system_prompt() -> str:
    return (
        "You are the HoloBuild Context Governor for a frozen D5 mini scout packet. "
        "Return strict JSON only. You manage canonical state, artifact registry, baton passing, "
        "role compliance, and state-audit evidence. Do not write the final artifact. "
        "Use only frozen packet metadata and registered artifacts supplied in the prompt."
    )


def governor_prompt(
    *,
    packet_dir: Path,
    call_type: str,
    run_id: str,
    turn_index: int | None,
    next_turn: dict[str, Any] | None,
    registry: list[dict[str, Any]],
    prior_state: dict[str, Any] | None,
    prior_baton: dict[str, Any] | None,
    generation_artifact: dict[str, Any] | None,
    role_result: dict[str, Any] | None,
    audit_result: dict[str, Any] | None,
    final: bool = False,
) -> str:
    return (
        "FULL_GOV_V4 GOVERNOR CALL\n"
        "=========================\n"
        f"call_type: {call_type}\n"
        f"run_id: {run_id}\n"
        f"turn_index: {turn_index}\n"
        f"packet_hash: {sha_file(packet_dir / 'source_packet.json')}\n\n"
        "FROZEN PACKET HASH BUNDLE\n"
        "=========================\n"
        f"{stable_json(packet_hash_bundle(packet_dir))}\n\n"
        "CURRENT LOCKED ARTIFACT REGISTRY STORE\n"
        "======================================\n"
        f"{stable_json(schema_registry_entries(registry))}\n\n"
        "PRIOR GOVERNOR STATE\n"
        "====================\n"
        f"{stable_json(prior_state or {})}\n\n"
        "PRIOR BATON_PASS\n"
        "================\n"
        f"{stable_json(prior_baton or {})}\n\n"
        "GENERATION ARTIFACT FOR AUDIT\n"
        "=============================\n"
        f"{stable_json(generation_artifact or {})}\n\n"
        "RUNNER-OBSERVED ROLE COMPLIANCE RESULT\n"
        "======================================\n"
        f"{stable_json(role_result or {})}\n\n"
        "RUNNER-OBSERVED STATE AUDIT RESULT\n"
        "==================================\n"
        f"{stable_json(audit_result or {})}\n\n"
        "NEXT TURN ROUTING REQUEST\n"
        "=========================\n"
        f"{stable_json(next_turn or {})}\n\n"
        "REQUIRED JSON OUTPUT SCHEMA\n"
        "===========================\n"
        "{\n"
        '  "governor_call_type": "init|update|final_audit",\n'
        '  "mode": "full_gov_v4",\n'
        '  "source": "provider_output",\n'
        '  "proof_credit_eligible": true,\n'
        '  "state_object_source": "governor_output",\n'
        '  "baton_pass_source": "governor_output",\n'
        '  "artifact_registry_source": "governor_output_or_governor_locked_update",\n'
        '  "state_object": {},\n'
        '  "artifact_registry": [],\n'
        '  "pinned_registry_updates": [],\n'
        '  "baton_pass": {},\n'
        '  "gov_notes": {},\n'
        '  "unresolved_tensions": [],\n'
        '  "role_compliance_result": {},\n'
        '  "state_audit_result": {},\n'
        '  "next_turn_routing": {},\n'
        '  "evidence_lock_result": {"status": "pass|fail", "reason": ""}\n'
        "}\n\n"
        "For init, produce the state and BATON_PASS for turn 1. "
        "For update, audit the just-completed generation turn and produce the next-turn state/BATON_PASS unless final=true. "
        "For final_audit, lock the evidence and fail if any Gov call, state, registry, baton, prompt hash, or final artifact hash is missing. "
        f"final_audit_requested: {final}"
    )


def parse_governor_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"governor_output_not_strict_json: {exc}") from exc
    required = {
        "governor_call_type",
        "mode",
        "source",
        "proof_credit_eligible",
        "state_object_source",
        "baton_pass_source",
        "artifact_registry_source",
        "state_object",
        "artifact_registry",
        "baton_pass",
        "gov_notes",
        "unresolved_tensions",
        "role_compliance_result",
        "state_audit_result",
        "next_turn_routing",
        "evidence_lock_result",
    }
    missing = sorted(required - set(payload))
    if missing:
        raise RuntimeError(f"governor_output_missing_required_fields:{missing}")
    if payload["mode"] != HOLO_MODE_FULL_GOV_V4:
        raise RuntimeError("governor_output_wrong_mode")
    if payload["state_object_source"] != "governor_output":
        raise RuntimeError("governor_output_state_not_governor_sourced")
    if payload["baton_pass_source"] != "governor_output":
        raise RuntimeError("governor_output_baton_not_governor_sourced")
    if payload["artifact_registry_source"] != "governor_output_or_governor_locked_update":
        raise RuntimeError("governor_output_registry_not_governor_sourced")
    return payload


def synthetic_governor_output(
    *,
    packet_dir: Path,
    run_id: str,
    call_type: str,
    turn_index: int | None,
    next_turn: dict[str, Any] | None,
    registry: list[dict[str, Any]],
    prior_artifact_hashes: list[str],
    prior_audit_results: list[dict[str, Any]],
    generation_artifact: dict[str, Any] | None,
    role_result: dict[str, Any] | None,
    audit_result: dict[str, Any] | None,
    final: bool = False,
) -> dict[str, Any]:
    if next_turn:
        provider, model = provider_model(next_turn["provider_model"])
        role = next_turn["role"]
        objective = next_turn["objective"]
        turn_number = int(next_turn["turn_index"])
    else:
        provider, model = provider_model(GOVERNOR_PROVIDER_MODEL)
        role = "governor_final_audit"
        objective = "Lock final architecture evidence."
        turn_number = int(turn_index or EXPECTED_TURN_COUNT)
    state_payload = build_state_object(
        packet_dir=packet_dir,
        run_id=run_id,
        turn_index=turn_number,
        role=role,
        objective=objective,
        registry=registry,
        prior_artifact_hashes=prior_artifact_hashes,
        prior_audit_results=prior_audit_results,
    )
    state_payload["state_object_source"] = "governor_output"
    state_payload["full_gov_v4"] = {
        "governor_call_type": call_type,
        "governor_model_id": model,
        "governor_provider": provider,
        "synthetic_smoke_only": True,
        "proof_credit_eligible": False,
    }
    state_hash = sha_text(json.dumps(state_payload, sort_keys=True))
    retrieval_ids = ["TASK_BRIEF"] + source_ids(packet_dir) + [
        item["artifact_id"]
        for item in registry
        if item["artifact_type"] in {"reviewer_turn_artifact", "final_artifact"}
    ]
    baton_payload = build_baton_pass(
        run_id=run_id,
        turn_index=turn_number,
        next_model_id=model,
        adversarial_role=role,
        focus_area=objective,
        unresolved_tensions=state_payload["unresolved_tensions"],
        state_hash=state_hash,
        retrieved_artifact_ids=retrieval_ids,
        final=final,
    )
    baton_payload["baton_pass_source"] = "governor_output"
    return {
        "governor_call_type": call_type,
        "mode": HOLO_MODE_FULL_GOV_V4,
        "source": "no_provider_smoke_only",
        "proof_credit_eligible": False,
        "state_object_source": "governor_output",
        "baton_pass_source": "governor_output",
        "artifact_registry_source": "governor_output_or_governor_locked_update",
        "state_object": state_payload,
        "artifact_registry": schema_registry_entries(registry),
        "pinned_registry_updates": schema_registry_entries(registry[-1:]) if generation_artifact else [],
        "baton_pass": baton_payload,
        "gov_notes": state_payload["gov_notes"],
        "unresolved_tensions": state_payload["unresolved_tensions"],
        "role_compliance_result": role_result or {"status": "not_applicable_init"},
        "state_audit_result": audit_result or {"state_audit_status": "not_applicable_init"},
        "next_turn_routing": {
            "turn_index": turn_number,
            "selected_model": model,
            "provider": provider,
            "adversarial_role": role,
            "focus_area": objective,
        },
        "evidence_lock_result": {
            "status": "pass" if final else "not_final",
            "reason": "synthetic no-provider smoke evidence is diagnostic-only and never proof-credit eligible",
        },
    }


def governor_output_hash(payload: dict[str, Any]) -> str:
    return sha_text(json.dumps(payload, sort_keys=True))


def governor_state_hash(payload: dict[str, Any]) -> str:
    return sha_text(json.dumps(payload["state_object"], sort_keys=True))


def governor_baton_hash(payload: dict[str, Any]) -> str:
    return sha_text(json.dumps(payload["baton_pass"], sort_keys=True))


def governor_registry_hash(payload: dict[str, Any]) -> str:
    return sha_text(json.dumps(payload["artifact_registry"], sort_keys=True))


def save_governor_output(condition_dir: Path, *, call_id: str, payload: dict[str, Any]) -> Path:
    path = condition_dir / "gov_outputs" / f"{call_id}.json"
    write_json(path, payload)
    return path


def save_governor_smoke_trace(
    condition_dir: Path,
    *,
    call_id: str,
    prompt_card_path: Path,
    output_path: Path,
    payload: dict[str, Any],
    turn_index: int | None,
) -> dict[str, Any]:
    trace = {
        "call_id": call_id,
        "call_type": payload["governor_call_type"],
        "role": "context_governor",
        "turn_index": turn_index,
        "provider": "no_provider_smoke",
        "model": GOVERNOR_PROVIDER_MODEL,
        "endpoint": "no_provider_smoke",
        "prompt_card_path": str(prompt_card_path),
        "artifact_path": str(output_path),
        "artifact_sha256": governor_output_hash(payload),
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_ms": 0,
        "http_status": "no_provider_smoke",
        "response_id": "no_provider_smoke_only",
        "created_at_utc": utc_iso(),
        "judge_visible": False,
        "proof_credit_eligible": False,
    }
    write_json(condition_dir / "traces" / f"{call_id}.json", trace)
    return trace


def save_generation_smoke_trace(
    condition_dir: Path,
    *,
    call_id: str,
    provider_model_name: str,
    call_type: str,
    role: str,
    turn_index: int,
    prompt_card_path: Path,
    artifact_path: Path,
    artifact_text: str,
) -> dict[str, Any]:
    provider, model = provider_model(provider_model_name)
    trace = {
        "call_id": call_id,
        "call_type": call_type,
        "role": role,
        "turn_index": turn_index,
        "provider": "no_provider_smoke",
        "planned_provider": provider,
        "model": model,
        "endpoint": "no_provider_smoke",
        "prompt_card_path": str(prompt_card_path),
        "artifact_path": str(artifact_path),
        "artifact_sha256": sha_text(artifact_text),
        "input_tokens": 0,
        "output_tokens": 0,
        "latency_ms": 0,
        "http_status": "no_provider_smoke",
        "response_id": "no_provider_smoke_only",
        "created_at_utc": utc_iso(),
        "judge_visible": False,
        "proof_credit_eligible": False,
    }
    write_json(condition_dir / "traces" / f"{call_id}.json", trace)
    return trace


def call_governor(
    condition_dir: Path,
    *,
    packet_dir: Path,
    run_id: str,
    call_id: str,
    call_type: str,
    turn_index: int | None,
    next_turn: dict[str, Any] | None,
    registry: list[dict[str, Any]],
    prior_state: dict[str, Any] | None,
    prior_baton: dict[str, Any] | None,
    prior_artifact_hashes: list[str],
    prior_audit_results: list[dict[str, Any]],
    generation_artifact: dict[str, Any] | None,
    role_result: dict[str, Any] | None,
    audit_result: dict[str, Any] | None,
    timeout: int,
    live: bool,
    final: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    prompt = governor_prompt(
        packet_dir=packet_dir,
        call_type=call_type,
        run_id=run_id,
        turn_index=turn_index,
        next_turn=next_turn,
        registry=registry,
        prior_state=prior_state,
        prior_baton=prior_baton,
        generation_artifact=generation_artifact,
        role_result=role_result,
        audit_result=audit_result,
        final=final,
    )
    if live:
        raw_text, trace = call_live_model(
            condition_dir,
            provider_model_name=GOVERNOR_PROVIDER_MODEL,
            system=governor_system_prompt(),
            user=prompt,
            max_tokens=3600,
            timeout=timeout,
            call_type=call_type,
            role="context_governor",
            turn_index=turn_index,
            call_id=call_id,
            artifact_path=condition_dir / "gov_outputs" / f"{call_id}.raw.txt",
        )
        payload = parse_governor_json(raw_text)
        output_path = save_governor_output(condition_dir, call_id=call_id, payload=payload)
        trace["artifact_path"] = str(output_path)
        trace["artifact_sha256"] = governor_output_hash(payload)
        write_json(condition_dir / "traces" / f"{call_id}.json", trace)
        return payload, trace

    payload = synthetic_governor_output(
        packet_dir=packet_dir,
        run_id=run_id,
        call_type=call_type,
        turn_index=turn_index,
        next_turn=next_turn,
        registry=registry,
        prior_artifact_hashes=prior_artifact_hashes,
        prior_audit_results=prior_audit_results,
        generation_artifact=generation_artifact,
        role_result=role_result,
        audit_result=audit_result,
        final=final,
    )
    prompt_card_path = save_prompt_card(
        condition_dir,
        call_id=call_id,
        provider_model_name=GOVERNOR_PROVIDER_MODEL,
        system=governor_system_prompt(),
        user=prompt,
        call_type=call_type,
        role="context_governor",
        turn_index=turn_index,
    )
    output_path = save_governor_output(condition_dir, call_id=call_id, payload=payload)
    trace = save_governor_smoke_trace(
        condition_dir,
        call_id=call_id,
        prompt_card_path=prompt_card_path,
        output_path=output_path,
        payload=payload,
        turn_index=turn_index,
    )
    return payload, trace


def required_env_for_conditions(conditions: list[str], *, holo_mode: str = HOLO_MODE_DIAGNOSTIC_V3) -> list[str]:
    provider_models: list[str] = []
    if "solo_openai_gpt_5_5" in conditions:
        provider_models.append(SOLO_PROVIDER_MODEL)
    if "holo_build_arch" in conditions:
        provider_models.extend(expected_holobuild_provider_models(holo_mode))
    envs: list[str] = []
    for provider_model_name in provider_models:
        provider, _ = provider_model(provider_model_name)
        env = PROVIDER_ENV[provider]
        if env not in envs:
            envs.append(env)
    return envs


def ensure_env_available(conditions: list[str], *, holo_mode: str = HOLO_MODE_DIAGNOSTIC_V3) -> None:
    required = required_env_for_conditions(conditions, holo_mode=holo_mode)
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


def role_compliance(text: str, *, role: str, final: bool = False) -> dict[str, str]:
    lower = text.lower()
    defects: list[str] = []
    if not text.strip():
        defects.append("empty_output")
    if not SOURCE_ID_RE.search(text):
        defects.append("missing_source_id_references")
    required_terms = ROLE_BEHAVIOR_TERMS.get(role, ())
    missing_terms = [term for term in required_terms if term not in lower]
    if missing_terms:
        defects.append(f"missing_role_behavior_terms:{','.join(missing_terms)}")
    praise_terms = sum(lower.count(term) for term in ("strong", "useful", "excellent", "good"))
    critique_terms = sum(lower.count(term) for term in ("weak", "risk", "contradict", "uncertain", "unsupported", "limit", "missing"))
    if not final and praise_terms > 2 and critique_terms == 0:
        defects.append("generic_praise_only_pass")
    if final:
        count = word_count(text)
        if not (FINAL_WORD_MIN <= count <= FINAL_WORD_MAX):
            defects.append(f"word_count:{count}")
        missing_sections = [marker for marker in REQUIRED_FINAL_SECTION_MARKERS if marker not in lower]
        if missing_sections:
            defects.append("missing_required_sections:" + ",".join(missing_sections[:5]))
    status = "fail" if defects else "pass"
    evidence = "semantic_role_checks:" + (";".join(defects) if defects else f"source_refs_present_word_count:{word_count(text)}")
    return {"status": status, "evidence_hash_or_location": evidence}


def state_audit(
    text: str,
    *,
    packet_dir: Path,
    state_object: dict[str, Any],
    registry: list[dict[str, Any]],
    prompt_card_hash: str,
) -> dict[str, str]:
    allowed_ids = set(source_ids(packet_dir))
    cited_ids = set(SOURCE_ID_RE.findall(text))
    invented_ids = sorted(cited_ids - allowed_ids)
    lower = text.lower()
    defects: list[str] = []
    if invented_ids:
        defects.append("invented_source_ids:" + ",".join(invented_ids))
    if sha_file(packet_dir / "source_packet.json") not in stable_json(state_object):
        defects.append("packet_hash_missing_from_state_object")
    if not registry or not registry_hash(registry):
        defects.append("source_registry_missing")
    if "no_external_sources" not in stable_json(state_object):
        defects.append("source_boundary_missing_from_state_object")
    forbidden_hits = [claim for claim in FORBIDDEN_SOURCE_BOUNDARY_CLAIMS if claim in lower]
    if forbidden_hits:
        defects.append("source_boundary_contradiction:" + ",".join(forbidden_hits))
    status = "fail" if defects else "pass"
    return {
        "state_audit_status": status,
        "constraint_preservation_status": status,
        "evidence_hash_or_location": (
            f"prompt_card_sha256:{prompt_card_hash};registry_sha256:{registry_hash(registry)};"
            + ("defects:" + ";".join(defects) if defects else "semantic_checks:constraints_preserved")
        ),
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
    for record in turn_records:
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
                        "evidence_hash_or_location": f"prompt_card_sha256:{record['prompt_card_hash']}:use_only_frozen_sources",
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
                "artifact_registry_entries": record["artifact_registry_entries"],
                "artifact_registry_hash": record["artifact_registry_hash"],
                "pinned_source_hashes": record["pinned_source_hashes"],
                "pinned_artifact_hashes": record["pinned_artifact_hashes"],
                "retrieve_by_id_or_source_reference_behavior": {
                    "required": True,
                    "observed": True,
                    "evidence_hash_or_location": (
                        f"prompt_card_sha256:{record['prompt_card_hash']};"
                        f"retrieved_ids:{','.join(record['retrieved_artifact_ids'])}"
                    ),
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
    final_registry_hash = turn_records[-1].get("artifact_registry_after_hash", turn_records[-1]["artifact_registry_hash"])
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


def build_full_gov_v4_arch_evidence(
    *,
    packet_dir: Path,
    run_id: str,
    condition_dir: Path,
    gov_init_record: dict[str, Any],
    gov_update_records: list[dict[str, Any]],
    gov_final_record: dict[str, Any],
    generation_records: list[dict[str, Any]],
    final_artifact_path: Path,
    final_artifact_text: str,
    synthetic_smoke_only: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "holo_build_full_gov_arch_evidence_v4",
        "architecture_policy_id": "HOLOBUILD_PATENT_ALIGNMENT_POLICY_V4_1",
        "run_id": run_id,
        "domain_id": "D5_healthcare_medtech_evidence_synthesis",
        "condition_type": "holo_build_arch",
        "holo_mode": HOLO_MODE_FULL_GOV_V4,
        "proof_credit_class": "no_provider_smoke_only" if synthetic_smoke_only else "full_gov_v4_proof_eligible",
        "synthetic_smoke_only": synthetic_smoke_only,
        "expected_holo_call_count": FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT,
        "provider_calls_recorded": PROVIDER_CALLS,
        "state_object_source": "governor_output",
        "baton_pass_source": "governor_output",
        "artifact_registry_source": "governor_output_or_governor_locked_update",
        "architecture_evidence_visible_to_judges": False,
        "visible_surface_boundary": visible_surface_boundary(),
        "proof_credit_fail_closed_rules": [
            "missing Gov init call = no proof credit",
            "missing any Gov update/audit call = no proof credit",
            "missing Gov final audit = no proof credit",
            "runner-created canonical state without Gov output = no proof credit",
            "generation prompt hash not matching Gov-produced state/baton/registry = no proof credit",
            "Gov final audit fail = no proof credit",
            "architecture evidence visible to judges = no proof credit",
            "synthetic smoke evidence is diagnostic-only and not proof-credit eligible",
        ],
        "gov_init_call": gov_init_record,
        "gov_update_calls": gov_update_records,
        "gov_final_audit_call": gov_final_record,
        "generation_turns": generation_records,
        "final": {
            "final_artifact_hash": sha_text(final_artifact_text),
            "final_artifact_path": str(final_artifact_path),
            "final_artifact_word_count": word_count(final_artifact_text),
            "final_architecture_evidence_lock_status": (
                gov_final_record.get("output", {}).get("evidence_lock_result", {}).get("status")
            ),
            "architecture_evidence_visible_to_judges": False,
        },
    }


def validate_full_gov_v4_arch_evidence(evidence: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if evidence.get("holo_mode") != HOLO_MODE_FULL_GOV_V4:
        errors.append("full_gov_v4 evidence missing holo_mode")
    if evidence.get("architecture_evidence_visible_to_judges") is not False:
        errors.append("architecture evidence is judge-visible")
    if evidence.get("state_object_source") != "governor_output":
        errors.append("state_object_source is not governor_output")
    if evidence.get("baton_pass_source") != "governor_output":
        errors.append("baton_pass_source is not governor_output")
    if evidence.get("artifact_registry_source") != "governor_output_or_governor_locked_update":
        errors.append("artifact_registry_source is not governor locked")
    if evidence.get("expected_holo_call_count") != FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT:
        errors.append("expected Holo call count is not 14")

    gov_init = evidence.get("gov_init_call") or {}
    gov_updates = evidence.get("gov_update_calls") or []
    gov_final = evidence.get("gov_final_audit_call") or {}
    generations = evidence.get("generation_turns") or []
    if not gov_init:
        errors.append("missing Gov init call")
    if len(gov_updates) != EXPECTED_TURN_COUNT:
        errors.append(f"missing Gov update calls: expected {EXPECTED_TURN_COUNT}, got {len(gov_updates)}")
    if not gov_final:
        errors.append("missing Gov final audit call")
    if len(generations) != EXPECTED_TURN_COUNT:
        errors.append(f"generation turn count mismatch: expected {EXPECTED_TURN_COUNT}, got {len(generations)}")

    if evidence.get("synthetic_smoke_only") and evidence.get("proof_credit_class") != "no_provider_smoke_only":
        errors.append("synthetic smoke evidence treated as proof-credit eligible")
    if not evidence.get("synthetic_smoke_only"):
        if gov_final.get("output", {}).get("evidence_lock_result", {}).get("status") != "pass":
            errors.append("Gov final audit did not pass")

    required_prompt_markers = [
        "CANONICAL STATE_OBJECT",
        "STATE_OBJECT_SHA256",
        "BATON_PASS",
        "BATON_PASS_SHA256",
        "ARTIFACT_REGISTRY",
        "ARTIFACT_REGISTRY_SHA256",
        "RETRIEVED PINNED SOURCES AND ARTIFACTS",
        "gov_notes",
    ]
    for turn in generations:
        turn_index = int(turn.get("turn_index") or 0)
        prompt_path = Path(turn.get("prompt_card_path", ""))
        if not prompt_path.exists():
            errors.append(f"generation turn {turn_index} missing prompt card")
            continue
        prompt_hash = sha_file(prompt_path)
        if prompt_hash != turn.get("prompt_card_sha256"):
            errors.append(f"generation turn {turn_index} prompt hash mismatch")
        prompt_card = read_json(prompt_path)
        prompt_surface = f"{prompt_card.get('system', '')}\n{prompt_card.get('user', '')}"
        for marker in required_prompt_markers:
            if marker not in prompt_surface:
                errors.append(f"generation turn {turn_index} prompt card missing {marker}")
        if prompt_card.get("judge_visible") is not False:
            errors.append(f"generation turn {turn_index} prompt card is judge-visible")
        if turn.get("state_object_source") != "governor_output":
            errors.append(f"generation turn {turn_index} state not Gov-produced")
        if turn.get("baton_pass_source") != "governor_output":
            errors.append(f"generation turn {turn_index} baton not Gov-produced")
        if turn.get("artifact_registry_source") != "governor_output_or_governor_locked_update":
            errors.append(f"generation turn {turn_index} registry not Gov-produced")
        if turn.get("state_object_sha256") not in prompt_surface:
            errors.append(f"generation turn {turn_index} Gov state hash not in prompt")
        if turn.get("baton_pass_sha256") not in prompt_surface:
            errors.append(f"generation turn {turn_index} Gov baton hash not in prompt")
        if turn.get("artifact_registry_sha256") not in prompt_surface:
            errors.append(f"generation turn {turn_index} Gov registry hash not in prompt")
        retrieved_ids = turn.get("retrieved_ids") or []
        if not retrieved_ids:
            errors.append(f"generation turn {turn_index} retrieved no pinned IDs")
        if turn_index > 1 and not any(str(item).startswith("turn_001_") for item in retrieved_ids):
            errors.append(f"generation turn {turn_index} missing previous registered artifact ID")

    return errors


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
        "holo_mode": HOLO_MODE_DIAGNOSTIC_V3 if condition == "holo_build_arch" else None,
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


def full_gov_generation_turns() -> list[dict[str, Any]]:
    turns = [dict(item) for item in HOLO_PROVIDER_TURNS]
    turns.append(
        {
            "provider_model": HOLO_SYNTHESIS_MODEL,
            "role": "final_synthesis_author",
            "objective": "Synthesize the final 900-1,300 word decision-grade crisis brief from frozen sources and registered critique artifacts.",
            "max_tokens": 3400,
        }
    )
    for index, item in enumerate(turns, start=1):
        item["turn_index"] = index
        item["final"] = index == EXPECTED_TURN_COUNT
    return turns


def full_gov_smoke_generation_text(role: str, *, final: bool) -> str:
    if final:
        final_sentence = (
            "What is happening: smoke brief cites S1_FDA_PULSE_OX_PAGE_2025 and treats pulse-ox evidence as bounded. "
            "Why it matters now: leaders face capacity pressure but the packet does not prove capacity relief. "
            "Strong evidence: frozen sources support safety and equity concerns. "
            "Weak and contradictory evidence: stale, preprint, and vendor claims remain limited. "
            "Calculation checks: subgroup and table interpretation matter. "
            "Options: pilot, delay, adopt narrowly, or reject. "
            "Risks of acting: unsupported scale and overclaiming. "
            "Risks of waiting: missed monitoring workflow benefit. "
            "Next steps: validate operations before adoption. "
            "Claim boundaries: no capacity solution or regulatory approval claim. "
        )
        return " ".join([final_sentence] * 12)
    return (
        f"Smoke {role} output cites S1_FDA_PULSE_OX_PAGE_2025. "
        "It names weak evidence, source limits, missing assumptions, contradictions, uncertainty, "
        "operational options, risk tradeoffs, unsupported overclaim controls, and claim boundaries."
    )


def run_holobuild_full_gov_v4(packet_dir: Path, run_id: str, timeout: int, *, live: bool) -> dict[str, Any]:
    condition = "holo_build_arch"
    condition_dir = packet_dir / "runs" / run_id / condition
    condition_dir.mkdir(parents=True, exist_ok=True)

    registry = base_registry(packet_dir)
    prior_hashes: list[str] = []
    prior_audit_results: list[dict[str, Any]] = []
    generation_records: list[dict[str, Any]] = []
    generation_traces: list[dict[str, Any]] = []
    governor_traces: list[dict[str, Any]] = []
    gov_update_records: list[dict[str, Any]] = []
    turns = full_gov_generation_turns()

    current_gov, gov_init_trace = call_governor(
        condition_dir,
        packet_dir=packet_dir,
        run_id=run_id,
        call_id="gov_init",
        call_type="gov_init",
        turn_index=1,
        next_turn=turns[0],
        registry=registry,
        prior_state=None,
        prior_baton=None,
        prior_artifact_hashes=prior_hashes,
        prior_audit_results=prior_audit_results,
        generation_artifact=None,
        role_result=None,
        audit_result=None,
        timeout=timeout,
        live=live,
    )
    governor_traces.append(gov_init_trace)
    gov_init_record = {
        "call_id": "gov_init",
        "call_type": "gov_init",
        "governor_model_id": provider_model(GOVERNOR_PROVIDER_MODEL)[1],
        "prompt_card_path": gov_init_trace["prompt_card_path"],
        "prompt_card_sha256": sha_file(Path(gov_init_trace["prompt_card_path"])),
        "output_path": gov_init_trace["artifact_path"],
        "output_sha256": governor_output_hash(current_gov),
        "input_tokens": int(gov_init_trace.get("input_tokens") or 0),
        "output_tokens": int(gov_init_trace.get("output_tokens") or 0),
        "output": current_gov,
    }

    for turn in turns:
        turn_index = int(turn["turn_index"])
        final = bool(turn["final"])
        provider_model_name = turn["provider_model"]
        state_payload = current_gov["state_object"]
        baton_payload = current_gov["baton_pass"]
        gov_registry_payload = current_gov["artifact_registry"]
        state_hash = governor_state_hash(current_gov)
        baton_hash = governor_baton_hash(current_gov)
        gov_registry_hash = governor_registry_hash(current_gov)
        state_path = condition_dir / f"state_object_turn_{turn_index:03d}.json"
        baton_path = condition_dir / f"baton_pass_turn_{turn_index:03d}.json"
        write_json(state_path, state_payload)
        write_json(baton_path, baton_payload)

        retrieved_ids = baton_payload.get("retrieved_artifact_ids") or []
        if not retrieved_ids:
            raise RuntimeError(f"Gov BATON_PASS missing retrieved_artifact_ids for turn {turn_index}")
        retrieved_entries = retrieve_registry_entries(registry, retrieved_ids)
        call_id = "holo_final_synthesis" if final else f"holo_turn_{turn_index:03d}"
        artifact_path = condition_dir / "artifact.md" if final else condition_dir / "turn_artifacts" / f"turn_{turn_index:03d}.md"
        system = holo_synthesis_system_prompt() if final else holo_turn_system_prompt(turn["role"])
        user = holo_architecture_user_prompt(
            packet_dir=packet_dir,
            state_object=state_payload,
            state_hash=state_hash,
            baton_pass=baton_payload,
            baton_hash=baton_hash,
            registry=registry,
            retrieved_entries=retrieved_entries,
            objective=turn["objective"],
            final=final,
            registry_payload=gov_registry_payload,
            registry_hash_override=gov_registry_hash,
        )

        if live:
            text, trace = call_live_model(
                condition_dir,
                provider_model_name=provider_model_name,
                system=system,
                user=user,
                max_tokens=int(turn["max_tokens"]),
                timeout=timeout,
                call_type="holo_final_synthesis" if final else "holo_reviewer_turn",
                role=turn["role"],
                turn_index=turn_index,
                call_id=call_id,
                artifact_path=artifact_path,
            )
        else:
            prompt_card_path = save_prompt_card(
                condition_dir,
                call_id=call_id,
                provider_model_name=provider_model_name,
                system=system,
                user=user,
                call_type="holo_final_synthesis" if final else "holo_reviewer_turn",
                role=turn["role"],
                turn_index=turn_index,
            )
            text = full_gov_smoke_generation_text(turn["role"], final=final) + "\n"
            write_text(artifact_path, text)
            trace = save_generation_smoke_trace(
                condition_dir,
                call_id=call_id,
                provider_model_name=provider_model_name,
                call_type="holo_final_synthesis" if final else "holo_reviewer_turn",
                role=turn["role"],
                turn_index=turn_index,
                prompt_card_path=prompt_card_path,
                artifact_path=artifact_path,
                artifact_text=text,
            )
        generation_traces.append(trace)
        prompt_card_hash = sha_file(Path(trace["prompt_card_path"]))
        artifact_record = artifact_entry(
            artifact_id="final_synthesis_artifact" if final else f"turn_{turn_index:03d}_{turn['role']}",
            artifact_type="final_artifact" if final else "reviewer_turn_artifact",
            text=text,
            path=artifact_path,
            role=turn["role"],
        )
        role_result = role_compliance(text, role=turn["role"], final=final)
        audit_result = state_audit(
            text,
            packet_dir=packet_dir,
            state_object=state_payload,
            registry=registry,
            prompt_card_hash=prompt_card_hash,
        )
        generation_records.append(
            {
                "turn_index": turn_index,
                "call_id": call_id,
                "provider_model": provider_model_name,
                "state_object_source": current_gov["state_object_source"],
                "baton_pass_source": current_gov["baton_pass_source"],
                "artifact_registry_source": current_gov["artifact_registry_source"],
                "state_object_sha256": state_hash,
                "state_object_path": str(state_path),
                "baton_pass_sha256": baton_hash,
                "baton_pass_path": str(baton_path),
                "artifact_registry_sha256": gov_registry_hash,
                "prompt_card_path": trace["prompt_card_path"],
                "prompt_card_sha256": prompt_card_hash,
                "retrieved_ids": retrieved_ids,
                "retrieved_hashes": [item["artifact_hash"] for item in retrieved_entries],
                "artifact_record": artifact_record,
                "role_compliance_result": role_result,
                "state_audit_result": audit_result,
                "synthesis_trigger": {"triggered": final, "reason": "full_gov_v4_final_turn" if final else None},
                "trace": trace,
            }
        )
        registry.append(artifact_record)
        prior_hashes.append(artifact_record["artifact_hash"])
        prior_audit_results.append(
            {
                "turn_index": turn_index,
                "role": turn["role"],
                "status": audit_result["state_audit_status"],
                "evidence_hash_or_location": audit_result["evidence_hash_or_location"],
            }
        )
        next_turn = turns[turn_index] if turn_index < EXPECTED_TURN_COUNT else None
        update_output, update_trace = call_governor(
            condition_dir,
            packet_dir=packet_dir,
            run_id=run_id,
            call_id=f"gov_update_{turn_index:03d}",
            call_type="gov_update_audit",
            turn_index=turn_index,
            next_turn=next_turn,
            registry=registry,
            prior_state=state_payload,
            prior_baton=baton_payload,
            prior_artifact_hashes=prior_hashes,
            prior_audit_results=prior_audit_results,
            generation_artifact=artifact_record,
            role_result=role_result,
            audit_result=audit_result,
            timeout=timeout,
            live=live,
            final=final,
        )
        governor_traces.append(update_trace)
        gov_update_records.append(
            {
                "call_id": f"gov_update_{turn_index:03d}",
                "call_type": "gov_update_audit",
                "turn_index": turn_index,
                "governor_model_id": provider_model(GOVERNOR_PROVIDER_MODEL)[1],
                "prompt_card_path": update_trace["prompt_card_path"],
                "prompt_card_sha256": sha_file(Path(update_trace["prompt_card_path"])),
                "output_path": update_trace["artifact_path"],
                "output_sha256": governor_output_hash(update_output),
                "input_tokens": int(update_trace.get("input_tokens") or 0),
                "output_tokens": int(update_trace.get("output_tokens") or 0),
                "state_diff": {
                    "previous_state_sha256": state_hash,
                    "next_state_sha256": governor_state_hash(update_output),
                },
                "registry_diff": {
                    "previous_registry_sha256": gov_registry_hash,
                    "next_registry_sha256": governor_registry_hash(update_output),
                    "added_artifact_id": artifact_record["artifact_id"],
                },
                "baton_output_sha256": governor_baton_hash(update_output),
                "audit_outputs": {
                    "role_compliance_result": update_output.get("role_compliance_result"),
                    "state_audit_result": update_output.get("state_audit_result"),
                },
                "output": update_output,
            }
        )
        current_gov = update_output

    final_artifact_path = condition_dir / "artifact.md"
    final_text = final_artifact_path.read_text(encoding="utf-8")
    final_output, final_trace = call_governor(
        condition_dir,
        packet_dir=packet_dir,
        run_id=run_id,
        call_id="gov_final_audit",
        call_type="gov_final_audit",
        turn_index=EXPECTED_TURN_COUNT,
        next_turn=None,
        registry=registry,
        prior_state=current_gov["state_object"],
        prior_baton=current_gov["baton_pass"],
        prior_artifact_hashes=prior_hashes,
        prior_audit_results=prior_audit_results,
        generation_artifact={
            "artifact_id": "final_synthesis_artifact",
            "artifact_hash": sha_text(final_text),
            "artifact_path": str(final_artifact_path),
        },
        role_result=role_compliance(final_text, role="final_synthesis_author", final=True),
        audit_result=state_audit(
            final_text,
            packet_dir=packet_dir,
            state_object=current_gov["state_object"],
            registry=registry,
            prompt_card_hash=sha_file(Path(generation_records[-1]["prompt_card_path"])),
        ),
        timeout=timeout,
        live=live,
        final=True,
    )
    governor_traces.append(final_trace)
    gov_final_record = {
        "call_id": "gov_final_audit",
        "call_type": "gov_final_audit",
        "governor_model_id": provider_model(GOVERNOR_PROVIDER_MODEL)[1],
        "prompt_card_path": final_trace["prompt_card_path"],
        "prompt_card_sha256": sha_file(Path(final_trace["prompt_card_path"])),
        "output_path": final_trace["artifact_path"],
        "output_sha256": governor_output_hash(final_output),
        "input_tokens": int(final_trace.get("input_tokens") or 0),
        "output_tokens": int(final_trace.get("output_tokens") or 0),
        "state_diff": {
            "previous_state_sha256": governor_state_hash(current_gov),
            "locked_state_sha256": governor_state_hash(final_output),
        },
        "registry_diff": {
            "previous_registry_sha256": governor_registry_hash(current_gov),
            "locked_registry_sha256": governor_registry_hash(final_output),
        },
        "baton_output_sha256": governor_baton_hash(final_output),
        "output": final_output,
    }
    evidence = build_full_gov_v4_arch_evidence(
        packet_dir=packet_dir,
        run_id=run_id,
        condition_dir=condition_dir,
        gov_init_record=gov_init_record,
        gov_update_records=gov_update_records,
        gov_final_record=gov_final_record,
        generation_records=generation_records,
        final_artifact_path=final_artifact_path,
        final_artifact_text=final_text,
        synthetic_smoke_only=not live,
    )
    arch_errors = validate_full_gov_v4_arch_evidence(evidence)
    arch_path = condition_dir / "arch_evidence.json"
    write_json(arch_path, evidence)
    all_traces = generation_traces + governor_traces
    metadata = {
        "runner_id": RUNNER_ID,
        "run_mode": RUN_MODE_FULL_GOV_V4,
        "holo_mode": HOLO_MODE_FULL_GOV_V4,
        "run_id": run_id,
        "condition": condition,
        "condition_label": CONDITION_LABELS[condition],
        "status": "live_generation_complete" if live else "planned_no_provider_full_gov_v4_smoke",
        "created_at_utc": utc_iso(),
        "provider_calls": sum(1 for trace in all_traces if trace.get("provider") != "no_provider_smoke"),
        "expected_holo_call_count": FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT,
        "provider_models": expected_holobuild_provider_models(HOLO_MODE_FULL_GOV_V4),
        "scores_generated": SCORES_GENERATED,
        "packet_dir": str(packet_dir),
        "packet_id": read_json(packet_dir / "packet_lock.json")["packet_id"],
        "packet_hash": sha_file(packet_dir / "source_packet.json"),
        "artifact_path": str(final_artifact_path),
        "artifact_written": True,
        "artifact_sha256": sha_text(final_text),
        "artifact_word_count": word_count(final_text),
        "deterministic_gate_status": deterministic_gate_precheck(packet_dir, condition, final_text)["deterministic_gate_status"],
        "architecture_evidence_path": str(arch_path),
        "architecture_evidence_status": "valid" if not arch_errors else "invalid",
        "architecture_evidence_errors": arch_errors,
        "input_tokens": sum(int(trace.get("input_tokens") or 0) for trace in all_traces),
        "output_tokens": sum(int(trace.get("output_tokens") or 0) for trace in all_traces),
        "architecture_evidence_visible_to_judges": False,
        "proof_credit_class": "no_provider_smoke_only" if not live else "full_gov_v4_proof_eligible",
    }
    write_json(condition_dir / "deterministic_gate_precheck.json", deterministic_gate_precheck(packet_dir, condition, final_text))
    write_json(condition_dir / "artifact_metadata.json", metadata)
    return {
        "condition": condition,
        "condition_dir": str(condition_dir),
        "packet_hash": metadata["packet_hash"],
        "artifact_path": str(final_artifact_path),
        "artifact_sha256": metadata["artifact_sha256"],
        "deterministic_gate_precheck": metadata["deterministic_gate_status"],
        "architecture_evidence_status": metadata["architecture_evidence_status"],
        "architecture_evidence_errors": arch_errors,
        "architecture_evidence_path": str(arch_path),
        "provider_calls": metadata["provider_calls"],
        "expected_holo_call_count": FULL_GOV_V4_EXPECTED_HOLO_CALL_COUNT,
        "holo_mode": HOLO_MODE_FULL_GOV_V4,
    }


def run_live_holobuild(packet_dir: Path, run_id: str, timeout: int) -> dict[str, Any]:
    condition = "holo_build_arch"
    condition_dir = packet_dir / "runs" / run_id / condition
    condition_dir.mkdir(parents=True, exist_ok=True)
    turn_records: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    registry = base_registry(packet_dir)
    prior_artifact_ids: list[str] = []
    prior_hashes: list[str] = []
    prior_audit_results: list[dict[str, Any]] = []
    source_retrieval_ids = ["TASK_BRIEF"] + source_ids(packet_dir)

    for index, turn in enumerate(HOLO_PROVIDER_TURNS, start=1):
        provider_model_name = turn["provider_model"]
        provider, model = provider_model(provider_model_name)
        retrieved_ids = source_retrieval_ids + prior_artifact_ids
        retrieved_entries = retrieve_registry_entries(registry, retrieved_ids)
        state_payload = build_state_object(
            packet_dir=packet_dir,
            run_id=run_id,
            turn_index=index,
            role=turn["role"],
            objective=turn["objective"],
            registry=registry,
            prior_artifact_hashes=prior_hashes,
            prior_audit_results=prior_audit_results,
        )
        state_hash = sha_text(json.dumps(state_payload, sort_keys=True))
        state_path = condition_dir / f"state_object_turn_{index:03d}.json"
        write_json(state_path, state_payload)
        baton_payload = build_baton_pass(
            run_id=run_id,
            turn_index=index,
            next_model_id=model,
            adversarial_role=turn["role"],
            focus_area=turn["objective"],
            unresolved_tensions=state_payload["unresolved_tensions"],
            state_hash=state_hash,
            retrieved_artifact_ids=retrieved_ids,
            final=False,
        )
        baton_hash = sha_text(json.dumps(baton_payload, sort_keys=True))
        baton_path = condition_dir / f"baton_pass_turn_{index:03d}.json"
        write_json(baton_path, baton_payload)
        turn_path = condition_dir / "turn_artifacts" / f"turn_{index:03d}.md"
        text, trace = call_live_model(
            condition_dir,
            provider_model_name=provider_model_name,
            system=holo_turn_system_prompt(turn["role"]),
            user=holo_architecture_user_prompt(
                packet_dir=packet_dir,
                state_object=state_payload,
                state_hash=state_hash,
                baton_pass=baton_payload,
                baton_hash=baton_hash,
                registry=registry,
                retrieved_entries=retrieved_entries,
                objective=turn["objective"],
                final=False,
            ),
            max_tokens=int(turn["max_tokens"]),
            timeout=timeout,
            call_type="holo_reviewer_turn",
            role=turn["role"],
            turn_index=index,
            call_id=f"holo_turn_{index:03d}",
            artifact_path=turn_path,
        )
        traces.append(trace)
        prompt_card_hash = sha_file(Path(trace["prompt_card_path"]))
        artifact_hash = sha_text(text)
        prior_hashes.append(artifact_hash)
        artifact_record = artifact_entry(
            artifact_id=f"turn_{index:03d}_{turn['role']}",
            artifact_type="reviewer_turn_artifact",
            text=text,
            path=turn_path,
            role=turn["role"],
        )
        role_result = role_compliance(text, role=turn["role"])
        audit_result = state_audit(
            text,
            packet_dir=packet_dir,
            state_object=state_payload,
            registry=registry,
            prompt_card_hash=prompt_card_hash,
        )
        prior_audit_results.append(
            {
                "turn_index": index,
                "role": turn["role"],
                "status": audit_result["state_audit_status"],
                "evidence_hash_or_location": audit_result["evidence_hash_or_location"],
            }
        )
        turn_records.append(
            {
                "turn_index": index,
                "state_object_hash": state_hash,
                "state_object_path": state_path,
                "baton_pass_hash": baton_hash,
                "baton_pass_path": baton_path,
                "selected_model": {"provider": provider, "exact_model_id": model, "endpoint": endpoint_for_provider(provider)},
                "adversarial_role": turn["role"],
                "role_compliance_result": role_result,
                "state_audit_constraint_preservation_result": audit_result,
                "synthesis_trigger": {"triggered": False, "reason": None},
                "token_budget_partial_injection_flags": {
                    "present": True,
                    "token_budget_limit": int(turn["max_tokens"]),
                    "tokens_used": int(trace.get("output_tokens") or 0),
                    "partial_injection_used": False,
                    "partial_injection_reason": None,
                },
                "artifact_record": artifact_record,
                "artifact_registry_entries": schema_registry_entries(registry),
                "artifact_registry_hash": registry_hash(registry),
                "pinned_source_hashes": [item["artifact_hash"] for item in retrieved_entries if item["artifact_type"].startswith("frozen_")],
                "pinned_artifact_hashes": pinned_artifact_hashes_from_retrieval(retrieved_entries),
                "retrieved_artifact_ids": retrieved_ids,
                "prompt_card_hash": prompt_card_hash,
            }
        )
        registry.append(artifact_record)
        prior_artifact_ids.append(artifact_record["artifact_id"])

    synthesis_index = len(HOLO_PROVIDER_TURNS) + 1
    provider, model = provider_model(HOLO_SYNTHESIS_MODEL)
    retrieved_ids = source_retrieval_ids + prior_artifact_ids
    retrieved_entries = retrieve_registry_entries(registry, retrieved_ids)
    synthesis_state = build_state_object(
        packet_dir=packet_dir,
        run_id=run_id,
        turn_index=synthesis_index,
        role="final_synthesis_author",
        objective="Synthesize the final 900-1,300 word decision-grade crisis brief from frozen sources and reviewer notes.",
        registry=registry,
        prior_artifact_hashes=prior_hashes,
        prior_audit_results=prior_audit_results,
    )
    synthesis_state_hash = sha_text(json.dumps(synthesis_state, sort_keys=True))
    synthesis_state_path = condition_dir / f"state_object_turn_{synthesis_index:03d}.json"
    write_json(synthesis_state_path, synthesis_state)
    synthesis_baton = build_baton_pass(
        run_id=run_id,
        turn_index=synthesis_index,
        next_model_id=model,
        adversarial_role="final_synthesis_author",
        focus_area="Synthesize final artifact under claim-boundary and source-fidelity constraints.",
        unresolved_tensions=synthesis_state["unresolved_tensions"],
        state_hash=synthesis_state_hash,
        retrieved_artifact_ids=retrieved_ids,
        final=True,
    )
    synthesis_baton_hash = sha_text(json.dumps(synthesis_baton, sort_keys=True))
    synthesis_baton_path = condition_dir / f"baton_pass_turn_{synthesis_index:03d}.json"
    write_json(synthesis_baton_path, synthesis_baton)
    artifact_path = condition_dir / "artifact.md"
    final_text, final_trace = call_live_model(
        condition_dir,
        provider_model_name=HOLO_SYNTHESIS_MODEL,
        system=holo_synthesis_system_prompt(),
        user=holo_architecture_user_prompt(
            packet_dir=packet_dir,
            state_object=synthesis_state,
            state_hash=synthesis_state_hash,
            baton_pass=synthesis_baton,
            baton_hash=synthesis_baton_hash,
            registry=registry,
            retrieved_entries=retrieved_entries,
            objective="Synthesize the final 900-1,300 word decision-grade crisis brief from frozen sources and registered critique artifacts.",
            final=True,
        ),
        max_tokens=3400,
        timeout=timeout,
        call_type="holo_final_synthesis",
        role="final_synthesis_author",
        turn_index=synthesis_index,
        call_id="holo_final_synthesis",
        artifact_path=artifact_path,
    )
    traces.append(final_trace)
    final_prompt_hash = sha_file(Path(final_trace["prompt_card_path"]))
    final_hash = sha_text(final_text)
    final_record = artifact_entry(
        artifact_id="final_synthesis_artifact",
        artifact_type="final_artifact",
        text=final_text,
        path=artifact_path,
        role="final_synthesis_author",
    )
    final_role_result = role_compliance(final_text, role="final_synthesis_author", final=True)
    final_audit_result = state_audit(
        final_text,
        packet_dir=packet_dir,
        state_object=synthesis_state,
        registry=registry,
        prompt_card_hash=final_prompt_hash,
    )
    final_registry = registry + [final_record]
    turn_records.append(
        {
            "turn_index": synthesis_index,
            "state_object_hash": synthesis_state_hash,
            "state_object_path": synthesis_state_path,
            "baton_pass_hash": synthesis_baton_hash,
            "baton_pass_path": synthesis_baton_path,
            "selected_model": {"provider": provider, "exact_model_id": model, "endpoint": endpoint_for_provider(provider)},
            "adversarial_role": "final_synthesis_author",
            "role_compliance_result": final_role_result,
            "state_audit_constraint_preservation_result": final_audit_result,
            "synthesis_trigger": {"triggered": True, "reason": "final_synthesis_turn_completed"},
            "token_budget_partial_injection_flags": {
                "present": True,
                "token_budget_limit": 3400,
                "tokens_used": int(final_trace.get("output_tokens") or 0),
                "partial_injection_used": False,
                "partial_injection_reason": None,
            },
            "artifact_record": final_record,
            "artifact_registry_entries": schema_registry_entries(registry),
            "artifact_registry_hash": registry_hash(registry),
            "artifact_registry_after_hash": registry_hash(final_registry),
            "pinned_source_hashes": [item["artifact_hash"] for item in retrieved_entries if item["artifact_type"].startswith("frozen_")],
            "pinned_artifact_hashes": pinned_artifact_hashes_from_retrieval(retrieved_entries),
            "retrieved_artifact_ids": retrieved_ids,
            "prompt_card_hash": final_prompt_hash,
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


def write_condition_smoke(
    packet_dir: Path,
    run_id: str,
    condition: str,
    *,
    holo_mode: str = HOLO_MODE_DIAGNOSTIC_V3,
) -> dict[str, Any]:
    if condition == "holo_build_arch" and holo_mode == HOLO_MODE_FULL_GOV_V4:
        return run_holobuild_full_gov_v4(packet_dir, run_id, timeout=0, live=False)

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
        "run_mode": RUN_MODE,
        "holo_mode": HOLO_MODE_DIAGNOSTIC_V3 if condition == "holo_build_arch" else None,
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


def update_run_manifest(
    packet_dir: Path,
    run_id: str,
    condition_results: list[dict[str, Any]],
    *,
    holo_mode: str = HOLO_MODE_DIAGNOSTIC_V3,
) -> dict[str, Any]:
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
        "run_mode": run_mode_for_holo_mode(holo_mode),
        "holo_mode": holo_mode if any(item.get("condition") == "holo_build_arch" for item in condition_results) else None,
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
        "expected_holo_call_count": expected_holo_call_count(holo_mode),
        "final_word_target": FINAL_WORD_TARGET,
    }
    write_json(manifest_path, manifest)
    return manifest


def update_live_run_manifest(
    packet_dir: Path,
    run_id: str,
    condition_results: list[dict[str, Any]],
    *,
    holo_mode: str = HOLO_MODE_DIAGNOSTIC_V3,
) -> dict[str, Any]:
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
        "run_mode": run_mode_for_holo_mode(holo_mode),
        "holo_mode": holo_mode if any(item.get("condition") == "holo_build_arch" for item in condition_results) else None,
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
        "expected_holo_call_count": expected_holo_call_count(holo_mode),
        "final_word_target": FINAL_WORD_TARGET,
    }
    write_json(manifest_path, manifest)
    return manifest


def run_no_provider_smoke(
    packet_dir: Path,
    run_id: str,
    conditions: list[str],
    *,
    holo_mode: str = HOLO_MODE_DIAGNOSTIC_V3,
) -> int:
    require_packet(packet_dir)
    results = [write_condition_smoke(packet_dir, run_id, condition, holo_mode=holo_mode) for condition in conditions]
    manifest = update_run_manifest(packet_dir, run_id, results, holo_mode=holo_mode)
    status = "D5_MINI_SCOUT_RUNNER_NO_PROVIDER_SMOKE_PASS"
    if any(item.get("architecture_evidence_errors") for item in results):
        status = "D5_MINI_SCOUT_RUNNER_NO_PROVIDER_SMOKE_FAIL"
    print(
        json.dumps(
            {
                "status": status,
                "runner_id": RUNNER_ID,
                "run_mode": run_mode_for_holo_mode(holo_mode),
                "holo_mode": holo_mode if "holo_build_arch" in conditions else None,
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


def run_live_guarded(
    packet_dir: Path,
    run_id: str,
    conditions: list[str],
    timeout: int,
    *,
    holo_mode: str = HOLO_MODE_DIAGNOSTIC_V3,
) -> int:
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
    ensure_env_available(conditions, holo_mode=holo_mode)
    results: list[dict[str, Any]] = []
    try:
        for condition in conditions:
            if condition == "solo_openai_gpt_5_5":
                results.append(run_live_solo(packet_dir, run_id, timeout))
            elif condition == "holo_build_arch":
                if holo_mode == HOLO_MODE_FULL_GOV_V4:
                    results.append(run_holobuild_full_gov_v4(packet_dir, run_id, timeout, live=True))
                else:
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
    manifest = update_live_run_manifest(packet_dir, run_id, results, holo_mode=holo_mode)
    print(
        json.dumps(
            {
                "status": "D5_MINI_SCOUT_LIVE_GENERATION_COMPLETE",
                "run_mode": run_mode_for_holo_mode(holo_mode),
                "holo_mode": holo_mode if "holo_build_arch" in conditions else None,
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
    parser.add_argument("--holo-mode", choices=HOLO_MODES, default=HOLO_MODE_DIAGNOSTIC_V3)
    parser.add_argument("--no-provider-smoke", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    packet_dir = Path(args.packet_dir).resolve()
    conditions = list(dict.fromkeys(args.condition))
    if args.live:
        return run_live_guarded(packet_dir, args.run_id, conditions, args.timeout, holo_mode=args.holo_mode)
    return run_no_provider_smoke(packet_dir, args.run_id, conditions, holo_mode=args.holo_mode)


if __name__ == "__main__":
    raise SystemExit(main())
