"""Hard-failure tests for extractor source-shape drift."""

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.lsp_contract.diagnostics import ExtractionError
from scripts.lsp_contract.extract.ls_config_ast import extract_ls_config
from scripts.lsp_contract.extract.workflow_yaml import extract_workflow

FIXTURES = Path(__file__).parent / "fixtures" / "extractor"


def test_unknown_matcher_shape_names_file_and_line() -> None:
    path = FIXTURES / "mutated" / "ls_config.py"

    with pytest.raises(ExtractionError) as error:
        extract_ls_config(path)

    assert str(path) in str(error.value)
    assert ":12:" in str(error.value)
    assert "matcher" in str(error.value).lower()


def test_missing_workflow_marker_group_is_drift() -> None:
    path = FIXTURES / "mutated" / "workflow.yml"

    with pytest.raises(ExtractionError) as error:
        extract_workflow(path)

    assert "MARKERS_JVM" in str(error.value)
    assert f"{path}:" in str(error.value)


def test_driver_uses_exit_two_for_extractor_drift() -> None:
    root = FIXTURES / "mutated"
    completed = subprocess.run(
        [sys.executable, "-m", "scripts.lsp_contract", "extract", "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 2
    assert "ls_config.py:12" in completed.stderr
    assert "matcher" in completed.stderr.lower()
