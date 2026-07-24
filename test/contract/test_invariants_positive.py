"""Positive representatives for P4 registration and test-surface classes."""

from __future__ import annotations

import json

import pytest

from test.contract.invariant_support import FIXTURES, load_fixture, validate_fixture

VALID_CASES = [
    "python",
    "python-ty",
    "cpp",
    "cpp-ccls",
    "gdscript",
    "msl",
    "erlang-waived",
]


@pytest.mark.parametrize("case_name", VALID_CASES)
def test_valid_integration_class_is_accepted(case_name: str) -> None:
    case_dir = FIXTURES / "valid" / case_name
    metadata = json.loads((case_dir / "expected.json").read_text())
    document = load_fixture(case_dir)
    assert metadata["backend"] in document["backends"]

    returncode, _, stderr = validate_fixture(case_dir)
    assert returncode == 0, f"expected valid fixture {case_name} to pass:\n{stderr}"
