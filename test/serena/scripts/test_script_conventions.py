"""Conventions every script under scripts/ must keep: a shebang, an executable bit, a
module docstring saying what the script does, and a working --help. All of it is checked
through the artifact's observable surface — file mode, first line, docstring, and what
--help actually prints — never through how a script is implemented.
"""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"

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

    @posix_only
    def test_is_executable(self, script: Path) -> None:
        """Given any script, its executable bit is set, so ./scripts/... works directly."""
        assert os.access(script, os.X_OK), f"{script.name} is not executable"


SERVED_APPS = {"agno_agent.py"}
"""scripts that build a served application at import time; --help is not a safe probe there"""


class TestScriptSmoke:
    """Every script actually starts. Scripts are the least-executed code in the repository,
    so their natural failure mode is an import silently broken by a refactor; --help is the
    cheapest execution that proves imports resolve and the argument wiring works.
    """

    @pytest.mark.parametrize(
        "script",
        [script for script in _ALL_SCRIPTS if script.name not in SERVED_APPS],
        ids=lambda p: str(p.relative_to(_SCRIPTS_DIR)),
    )
    def test_help_exits_zero_and_prints_help(self, script: Path) -> None:
        """Given any script that is not a served app, when it is invoked with --help,
        then it exits 0 and prints usage text — exit code alone would also pass a script
        that ignores its arguments and silently does its real work instead.
        """
        result = subprocess.run(
            [sys.executable, str(script), "--help"], capture_output=True, text=True, timeout=120, check=False, cwd=_REPO_ROOT
        )
        assert result.returncode == 0, f"{script.name} --help exited {result.returncode}:\n{result.stderr[-800:]}"
        assert "usage" in (result.stdout + result.stderr).lower(), f"{script.name} --help exited 0 without printing help"
