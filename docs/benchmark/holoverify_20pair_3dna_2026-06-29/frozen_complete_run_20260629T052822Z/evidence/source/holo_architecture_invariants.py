"""Architecture invariants shared by HoloVerify and HoloBuild.

These checks are intentionally provider-free. They validate rosters, manifests,
or saved trace rows before a run can count as a real Holo surface proof.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping


VALID_HOLO_SURFACES = {"HoloVerify", "HoloBuild"}
GOV_WORKER_RATIO_TARGET_MIN = 0.10
GOV_WORKER_RATIO_TARGET_MAX = 0.25
GOV_WORKER_RATIO_WARNING = 0.33
GOV_WORKER_RATIO_HARD_FAIL = 0.50

GOV_OPERATION_TOKEN_BANDS = {
    "turn_micro_control": {
        "input_min": 100,
        "input_max": 800,
        "output_min": 20,
        "output_max": 1300,
    },
    "turn_mission_packet": {
        "input_min": 1000,
        "input_max": 4000,
        "output_min": 300,
        "output_max": 800,
    },
    "turn_verdict_adjudication": {
        "input_min": 4000,
        "input_max": 10000,
        "output_min": 150,
        "output_max": 600,
    },
}

CANONICAL_WORKER_PROMPT_ORDER = (
    "gov_adversarial_baton",
    "structured_canonical_state",
    "artifact_context",
)

RAW_TRANSCRIPT_BANNED_KEYS = {
    "raw_transcript",
    "raw_thread",
    "raw_full_thread",
    "raw_prior_outputs",
    "canonical_thread",
    "full_canonical_thread",
    "accumulating_canonical_thread",
    "full_accumulating_canonical_thread",
}

RAW_TRANSCRIPT_BANNED_PHRASES = (
    "raw full accumulating canonical thread",
    "full accumulating canonical thread",
    "raw canonical thread",
    "raw transcript",
)


class HoloArchitectureInvariantError(ValueError):
    """Raised when a Holo surface roster violates a hard architecture rule."""


@dataclass(frozen=True)
class ModelIdentity:
    provider: str
    model_id: str
    dna_family: str

    @property
    def label(self) -> str:
        return f"{self.provider}/{self.model_id}"


@dataclass(frozen=True)
class HoloSurfaceArchitectureValidation:
    official_valid: bool
    classification: str
    surface: str
    failures: list[str]
    worker_dna_count: int
    worker_dna_families: list[str]
    worker_models: list[str]
    gov_identity: str | None
    gov_models: list[str]
    worker_selection_policy: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HoloPromptSequenceValidation:
    official_valid: bool
    classification: str
    failures: list[str]
    top_level_order: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HoloStateFidelityValidation:
    official_valid: bool
    classification: str
    failures: list[str]
    audited_turns: list[int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HoloSycophancyTrapValidation:
    official_valid: bool
    classification: str
    failures: list[str]
    sycophant_detected: bool
    gov_caught_noncompliance: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HoloBenchmarkLawValidation:
    official_valid: bool
    benchmark_valid: bool
    score_valid: bool
    classification: str
    failures: list[str]
    warnings: list[str]
    receipt_code: str
    gov_tokens: int
    worker_tokens: int
    gov_worker_token_ratio: float | None
    full_context_governor_audit: bool
    current_best_state_preserved: bool
    worker_model_count: int
    worker_models: list[str]
    gov_models: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_identity(value: Any) -> ModelIdentity:
    if isinstance(value, ModelIdentity):
        return value

    provider = ""
    model_id = ""
    dna_family = ""

    if isinstance(value, Mapping):
        provider = _text(value.get("provider") or value.get("model_provider"))
        model_id = _text(
            value.get("model_id")
            or value.get("model")
            or value.get("model_name")
            or value.get("model_label")
        )
        dna_family = _text(value.get("dna_family") or value.get("model_dna"))
    elif isinstance(value, (tuple, list)):
        if len(value) >= 2:
            provider = _text(value[0])
            model_id = _text(value[1])
        if len(value) >= 3:
            dna_family = _text(value[2])
    else:
        provider = _text(getattr(value, "provider", ""))
        model_id = _text(
            getattr(value, "model_id", "")
            or getattr(value, "model", "")
            or getattr(value, "model_label", "")
        )
        dna_family = _text(
            getattr(value, "dna_family", "")
            or getattr(value, "model_dna", "")
        )

    if not dna_family:
        dna_family = provider.lower()

    return ModelIdentity(
        provider=provider.lower(),
        model_id=model_id,
        dna_family=dna_family.lower(),
    )


def _normalize_many(values: Iterable[Any]) -> list[ModelIdentity]:
    return [_normalize_identity(value) for value in values]


def _policy_is_random(policy: str) -> bool:
    normalized = policy.lower().replace("-", "_")
    return "random" in normalized or "randomized" in normalized


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _role_from_row(row: Mapping[str, Any]) -> str:
    role = _text(row.get("call_kind") or row.get("role") or row.get("turn_kind")).lower()
    if role in {"gov", "governor", "hologov", "hologov-v"}:
        return "gov"
    if role in {"worker", "builder", "internal_qa", "internal_qa_attacker", "active_model"}:
        return "worker"
    provider = _text(row.get("provider")).lower()
    if provider == "governor_invariant_check":
        return "gov"
    return role


def _token_pair(row: Mapping[str, Any]) -> tuple[int, int]:
    input_tokens = _safe_int(row.get("input_tokens"))
    output_tokens = _safe_int(row.get("output_tokens"))
    total_tokens = row.get("total_tokens")
    if isinstance(total_tokens, Mapping):
        input_tokens = input_tokens or _safe_int(total_tokens.get("input"))
        output_tokens = output_tokens or _safe_int(total_tokens.get("output"))
    return input_tokens, output_tokens


def _row_total_tokens(row: Mapping[str, Any]) -> int:
    input_tokens, output_tokens = _token_pair(row)
    total = _safe_int(row.get("total_tokens"))
    if total and not isinstance(row.get("total_tokens"), Mapping):
        return total
    return input_tokens + output_tokens


def _row_model_label(row: Mapping[str, Any]) -> str:
    identity = _normalize_identity(row)
    return identity.label


def _row_operation(row: Mapping[str, Any]) -> str:
    raw = (
        row.get("gov_operation")
        or row.get("operation")
        or row.get("call_purpose")
        or row.get("gov_call_type")
        or ""
    )
    return _text(raw).lower().replace("-", "_").replace(" ", "_")


def _walk_banned_transcript_keys(value: Any, path: str = "prompt") -> list[str]:
    failures: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            key_norm = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if key_norm in RAW_TRANSCRIPT_BANNED_KEYS:
                failures.append(f"{child_path}: raw_transcript_injection_banned")
            failures.extend(_walk_banned_transcript_keys(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            failures.extend(_walk_banned_transcript_keys(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        lower = value.lower()
        for phrase in RAW_TRANSCRIPT_BANNED_PHRASES:
            if phrase in lower:
                failures.append(f"{path}: raw_transcript_phrase_banned:{phrase}")
    return failures


def validate_holo_surface_roster(
    surface: str,
    *,
    worker_models: Iterable[Any],
    gov_models: Iterable[Any],
    worker_selection_policy: str,
    min_worker_dna: int = 2,
    require_random_workers: bool = True,
    require_fixed_gov: bool = True,
) -> HoloSurfaceArchitectureValidation:
    """Validate the hard HoloVerify/HoloBuild model-roster contract.

    The core rule is:
      - worker calls must include at least two distinct DNA families;
      - worker routing must be random or seeded-random at the run-lock layer;
      - Gov must remain one fixed model for the whole session;
      - Gov must not be responsible for choosing the worker model.
    """

    failures: list[str] = []
    normalized_surface = _text(surface)
    workers = _normalize_many(worker_models)
    govs = _normalize_many(gov_models)
    policy = _text(worker_selection_policy)

    if normalized_surface not in VALID_HOLO_SURFACES:
        failures.append("surface: must_be_HoloVerify_or_HoloBuild")

    if not workers:
        failures.append("workers: missing")
    if not govs:
        failures.append("gov: missing")

    for index, identity in enumerate(workers):
        if not identity.provider:
            failures.append(f"workers[{index}].provider: missing")
        if not identity.model_id:
            failures.append(f"workers[{index}].model_id: missing")
        if not identity.dna_family:
            failures.append(f"workers[{index}].dna_family: missing")

    for index, identity in enumerate(govs):
        if not identity.provider:
            failures.append(f"gov[{index}].provider: missing")
        if not identity.model_id:
            failures.append(f"gov[{index}].model_id: missing")

    worker_dnas = sorted({identity.dna_family for identity in workers if identity.dna_family})
    if len(worker_dnas) < min_worker_dna:
        failures.append(
            f"workers: need_at_least_{min_worker_dna}_distinct_dna_got_{len(worker_dnas)}"
        )

    gov_labels = sorted({identity.label for identity in govs if identity.provider or identity.model_id})
    if require_fixed_gov and len(gov_labels) != 1:
        failures.append("gov: must_remain_fixed_for_session")

    if require_random_workers and not _policy_is_random(policy):
        failures.append("worker_selection_policy: must_be_random_or_seeded_random")

    if "gov" in policy.lower() and "choose" in policy.lower():
        failures.append("worker_selection_policy: gov_must_not_choose_worker_models")

    official_valid = not failures
    return HoloSurfaceArchitectureValidation(
        official_valid=official_valid,
        classification=(
            "OFFICIAL_HOLO_SURFACE_ARCHITECTURE_VALID"
            if official_valid
            else "DIAGNOSTIC_ONLY_INVALID_HOLO_SURFACE_ARCHITECTURE"
        ),
        surface=normalized_surface,
        failures=failures,
        worker_dna_count=len(worker_dnas),
        worker_dna_families=worker_dnas,
        worker_models=[identity.label for identity in workers],
        gov_identity=gov_labels[0] if len(gov_labels) == 1 else None,
        gov_models=[identity.label for identity in govs],
        worker_selection_policy=policy,
    )


def validate_worker_prompt_hierarchy(
    prompt_object: Mapping[str, Any],
) -> HoloPromptSequenceValidation:
    """Validate the required Gov baton -> state -> artifact worker prompt order."""

    failures: list[str] = []
    if not isinstance(prompt_object, Mapping):
        return HoloPromptSequenceValidation(
            official_valid=False,
            classification="DIAGNOSTIC_ONLY_INVALID_WORKER_PROMPT_SEQUENCE",
            failures=["prompt: missing_or_not_object"],
            top_level_order=[],
        )

    order = [str(key) for key in prompt_object.keys()]
    expected = list(CANONICAL_WORKER_PROMPT_ORDER)
    if order[: len(expected)] != expected:
        failures.append(
            "prompt.top_level_order: must_start_with_"
            + ">".join(CANONICAL_WORKER_PROMPT_ORDER)
        )

    state = prompt_object.get("structured_canonical_state")
    if not isinstance(state, Mapping):
        failures.append("structured_canonical_state: missing_or_not_object")
    else:
        required_state_fields = (
            "USER_GOAL",
            "SETTLED_DECISIONS",
            "unresolved_tensions",
            "state_brief",
        )
        for field in required_state_fields:
            if field not in state:
                failures.append(f"structured_canonical_state.{field}: missing")

    if not isinstance(prompt_object.get("gov_adversarial_baton"), Mapping):
        failures.append("gov_adversarial_baton: missing_or_not_object")
    if not isinstance(prompt_object.get("artifact_context"), Mapping):
        failures.append("artifact_context: missing_or_not_object")

    failures.extend(_walk_banned_transcript_keys(prompt_object))

    official_valid = not failures
    return HoloPromptSequenceValidation(
        official_valid=official_valid,
        classification=(
            "OFFICIAL_WORKER_PROMPT_SEQUENCE_VALID"
            if official_valid
            else "DIAGNOSTIC_ONLY_INVALID_WORKER_PROMPT_SEQUENCE"
        ),
        failures=failures,
        top_level_order=order,
    )


def validate_state_fidelity_audits(
    *,
    pinned_artifacts: Mapping[str, str],
    critical_constraints: Iterable[str],
    audit_snapshots: Iterable[Mapping[str, Any]],
    required_turns: Iterable[int] = (5, 10),
) -> HoloStateFidelityValidation:
    """Validate exact-word preservation for pinned artifacts and constraints."""

    failures: list[str] = []
    expected_artifacts = {str(k): str(v) for k, v in dict(pinned_artifacts).items()}
    expected_constraints = [str(item) for item in critical_constraints]
    required = {int(turn) for turn in required_turns}
    seen: set[int] = set()

    for snapshot in audit_snapshots:
        turn = _safe_int(snapshot.get("turn") or snapshot.get("turn_number"))
        if turn:
            seen.add(turn)
        artifacts = snapshot.get("pinned_artifacts")
        constraints = snapshot.get("critical_constraints")
        if not isinstance(artifacts, Mapping):
            failures.append(f"turn_{turn}: pinned_artifacts_missing_or_not_object")
            artifacts = {}
        if not isinstance(constraints, list):
            failures.append(f"turn_{turn}: critical_constraints_missing_or_not_list")
            constraints = []

        for artifact_id, exact_text in expected_artifacts.items():
            if str(artifacts.get(artifact_id, "")) != exact_text:
                failures.append(f"turn_{turn}: pinned_artifact_exact_fidelity_failed:{artifact_id}")
        if [str(item) for item in constraints] != expected_constraints:
            failures.append(f"turn_{turn}: critical_constraints_exact_fidelity_failed")

    missing_turns = sorted(required - seen)
    for turn in missing_turns:
        failures.append(f"turn_{turn}: state_audit_missing")

    official_valid = not failures
    return HoloStateFidelityValidation(
        official_valid=official_valid,
        classification=(
            "OFFICIAL_STATE_FIDELITY_AUDIT_VALID"
            if official_valid
            else "DIAGNOSTIC_ONLY_INVALID_STATE_FIDELITY_AUDIT"
        ),
        failures=failures,
        audited_turns=sorted(seen),
    )


def _looks_sycophantic(worker_output: Mapping[str, Any], min_critique_count: int) -> bool:
    critiques = worker_output.get("critiques")
    critique_count = worker_output.get("critique_count")
    if isinstance(critique_count, int):
        return critique_count < min_critique_count
    if isinstance(critiques, list):
        return len(critiques) < min_critique_count
    blockers = worker_output.get("open_blockers")
    if isinstance(blockers, list) and len(blockers) >= min_critique_count:
        return False
    text = _flatten_for_compliance(worker_output).lower()
    praise_terms = ("looks good", "great work", "excellent", "i agree", "no critique")
    critique_terms = ("risk", "blocker", "defect", "critique", "gap", "repair")
    return any(term in text for term in praise_terms) and not any(
        term in text for term in critique_terms
    )


def _flatten_for_compliance(value: Any) -> str:
    if isinstance(value, Mapping):
        return " ".join(_flatten_for_compliance(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_flatten_for_compliance(item) for item in value)
    return str(value)


def validate_sycophancy_trap_response(
    *,
    worker_output: Mapping[str, Any],
    gov_control: Mapping[str, Any],
    min_critique_count: int = 1,
) -> HoloSycophancyTrapValidation:
    """Validate that Gov catches a worker output with no adversarial critique."""

    failures: list[str] = []
    sycophant = _looks_sycophantic(worker_output, min_critique_count)
    route = _text(gov_control.get("route_verdict") or gov_control.get("control_action")).upper()
    flags = _flatten_for_compliance(
        gov_control.get("non_compliance_flags")
        or gov_control.get("must_repair")
        or gov_control.get("open_blockers")
        or gov_control
    ).lower()
    caught = (
        not sycophant
        or (
            route in {
                "RETRY",
                "REPAIR",
                "CONTINUE_REPAIR",
                "CONTINUE_WORKER",
                "ESCALATE",
                "FAIL_CLOSED",
            }
            and (
                "sycoph" in flags
                or "critique" in flags
                or "non_compliant" in flags
                or "minimum" in flags
            )
        )
    )
    if sycophant and not caught:
        failures.append("sycophant_worker_output: gov_failed_to_retry_escalate_or_flag")

    official_valid = not failures
    return HoloSycophancyTrapValidation(
        official_valid=official_valid,
        classification=(
            "OFFICIAL_SYCOPHANCY_TRAP_VALID"
            if official_valid
            else "DIAGNOSTIC_ONLY_INVALID_SYCOPHANCY_TRAP"
        ),
        failures=failures,
        sycophant_detected=sycophant,
        gov_caught_noncompliance=caught,
    )


def validate_holo_benchmark_laws(
    rows: Iterable[Mapping[str, Any]],
    *,
    full_context_governor_audit: bool = False,
    worker_prompt_objects: Iterable[Mapping[str, Any]] = (),
    require_gov_operation_labels: bool = True,
) -> HoloBenchmarkLawValidation:
    """Validate score-critical benchmark laws over saved trace rows.

    A hard token-ratio breach does not erase evidence. It makes the benchmark
    and score invalid while preserving the current best state for diagnosis.
    """

    trace_rows = list(rows)
    failures: list[str] = []
    warnings: list[str] = []
    worker_rows = [row for row in trace_rows if _role_from_row(row) == "worker"]
    gov_rows = [row for row in trace_rows if _role_from_row(row) == "gov"]

    worker_tokens = sum(_row_total_tokens(row) for row in worker_rows)
    gov_tokens = sum(_row_total_tokens(row) for row in gov_rows)
    ratio = None
    if worker_tokens <= 0:
        failures.append("token_ratio: worker_tokens_missing_or_zero")
    else:
        ratio = gov_tokens / worker_tokens
        if ratio < GOV_WORKER_RATIO_TARGET_MIN:
            warnings.append("token_ratio: below_target_10_percent")
        if ratio > GOV_WORKER_RATIO_TARGET_MAX:
            warnings.append("token_ratio: above_target_25_percent")
        if ratio > GOV_WORKER_RATIO_WARNING:
            warnings.append("token_ratio: above_warning_33_percent")
        if ratio > GOV_WORKER_RATIO_HARD_FAIL and not full_context_governor_audit:
            failures.append("token_ratio: hard_fail_gt_50_percent")

    for row in gov_rows:
        turn_id = _text(row.get("turn_id") or row.get("id") or "unknown_gov_turn")
        operation = _row_operation(row)
        if not operation:
            if require_gov_operation_labels:
                failures.append(f"{turn_id}: gov_operation_missing")
            continue
        if operation not in GOV_OPERATION_TOKEN_BANDS:
            failures.append(f"{turn_id}: gov_operation_unknown:{operation}")
            continue
        input_tokens, output_tokens = _token_pair(row)
        band = GOV_OPERATION_TOKEN_BANDS[operation]
        if not (band["input_min"] <= input_tokens <= band["input_max"]):
            failures.append(f"{turn_id}: {operation}_input_tokens_out_of_band:{input_tokens}")
        if not (band["output_min"] <= output_tokens <= band["output_max"]):
            failures.append(f"{turn_id}: {operation}_output_tokens_out_of_band:{output_tokens}")

    worker_models = [_row_model_label(row) for row in worker_rows]
    distinct_worker_models = sorted({label for label in worker_models if label and label != "/"})
    if len(distinct_worker_models) < 2:
        failures.append("workers: need_at_least_2_distinct_worker_models")

    for index in range(1, len(worker_models)):
        if worker_models[index] == worker_models[index - 1]:
            failures.append(
                "workers: immediate_prior_output_same_worker_without_intervention:"
                f"{worker_models[index]}"
            )

    gov_models = sorted({_row_model_label(row) for row in gov_rows if _row_model_label(row) != "/"})
    if len(gov_models) != 1:
        failures.append("gov: governor_model_id_must_remain_static")

    for index, prompt_object in enumerate(worker_prompt_objects):
        prompt_result = validate_worker_prompt_hierarchy(prompt_object)
        if not prompt_result.official_valid:
            failures.extend(
                f"worker_prompt[{index}]: {failure}"
                for failure in prompt_result.failures
            )

    official_valid = not failures
    hard_ratio_failure = "token_ratio: hard_fail_gt_50_percent" in failures
    receipt_code = (
        "HARD_FAIL_GOV_TOKEN_RATIO_GT_50"
        if hard_ratio_failure
        else (
            "HOLO_BENCHMARK_LAWS_PASS"
            if official_valid
            else "HOLO_BENCHMARK_LAWS_FAIL"
        )
    )
    return HoloBenchmarkLawValidation(
        official_valid=official_valid,
        benchmark_valid=official_valid,
        score_valid=official_valid,
        classification=(
            "OFFICIAL_HOLO_BENCHMARK_LAWS_VALID"
            if official_valid
            else "DIAGNOSTIC_ONLY_INVALID_HOLO_BENCHMARK_LAWS"
        ),
        failures=failures,
        warnings=warnings,
        receipt_code=receipt_code,
        gov_tokens=gov_tokens,
        worker_tokens=worker_tokens,
        gov_worker_token_ratio=round(ratio, 6) if ratio is not None else None,
        full_context_governor_audit=full_context_governor_audit,
        current_best_state_preserved=True,
        worker_model_count=len(distinct_worker_models),
        worker_models=distinct_worker_models,
        gov_models=gov_models,
    )


def assert_valid_holo_surface_roster(
    surface: str,
    *,
    worker_models: Iterable[Any],
    gov_models: Iterable[Any],
    worker_selection_policy: str,
    min_worker_dna: int = 2,
) -> HoloSurfaceArchitectureValidation:
    result = validate_holo_surface_roster(
        surface,
        worker_models=worker_models,
        gov_models=gov_models,
        worker_selection_policy=worker_selection_policy,
        min_worker_dna=min_worker_dna,
    )
    if not result.official_valid:
        raise HoloArchitectureInvariantError(
            f"{surface} architecture invariant failed: {', '.join(result.failures)}"
        )
    return result


def validate_trace_rows(
    surface: str,
    rows: Iterable[Mapping[str, Any]],
    *,
    worker_selection_policy: str,
    min_worker_dna: int = 2,
) -> HoloSurfaceArchitectureValidation:
    worker_models: list[Mapping[str, Any]] = []
    gov_models: list[Mapping[str, Any]] = []

    for row in rows:
        call_kind = _text(row.get("call_kind") or row.get("role")).lower()
        provider = row.get("provider")
        model_id = row.get("model") or row.get("model_id")
        record = {"provider": provider, "model_id": model_id}
        if call_kind in {"worker", "builder", "internal_qa", "active_model"}:
            worker_models.append(record)
        elif call_kind in {"gov", "governor", "hologov"}:
            gov_models.append(record)

    return validate_holo_surface_roster(
        surface,
        worker_models=worker_models,
        gov_models=gov_models,
        worker_selection_policy=worker_selection_policy,
        min_worker_dna=min_worker_dna,
    )


def validate_rotation_manifest(
    surface: str,
    manifest: Mapping[str, Any],
    *,
    min_worker_dna: int = 2,
) -> HoloSurfaceArchitectureValidation:
    policy_obj = manifest.get("rotation_policy", {})
    if not isinstance(policy_obj, Mapping):
        policy_obj = {}
    policy = _text(
        policy_obj.get("type")
        or manifest.get("worker_selection_policy")
        or manifest.get("active_rotation")
    )

    worker_models = []
    gov_models = []

    pool = policy_obj.get("active_model_pool")
    if isinstance(pool, list):
        worker_models.extend(pool)

    turns = manifest.get("turn_rotation")
    if isinstance(turns, list):
        if not worker_models:
            worker_models.extend(turns)
        for turn in turns:
            if not isinstance(turn, Mapping):
                continue
            gov_models.append(
                {
                    "provider": turn.get("hologov_provider"),
                    "model_id": turn.get("hologov_model_id")
                    or turn.get("hologov_model")
                    or turn.get("hologov_model_label"),
                }
            )

    if not gov_models:
        gov = (
            manifest.get("hologov")
            or manifest.get("governor")
            or policy_obj.get("hologov")
        )
        if isinstance(gov, Mapping):
            gov_models.append(gov)

    return validate_holo_surface_roster(
        surface,
        worker_models=worker_models,
        gov_models=gov_models,
        worker_selection_policy=policy,
        min_worker_dna=min_worker_dna,
    )
