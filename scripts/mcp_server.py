#!/usr/bin/env python3
"""Starts the Serena MCP server programmatically — the legacy entry point that external MCP
client configurations launch by path, and a convenient place to hang a debugger. Arguments
are handled by the ``serena start-mcp-server`` CLI itself, so ``--help`` prints that
command's options.
"""

from serena.cli import top_level

if __name__ == "__main__":
    top_level.start_mcp_server()
