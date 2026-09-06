"""Conventions every script under scripts/ must keep: a shebang, an executable bit, a
module docstring saying what the script does, and a working --help. All of it is checked
through the artifact's observable surface — file mode, first line, docstring, and what
--help actually prints — never through how a script is implemented.
"""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"

_ALL_SCRIPTS = sorted(_SCRIPTS_DIR.rglob("*.py"))
# a parametrization over an empty list collects zero tests and reports success, so a moved
# or renamed scripts/ directory would silently retire every check on this page
assert _ALL_SCRIPTS, f"no scripts found under {_SCRIPTS_DIR}: this suite would pass by collecting nothing"

posix_only = pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes")


@pytest.mark.parametrize("script", _ALL_SCRIPTS, ids=lambda p: str(p.relative_to(_SCRIPTS_DIR)))
class TestScriptConventions:
    """Every script explains itself — in its source, and at --help."""

    def test_has_a_shebang_and_a_module_docstring(self, script: Path) -> None:
        """Given any script in the tree, its first line is the python3 shebang and its
        module docstring is present and nonempty.
        """
        source = script.read_text(encoding="utf-8")
        assert source.splitlines()[0] == "#!/usr/bin/env python3", f"{script.name} lacks the shebang"
        docstring = ast.get_docstring(ast.parse(source))
        assert docstring is not None and docstring.strip(), f"{script.name} lacks a nonempty module docstring"

    @posix_only
    def test_is_executable(self, script: Path) -> None:
        """Given any script, its file mode permits direct execution on POSIX."""
        assert os.access(script, os.X_OK), f"{script.name} is not executable"


class TestScriptSmoke:
    """Every script answers --help, including Agno without its optional imports.

    This exercises imports reached before help exits, not full application startup
    or the absence of side effects.
    """

    @pytest.mark.parametrize("script", _ALL_SCRIPTS, ids=lambda p: str(p.relative_to(_SCRIPTS_DIR)))
    def test_help_exits_zero_and_prints_help(self, script: Path) -> None:
        """Given any script, --help exits 0 and prints a usage header, not merely
        normal output that happens to mention the word "usage".
        """
        result = subprocess.run(
            [sys.executable, str(script), "--help"], capture_output=True, text=True, timeout=120, check=False, cwd=_REPO_ROOT
        )
        assert result.returncode == 0, f"{script.name} --help exited {result.returncode}:\n{result.stderr[-800:]}"
        assert any(re.search(r"^usage:[ \t]+\S", output, re.IGNORECASE | re.MULTILINE) for output in (result.stdout, result.stderr)), (
            f"{script.name} --help exited 0 without printing a usage header"
        )
