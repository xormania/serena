"""Rejection diagnostics for registration, testing, and waiver invariants."""

from __future__ import annotations

import json

import pytest

from scripts.lsp_contract.diagnostics import render_cue_diagnostics
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
    "c-prov-001-shape",
    "c-prov-002-cargo-unlocked",
    "c-prov-002-command-missing",
    "c-prov-002-command-undeclared",
    "c-prov-003-sha-missing",
    "c-prov-003-sha-opaque",
    "c-prov-003-omnisharp-integrity-missing",
    "c-prov-003-no-evidence",
    "c-prov-004-unpinned",
    "c-prov-005-platform-no-path",
    "c-prov-005-path-outside-support",
    "c-prov-006-owner-ambiguous",
    "c-plat-001-unexcluded",
    "c-plat-001-overlap",
    "c-plat-001-reason-missing",
    "c-waive-001-stale",
]

CATEGORIES = {
    "C_REG": "registration",
    "C_TEST": "testing",
    "C_PROV": "provisioning",
    "C_PLAT": "platform",
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

    raw_path = expected.get("raw_path")
    if raw_path is not None:
        assert raw_path in stderr
        diagnostic_output = render_cue_diagnostics(stderr)
    else:
        diagnostic_output = stderr
    assert diagnostic in diagnostic_output
    assert expected["subject"] in diagnostic_output


def test_all_named_rejection_fixture_files_exist() -> None:
    for case_name in INVALID_CASES:
        case_dir = FIXTURES / "invalid" / case_name
        assert case_dir.is_dir()
        assert {path.name for path in case_dir.iterdir()} == {
            "declarations.json",
            "expected.json",
            "extracted.json",
        }
