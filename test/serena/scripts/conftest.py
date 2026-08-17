"""Fixtures for the contributor-script tests. The scripts are standalone files rather than
packages, so they are imported by file path. The path is pinned: if a script is not where
this tree says it lives, the suite errors rather than adapting — a missing or misplaced
script is a finding, not something to fall back from.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_script(name: str) -> ModuleType:
    script_path = _REPO_ROOT / "scripts" / f"{name}.py"
    assert script_path.is_file(), f"contributor script not where this tree keeps it: {script_path}"
    spec = importlib.util.spec_from_file_location(name, script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def doctor() -> ModuleType:
    """The dev-environment doctor, check_dev_env.py"""
    return _load_script("check_dev_env")


@pytest.fixture(scope="session")
def probe_module() -> ModuleType:
    """The live client-setup probe, live_test_client_setup.py"""
    return _load_script("live_test_client_setup")
