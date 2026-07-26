"""Tests for the pinned CUE contract-compiler runtime."""

from __future__ import annotations

import io
import json
import os
import subprocess
import tarfile
from pathlib import Path
from unittest.mock import patch

import pytest
from ruamel.yaml import YAML

from scripts.lsp_contract.cue_runtime import ChecksumMismatchError, CueRuntime


@pytest.fixture
def tampered_archive(tmp_path: Path) -> Path:
    """Archive whose bytes deliberately do not match the pinned digest."""
    archive = tmp_path / "cue_v0.17.1_linux_amd64.tar.gz"
    payload = b"not the pinned cue binary"
    member = tarfile.TarInfo("cue")
    member.mode = 0o755
    member.size = len(payload)
    with tarfile.open(archive, "w:gz") as tar:
        tar.addfile(member, io.BytesIO(payload))
    return archive


def test_tampered_archive_is_rejected_without_installing(tmp_path: Path, tampered_archive: Path) -> None:
    runtime = CueRuntime(managed_root=tmp_path / "managed")

    with pytest.raises(ChecksumMismatchError, match="sha256"):
        runtime.install_from_archive(
            tampered_archive,
            asset_name=tampered_archive.name,
            expected_sha256="0" * 64,
        )

    assert not runtime.managed_root.exists() or not any(runtime.managed_root.rglob("cue"))


def test_locate_honors_serena_cue_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    executable = tmp_path / "cue"
    executable.touch()
    executable = executable.resolve()
    monkeypatch.setenv("SERENA_CUE", str(executable))
    completed = subprocess.CompletedProcess(args=[executable, "version"], returncode=0, stdout="cue version v0.17.1\n", stderr="")

    with patch.object(subprocess, "run", return_value=completed) as run:
        assert CueRuntime(managed_root=tmp_path / "managed").locate() == executable

    run.assert_called_once_with([executable, "version"], check=False, capture_output=True, text=True, timeout=10)


def test_locate_rejects_prefix_version_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    executable = tmp_path / "cue"
    executable.touch()
    executable = executable.resolve()
    monkeypatch.setenv("SERENA_CUE", str(executable))
    completed = subprocess.CompletedProcess(args=[executable, "version"], returncode=0, stdout="cue version v0.17.10\n", stderr="")

    with patch.object(subprocess, "run", return_value=completed):
        with pytest.raises(RuntimeError, match=r"does not report v0\.17\.1"):
            CueRuntime(managed_root=tmp_path / "managed").locate()


def test_project_config_keeps_cue_activation_local() -> None:
    project_path = Path(__file__).parents[2] / ".serena" / "project.yml"
    project = YAML(typ="safe").load(project_path.read_text(encoding="utf-8"))
    cue_settings = project.get("ls_specific_settings", {}).get("cue", {})

    assert "cue" not in project["language_servers"]
    assert "ls_path" not in cue_settings


@pytest.mark.skipif(os.environ.get("SERENA_CONTRACT_OFFLINE") == "1", reason="explicit offline contract run")
def test_real_install_has_pinned_version() -> None:
    binary = CueRuntime().install()
    completed = subprocess.run([binary, "version"], check=True, capture_output=True, text=True)
    version_lines = [line.split() for line in completed.stdout.splitlines() if line.startswith("cue version ")]

    assert version_lines == [["cue", "version", "v0.17.1"]]


@pytest.mark.skipif(os.environ.get("SERENA_CONTRACT_OFFLINE") == "1", reason="explicit offline contract run")
def test_cue_exports_pytest_workflow_as_json() -> None:
    workflow = Path(".github/workflows/pytest.yml")
    exit_code, stdout, stderr = CueRuntime().run(["export", "--out", "json"], [workflow])

    assert exit_code == 0, stderr
    assert "cpu" in json.loads(stdout)["jobs"]
