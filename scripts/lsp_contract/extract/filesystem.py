"""Filesystem extraction of fixture and test-directory facts.\n\nThe repository source remains authoritative; extraction supplies agreement checks and never a competing editable truth.\n"""

from pathlib import Path


def extract_filesystem(root: Path) -> dict[str, object]:
    """Extract fixture repositories, test directories, and bootstrap files."""
    repository_root = root / "test" / "resources" / "repos"
    test_root = root / "test" / "solidlsp"

    repo_dirs = sorted(path.name for path in repository_root.iterdir() if path.is_dir()) if repository_root.is_dir() else []
    test_dirs = sorted(path.name for path in test_root.iterdir() if path.is_dir()) if test_root.is_dir() else []
    bootstrap_conftests = (
        sorted(path.parent.name for path in test_root.glob("*/conftest.py") if path.is_file()) if test_root.is_dir() else []
    )
    return {
        "repoDirs": repo_dirs,
        "testDirs": test_dirs,
        "bootstrapConftests": bootstrap_conftests,
    }
