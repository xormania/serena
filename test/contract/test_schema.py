"""Acceptance and rejection tests for the complete CUE schema layer."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.lsp_contract.cue_runtime import CueRuntime

ROOT = Path(__file__).parents[2]
FIXTURES = Path(__file__).parent / "fixtures" / "schema"

ACCEPT_CASES = [
    ("backend-path.json", "#Backend"),
    ("provisioning-download.json", "#Provisioning"),
    ("provisioning-composite.json", "#Provisioning"),
    ("platforms.json", "#Platforms"),
    ("testing.json", "#Testing"),
    ("ci.json", "#CI"),
    ("capabilities.json", "#Capabilities"),
    ("waiver.json", "#Waiver"),
    ("extracted.json", "#Extracted"),
]

REJECT_CASES = [
    ("backend-extra-field.json", "#Backend", "unexpected: field not allowed"),
    ("provisioning-download-missing-pin.json", "#Provisioning", "pin: field is required"),
    ("provisioning-owner-missing-ci.json", "#Provisioning", "owner.ci: field is required"),
    ("platforms-unknown-os.json", "#Platforms", "supported.0"),
    ("testing-missing-marker.json", "#Testing", "marker: field is required"),
    ("bootstrap-ci-skip.json", "#Bootstrap", "onFailure.ci"),
    ("ci-missing-batch.json", "#CI", "batch: field is required"),
    ("skip-policy-missing-loud-on.json", "#SkipPolicy", "loudOn: field is required"),
    ("capabilities-unknown.json", "#Capabilities", "implementationSupport"),
    ("waiver-empty-reason.json", "#Waiver", "reason"),
    ("extracted-extra-field.json", "#Extracted", "unexpected: field not allowed"),
]


def _schema_files() -> list[Path]:
    return sorted((ROOT / "contract").glob("schema_*.cue"))


def _vet(fixture: Path, definition: str) -> tuple[int, str, str]:
    schema_files = _schema_files()
    if not schema_files:
        return 1, "", "contract/schema_*.cue: schema files missing"
    return CueRuntime().run(["vet", "-c=false", "-d", definition], [*schema_files, fixture])


@pytest.mark.parametrize(("filename", "definition"), ACCEPT_CASES)
def test_schema_accepts_valid_instances(filename: str, definition: str) -> None:
    returncode, _, stderr = _vet(FIXTURES / "accept" / filename, definition)
    assert returncode == 0, f"expected cue vet to succeed for {filename}:\n{stderr}"


@pytest.mark.parametrize(("filename", "definition", "diagnostic"), REJECT_CASES)
def test_schema_rejects_invalid_instances(filename: str, definition: str, diagnostic: str) -> None:
    returncode, _, stderr = _vet(FIXTURES / "reject" / filename, definition)
    assert returncode == 1, f"expected cue vet to reject {filename}"
    assert diagnostic in stderr


def test_schema_package_vets_and_is_formatted() -> None:
    schema_files = _schema_files()
    assert schema_files, "expected the contract CUE schema files to exist"
    runtime = CueRuntime()
    returncode, _, stderr = runtime.run(["vet", "-c=false"], schema_files)
    assert returncode == 0, stderr
    returncode, _, stderr = runtime.run(["fmt", "--check"], schema_files)
    assert returncode == 0, stderr


def test_vet_schema_driver_runs_the_offline_schema_gate() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.lsp_contract", "vet-schema", "--root", str(ROOT)],
        check=False,
        capture_output=True,
        text=True,
        env={"CUE_REGISTRY": "host.invalid"},
    )
    assert completed.returncode == 0, completed.stderr
