"""End-to-end validation against the live repository."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]


def test_full_repo_validates() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.lsp_contract", "validate", "--root", str(ROOT)],
        check=False,
        capture_output=True,
        text=True,
        env={"CUE_REGISTRY": "host.invalid"},
    )
    assert completed.returncode == 0, completed.stderr
    assert "0 violations" in completed.stdout
    assert "waivers: 7" in completed.stdout
