"""Conventions every script under scripts/ must keep: a shebang, an executable bit, a
module docstring saying what the script does, and a --help path — argparse or click, or
membership in the explicit delegation list for entry points whose underlying CLI parses
argv itself.
"""

import ast
import os
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"

HELP_BY_DELEGATION = {"mcp_server.py", "agno_agent.py"}
"""scripts whose --help is answered by the CLI they delegate to, or that build a served app"""

_ALL_SCRIPTS = sorted(_SCRIPTS_DIR.rglob("*.py"))

posix_only = pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes")


@pytest.mark.parametrize("script", _ALL_SCRIPTS, ids=lambda p: str(p.relative_to(_SCRIPTS_DIR)))
class TestScriptConventions:
    """Every script explains itself — in its source, and at --help."""

    def test_has_a_shebang_and_a_module_docstring(self, script: Path) -> None:
        """Given any script in the tree, its first line is the python3 shebang and its
        module docstring says what the script does.
        """
        source = script.read_text(encoding="utf-8")
        assert source.splitlines()[0] == "#!/usr/bin/env python3", f"{script.name} lacks the shebang"
        docstring = ast.get_docstring(ast.parse(source))
        assert docstring is not None and len(docstring.strip()) >= 20, f"{script.name} lacks a meaningful module docstring"

    def test_answers_help_or_is_a_documented_delegation(self, script: Path) -> None:
        """Given any script, it either wires argparse or click (which provide -h/--help)
        or is on the explicit delegation list.
        """
        if script.name in HELP_BY_DELEGATION:
            return
        source = script.read_text(encoding="utf-8")
        assert "argparse" in source or "click" in source, f"{script.name} has no --help path"

    @posix_only
    def test_is_executable(self, script: Path) -> None:
        """Given any script, its executable bit is set, so ./scripts/... works directly."""
        assert os.access(script, os.X_OK), f"{script.name} is not executable"
