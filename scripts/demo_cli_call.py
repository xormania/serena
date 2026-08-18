#!/usr/bin/env python3
"""Demonstrates invoking Serena's CLI entry point programmatically: calls the top-level
command group in-process (asking it for its own help text) instead of spawning a ``serena``
subprocess.
"""

import argparse

from serena.cli import top_level

if __name__ == "__main__":
    argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0]).parse_args()
    top_level(["--help"])
