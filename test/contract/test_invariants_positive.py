"""Positive representatives for P4 registration and test-surface classes."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from test.contract.invariant_support import FIXTURES, ROOT, load_fixture, validate_fixture

VALID_CASES = [
    "python",
    "python-ty",
    "cpp",
    "cpp-ccls",
    "gdscript",
    "msl",
    "erlang-waived",
    "hlsl",
    "csharp",
    "java",
    "ruby",
    "nix",
    "al",
    "swift",
    "qml-provisioning",
    "svelte-bootstrap",
    "elixir-waived",
    "opaque-shell-waived",
    "cap-verified",
    "kotlin-ci-waived",
    "cache-unversioned-restore",
    "ci-marker-duplicate-same-group",
]


@pytest.mark.parametrize("case_name", VALID_CASES)
def test_valid_integration_class_is_accepted(case_name: str) -> None:
    case_dir = FIXTURES / "valid" / case_name
    metadata = json.loads((case_dir / "expected.json").read_text())
    document = load_fixture(case_dir)
    assert metadata["backend"] in document["backends"]

    def lookup(dotted_path: str) -> object:
        value: object = document
        for part in dotted_path.split("."):
            if isinstance(value, list):
                value = value[int(part)]
            else:
                assert isinstance(value, dict), f"{dotted_path}: {part} is not addressable"
                value = value[part]
        return value

    for dotted_path, expected in metadata.get("must_equal", {}).items():
        assert lookup(dotted_path) == expected, dotted_path
    for dotted_path, expected_length in metadata.get("must_have_length", {}).items():
        value = lookup(dotted_path)
        assert isinstance(value, list | dict), dotted_path
        assert len(value) == expected_length, dotted_path
    for dotted_path in metadata.get("all_nonempty", []):
        container_path, field = dotted_path.rsplit(".", 1)
        values = lookup(container_path)
        assert isinstance(values, list) and values, dotted_path
        assert all(isinstance(value, dict) and value.get(field) not in (None, "") for value in values), dotted_path

    returncode, _, stderr = validate_fixture(case_dir)
    assert returncode == 0, f"expected valid fixture {case_name} to pass:\n{stderr}"


def test_fixture_input_is_created_on_repository_volume() -> None:
    with patch("test.contract.invariant_support.CueRuntime.run", return_value=(0, "", "")) as run:
        validate_fixture(FIXTURES / "valid" / "python")

    input_path = run.call_args.args[-1][-1]
    assert input_path.is_relative_to(ROOT)
