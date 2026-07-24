"""Command-line interface for the language-integration contract."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from scripts.lsp_contract.cue_runtime import install


def _build_parser() -> argparse.ArgumentParser:
    """Build the contract command-line parser."""
    parser = argparse.ArgumentParser(prog="python -m scripts.lsp_contract")
    parser.add_argument("command", choices=("install-cue", "extract", "vet-schema", "validate", "explain"))
    parser.add_argument("argument", nargs="?")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected contract command."""
    arguments = _build_parser().parse_args(argv)

    # install the pinned compiler
    if arguments.command == "install-cue":
        print(install())
        return 0

    # reserve dependency-ordered commands
    raise NotImplementedError(f"lsp_contract.{arguments.command}")


if __name__ == "__main__":
    raise SystemExit(main())
