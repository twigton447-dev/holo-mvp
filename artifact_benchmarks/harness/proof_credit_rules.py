from __future__ import annotations

import json
import re
from typing import Any


JUDGE_VISIBLE_PACKET_KEYS = {
    "packet_kind",
    "blind",
    "domain_id",
    "cohort",
    "turn",
    "brief",
    "source_pack",
    "datasets",
    "exhibits",
    "judge_brief",
    "rubric",
    "judge_instructions",
}

FORBIDDEN_MODEL_VISIBLE_KEYS = {
    "expected_verdict",
    "hidden_ground_truth",
    "gold_answer",
    "scoring_targets",
    "builder_hypothesis",
    "hypothesized_verdict",
    "build_state_object",
    "verify_state_object",
    "state_object",
    "state_objects",
    "state_object_version",
    "gov_state",
    "govstate",
    "batonpass",
    "baton_pass",
    "anonymization_map",
    "document_x_condition",
    "document_y_condition",
    "solo_condition",
    "holo_condition",
    "provider_model",
    "model_lineup",
    "analyst_rotation",
    "governor_model",
    "trace_path",
    "prompt_card_path",
    "artifact_path",
    "_builder",
    "_internal",
    "_harness",
}

FORBIDDEN_RUNTIME_TEXT_PATTERNS = (
    r"\bBUILD_STATE_OBJECT\b",
    r"\bVERIFY_STATE_OBJECT\b",
    r"\bGovState\b",
    r"\bBatonPass\b",
    r"\bcanonical\s+holo\s+state\s+object\b",
    r"\bstate_object_version\b",
    r"\brepair_ledger\b",
    r"\bmission_packet_required_fields\b",
    r"\bcurrent_best_state\b",
    r"\bnew_learnings_from_prior_turns\b",
    r"\bhighest_value_flaw\b",
    r"\bconvergence_target\b",
    r"\banonymization\s+map\b",
    r"\bdocument_[xy]_condition\b",
    r"\bsolo_condition\b",
    r"\bholo_condition\b",
    r"\bsolo_(openai|anthropic|google|xai|minimax|grok|haiku|flash|opus)\b",
    r"\bholo_(frontier|mini|3substrate|factory)\b",
    r"\banalyst_rotation\b",
    r"\bgovernor_model\b",
)

MODEL_VISIBLE_PAYLOAD_KEYS = {"action", "context"}


def provider_family(provider: str | None, model: str | None = None) -> str:
    if provider:
        return str(provider).split(":", 1)[0].strip().lower()
    if model and ":" in str(model):
        return str(model).split(":", 1)[0].strip().lower()
    return ""


def provider_model_ref(provider_model: str | None) -> dict[str, str]:
    text = str(provider_model or "").strip()
    if ":" in text:
        provider, model = text.split(":", 1)
    else:
        provider, model = text, ""
    return {
        "provider": provider.strip().lower(),
        "model": model.strip(),
        "provider_model": f"{provider.strip().lower()}:{model.strip()}" if model.strip() else provider.strip().lower(),
    }


def judge_provider_model(judge: dict[str, Any]) -> dict[str, str]:
    provider = str(judge.get("provider") or judge.get("judge_provider") or "").strip().lower()
    model = str(judge.get("model") or judge.get("judge_model") or "").strip()
    return {
        "provider": provider,
        "model": model,
        "provider_model": f"{provider}:{model}" if provider and model else provider,
    }


def generation_dna_from_provider_models(provider_models: list[str]) -> dict[str, Any]:
    refs = [provider_model_ref(item) for item in provider_models if item]
    models = sorted({item["provider_model"] for item in refs if item["provider_model"]})
    providers = sorted({item["provider"] for item in refs if item["provider"]})
    return {
        "generation_dna_version": "provider_family_v1",
        "providers": providers,
        "provider_models": models,
    }


def generation_dna_for_pair(
    *,
    cohort_plan: dict[str, Any],
    solo_condition: str | None,
    holo_condition: str | None,
) -> dict[str, Any]:
    holo_models: list[str] = []
    if holo_condition and holo_condition == cohort_plan.get("holo_condition_id"):
        holo_models.extend(str(item) for item in cohort_plan.get("analyst_rotation", []) if item)
        if cohort_plan.get("governor_model"):
            holo_models.append(str(cohort_plan["governor_model"]))

    solo_model = None
    solo_conditions = cohort_plan.get("solo_conditions") or {}
    if solo_condition:
        solo_model = solo_conditions.get(solo_condition)

    all_models = list(holo_models)
    if solo_model:
        all_models.append(str(solo_model))

    dna = generation_dna_from_provider_models(all_models)
    dna.update(
        {
            "holo_condition": holo_condition or "",
            "solo_condition": solo_condition or "",
            "holo_provider_models": sorted(set(holo_models)),
            "solo_provider_model": solo_model or "",
        }
    )
    return dna


