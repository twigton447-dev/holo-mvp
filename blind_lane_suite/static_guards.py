"""T2/T3 static guards - AST truth-reachability scan.

Falsifies: "no runtime-reachable code path can read truth-bearing spec fields
or derive a verdict from the sibling suffix."

Detector-validation: run against the known-leaky governed runner
(docs/benchmark/run_20pair_holoverify_3dna_2026_06_29.py) and EXPECT findings.
A scanner that reports the governed runner clean is itself broken.

Passing does NOT show fields added later stay unreachable; re-run on every
runner change.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

FORBIDDEN_FIELD_NAMES = {
    "knew_terms",
    "allow_rule",
    "esc_rule",
    "packet_truth",
    "hypothesized_verdict",
    "expected_verdict_for_local_gate",
}

FORBIDDEN_CALL_NAMES = {
    "_normalize_worker_artifact_after_gate",
    "_gate_repair_directive",
    "_enforce_gov_gate_compliance",
    "_worker_expected_binding",
}

VERDICT_LITERALS = {"ALLOW", "ESCALATE"}


def _names_in(node) -> list[str]:
    return [n.id for n in ast.walk(node) if isinstance(n, ast.Name)]


def _consts_in(node) -> list:
    return [c.value for c in ast.walk(node) if isinstance(c, ast.Constant)]


def scan_source_for_truth_reachability(path: Path | str) -> list[dict]:
    """Return findings; empty list == no detected truth reachability."""
    path = Path(path)
    findings: list[dict] = []
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except SyntaxError as e:
        return [{"kind": "unparseable_source", "detail": str(e)[:120], "line": 0}]

    for node in ast.walk(tree):
        line = getattr(node, "lineno", 0)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in FORBIDDEN_FIELD_NAMES:
                findings.append({"kind": "forbidden_field_string", "name": node.value, "line": line})
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_FIELD_NAMES:
            findings.append({"kind": "forbidden_field_name", "name": node.id, "line": line})
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_FIELD_NAMES:
            findings.append({"kind": "forbidden_field_attr", "name": node.attr, "line": line})
        elif isinstance(node, ast.Call):
            fn = node.func
            fn_name = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else None
            if fn_name in FORBIDDEN_CALL_NAMES:
                findings.append({"kind": "forbidden_call", "name": fn_name, "line": line})
        elif isinstance(node, ast.FunctionDef) and node.name in FORBIDDEN_CALL_NAMES:
            findings.append({"kind": "forbidden_def", "name": node.name, "line": line})

        # suffix -> verdict derivation: any expression comparing a *suffix*-ish
        # name to "A"/"B" while ALLOW/ESCALATE appears in the same statement,
        # or a conditional expression selecting verdict literals on a suffix test.
        if isinstance(node, (ast.IfExp, ast.If, ast.Compare)):
            names = [n.lower() for n in _names_in(node)]
            consts = _consts_in(node)
            suffixish = any("suffix" in n or "sibling" in n for n in names)
            ab = any(c in ("A", "B") for c in consts)
            verdicts = any(c in VERDICT_LITERALS for c in consts)
            if suffixish and ab and (verdicts or isinstance(node, ast.IfExp)):
                findings.append({"kind": "suffix_verdict_derivation", "line": line})
    return findings


def _module_to_repo_path(module_name: str, repo_root: Path) -> Path | None:
    if not module_name:
        return None
    top = module_name.split(".", 1)[0]
    if top in getattr(sys, "stdlib_module_names", set()):
        return None
    rel = Path(*module_name.split("."))
    candidates = [
        repo_root / f"{rel}.py",
        repo_root / rel / "__init__.py",
    ]
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if resolved.exists():
            return resolved
    return None


def _imports_in_source(path: Path, repo_root: Path) -> list[Path]:
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except SyntaxError:
        return []

    imports: list[Path] = []
    package_parts = path.relative_to(repo_root).with_suffix("").parts[:-1]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found = _module_to_repo_path(alias.name, repo_root)
                if found:
                    imports.append(found)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base_parts = list(package_parts[: max(0, len(package_parts) - node.level + 1)])
                if node.module:
                    base_parts.extend(node.module.split("."))
                base = ".".join(base_parts)
            else:
                base = node.module or ""
            found = _module_to_repo_path(base, repo_root)
            if found:
                imports.append(found)
            for alias in node.names:
                if alias.name == "*":
                    continue
                child = f"{base}.{alias.name}" if base else alias.name
                found_child = _module_to_repo_path(child, repo_root)
                if found_child:
                    imports.append(found_child)
    return imports


def source_import_closure(path: Path | str, repo_root: Path | str | None = None) -> list[Path]:
    """Return repo-local Python sources reachable from imports, including path."""
    start = Path(path).resolve()
    root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    seen: set[Path] = set()
    ordered: list[Path] = []
    stack = [start]
    while stack:
        current = stack.pop()
        try:
            current = current.resolve()
            current.relative_to(root)
        except ValueError:
            continue
        if current in seen or not current.exists():
            continue
        seen.add(current)
        ordered.append(current)
        for imported in reversed(_imports_in_source(current, root)):
            if imported not in seen:
                stack.append(imported)
    return ordered


def scan_import_closure_for_truth_reachability(
    path: Path | str,
    repo_root: Path | str | None = None,
) -> list[dict]:
    findings: list[dict] = []
    for source in source_import_closure(path, repo_root=repo_root):
        for finding in scan_source_for_truth_reachability(source):
            findings.append({**finding, "source": str(source)})
    return findings
