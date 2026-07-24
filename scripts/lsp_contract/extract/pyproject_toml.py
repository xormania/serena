"""TOML extraction of marker and development-pin facts.\n\nThe repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.\n"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any, cast

from scripts.lsp_contract.diagnostics import ExtractionError

_PIN_PATTERN = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[^]]+])?==([^; ]+)")


def _table(value: object, path: Path, name: str) -> dict[str, Any]:
    """Require a TOML table at a known structural path."""
    if not isinstance(value, dict):
        raise ExtractionError(path, 1, f"missing or invalid TOML table {name}")
    return cast(dict[str, Any], value)


def extract_pyproject(path: Path) -> dict[str, Any]:
    """Extract normalized pyproject contract facts."""
    # parse the structured configuration
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ExtractionError(path, 1, f"could not parse TOML: {error}") from error
    tool = _table(document.get("tool"), path, "tool")
    pytest = _table(tool.get("pytest"), path, "tool.pytest")
    options = _table(pytest.get("ini_options"), path, "tool.pytest.ini_options")
    raw_markers = options.get("markers")
    if not isinstance(raw_markers, list) or not all(isinstance(marker, str) for marker in raw_markers):
        raise ExtractionError(path, 1, "tool.pytest.ini_options.markers must be a literal string list")

    # split marker ownership names from human descriptions
    markers: list[dict[str, str]] = []
    for marker in raw_markers:
        name, separator, description = marker.partition(":")
        name = name.strip()
        if not separator or not name:
            raise ExtractionError(path, 1, f"invalid pytest marker declaration: {marker!r}")
        markers.append({"name": name, "description": description.strip()})

    # retain exact development pins without importing packaging libraries
    dependency_groups = document.get("dependency-groups", {})
    optional_dependencies = document.get("project", {}).get("optional-dependencies", {})
    candidates: list[object] = []
    if isinstance(dependency_groups, dict):
        candidates.extend(dependency_groups.get("dev", []))
    if isinstance(optional_dependencies, dict):
        candidates.extend(optional_dependencies.get("dev", []))
    pins: dict[str, str] = {}
    for candidate in candidates:
        if not isinstance(candidate, str):
            continue
        match = _PIN_PATTERN.match(candidate)
        if match:
            pins[match.group(1)] = match.group(2)

    return {"markers": markers, "devPins": dict(sorted(pins.items()))}
