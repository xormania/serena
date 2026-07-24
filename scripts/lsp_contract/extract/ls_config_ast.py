"""AST extraction of language-server identity, matcher, and dispatch facts.\n\nThe repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.\n"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from scripts.lsp_contract.diagnostics import ExtractionError


def _parse(path: Path) -> ast.Module:
    """Parse *path* or raise a location-bearing extraction error."""
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as error:
        line = getattr(error, "lineno", 1) or 1
        raise ExtractionError(path, line, f"could not parse Python source: {error}") from error


def _language_class(tree: ast.Module, path: Path) -> ast.ClassDef:
    """Find the single `LanguageServerId` class."""
    matches = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "LanguageServerId"]
    if len(matches) != 1:
        raise ExtractionError(path, 1, f"expected one LanguageServerId class, found {len(matches)}")
    return matches[0]


def _method(language_class: ast.ClassDef, name: str, path: Path) -> ast.FunctionDef:
    """Find a required method on the language enum."""
    matches = [node for node in language_class.body if isinstance(node, ast.FunctionDef) and node.name == name]
    if len(matches) != 1:
        raise ExtractionError(path, language_class.lineno, f"expected one LanguageServerId.{name} method")
    return matches[0]


def _pattern_members(pattern: ast.pattern, path: Path) -> list[str]:
    """Extract `self.MEMBER` names from a match pattern."""
    if isinstance(pattern, ast.MatchOr):
        members: list[str] = []
        for child in pattern.patterns:
            members.extend(_pattern_members(child, path))
        return members
    if isinstance(pattern, ast.MatchValue) and isinstance(pattern.value, ast.Attribute):
        attribute = pattern.value
        if isinstance(attribute.value, ast.Name) and attribute.value.id == "self":
            return [attribute.attr]
    if isinstance(pattern, ast.MatchAs) and pattern.name is None:
        return []
    raise ExtractionError(path, getattr(pattern, "lineno", 1), "unsupported LanguageServerId match pattern")


def _enum_members(language_class: ast.ClassDef, path: Path) -> tuple[list[str], dict[str, str]]:
    """Extract enum symbols and serialized values in declaration order."""
    symbols: list[str] = []
    values: dict[str, str] = {}
    for node in language_class.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        symbol = node.targets[0].id
        if not symbol.isupper():
            continue
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            raise ExtractionError(path, node.lineno, f"enum member {symbol} is not a literal string")
        symbols.append(symbol)
        values[symbol] = node.value.value
    if not symbols:
        raise ExtractionError(path, language_class.lineno, "LanguageServerId has no literal members")
    return symbols, values


def _membership_set(method: ast.FunctionDef, *, negated: bool, path: Path) -> list[str]:
    """Extract a literal `self [not] in {self.X}` return expression."""
    for node in ast.walk(method):
        if not isinstance(node, ast.Return):
            continue
        comparison = node.value
        if not isinstance(comparison, ast.Compare):
            continue
        operator_type = ast.NotIn if negated else ast.In
        if len(comparison.ops) != 1 or not isinstance(comparison.ops[0], operator_type) or len(comparison.comparators) != 1:
            continue
        comparator = comparison.comparators[0]
        if not isinstance(comparator, ast.Set | ast.List | ast.Tuple):
            continue
        result: list[str] = []
        for element in comparator.elts:
            if not isinstance(element, ast.Attribute) or not isinstance(element.value, ast.Name) or element.value.id != "self":
                raise ExtractionError(path, element.lineno, f"non-literal membership in {method.name}")
            result.append(element.attr)
        return result
    return []


def _matcher_data(case: ast.match_case, path: Path) -> dict[str, Any]:
    """Extract one literal or recognized computed matcher arm."""
    returns = [node for node in case.body if isinstance(node, ast.Return)]
    if len(returns) != 1:
        raise ExtractionError(path, getattr(case.pattern, "lineno", 1), "matcher arm must have one top-level return")
    returned = returns[0]
    call = returned.value
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "FilenameMatcher":
        raise ExtractionError(path, returned.lineno, "unsupported matcher return shape")
    if any(isinstance(argument, ast.Starred) for argument in call.args):
        return {"computedShape": True}

    extensions: list[str] = []
    for argument in call.args:
        if not isinstance(argument, ast.Constant) or not isinstance(argument.value, str):
            raise ExtractionError(
                path,
                returned.lineno,
                "matcher extensions must be literal strings or a recognized computed list",
            )
        extensions.append(argument.value)

    case_sensitive = True
    for keyword in call.keywords:
        if keyword.arg != "case_sensitive" or not isinstance(keyword.value, ast.Constant) or not isinstance(keyword.value.value, bool):
            raise ExtractionError(path, keyword.value.lineno, "unsupported FilenameMatcher keyword")
        case_sensitive = keyword.value.value
    return {"literalExtensions": extensions, "caseSensitive": case_sensitive}


def _extract_matchers(method: ast.FunctionDef, values: dict[str, str], path: Path) -> dict[str, object]:
    """Extract every matcher arm with strict shape handling."""
    matches = [node for node in method.body if isinstance(node, ast.Match)]
    if len(matches) != 1:
        raise ExtractionError(path, method.lineno, "get_source_fn_matcher must contain one top-level match")
    result: dict[str, object] = {}
    for case in matches[0].cases:
        symbols = _pattern_members(case.pattern, path)
        if not symbols:
            continue
        data = _matcher_data(case, path)
        for symbol in symbols:
            if symbol not in values:
                raise ExtractionError(path, getattr(case.pattern, "lineno", method.lineno), f"unknown matcher member {symbol}")
            result[values[symbol]] = data
    return result


def _extract_dispatch(method: ast.FunctionDef, values: dict[str, str], path: Path) -> dict[str, object]:
    """Extract lazy-import dispatch arms without executing repository code."""
    matches = [node for node in method.body if isinstance(node, ast.Match)]
    if len(matches) != 1:
        raise ExtractionError(path, method.lineno, "get_ls_class must contain one top-level match")
    result: dict[str, object] = {}
    for case in matches[0].cases:
        symbols = _pattern_members(case.pattern, path)
        if not symbols:
            continue
        if len(case.body) != 2 or not isinstance(case.body[0], ast.ImportFrom) or not isinstance(case.body[1], ast.Return):
            raise ExtractionError(
                path, getattr(case.pattern, "lineno", method.lineno), "dispatch arm must contain one import and one return"
            )
        imported = case.body[0]
        returned = case.body[1].value
        if imported.module is None or len(imported.names) != 1 or not isinstance(returned, ast.Name):
            raise ExtractionError(path, case.body[0].lineno, "unsupported dispatch import or return")
        imported_name = imported.names[0].asname or imported.names[0].name
        if returned.id != imported_name:
            raise ExtractionError(path, case.body[1].lineno, "dispatch return does not match imported class")
        data = {"module": imported.module, "class": imported.names[0].name}
        for symbol in symbols:
            if symbol not in values:
                raise ExtractionError(path, getattr(case.pattern, "lineno", method.lineno), f"unknown dispatch member {symbol}")
            result[values[symbol]] = data
    return result


def _priority_zero_set(method: ast.FunctionDef, experimental: list[str], path: Path) -> list[str]:
    """Extract members whose explicit or experimental priority is zero."""
    result = set(experimental)
    for node in ast.walk(method):
        if not isinstance(node, ast.Match):
            continue
        for case in node.cases:
            returns_zero = any(
                isinstance(child, ast.Return) and isinstance(child.value, ast.Constant) and child.value.value == 0 for child in case.body
            )
            if returns_zero:
                result.update(_pattern_members(case.pattern, path))
    return sorted(result)


def extract_ls_config(path: Path) -> dict[str, object]:
    """Extract normalized facts from `LanguageServerId`."""
    language_class = _language_class(_parse(path), path)
    symbols, values = _enum_members(language_class, path)

    # Matcher and dispatch shape drift are the most actionable errors and are
    # validated before optional classification helpers.
    matchers = _extract_matchers(_method(language_class, "get_source_fn_matcher", path), values, path)
    dispatch = _extract_dispatch(_method(language_class, "get_ls_class", path), values, path)

    experimental_symbols = _membership_set(_method(language_class, "is_experimental", path), negated=False, path=path)
    non_programming_symbols = _membership_set(_method(language_class, "is_programming_language", path), negated=True, path=path)
    priority_symbols = _priority_zero_set(_method(language_class, "get_priority", path), experimental_symbols, path)

    return {
        "members": [values[symbol] for symbol in symbols],
        "memberSymbols": {values[symbol]: symbol for symbol in symbols},
        "dispatch": dispatch,
        "matchers": matchers,
        "experimentalSet": sorted(values[symbol] for symbol in experimental_symbols),
        "nonProgrammingSet": sorted(values[symbol] for symbol in non_programming_symbols),
        "priorityZeroSet": sorted(values[symbol] for symbol in priority_symbols),
    }
