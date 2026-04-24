"""
benchmark_telemetry.py

Captures and exports structured telemetry for a Holo full-architecture run.
Exports one JSON file per scenario run to benchmark_results/telemetry/.

Filename format: telemetry_YYYYMMDD_HHMMSS_<scenario_name>.json

Data captured per run:
  - Turn-by-turn trace: model_name, model_family, role, verdict,
    severity_flags, raw_output, reasoning, token_counts, logprobs (if available)
  - Governor brief log: for_turn, convergence_level, brief_output, driver_family
  - Cosine similarity between consecutive turn outputs via OpenAI text-embedding-3-small.
    All model families embed through the same endpoint so comparisons are cross-architecture.
    If embeddings are unavailable the field is null and the reason is recorded.
  - Entropy per turn derived from flag severity distribution (logprobs not available
    from Anthropic or Google APIs; OpenAI JSON response mode suppresses them too).
  - Model family assignment map with consecutive-same-family violation check.
"""

import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

TELEMETRY_DIR = Path("benchmark_results/telemetry")

SEVERITY_RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

PROVIDER_TO_FAMILY = {
    "openai":    "openai",
    "anthropic": "anthropic",
    "google":    "google",
    "xai":       "xai",
    "mistral":   "mistral",
    "deepseek":  "deepseek",
    "minimax":   "minimax",
}

FAMILY_COLORS = {
    "openai":    "#74b9ff",
    "anthropic": "#a29bfe",
    "google":    "#55efc4",
    "xai":       "#fd79a8",
    "mistral":   "#fdcb6e",
    "deepseek":  "#e17055",
    "minimax":   "#00cec9",
    "unknown":   "#b2bec3",
}


def _model_family(provider: str) -> str:
    return PROVIDER_TO_FAMILY.get(provider.lower(), "unknown")


def _severity_entropy(severity_flags: dict) -> float:
    """
    Shannon entropy over the severity rank distribution for a turn's flags.

    Each category maps to a rank 0-3. The distribution of ranks across
    categories is treated as a discrete probability distribution.

    High entropy = many distinct severity levels active (uncertainty).
    Low entropy = all categories converged to the same level (certainty).

    This is the proxy metric when logprobs are unavailable (Anthropic, Google,
    and OpenAI in JSON response mode all suppress token-level probabilities).
    """
    ranks = [SEVERITY_RANK.get(v, 0) for v in severity_flags.values()]
    total = len(ranks)
    if total == 0:
        return 0.0
    counts: dict[int, int] = {}
    for r in ranks:
        counts[r] = counts.get(r, 0) + 1
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return round(entropy, 6)


def _normalized_severity(severity_flags: dict) -> float:
    """Mean severity rank across all categories, normalized to 0.0–1.0."""
    ranks = [SEVERITY_RANK.get(v, 0) for v in severity_flags.values()]
    if not ranks:
        return 0.0
    return round(sum(ranks) / (len(ranks) * 3), 6)


def _compute_embeddings(texts: list[str], api_key: str) -> Optional[list[list[float]]]:
    """
    Embed texts via OpenAI text-embedding-3-small.

    All model families are embedded through the same endpoint so that cosine
    similarity scores are comparable across architectures. This is intentional:
    we are measuring semantic convergence in a shared vector space, not within
    each model's own representation.

    Returns None if the call fails; the caller records the failure reason.
    """
    if not api_key or not texts:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return [item.embedding for item in response.data]
    except Exception:
        return None


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Standard cosine similarity. Returns 0.0 for zero-norm vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    return round(dot / (n1 * n2), 8)


def _verify_family_constraint(family_map: list[dict]) -> dict:
    """
    Check that no two consecutive turns share the same model family.
    Returns a summary including any violations found.
    """
    violations = []
    for i in range(1, len(family_map)):
        if family_map[i]["model_family"] == family_map[i - 1]["model_family"]:
            violations.append({
                "turn_a": family_map[i - 1]["turn_number"],
                "turn_b": family_map[i]["turn_number"],
                "family": family_map[i]["model_family"],
            })
    return {
        "constraint_satisfied": len(violations) == 0,
        "violations": violations,
    }


