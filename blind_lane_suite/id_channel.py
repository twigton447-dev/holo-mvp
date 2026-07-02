"""T1 - ID-channel mutual-information scan.

Falsifies: "no runtime component receives an identifier from which packet
truth is derivable."

Two detectors:
  1. suffix_channel  - any ID-like token ending in -A/-B inside model-visible
     message content (the corpus-wide convention -A=ALLOW / -B=ESCALATE makes
     this a literal 1-bit answer key).
  2. deterministic_tokens - any token appearing in >= min_pairs distinct pairs
     that always co-occurs with one truth side (catches truth-correlated
     re-keying schemes that avoid literal A/B suffixes).

Passing does NOT show payload *content* carries no truth signal.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

# Token that looks like a packet/sibling ID and ends in the truth suffix.
SUFFIXED_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+-(?:A|B)\b")
# Generic ID-like token (two or more dash-joined uppercase/digit segments).
ID_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,}(?:-[A-Z0-9]{2,}){1,}\b")


def truth_from_packet_id(packet_id: str) -> str | None:
    if packet_id.endswith("-A"):
        return "ALLOW"
    if packet_id.endswith("-B"):
        return "ESCALATE"
    return None


def packet_id_from_prompt_filename(name: str) -> str:
    # e.g. HV-DPRV-REP-009-A_W1.json -> HV-DPRV-REP-009-A
    stem = name[: -len(".json")] if name.endswith(".json") else name
    return stem.rsplit("_", 1)[0]


def model_visible_text(prompt_obj) -> str:
    msgs = prompt_obj.get("messages", []) if isinstance(prompt_obj, dict) else []
    return "\n".join(str(m.get("content", "")) for m in msgs if isinstance(m, dict))


def scan_prompt_dir(prompt_dir: Path | str) -> dict:
    prompt_dir = Path(prompt_dir)
    suffix_hits: list[dict] = []
    token_pairs: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    files = sorted(prompt_dir.glob("*.json"))
    for path in files:
        try:
            text = model_visible_text(json.loads(path.read_text(errors="replace")))
        except Exception:
            continue
        pid = packet_id_from_prompt_filename(path.name)
        truth = truth_from_packet_id(pid)
        pair = pid[:-2] if truth else pid
        for tok in sorted(set(SUFFIXED_ID_RE.findall(text))):
            suffix_hits.append({"file": path.name, "token": tok})
        if truth:
            for tok in set(ID_TOKEN_RE.findall(text)):
                token_pairs[tok][truth].add(pair)
    return {
        "prompt_files_scanned": len(files),
        "suffix_channel_hits": suffix_hits,
        "_token_pairs": token_pairs,
    }


def deterministic_tokens(token_pairs, min_pairs: int = 3) -> list[dict]:
    out = []
    for tok, by_truth in token_pairs.items():
        truths = [t for t, pairs in by_truth.items() if pairs]
        support = sum(len(p) for p in by_truth.values())
        if len(truths) == 1 and support >= min_pairs:
            out.append({"token": tok, "always_truth": truths[0], "pair_support": support})
    return sorted(out, key=lambda r: -r["pair_support"])


def id_channel_report(prompt_dir: Path | str, min_pairs: int = 3) -> dict:
    scan = scan_prompt_dir(prompt_dir)
    det = deterministic_tokens(scan.pop("_token_pairs"), min_pairs=min_pairs)
    violation = bool(scan["suffix_channel_hits"] or det)
    return {
        "prompt_dir": str(prompt_dir),
        "prompt_files_scanned": scan["prompt_files_scanned"],
        "suffix_channel_hits": scan["suffix_channel_hits"][:50],
        "suffix_channel_hit_count": len(scan["suffix_channel_hits"]),
        "deterministic_tokens": det[:50],
        "violation": violation,
    }
