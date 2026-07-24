"""Rejection diagnostics for registration, testing, and waiver invariants."""

from __future__ import annotations

import json

import pytest

from test.contract.invariant_support import FIXTURES, validate_fixture

INVALID_CASES = [
    "c-reg-001-missing-decl",
    "c-reg-001-orphan-decl",
    "c-reg-002-dispatch-missing",
    "c-reg-003-matcher-missing",
    "c-reg-004-status-drift",
    "c-reg-005-alt-as-language",
    "c-reg-006-two-defaults",
    "c-reg-007-template-stale",
    "c-test-001-marker-missing",
    "c-test-002-fixture-missing",
    "c-test-003-testdir-missing",
    "c-test-004-orphan-marker",
    "c-test-005-dup-alias",
    "c-test-006-untested-unwaived",
    "c-waive-001-stale",
]

CATEGORIES = {
    "C_REG": "registration",
    "C_TEST": "testing",
    "C_WAIVE": "waiver hygiene",
}


@pytest.mark.parametrize("case_name", INVALID_CASES)
def test_invalid_fixture_is_rejected_with_stable_diagnostic(case_name: str) -> None:
    case_dir = FIXTURES / "invalid" / case_name
    expected = json.loads((case_dir / "expected.json").read_text())
    returncode, _, stderr = validate_fixture(case_dir)

    diagnostic = expected["diagnostic"]
    prefix = diagnostic.rsplit("_", 1)[0]
    assert expected["category"] == CATEGORIES[prefix]
    assert returncode == 1, f"expected rejection {diagnostic}, got exit {returncode}:\n{stderr}"
    assert diagnostic in stderr
    assert expected["subject"] in stderr


def test_all_named_rejection_fixture_files_exist() -> None:
    for case_name in INVALID_CASES:
        case_dir = FIXTURES / "invalid" / case_name
        assert case_dir.is_dir()
        assert {path.name for path in case_dir.iterdir()} == {
            "declarations.json",
            "expected.json",
            "extracted.json",
        }
