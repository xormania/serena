#!/usr/bin/env python3
"""Prints the names and descriptions of default-enabled tools."""

import argparse

from serena.agent import ToolRegistry

if __name__ == "__main__":
    argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0]).parse_args()
    ToolRegistry().print_tool_overview()
