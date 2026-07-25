"""Filesystem extraction of fixture and test-directory facts.

The repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.
"""

import ast
from pathlib import Path


def _is_session_autouse_fixture(decorator: ast.expr) -> bool:
    if not isinstance(decorator, ast.Call):
        return False
    function = decorator.func
    if not (
        isinstance(function, ast.Attribute)
        and function.attr == "fixture"
        and isinstance(function.value, ast.Name)
        and function.value.id == "pytest"
    ):
        return False
    keywords = {keyword.arg: keyword.value for keyword in decorator.keywords if keyword.arg is not None}
    scope = keywords.get("scope")
    autouse = keywords.get("autouse")
    return isinstance(scope, ast.Constant) and scope.value == "session" and isinstance(autouse, ast.Constant) and autouse.value is True


def _has_bootstrap_fixture(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(
        any(_is_session_autouse_fixture(decorator) for decorator in node.decorator_list)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    )


def extract_filesystem(root: Path) -> dict[str, object]:
    """Extract fixture repositories, test directories, and session bootstrap fixtures."""
    repository_root = root / "test" / "resources" / "repos"
    test_root = root / "test" / "solidlsp"

    repo_dirs = sorted(path.name for path in repository_root.iterdir() if path.is_dir()) if repository_root.is_dir() else []
    test_dirs = sorted(path.name for path in test_root.iterdir() if path.is_dir()) if test_root.is_dir() else []
    bootstrap_conftests = (
        sorted(path.parent.name for path in test_root.glob("*/conftest.py") if path.is_file() and _has_bootstrap_fixture(path))
        if test_root.is_dir()
        else []
    )
    return {
        "repoDirs": repo_dirs,
        "testDirs": test_dirs,
        "bootstrapConftests": bootstrap_conftests,
    }
