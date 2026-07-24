"""Tests for the pinned CUE contract-compiler runtime."""

from __future__ import annotations

import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

import pytest

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
    executable.write_text("#!/bin/sh\necho 'cue version v0.17.1'\n", encoding="utf-8")
    executable.chmod(0o755)
    monkeypatch.setenv("SERENA_CUE", str(executable))

    assert CueRuntime(managed_root=tmp_path / "managed").locate() == executable


@pytest.mark.skipif(os.environ.get("SERENA_CONTRACT_OFFLINE") == "1", reason="explicit offline contract run")
def test_real_install_has_pinned_version() -> None:
    binary = CueRuntime().install()
    completed = subprocess.run([binary, "version"], check=True, capture_output=True, text=True)

    assert "v0.17.1" in completed.stdout


@pytest.mark.skipif(os.environ.get("SERENA_CONTRACT_OFFLINE") == "1", reason="explicit offline contract run")
def test_cue_exports_pytest_workflow_as_json() -> None:
    workflow = Path(".github/workflows/pytest.yml")
    exit_code, stdout, stderr = CueRuntime().run(["export", "--out", "json"], [workflow])

    assert exit_code == 0, stderr
    assert "cpu" in json.loads(stdout)["jobs"]
