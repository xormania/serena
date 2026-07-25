"""Shared fixture runner for CUE contract invariant tests."""

from __future__ import annotations

import json
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from scripts.lsp_contract.cue_runtime import CueRuntime

ROOT = Path(__file__).parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "invariants"


def _lookup(document: dict[str, Any], path: list[str | int]) -> Any:
    value: Any = document
    for part in path:
        value = value[part]
    return value


def _parent(document: dict[str, Any], path: list[str | int]) -> tuple[Any, str | int]:
    if not path:
        raise ValueError("fixture operation path may not be empty")
    return _lookup(document, path[:-1]), path[-1]


def _apply_operations(document: dict[str, Any], overlay: Path) -> None:
    payload = json.loads(overlay.read_text())
    for operation in payload["operations"]:
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
    """Load the shared valid document and apply one case's two overlays."""
    document = json.loads((FIXTURES / "base.json").read_text())
    _apply_operations(document, case_dir / "declarations.json")
    _apply_operations(document, case_dir / "extracted.json")
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
        input_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return CueRuntime().run(["export", "--out", "json"], [*cue_files, input_path])