def judge_dna_overlap(judge: dict[str, Any], generation_dna: dict[str, Any] | None) -> list[str]:
    if not generation_dna:
        return ["unknown_generation_dna"]
    judge_ref = judge_provider_model(judge)
    if not judge_ref["provider"]:
        return ["unknown_judge_dna"]

    generation_providers = {str(item).lower() for item in generation_dna.get("providers", [])}
    generation_models = {str(item).lower() for item in generation_dna.get("provider_models", [])}
    reasons: list[str] = []
    if judge_ref["provider"] in generation_providers:
        reasons.append(f"same_provider:{judge_ref['provider']}")
    if judge_ref["provider_model"].lower() in generation_models:
        reasons.append(f"same_model:{judge_ref['provider_model']}")
    return reasons


def annotate_judge_credit(judge: dict[str, Any], generation_dna: dict[str, Any] | None) -> dict[str, Any]:
    overlap = judge_dna_overlap(judge, generation_dna)
    eligible = not overlap
    if eligible:
        label = "proof_credit_candidate"
        score_use = "proof_credit_if_blind_and_boundary_clean"
    elif "unknown_generation_dna" in overlap or "unknown_judge_dna" in overlap:
        label = "diagnostic_unknown_dna"
        score_use = "diagnostic_only"
    else:
        label = "diagnostic_same_dna"
        score_use = "diagnostic_only"
    return {
        "generation_dna_providers": ",".join(generation_dna.get("providers", [])) if generation_dna else "",
        "generation_dna_models": ",".join(generation_dna.get("provider_models", [])) if generation_dna else "",
        "judge_dna_overlap": ",".join(overlap),
        "proof_credit_eligible": eligible,
        "score_credit_label": label,
        "score_use": score_use,
    }


def select_outside_dna_judges(
    judge_panel: list[dict[str, Any]],
    generation_dna: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for judge in judge_panel:
        annotated = {**judge, **annotate_judge_credit(judge, generation_dna)}
        if annotated["proof_credit_eligible"]:
            selected.append(annotated)
    return selected


def _walk_key_paths(obj: Any, prefix: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            found.append((path, str(key)))
            found.extend(_walk_key_paths(value, path))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            found.extend(_walk_key_paths(value, f"{prefix}[{index}]"))
    return found


def forbidden_key_errors(obj: Any, *, scope: str) -> list[str]:
    errors: list[str] = []
    for path, key in _walk_key_paths(obj):
        normalized = key.lower()
        if normalized in FORBIDDEN_MODEL_VISIBLE_KEYS:
            errors.append(f"{scope}:forbidden_model_visible_key:{path}")
    return errors


def forbidden_text_errors(obj: Any, *, scope: str) -> list[str]:
    text = json.dumps(obj, sort_keys=True, ensure_ascii=True) if not isinstance(obj, str) else obj
    errors: list[str] = []
    for pattern in FORBIDDEN_RUNTIME_TEXT_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            errors.append(f"{scope}:forbidden_runtime_text:{pattern}")
    return errors


def runtime_visibility_errors(obj: Any, *, scope: str) -> list[str]:
    return [*forbidden_key_errors(obj, scope=scope), *forbidden_text_errors(obj, scope=scope)]


def model_visible_payload_errors(packet: dict[str, Any]) -> list[str]:
    payload = packet.get("payload")
    if not isinstance(payload, dict):
        return ["payload:missing_or_not_object"]
    errors: list[str] = []
    keys = set(payload.keys())
    extra = sorted(keys - MODEL_VISIBLE_PAYLOAD_KEYS)
    missing = sorted(MODEL_VISIBLE_PAYLOAD_KEYS - keys)
    if extra:
        errors.append(f"payload:non_model_visible_keys:{extra}")
    if missing:
        errors.append(f"payload:missing_model_visible_keys:{missing}")
    errors.extend(runtime_visibility_errors(payload, scope="payload"))
    return errors


def judge_visible_packet(packet: dict[str, Any]) -> dict[str, Any]:
    visible = {key: packet[key] for key in JUDGE_VISIBLE_PACKET_KEYS if key in packet}
    errors = runtime_visibility_errors(visible, scope="judge_visible_packet")
    if errors:
        raise RuntimeError("judge_visible_packet_boundary_failed " + "; ".join(errors))
    return visible
