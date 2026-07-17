"""Deterministic HoloChat onboarding import admission.

This module turns a user-pasted HoloBrain import packet into scoped context
writes without calling a model, search provider, or external service. The user
can review the result later, but ordinary onboarding should not stall on a
memory-by-memory approval chore.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
import re
from typing import Iterable


ONBOARDING_IMPORT_PROMPT = """I am setting up HoloChat, a persistent Personal workspace that preserves only the context I choose to keep. The areas I expect to use most are: {areas}.

Create a HoloBrain Import Packet from what you already know about me. This will be pasted into HoloChat so it can give me a useful beginning without making me explain everything again.

Important rules:
- Use only information I explicitly shared or directly confirmed.
- Do not infer motives, diagnose, flatter, fill gaps, or turn temporary ideas into stable facts.
- Separate Personal context from employer, client, team, organization, or deal information.
- Put uncertain, old, disputed, inferred, contradictory, or incomplete claims in Needs confirmation.
- Put sensitive items that should not be stored in Do not import.
- Do not include passwords, API keys, security answers, financial account numbers, government identifiers, full addresses, private medical records, identifiable patient or client information, privileged communications, or anything unsafe to store.

Return exactly these labeled sections:
1. Stable personal context
2. Current priorities
3. Working style
4. Important relationships and stakeholders
5. Constraints and boundaries
6. Open loops
7. Needs confirmation
8. Do not import

