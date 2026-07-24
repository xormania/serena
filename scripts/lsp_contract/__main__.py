"""Command-line interface for the language-integration contract."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from scripts.lsp_contract.cue_runtime import CueRuntime, install
from scripts.lsp_contract.diagnostics import ExtractionError, render_cue_diagnostics
from scripts.lsp_contract.extract.assemble import write_extracted


def _build_parser() -> argparse.ArgumentParser:
    """Build the contract command-line parser."""
    parser = argparse.ArgumentParser(prog="python -m scripts.lsp_contract")
    parser.add_argument(
        "command",
        choices=(
            "install-cue",
            "extract",
            "vet-schema",
            "validate",
            "explain",
            "render-registration",
            "render-template-list",
        ),
    )
    parser.add_argument("argument", nargs="?")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    return parser


def _vet_schema(root: Path) -> int:
    """Vet and format-check the unified offline CUE schema package."""
    schema_files = sorted((root / "contract").glob("schema_*.cue"))
    if not schema_files:
        print(f"{root / 'contract'}: no schema_*.cue files found", file=sys.stderr)
        return 2

    runtime = CueRuntime()
    for arguments in (["vet", "-c=false"], ["fmt", "--check"]):
        returncode, stdout, stderr = runtime.run(arguments, schema_files)
        if stdout:
            print(stdout, end="")
        if returncode:
            print(stderr, file=sys.stderr, end="" if stderr.endswith("\n") else "\n")
            return 1
    return 0


def _validate(root: Path, output: Path | None = None) -> int:
    """Extract repository facts, vet schemas, and evaluate the full CUE contract."""
    root = root.resolve()
    try:
        extracted_path = write_extracted(root, output)
    except ExtractionError as error:
        print(error, file=sys.stderr)
        return 2

    schema_result = _vet_schema(root)
    if schema_result:
        return schema_result

    runtime = CueRuntime()
    returncode, stdout, stderr = runtime.run(["export", str(root / "contract"), str(extracted_path), "--out", "json"])
    if returncode:
        rendered = render_cue_diagnostics(stderr)
        if rendered:
            print(rendered, file=sys.stderr)
        return 1

    try:
        document = json.loads(stdout)
        waiver_count = len(document["waivers"])
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"contract: invalid CUE export output: {error}", file=sys.stderr)
        return 2

    print(f"contract: 0 violations; waivers: {waiver_count}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected contract command."""
    arguments = _build_parser().parse_args(argv)
    if arguments.command == "install-cue":
        print(install())
        return 0
    if arguments.command == "extract":
        try:
            print(write_extracted(arguments.root, arguments.output))
        except ExtractionError as error:
            print(error, file=sys.stderr)
            return 2
        return 0
    if arguments.command == "vet-schema":
        return _vet_schema(arguments.root)
    if arguments.command == "validate":
        return _validate(arguments.root, arguments.output)

    raise NotImplementedError(f"lsp_contract.{arguments.command}")


if __name__ == "__main__":
    raise SystemExit(main())
