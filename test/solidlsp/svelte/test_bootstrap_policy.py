from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from test.solidlsp.svelte import conftest as svelte_conftest


@pytest.fixture(scope="session", autouse=True)
def _install_svelte_test_repo_node_modules() -> None:
    """Keep this policy unit test independent of the real Svelte fixture bootstrap."""


@pytest.mark.parametrize(
    ("returncode", "expected_message"),
    [
        (1, "npm ci failed"),
        (0, "required Svelte fixture packages are missing"),
    ],
)
def test_npm_ci_bootstrap_failures_are_visible(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    returncode: int,
    expected_message: str,
) -> None:
    package_lock = tmp_path / "package-lock.json"
    package_lock.write_text("{}\n", encoding="utf-8")

    monkeypatch.setattr(svelte_conftest, "PACKAGE_LOCK", package_lock)
    monkeypatch.setattr(svelte_conftest, "INSTALL_LOCK", tmp_path / "install.lock")
    monkeypatch.setattr(svelte_conftest, "SVELTE_MARKER", tmp_path / "node_modules/svelte/package.json")
    monkeypatch.setattr(
        svelte_conftest,
        "SVELTE_KIT_ADAPTER_MARKER",
        tmp_path / "node_modules/@sveltejs/adapter-auto/package.json",
    )
    monkeypatch.setattr(svelte_conftest, "_fixture_ready", lambda: False)
    monkeypatch.setattr(svelte_conftest.shutil, "which", lambda _name: "/usr/bin/npm")
    monkeypatch.setattr(
        svelte_conftest.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=returncode, stdout="stdout", stderr="stderr"),
    )

    with pytest.raises(BaseException) as raised:
        svelte_conftest._install_svelte_test_repo_node_modules.__wrapped__()

    assert isinstance(raised.value, pytest.fail.Exception)
    assert expected_message in str(raised.value)


def test_missing_npm_remains_an_environmental_skip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(svelte_conftest, "_fixture_ready", lambda: False)
    monkeypatch.setattr(svelte_conftest.shutil, "which", lambda _name: None)

    with pytest.raises(BaseException) as raised:
        svelte_conftest._install_svelte_test_repo_node_modules.__wrapped__()

    assert isinstance(raised.value, pytest.skip.Exception)
    assert "npm is not available" in str(raised.value)
