"""Shared fixture runner for CUE contract invariant tests."""

from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.lsp_contract.cue_runtime import CueRuntime

ROOT = Path(__file__).parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "invariants"
CASE_MANIFEST_NAME = "declarations.json"
CASE_SECTIONS = ("declarations", "extracted", "expected")
CASE_KINDS = ("valid", "invalid")


@dataclass(frozen=True)
class InvariantCase:
    """One invariant case loaded losslessly from its consolidated manifest."""

    case_id: str
    case_dir: Path
    declarations: dict[str, Any]
    extracted: dict[str, Any]
    expected: dict[str, Any]


class InvariantFixtureError(ValueError):
    """Raised when an invariant fixture cannot be loaded unambiguously."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in pairs:
        if key in payload:
            raise InvariantFixtureError(f"duplicate JSON key {key!r}")
        payload[key] = value
    return payload


def load_case(case_dir: Path, *, case_id: str | None = None) -> InvariantCase:
    """Load one exact three-section manifest using deterministic UTF-8 JSON."""
    manifest_path = case_dir / CASE_MANIFEST_NAME
    try:
        entries = sorted(path.name for path in case_dir.iterdir())
    except OSError as error:
        raise InvariantFixtureError(f"{case_dir}: manifest directory is unavailable: {error}") from error
    if entries != [CASE_MANIFEST_NAME]:
        raise InvariantFixtureError(f"{case_dir}: case must contain exactly one manifest {CASE_MANIFEST_NAME!r}; found {entries}")

    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as error:
        raise InvariantFixtureError(f"{manifest_path}: manifest is unavailable: {error}") from error
    try:
        payload = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as error:
        raise InvariantFixtureError(f"{manifest_path}: malformed JSON at line {error.lineno}, column {error.colno}: {error.msg}") from error
    except InvariantFixtureError as error:
        raise InvariantFixtureError(f"{manifest_path}: {error}") from error

    if not isinstance(payload, dict):
        raise InvariantFixtureError(f"{manifest_path}: manifest must be a JSON object")
    missing = [section for section in CASE_SECTIONS if section not in payload]
    if missing:
        raise InvariantFixtureError(f"{manifest_path}: missing manifest sections: {', '.join(missing)}")
    unknown = sorted(set(payload) - set(CASE_SECTIONS))
    if unknown:
        raise InvariantFixtureError(f"{manifest_path}: unknown manifest sections: {', '.join(unknown)}")

    for section in CASE_SECTIONS:
        if not isinstance(payload[section], dict):
            raise InvariantFixtureError(f"{manifest_path}: {section} section must be a JSON object")
    for section in ("declarations", "extracted"):
        if not isinstance(payload[section].get("operations"), list):
            raise InvariantFixtureError(f"{manifest_path}: {section}.operations must be a JSON array")

    return InvariantCase(
        case_id=case_id or case_dir.name,
        case_dir=case_dir,
        declarations=payload["declarations"],
        extracted=payload["extracted"],
        expected=payload["expected"],
    )


def discover_cases(root: Path = FIXTURES) -> tuple[InvariantCase, ...]:
    """Discover every valid and invalid case exactly once in stable order."""
    cases: list[InvariantCase] = []
    for kind in CASE_KINDS:
        kind_dir = root / kind
        try:
            entries = sorted(kind_dir.iterdir(), key=lambda path: path.name)
        except OSError as error:
            raise InvariantFixtureError(f"{kind_dir}: fixture category is unavailable: {error}") from error
        for case_dir in entries:
            case_id = f"{kind}/{case_dir.name}"
            if not case_dir.is_dir():
                raise InvariantFixtureError(f"{case_id}: fixture case must be a directory")
            cases.append(load_case(case_dir, case_id=case_id))
    return tuple(cases)


def _lookup(document: dict[str, Any], path: list[str | int]) -> Any:
    value: Any = document
    for part in path:
        value = value[part]
    return value


def _parent(document: dict[str, Any], path: list[str | int]) -> tuple[Any, str | int]:
    if not path:
        raise ValueError("fixture operation path may not be empty")
    return _lookup(document, path[:-1]), path[-1]


def _apply_operations(document: dict[str, Any], overlay: dict[str, Any]) -> None:
    for operation in overlay["operations"]:
        path = operation["path"]
        parent, key = _parent(document, path)
        if operation["op"] == "set":
            parent[key] = deepcopy(operation["value"])
        elif operation["op"] == "delete":
            del parent[key]
        elif operation["op"] == "append":
            parent[key].append(deepcopy(operation["value"]))
        elif operation["op"] == "copy":
            parent[key] = deepcopy(_lookup(document, operation["from"]))
        else:
            raise ValueError(f"unknown fixture operation: {operation['op']}")


def load_fixture(case_dir: Path) -> dict[str, Any]:
    """Load the shared valid document and apply one case manifest's overlays."""
    case = load_case(case_dir)
    document = json.loads((FIXTURES / "base.json").read_text(encoding="utf-8"))
    _apply_operations(document, case.declarations)
    _apply_operations(document, case.extracted)
    return document


def validate_fixture(case_dir: Path) -> tuple[int, str, str]:
    """Evaluate a fixture against schemas and every implemented invariant."""
    cue_files = [
        *sorted((ROOT / "contract").glob("schema_*.cue")),
        *sorted((ROOT / "contract").glob("invariant_*.cue")),
        FIXTURES / "contract.cue",
    ]
    document = load_fixture(case_dir)
    with tempfile.TemporaryDirectory(prefix="serena-contract-fixture-", dir=ROOT) as directory:
        input_path = Path(directory) / "input.json"
        input_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        return CueRuntime().run(["export", "--out", "json"], [*cue_files, input_path])
