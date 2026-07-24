"""Command-line interface for the language-integration contract."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from scripts.lsp_contract.cue_runtime import install
from scripts.lsp_contract.diagnostics import ExtractionError
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

    raise NotImplementedError(f"lsp_contract.{arguments.command}")


if __name__ == "__main__":
    raise SystemExit(main())
