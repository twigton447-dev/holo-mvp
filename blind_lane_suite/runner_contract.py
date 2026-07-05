"""Contract binding for a future blind runner (built by Codex, not this suite).

A candidate blind runner registers via env var BLIND_RUNNER_MODULE, naming an
importable module that must expose:

  run_blind_fixture(payload: dict, transcripts: list[str], out_dir: str,
                    transport=None) -> dict
      Runs the blind pipeline over one packet payload using recorded mock
      transcripts (no providers). `transport`, when given, is a callable
      (prompt_messages) -> str used instead of transcripts, so tests can
      inject failing transports. Returns a run-result dict containing at
      minimum: "prompts" (list of message-lists actually built),
      "worker_rows" (each with raw_output_sha256, artifact_text, gate_result),
      "final" ({"verdict", "artifact_id"}), "retry_log" (list of
      {"kind": "transport"|..., "attempt": int}).

  select_final(artifacts: list[dict]) -> dict
      Pure final-selector. Returns {"selected_artifact_id", "criteria_trace"}.

  SELECTOR_CRITERIA: tuple[str, ...]
      Closed-form ordered criteria names.

  apply_criteria(artifacts: list[dict]) -> dict
      Independent recomputation of the selection from SELECTOR_CRITERIA only.

  BUDGET_LIMITS: dict
      {"max_worker_turns_per_packet": int, "max_calls_per_packet": int,
       "transport_retry_limit": int, "max_output_tokens": int}

  run_blind_runtime_manifest(runtime_manifest_path: str, out_dir: str,
                             transport) -> dict
      Live-canary executor surface. Loads only the runtime manifest and opaque
      runtime payload files, calls the supplied transport, and writes frozen
      traces/results. This is required so filesystem-isolation tests bind to
      the same loader/executor that will be used for live providers.

Absent registration, contract tests SKIP with an explicit warning that the
skip is not a pass. A registered module missing any attribute FAILS (contract
violation), it does not skip.
"""

from __future__ import annotations

import importlib
import os

from . import BLIND_RUNNER_ENV

REQUIRED_ATTRS = (
    "run_blind_fixture",
    "select_final",
    "apply_criteria",
    "SELECTOR_CRITERIA",
    "BUDGET_LIMITS",
    "run_blind_runtime_manifest",
)

SKIP_REASON = (
    "BLIND RUNNER NOT REGISTERED (set {env}). Test NOT executed. "
    "A skip is NOT a pass; do not report this test green.".format(env=BLIND_RUNNER_ENV)
)


def load_runner():
    """Return (module, missing_attrs). module is None when unregistered."""
    name = os.environ.get(BLIND_RUNNER_ENV, "").strip()
    if not name:
        return None, []
    mod = importlib.import_module(name)  # import errors surface as test errors
    missing = [a for a in REQUIRED_ATTRS if not hasattr(mod, a)]
    return mod, missing


def runner_source_path(mod) -> str | None:
    return getattr(mod, "__file__", None)
