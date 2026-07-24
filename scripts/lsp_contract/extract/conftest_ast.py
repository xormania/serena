"""AST extraction of central test registration and evidence facts.\n\nThe repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.\n"""

from __future__ import annotations

import ast
from pathlib import Path

from scripts.lsp_contract.diagnostics import ExtractionError


def _parse(path: Path) -> ast.Module:
    """Parse central conftest source with location-bearing errors."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as error:
        line = getattr(error, "lineno", 1) or 1
        raise ExtractionError(path, line, f"could not parse conftest: {error}") from error


def _assignments(tree: ast.Module) -> dict[str, ast.AST]:
    """Top-level simple assignments by target name."""
    result: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            result[node.targets[0].id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            result[node.target.id] = node.value
    return result


def _member(node: ast.AST, path: Path) -> str:
    """LanguageServerId member name represented by *node*."""
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "LanguageServerId":
        return node.attr
    raise ExtractionError(path, getattr(node, "lineno", 1), "expected a literal LanguageServerId member")


def _member_sequence(node: ast.AST, path: Path) -> list[str]:
    """Literal sequence or set of LanguageServerId members."""
    if not isinstance(node, ast.List | ast.Tuple | ast.Set):
        raise ExtractionError(path, getattr(node, "lineno", 1), "expected a literal LanguageServerId collection")
    return [_member(element, path) for element in node.elts]


def _literal_strings(node: ast.AST, path: Path) -> list[str]:
    """Literal strings or pytest marker attributes."""
    if not isinstance(node, ast.List | ast.Tuple | ast.Set):
        raise ExtractionError(path, getattr(node, "lineno", 1), "expected a literal string collection")
    values: list[str] = []
    for element in node.elts:
        if isinstance(element, ast.Constant) and isinstance(element.value, str):
            values.append(element.value)
        elif isinstance(element, ast.Attribute):
            values.append(element.attr)
        else:
            raise ExtractionError(path, getattr(element, "lineno", 1), "expected a literal string or pytest marker")
    return values


def _alias_dict(node: ast.AST, path: Path) -> tuple[dict[str, str], list[list[object]]]:
    """Alias mapping plus duplicate-key evidence preserved from the AST."""
    if not isinstance(node, ast.Dict):
        raise ExtractionError(path, getattr(node, "lineno", 1), "_LANGUAGE_REPO_ALIASES must be a literal dict")
    aliases: dict[str, str] = {}
    first_lines: dict[str, int] = {}
    duplicates: list[list[object]] = []
    for key_node, value_node in zip(node.keys, node.values, strict=True):
        if key_node is None:
            raise ExtractionError(path, node.lineno, "dict expansion is not supported in aliases")
        key = _member(key_node, path)
        value = _member(value_node, path)
        if key in first_lines:
            duplicates.append([key, first_lines[key], key_node.lineno])
        else:
            first_lines[key] = key_node.lineno
        aliases[key] = value
    return aliases, duplicates


def _marker_dict(node: ast.AST, path: Path) -> dict[str, list[str]]:
    """Backend-to-marker mapping from a literal dictionary."""
    if not isinstance(node, ast.Dict):
        raise ExtractionError(path, getattr(node, "lineno", 1), "_LANGUAGE_PYTEST_MARKERS must be a literal dict")
    result: dict[str, list[str]] = {}
    for key_node, value_node in zip(node.keys, node.values, strict=True):
        if key_node is None:
            raise ExtractionError(path, node.lineno, "dict expansion is not supported in marker mapping")
        result[_member(key_node, path)] = _literal_strings(value_node, path)
    return result


def extract_conftest(path: Path) -> dict[str, object]:
    """Extract aliases, marker mappings, backend lists, and evidence sets."""
    assignments = _assignments(_parse(path))

    # require the central registration structures
    try:
        alias_node = assignments["_LANGUAGE_REPO_ALIASES"]
        marker_node = assignments["_LANGUAGE_PYTEST_MARKERS"]
        verified_node = assignments["_VERIFIED_IMPLEMENTATION_LANGUAGES"]
    except KeyError as error:
        raise ExtractionError(path, 1, f"missing required conftest assignment {error.args[0]}") from error

    aliases, duplicates = _alias_dict(alias_node, path)

    # retain every literal backend-selection list for drift comparison
    backend_lists: dict[str, list[str]] = {}
    for name, value in assignments.items():
        if "BACKEND" not in name or not isinstance(value, ast.List | ast.Tuple | ast.Set):
            continue
        try:
            backend_lists[name] = _member_sequence(value, path)
        except ExtractionError:
            continue

    return {
        "aliases": aliases,
        "rawDuplicateKeys": duplicates,
        "markerDict": _marker_dict(marker_node, path),
        "backendLists": backend_lists,
        "verifiedImplementationSet": sorted(_member_sequence(verified_node, path)),
    }
