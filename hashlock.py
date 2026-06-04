"""
hashlock.py — Cryptographic integrity layer for the Holo benchmark protocol.

Stateless. No imports from pipeline code. No business logic.

Hash boundary — INCLUDED:
  action + context keys from the packet dict (model-visible content only)
  system prompt text (exact model-visible instruction string)

Hash boundary — EXCLUDED from packet hash (never model-visible):
  expected_verdict, hidden_ground_truth, gold_answer, scoring_targets
  hypothesized_verdict, builder_rationale, builder_notes
  judge_*, benchmark_status, model_labels, freeze_record
  scenario_id, domain, scenario_type, fp_freeze_state, fp_freeze_metadata
  _payload_file, and any key not in {"action", "context"}
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any


_MODEL_VISIBLE_KEYS = ("action", "context")


@dataclass(frozen=True)
class FreezeRecord:
    frozen_packet_hash:   str
    frozen_prompt_hash:   str
    combined_freeze_hash: str
    frozen_at:            str
    freeze_confirmed_by:  str


def canonical_serialize_packet(packet: dict[str, Any]) -> str:
    """
    Canonical JSON of the model-visible packet content.
    Extracts only action + context. Sorted keys, no extra whitespace.
    All metadata keys are silently dropped regardless of presence.
    """
    model_visible = {k: packet[k] for k in _MODEL_VISIBLE_KEYS if k in packet}
    return json.dumps(model_visible, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def canonical_serialize_prompt(system_prompt: str) -> str:
    """
    Normalize prompt text to a deterministic canonical form.
    Strips leading/trailing whitespace; normalizes all line endings to LF.
    """
    return system_prompt.strip().replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_packet_hash(packet: dict[str, Any]) -> str:
    return sha256_text(canonical_serialize_packet(packet))


def compute_prompt_hash(prompt: str) -> str:
    return sha256_text(canonical_serialize_prompt(prompt))


def compute_combined_freeze_hash(packet_hash: str, prompt_hash: str) -> str:
    """
    Combined hash over the two pre-computed component hashes.
    Separator "|" is safe because SHA-256 hex output never contains "|".
    """
    return sha256_text(packet_hash + "|" + prompt_hash)


def verify_freeze(
    packet: dict[str, Any],
    prompt: str,
    freeze_record: FreezeRecord,
) -> bool:
    """
    Return True iff all three hashes match the freeze record. Does not raise.
    A False return means the packet or prompt was mutated after freeze.
    """
    actual_packet   = compute_packet_hash(packet)
    actual_prompt   = compute_prompt_hash(prompt)
    actual_combined = compute_combined_freeze_hash(actual_packet, actual_prompt)
    return (
        actual_packet   == freeze_record.frozen_packet_hash
        and actual_prompt   == freeze_record.frozen_prompt_hash
        and actual_combined == freeze_record.combined_freeze_hash
    )