def build_telemetry(
    scenario_name: str,
    holo_result: dict,
    governor_briefs: list,
    openai_api_key: Optional[str] = None,
) -> dict:
    """
    Build the complete telemetry dict from a holo_full condition result.

    holo_result    — the dict returned by _ok() for condition "holo_full"
    governor_briefs — list of {for_turn, brief, convergence_level} dicts
                      (sourced from result["extra"]["governor_briefs"])
    openai_api_key — used for embedding calls (cross-architecture cosine similarity)
    """
    turn_log = holo_result.get("turn_log", [])
    if not turn_log:
        return {
            "schema_version": "1.0",
            "scenario_name":  scenario_name,
            "generated_at":   datetime.utcnow().isoformat() + "Z",
            "error":          "no turn_log in holo_result",
        }

    # ---- Per-turn structured data -------------------------------------------
    turns = []
    texts_for_embedding = []

    for t in turn_log:
        flags = t.get("severity_flags", {})
        entry = {
            "turn_number":             t.get("turn_number"),
            "model_name":              t.get("model_id", t.get("provider", "unknown")),
            "model_family":            _model_family(t.get("provider", "")),
            "role":                    t.get("role"),
            "verdict":                 t.get("verdict"),
            "severity_flags":          flags,
            "raw_output":              t.get("raw_response", ""),
            "reasoning":               t.get("reasoning", ""),
            "input_tokens":            t.get("input_tokens", 0),
            "output_tokens":           t.get("output_tokens", 0),
            "logprobs":                t.get("logprobs"),
            "delta":                   t.get("delta"),
            "temperature":             t.get("temperature"),
            "convergence_level_after": t.get("convergence_level_after"),
            "signal":                  t.get("signal", {}),
            # Entropy proxy (flag severity distribution)
            "severity_entropy":        _severity_entropy(flags),
            "normalized_severity":     _normalized_severity(flags),
            # Logprob entropy: placeholder — populated if logprobs are present
            "logprob_entropy":         None,
            # Cosine similarity to previous turn — filled after embedding pass
            "cosine_similarity_prev":  None,
        }
        # If logprobs were captured (future: OpenAI non-JSON mode), compute real entropy
        if t.get("logprobs") and isinstance(t["logprobs"], list):
            try:
                lp = [lp_val for lp_val in t["logprobs"] if lp_val is not None]
                if lp:
                    probs = [math.exp(v) for v in lp]
                    total_p = sum(probs)
                    if total_p > 0:
                        probs = [p / total_p for p in probs]
                        entry["logprob_entropy"] = round(
                            -sum(p * math.log2(p) for p in probs if p > 0), 6
                        )
            except Exception:
                pass

        turns.append(entry)
        # Use reasoning for embeddings; fall back to raw_output if reasoning is empty
        embed_text = t.get("reasoning") or t.get("raw_response") or ""
        texts_for_embedding.append(embed_text)

    # ---- Embeddings + cosine similarity -------------------------------------
    embeddings_available = False
    embedding_model = None
    embedding_note = None
    embeddings: Optional[list] = None

    if openai_api_key and texts_for_embedding:
        embeddings = _compute_embeddings(texts_for_embedding, openai_api_key)
        if embeddings:
            embeddings_available = True
            embedding_model = "text-embedding-3-small"
            embedding_note = (
                "All model families embedded via OpenAI text-embedding-3-small "
                "in a shared 1536-dim vector space. Cosine similarity scores "
                "are cross-architecture — not within each model's own latent space."
            )
            for i in range(1, len(turns)):
                turns[i]["cosine_similarity_prev"] = _cosine_similarity(
                    embeddings[i - 1], embeddings[i]
                )
        else:
            embedding_note = (
                "OpenAI embedding call failed. "
                "Cosine similarity values are null. "
                "Check OPENAI_API_KEY and network access."
            )
    elif not openai_api_key:
        embedding_note = (
            "OPENAI_API_KEY not set. Cosine similarity unavailable. "
            "Anthropic and Google do not expose public embedding endpoints."
        )
    else:
        embedding_note = "No turn text available for embedding."

    # ---- Model family assignment map ----------------------------------------
    family_map = [
        {
            "turn_number":  t["turn_number"],
            "model_family": t["model_family"],
            "model_name":   t["model_name"],
            "role":         t["role"],
            "verdict":      t["verdict"],
            "color":        FAMILY_COLORS.get(t["model_family"], FAMILY_COLORS["unknown"]),
        }
        for t in turns
    ]

    family_constraint = _verify_family_constraint(family_map)

    # ---- Convergence curve data series (Panel 1) ----------------------------
    convergence_series = [
        {
            "turn":               t["turn_number"],
            "cosine_similarity":  t["cosine_similarity_prev"],
            "model_family":       t["model_family"],
            "verdict":            t["verdict"],
        }
        for t in turns
        if t["turn_number"] is not None and t["turn_number"] > 1
    ]

    # ---- Entropy decay data series (Panel 2) --------------------------------
    entropy_series = [
        {
            "turn":                t["turn_number"],
            "severity_entropy":    t["severity_entropy"],
            "logprob_entropy":     t["logprob_entropy"],
            "normalized_severity": t["normalized_severity"],
            "verdict":             t["verdict"],
            "model_family":        t["model_family"],
        }
        for t in turns
    ]

    # ---- Governor brief log -------------------------------------------------
    governor_brief_log = []
    for b in sorted(governor_briefs or [], key=lambda x: x.get("for_turn", 0)):
        target_turn = b.get("for_turn", 0)
        driver_family = None
        if 0 < target_turn <= len(family_map):
            driver_family = family_map[target_turn - 1]["model_family"]
        governor_brief_log.append({
            "for_turn":          target_turn,
            "convergence_level": b.get("convergence_level"),
            "brief_output":      b.get("brief", ""),
            "driver_family":     driver_family,
            "driver_model":      family_map[target_turn - 1]["model_name"]
                                 if 0 < target_turn <= len(family_map) else None,
        })

    # Strip embeddings from turn entries (large vectors — visualization doesn't need them)
    # They were only needed locally for cosine similarity computation above.
    for t in turns:
        t.pop("embedding", None)

    return {
        "schema_version": "1.0",
        "scenario_name":  scenario_name,
        "generated_at":   datetime.utcnow().isoformat() + "Z",
        "verdict":        holo_result.get("verdict"),
        "turns_run":      holo_result.get("turns_run"),
        "run_health":     holo_result.get("run_health"),
        "deltas":         holo_result.get("extra", {}).get("deltas", []),
        "coverage_matrix": holo_result.get("extra", {}).get("coverage_matrix", {}),
        "threat_hypothesis": holo_result.get("extra", {}).get("threat_hypothesis", ""),

        # Architecture proof: no two consecutive turns share the same model family
        "architecture_proof": {
            "consecutive_same_family_constraint": family_constraint,
            "model_family_assignment_map":        family_map,
            "family_colors":                      FAMILY_COLORS,
        },

        # Embedding metadata
        "embeddings": {
            "available": embeddings_available,
            "model":     embedding_model,
            "note":      embedding_note,
        },

        # Turn-by-turn structured trace
        "turns": turns,

        # Visualization-ready data series
        "convergence_series": convergence_series,
        "entropy_series":     entropy_series,

        # Governor brief log (input + output per between-turn call)
        "governor_brief_log": governor_brief_log,
    }


def export_telemetry(
    scenario_name: str,
    holo_result: dict,
    governor_briefs: list,
    openai_api_key: Optional[str] = None,
) -> Path:
    """Build telemetry, write JSON, return output path."""
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"telemetry_{ts}_{scenario_name}.json"
    output_path = TELEMETRY_DIR / filename

    print(f"\n  Building telemetry for {scenario_name}...")
    telemetry = build_telemetry(scenario_name, holo_result, governor_briefs, openai_api_key)

    if telemetry.get("embeddings", {}).get("available"):
        print(f"    Embeddings : {telemetry['embeddings']['model']} — cosine similarity computed")
    else:
        print(f"    Embeddings : unavailable — {telemetry.get('embeddings', {}).get('note', '')}")

    constraint = telemetry.get("architecture_proof", {}).get(
        "consecutive_same_family_constraint", {}
    )
    if constraint.get("constraint_satisfied"):
        print(f"    Family map : constraint satisfied — no consecutive same-family turns")
    else:
        viol = constraint.get("violations", [])
        print(f"    Family map : {len(viol)} violation(s) detected")

    with open(output_path, "w") as f:
        json.dump(telemetry, f, indent=2)

    print(f"    Telemetry  : {output_path}")
    return output_path
