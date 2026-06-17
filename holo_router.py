"""Serial HoloRouter for HoloChat 4DNA.

HoloCouncil is a pool and role protocol, not a parallel panel. This router
selects exactly one council model for a turn and one HoloGov model to hold the
conversation arc. It does not call providers.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from holo_state import CouncilRole, HoloState


DEFAULT_DNA_PROFILE = "verify_4mini"
DEFAULT_DNA_MODE = "serial"
DEFAULT_HOLOGOV_TENURE_MIN = 7
DEFAULT_HOLOGOV_TENURE_MAX = 11


@dataclass(frozen=True)
class DnaModelSpec:
    provider: str
    model_id: str
    required_env_var: str
    source_role: str
    source_provider: str | None = None


VERIFY_4MINI_PROFILE: tuple[DnaModelSpec, ...] = (
    DnaModelSpec(
        provider="minimax",
        model_id="MiniMax-M2.5-highspeed",
        required_env_var="MINIMAX_API_KEY",
        source_role="evidence_mapper",
    ),
    DnaModelSpec(
        provider="xai",
        model_id="grok-3-mini",
        required_env_var="XAI_API_KEY",
        source_role="risk_attacker",
    ),
    DnaModelSpec(
        provider="openai",
        model_id="gpt-4o-mini",
        required_env_var="OPENAI_API_KEY",
        source_role="allow_closure_defender",
    ),
    DnaModelSpec(
        provider="google",
        model_id="gemini-2.5-flash-lite",
        required_env_var="GOOGLE_API_KEY",
        source_role="hologov_final_governor",
        source_provider="google_gemini",
    ),
)


DNA_PROFILES: dict[str, tuple[DnaModelSpec, ...]] = {
    DEFAULT_DNA_PROFILE: VERIFY_4MINI_PROFILE,
}


@dataclass(frozen=True)
class AdapterIdentity:
    provider: str
    model_id: str


@dataclass(frozen=True)
class DnaProfileResolution:
    requested_profile: str
    resolved_profile: str
    eligible_adapters: tuple[Any, ...]
    configured_specs: tuple[DnaModelSpec, ...]
    skipped: tuple[str, ...]
    fallback_used: bool
    fallback_reason: str | None
    dna_degraded: bool

    @property
    def eligible_provider_count(self) -> int:
        return len({adapter_identity(a).provider for a in self.eligible_adapters})


@dataclass(frozen=True)
class RouteDecision:
    council_provider: str
    council_model: str
    hologov_provider: str
    hologov_model: str
    assigned_role: str
    route_reason: str
    fallback_used: bool
    fallback_reason: str | None
    dna_profile: str
    dna_degraded: bool
    eligible_provider_count: int
    previous_council_provider: str | None = None
    previous_council_model: str | None = None
    hologov_tenure_remaining: int | None = None
    hologov_tenure_window: tuple[int, int] = (
        DEFAULT_HOLOGOV_TENURE_MIN,
        DEFAULT_HOLOGOV_TENURE_MAX,
    )

    def as_previous_route(self) -> "PreviousRoute":
        return PreviousRoute(
            council_provider=self.council_provider,
            council_model=self.council_model,
            hologov_provider=self.hologov_provider,
            hologov_model=self.hologov_model,
            hologov_tenure_remaining=self.hologov_tenure_remaining or 0,
        )


@dataclass(frozen=True)
class PreviousRoute:
    council_provider: str | None = None
    council_model: str | None = None
    hologov_provider: str | None = None
    hologov_model: str | None = None
    hologov_tenure_remaining: int = 0


def adapter_identity(adapter: Any) -> AdapterIdentity:
    return AdapterIdentity(
        provider=str(getattr(adapter, "provider", "")),
        model_id=str(getattr(adapter, "model_id", getattr(adapter, "model", ""))),
    )


def _env_has_key(env: Mapping[str, str], key: str) -> bool:
    return bool(str(env.get(key, "")).strip())


def _matches_spec(adapter: Any, spec: DnaModelSpec) -> bool:
    identity = adapter_identity(adapter)
    return identity.provider == spec.provider and identity.model_id == spec.model_id


def resolve_holochat_dna_profile(
    adapters: Sequence[Any],
    *,
    profile: str = DEFAULT_DNA_PROFILE,
    env: Mapping[str, str] | None = None,
) -> DnaProfileResolution:
    env_map = env if env is not None else os.environ
    specs = DNA_PROFILES.get(profile)
    if not specs:
        return DnaProfileResolution(
            requested_profile=profile,
            resolved_profile="active_adapter_pool",
            eligible_adapters=tuple(adapters),
            configured_specs=(),
            skipped=(f"unknown_profile:{profile}",),
            fallback_used=True,
            fallback_reason=f"unknown HoloChat DNA profile: {profile}",
            dna_degraded=True,
        )

    eligible: list[Any] = []
    skipped: list[str] = []
    for spec in specs:
        if not _env_has_key(env_map, spec.required_env_var):
            skipped.append(f"{spec.provider}/{spec.model_id}:missing_env:{spec.required_env_var}")
            continue
        match = next((adapter for adapter in adapters if _matches_spec(adapter, spec)), None)
        if match is None:
            skipped.append(f"{spec.provider}/{spec.model_id}:adapter_not_loaded")
            continue
        eligible.append(match)

    if not eligible:
        return DnaProfileResolution(
            requested_profile=profile,
            resolved_profile="active_adapter_pool",
            eligible_adapters=tuple(adapters),
            configured_specs=specs,
            skipped=tuple(skipped),
            fallback_used=True,
            fallback_reason=f"profile {profile} resolved zero eligible adapters",
            dna_degraded=True,
        )

    unique_providers = {adapter_identity(adapter).provider for adapter in eligible}
    return DnaProfileResolution(
        requested_profile=profile,
        resolved_profile=profile,
        eligible_adapters=tuple(eligible),
        configured_specs=specs,
        skipped=tuple(skipped),
        fallback_used=False,
        fallback_reason=None if len(eligible) == len(specs) else "; ".join(skipped),
        dna_degraded=len(eligible) < len(specs) or len(unique_providers) < len(eligible),
    )


class HoloRouter:
    def __init__(
        self,
        adapters: Sequence[Any],
        *,
        dna_profile: str | None = None,
        env: Mapping[str, str] | None = None,
        tenure_min: int | None = None,
        tenure_max: int | None = None,
        seed: int | str | None = None,
        rng: random.Random | None = None,
    ):
        if not adapters:
            raise ValueError("HoloRouter requires at least one adapter")

        profile = dna_profile or os.getenv("HOLOCHAT_DNA_PROFILE", DEFAULT_DNA_PROFILE)
        self._resolution = resolve_holochat_dna_profile(
            adapters,
            profile=profile,
            env=env,
        )
        if not self._resolution.eligible_adapters:
            raise ValueError("HoloRouter has no eligible adapters after profile resolution")

        self.tenure_min = int(tenure_min or os.getenv("HOLOGOV_TENURE_MIN", DEFAULT_HOLOGOV_TENURE_MIN))
        self.tenure_max = int(tenure_max or os.getenv("HOLOGOV_TENURE_MAX", DEFAULT_HOLOGOV_TENURE_MAX))
        if self.tenure_min < 1 or self.tenure_max < self.tenure_min:
            raise ValueError("invalid HoloGov tenure window")

        if rng is not None:
            self._rng = rng
        else:
            seed_value = seed if seed is not None else os.getenv("HOLOCHAT_DNA_SEED")
            self._rng = random.Random(seed_value)

    @property
    def resolution(self) -> DnaProfileResolution:
        return self._resolution

    def select_route(
        self,
        holo_state: HoloState,
        *,
        previous_route: PreviousRoute | RouteDecision | None = None,
    ) -> RouteDecision:
        previous = self._coerce_previous(previous_route)
        pool = list(self._resolution.eligible_adapters)
        locked_gov = self._find_adapter(
            pool,
            previous.hologov_provider,
            previous.hologov_model,
        ) if previous.hologov_tenure_remaining > 0 else None

        council_pool = list(pool)
        if len(council_pool) > 1 and previous.council_provider and previous.council_model:
            filtered = [
                adapter for adapter in council_pool
                if adapter_identity(adapter) != AdapterIdentity(
                    previous.council_provider,
                    previous.council_model,
                )
            ]
            if filtered:
                council_pool = filtered

        if locked_gov and len({adapter_identity(a).provider for a in council_pool}) > 1:
            filtered = [
                adapter for adapter in council_pool
                if adapter_identity(adapter).provider != adapter_identity(locked_gov).provider
            ]
            if filtered:
                council_pool = filtered

        council = self._rng.choice(council_pool)
        council_id = adapter_identity(council)

        if locked_gov is not None:
            hologov = locked_gov
            tenure_remaining = max(0, previous.hologov_tenure_remaining - 1)
            gov_reason = "HoloGov tenure lock preserved"
        else:
            gov_pool = list(pool)
            if len({adapter_identity(a).provider for a in gov_pool}) > 1:
                filtered = [
                    adapter for adapter in gov_pool
                    if adapter_identity(adapter).provider != council_id.provider
                ]
                if filtered:
                    gov_pool = filtered
            hologov = self._rng.choice(gov_pool)
            tenure_remaining = self._rng.randint(self.tenure_min, self.tenure_max) - 1
            gov_reason = "HoloGov selected for new tenure"

        hologov_id = adapter_identity(hologov)
        assigned_role = self._assigned_role(holo_state)
        diversity_degraded = (
            self._resolution.dna_degraded
            or self._resolution.eligible_provider_count < 2
            or council_id.provider == hologov_id.provider
        )
        reasons = [
            f"profile={self._resolution.resolved_profile}",
            "serial_one_model_context",
            gov_reason,
        ]
        if previous.council_provider and previous.council_model:
            reasons.append("avoided_immediate_council_repeat_when_possible")
        if council_id.provider != hologov_id.provider:
            reasons.append("hologov_council_provider_separated")
        else:
            reasons.append("degraded_dna_diversity")

        return RouteDecision(
            council_provider=council_id.provider,
            council_model=council_id.model_id,
            hologov_provider=hologov_id.provider,
            hologov_model=hologov_id.model_id,
            assigned_role=assigned_role,
            route_reason="; ".join(reasons),
            fallback_used=self._resolution.fallback_used,
            fallback_reason=self._resolution.fallback_reason,
            dna_profile=self._resolution.resolved_profile,
            dna_degraded=diversity_degraded,
            eligible_provider_count=self._resolution.eligible_provider_count,
            previous_council_provider=previous.council_provider,
            previous_council_model=previous.council_model,
            hologov_tenure_remaining=tenure_remaining,
            hologov_tenure_window=(self.tenure_min, self.tenure_max),
        )

    @staticmethod
    def _coerce_previous(previous_route: PreviousRoute | RouteDecision | None) -> PreviousRoute:
        if previous_route is None:
            return PreviousRoute()
        if isinstance(previous_route, RouteDecision):
            return previous_route.as_previous_route()
        return previous_route

    @staticmethod
    def _find_adapter(
        adapters: Sequence[Any],
        provider: str | None,
        model_id: str | None,
    ) -> Any | None:
        if not provider or not model_id:
            return None
        identity = AdapterIdentity(provider, model_id)
        return next((adapter for adapter in adapters if adapter_identity(adapter) == identity), None)

    @staticmethod
    def _assigned_role(holo_state: HoloState) -> str:
        role = getattr(holo_state.baton_pass, "assigned_role", CouncilRole.DIRECT_SYNTHESIS)
        return str(role.value if isinstance(role, CouncilRole) else role)