For each important item, write one short bullet with the fact or context, confidence (confirmed, user-stated, or needs confirmation), and recency when known. Keep it under 1,500 words. End with: "HoloChat should import the clear Personal context, quarantine uncertain items, and reject anything unsafe or Enterprise-confidential."
"""


class ImportDisposition(str, Enum):
    ADMIT = "admit"
    QUARANTINE = "quarantine"
    REJECT = "reject"


class ImportBucket(str, Enum):
    PERSONAL_PROFILE = "personal_profile"
    PERSONAL_PRIVATE = "personal_private"
    WORKING_STYLE = "working_style"
    CURRENT_PRIORITIES = "current_priorities"
    OPEN_LOOPS = "open_loops"
    BOUNDARIES = "boundaries"


@dataclass(frozen=True)
class ImportItem:
    item_id: str
    text: str
    section: str
    disposition: ImportDisposition
    reason: str
    bucket: ImportBucket | None = None


@dataclass(frozen=True)
class OnboardingImportResult:
    context_writes: dict[str, str]
    admitted: tuple[ImportItem, ...] = ()
    quarantined: tuple[ImportItem, ...] = ()
    rejected: tuple[ImportItem, ...] = ()
    review_required: bool = False
    review_available: bool = True
    no_external_calls: bool = True

    def summary(self) -> dict[str, object]:
        return {
            "admitted_count": len(self.admitted),
            "quarantined_count": len(self.quarantined),
            "rejected_count": len(self.rejected),
            "review_required": self.review_required,
            "review_available": self.review_available,
            "no_external_calls": self.no_external_calls,
        }


@dataclass
class _Section:
    name: str
    lines: list[str] = field(default_factory=list)


_SECTION_ALIASES = {
    "stable personal context": "stable_personal_context",
    "current priorities": "current_priorities",
    "working style": "working_style",
    "important relationships and stakeholders": "relationships",
    "constraints and boundaries": "boundaries",
    "open loops": "open_loops",
    "needs confirmation": "needs_confirmation",
    "do not import": "do_not_import",
}

_SECRET_RE = re.compile(
    r"\b(password|passcode|api key|secret key|security answer|ssn|social security|"
    r"account number|routing number|full address|private key|recovery phrase)\b",
    re.IGNORECASE,
)

_ENTERPRISE_CONFIDENTIAL_RE = re.compile(
    r"\b(client name|client identity|issuer|live deal|deal name|mandate|mnpi|nonpublic|"
    r"cap table|board deck|diligence finding|transaction status|confidential memo|"
    r"valuation file|investment committee material|ic material|revenue numbers|"
    r"portfolio holding|trade ticket)\b",
    re.IGNORECASE,
)

_GENERAL_WORK_RE = re.compile(
    r"\b(employer|role|job|works at|profession|career|associate|director|manager|"
    r"analyst|firm|company|work style)\b",
    re.IGNORECASE,
)

_PERSONAL_PRIVATE_RE = re.compile(
    r"\b(wife|husband|spouse|partner|child|children|son|daughter|kid|custody|school|"
    r"migraines?|medical|diagnosis|medication|therapy|disability|doctor|clinician|"
    r"marriage|family|legal trouble|conviction|arrest|addiction|trauma)\b",
    re.IGNORECASE,
)

_UNCERTAIN_RE = re.compile(
    r"\b(needs confirmation|unconfirmed|uncertain|maybe|might|likely|appears|seems|"
    r"inferred|possibly|old|outdated|contradictory|disputed)\b",
    re.IGNORECASE,
)


def onboarding_prompt_for_areas(labels: Iterable[str]) -> str:
    clean = [str(label).strip() for label in labels if str(label).strip()]
    areas = ", ".join(clean) if clean else "Personal, Work, Finance, Health, Family, and other important areas"
    return ONBOARDING_IMPORT_PROMPT.format(areas=areas)


def build_onboarding_context_writes(
    imported_context: str,
    *,
    selected_areas: Iterable[str] = (),
) -> OnboardingImportResult:
    """Return deterministic context writes for a pasted HoloBrain packet."""
    source = _normalize(imported_context)
    if not source:
        return OnboardingImportResult(context_writes={})

    sections = _parse_sections(source)
    admitted: list[ImportItem] = []
    quarantined: list[ImportItem] = []
    rejected: list[ImportItem] = []

    for section in sections:
        for line in section.lines:
            item = _classify_line(line, section.name)
            if item.disposition is ImportDisposition.ADMIT:
                admitted.append(item)
            elif item.disposition is ImportDisposition.QUARANTINE:
                quarantined.append(item)
            else:
                rejected.append(item)

    writes: dict[str, str] = {
        "holo_onboarding_import_v1": _compact_json({
            "source_hash": sha256(source.encode("utf-8")).hexdigest(),
            "selected_areas": [str(area).strip() for area in selected_areas if str(area).strip()],
            "summary": {
                "admitted_count": len(admitted),
                "quarantined_count": len(quarantined),
                "rejected_count": len(rejected),
            },
            "policy": "personal_import_auto_admit_with_quarantine_and_rejects",
        }),
        "holo_personal_enterprise_boundary_v1": (
            "HoloPersonal may remember general professional context and how work affects the person, "
            "but must not retain client names, issuer names, live deal facts, confidential files, "
            "nonpublic financials, or formal Enterprise records. HoloEnterprise may receive only "
            "minimal user-authorized availability signals from Personal, never family or medical details."
        ),
    }

    grouped: dict[ImportBucket, list[str]] = {bucket: [] for bucket in ImportBucket}
    for item in admitted:
        if item.bucket:
            grouped[item.bucket].append(item.text)

    _write_bucket(writes, "holo_personal_profile_v1", grouped[ImportBucket.PERSONAL_PROFILE])
    _write_bucket(writes, "holo_personal_private_v1", grouped[ImportBucket.PERSONAL_PRIVATE])
    _write_bucket(writes, "holo_working_style_v1", grouped[ImportBucket.WORKING_STYLE])
    _write_bucket(writes, "holo_current_priorities_v1", grouped[ImportBucket.CURRENT_PRIORITIES])
    _write_bucket(writes, "holo_open_loops_v1", grouped[ImportBucket.OPEN_LOOPS])
    _write_bucket(writes, "holo_boundaries_v1", grouped[ImportBucket.BOUNDARIES])

    if quarantined:
        writes["holo_onboarding_quarantine_v1"] = _compact_json([
            {"text": item.text, "section": item.section, "reason": item.reason}
            for item in quarantined
        ])
    if rejected:
        writes["holo_onboarding_rejected_v1"] = _compact_json([
            {"text": item.text, "section": item.section, "reason": item.reason}
            for item in rejected
        ])

    return OnboardingImportResult(
        context_writes=writes,
        admitted=tuple(admitted),
        quarantined=tuple(quarantined),
        rejected=tuple(rejected),
    )


def _classify_line(line: str, section: str) -> ImportItem:
    clean = _strip_bullet(line)
    item_id = sha256(f"{section}:{clean}".encode("utf-8")).hexdigest()[:16]

    if not clean:
        return ImportItem(item_id, clean, section, ImportDisposition.REJECT, "empty")
    if _SECRET_RE.search(clean):
        return ImportItem(item_id, clean, section, ImportDisposition.REJECT, "unsafe_secret_or_identifier")
    if section == "do_not_import":
        return ImportItem(item_id, clean, section, ImportDisposition.REJECT, "explicit_do_not_import")
    if _ENTERPRISE_CONFIDENTIAL_RE.search(clean):
        return ImportItem(item_id, clean, section, ImportDisposition.REJECT, "enterprise_confidential_not_valid_in_personal_import")
    if section == "needs_confirmation" or _UNCERTAIN_RE.search(clean):
        return ImportItem(item_id, clean, section, ImportDisposition.QUARANTINE, "needs_confirmation")

    if _PERSONAL_PRIVATE_RE.search(clean):
        return ImportItem(
            item_id, clean, section, ImportDisposition.ADMIT,
            "personal_private_user_import", ImportBucket.PERSONAL_PRIVATE,
        )
    if section == "working_style":
        return ImportItem(item_id, clean, section, ImportDisposition.ADMIT, "working_style", ImportBucket.WORKING_STYLE)
    if section == "current_priorities":
        return ImportItem(item_id, clean, section, ImportDisposition.ADMIT, "current_priority", ImportBucket.CURRENT_PRIORITIES)
    if section == "open_loops":
        return ImportItem(item_id, clean, section, ImportDisposition.ADMIT, "open_loop", ImportBucket.OPEN_LOOPS)
    if section == "boundaries":
        return ImportItem(item_id, clean, section, ImportDisposition.ADMIT, "personal_boundary", ImportBucket.BOUNDARIES)
    if section == "relationships":
        return ImportItem(
            item_id, clean, section, ImportDisposition.ADMIT,
            "relationship_context_private_by_default", ImportBucket.PERSONAL_PRIVATE,
        )
    if _GENERAL_WORK_RE.search(clean):
        return ImportItem(
            item_id, clean, section, ImportDisposition.ADMIT,
            "general_professional_context_only", ImportBucket.PERSONAL_PROFILE,
        )
    return ImportItem(item_id, clean, section, ImportDisposition.ADMIT, "stable_personal_context", ImportBucket.PERSONAL_PROFILE)


def _parse_sections(text: str) -> tuple[_Section, ...]:
    current = _Section("stable_personal_context")
    sections: list[_Section] = [current]

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        header = _section_header(line)
        if header:
            current = _Section(header)
            sections.append(current)
            continue
        current.lines.append(line)
    return tuple(section for section in sections if section.lines)


def _section_header(line: str) -> str | None:
    normalized = re.sub(r"^[#*\-\s\d.]+", "", line).strip().strip(":").lower()
    return _SECTION_ALIASES.get(normalized)


def _normalize(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", str(text or "").replace("\r\n", "\n")).strip()


def _strip_bullet(line: str) -> str:
    return re.sub(r"^\s*(?:[-*+]|\d+[.)])\s*", "", line).strip()


def _write_bucket(writes: dict[str, str], key: str, values: list[str]) -> None:
    if values:
        writes[key] = _compact_json(values)


def _compact_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
